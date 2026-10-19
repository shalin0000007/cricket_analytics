import React from 'react';
import { useTerminalStore } from '../../store/useTerminalStore';
import { VENUES } from '../../data/mockData';
import { Search, Activity, ShieldAlert, Cpu } from 'lucide-react';

export const GlobalTelemetryBar: React.FC = () => {
  const { 
    era, setEra, 
    venue, setVenue, 
    engineMs, 
    setCommandOpen,
    isMockMode 
  } = useTerminalStore();

  const activeVenueObj = VENUES.find(v => v.venue === venue) || VENUES[0];

  return (
    <header className="sticky top-0 z-50 w-full bg-[#05070B]/90 backdrop-blur-md border-b border-[#F2EEE3]/10 px-4 py-2.5">
      <div className="max-w-[1920px] mx-auto flex items-center justify-between gap-4">
        
        {/* Left: Brand Identity & Live Engine Badge */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#C8102E] animate-pulse shadow-[0_0_8px_#C8102E]" />
            <span className="font-display text-2xl font-black tracking-wider text-[#F2EEE3]">
              DUGOUT<span className="text-[#C8102E]">.OS</span>
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#0D1117] border border-[#F2EEE3]/10 font-data text-xs text-[#8E9AA8]">
            <Cpu className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span className="text-[#F2EEE3]">DUCKDB</span>
            <span className="text-[#8E9AA8]">•</span>
            <span className="text-[#10B981]">{engineMs.toFixed(1)}ms</span>
          </div>

          <div className="hidden md:flex items-center gap-1.5 px-2 py-0.5 rounded bg-[#07140D] border border-[#10B981]/20 font-data text-xs text-[#10B981]">
            <Activity className="w-3.5 h-3.5" />
            <span className="font-scoreboard tracking-wide">295,732</span>
            <span className="text-[#8E9AA8]">BALLS</span>
          </div>
        </div>

        {/* Center: Command Palette Trigger */}
        <button
          onClick={() => setCommandOpen(true)}
          className="flex-1 max-w-md flex items-center justify-between px-3 py-1.5 rounded-md bg-[#0D1117]/80 hover:bg-[#0D1117] border border-[#F2EEE3]/15 text-[#8E9AA8] hover:text-[#F2EEE3] transition-all text-xs font-body group shadow-inner"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-[#8E9AA8] group-hover:text-[#F2EEE3] transition-colors" />
            <span>Search player, duel, ground, squad...</span>
          </div>
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-[#05070B] border border-[#F2EEE3]/15 font-data text-[10px] text-[#8E9AA8]">
            ⌘K
          </kbd>
        </button>

        {/* Right: Tactical Era & Ground Par Context */}
        <div className="flex items-center gap-3">
          
          {/* Era Toggle */}
          <div className="flex items-center rounded-md bg-[#0D1117] p-0.5 border border-[#F2EEE3]/10 text-xs font-data">
            <button
              onClick={() => setEra('recent')}
              className={`px-2.5 py-1 rounded transition-all font-medium ${
                era === 'recent'
                  ? 'bg-[#1A2230] text-[#38BDF8] shadow-sm'
                  : 'text-[#8E9AA8] hover:text-[#F2EEE3]'
              }`}
            >
              MODERN 22-24
            </button>
            <button
              onClick={() => setEra('alltime')}
              className={`px-2.5 py-1 rounded transition-all font-medium ${
                era === 'alltime'
                  ? 'bg-[#1A2230] text-[#F2EEE3] shadow-sm'
                  : 'text-[#8E9AA8] hover:text-[#F2EEE3]'
              }`}
            >
              ALL-TIME 08-24
            </button>
          </div>

          {/* Venue Selector */}
          <div className="hidden lg:flex items-center gap-2">
            <select
              value={venue}
              onChange={(e) => setVenue(e.target.value)}
              className="bg-[#0D1117] border border-[#F2EEE3]/15 rounded-md px-2.5 py-1 text-xs text-[#F2EEE3] font-data focus:outline-none focus:border-[#C8102E]"
            >
              {VENUES.map((v) => (
                <option key={v.venue} value={v.venue} className="bg-[#0D1117]">
                  {v.venue}
                </option>
              ))}
            </select>

            <div className="px-2 py-1 rounded bg-[#0D1117] border border-[#F2EEE3]/10 font-data text-xs flex items-center gap-1.5">
              <span className="text-[#8E9AA8]">PAR:</span>
              <span className="font-scoreboard font-bold text-[#FBBF24]">
                {activeVenueObj.parRpo.toFixed(2)} RPO
              </span>
            </div>
          </div>

          {/* Mock Mode Alert Tag */}
          {isMockMode && (
            <div className="hidden xl:flex items-center gap-1 px-2 py-0.5 rounded bg-[#FBBF24]/10 border border-[#FBBF24]/30 text-[#FBBF24] font-data text-[10px] uppercase font-bold tracking-wider">
              <ShieldAlert className="w-3 h-3" />
              <span>SAMPLE DATA</span>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};
