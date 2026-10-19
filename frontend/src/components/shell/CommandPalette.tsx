import React, { useState, useEffect, useRef } from 'react';
import { useTerminalStore } from '../../store/useTerminalStore';
import { PLAYERS, VENUES, FRANCHISES } from '../../data/mockData';
import { Search, X, Swords, MapPin } from 'lucide-react';

export const CommandPalette: React.FC = () => {
  const { 
    isCommandOpen, setCommandOpen, 
    setSelectedBatter, setSelectedBowler,
    setVenue, setActiveWorkspace 
  } = useTerminalStore();

  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Global keyboard shortcut Cmd+K or Ctrl+K
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandOpen(!isCommandOpen);
      }
      if (e.key === 'Escape' && isCommandOpen) {
        setCommandOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isCommandOpen, setCommandOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isCommandOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery('');
    }
  }, [isCommandOpen]);

  if (!isCommandOpen) return null;

  // Search Results Filter
  const q = query.toLowerCase().trim();

  const playerResults = PLAYERS.filter(p => 
    p.name.toLowerCase().includes(q) || 
    p.team.toLowerCase().includes(q) ||
    (p.bowlerSubtype && p.bowlerSubtype.toLowerCase().includes(q))
  ).slice(0, 5);

  const venueResults = VENUES.filter(v => 
    v.venue.toLowerCase().includes(q)
  ).slice(0, 3);

  const franchiseResults = Object.keys(FRANCHISES).filter(f => 
    f.toLowerCase().includes(q) || FRANCHISES[f].short.toLowerCase().includes(q)
  ).slice(0, 3);

  const totalResults = playerResults.length + venueResults.length + franchiseResults.length;

  const handleSelectPlayer = (player: typeof PLAYERS[0]) => {
    if (player.bowlerType) {
      setSelectedBowler(player.name);
    } else {
      setSelectedBatter(player.name);
    }
    setActiveWorkspace('arena');
    setCommandOpen(false);
  };

  const handleSelectVenue = (venueName: string) => {
    setVenue(venueName);
    setCommandOpen(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-[#05070B]/80 backdrop-blur-md">
      <div 
        className="w-full max-w-2xl bg-[#0D1117] border border-[#F2EEE3]/20 rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.8)] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3 border-b border-[#F2EEE3]/10 gap-3 bg-[#05070B]">
          <Search className="w-5 h-5 text-[#8E9AA8]" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type a player (Kohli, Bumrah), ground (Wankhede), or team..."
            className="flex-1 bg-transparent text-[#F2EEE3] font-body text-sm placeholder-[#8E9AA8] focus:outline-none"
          />
          <button 
            onClick={() => setCommandOpen(false)}
            className="p-1 rounded hover:bg-[#1A2230] text-[#8E9AA8] hover:text-[#F2EEE3]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results Container */}
        <div className="max-h-96 overflow-y-auto p-2 divide-y divide-[#F2EEE3]/5 font-body">
          {totalResults === 0 && (
            <div className="py-8 text-center text-[#8E9AA8] font-data text-xs">
              No matching tactical records found for "{query}".
            </div>
          )}

          {/* Players Group */}
          {playerResults.length > 0 && (
            <div className="py-2">
              <div className="px-3 py-1 text-[10px] font-data font-bold uppercase tracking-wider text-[#8E9AA8]">
                Players ({playerResults.length})
              </div>
              {playerResults.map((p) => (
                <div
                  key={p.name}
                  onClick={() => handleSelectPlayer(p)}
                  className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#1A2230] cursor-pointer transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <img 
                      src={p.image} 
                      alt={p.name} 
                      className="w-8 h-8 rounded-full object-cover border border-[#F2EEE3]/20"
                      onError={(e) => {
                        (e.target as HTMLElement).style.display = 'none';
                      }}
                    />
                    <div>
                      <div className="font-display text-base font-bold text-[#F2EEE3] group-hover:text-[#38BDF8]">
                        {p.name}
                      </div>
                      <div className="text-xs text-[#8E9AA8] font-data">
                        {p.role} • {p.team}
                      </div>
                    </div>
                  </div>
                  <span className="font-data text-xs text-[#8E9AA8] group-hover:text-[#F2EEE3] flex items-center gap-1">
                    <Swords className="w-3 h-3 text-[#C8102E]" /> Duel
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Venues Group */}
          {venueResults.length > 0 && (
            <div className="py-2">
              <div className="px-3 py-1 text-[10px] font-data font-bold uppercase tracking-wider text-[#8E9AA8]">
                Stadiums & Grounds ({venueResults.length})
              </div>
              {venueResults.map((v) => (
                <div
                  key={v.venue}
                  onClick={() => handleSelectVenue(v.venue)}
                  className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[#1A2230] cursor-pointer transition-colors group"
                >
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-[#FBBF24]" />
                    <span className="font-body text-sm font-semibold text-[#F2EEE3]">
                      {v.venue}
                    </span>
                  </div>
                  <span className="font-scoreboard text-xs font-bold text-[#FBBF24]">
                    {v.parRpo.toFixed(2)} RPO
                  </span>
                </div>
              ))}
            </div>
          )}

        </div>

        {/* Footer shortcuts */}
        <div className="px-4 py-2 border-t border-[#F2EEE3]/10 bg-[#05070B] flex items-center justify-between text-[11px] font-data text-[#8E9AA8]">
          <div className="flex items-center gap-3">
            <span>[↑↓] Navigate</span>
            <span>[↵] Select</span>
            <span>[Esc] Close</span>
          </div>
          <span className="text-[#10B981]">DUGOUT TELEMETRY ACTIVE</span>
        </div>
      </div>
    </div>
  );
};
