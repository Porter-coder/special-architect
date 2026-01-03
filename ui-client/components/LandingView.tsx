import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface LandingViewProps {
  onGenerate: (prompt: string) => void;
  onDebugMode: (projectId: string) => void;
}

// Animated Text Component for individual letters
const AnimatedText: React.FC<{ text: string; delay?: number }> = ({ text, delay = 0 }) => {
  const letters = text.split('');

  return (
    <span className="inline-block overflow-hidden">
      {letters.map((letter, index) => (
        <motion.span
          key={index}
          initial={{ y: '100%', opacity: 0 }}
          animate={{ y: '0%', opacity: 1 }}
          transition={{
            duration: 0.8,
            delay: delay + index * 0.05,
            ease: [0.25, 0.46, 0.45, 0.94]
          }}
          className="inline-block"
        >
          {letter === ' ' ? '\u00A0' : letter}
        </motion.span>
      ))}
    </span>
  );
};

// Typewriter Effect Component
const TypewriterText: React.FC<{ texts: string[]; delay?: number }> = ({ texts, delay = 1000 }) => {
  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const text = texts[currentTextIndex];
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        // Typing
        if (currentText.length < text.length) {
          setCurrentText(text.substring(0, currentText.length + 1));
        } else {
          // Pause before deleting
          setTimeout(() => setIsDeleting(true), 2000);
        }
      } else {
        // Deleting
        if (currentText.length > 0) {
          setCurrentText(currentText.substring(0, currentText.length - 1));
        } else {
          setIsDeleting(false);
          setCurrentTextIndex((prev) => (prev + 1) % texts.length);
        }
      }
    }, isDeleting ? 50 : 100);

    return () => clearTimeout(timeout);
  }, [currentText, currentTextIndex, isDeleting, texts]);

  return (
    <span className="text-zinc-700">
      {currentText}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
        className="inline-block w-[2px] h-[1.2em] bg-zinc-600 ml-1"
      />
    </span>
  );
};

