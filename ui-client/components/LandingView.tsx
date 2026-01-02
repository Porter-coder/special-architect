import React, { useState } from 'react';

interface LandingViewProps {
  onGenerate: (prompt: string) => void;
  onDebugMode: (projectId: string) => void;
}

const LandingView: React.FC<LandingViewProps> = ({ onGenerate, onDebugMode }) => {
  console.log('🎨🎨🎨 LANDING VIEW RENDERED');

  const [input, setInput] = useState('');
  const [debugProjectId, setDebugProjectId] = useState('');
  const [showDebug, setShowDebug] = useState(false);

  const handleSubmit = () => {
    console.log('🚀🚀🚀 GENERATE BUTTON CLICKED');
    if (!input.trim()) return;
    onGenerate(input);
  };

  const handleDebugSubmit = () => {
    console.log('🔧🔧🔧 DEBUG LOAD BUTTON CLICKED with projectId:', debugProjectId);
    console.log('🔧🔧🔧 debugProjectId.trim():', debugProjectId.trim());
    console.log('🔧🔧🔧 debugProjectId.trim() length:', debugProjectId.trim().length);

    // Hardcode project ID for testing if input is empty
    const testProjectId = debugProjectId.trim() || '31ae5634-0c4d-4a05-a776-661519097618';
    console.log('🔧🔧🔧 Using project ID:', testProjectId);

    onDebugMode(testProjectId);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.metaKey) {
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden bg-[#050505] selection:bg-white/20 selection:text-white">
      {/* Decorative Grid Background */}
      <div className="absolute inset-0 grid grid-cols-[repeat(40,minmax(0,1fr))] opacity-[0.03] pointer-events-none">
        {Array.from({ length: 40 }).map((_, i) => (
          <div key={i} className="border-r border-white h-full" />
        ))}
      </div>

      <div className="z-10 w-full max-w-4xl flex flex-col items-center gap-12 animate-fade-in-up">
        
        {/* Header Section */}
        <div className="text-center space-y-6">
          <div className="inline-block px-3 py-1 border border-white/20 rounded-full">
            <span className="text-[10px] tracking-[0.2em] text-zinc-400 uppercase">
              18岁口腔医学生的创造力革命
            </span>
          </div>

          {/* Debug Mode Toggle */}
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors underline"
          >
            {showDebug ? '隐藏调试模式' : '显示调试模式'}
          </button>
          
          <div className="space-y-2">
            <h1 className="text-5xl md:text-7xl font-architect font-bold text-zinc-100 tracking-tighter">
              用积木组装软件
            </h1>
            <div className="flex items-center justify-center gap-4 text-zinc-500">
              <div className="h-[1px] w-12 bg-zinc-800"></div>
              <h2 className="text-xs tracking-[0.4em] font-light">
                PORTER · S.P.E.C.I.A.L. ARCHITECT
              </h2>
              <div className="h-[1px] w-12 bg-zinc-800"></div>
            </div>
          </div>
        </div>

        {/* Input Terminal Area */}
        <div className="w-full relative group">
          {/* Subtle glow effect */}
          <div className="absolute -inset-0.5 bg-gradient-to-r from-zinc-800 to-zinc-900 rounded-sm opacity-20 blur transition duration-500 group-hover:opacity-40"></div>
          
          <div className="relative bg-[#080808] border border-white/10 p-6 md:p-10 shadow-2xl">
            <div className="flex flex-col h-64">
              <div className="flex items-center gap-2 mb-4 text-zinc-500 text-xs select-none">
                <span className="text-green-500/50">●</span>
                <span>SPEC_INPUT_MODE</span>
                <span className="flex-1 h-[1px] bg-white/5 ml-2"></span>
              </div>
              
              <div className="flex h-full">
                <span className="text-zinc-600 mr-3 mt-1 select-none">{'>'}</span>
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="w-full h-full bg-transparent border-none outline-none resize-none text-zinc-300 text-lg md:text-xl font-mono leading-relaxed placeholder:text-zinc-700"
                  placeholder="告诉我想做什么。不需要代码，只需要你的意图..."
                  spellCheck={false}
                  autoFocus
                />
              </div>

              <div className="absolute bottom-6 right-6">
                <button
                  onClick={handleSubmit}
                  disabled={!input.trim()}
                  className="group relative px-6 py-2 bg-zinc-100 text-zinc-950 font-medium text-sm hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    点火起航 <span className="transition-transform group-hover:translate-x-1">→</span>
                  </span>
                </button>
              </div>
            </div>
          </div>
          
          {/* Decorative Technical Markers */}
          <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-zinc-500"></div>
          <div className="absolute -top-1 -right-1 w-2 h-2 border-t border-r border-zinc-500"></div>
          <div className="absolute -bottom-1 -left-1 w-2 h-2 border-b border-l border-zinc-500"></div>
          <div className="absolute -bottom-1 -right-1 w-2 h-2 border-b border-r border-zinc-500"></div>
        </div>

        {/* Debug Mode Input */}
        {showDebug && (
          <div className="w-full max-w-md mx-auto">
            <div className="bg-[#080808] border border-white/10 p-4 rounded-sm">
              <div className="text-xs text-zinc-500 mb-2 font-mono">Debug Mode - Enter Project ID</div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={debugProjectId}
                  onChange={(e) => {
                    console.log('🔤 INPUT CHANGED:', e.target.value);
                    console.log('🔤 Current debugProjectId:', debugProjectId);
                    setDebugProjectId(e.target.value);
                    console.log('🔤 After set, debugProjectId should be:', e.target.value);
                  }}
                  placeholder="e.g., 31ae5634-0c4d-4a05-a776-661519097618"
                  className="flex-1 bg-transparent border border-white/10 rounded px-2 py-1 text-xs font-mono text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500"
                />
                <button
                  onClick={() => {
                    console.log('🖱️🖱️🖱️ LOAD BUTTON CLICKED - NO CONDITIONS');
                    handleDebugSubmit();
                  }}
                  className="px-3 py-1 bg-zinc-700 text-zinc-300 text-xs font-mono hover:bg-zinc-600 transition-colors"
                >
                  Load
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Footer Quote */}
        <div className="mt-8 text-center opacity-40 hover:opacity-80 transition-opacity duration-700">
          <p className="text-xs font-mono text-zinc-500">
            "AI 时代的掠夺者，拒绝背诵该死的语法。"
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingView;