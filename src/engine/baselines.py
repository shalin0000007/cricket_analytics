"""
Contextual Par Benchmarks & Venue-Adjustment Engine.
Calculates situational baseline standards across phases, archetypes, and venues.
"""

from typing import Dict, Any, Optional
import pandas as pd


def compute_contextual_baselines(
    df: pd.DataFrame, venue: Optional[str] = None
) -> pd.DataFrame:
    """
    Computes par benchmark performance metrics grouped by phase and bowling archetype.
    If a venue is supplied, computes venue-specific par baselines.
    """
    if df.empty:
        return pd.DataFrame()

    data = df
    if venue and venue != "All Venues":
        v_data = df[df["venue"].str.contains(venue, case=False, na=False)]
        # If sufficient sample at venue (>= 500 balls), use venue data
        if len(v_data) >= 500:
            data = v_data

    records = []
    has_subtype = "bowler_subtype" in data.columns
    group_cols = ["phase"]
    if has_subtype:
        group_cols.append("bowler_subtype")

    for keys, sub_df in data.groupby(group_cols):
        phase = keys[0] if isinstance(keys, tuple) else keys
        bowler_sub = keys[1] if isinstance(keys, tuple) and len(keys) > 1 else "All"

        legal_balls = len(sub_df[sub_df["wides"] == 0])
        if legal_balls == 0:
            continue

        runs = sub_df["batter_runs"].sum()
        total_runs = sub_df["total_runs"].sum() - sub_df["byes"].sum() - sub_df["legbyes"].sum()
        dots = sub_df["is_dot"].sum()
        boundaries = sub_df["is_boundary"].sum()

        par_sr = (runs / legal_balls) * 100
        par_econ = (total_runs / (legal_balls / 6.0)) if legal_balls > 0 else 0.0
        par_dot_pct = (dots / legal_balls) * 100
        par_boundary_pct = (boundaries / legal_balls) * 100

        records.append({
            "phase": phase,
            "bowler_subtype": bowler_sub,
            "sample_balls": legal_balls,
            "par_sr": round(par_sr, 2),
            "par_econ": round(par_econ, 2),
            "par_dot_pct": round(par_dot_pct, 2),
            "par_boundary_pct": round(par_boundary_pct, 2),
        })

    return pd.DataFrame(records)
