import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface PreloaderProps {
  onComplete: () => void;
}

export const StadiumPreloader: React.FC<PreloaderProps> = ({ onComplete }) => {
  const [count, setCount] = useState(0);
  const [lightsActive, setLightsActive] = useState([false, false, false, false]);
  const [pitchDrawn, setPitchDrawn] = useState(false);
  const targetCount = 295732;

  useEffect(() => {
    // Escape key skips preloader
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onComplete();
      }
    };
    window.addEventListener('keydown', handleKey);

    // Sequential floodlight ignition
    const t1 = setTimeout(() => setLightsActive([true, false, false, false]), 200);
    const t2 = setTimeout(() => setLightsActive([true, true, false, false]), 450);
    const t3 = setTimeout(() => setLightsActive([true, true, true, false]), 700);
    const t4 = setTimeout(() => setLightsActive([true, true, true, true]), 950);
    const tPitch = setTimeout(() => setPitchDrawn(true), 1100);

    // Fast scoreboard number counter (0 -> 295,732)
    const startTime = Date.now();
    const duration = 1600;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Easing cubic ease-out
      const ease = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(ease * targetCount));

      if (progress >= 1) {
        clearInterval(interval);
        setTimeout(onComplete, 400); // Flood lights up and dismiss
      }
    }, 20);

    return () => {
      window.removeEventListener('keydown', handleKey);
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(tPitch);
      clearInterval(interval);
    };
  }, [onComplete]);

  return (
    <AnimatePresence>
      <motion.div
        exit={{ opacity: 0, scale: 1.02 }}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className="fixed inset-0 z-[100] bg-[#05070B] flex flex-col items-center justify-center p-6 overflow-hidden select-none"
      >
        {/* Stadium Floodlight Cones (Top Corners) */}
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
          {/* Tower 1 (North-West) */}
          <div
            className={`absolute -top-16 -left-16 w-96 h-96 rounded-full transition-opacity duration-300 blur-3xl ${
              lightsActive[0] ? 'opacity-30 bg-[#FFF1CC]' : 'opacity-0'
            }`}
          />
          {/* Tower 2 (North-East) */}
          <div
            className={`absolute -top-16 -right-16 w-96 h-96 rounded-full transition-opacity duration-300 blur-3xl ${
              lightsActive[1] ? 'opacity-30 bg-[#FFF1CC]' : 'opacity-0'
            }`}
          />
          {/* Tower 3 (South-West) */}
          <div
            className={`absolute -bottom-16 -left-16 w-96 h-96 rounded-full transition-opacity duration-300 blur-3xl ${
              lightsActive[2] ? 'opacity-20 bg-[#07140D]' : 'opacity-0'
            }`}
          />
          {/* Tower 4 (South-East) */}
          <div
            className={`absolute -bottom-16 -right-16 w-96 h-96 rounded-full transition-opacity duration-300 blur-3xl ${
              lightsActive[3] ? 'opacity-20 bg-[#07140D]' : 'opacity-0'
            }`}
          />
        </div>

        {/* Center Telemetry Cluster */}
        <div className="relative z-10 flex flex-col items-center text-center max-w-xl mx-auto space-y-6">
          
          {/* Brand Mark with glowing cherry indicator */}
          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-[#C8102E] animate-ping" />
            <h1 className="font-display text-4xl sm:text-5xl font-black tracking-widest text-[#F2EEE3]">
              DUGOUT<span className="text-[#C8102E]">.OS</span>
            </h1>
          </div>

          <p className="font-data text-xs uppercase tracking-widest text-[#8E9AA8]">
            IPL TACTICAL MATCHUP & DECISION ENGINE
          </p>

          {/* 22-Yard Pitch Strip Draw-In */}
          <div className="w-72 sm:w-96 relative my-4">
            <div className="h-[2px] w-full bg-[#0D1117] rounded relative overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: pitchDrawn ? '100%' : '0%' }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="h-full bg-gradient-to-r from-transparent via-[#CBB98A] to-transparent"
              />
            </div>
            {/* Bowling Stumps Glyphs */}
            <div className="flex justify-between items-center text-[10px] font-data text-[#CBB98A] mt-1 px-2">
              <span>||| BOWLER</span>
              <span className="text-[#8E9AA8]">22 YARDS</span>
              <span>||| STRIKER</span>
            </div>
          </div>

          {/* Stadium Scoreboard Numerals Counter */}
          <div className="bg-[#0D1117] border border-[#F2EEE3]/15 rounded-xl px-8 py-5 shadow-2xl backdrop-blur-md">
            <div className="text-[11px] font-data text-[#8E9AA8] uppercase tracking-wider mb-1 flex items-center justify-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span>DUCKDB PARQUET INGESTION</span>
            </div>
            <div className="font-scoreboard text-4xl sm:text-6xl font-bold tracking-tight text-[#FFF1CC] text-shadow">
              {count.toLocaleString()}
            </div>
            <div className="text-[10px] font-data text-[#8E9AA8] mt-1">
              HISTORICAL IPL DELIVERIES LOADED (2008–2024)
            </div>
          </div>

          {/* Skip Instruction */}
          <button
            onClick={onComplete}
            className="text-[11px] font-data text-[#8E9AA8] hover:text-[#F2EEE3] transition-colors px-3 py-1 rounded bg-[#0D1117]/60 border border-[#F2EEE3]/10"
          >
            PRESS <kbd className="text-[#FFF1CC]">ESC</kbd> TO SKIP
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};
