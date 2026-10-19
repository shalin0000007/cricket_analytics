import { create } from 'zustand';
import type { WorkspaceId, Era } from '../types';

interface TerminalState {
  // Navigation & Workspace
  activeWorkspace: WorkspaceId;
  setActiveWorkspace: (ws: WorkspaceId) => void;

  // Tactical Filters
  era: Era;
  setEra: (era: Era) => void;
  venue: string;
  setVenue: (venue: string) => void;

  // Selected Players for Duel
  selectedBatter: string;
  setSelectedBatter: (b: string) => void;
  selectedBowler: string;
  setSelectedBowler: (bw: string) => void;

  // Selected Players for Tale of the Tape
  tapeBatter1: string;
  setTapeBatter1: (b: string) => void;
  tapeBatter2: string;
  setTapeBatter2: (b: string) => void;
  tapeBowler1: string;
  setTapeBowler1: (bw: string) => void;
  tapeBowler2: string;
  setTapeBowler2: (bw: string) => void;
  tapeMode: 'batter' | 'bowler';
  setTapeMode: (m: 'batter' | 'bowler') => void;

  // Squad War Room
  oppTeam: string;
  setOppTeam: (team: string) => void;
  ourTeam: string;
  setOurTeam: (team: string) => void;
  activeBatters: string[];
  setActiveBatters: (batters: string[]) => void;
  activeBowlers: string[];
  setActiveBowlers: (bowlers: string[]) => void;

  // Command Palette
  isCommandOpen: boolean;
  setCommandOpen: (open: boolean) => void;

  // Telemetry & System
  engineMs: number;
  setEngineMs: (ms: number) => void;
  isMockMode: boolean;
  setIsMockMode: (mock: boolean) => void;
  activeFranchiseColor: string;
  setActiveFranchiseColor: (hex: string) => void;
}

export const useTerminalStore = create<TerminalState>((set) => ({
  activeWorkspace: 'arena',
  setActiveWorkspace: (ws) => set({ activeWorkspace: ws }),

  era: 'recent',
  setEra: (era) => set({ era }),
  venue: 'All Venues',
  setVenue: (venue) => set({ venue }),

  selectedBatter: 'V Kohli',
  setSelectedBatter: (b) => set({ selectedBatter: b }),
  selectedBowler: 'JJ Bumrah',
  setSelectedBowler: (bw) => set({ selectedBowler: bw }),

  tapeBatter1: 'V Kohli',
  setTapeBatter1: (b) => set({ tapeBatter1: b }),
  tapeBatter2: 'RG Sharma',
  setTapeBatter2: (b) => set({ tapeBatter2: b }),
  tapeBowler1: 'JJ Bumrah',
  setTapeBowler1: (bw) => set({ tapeBowler1: bw }),
  tapeBowler2: 'Rashid Khan',
  setTapeBowler2: (bw) => set({ tapeBowler2: bw }),
  tapeMode: 'batter',
  setTapeMode: (m) => set({ tapeMode: m }),

  oppTeam: 'Royal Challengers Bengaluru',
  setOppTeam: (oppTeam) => set({ oppTeam }),
  ourTeam: 'Mumbai Indians',
  setOurTeam: (ourTeam) => set({ ourTeam }),
  activeBatters: ['V Kohli', 'F du Plessis', 'RM Patidar', 'GJ Maxwell', 'C Green', 'KD Karthik'],
  setActiveBatters: (activeBatters) => set({ activeBatters }),
  activeBowlers: ['JJ Bumrah', 'HH Pandya', 'G Coetzee', 'P Chawla', 'N Thushara'],
  setActiveBowlers: (activeBowlers) => set({ activeBowlers }),

  isCommandOpen: false,
  setCommandOpen: (isCommandOpen) => set({ isCommandOpen }),

  engineMs: 14.8,
  setEngineMs: (engineMs) => set({ engineMs }),
  isMockMode: true,
  setIsMockMode: (isMockMode) => set({ isMockMode }),
  activeFranchiseColor: '#DC2626',
  setActiveFranchiseColor: (activeFranchiseColor) => set({ activeFranchiseColor }),
}));
