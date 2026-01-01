/**
 * AI Code Flow - 主页面
 *
 * 提供代码生成的 Web 界面，具有教育性的过程透明度。
 */

import { useState } from 'react';
import Head from 'next/head';

export default function Home() {
  const [userInput, setUserInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentPhase, setCurrentPhase] = useState('');
  const [phaseMessage, setPhaseMessage] = useState('');
  const [thinkingTrace, setThinkingTrace] = useState('');
  const [generatedFiles, setGeneratedFiles] = useState<any>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!userInput.trim()) {
      setError('请输入代码生成需求');
      return;
    }

    setIsGenerating(true);
    setError('');
    setCurrentPhase('');
    setPhaseMessage('');
    setThinkingTrace('');
    setGeneratedFiles(null);

    try {
      // 启动代码生成
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '请求失败');
      }

      const data = await response.json();
      const requestId = data.request_id;

      // 监听进度更新
      await listenToProgress(requestId);

    } catch (err: any) {
      setError(err.message || '生成失败，请稍后重试');
      setIsGenerating(false);
    }
  };

  const listenToProgress = async (requestId: string) => {
    const eventSource = new EventSource(`/api/generate/${requestId}/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (event.type === 'phase') {
        setCurrentPhase(data.phase);
        setPhaseMessage(data.message);
      } else if (event.type === 'thinking') {
        setThinkingTrace(prev => prev + data.content);
      } else if (event.type === 'complete') {
        // 生成完成，获取文件
        fetchGeneratedFiles(requestId);
        eventSource.close();
      } else if (event.type === 'error') {
        setError(data);
        setIsGenerating(false);
        eventSource.close();
      }
    };

    eventSource.onerror = () => {
      setError('连接断开，请刷新页面重试');
      setIsGenerating(false);
      eventSource.close();
    };
  };

  const fetchGeneratedFiles = async (requestId: string) => {
    try {
      const response = await fetch(`/api/generate/${requestId}/files`);
      if (response.ok) {
        const data = await response.json();
        setGeneratedFiles(data);
      } else {
        setError('获取生成文件失败');
      }
    } catch (err) {
      setError('获取生成文件失败');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadFile = (filePath: string, content: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filePath;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>AI Code Flow - AI 代码生成</title>
        <meta name="description" content="通过 AI 生成代码，了解软件工程过程" />
      </Head>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Code Flow
          </h1>
          <p className="text-xl text-gray-600">
            通过 AI 生成代码，了解软件工程的核心过程
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="mb-4">
            <label htmlFor="userInput" className="block text-sm font-medium text-gray-700 mb-2">
              描述您想要生成的代码
            </label>
            <textarea
              id="userInput"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="例如：帮我写个贪吃蛇游戏"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              disabled={isGenerating}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={isGenerating || !userInput.trim()}
            className={`w-full py-2 px-4 rounded-md font-medium ${
              isGenerating || !userInput.trim()
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }`}
          >
            {isGenerating ? '正在生成代码...' : '开始生成'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {(currentPhase || phaseMessage) && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
            <h3 className="text-lg font-medium text-blue-900 mb-2">
              当前阶段: {currentPhase}
            </h3>
            <p className="text-blue-800">{phaseMessage}</p>
          </div>
        )}

        {thinkingTrace && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-6">
            <h3 className="text-lg font-medium text-green-900 mb-2">
              AI 思考过程
            </h3>
            <pre className="text-green-800 whitespace-pre-wrap text-sm">
              {thinkingTrace}
            </pre>
          </div>
        )}

        {generatedFiles && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <h3 className="text-lg font-medium text-green-900 mb-4">
              生成完成！项目：{generatedFiles.project_name}
            </h3>

            <div className="space-y-3">
              {generatedFiles.files.map((file: any, index: number) => (
                <div key={index} className="flex items-center justify-between bg-white p-3 rounded border">
                  <span className="font-mono text-sm">{file.path}</span>
                  <div className="space-x-2">
                    <button
                      onClick={() => downloadFile(file.path, file.content)}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      下载
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 p-4 bg-gray-100 rounded">
              <p className="text-sm text-gray-600">
                💡 <strong>主文件：</strong>{generatedFiles.main_file}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                运行命令：python {generatedFiles.main_file}
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
