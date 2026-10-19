import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTerminalStore } from '../../store/useTerminalStore';
import type { WorkspaceId } from '../../types';
import { Swords, Scale, Users, LineChart, FileText } from 'lucide-react';

interface TabItem {
  id: WorkspaceId;
  label: string;
  keyNumber: string;
  icon: React.ComponentType<{ className?: string }>;
}

const TABS: TabItem[] = [
  { id: 'arena', label: 'DUEL ARENA', keyNumber: '1', icon: Swords },
  { id: 'tape', label: 'TALE OF THE TAPE', keyNumber: '2', icon: Scale },
  { id: 'warroom', label: 'SQUAD WAR ROOM', keyNumber: '3', icon: Users },
  { id: 'metrics', label: 'TRUE METRICS', keyNumber: '4', icon: LineChart },
  { id: 'dossier', label: 'SCOUTING DOSSIER', keyNumber: '5', icon: FileText },
];

export const WorkspaceSwitcher: React.FC = () => {
  const { activeWorkspace, setActiveWorkspace } = useTerminalStore();

  // Keyboard shortcut listener: 1-5 to switch workspaces
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }
      const match = TABS.find((t) => t.keyNumber === e.key);
      if (match) {
        e.preventDefault();
        setActiveWorkspace(match.id);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setActiveWorkspace]);

  return (
    <nav className="w-full bg-[#07140D]/40 border-b border-[#F2EEE3]/10 px-4">
      <div className="max-w-[1920px] mx-auto flex items-center justify-between overflow-x-auto no-scrollbar">
        <div className="flex items-center space-x-1 sm:space-x-2">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeWorkspace === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveWorkspace(tab.id)}
                className={`relative flex items-center gap-2 px-3 sm:px-4 py-3 font-display text-sm tracking-wider uppercase transition-colors group focus:outline-none ${
                  isActive ? 'text-[#F2EEE3] font-black' : 'text-[#8E9AA8] hover:text-[#F2EEE3] font-bold'
                }`}
              >
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-[#C8102E]' : 'text-[#8E9AA8] group-hover:text-[#F2EEE3]'}`} />
                <span className="whitespace-nowrap">{tab.label}</span>

                <span className="hidden md:inline-block ml-1 px-1 py-0.2 rounded bg-[#05070B] border border-[#F2EEE3]/10 font-data text-[10px] text-[#8E9AA8]">
                  [{tab.keyNumber}]
                </span>

                {/* Sliding Cherry Underline Motif */}
                {isActive && (
                  <motion.div
                    layoutId="activeWorkspaceUnderline"
                    className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#C8102E] shadow-[0_0_10px_#C8102E]"
                    transition={{ type: 'spring', stiffness: 500, damping: 35 }}
                  />
                )}
              </button>
            );
          })}
        </div>

        <div className="hidden lg:flex items-center gap-2 text-[11px] font-data text-[#8E9AA8]">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
          <span>BROADCAST HUD • 60FPS</span>
        </div>
      </div>
    </nav>
  );
};
