"""
Tactical Metrics & Contextual Decision Engine.
Calculates high-leverage metrics used by IPL decision-makers:
- True Strike Rate (TSR): Strike rate normalized against phase/archetype par.
- True Economy Rate (TER): Economy rate normalized against phase par.
- Dot Ball Pressure Index: Ratio of dots forced vs legal balls.
- Boundary Frequency & Boundary Run Reliance: Balls per boundary & % runs from boundaries.
- Archetype Matchup Matrix: Batter performance split by bowling style (SLA, LBG, OB, Left/Right Pace).
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


def compute_phase_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes par benchmark performance metrics grouped by phase and bowling subtype.
    Used to calculate True Strike Rate (TSR) and True Economy Rate (TER).
    """
    if df.empty:
        return pd.DataFrame()

    records = []
    # Group by phase (and optionally bowling_subtype if available)
    has_subtype = "bowler_subtype" in df.columns

    group_cols = ["phase"]
    if has_subtype:
        group_cols.append("bowler_subtype")

    for keys, sub_df in df.groupby(group_cols):
        phase = keys[0] if isinstance(keys, tuple) else keys
        bowler_sub = keys[1] if isinstance(keys, tuple) and len(keys) > 1 else "All"

        legal_balls = len(sub_df[sub_df["wides"] == 0])
        if legal_balls == 0:
            continue

        runs = sub_df["batter_runs"].sum()
        total_runs = sub_df["total_runs"].sum() - sub_df["byes"].sum() - sub_df["legbyes"].sum()
        dots = sub_df["is_dot"].sum()
        boundaries = sub_df["is_boundary"].sum()
        wickets = len(sub_df[(sub_df["is_wicket"] == 1) & (~sub_df["wicket_kind"].isin(["run out", "retired hurt"]))])

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


def get_batter_tactical_profile(
    df: pd.DataFrame, batter: str, baselines: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Generates a phase-segmented tactical profile for a batter, including
    True Strike Rate (TSR), Boundary % and Dot %.
    """
    b_df = df[df["batter"] == batter]
    if b_df.empty:
        return pd.DataFrame()

    # Pre-calculate baseline par by phase if provided
    phase_par_map = {}
    if baselines is not None and not baselines.empty:
        # Group general phase average
        agg_par = baselines.groupby("phase")["par_sr"].mean().to_dict()
        phase_par_map = agg_par

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


def get_bowler_tactical_profile(
    df: pd.DataFrame, bowler: str, baselines: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Generates a phase-segmented tactical profile for a bowler, including
    True Economy Rate (TER), Dot Ball Pressure %, and Wickets.
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
        true_econ = raw_econ - par_econ  # Negative is better (cheaper than par)

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


def get_archetype_matchup_matrix(df: pd.DataFrame, batter: str) -> pd.DataFrame:
    """
    Computes batter performance split across bowling archetypes:
    (Right-arm Pace, Left-arm Pace, Left-arm Orthodox, Right-arm Offbreak, Right-arm Legbreak).
    Answers: 'What bowler type chokes or dismisses this batter?'
    """
    b_df = df[df["batter"] == batter]
    if b_df.empty or "bowler_subtype" not in b_df.columns:
        return pd.DataFrame()

    records = []
    for subtype, sub_df in b_df.groupby("bowler_subtype"):
        if subtype in ["Unknown", ""]:
            continue

        legal_balls = len(sub_df[sub_df["wides"] == 0])
        if legal_balls == 0:
            continue

        runs = int(sub_df["batter_runs"].sum())
        dismissals = len(sub_df[(sub_df["is_wicket"] == 1) & (sub_df["player_out"] == batter)])
        dots = int(sub_df["is_dot"].sum())
        boundaries = int(sub_df["is_boundary"].sum())

        sr = (runs / legal_balls * 100) if legal_balls > 0 else 0.0
        dot_pct = (dots / legal_balls * 100) if legal_balls > 0 else 0.0
        boundary_pct = (boundaries / legal_balls * 100) if legal_balls > 0 else 0.0
        avg = (runs / dismissals) if dismissals > 0 else float("inf")

        records.append({
            "bowling_archetype": subtype,
            "balls": legal_balls,
            "runs": runs,
            "dismissals": dismissals,
            "average": round(avg, 1) if avg != float("inf") else "-",
            "strike_rate": round(sr, 1),
            "dot_pct": round(dot_pct, 1),
            "boundary_pct": round(boundary_pct, 1),
        })

    res = pd.DataFrame(records)
    if not res.empty:
        res = res.sort_values(by="balls", ascending=False)
    return res


def get_dugout_matchup_summary(
    df: pd.DataFrame, batter: str, bowler: str
) -> Dict[str, Any]:
    """
    Generates an instant 10-second Dugout Decision Summary between a batter and bowler.
    Combines Head-to-Head with Archetype baseline context.
    """
    matchup = df[(df["batter"] == batter) & (df["bowler"] == bowler)]
    balls_faced = len(matchup[matchup["wides"] == 0])
    runs_scored = int(matchup["batter_runs"].sum()) if not matchup.empty else 0
    dismissals = len(matchup[(matchup["is_wicket"] == 1) & (matchup["player_out"] == batter)]) if not matchup.empty else 0

    sr = (runs_scored / balls_faced * 100) if balls_faced > 0 else 0.0
    dots = int(matchup["is_dot"].sum()) if not matchup.empty else 0
    dot_pct = (dots / balls_faced * 100) if balls_faced > 0 else 0.0
    fours = int(matchup["is_four"].sum()) if not matchup.empty else 0
    sixes = int(matchup["is_six"].sum()) if not matchup.empty else 0

    # Archetype details
    b_hand = matchup["batter_hand"].iloc[0] if not matchup.empty and "batter_hand" in matchup.columns else "Unknown"
    b_style = matchup["bowler_subtype"].iloc[0] if not matchup.empty and "bowler_subtype" in matchup.columns else "Unknown"

    # Tactical Verdict
    verdict = "INSUFFICIENT SAMPLE"
    if balls_faced >= 10:
        if dismissals >= 2 or (sr < 110 and dot_pct > 45):
            verdict = "FAVOR BOWLER (High Pressure / Dismissal Threat)"
        elif sr > 150:
            verdict = "FAVOR BATTER (High Scoring / Exploit Matchup)"
        else:
            verdict = "NEUTRAL / TACTICAL PAR"

    return {
        "batter": batter,
        "batter_hand": b_hand,
        "bowler": bowler,
        "bowler_subtype": b_style,
        "sample_size": "H2H (Direct)",
        "balls_faced": balls_faced,
        "runs_scored": runs_scored,
        "dismissals": dismissals,
        "strike_rate": round(sr, 1),
        "dot_pct": round(dot_pct, 1),
        "fours": fours,
        "sixes": sixes,
        "verdict": verdict,
    }
