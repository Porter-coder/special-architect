import React, { useState } from 'react';
import { ArrowRight, Quote } from 'lucide-react';

interface SceneIdleProps {
  onStart: () => void;
}

const SceneIdle: React.FC<SceneIdleProps> = ({ onStart }) => {
  const [input, setInput] = useState('');

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.metaKey) {
      onStart();
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-8 bg-morandi-bg text-morandi-text relative z-10">
      <div className="max-w-2xl w-full flex flex-col items-center fade-in">
        
        {/* Identity Badge */}
        <div className="mb-6 px-4 py-1 border border-morandi-border rounded-full bg-white/5 backdrop-blur-md">
            <span className="text-[10px] tracking-[0.2em] text-morandi-sub uppercase">
                18岁口腔医学生的创造力革命
            </span>
        </div>

        {/* Header */}
        <h1 className="font-serif text-4xl md:text-6xl mb-4 text-morandi-text font-medium tracking-tight text-center leading-tight">
          用积木<br/>组装软件
        </h1>
        
        <div className="flex items-center gap-3 mb-12 opacity-80">
            <div className="h-px w-8 bg-morandi-sub"></div>
            <p className="font-sans text-morandi-sub text-xs md:text-sm tracking-widest uppercase">
                Porter · S.P.E.C.I.A.L. Architect
            </p>
            <div className="h-px w-8 bg-morandi-sub"></div>
        </div>

        {/* Input Card */}
        <div className="w-full bg-morandi-surface rounded-sm p-8 border border-morandi-border transition-all duration-500 focus-within:border-white/20 shadow-2xl shadow-black/20">
          <div className="mb-4 flex gap-2 text-xs text-morandi-sub/60 font-mono">
            <span>&gt;</span>
            <span>SPEC_INPUT_MODE</span>
          </div>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="告诉我你的点子。不需要代码，只需要你的意图..."
            className="w-full h-32 bg-transparent border-b border-morandi-border focus:border-morandi-text text-morandi-text placeholder-morandi-sub/30 font-sans text-lg outline-none resize-none transition-colors duration-300 leading-relaxed"
            autoFocus
          />
          
          <div className="mt-8 flex justify-between items-center">
             <div className="flex flex-col gap-1">
                 <span className="text-[10px] text-morandi-sub font-mono opacity-50 uppercase tracking-wider">
                   Spec Kit Lite v1.0
                 </span>
             </div>
             
             <button 
               onClick={onStart}
               disabled={!input.trim()}
               className={`
                 group flex items-center gap-3 px-8 py-3 bg-[#D4D4D8] hover:bg-white 
                 text-morandi-bg text-sm font-semibold tracking-wide rounded-sm transition-all duration-300
                 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg
               `}
             >
               点火起航
               <ArrowRight size={14} className="opacity-70 group-hover:translate-x-1 transition-transform" />
             </button>
          </div>
        </div>

        {/* Footer Manifesto */}
        <div className="mt-16 text-center fade-in-delayed max-w-lg">
           <p className="text-sm text-morandi-sub/60 font-serif italic leading-relaxed">
             "AI 时代的掠夺者，拒绝背诵该死的语法。"
           </p>
        </div>

      </div>
    </div>
  );
};

export default SceneIdle;