const LandingView: React.FC<LandingViewProps> = ({ onGenerate, onDebugMode }) => {
  console.log('🎨🎨🎨 LANDING VIEW RENDERED');

  const [input, setInput] = useState('');
  const [debugProjectId, setDebugProjectId] = useState('');
  const [showDebug, setShowDebug] = useState(false);

  const placeholderTexts = [
    "创建一个简单的计算器应用",
    "帮我搭建一个博客网站",
    "设计一个待办事项管理系统",
    "构建一个天气预报应用",
    "制作一个个人作品集网站"
  ];

  const handleSubmit = () => {
    console.log('🚀🚀🚀 GENERATE BUTTON CLICKED');
    console.log('🚀🚀🚀 Input value:', input);
    console.log('🚀🚀🚀 Input trimmed:', input.trim());
    console.log('🚀🚀🚀 Input length:', input.trim().length);

    if (!input.trim()) {
      console.log('🚀🚀🚀 Input is empty, not proceeding');
      return;
    }

    console.log('🚀🚀🚀 Calling onGenerate with:', input);
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
        <motion.div
          className="text-center space-y-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <motion.div
            className="inline-block px-3 py-1 border border-white/20 rounded-full bg-gradient-to-r from-zinc-900/50 to-zinc-800/50 backdrop-blur-sm"
            whileHover={{
              scale: 1.05,
              borderColor: "rgba(255, 255, 255, 0.4)",
              boxShadow: "0 0 20px rgba(255, 255, 255, 0.1)"
            }}
            transition={{ duration: 0.3 }}
          >
            <motion.span
              className="text-[10px] tracking-[0.2em] text-zinc-400 uppercase"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              18岁口腔医学生的创造力革命
            </motion.span>
          </motion.div>

          <motion.button
            onClick={() => setShowDebug(!showDebug)}
            className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors underline"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
          >
            {showDebug ? '隐藏调试模式' : '显示调试模式'}
          </motion.button>

          <div className="space-y-2">
            <motion.a
              href="https://www.wolai.com/25LZi7snWkC32qeuK1kZtM"
              target="_blank"
              rel="noopener noreferrer"
              className="group block cursor-pointer"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 1, delay: 0.8, ease: [0.25, 0.46, 0.45, 0.94] }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <motion.div
                className="relative flex justify-center"
              >
                <motion.div
                  className="relative flex items-center justify-center p-6 md:p-8 border border-zinc-700/0 rounded-lg"
                  style={{ minHeight: 160 }}
                  initial={{
                    borderColor: "rgba(63, 63, 70, 0)",
                    boxShadow: "0 0 0 rgba(82, 82, 91, 0)"
                  }}
                  animate={{
                    borderColor: "rgba(63, 63, 70, 0.5)",
                    boxShadow: "0 0 15px rgba(82, 82, 91, 0.1)"
                  }}
                  transition={{
                    duration: 1,
                    delay: 2.5, // 等待文字动画完成后再显示框线
                    ease: [0.25, 0.46, 0.45, 0.94]
                  }}
                  whileHover={{
                    borderColor: "rgb(82, 82, 91)",
                    boxShadow: "0 0 25px rgba(82, 82, 91, 0.3)"
                  }}
                >
                  <motion.div className="inline-block relative">
                    <motion.h1
                      className="text-5xl md:text-7xl font-architect font-bold text-zinc-100 tracking-tighter text-center leading-tight m-0"
                    >
                      <AnimatedText text="用积木组装软件" delay={1} />
                    </motion.h1>
                    <motion.div
                      className="absolute -bottom-1 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-zinc-500 to-transparent"
                      initial={{ width: 0, opacity: 0 }}
                      animate={{
                        width: "100%",
                        opacity: 1
                      }}
                      transition={{
                        duration: 1.2,
                        delay: 3, // 在框线出现后0.5秒显示底边线（已移入容器内）
                        ease: [0.25, 0.46, 0.45, 0.94]
                      }}
                    />
                  </motion.div>
                </motion.div>
              </motion.div>
            </motion.a>
            <motion.div
              className="flex items-center justify-center gap-4 text-zinc-500"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 1.5 }}
            >
              <motion.div
                className="h-[1px] bg-gradient-to-r from-transparent via-zinc-800 to-transparent"
                initial={{ width: 0 }}
                animate={{ width: 48 }}
                transition={{ duration: 1, delay: 1.8 }}
              ></motion.div>
              <motion.h2
                className="text-xs tracking-[0.4em] font-light bg-gradient-to-r from-zinc-500 via-zinc-400 to-zinc-500 bg-clip-text text-transparent"
                initial={{ opacity: 0, letterSpacing: "0.2em" }}
                animate={{ opacity: 1, letterSpacing: "0.4em" }}
                transition={{ duration: 1, delay: 2 }}
              >
                PORTER · S.P.E.C.I.A.L. ARCHITECT
              </motion.h2>
              <motion.div
                className="h-[1px] bg-gradient-to-r from-transparent via-zinc-800 to-transparent"
                initial={{ width: 0 }}
                animate={{ width: 48 }}
                transition={{ duration: 1, delay: 1.8 }}
              ></motion.div>
            </motion.div>
          </div>
        </motion.div>

        {/* Input Terminal Area */}
        <motion.div
          className="w-full relative group"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          {/* Enhanced glow effect */}
          <motion.div
            className="absolute -inset-0.5 bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-800 rounded-sm opacity-20 blur"
            whileHover={{
              opacity: 0.6,
              scale: 1.02,
              filter: "blur(12px)"
            }}
            transition={{ duration: 0.3 }}
          ></motion.div>

          <motion.div
            className="relative bg-[#080808] border border-white/10 p-6 md:p-10 shadow-2xl overflow-hidden"
            whileHover={{
              borderColor: "rgba(255, 255, 255, 0.2)",
              boxShadow: "0 0 40px rgba(255, 255, 255, 0.1)"
            }}
            transition={{ duration: 0.3 }}
          >
            <div className="flex flex-col h-64">
              <motion.div
                className="flex items-center gap-2 mb-4 text-zinc-500 text-xs select-none"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
              >
                <motion.span
                  className="text-green-500/50"
                  animate={{
                    opacity: [0.5, 1, 0.5],
                    scale: [1, 1.1, 1]
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                >●</motion.span>
                <span>SPEC_INPUT_MODE</span>
                <span className="flex-1 h-[1px] bg-white/5 ml-2"></span>
              </motion.div>

              <motion.div
                className="flex h-full"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
              >
                <motion.span
                  className="text-zinc-600 mr-3 mt-1 select-none"
                  animate={{
                    opacity: [0.6, 1, 0.6]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                >{'>'}</motion.span>
                <div className="w-full h-full relative">
                  <textarea
                    value={input}
                    onChange={(e) => {
                      console.log('⌨️ TEXTAREA CHANGED:', e.target.value);
                      setInput(e.target.value);
                      console.log('⌨️ Input state updated to:', e.target.value);
                    }}
                    onKeyDown={handleKeyDown}
                    className="w-full h-full bg-transparent border-none outline-none resize-none text-zinc-300 text-lg md:text-xl font-mono leading-relaxed"
                    placeholder=""
                    spellCheck={false}
                    autoFocus
                  />
                  {input === '' && (
                    <div className="absolute top-0 left-0 pointer-events-none text-zinc-700 text-lg md:text-xl font-mono leading-relaxed">
                      <TypewriterText texts={placeholderTexts} />
                    </div>
                  )}
                </div>
              </motion.div>

              <motion.div
                className="absolute bottom-6 right-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 1 }}
              >
                <motion.button
                  onClick={handleSubmit}
                  className="group relative px-6 py-2 bg-zinc-100 text-zinc-950 font-medium text-sm overflow-hidden"
                  whileHover={{
                    scale: 1.05,
                    boxShadow: "0 0 25px rgba(255, 255, 255, 0.3)"
                  }}
                  whileTap={{
                    scale: 0.95,
                    transition: { duration: 0.1 }
                  }}
                  transition={{ duration: 0.2 }}
                >
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-white via-zinc-200 to-white opacity-0 group-hover:opacity-100"
                    initial={false}
                    animate={{ x: ["-100%", "100%"] }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      repeatDelay: 2,
                      ease: "easeInOut"
                    }}
                  />
                  <span className="relative z-10 flex items-center gap-2">
                    <motion.span
                      initial={{ x: 0 }}
                      whileHover={{ x: 2 }}
                      transition={{ duration: 0.2 }}
                    >
                      点火起航
                    </motion.span>
                    <motion.span
                      initial={{ x: 0 }}
                      whileHover={{ x: 4 }}
                      transition={{ duration: 0.2 }}
                    >→</motion.span>
                  </span>
                </motion.button>
              </motion.div>
            </div>
          </motion.div>

          {/* Decorative Technical Markers with Animation */}
          <motion.div
            className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-zinc-500"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          ></motion.div>
          <motion.div
            className="absolute -top-1 -right-1 w-2 h-2 border-t border-r border-zinc-500"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          ></motion.div>
          <motion.div
            className="absolute -bottom-1 -left-1 w-2 h-2 border-b border-l border-zinc-500"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          ></motion.div>
          <motion.div
            className="absolute -bottom-1 -right-1 w-2 h-2 border-b border-r border-zinc-500"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          ></motion.div>
        </motion.div>

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
        <motion.div
          className="mt-8 text-center"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 0.4, y: 0 }}
          transition={{ duration: 0.8, delay: 1.2 }}
          whileHover={{ opacity: 0.8, scale: 1.02 }}
        >
          <motion.p
            className="text-xs font-mono text-zinc-500"
            animate={{
              background: [
                "linear-gradient(90deg, #71717a, #a1a1aa, #71717a)",
                "linear-gradient(90deg, #a1a1aa, #d4d4d8, #a1a1aa)",
                "linear-gradient(90deg, #71717a, #a1a1aa, #71717a)"
              ]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}
          >
            "AI 时代的掠夺者，拒绝背诵该死的语法。"
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingView;