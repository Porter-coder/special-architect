import React from 'react';

interface StreamChunk {
  type: 'phase_update' | 'content_chunk' | 'completion' | 'error';
  phase?: string;
  message?: string;
  content?: string;
  error?: string;
}

interface StreamingDisplayProps {
  chunks: StreamChunk[];
  isActive: boolean;
}

const StreamingDisplay: React.FC<StreamingDisplayProps> = ({ chunks, isActive }) => {
  const getChunkColor = (type: string) => {
    switch (type) {
      case 'phase_update':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'content_chunk':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'completion':
        return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'error':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">
        生成进度 {isActive && <span className="text-blue-500 animate-pulse">●</span>}
      </h3>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {chunks.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            等待代码生成请求...
          </div>
        ) : (
          chunks.map((chunk, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getChunkColor(chunk.type)}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    chunk.type === 'error' ? 'bg-red-400' :
                    chunk.type === 'completion' ? 'bg-purple-400' :
                    'bg-current'
                  }`} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium uppercase tracking-wide">
                      {chunk.type === 'phase_update' && '阶段更新'}
                      {chunk.type === 'content_chunk' && '内容块'}
                      {chunk.type === 'completion' && '完成'}
                      {chunk.type === 'error' && '错误'}
                    </span>
                    {chunk.phase && (
                      <span className="text-xs bg-white bg-opacity-50 px-2 py-1 rounded">
                        {chunk.phase}
                      </span>
                    )}
                  </div>

                  <div className="text-sm">
                    {chunk.message && <p className="whitespace-pre-wrap">{chunk.message}</p>}
                    {chunk.content && (
                      <pre className="whitespace-pre-wrap font-mono text-xs bg-white bg-opacity-50 p-2 rounded mt-2 overflow-x-auto">
                        {chunk.content}
                      </pre>
                    )}
                    {chunk.error && <p className="font-medium">{chunk.error}</p>}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default StreamingDisplay;
