import React, { useEffect, useRef } from 'react';
import { COLORS } from '../constants';

interface MatrixRainProps {
  onComplete?: () => void;
}

const MatrixRain: React.FC<MatrixRainProps> = ({ onComplete }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas full screen
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const characters = katakana.split('');
    const fontSize = 16;
    const columns = canvas.width / fontSize;
    const drops: number[] = [];

    // Initialize drops at random vertical positions to start efficiently
    for (let i = 0; i < columns; i++) {
      drops[i] = Math.random() * -100; 
    }

    let frameId: number;
    let startTime = Date.now();
    const duration = 2500; // Run for 2.5 seconds heavily

    const draw = () => {
      // Semi-transparent black to create trail effect
      ctx.fillStyle = 'rgba(5, 5, 5, 0.1)'; 
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.font = fontSize + 'px monospace';

      for (let i = 0; i < drops.length; i++) {
        // Randomize color: Mostly Orange, some White
        const isWhite = Math.random() > 0.95;
        ctx.fillStyle = isWhite ? '#FFFFFF' : COLORS.laser;

        const text = characters[Math.floor(Math.random() * characters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        drops[i]++;
      }

      // Check if we should stop
      if (Date.now() - startTime < duration) {
        frameId = requestAnimationFrame(draw);
      } else {
        if (onComplete) onComplete();
      }
    };

    draw();

    return () => {
      cancelAnimationFrame(frameId);
    };
  }, [onComplete]);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 z-50 pointer-events-none"
    />
  );
};

export default MatrixRain;