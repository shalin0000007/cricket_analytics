export type WorkspaceId = 'arena' | 'tape' | 'warroom' | 'metrics' | 'dossier';

export type Era = 'recent' | 'alltime';

export type PlayerRole = 'Opening Batter' | 'Top-order Batter' | 'Middle-order Batter' | 'Finisher' | 'Allrounder' | 'Pace Bowler' | 'Spin Bowler';

export type BowlingArchetype = 
  | 'Right-arm Pace'
  | 'Left-arm Pace'
  | 'Right-arm Offbreak'
  | 'Right-arm Legbreak'
  | 'Left-arm Orthodox'
  | 'Left-arm Wrist Spin';

export interface Player {
  name: string;
  hand?: 'RHB' | 'LHB';
  role?: string;
  bowlerType?: 'Pace' | 'Spin';
  bowlerSubtype?: BowlingArchetype;
  team: string;
  image: string;
}

export interface MatchupVerdict {
  batter: string;
  batterHand: 'RHB' | 'LHB';
  bowler: string;
  bowlerSubtype: BowlingArchetype;
  directBalls: number;
  directRuns: number;
  directOuts: number;
  directSr: number;
  directDotPct: number;
  archetypeBalls: number;
  archetypeRuns: number;
  archetypeOuts: number;
  archetypeSr: number;
  regressedSr: number;
  archetypeDotPct: number;
  decisionSource: string;
  verdict: string;
  level: 'bowler_advantage' | 'batter_advantage' | 'neutral';
  advice: string;
}

export interface DeliveryBall {
  over: number;
  ball: number;
  runs: number;
  isDot: boolean;
  isFour: boolean;
  isSix: boolean;
  isWicket: boolean;
  wicketKind?: string;
  matchId?: string;
  date?: string;
}

export interface BatterPhaseStat {
  phase: string;
  balls: number;
  runs: number;
  dismissals: number;
  strikeRate: number;
  trueSr: number;
  dotPct: number;
  boundaryPct: number;
  boundaryRunPct: number;
  ballsPerBoundary: number;
}

export interface BowlerPhaseStat {
  phase: string;
  overs: number;
  balls: number;
  runs: number;
  wickets: number;
  economy: number;
  trueEconomy: number;
  dotPct: number;
  boundaryPct: number;
}

export interface BatterRadarProfile {
  'Powerplay Velocity': number;
  'Middle Phase Control': number;
  'Death Finishing Power': number;
  'Boundary Frequency': number;
  'Dot Avoidance': number;
  'Dismissal Resistance': number;
  'Spin Mastery': number;
  'Pace Acceleration': number;
}

export interface BowlerRadarProfile {
  'Powerplay Control': number;
  'Middle Overs Choke': number;
  'Death Yorker Control': number;
  'Dot Ball Mastery': number;
  'Boundary Suppression': number;
  'Wicket Strike Rate': number;
  'Powerplay Dot Pressure': number;
  'Workhorse Volume': number;
}

export interface VenuePar {
  venue: string;
  parRpo: number;
  sampleDeliveries: number;
  ppParSr: number;
  middleParSr: number;
  deathParSr: number;
}

export interface BowlingPlanOver {
  bowler: string;
  overs: number;
  subtype: string;
  role: string;
  metric: string;
}

export interface BowlingPlan {
  plan: {
    'Powerplay (Overs 1-6)': BowlingPlanOver[];
    'Middle (Overs 7-15)': BowlingPlanOver[];
    'Death (Overs 16-20)': BowlingPlanOver[];
  };
  oversByBowler: Record<string, number>;
}
