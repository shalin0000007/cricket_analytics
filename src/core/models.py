"""
Domain Models & Data Structures for Cricket Analytics Engine.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class BatterPhaseStats:
    phase: str
    balls: int
    runs: int
    dismissals: int
    raw_sr: float
    true_sr: float
    dot_pct: float
    boundary_pct: float
    boundary_run_pct: float
    balls_per_boundary: float


@dataclass
class BowlerPhaseStats:
    phase: str
    overs: float
    balls: int
    runs: int
    wickets: int
    economy: float
    true_economy: float
    dot_pct: float
    boundary_pct: float


@dataclass
class ArchetypeMatchup:
    archetype: str
    balls: int
    runs: int
    dismissals: int
    average: float
    strike_rate: float
    regressed_strike_rate: float  # Bayesian regressed for small sample credibility
    dot_pct: float
    boundary_pct: float


@dataclass
class DugoutMatchupVerdict:
    batter: str
    batter_hand: str
    bowler: str
    bowler_subtype: str
    direct_balls: int
    direct_runs: int
    direct_outs: int
    direct_sr: float
    direct_dot_pct: float
    archetype_balls: int
    archetype_sr: float
    archetype_dot_pct: float
    verdict: str
    recommendation: str


@dataclass
class VenueParProfile:
    venue: str
    sample_deliveries: int
    par_rpo: float
    pp_par_sr: float
    middle_par_sr: float
    death_par_sr: float
