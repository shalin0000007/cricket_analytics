import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTerminalStore } from './store/useTerminalStore';
import { GlobalTelemetryBar } from './components/shell/GlobalTelemetryBar';
import { WorkspaceSwitcher } from './components/shell/WorkspaceSwitcher';
import { CommandPalette } from './components/shell/CommandPalette';
import { StadiumPreloader } from './components/home/StadiumPreloader';
import { DeliveryFieldHero } from './components/home/DeliveryFieldHero';
import { Swords, Scale, Users, LineChart, FileText, Home } from 'lucide-react';

export const App: React.FC = () => {
  const { activeWorkspace, selectedBatter, selectedBowler, venue, era } = useTerminalStore();
  const [showPreloader, setShowPreloader] = useState(true);
  const [showHeroField, setShowHeroField] = useState(true);

  const renderActiveWorkspace = () => {
    switch (activeWorkspace) {
      case 'arena':
        return (
          <div className="p-4 sm:p-6 max-w-[1920px] mx-auto space-y-6">
            
            {/* Arena Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-[#F2EEE3]/10 pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-lg bg-[#C8102E]/10 border border-[#C8102E]/30 text-[#C8102E]">
                  <Swords className="w-5 h-5" />
                </div>
                <div>
                  <h1 className="font-display text-2xl sm:text-3xl font-black uppercase tracking-wide text-[#F2EEE3]">
                    THE DUEL ARENA // 1-TO-1 TACTICAL CONFRONTATION
                  </h1>
                  <p className="font-data text-xs text-[#8E9AA8]">
                    {selectedBatter} vs {selectedBowler} • {venue} • {era === 'recent' ? 'Recent Era (2022–2024)' : 'All-Time (2008–2024)'}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowHeroField(!showHeroField)}
                  className="px-3 py-1.5 rounded-md bg-[#0D1117] hover:bg-[#1A2230] border border-[#F2EEE3]/15 font-data text-xs text-[#8E9AA8] hover:text-[#F2EEE3] flex items-center gap-1.5 transition-colors"
                >
                  <Home className="w-3.5 h-3.5 text-[#FBBF24]" />
                  <span>{showHeroField ? 'HIDE DELIVERY FIELD' : 'SHOW DELIVERY FIELD'}</span>
                </button>
                <span className="px-3 py-1.5 rounded-md bg-[#07140D] border border-[#10B981]/20 font-data text-xs text-[#10B981] font-semibold">
                  DIRECT H2H ACTIVE
                </span>
              </div>
            </div>

            {/* Pitch Strip Motif */}
            <div className="pitch-strip" />

            {/* If Hero Field is toggled on, show signature delivery field */}
            {showHeroField && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                <DeliveryFieldHero />
                <div className="pitch-strip my-6" />
              </motion.div>
            )}

            {/* Arena Preview Placeholder ready for Pass 3 */}
            <div className="rounded-xl border border-[#F2EEE3]/10 bg-[#0D1117]/90 p-8 text-center backdrop-blur-md">
              <div className="max-w-md mx-auto space-y-3">
                <span className="font-display text-xl font-extrabold uppercase text-[#FFF1CC] tracking-wider block">
                  PASS 2 DELIVERY FIELD & HERO INITIALIZED
                </span>
                <p className="font-body text-xs text-[#8E9AA8] leading-relaxed">
                  Interactive Beeswarm Canvas (20 Overs x 7 Outcome Lanes), Thermal Lens reticle, and 1-Click Featured Duels are live. Next: Pass 3 Flagship Duel Arena with 22-Yard pitch clash, replay ball strip, and Bayesian shrinkage gauge!
                </p>
              </div>
            </div>
          </div>
        );

      case 'tape':
        return (
          <div className="p-6 max-w-[1920px] mx-auto space-y-4">
            <div className="flex items-center gap-3 border-b border-[#F2EEE3]/10 pb-3">
              <Scale className="w-5 h-5 text-[#38BDF8]" />
              <h1 className="font-display text-2xl font-black uppercase text-[#F2EEE3]">
                TALE OF THE TAPE // STATSBOMB 8-AXIS RADAR COMPARISON
              </h1>
            </div>
            <div className="pitch-strip my-2" />
            <div className="rounded-xl border border-[#F2EEE3]/10 bg-[#0D1117]/80 p-8 text-center text-[#8E9AA8] font-body text-xs">
              Tale of the Tape Workspace ready for Pass 4.
            </div>
          </div>
        );

      case 'warroom':
        return (
          <div className="p-6 max-w-[1920px] mx-auto space-y-4">
            <div className="flex items-center gap-3 border-b border-[#F2EEE3]/10 pb-3">
              <Users className="w-5 h-5 text-[#FBBF24]" />
              <h1 className="font-display text-2xl font-black uppercase text-[#F2EEE3]">
                SQUAD WAR ROOM // XI VS XI MATCHUP MATRIX & 20-OVER ALLOCATOR
              </h1>
            </div>
            <div className="pitch-strip my-2" />
            <div className="rounded-xl border border-[#F2EEE3]/10 bg-[#0D1117]/80 p-8 text-center text-[#8E9AA8] font-body text-xs">
              Squad War Room Workspace ready for Pass 5.
            </div>
          </div>
        );

      case 'metrics':
        return (
          <div className="p-6 max-w-[1920px] mx-auto space-y-4">
            <div className="flex items-center gap-3 border-b border-[#F2EEE3]/10 pb-3">
              <LineChart className="w-5 h-5 text-[#10B981]" />
              <h1 className="font-display text-2xl font-black uppercase text-[#F2EEE3]">
                TRUE METRICS // TSR & TER ACCELERATION DIAGNOSTICS
              </h1>
            </div>
            <div className="pitch-strip my-2" />
            <div className="rounded-xl border border-[#F2EEE3]/10 bg-[#0D1117]/80 p-8 text-center text-[#8E9AA8] font-body text-xs">
              True Metrics Workspace ready for Pass 6.
            </div>
          </div>
        );

      case 'dossier':
        return (
          <div className="p-6 max-w-[1920px] mx-auto space-y-4">
            <div className="flex items-center gap-3 border-b border-[#F2EEE3]/10 pb-3">
              <FileText className="w-5 h-5 text-[#C8102E]" />
              <h1 className="font-display text-2xl font-black uppercase text-[#F2EEE3]">
                SCOUTING DOSSIER STUDIO // 1-PAGE PRE-MATCH PRINTABLE BRIEF
              </h1>
            </div>
            <div className="pitch-strip my-2" />
            <div className="rounded-xl border border-[#F2EEE3]/10 bg-[#0D1117]/80 p-8 text-center text-[#8E9AA8] font-body text-xs">
              Scouting Dossier Studio ready for Pass 6.
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#05070B] text-[#F2EEE3] stadium-ambient flex flex-col selection:bg-[#C8102E] selection:text-[#F2EEE3]">
      
      {/* Stadium Preloader (warm flicker, pitch draw, scoreboard count) */}
      {showPreloader && (
        <StadiumPreloader onComplete={() => setShowPreloader(false)} />
      )}

      {/* Tier 1: Sticky Global Telemetry Bar */}
      <GlobalTelemetryBar />

      {/* Tier 2: Workspace Switcher with Sliding Cherry Underline */}
      <WorkspaceSwitcher />

      {/* Tier 3: Active Workspace Viewport */}
      <main className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeWorkspace}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="w-full h-full"
          >
            {renderActiveWorkspace()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Universal Command Palette (⌘K) */}
      <CommandPalette />
    </div>
  );
};

export default App;
