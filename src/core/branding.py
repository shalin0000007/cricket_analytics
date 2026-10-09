"""
Branding, Team Visual Assets & Player Headshot Registry.
Provides official IPL franchise colorways, crests, and ESPN Cricinfo player headshots.
"""

import os
import re
from typing import Dict, Optional, Any
import pandas as pd

# IPL Franchise Color Codes & Badges
IPL_TEAM_BRANDING: Dict[str, Dict[str, str]] = {
    "Chennai Super Kings": {
        "primary": "#facc15",
        "secondary": "#1e3a8a",
        "accent": "#fbbf24",
        "short": "CSK",
    },
    "Mumbai Indians": {
        "primary": "#0284c7",
        "secondary": "#eab308",
        "accent": "#38bdf8",
        "short": "MI",
    },
    "Kolkata Knight Riders": {
        "primary": "#7c3aed",
        "secondary": "#f59e0b",
        "accent": "#a855f7",
        "short": "KKR",
    },
    "Royal Challengers Bengaluru": {
        "primary": "#dc2626",
        "secondary": "#f59e0b",
        "accent": "#ef4444",
        "short": "RCB",
    },
    "Rajasthan Royals": {
        "primary": "#ec4899",
        "secondary": "#1e3a8a",
        "accent": "#f472b6",
        "short": "RR",
    },
    "Sunrisers Hyderabad": {
        "primary": "#f97316",
        "secondary": "#0f172a",
        "accent": "#fb923c",
        "short": "SRH",
    },
    "Gujarat Titans": {
        "primary": "#1e293b",
        "secondary": "#38bdf8",
        "accent": "#0ea5e9",
        "short": "GT",
    },
    "Delhi Capitals": {
        "primary": "#0284c7",
        "secondary": "#dc2626",
        "accent": "#38bdf8",
        "short": "DC",
    },
    "Lucknow Super Giants": {
        "primary": "#06b6d4",
        "secondary": "#f97316",
        "accent": "#22d3ee",
        "short": "LSG",
    },
    "Punjab Kings": {
        "primary": "#ef4444",
        "secondary": "#94a3b8",
        "accent": "#f87171",
        "short": "PBKS",
    },
}

DEFAULT_SILHOUETTE_URL = "https://raw.githubusercontent.com/bhavanachitragar/Ipl-data-analysis-with-powerbi/main/images/avatar.png"

# Common Name Aliases for Cricsheet Match Names
NAME_ALIASES: Dict[str, str] = {
    "v kohli": "virat kohli",
    "rg sharma": "rohit sharma",
    "ms dhoni": "ms dhoni",
    "jj bumrah": "jasprit bumrah",
    "kl rahul": "kl rahul",
    "sa yadav": "suryakumar yadav",
    "hh pandya": "hardik pandya",
    "s dube": "shivam dube",
    "rd gaikwad": "ruturaj gaikwad",
    "ra jadeja": "ravindra jadeja",
    "jc buttler": "jos buttler",
    "ybk jaiswal": "yashasvi jaiswal",
    "sv samson": "sanju samson",
    "shubman gill": "shubman gill",
    "b sai sudharsan": "sai sudharsan",
    "tm head": "travis head",
    "h klaasen": "heinrich klaasen",
    "rashid khan": "rashid khan",
    "ma starc": "mitchell starc",
    "sunil narine": "sunil narine",
    "ad russell": "andre russell",
    "cv varun": "varun chakravarthy",
    "mohammed siraj": "mohammed siraj",
    "mohammed shami": "mohammed shami",
    "kuldeep yadav": "kuldeep yadav",
    "ys chahal": "yuzvendra chahal",
    "arshdeep singh": "arshdeep singh",
    "pj cummins": "pat cummins",
}


class PlayerVisualRegistry:
    """Manages player images and headshots from official sources."""

    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            csv_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "metadata", "player_images.csv"
            )
        self.csv_path = csv_path
        self.image_map: Dict[str, str] = {}
        self.team_map: Dict[str, str] = {}
        self._load()

    def _clean(self, s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower()) if isinstance(s, str) else ""

    def _load(self):
        if not os.path.exists(self.csv_path):
            return
        df = pd.read_csv(self.csv_path)
        for _, row in df.iterrows():
            p_name = str(row.get("player", "")).strip()
            img_url = str(row.get("Image", "")).strip()
            team_val = str(row.get("team", "")).strip()

            if p_name and img_url and img_url.startswith("http"):
                clean_n = self._clean(p_name)
                self.image_map[clean_n] = img_url
                self.team_map[clean_n] = team_val

    def get_player_image(self, name: str) -> str:
        """Looks up headshot image URL with alias handling."""
        if not name:
            return DEFAULT_SILHOUETTE_URL

        clean = self._clean(name)
        if clean in self.image_map:
            return self.image_map[clean]

        # Check alias
        alias = NAME_ALIASES.get(name.lower().strip())
        if alias:
            clean_alias = self._clean(alias)
            if clean_alias in self.image_map:
                return self.image_map[clean_alias]

        # Substring search
        for k, url in self.image_map.items():
            if clean in k or k in clean:
                return url

        return DEFAULT_SILHOUETTE_URL

    def get_player_team(self, name: str) -> str:
        clean = self._clean(name)
        if clean in self.team_map:
            return self.team_map[clean]
        alias = NAME_ALIASES.get(name.lower().strip())
        if alias and self._clean(alias) in self.team_map:
            return self.team_map[self._clean(alias)]
        return "IPL"


# Singleton
_GLOBAL_VISUAL_REGISTRY: Optional[PlayerVisualRegistry] = None


def get_visual_registry() -> PlayerVisualRegistry:
    global _GLOBAL_VISUAL_REGISTRY
    if _GLOBAL_VISUAL_REGISTRY is None:
        _GLOBAL_VISUAL_REGISTRY = PlayerVisualRegistry()
    return _GLOBAL_VISUAL_REGISTRY
