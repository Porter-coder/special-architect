import React from 'react';
import { Folder, FileText, Code2, Zap, CheckCircle, AlertCircle, Loader } from 'lucide-react';

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  created?: string;
}

interface WorkbenchSceneProps {
  files: FileItem[];
  isStreaming: boolean;
  connectionStatus: 'connecting' | 'connected' | 'completed' | 'error';
}

const FileTreeItem: React.FC<{ file: FileItem; depth?: number }> = ({ file, depth = 0 }) => {
  const isFolder = file.type === 'directory';

  return (
    <div className="select-none text-sm">
      <div
        className="flex items-center hover:bg-green-900/20 cursor-pointer py-2 transition-colors duration-200"
        style={{ paddingLeft: `${depth * 16 + 16}px` }}
      >
        <span className={`mr-2 ${isFolder ? 'text-green-400' : 'text-green-600'}`}>
          {isFolder ? <Folder size={14} /> : <FileText size={14} />}
        </span>
        <span className={`font-mono text-sm ${isFolder ? 'text-green-300 font-medium' : 'text-green-500'}`}>
          {file.name}
        </span>
        {!isFolder && file.size && (
          <span className="ml-auto text-green-700 text-xs">
            {file.size} bytes
          </span>
        )}
      </div>
    </div>
  );
};

const StatusIndicator: React.FC<{ status: WorkbenchSceneProps['connectionStatus'] }> = ({ status }) => {
  const configs = {
    connecting: { icon: Loader, text: '连接中...', color: 'text-yellow-400', animate: true },
    connected: { icon: Zap, text: '已连接', color: 'text-green-400', animate: false },
    completed: { icon: CheckCircle, text: '完成', color: 'text-green-500', animate: false },
    error: { icon: AlertCircle, text: '错误', color: 'text-red-400', animate: false }
  };

  const config = configs[status];
  const Icon = config.icon;

  return (
    <div className={`flex items-center gap-2 ${config.color}`}>
      <Icon size={16} className={config.animate ? 'animate-spin' : ''} />
      <span className="text-sm font-mono">{config.text}</span>
    </div>
  );
};

const WorkbenchScene: React.FC<WorkbenchSceneProps> = ({
  files,
  isStreaming,
  connectionStatus
}) => {
  return (
    <div className="w-full h-full flex flex-col bg-black text-green-400 font-mono">
      {/* Header */}
      <div className="h-16 border-b border-green-800 flex items-center justify-between px-6 bg-gray-900/50">
        <div className="flex items-center gap-4">
          <Code2 size={24} className="text-green-400" />
          <h1 className="text-xl font-bold text-green-300">工作台</h1>
        </div>

        <div className="flex items-center gap-4">
          {isStreaming && <StatusIndicator status={connectionStatus} />}
          <div className="text-green-500 text-sm">
            {files.length} 个文件
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* File Explorer */}
        <div className="w-80 border-r border-green-800 bg-gray-900/30">
          <div className="p-4 border-b border-green-800">
            <h2 className="text-green-300 font-semibold mb-2">项目文件</h2>
            {files.length === 0 && isStreaming && (
              <div className="text-green-600 text-sm italic">
                等待文件生成...
              </div>
            )}
          </div>

          <div className="p-2 max-h-full overflow-y-auto">
            {files.map((file, index) => (
              <FileTreeItem key={`${file.path}-${index}`} file={file} />
            ))}
          </div>
        </div>

        {/* Code Editor Placeholder */}
        <div className="flex-1 bg-gray-900/20 flex items-center justify-center">
          <div className="text-center text-green-600">
            <Code2 size={48} className="mx-auto mb-4 opacity-50" />
            <p className="text-lg mb-2">代码编辑器</p>
            <p className="text-sm">选择文件开始编辑</p>
            {files.length > 0 && (
              <div className="mt-4 text-green-500">
                <p>已生成 {files.length} 个文件</p>
                <p className="text-xs mt-1">点击文件查看内容</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="h-12 border-t border-green-800 bg-gray-900/50 px-6 flex items-center justify-between text-xs text-green-600">
        <div>
          实时工作台模式 {isStreaming ? '已激活' : '未激活'}
        </div>
        <div>
          文件实时同步已{connectionStatus === 'connected' ? '启用' : '禁用'}
        </div>
      </div>
    </div>
  );
};

export default WorkbenchScene;
