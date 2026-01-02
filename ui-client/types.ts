export type ViewState = 'landing' | 'workbench';

export interface FileNode {
  id: string;
  name: string;
  type: 'file' | 'folder';
  content?: string;
  children?: FileNode[];
  isOpen?: boolean;
  path?: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'process';
}

export interface ProjectState {
  name: string;
  status: 'idle' | 'generating' | 'completed';
}