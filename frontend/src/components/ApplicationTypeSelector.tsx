import React, { useState, useEffect } from 'react';

interface ApplicationType {
  type: string;
  name: string;
  description: string;
  complexity: string;
}

interface ApplicationTypeSelectorProps {
  onApplicationTypeChange: (type: string) => void;
  selectedType?: string;
}

const ApplicationTypeSelector: React.FC<ApplicationTypeSelectorProps> = ({
  onApplicationTypeChange,
  selectedType = ''
}) => {
  const [applicationTypes, setApplicationTypes] = useState<ApplicationType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Default application types (fallback if API fails)
  const defaultTypes: ApplicationType[] = [
    {
      type: 'game',
      name: '游戏',
      description: '创建交互式游戏，如贪吃蛇、俄罗斯方块等',
      complexity: 'simple'
    },
    {
      type: 'web_app',
      name: 'Web应用',
      description: '开发网站、Web API或全栈应用',
      complexity: 'medium'
    },
    {
      type: 'data_processing',
      name: '数据处理',
      description: '数据分析、可视化、机器学习应用',
      complexity: 'complex'
    },
    {
      type: 'utility',
      name: '实用工具',
      description: '命令行工具、自动化脚本、文件处理',
      complexity: 'simple'
    },
    {
      type: 'educational',
      name: '教学示例',
      description: '编程教学演示和学习辅助工具',
      complexity: 'simple'
    }
  ];

  useEffect(() => {
    // Try to fetch application types from API
    fetchApplicationTypes();
  }, []);

  const fetchApplicationTypes = async () => {
    try {
      // TODO: Replace with actual API endpoint when backend supports it
      // const response = await fetch('/api/application-types');
      // const data = await response.json();

      // For now, use default types
      setApplicationTypes(defaultTypes);
      setLoading(false);
    } catch (err) {
      console.warn('Failed to fetch application types, using defaults:', err);
      setApplicationTypes(defaultTypes);
      setLoading(false);
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'simple': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'complex': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getComplexityText = (complexity: string) => {
    switch (complexity) {
      case 'simple': return '简单';
      case 'medium': return '中等';
      case 'complex': return '复杂';
      default: return '未知';
    }
  };

  if (loading) {
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">应用类型</h3>
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-gray-800">应用类型</h3>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">加载应用类型失败: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6">
      <h3 className="text-lg font-semibold mb-3 text-gray-800">应用类型</h3>
      <p className="text-sm text-gray-600 mb-4">
        选择您要创建的应用类型，这将帮助AI为您推荐合适的框架和技术栈。
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {applicationTypes.map((appType) => (
          <div
            key={appType.type}
            className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 hover:shadow-md ${
              selectedType === appType.type
                ? 'border-blue-500 bg-blue-50 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => onApplicationTypeChange(appType.type)}
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium text-gray-900">{appType.name}</h4>
              <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getComplexityColor(appType.complexity)}`}>
                {getComplexityText(appType.complexity)}
              </span>
            </div>

            <p className="text-sm text-gray-600 leading-relaxed">
              {appType.description}
            </p>

            {selectedType === appType.type && (
              <div className="mt-3 flex items-center text-blue-600">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="text-sm font-medium">已选择</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedType && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            <strong>已选择:</strong> {
              applicationTypes.find(t => t.type === selectedType)?.name || selectedType
            }
          </p>
          <p className="text-xs text-blue-600 mt-1">
            AI将根据您的选择优化代码生成提示和推荐技术栈。
          </p>
        </div>
      )}
    </div>
  );
};

export default ApplicationTypeSelector;
