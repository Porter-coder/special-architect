import React, { useState } from 'react';
import { Folder, FileText, Download, ChevronRight, ChevronDown, Layers, Code2 } from 'lucide-react';
import { MOCK_FILE_TREE, MOCK_CODE_CONTENT } from '../constants';
import { FileNode } from '../types';

interface SceneWorkbenchProps {
  onReset: () => void;
}

const FileTreeItem: React.FC<{ node: FileNode; depth: number }> = ({ node, depth }) => {
  const [isOpen, setIsOpen] = useState(true);
  const isFolder = node.type === 'folder';
  
  return (
    <div className="select-none text-sm">
      <div 
        className="flex items-center hover:bg-white/5 cursor-pointer py-1.5 transition-colors duration-200"
        style={{ paddingLeft: `${depth * 16 + 16}px` }}
        onClick={() => isFolder && setIsOpen(!isOpen)}
      >
        <span className="mr-2 text-morandi-sub opacity-70">
            {isFolder ? (
                isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />
            ) : <span className="w-[12px] inline-block"/>}
        </span>
        <span className={`mr-2 ${isFolder ? 'text-morandi-text/80' : 'text-morandi-sub/60'}`}>
            {isFolder ? <Folder size={13} strokeWidth={1.5} /> : <FileText size={13} strokeWidth={1.5} />}
        </span>
        <span className={`font-mono text-xs tracking-wide ${isFolder ? 'text-morandi-text/90 font-medium' : 'text-morandi-sub'}`}>
            {node.name}
        </span>
      </div>
      {isFolder && isOpen && node.children && (
        <div>
          {node.children.map((child, idx) => (
            <FileTreeItem key={idx} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

const SceneWorkbench: React.FC<SceneWorkbenchProps> = ({ onReset }) => {
  return (
    <div className="w-full h-full flex flex-col bg-morandi-bg text-morandi-text fade-in">
      
      {/* Navbar */}
      <div className="h-16 border-b border-morandi-border flex items-center justify-between px-6 md:px-8 bg-morandi-bg/50 backdrop-blur-sm z-20">
        <div className="flex items-center gap-4">
            <div className="w-8 h-8 bg-morandi-surface border border-morandi-border flex items-center justify-center rounded-sm">
                <Code2 size={16} className="text-morandi-text/80" />
            </div>
            <div>
                <h1 className="font-serif text-lg text-morandi-text tracking-tight">SpecKit Lite</h1>
                <p className="text-[10px] text-morandi-sub tracking-widest uppercase">架构生成完毕</p>
            </div>
        </div>
        <div className="flex gap-4">
             <button 
                onClick={onReset}
                className="text-morandi-sub hover:text-morandi-text text-xs tracking-wider font-medium px-4 py-2 transition-colors"
            >
                重新构建
            </button>
            <button 
                className="flex items-center gap-2 bg-[#D4D4D8] text-morandi-bg px-5 py-2 text-xs font-semibold tracking-wider rounded-sm hover:bg-white transition-colors shadow-lg shadow-black/10"
                onClick={() => alert("正在下载 generated_project_20260102.zip ...")}
            >
                下载项目
                <Download size={12} />
            </button>
        </div>
      </div>

      {/* Workspace */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Sidebar */}
        <div className="w-72 border-r border-morandi-border bg-morandi-bg/30 flex flex-col hidden md:flex">
            <div className="p-4 border-b border-morandi-border/50">
                <span className="text-[10px] font-bold text-morandi-sub uppercase tracking-widest flex items-center gap-2">
                    <Layers size={10} /> 项目文件
                </span>
            </div>
            <div className="flex-1 overflow-y-auto py-2 custom-scrollbar">
                {MOCK_FILE_TREE.map((node, idx) => (
                    <FileTreeItem key={idx} node={node} depth={0} />
                ))}
            </div>
            <div className="p-4 border-t border-morandi-border/30">
                 <div className="text-[10px] text-morandi-sub/40 font-mono">
                    Mode: S.P.E.C.I.A.L.<br/>
                    Status: Ready
                 </div>
            </div>
        </div>

        {/* Editor Area */}
        <div className="flex-1 flex flex-col min-w-0 bg-[#151515]">
            {/* Tab Bar */}
            <div className="flex border-b border-morandi-border bg-morandi-bg">
                <div className="px-6 py-3 border-r border-morandi-border bg-[#151515] text-xs text-morandi-text font-medium flex items-center gap-2 border-t-2 border-t-morandi-text/20">
                    <FileText size={12} className="text-morandi-sub" />
                    main.py
                </div>
                <div className="px-6 py-3 border-r border-morandi-border/30 text-xs text-morandi-sub/60 font-medium flex items-center gap-2 hover:bg-white/5 cursor-pointer transition-colors">
                    spec.md
                </div>
                <div className="px-6 py-3 border-r border-morandi-border/30 text-xs text-morandi-sub/60 font-medium flex items-center gap-2 hover:bg-white/5 cursor-pointer transition-colors">
                    plan.md
                </div>
            </div>
            
            {/* Code Content */}
            <div className="flex-1 overflow-auto p-8 custom-scrollbar relative">
                <div className="absolute top-8 left-4 bottom-8 w-px bg-white/5"></div>
                <pre className="font-mono text-sm leading-relaxed pl-6">
                    {MOCK_CODE_CONTENT.split('\n').map((line, i) => (
                        <div key={i} className="table-row">
                             {/* Muted line numbers */}
                            <span className="table-cell select-none text-morandi-sub/20 w-8 text-right pr-6 text-xs">{i + 1}</span>
                            {/* Python Syntax Highlighting Simulation */}
                            <span className="table-cell" dangerouslySetInnerHTML={{ __html: highlightPython(line) }} />
                        </div>
                    ))}
                </pre>
            </div>
        </div>
      </div>
    </div>
  );
};

// Python-ish Syntax Highlighting for Morandi Theme
function highlightPython(code: string) {
    let html = code
        .replace(/(import|from|class|def|return|if|else|super|print|try|except)/g, '<span style="color: #81A1C1;">$1</span>') // Keywords (Soft Blue)
        .replace(/('.*?')|(".*?")/g, '<span style="color: #A3BE8C;">$1</span>') // Strings (Soft Green)
        .replace(/(#.*)/g, '<span style="color: #606060; font-style: italic;">$1</span>') // Comments (Dark Grey)
        .replace(/(self|True|False|None)/g, '<span style="color: #D08770;">$1</span>') // Built-ins/Self (Soft Orange/Red)
        .replace(/(SpecParser|SpecialArchitectApp|QApplication|QMainWindow|QLabel)/g, '<span style="color: #EBCB8B;">$1</span>') // Classes (Soft Yellow)
        .replace(/(__init__|setup_ui)/g, '<span style="color: #88C0D0;">$1</span>') // Methods (Cyan)
        .replace(/({|}|<|>|\(|\)|\[|\]|=|\.)/g, '<span style="color: #5E81AC;">$1</span>'); // Punctuation
    return html;
}

export default SceneWorkbench;