import { NextRequest, NextResponse } from 'next/server';
import { randomUUID } from 'crypto';
import fs from 'fs/promises';
import path from 'path';
import { config } from '../../../../env.config';
import { minimaxClient } from '../../../lib/minimax';
import { generateUniversalPrompt, GenerationPhase } from '../../../lib/prompts';
import { parseGeneratedCode, generateRequirementsTxt } from '../../../lib/parser';
import { log } from '../../../lib/logger';
import { ensureDirectory, writeFileAtomic, createProjectStructure, fileExists } from '../../../lib/fileSystem';
import { DEFAULT_README, DEFAULT_REQUIREMENTS, DEFAULT_SPEC, DEFAULT_PLAN } from '../../../lib/templates';
import { streams } from '../../../lib/store';

// Configuration
const MINIMAX_API_KEY = config.minimax.apiKey;
const MINIMAX_GROUP_ID = config.minimax.groupId;
const PROJECTS_ROOT = config.system.projectsRoot;

// Types
interface GenerateRequest {
  prompt: string;
  projectId: string;
  application_type?: string;
}

interface SSEEvent {
  event: string;
  data: any;
}

// Phase definitions (matching prompts.ts)
type PhaseName = GenerationPhase;

const PHASE_ORDER: PhaseName[] = [GenerationPhase.SPECIFY, GenerationPhase.PLAN, GenerationPhase.IMPLEMENT];

// Utility functions
function getPhaseMessage(phase: PhaseName): string {
  switch (phase) {
    case 'specify':
      return '正在分析需求并制定技术规格...';
    case 'plan':
      return '正在制定详细的实现计划...';
    case 'implement':
      return '正在生成代码实现...';
    default:
      return '处理中...';
  }
}






// Main API handler - Trigger generation via SSE controller
export async function POST(request: NextRequest): Promise<NextResponse> {
  try {
    log('GENERATE', 'Request received', {
      method: request.method,
      url: request.url,
      timestamp: new Date().toISOString()
    });

    let body;
    try {
      body = await request.json();
      console.log("[API] /generate received body:", body); // <--- ADD THIS
    } catch (jsonError) {
      console.error("[API] JSON Parse Error:", jsonError);
      return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
    }

    const { prompt, projectId } = body;

    log('GENERATE', 'Request parsed', {
      promptLength: prompt?.length || 0,
      projectId
    });

    if (!prompt?.trim()) {
      console.error("[API] Missing prompt!");
      return NextResponse.json({ error: '用户输入不能为空' }, { status: 400 });
    }

    if (!projectId?.trim()) {
      console.error("[API] Missing projectId!");
      return NextResponse.json({ error: '项目ID不能为空' }, { status: 400 });
    }

    // Get SSE controller if available (optional for streaming)
    const controller = streams.get(projectId);
    const hasStreaming = !!controller;

    if (!hasStreaming) {
      log('GENERATE', 'SSE not connected, proceeding without streaming', { projectId });
    }

    // Start generation asynchronously - trigger pattern
    startGeneration(projectId, prompt, controller, hasStreaming);

    log('GENERATE', 'Generation triggered', {
      projectId,
      promptPreview: prompt.substring(0, 100) + '...'
    });

    // Return immediately
    return NextResponse.json({ status: 'started' });

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json(
      { error: '生成请求处理失败，请稍后重试' },
      { status: 500 }
    );
  }
}

// Safety check: ensure critical files exist
async function ensureCriticalFiles(projectId: string, projectDir: string, files: Record<string, string>): Promise<void> {
  const criticalFiles = [
    { name: 'README.md', defaultContent: DEFAULT_README },
    { name: 'requirements.txt', defaultContent: DEFAULT_REQUIREMENTS },
    { name: 'spec.md', defaultContent: DEFAULT_SPEC },
    { name: 'plan.md', defaultContent: DEFAULT_PLAN }
  ];

  for (const { name, defaultContent } of criticalFiles) {
    const filePath = path.join(projectDir, name);

    // Check if file exists in parsed files OR on disk
    const existsInParsed = files[name] && files[name].trim().length > 0;
    const existsOnDisk = await fileExists(filePath);

    if (!existsInParsed && !existsOnDisk) {
      log('GENERATE', 'Creating missing critical file', { filename: name, path: filePath });
      await ensureDirectory(path.dirname(filePath));
      await writeFileAtomic(filePath, defaultContent);
    }
  }
}

