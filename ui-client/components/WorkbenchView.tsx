import React, { useEffect, useState, useRef } from 'react';
import { FileNode, LogEntry, ProjectState } from '../types';

interface WorkbenchViewProps {
  initialPrompt: string;
  projectId: string;
  debugMode?: boolean;
}

const WorkbenchView: React.FC<WorkbenchViewProps> = ({ initialPrompt, projectId, debugMode = false }) => {
  const [project, setProject] = useState<ProjectState>({
    name: 'Untitled-Spec-01',
    status: 'generating',
  });

  const [files, setFiles] = useState<FileNode[]>([]);
  const [projectStructureLoaded, setProjectStructureLoaded] = useState(false);

  const [activeFileId, setActiveFileId] = useState<string>('1');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // EventSource Connection for Real-time Updates
  useEffect(() => {
    console.log('🔥 [DEBUG] Workbench useEffect triggered, projectId:', projectId, 'debugMode:', debugMode);

    if (!projectId) {
      console.log('🔥 [DEBUG] No projectId, returning early');
      return;
    }

    console.log('🔥 [DEBUG] Connecting to stream:', projectId);
    console.log('🔥 [DEBUG] Stream URL:', `/api/stream/${projectId}`);
    console.log('🔥 [DEBUG] Debug mode:', debugMode);

    const eventSource = new EventSource(`/api/stream/${projectId}`);

    eventSource.onopen = () => {
      console.log('🔥 [DEBUG] EventSource connected successfully');
      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message: '🔗 连接到生成服务...',
        type: 'info'
      };
      setLogs(prev => [...prev, newLog]);
    };

    eventSource.onmessage = (event) => {
      console.log('📨 [DEBUG] Received message event:', event.type, event.data);
    };

    eventSource.addEventListener('connected', async (event) => {
      const data = JSON.parse(event.data);
      console.log('🔗 [DEBUG] SSE connected event:', data);
      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message: '📡 SSE连接已建立',
        type: 'info'
      };
      setLogs(prev => [...prev, newLog]);

      // In debug mode, immediately load project structure
      if (debugMode) {
        console.log('🔗 [DEBUG] Debug mode detected, loading project structure immediately');
        await loadProjectStructure();
      }
    });

    eventSource.addEventListener('phase_start', (event) => {
      const data = JSON.parse(event.data);
      console.log('🚀 [DEBUG] Phase start event:', data);
      const phaseMessages = {
        specify: '正在分析需求并制定技术规格...',
        plan: '正在制定详细的实现计划...',
        implement: '正在生成代码实现...'
      };

      const message = phaseMessages[data.phase as keyof typeof phaseMessages] || '开始新阶段...';

      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message,
        type: 'process'
      };

      setLogs(prev => [...prev, newLog]);
    });

    eventSource.addEventListener('chunk', (event) => {
      // Handle streaming chunks - could show progress indicators
      const data = JSON.parse(event.data);
      console.log('Received chunk:', data.content.length, 'characters');
    });

    eventSource.addEventListener('phase_complete', (event) => {
      const data = JSON.parse(event.data);
      const phaseMessages = {
        specify: '技术规格制定完成',
        plan: '实现计划制定完成',
        implement: '代码实现完成'
      };

      const message = phaseMessages[data.phase as keyof typeof phaseMessages] || '阶段完成';

      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message,
        type: 'info'
      };

      setLogs(prev => [...prev, newLog]);
    });

    eventSource.addEventListener('file_created', async (event) => {
      const data = JSON.parse(event.data);

      // Immediately add the file to the file tree
      setFiles(prevFiles => {
        const addFileToTree = (nodes: FileNode[]): FileNode[] => {
          return nodes.map(node => {
            if (node.type === 'folder') {
              // Check if this file should be added to this folder
              const filePathParts = data.path.split('/');
              if (filePathParts.length > 1 && node.name === filePathParts[0]) {
                const newFile: FileNode = {
                  id: data.path.replace(/\//g, '-'),
                  name: data.filename,
                  type: 'file',
                  content: '', // Will be loaded when clicked or when content is written
                  path: data.path
                };

                // If there's a subfolder structure
                if (filePathParts.length > 2) {
                  const subFolderName = filePathParts[1];
                  const existingSubFolder = node.children?.find(child => child.name === subFolderName && child.type === 'folder');

                  if (existingSubFolder) {
                    return {
                      ...node,
                      children: addFileToTree(node.children || [])
                    };
                  } else {
                    // Create subfolder
                    const subFolder: FileNode = {
                      id: `${node.id}-${subFolderName}`,
                      name: subFolderName,
                      type: 'folder',
                      isOpen: true,
                      children: [newFile],
                      path: filePathParts.slice(0, 2).join('/')
                    };

                    return {
                      ...node,
                      children: [...(node.children || []), subFolder]
                    };
                  }
                } else {
                  // Add directly to this folder
                  return {
                    ...node,
                    children: [...(node.children || []), newFile]
                  };
                }
              }

              // Recursively check children
              return {
                ...node,
                children: node.children ? addFileToTree(node.children) : undefined
              };
            }
            return node;
          });
        };

        // Check if file should be added to root
        const filePathParts = data.path.split('/');
        if (filePathParts.length === 1) {
          const newFile: FileNode = {
            id: data.path.replace(/\//g, '-'),
            name: data.filename,
            type: 'file',
            content: '', // Will be loaded when clicked or when content is written
            path: data.path
          };
          return [...prevFiles, newFile];
        }

        return addFileToTree(prevFiles);
      });

      // Try to load the file content immediately after creation
      try {
        const response = await fetch(`/api/projects/${projectId}/files/${encodeURIComponent(data.path)}`);
        if (response.ok) {
          const content = await response.text();

          // Update the file with its content
          setFiles(prevFiles => {
            const updateFileContent = (nodes: FileNode[]): FileNode[] => {
              return nodes.map(node => {
                if (node.path === data.path) {
                  return { ...node, content };
                }
                if (node.children) {
                  return { ...node, children: updateFileContent(node.children) };
                }
                return node;
              });
            };
            return updateFileContent(prevFiles);
          });

          // If this is the first file created and no file is active, make it active
          if (!activeFileId || activeFileId === '') {
            setActiveFileId(data.path.replace(/\//g, '-'));
          }
        }
      } catch (error) {
        console.warn('Could not load content for newly created file:', data.path, error);
      }

      // Add log entry
      console.log('📁 [DEBUG] File created:', data.filename, 'at path:', data.path);
      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message: `📄 创建文件: ${data.filename} (${data.size_bytes} bytes)`,
        type: 'info'
      };

      setLogs(prev => [...prev, newLog]);
    });

    eventSource.addEventListener('generation_complete', async (event) => {
      const data = JSON.parse(event.data);
      console.log('✅ [DEBUG] Generation complete:', data);

      // Optionally refresh the project structure to ensure we have the final state
      // This handles any files that might have been modified after the initial creation
      if (projectStructureLoaded) {
        console.log('🔄 [DEBUG] Refreshing project structure...');
        await loadProjectStructure();
      }

      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message: `🎉 生成完成! 共创建 ${data.total_files} 个文件`,
        type: 'success'
      };

      setLogs(prev => [...prev, newLog]);
      setProject(prev => ({ ...prev, status: 'completed' }));
    });

    eventSource.addEventListener('generation_error', (event) => {
      const data = JSON.parse(event.data);
      console.error('❌ [DEBUG] Generation error:', data);

      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message: `💥 生成失败: ${data.error}`,
        type: 'process' // Could add error type
      };

      setLogs(prev => [...prev, newLog]);
      setProject(prev => ({ ...prev, status: 'completed' })); // Still mark as completed
    });

    eventSource.addEventListener('heartbeat', (event) => {
      // Heartbeat - no action needed, just keep connection alive
      console.log('Heartbeat received');
    });

    eventSource.onerror = (error) => {
      console.error('❌ [DEBUG] EventSource error:', error);
      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message: '🔌 连接错误，重试中...',
        type: 'info'
      };
      setLogs(prev => [...prev, newLog]);
    };

    return () => {
      console.log('Closing EventSource connection');
      eventSource.close();
    };
  }, [projectId]);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Auto-refresh active file content during generation
  useEffect(() => {
    if (!projectId || !activeFileId || project.status !== 'generating') return;

    // Find the file path for the active file
    const findFilePath = (nodes: FileNode[]): string | undefined => {
      for (const node of nodes) {
        if (node.id === activeFileId && node.type === 'file') {
          return node.path;
        }
        if (node.children) {
          const found = findFilePath(node.children);
          if (found) return found;
        }
      }
      return undefined;
    };

    const filePath = findFilePath(files);
    if (!filePath) return;

    // Refresh content every 2 seconds during generation
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/projects/${projectId}/files/${encodeURIComponent(filePath)}`);
        if (response.ok) {
          const content = await response.text();

          // Update the file content
          setFiles(prevFiles => {
            const updateFileContent = (nodes: FileNode[]): FileNode[] => {
              return nodes.map(node => {
                if (node.id === activeFileId) {
                  return { ...node, content };
                }
                if (node.children) {
                  return { ...node, children: updateFileContent(node.children) };
                }
                return node;
              });
            };
            return updateFileContent(prevFiles);
          });
        }
      } catch (error) {
        // Silently fail - file might not exist yet or network issues
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [projectId, activeFileId, project.status, files]);

  // Helper to flatten tree for simple viewing in this demo
  const getFileContent = (fileId: string): string => {
    const findFile = (nodes: FileNode[]): string | undefined => {
      for (const node of nodes) {
        if (node.id === fileId) return node.content || '';
        if (node.children) {
          const found = findFile(node.children);
          if (found !== undefined) return found;
        }
      }
      return undefined;
    };
    return findFile(files) || '';
  };

  // Load project structure from backend API
  const loadProjectStructure = async (): Promise<void> => {
    try {
      console.log('🔍 [DEBUG] loadProjectStructure called with projectId:', projectId);
      console.log('🔍 [DEBUG] Loading project structure for:', projectId);
      const response = await fetch(`/api/projects/${projectId}`);
      console.log('🔍 [DEBUG] Project structure API response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('🔍 [DEBUG] Loaded project structure:', data);

        // Convert backend tree structure to frontend FileNode format
        const convertToFileNode = (node: any): FileNode => {
          if (node.type === 'file') {
            return {
              id: node.path.replace(/\//g, '-'),
              name: node.name,
              type: 'file',
              content: '', // Will be loaded when clicked
              path: node.path
            };
          } else if (node.type === 'directory') {
            return {
              id: node.path.replace(/\//g, '-') || 'root',
              name: node.name,
              type: 'folder',
              isOpen: true,
              children: node.children ? node.children.map(convertToFileNode) : [],
              path: node.path
            };
          }
          throw new Error(`Unknown node type: ${node.type}`);
        };

        const fileNodes = data.root.children ? data.root.children.map(convertToFileNode) : [];
        setFiles(fileNodes);
        setProjectStructureLoaded(true);
      } else {
        console.error('Failed to load project structure:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading project structure:', error);
    }
  };

  // Load file content from backend API
  const loadFileContent = async (filePath: string): Promise<void> => {
    try {
      console.log('📖 [DEBUG] Loading file content:', filePath);
      const response = await fetch(`/api/projects/${projectId}/files/${encodeURIComponent(filePath)}`);
      console.log('📖 [DEBUG] File content API response status:', response.status);

      if (response.ok) {
        const content = await response.text();
        console.log('📖 [DEBUG] Loaded file content length:', content.length);

        // Update the file content in the tree
        setFiles(prevFiles => {
          const updateFileContent = (nodes: FileNode[]): FileNode[] => {
            return nodes.map(node => {
              if (node.path === filePath) {
                return { ...node, content };
              }
              if (node.children) {
                return { ...node, children: updateFileContent(node.children) };
              }
              return node;
            });
          };
          return updateFileContent(prevFiles);
        });

        setActiveFileId(filePath.replace(/\//g, '-'));
      } else {
        console.error('Failed to load file content:', response.statusText);
      }
    } catch (error) {
      console.error('Error loading file content:', error);
    }
  };

  return (
    <div className="h-screen w-full bg-[#050505] text-zinc-300 flex flex-col font-mono overflow-hidden">
      {/* Top Bar */}
      <header className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-[#080808]">
        <div className="flex items-center gap-4">
           <span className="font-architect font-bold text-lg text-zinc-100">Spec-Kit</span>
           <div className="h-4 w-[1px] bg-white/10"></div>
           <span className="text-xs text-zinc-500 uppercase tracking-widest">{project.name}</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/5 rounded-full">
            <div className={`w-1.5 h-1.5 rounded-full ${project.status === 'generating' ? 'bg-amber-500 animate-pulse' : 'bg-green-500'}`}></div>
            <span className="text-[10px] uppercase tracking-wider text-zinc-400">
              {project.status === 'generating' ? 'BUILDING' : 'READY'}
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar: File Tree */}
        <aside className="w-64 border-r border-white/10 flex flex-col bg-[#050505]">
          <div className="p-3 text-[10px] font-bold text-zinc-600 uppercase tracking-widest border-b border-white/5">
            Explorer
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <FileTree
              nodes={files}
              activeId={activeFileId}
              onSelect={(fileId) => {
                // Find the file path from the file tree
                const findFilePath = (nodes: FileNode[], targetId: string): string | undefined => {
                  for (const node of nodes) {
                    if (node.id === targetId && node.type === 'file') {
                      // Convert id back to file path
                      return node.id.replace(/-/g, '/');
                    }
                    if (node.children) {
                      const found = findFilePath(node.children, targetId);
                      if (found) return found;
                    }
                  }
                  return undefined;
                };

                const filePath = findFilePath(files, fileId);
                if (filePath) {
                  // Always reload content when clicking a file to ensure we have the latest version
                  loadFileContent(filePath);
                } else {
                  setActiveFileId(fileId);
                }
              }}
            />
          </div>
        </aside>

        {/* Main Editor Area */}
        <main className="flex-1 flex flex-col bg-[#050505] relative">
          {/* Tab/Breadcrumb */}
          <div className="h-9 border-b border-white/10 flex items-center px-4 text-xs text-zinc-400 bg-[#080808]">
            <span className="mr-2 opacity-50">PREVIEW</span>
            {getFileContent(activeFileId) ? 'Active File' : 'Select a file'}
          </div>
          
          <div className="flex-1 p-0 relative overflow-hidden">
             {/* Line Numbers Decoration */}
             <div className="absolute left-0 top-0 bottom-0 w-12 border-r border-white/5 bg-[#070707] text-zinc-700 text-xs text-right pr-3 pt-4 select-none leading-6 font-mono">
               {Array.from({length: 20}).map((_, i) => <div key={i}>{i+1}</div>)}
             </div>
             
             {/* Code Content */}
             <textarea 
               className="w-full h-full bg-transparent resize-none outline-none border-none p-4 pl-16 font-mono text-sm leading-6 text-zinc-300"
               value={getFileContent(activeFileId)}
               readOnly
               spellCheck={false}
             />
          </div>

          {/* Bottom Panel: Terminal/Logs */}
          <div className="h-48 border-t border-white/10 bg-[#020202] flex flex-col">
            <div className="h-8 border-b border-white/10 flex items-center px-4 gap-4 bg-[#080808]">
               <button className="text-[10px] uppercase font-bold text-zinc-300 border-b border-white pb-[11px] translate-y-[1px]">Terminal</button>
               <button className="text-[10px] uppercase font-bold text-zinc-600 hover:text-zinc-400 transition-colors">Output</button>
               <button className="text-[10px] uppercase font-bold text-zinc-600 hover:text-zinc-400 transition-colors">Problems</button>
            </div>
            <div className="flex-1 p-4 overflow-y-auto font-mono text-xs space-y-1">
              {logs.map((log) => (
                <div key={log.id} className="flex gap-3 animate-fade-in">
                  <span className="text-zinc-600 shrink-0 select-none">[{log.timestamp}]</span>
                  <span className={`${
                    log.type === 'success' ? 'text-green-400' : 
                    log.type === 'info' ? 'text-blue-400' : 'text-zinc-400'
                  }`}>
                    {log.type === 'process' && <span className="mr-2 text-amber-500">&gt;&gt;</span>}
                    {log.message}
                  </span>
                </div>
              ))}
              <div ref={logsEndRef} />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

// Simple Recursive File Tree Component
const FileTree: React.FC<{ nodes: FileNode[]; activeId: string; onSelect: (id: string) => void; level?: number }> = ({ nodes, activeId, onSelect, level = 0 }) => {
  return (
    <ul className="space-y-0.5">
      {nodes.map(node => (
        <li key={node.id}>
          <div 
            onClick={() => node.type === 'file' && onSelect(node.id)}
            className={`
              flex items-center gap-2 px-2 py-1.5 cursor-pointer rounded-sm select-none text-xs transition-colors
              ${node.id === activeId ? 'bg-white/10 text-white' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5'}
            `}
            style={{ paddingLeft: `${level * 12 + 8}px` }}
          >
            <span className="opacity-70">
              {node.type === 'folder' ? 'DIR' : 'FILE'}
            </span>
            <span className="truncate">{node.name}</span>
          </div>
          {node.children && node.isOpen && (
            <FileTree nodes={node.children} activeId={activeId} onSelect={onSelect} level={level + 1} />
          )}
        </li>
      ))}
    </ul>
  );
};

export default WorkbenchView;