import React from 'react';

interface ProjectFile {
  name: string;
  size: number;
  language?: string;
  type: 'file' | 'directory';
  children?: ProjectFile[];
}

interface GeneratedProject {
  id: string;
  project_name: string;
  created_at: string;
  file_structure: ProjectFile;
  dependencies: string[];
  total_files: number;
  total_size_bytes: number;
  syntax_validated: boolean;
  main_file: string;
}

interface ProjectDownloaderProps {
  project: GeneratedProject | null;
  onDownload: (projectId: string) => void;
  isDownloading: boolean;
}

const ProjectDownloader: React.FC<ProjectDownloaderProps> = ({
  project,
  onDownload,
  isDownloading
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const renderFileTree = (files: ProjectFile[], level = 0): JSX.Element[] => {
    return files.map((file, index) => (
      <div key={index} style={{ paddingLeft: `${level * 20}px` }}>
        <div className="flex items-center space-x-2 py-1">
          <span className={`text-sm ${
            file.type === 'directory' ? 'text-blue-600 font-medium' : 'text-gray-700'
          }`}>
            {file.type === 'directory' ? '📁' : '📄'} {file.name}
          </span>
          {file.type === 'file' && file.size && (
            <span className="text-xs text-gray-500">
              ({formatFileSize(file.size)})
            </span>
          )}
          {file.language && (
            <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
              {file.language}
            </span>
          )}
        </div>
        {file.children && renderFileTree(file.children, level + 1)}
      </div>
    ));
  };

  if (!project) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">
        生成的项目
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Project Info */}
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">项目信息</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">项目名称:</span>
                <span className="font-mono">{project.project_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">创建时间:</span>
                <span>{new Date(project.created_at).toLocaleString('zh-CN')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">文件数量:</span>
                <span>{project.total_files}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">总大小:</span>
                <span>{formatFileSize(project.total_size_bytes)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">语法验证:</span>
                <span className={project.syntax_validated ? 'text-green-600' : 'text-red-600'}>
                  {project.syntax_validated ? '✓ 通过' : '✗ 失败'}
                </span>
              </div>
            </div>
          </div>

          {/* Dependencies */}
          {project.dependencies.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-700 mb-2">依赖项</h4>
              <div className="flex flex-wrap gap-2">
                {project.dependencies.map((dep, index) => (
                  <span
                    key={index}
                    className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded"
                  >
                    {dep}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Download Button */}
          <button
            onClick={() => onDownload(project.id)}
            disabled={isDownloading}
            className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
              isDownloading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
            }`}
          >
            {isDownloading ? '下载中...' : '下载项目'}
          </button>
        </div>

        {/* File Structure */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">文件结构</h4>
          <div className="bg-gray-50 rounded-lg p-4 max-h-80 overflow-y-auto">
            <div className="text-sm">
              {renderFileTree([project.file_structure])}
            </div>
          </div>

          {project.main_file && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center space-x-2">
                <span className="text-blue-600 font-medium">🏠 主文件:</span>
                <span className="font-mono text-sm">{project.main_file}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProjectDownloader;
