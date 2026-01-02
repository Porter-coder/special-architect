export type Scene = 'IDLE' | 'WAITING' | 'WORKBENCH';

export interface FileNode {
  name: string;
  type: 'folder' | 'file';
  children?: FileNode[];
}

export interface ManifestoItem {
  main: string;
  sub: string;
}