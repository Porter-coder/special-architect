import React, { useState } from 'react';

interface CodeGeneratorProps {
  onGenerate: (request: string) => void;
  isGenerating: boolean;
}

const CodeGenerator: React.FC<CodeGeneratorProps> = ({ onGenerate, isGenerating }) => {
  const [userInput, setUserInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userInput.trim() && !isGenerating) {
      onGenerate(userInput.trim());
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        AI 代码生成器
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="userInput" className="block text-sm font-medium text-gray-700 mb-2">
            描述您想要生成的代码
          </label>
          <textarea
            id="userInput"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="例如：帮我写个贪吃蛇游戏"
            className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={isGenerating}
          />
        </div>

        <button
          type="submit"
          disabled={!userInput.trim() || isGenerating}
          className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
            !userInput.trim() || isGenerating
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
          }`}
        >
          {isGenerating ? '正在生成代码...' : '生成代码'}
        </button>
      </form>
    </div>
  );
};

export default CodeGenerator;
