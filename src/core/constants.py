"""
Core Constants & Tactical Enums for Cricket Analytics.
Defines canonical phases, archetypes, and era boundaries.
"""

from enum import Enum
from typing import List, Dict

# Tactical Phase Definitions (0-indexed overs)
PHASE_POWERPLAY = "Powerplay (0-6)"
PHASE_MIDDLE = "Middle Overs (7-15)"
PHASE_DEATH = "Death Overs (16-20)"

ALL_PHASES: List[str] = [PHASE_POWERPLAY, PHASE_MIDDLE, PHASE_DEATH]

# Bowling Archetypes
ARCHETYPE_RA_PACE = "Right-arm Pace"
ARCHETYPE_LA_PACE = "Left-arm Pace"
ARCHETYPE_LA_ORTHODOX = "Left-arm Orthodox"
ARCHETYPE_RA_OFFBREAK = "Right-arm Offbreak"
ARCHETYPE_RA_LEGBREAK = "Right-arm Legbreak"
ARCHETYPE_LA_WRIST_SPIN = "Left-arm Wrist Spin"

ALL_ARCHETYPES: List[str] = [
    ARCHETYPE_RA_PACE,
    ARCHETYPE_LA_PACE,
    ARCHETYPE_LA_ORTHODOX,
    ARCHETYPE_RA_OFFBREAK,
    ARCHETYPE_RA_LEGBREAK,
    ARCHETYPE_LA_WRIST_SPIN,
]

# Batting Hands
HAND_LHB = "LHB"
HAND_RHB = "RHB"

# Era & Recency Windows
ERA_RECENT_START_YEAR = 2022  # Post mega-auction and modern high-scoring par era
ERA_ALL_TIME_START_YEAR = 2008

# Minimum Statistical Credibility Thresholds
MIN_BALLS_FOR_CREDIBLE_H2H = 12
MIN_BALLS_FOR_CREDIBLE_ARCHETYPE = 24
BAYESIAN_PRIOR_WEIGHT_BALLS = 18.0  # Weight given to tournament par for small samples
