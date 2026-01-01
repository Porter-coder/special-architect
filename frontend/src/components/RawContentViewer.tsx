"use client";

import React, { useState } from 'react';

interface RawContentItem {
  type: 'thinking' | 'content';
  content: string;
  phase: string;
  timestamp: string;
  raw_type: string;
}

interface RawContentViewerProps {
  rawContent: RawContentItem[];
  isVisible: boolean;
  onClose: () => void;
  currentPhase?: string;
}

const RawContentViewer: React.FC<RawContentViewerProps> = ({
  rawContent,
  isVisible,
  onClose,
  currentPhase
}) => {
  const [selectedType, setSelectedType] = useState<'all' | 'thinking' | 'content'>('all');
  const [selectedPhase, setSelectedPhase] = useState<string>('all');

  if (!isVisible) return null;

  const filteredContent = rawContent.filter(item => {
    const typeMatch = selectedType === 'all' || item.type === selectedType;
    const phaseMatch = selectedPhase === 'all' || item.phase === selectedPhase;
    return typeMatch && phaseMatch;
  });

  const phases = Array.from(new Set(rawContent.map(item => item.phase)));
  const thinkingCount = rawContent.filter(item => item.type === 'thinking').length;
  const contentCount = rawContent.filter(item => item.type === 'content').length;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">🤖 AI 原始内容查看器</h2>
              <p className="text-purple-100 text-sm mt-1">
                查看 AI 的思考过程和生成的内容
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-gray-50 p-4 border-b">
          <div className="flex flex-wrap gap-4 items-center">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                内容类型
              </label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value as any)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="all">全部 ({rawContent.length})</option>
                <option value="thinking">思考过程 ({thinkingCount})</option>
                <option value="content">生成内容 ({contentCount})</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                阶段筛选
              </label>
              <select
                value={selectedPhase}
                onChange={(e) => setSelectedPhase(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="all">全部阶段</option>
                {phases.map(phase => (
                  <option key={phase} value={phase}>{phase}</option>
                ))}
              </select>
            </div>

            <div className="text-sm text-gray-600 self-end">
              显示 {filteredContent.length} / {rawContent.length} 项内容
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-4">
            {filteredContent.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <div className="text-4xl mb-2">📭</div>
                <p>没有找到匹配的内容</p>
              </div>
            ) : (
              filteredContent.map((item, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 ${
                    item.type === 'thinking'
                      ? 'border-blue-200 bg-blue-50'
                      : 'border-green-200 bg-green-50'
                  }`}
                >
                  {/* Header */}
                  <div className="flex justify-between items-center mb-3">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        item.type === 'thinking'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {item.type === 'thinking' ? '🧠 思考' : '💻 代码'}
                      </span>
                      <span className="text-sm text-gray-600">
                        阶段: {item.phase}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {item.timestamp || '实时'}
                    </span>
                  </div>

                  {/* Content */}
                  <div className={`rounded p-3 font-mono text-sm ${
                    item.type === 'thinking'
                      ? 'bg-blue-100 text-blue-900'
                      : 'bg-green-100 text-green-900'
                  }`}>
                    <pre className="whitespace-pre-wrap break-words">
                      {item.content}
                    </pre>
                  </div>

                  {/* Metadata */}
                  <div className="mt-2 text-xs text-gray-500 flex justify-between">
                    <span>类型: {item.raw_type}</span>
                    <span>{item.content.length} 字符</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-4 py-3 rounded-b-lg border-t flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <span className="font-medium">当前阶段:</span> {currentPhase || '未知'}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => {
                const content = filteredContent
                  .map(item => `[${item.type.toUpperCase()}] ${item.content}`)
                  .join('\n\n');
                navigator.clipboard?.writeText(content);
              }}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded text-sm"
            >
              📋 复制内容
            </button>
            <button
              onClick={onClose}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded text-sm"
            >
              关闭查看器
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RawContentViewer;
