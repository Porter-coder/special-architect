import React, { useEffect, useState } from 'react';
import { PROCESSING_STEPS, MANIFESTO_QUOTES } from '../constants';

interface SceneWaitingProps {
  onComplete: () => void;
}

const SceneWaiting: React.FC<SceneWaitingProps> = ({ onComplete }) => {
  const [stepIndex, setStepIndex] = useState(0);
  const [quoteIndex, setQuoteIndex] = useState(0);

  useEffect(() => {
    // 进度步骤控制
    const stepDuration = 2500;
    const totalDuration = stepDuration * PROCESSING_STEPS.length; 

    const stepInterval = setInterval(() => {
      setStepIndex((prev) => {
        if (prev < PROCESSING_STEPS.length - 1) return prev + 1;
        return prev;
      });
    }, stepDuration);

    // 宣言轮播控制
    const quoteInterval = setInterval(() => {
        setQuoteIndex((prev) => (prev + 1) % MANIFESTO_QUOTES.length);
    }, 3200);

    const finishTimeout = setTimeout(() => {
        onComplete();
    }, totalDuration);

    return () => {
      clearInterval(stepInterval);
      clearInterval(quoteInterval);
      clearTimeout(finishTimeout);
    };
  }, [onComplete]);

  const currentStep = PROCESSING_STEPS[stepIndex];
  const currentQuote = MANIFESTO_QUOTES[quoteIndex];

  return (
    <div className="w-full h-full flex flex-col items-center bg-morandi-bg z-10 relative overflow-hidden">
      
      {/* 顶部/中间内容区域：自动占据剩余空间并垂直居中 */}
      <div className="flex-1 flex flex-col items-center justify-center w-full px-4 pt-10">
        
        {/* 3D Structure - 稍微调小 scale 以适应不同屏幕 */}
        <div className="mb-12 md:mb-16 fade-in opacity-90 scale-90 md:scale-100">
          <div className="cube-wrapper">
            <div className="cube">
              <div className="face front">SPEC</div>
              <div className="face back">CODE</div>
              <div className="face right">INTENT</div>
              <div className="face left">PLAN</div>
              <div className="face top">ARCH</div>
              <div className="face bottom">BUILD</div>
            </div>
          </div>
        </div>

        {/* Main Status Text - 确保有最小高度防止文字跳动 */}
        <div className="text-center z-10 max-w-xl flex flex-col items-center min-h-[120px]">
          <h2 
              key={currentStep.main} 
              className="font-serif text-2xl md:text-4xl text-morandi-text mb-4 animate-[fadeIn_0.8s_ease-out]"
          >
              {currentStep.main}
          </h2>
          <div className="h-px w-12 bg-white/20 mb-4"></div>
          <p 
              key={currentStep.sub}
              className="text-morandi-sub font-mono text-xs md:text-sm tracking-widest uppercase animate-[fadeIn_0.8s_ease-out_0.2s_both]"
          >
              {currentStep.sub}
          </p>
        </div>
      </div>

      {/* Philosophy Quote Carousel - 放在流式布局的底部，留出 padding */}
      <div className="w-full max-w-2xl text-center px-6 pb-20 md:pb-24 z-10 min-h-[100px] shrink-0">
        <p 
            key={currentQuote.text}
            className="font-serif text-base md:text-xl text-morandi-text/80 italic leading-relaxed animate-[fadeIn_1s_ease-out]"
        >
            "{currentQuote.text}"
        </p>
        <p 
            key={currentQuote.author}
            className="text-xs text-morandi-sub/50 mt-4 tracking-widest uppercase animate-[fadeIn_1s_ease-out_0.2s_both]"
        >
            —— {currentQuote.author}
        </p>
      </div>

      {/* Minimal Progress Line - 绝对定位到底部，作为装饰线条 */}
      <div className="absolute bottom-0 left-0 w-full h-1 bg-white/5 z-20">
        <div 
            className="h-full bg-morandi-text/40 transition-all duration-[2500ms] ease-linear"
            style={{ width: `${((stepIndex + 1) / PROCESSING_STEPS.length) * 100}%` }}
        />
      </div>
    </div>
  );
};

export default SceneWaiting;