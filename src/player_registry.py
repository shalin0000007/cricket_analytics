"""
Player Registry & Archetype Classification Module.
Enriches Cricsheet ball-by-ball deliveries with critical scouting metadata:
- Batting Hand: LHB / RHB
- Bowling Discipline: Pace / Spin
- Bowling Sub-Type: Right-arm Pace, Left-arm Pace, Left-arm Orthodox (SLA),
                   Right-arm Offbreak (OB), Right-arm Legbreak (LBG), Left-arm Wrist Spin
- Playing Role: Batter, Bowler, Allrounder, Wicketkeeper
"""

import os
import re
from typing import Dict, Any, Optional
import pandas as pd


def classify_batting_hand(style: Optional[str]) -> str:
    """Classifies batting style into canonical tactical hand (LHB / RHB)."""
    if not isinstance(style, str) or pd.isna(style) or not style.strip():
        return "Unknown"
    s = style.lower()
    if "left" in s:
        return "LHB"
    elif "right" in s:
        return "RHB"
    return "Unknown"


def classify_bowling_style(style: Optional[str]) -> tuple[str, str, str]:
    """
    Returns (bowling_type, bowling_subtype, bowler_arm).
    Examples:
      - 'Slow Left arm Orthodox' -> ('Spin', 'Left-arm Orthodox', 'Left-arm')
      - 'Right arm Fast medium'   -> ('Pace', 'Right-arm Pace', 'Right-arm')
      - 'Legbreak Googly'        -> ('Spin', 'Right-arm Legbreak', 'Right-arm')
    """
    if not isinstance(style, str) or pd.isna(style) or not style.strip():
        return "Unknown", "Unknown", "Unknown"

    s = style.lower().strip()
    arm = "Left-arm" if "left" in s else ("Right-arm" if "right" in s else "Unknown")

    # Spin category
    if "orthodox" in s:
        return "Spin", "Left-arm Orthodox", "Left-arm"
    elif "wrist spin" in s or "chinaman" in s:
        return "Spin", "Left-arm Wrist Spin", "Left-arm"
    elif any(k in s for k in ["legbreak", "leg-break", "leg break"]):
        return "Spin", "Right-arm Legbreak", "Right-arm"
    elif any(k in s for k in ["offbreak", "off-break", "off break"]):
        return "Spin", "Right-arm Offbreak", "Right-arm"
    elif "spin" in s or "slow" in s:
        sub = f"{arm} Spin" if arm != "Unknown" else "Spin"
        return "Spin", sub, arm

    # Pace category
    elif any(k in s for k in ["fast", "medium", "pace", "seam"]):
        sub = f"{arm} Pace" if arm != "Unknown" else "Pace"
        return "Pace", sub, arm

    return "Unknown", "Unknown", arm


class PlayerRegistry:
    """
    Master registry mapping player IDs and names to tactical archetypes.
    Primary key: Cricsheet ID (hash)
    Secondary key: Normalized name strings
    """

    def __init__(self, metadata_path: Optional[str] = None):
        if metadata_path is None:
            metadata_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "metadata", "player_meta.csv"
            )
        self.metadata_path = metadata_path
        self.id_map: Dict[str, Dict[str, Any]] = {}
        self.name_map: Dict[str, Dict[str, Any]] = {}
        self._load_registry()

    def _normalize_name(self, name: str) -> str:
        if not isinstance(name, str):
            return ""
        return re.sub(r"[^a-z0-9]", "", name.lower())

    def _load_registry(self):
        if not os.path.exists(self.metadata_path):
            print(f"[Warning] Player metadata not found at {self.metadata_path}. Using fallback defaults.")
            return

        df = pd.read_csv(self.metadata_path, low_memory=False)

        for _, row in df.iterrows():
            cid = str(row.get("cricsheet_id", "")).strip()
            name = str(row.get("name", "")).strip()
            full_name = str(row.get("full_name", "")).strip()
            unique_name = str(row.get("unique_name", "")).strip()
            batting_raw = str(row.get("batting_style", "")) if pd.notna(row.get("batting_style")) else ""
            bowling_raw = str(row.get("bowling_style", "")) if pd.notna(row.get("bowling_style")) else ""
            role_raw = str(row.get("playing_role", "")) if pd.notna(row.get("playing_role")) else ""

            b_hand = classify_batting_hand(batting_raw)
            b_type, b_subtype, b_arm = classify_bowling_style(bowling_raw)

            profile = {
                "cricsheet_id": cid,
                "name": name if name and name != "nan" else full_name,
                "batting_hand": b_hand,
                "bowling_type": b_type,
                "bowling_subtype": b_subtype,
                "bowler_arm": b_arm,
                "playing_role": role_raw if role_raw != "nan" else "Unknown",
            }

            if cid and cid != "nan":
                self.id_map[cid] = profile

            # Index by various name representations
            for n_val in [name, full_name, unique_name]:
                if n_val and n_val != "nan":
                    norm = self._normalize_name(n_val)
                    if norm:
                        self.name_map[norm] = profile

    def get_player(self, player_id: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Look up player by ID with name fallback."""
        if player_id and player_id in self.id_map:
            return self.id_map[player_id]

        if name:
            norm = self._normalize_name(name)
            if norm in self.name_map:
                return self.name_map[norm]

        return {
            "cricsheet_id": player_id or "",
            "name": name or "Unknown",
            "batting_hand": "Unknown",
            "bowling_type": "Unknown",
            "bowling_subtype": "Unknown",
            "bowler_arm": "Unknown",
            "playing_role": "Unknown",
        }

    def enrich_deliveries(
        self, df: pd.DataFrame, people_registry: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Enriches a ball-by-ball DataFrame with tactical archetype columns:
        - batter_hand, batter_role
        - bowler_type, bowler_subtype, bowler_arm
        - matchup_archetype: e.g. 'LHB vs Left-arm Orthodox', 'RHB vs Right-arm Pace'
        """
        if df.empty:
            return df

        reg = people_registry or {}
        enriched = df.copy()

        # Cache lookups for unique players in this match
        unique_batters = enriched["batter"].unique()
        unique_bowlers = enriched["bowler"].unique()

        batter_profiles = {}
        for b in unique_batters:
            b_id = reg.get(b)
            batter_profiles[b] = self.get_player(player_id=b_id, name=b)

        bowler_profiles = {}
        for b in unique_bowlers:
            b_id = reg.get(b)
            bowler_profiles[b] = self.get_player(player_id=b_id, name=b)

        # Vectorized mapping
        enriched["batter_hand"] = enriched["batter"].map(
            lambda x: batter_profiles.get(x, {}).get("batting_hand", "Unknown")
        )
        enriched["batter_role"] = enriched["batter"].map(
            lambda x: batter_profiles.get(x, {}).get("playing_role", "Unknown")
        )
        enriched["bowler_type"] = enriched["bowler"].map(
            lambda x: bowler_profiles.get(x, {}).get("bowling_type", "Unknown")
        )
        enriched["bowler_subtype"] = enriched["bowler"].map(
            lambda x: bowler_profiles.get(x, {}).get("bowling_subtype", "Unknown")
        )
        enriched["bowler_arm"] = enriched["bowler"].map(
            lambda x: bowler_profiles.get(x, {}).get("bowler_arm", "Unknown")
        )
        enriched["matchup_archetype"] = (
            enriched["batter_hand"] + " vs " + enriched["bowler_subtype"]
        )

        return enriched


# Singleton helper
_GLOBAL_REGISTRY: Optional[PlayerRegistry] = None


def get_default_registry() -> PlayerRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = PlayerRegistry()
    return _GLOBAL_REGISTRY
