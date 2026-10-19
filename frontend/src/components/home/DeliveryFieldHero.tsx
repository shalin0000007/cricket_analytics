import React from 'react';
import { useTerminalStore } from '../../store/useTerminalStore';
import { DeliveryFieldCanvas } from './DeliveryFieldCanvas';
import { Search, Swords, Sparkles, ArrowRight } from 'lucide-react';

const FEATURED_DUELS = [
  {
    batter: 'V Kohli',
    bowler: 'JJ Bumrah',
    batterTeam: 'RCB',
    bowlerTeam: 'MI',
    batterImg: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait/prd/assets/players/generic/253802.png',
    bowlerImg: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait/prd/assets/players/generic/1124.png',
    headline: 'CLASH OF TITANS',
    stat: '24 balls • SR 137.5 • 1 Wicket',
    tag: 'TACTICAL PAR',
    tagColor: 'text-[#FBBF24] border-[#FBBF24]/30 bg-[#FBBF24]/10',
  },
  {
    batter: 'Shubman Gill',
    bowler: 'MA Starc',
    batterTeam: 'GT',
    bowlerTeam: 'KKR',
    batterImg: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait/prd/assets/players/generic/66818.png',
    bowlerImg: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait/prd/assets/players/generic/488.png',
    headline: 'PACE VELOCITY DUEL',
    stat: 'Regressed SR 136.3 vs LA Pace',
    tag: 'CHOKE HAZARD',
    tagColor: 'text-[#C8102E] border-[#C8102E]/30 bg-[#C8102E]/10',
  },
  {
    batter: 'H Klaasen',
    bowler: 'Rashid Khan',
    batterTeam: 'SRH',
    bowlerTeam: 'GT',
    batterImg: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait/prd/assets/players/generic/40836.png',
    bowlerImg: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait/prd/assets/players/generic/2887.png',
    headline: 'SPIN DEMOLITION',
    stat: 'Klaasen SR 198.4 vs Legbreak',
    tag: 'BATTER ATTACK',
    tagColor: 'text-[#10B981] border-[#10B981]/30 bg-[#10B981]/10',
  },
];

export const DeliveryFieldHero: React.FC = () => {
  const { setSelectedBatter, setSelectedBowler, setActiveWorkspace, setCommandOpen } = useTerminalStore();

  const handleLaunchDuel = (batter: string, bowler: string) => {
    setSelectedBatter(batter);
    setSelectedBowler(bowler);
    setActiveWorkspace('arena');
  };

  return (
    <div className="space-y-6">
      
      {/* Signature Delivery Field Visualization */}
      <DeliveryFieldCanvas />

      {/* Huge Command Search Bar */}
      <div className="relative max-w-3xl mx-auto">
        <button
          onClick={() => setCommandOpen(true)}
          className="w-full flex items-center justify-between px-6 py-4 rounded-xl bg-[#0D1117] hover:bg-[#131924] border border-[#F2EEE3]/20 hover:border-[#C8102E]/60 text-left transition-all shadow-[0_10px_30px_rgba(0,0,0,0.6)] group"
        >
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-lg bg-[#C8102E]/10 border border-[#C8102E]/30 text-[#C8102E] group-hover:scale-105 transition-transform">
              <Search className="w-5 h-5" />
            </div>
            <div>
              <div className="font-display text-lg font-bold text-[#F2EEE3] tracking-wide">
                SEARCH ANY IPL PLAYER, VENUE, OR MATCHUP DUEL...
              </div>
              <div className="font-data text-xs text-[#8E9AA8]">
                295k+ deliveries • 16k+ players • 8-axis radars • 50ms DuckDB OLAP queries
              </div>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-2">
            <kbd className="px-2.5 py-1 rounded bg-[#05070B] border border-[#F2EEE3]/20 font-data text-xs text-[#8E9AA8]">
              ⌘K
            </kbd>
            <ArrowRight className="w-4 h-4 text-[#8E9AA8] group-hover:text-[#F2EEE3] transition-colors" />
          </div>
        </button>
      </div>

      {/* 3 Featured Duels Cluster */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-[#FBBF24]" />
            <h2 className="font-display text-lg font-black tracking-wider text-[#F2EEE3] uppercase">
              FEATURED TACTICAL DUELS // 1-CLICK LAUNCH
            </h2>
          </div>
          <span className="font-data text-xs text-[#8E9AA8]">
            SELECT TO SIMULATE DIRECT HEAD-TO-HEAD
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {FEATURED_DUELS.map((duel, idx) => (
            <div
              key={idx}
              onClick={() => handleLaunchDuel(duel.batter, duel.bowler)}
              className="relative p-4 rounded-xl bg-[#0D1117]/90 hover:bg-[#131924] border border-[#F2EEE3]/10 hover:border-[#C8102E]/50 cursor-pointer transition-all group shadow-lg hover:shadow-[0_8px_25px_rgba(200,16,46,0.2)]"
            >
              {/* Header tag */}
              <div className="flex items-center justify-between mb-3">
                <span className="font-data text-[10px] text-[#8E9AA8] uppercase">
                  {duel.headline}
                </span>
                <span className={`px-2 py-0.5 rounded font-data text-[10px] font-bold border ${duel.tagColor}`}>
                  {duel.tag}
                </span>
              </div>

              {/* Player Avatars Facing Off */}
              <div className="flex items-center justify-between py-2">
                
                {/* Batter */}
                <div className="flex items-center gap-2.5">
                  <img
                    src={duel.batterImg}
                    alt={duel.batter}
                    className="w-12 h-12 rounded-full object-cover border-2 border-[#38BDF8]"
                    onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                  />
                  <div>
                    <div className="font-display text-base font-bold text-[#F2EEE3] leading-none">
                      {duel.batter}
                    </div>
                    <span className="font-data text-[11px] text-[#38BDF8]">{duel.batterTeam}</span>
                  </div>
                </div>

                {/* VS Badge */}
                <div className="font-scoreboard text-sm font-bold text-[#8E9AA8] group-hover:text-[#C8102E] transition-colors">
                  VS
                </div>

                {/* Bowler */}
                <div className="flex items-center gap-2.5 text-right">
                  <div>
                    <div className="font-display text-base font-bold text-[#F2EEE3] leading-none">
                      {duel.bowler}
                    </div>
                    <span className="font-data text-[11px] text-[#F43F5E]">{duel.bowlerTeam}</span>
                  </div>
                  <img
                    src={duel.bowlerImg}
                    alt={duel.bowler}
                    className="w-12 h-12 rounded-full object-cover border-2 border-[#F43F5E]"
                    onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                  />
                </div>

              </div>

              {/* Subtitle Stat */}
              <div className="mt-3 pt-2.5 border-t border-[#F2EEE3]/5 flex items-center justify-between text-xs font-data">
                <span className="text-[#8E9AA8]">{duel.stat}</span>
                <span className="text-[#F2EEE3] group-hover:text-[#C8102E] font-semibold flex items-center gap-1 transition-colors">
                  <Swords className="w-3.5 h-3.5" /> Duel
                </span>
              </div>

            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
