"""
True Metrics Engine.
Computes contextual, venue-and-phase-normalized metrics:
- True Strike Rate (TSR): Batter acceleration compared to situational par.
- True Economy Rate (TER): Bowler containment compared to situational par.
- Pressure Indices: Dot ball %, Boundary Frequency, Boundary Run Reliance.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


def calculate_batter_tactical_metrics(
    df: pd.DataFrame, batter: str, baselines: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Computes a phase-by-phase tactical breakdown with True Strike Rate (TSR).
    """
    b_df = df[df["batter"] == batter]
    if b_df.empty:
        return pd.DataFrame()

    phase_par_map = {}
    if baselines is not None and not baselines.empty:
        phase_par_map = baselines.groupby("phase")["par_sr"].mean().to_dict()

    phase_stats = []
    for phase, p_df in b_df.groupby("phase"):
        legal_balls = len(p_df[p_df["wides"] == 0])
        if legal_balls == 0:
            continue

        runs = int(p_df["batter_runs"].sum())
        dots = int(p_df["is_dot"].sum())
        boundaries = int(p_df["is_boundary"].sum())
        fours = int(p_df["is_four"].sum())
        sixes = int(p_df["is_six"].sum())
        dismissals = len(p_df[(p_df["is_wicket"] == 1) & (p_df["player_out"] == batter)])

        raw_sr = (runs / legal_balls) * 100
        dot_pct = (dots / legal_balls) * 100
        boundary_pct = (boundaries / legal_balls) * 100
        boundary_runs = (fours * 4) + (sixes * 6)
        boundary_run_pct = (boundary_runs / runs * 100) if runs > 0 else 0.0
        balls_per_boundary = (legal_balls / boundaries) if boundaries > 0 else float("inf")

        par_sr = phase_par_map.get(phase, raw_sr)
        true_sr = raw_sr - par_sr

        phase_stats.append({
            "phase": phase,
            "balls": legal_balls,
            "runs": runs,
            "dismissals": dismissals,
            "strike_rate": round(raw_sr, 1),
            "true_sr": round(true_sr, 1),
            "dot_pct": round(dot_pct, 1),
            "boundary_pct": round(boundary_pct, 1),
            "boundary_run_pct": round(boundary_run_pct, 1),
            "balls_per_boundary": round(balls_per_boundary, 1) if balls_per_boundary != float("inf") else "-",
        })

    return pd.DataFrame(phase_stats)


def calculate_bowler_tactical_metrics(
    df: pd.DataFrame, bowler: str, baselines: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Computes a phase-by-phase tactical breakdown with True Economy Rate (TER).
    """
    b_df = df[df["bowler"] == bowler]
    if b_df.empty:
        return pd.DataFrame()

    phase_par_map = {}
    if baselines is not None and not baselines.empty:
        phase_par_map = baselines.groupby("phase")["par_econ"].mean().to_dict()

    records = []
    for phase, p_df in b_df.groupby("phase"):
        legal_balls = len(p_df[p_df["wides"] == 0])
        if legal_balls == 0:
            continue

        runs_conceded = int(p_df["total_runs"].sum() - p_df["byes"].sum() - p_df["legbyes"].sum())
        wickets = len(p_df[(p_df["is_wicket"] == 1) & (~p_df["wicket_kind"].isin(["run out", "retired hurt"]))])
        dots = int(p_df["is_dot"].sum())
        boundaries_conceded = int(p_df["is_boundary"].sum())

        overs = legal_balls / 6.0
        raw_econ = (runs_conceded / overs) if overs > 0 else 0.0
        dot_pct = (dots / legal_balls) * 100
        boundary_pct = (boundaries_conceded / legal_balls) * 100

        par_econ = phase_par_map.get(phase, raw_econ)
        true_econ = raw_econ - par_econ  # Negative means cheaper than par

        records.append({
            "phase": phase,
            "overs": round(legal_balls // 6 + (legal_balls % 6) / 10, 1),
            "balls": legal_balls,
            "runs": runs_conceded,
            "wickets": wickets,
            "economy": round(raw_econ, 2),
            "true_economy": round(true_econ, 2),
            "dot_pct": round(dot_pct, 1),
            "boundary_pct": round(boundary_pct, 1),
        })

    return pd.DataFrame(records)