// Async generation function - Trigger pattern with optional SSE streaming
async function startGeneration(projectId: string, prompt: string, controller: ReadableStreamDefaultController | null, hasStreaming: boolean): Promise<void> {
  console.log(`[GENERATION] Starting generation for project ${projectId} with prompt: ${prompt}`);

  const encoder = new TextEncoder();

  try {
    const phasesData: Record<string, { content: string; thinking: string }> = {};
    let allCodeParts: string[] = [];

    // Execute each phase
    for (const phase of PHASE_ORDER) {
      try {
        // Generate prompt
        const phasePrompt = generateUniversalPrompt(
          phase,
          prompt,
          phasesData.specify?.content || '',
          phasesData.plan?.content || ''
        );

        // Send phase start event via SSE (if connected)
        if (hasStreaming && controller) {
          const phaseStartEvent = JSON.stringify({
            project_id: projectId,
            phase: phase,
            type: 'phase_start',
            timestamp: new Date().toISOString()
          });
          controller.enqueue(encoder.encode(`event: phase_start\ndata: ${phaseStartEvent}\n\n`));
        }

        console.log(`[API] Calling Minimax...`);

        // Collect content for this phase
        let phaseContent = '';
        let chunkCount = 0;

        try {
          for await (const chunk of minimaxClient.generateCodeStream(phasePrompt, phase)) {
            chunkCount++;
            console.log(`[API] Minimax Chunk: `, chunk.content.length);

            if (chunk.type === 'text') {
              phaseContent += chunk.content;

              // Send chunk via SSE (if connected)
              if (hasStreaming && controller) {
                const chunkEvent = JSON.stringify({
                  project_id: projectId,
                  phase: phase,
                  type: 'chunk',
                  content: chunk.content,
                  timestamp: new Date().toISOString()
                });
                controller.enqueue(encoder.encode(`event: chunk\ndata: ${chunkEvent}\n\n`));
              }
            }
          }

          console.log(`[GENERATION] Phase ${phase} completed with ${phaseContent.length} characters`);
        } catch (phaseError) {
          console.error(`[GENERATION] Phase ${phase} failed:`, phaseError);

          // Send phase error via SSE (if connected)
          if (hasStreaming && controller) {
            const errorEvent = JSON.stringify({
              project_id: projectId,
              phase: phase,
              type: 'phase_error',
              error: 'Phase failed',
              timestamp: new Date().toISOString()
            });
            controller.enqueue(encoder.encode(`event: phase_error\ndata: ${errorEvent}\n\n`));
          }

          throw phaseError;
        }

        // Store phase data
        phasesData[phase] = {
          content: phaseContent,
          thinking: '' // Could be enhanced to capture thinking traces
        };

        // Send phase complete via SSE (if connected)
        if (hasStreaming && controller) {
          const phaseCompleteEvent = JSON.stringify({
            project_id: projectId,
            phase: phase,
            type: 'phase_complete',
            content: phaseContent,
            timestamp: new Date().toISOString()
          });
          controller.enqueue(encoder.encode(`event: phase_complete\ndata: ${phaseCompleteEvent}\n\n`));
        }

        allCodeParts.push(phaseContent);

      } catch (error) {
        console.error(`Phase ${phase} failed:`, error);
        // Continue with other phases
        continue;
      }
    }

    // Parse and generate files
    const generatedContent = allCodeParts.join('');
    console.log(`[GENERATION] Generated content length: ${generatedContent.length}`);

    let files: Record<string, string> = {};
    if (generatedContent.trim()) {
      files = parseGeneratedCode(generatedContent);
      console.log(`[GENERATION] Parsed ${Object.keys(files).length} files:`, Object.keys(files));
    } else {
      // Fallback: create sample files if API failed
      console.log(`[GENERATION] No content generated, creating sample files`);
      files = {
        'main.py': `# Sample Python Calculator App
# Generated as fallback when API is unavailable

def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

def main():
    print("Simple Calculator")
    print("Operations: +, -, *, /")

    try:
        num1 = float(input("Enter first number: "))
        operation = input("Enter operation (+, -, *, /): ")
        num2 = float(input("Enter second number: "))

        if operation == '+':
            result = add(num1, num2)
        elif operation == '-':
            result = subtract(num1, num2)
        elif operation == '*':
            result = multiply(num1, num2)
        elif operation == '/':
            result = divide(num1, num2)
        else:
            result = "Invalid operation"

        print(f"Result: {result}")

    except ValueError:
        print("Invalid input. Please enter numbers.")

if __name__ == "__main__":
    main()
`
      };
    }

    // Create project directory
    const projectDir = await createProjectStructure(projectId);

    // Write files
    log('GENERATE', 'Writing code files', { count: Object.keys(files).length });
    for (const [filePath, content] of Object.entries(files)) {
      const fullPath = path.join(projectDir, filePath);
      log('GENERATE', 'Writing file', {
        relativePath: filePath,
        fullPath: path.resolve(fullPath),
        size: content.length
      });

      await ensureDirectory(path.dirname(fullPath));
      await writeFileAtomic(fullPath, content);

      // Send file created event via SSE (if connected)
      if (hasStreaming && controller) {
        const fileEvent = JSON.stringify({
          project_id: projectId,
          type: 'file_created',
          filename: filePath.split('/').pop() || filePath,
          path: filePath,
          size_bytes: Buffer.byteLength(content, 'utf-8'),
          timestamp: new Date().toISOString()
        });
        controller.enqueue(encoder.encode(`event: file_created\ndata: ${fileEvent}\n\n`));
      }
    }

    // Generate documentation files
    const documentationFiles = generateDocumentationFiles(prompt, phasesData, files);
    console.log(`[GENERATION] Generated ${Object.keys(documentationFiles).length} documentation files`);

    for (const [filePath, content] of Object.entries(documentationFiles)) {
      const fullPath = path.join(projectDir, filePath);
      log('GENERATE', 'Writing documentation file', {
        relativePath: filePath,
        fullPath: path.resolve(fullPath),
        size: content.length
      });

      await ensureDirectory(path.dirname(fullPath));
      await writeFileAtomic(fullPath, content);

      // Send documentation file created event via SSE (if connected)
      if (hasStreaming && controller) {
        const docEvent = JSON.stringify({
          project_id: projectId,
          type: 'file_created',
          filename: filePath.split('/').pop() || filePath,
          path: filePath,
          size_bytes: Buffer.byteLength(content, 'utf-8'),
          timestamp: new Date().toISOString()
        });
        controller.enqueue(encoder.encode(`event: file_created\ndata: ${docEvent}\n\n`));
      }
    }

    // Safety check: ensure all critical files exist
    await ensureCriticalFiles(projectId, projectDir, files);

    // Send completion event via SSE (if connected)
    if (hasStreaming && controller) {
      const completionEvent = JSON.stringify({
        project_id: projectId,
        type: 'generation_complete',
        total_files: Object.keys(files).length + Object.keys(documentationFiles).length,
        timestamp: new Date().toISOString()
      });
      controller.enqueue(encoder.encode(`event: generation_complete\ndata: ${completionEvent}\n\n`));
    }

    log('GENERATE', 'Generation completed successfully', { projectId });

  } catch (error) {
    console.error('[GENERATION] Generation failed:', error);

    // Send error event via SSE (if connected)
    if (hasStreaming && controller) {
      const errorEvent = JSON.stringify({
        project_id: projectId,
        type: 'generation_error',
        error: 'Generation failed',
        timestamp: new Date().toISOString()
      });
      controller.enqueue(encoder.encode(`event: generation_error\ndata: ${errorEvent}\n\n`));
    }
  }
}

// Documentation generation
function generateDocumentationFiles(
  userPrompt: string,
  phasesData: Record<string, { content: string; thinking: string }>,
  parsedFiles: Record<string, string>
): Record<string, string> {
  const files: Record<string, string> = {};

  // Only generate spec.md if it doesn't exist in parsedFiles
  if (!parsedFiles['spec.md'] && phasesData.specify?.content) {
    files['spec.md'] = `# 需求规格说明

## 用户需求
${userPrompt}

## 技术规格
${phasesData.specify.content}
`;
  }

  // Only generate plan.md if it doesn't exist in parsedFiles
  if (!parsedFiles['plan.md'] && phasesData.plan?.content) {
    files['plan.md'] = `# 实现计划

## 用户需求
${userPrompt}

## 详细计划
${phasesData.plan.content}
`;
  }

  // Only generate README.md if it doesn't exist in parsedFiles
  if (!parsedFiles['README.md']) {
    files['README.md'] = DEFAULT_README;
  }

  // Only generate requirements.txt if it doesn't exist in parsedFiles
  if (!parsedFiles['requirements.txt']) {
    files['requirements.txt'] = generateRequirementsTxt(parsedFiles);
  }

  return files;
}
