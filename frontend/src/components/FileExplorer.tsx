import React from 'react';
import { Folder, FileText } from 'lucide-react';

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  created?: string;
}

interface FileExplorerProps {
  files: FileItem[];
  onFileSelect?: (file: FileItem) => void;
  selectedFile?: FileItem | null;
}

const FileTreeItem: React.FC<{
  file: FileItem;
  depth?: number;
  onSelect?: (file: FileItem) => void;
  selectedFile?: FileItem | null;
}> = ({ file, depth = 0, onSelect, selectedFile }) => {
  const isFolder = file.type === 'directory';
  const isSelected = selectedFile?.path === file.path;

  return (
    <div className="select-none">
      <div
        className={`flex items-center hover:bg-green-900/30 cursor-pointer py-1.5 px-2 transition-colors duration-200 ${
          isSelected ? 'bg-green-900/50 border-l-2 border-green-400' : ''
        }`}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => onSelect?.(file)}
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

const FileExplorer: React.FC<FileExplorerProps> = ({
  files,
  onFileSelect,
  selectedFile
}) => {
  return (
    <div className="w-full h-full bg-gray-900/30 border-r border-green-800">
      <div className="p-4 border-b border-green-800">
        <h2 className="text-green-300 font-semibold">文件资源管理器</h2>
        <div className="text-green-600 text-sm mt-1">
          {files.length} 个文件
        </div>
      </div>

      <div className="overflow-y-auto max-h-full">
        {files.length === 0 ? (
          <div className="p-4 text-center text-green-700">
            <FileText size={32} className="mx-auto mb-2 opacity-50" />
            <p className="text-sm">等待文件生成...</p>
          </div>
        ) : (
          files.map((file, index) => (
            <FileTreeItem
              key={`${file.path}-${index}`}
              file={file}
              onSelect={onFileSelect}
              selectedFile={selectedFile}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default FileExplorer;
