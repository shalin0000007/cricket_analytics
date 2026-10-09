"""
Tactical Matchup & Archetype Intelligence Engine.
Computes Micro-Phase H2H, Archetype Matrices, Bayesian Sample Size Shrinkage,
and Dugout Tactical Decisions.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

from src.core.constants import (
    MIN_BALLS_FOR_CREDIBLE_H2H,
    MIN_BALLS_FOR_CREDIBLE_ARCHETYPE,
    BAYESIAN_PRIOR_WEIGHT_BALLS,
)


def get_archetype_matrix(
    df: pd.DataFrame, batter: str, baselines: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Computes batter performance against all bowling archetypes with
    Bayesian shrinkage regression for small sample sizes.
    """
    b_df = df[df["batter"] == batter]
    if b_df.empty or "bowler_subtype" not in b_df.columns:
        return pd.DataFrame()

    # Pre-compute average par SR by archetype if baselines available
    archetype_par_map = {}
    if baselines is not None and not baselines.empty and "bowler_subtype" in baselines.columns:
        archetype_par_map = baselines.groupby("bowler_subtype")["par_sr"].mean().to_dict()

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

        raw_sr = (runs / legal_balls * 100) if legal_balls > 0 else 0.0
        dot_pct = (dots / legal_balls * 100) if legal_balls > 0 else 0.0
        boundary_pct = (boundaries / legal_balls * 100) if legal_balls > 0 else 0.0
        avg = (runs / dismissals) if dismissals > 0 else float("inf")

        # Bayesian shrinkage: pulls small samples towards archetype par
        par_sr = archetype_par_map.get(subtype, 130.0)
        w = BAYESIAN_PRIOR_WEIGHT_BALLS
        regressed_sr = ((legal_balls * raw_sr) + (w * par_sr)) / (legal_balls + w)

        # Statistical credibility label
        credibility = "High" if legal_balls >= MIN_BALLS_FOR_CREDIBLE_ARCHETYPE else "Low (Sample Regressed)"

        records.append({
            "bowling_archetype": subtype,
            "balls": legal_balls,
            "runs": runs,
            "dismissals": dismissals,
            "average": round(avg, 1) if avg != float("inf") else "-",
            "raw_strike_rate": round(raw_sr, 1),
            "regressed_sr": round(regressed_sr, 1),
            "dot_pct": round(dot_pct, 1),
            "boundary_pct": round(boundary_pct, 1),
            "sample_credibility": credibility,
        })

    res = pd.DataFrame(records)
    if not res.empty:
        res = res.sort_values(by="balls", ascending=False)
    return res


def get_dugout_tactical_verdict(
    df: pd.DataFrame, batter: str, bowler: str, baselines: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Generates an executive, actionable Dugout Tactical Verdict
    combining direct H2H with Archetype priors.
    """
    matchup = df[(df["batter"] == batter) & (df["bowler"] == bowler)]
    direct_balls = len(matchup[matchup["wides"] == 0])
    direct_runs = int(matchup["batter_runs"].sum()) if not matchup.empty else 0
    direct_outs = len(matchup[(matchup["is_wicket"] == 1) & (matchup["player_out"] == batter)]) if not matchup.empty else 0
    direct_dots = int(matchup["is_dot"].sum()) if not matchup.empty else 0
    direct_sr = round(direct_runs / direct_balls * 100, 1) if direct_balls > 0 else 0.0
    direct_dot_pct = round(direct_dots / direct_balls * 100, 1) if direct_balls > 0 else 0.0

    b_meta = df[df["batter"] == batter]
    b_hand = b_meta["batter_hand"].iloc[0] if not b_meta.empty and "batter_hand" in b_meta.columns else "Unknown"

    bw_meta = df[df["bowler"] == bowler]
    bowler_style = bw_meta["bowler_subtype"].iloc[0] if not bw_meta.empty and "bowler_subtype" in bw_meta.columns else "Unknown"

    # Archetype metrics
    arch_matchup = df[(df["batter"] == batter) & (df["bowler_subtype"] == bowler_style)]
    arch_balls = len(arch_matchup[arch_matchup["wides"] == 0])
    arch_runs = int(arch_matchup["batter_runs"].sum()) if arch_balls > 0 else 0
    arch_outs = len(arch_matchup[(arch_matchup["is_wicket"] == 1) & (arch_matchup["player_out"] == batter)]) if arch_balls > 0 else 0
    arch_sr = round(arch_runs / arch_balls * 100, 1) if arch_balls > 0 else 0.0
    arch_dots = int(arch_matchup["is_dot"].sum()) if arch_balls > 0 else 0
    arch_dot_pct = round(arch_dots / arch_balls * 100, 1) if arch_balls > 0 else 0.0

    # Decision Logic: Combine direct H2H (if >= 12 balls) or Archetype
    if direct_balls >= MIN_BALLS_FOR_CREDIBLE_H2H:
        eval_sr = direct_sr
        eval_outs = direct_outs
        eval_dot_pct = direct_dot_pct
        source = f"Direct H2H ({direct_balls} balls)"
    else:
        eval_sr = arch_sr
        eval_outs = arch_outs
        eval_dot_pct = arch_dot_pct
        source = f"Archetype: {batter} vs {bowler_style} ({arch_balls} balls)"

    if eval_outs >= 3 or (eval_sr < 115 and eval_dot_pct > 35):
        verdict = "CHOKE / ATTACK BOWLER MATCHUP"
        advice = f"Strong tactical advantage for {bowler}. Restricts {batter} (SR: {eval_sr}, Dot %: {eval_dot_pct}%). Deploy to build pressure or induce mistake."
        level = "bowler_advantage"
    elif eval_sr >= 145:
        verdict = "DANGER MATCHUP / BATTER ADVANTAGE"
        advice = f"{batter} aggressively attacks {bowler_style} (SR: {eval_sr}). Avoid or hold back unless field is set for boundary containment."
        level = "batter_advantage"
    else:
        verdict = "TACTICAL PAR / BALANCED BATTLE"
        advice = f"Neutral contest at SR {eval_sr}. Decision should depend on match phase and boundary dimensions."
        level = "neutral"

    return {
        "batter": batter,
        "batter_hand": b_hand,
        "bowler": bowler,
        "bowler_subtype": bowler_style,
        "direct_balls": direct_balls,
        "direct_runs": direct_runs,
        "direct_outs": direct_outs,
        "direct_sr": direct_sr,
        "direct_dot_pct": direct_dot_pct,
        "archetype_balls": arch_balls,
        "archetype_runs": arch_runs,
        "archetype_outs": arch_outs,
        "archetype_sr": arch_sr,
        "archetype_dot_pct": arch_dot_pct,
        "decision_source": source,
        "verdict": verdict,
        "level": level,
        "advice": advice,
    }
