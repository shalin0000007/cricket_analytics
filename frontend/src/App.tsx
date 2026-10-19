import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useTerminalStore } from './store/useTerminalStore';
import { GlobalTelemetryBar } from './components/shell/GlobalTelemetryBar';
import { WorkspaceSwitcher } from './components/shell/WorkspaceSwitcher';
import { CommandPalette } from './components/shell/CommandPalette';
import { Swords, Scale, Users, LineChart, FileText } from 'lucide-react';

export const App: React.FC = () => {
  const { activeWorkspace, selectedBatter, selectedBowler, venue, era } = useTerminalStore();

  const renderActiveWorkspace = () => {
    switch (activeWorkspace) {
      case 'arena':
        return (
          <div className="p-6 max-w-[1920px] mx-auto">
            {/* Arena Header Preview */}
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-[#F2EEE3]/10 pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-[#C8102E]/10 border border-[#C8102E]/30 text-[#C8102E]">
                    <Swords className="w-5 h-5" />
                  </div>
                  <div>
                    <h1 className="font-display text-2xl font-black uppercase tracking-wide text-[#F2EEE3]">
                      THE DUEL ARENA // 1-TO-1 TACTICAL CONFRONTATION
                    </h1>
                    <p className="font-data text-xs text-[#8E9AA8]">
                      {selectedBatter} vs {selectedBowler} • {venue} • {era === 'recent' ? 'Recent Era (2022–2024)' : 'All-Time (2008–2024)'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-1 rounded bg-[#0D1117] border border-[#F2EEE3]/15 font-data text-xs text-[#10B981] font-semibold">
                    DIRECT H2H ACTIVE
                  </span>
                </div>
              </div>

              {/* 22-Yard Pitch Strip Divider Motif */}
              <div className="pitch-strip my-2" />

              {/* Status Banner for Pass 1 */}
              <div className="rounded-xl border border-[#F2EEE3]/10 bg-[#0D1117]/80 p-8 text-center backdrop-blur-sm">
                <div className="max-w-md mx-auto space-y-3">
                  <span className="font-display text-xl font-extrabold uppercase text-[#FFF1CC] tracking-wider block">
                    DUGOUT TELEMETRY SHELL INITIALIZED
                  </span>
                  <p className="font-body text-xs text-[#8E9AA8] leading-relaxed">
                    Pass 1 Shell, Telemetry HUD, Workspace Switcher, and Command Palette (<kbd className="px-1.5 py-0.5 rounded bg-[#05070B] border border-[#F2EEE3]/20 font-data">⌘K</kbd>) are live. Ready for Pass 2 (Preloader & Particle Delivery Field) and Pass 3 (Duel Arena).
                  </p>
                </div>
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
      {/* Tier 1: Sticky Global Telemetry Bar */}
      <GlobalTelemetryBar />

      {/* Tier 2: Workspace Switcher with Sliding Cherry Underline */}
      <WorkspaceSwitcher />

      {/* Tier 3: Active Workspace with Smooth Pan Transition */}
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
