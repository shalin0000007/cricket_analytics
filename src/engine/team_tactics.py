"""
Team Tactics & Probable XI Strategy Engine.
Computes Probable XI vs Probable XI Matchup Matrices, Heatmaps,
and 20-Over Bowling Plan Allocation.
"""

from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

from src.core.constants import (
    MIN_BALLS_FOR_CREDIBLE_H2H,
    BAYESIAN_PRIOR_WEIGHT_BALLS,
    PHASE_POWERPLAY,
    PHASE_MIDDLE,
    PHASE_DEATH,
)
from src.engine.true_metrics import (
    calculate_batter_tactical_metrics,
    calculate_bowler_tactical_metrics,
)


def compute_team_matchup_matrix(
    df: pd.DataFrame,
    batters: List[str],
    bowlers: List[str],
    baselines: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes an N x M tactical matchup matrix between a batting lineup and bowling attack.
    Returns:
      1. advantage_df: Numerical advantage score (-3.0 to +3.0)
         - Negative (< -0.5): Bowler Advantage (Choke / Wicket Risk)
         - Positive (> +0.5): Batter Advantage (Scoring Threat)
         - Near 0: Par / Neutral
      2. details_df: Formatted tactical summary string per cell
    """
    adv_data = {b: [] for b in bowlers}
    det_data = {b: [] for b in bowlers}

    archetype_par_map = {}
    if baselines is not None and not baselines.empty and "bowler_subtype" in baselines.columns:
        archetype_par_map = baselines.groupby("bowler_subtype")["par_sr"].mean().to_dict()

    for batter in batters:
        b_meta = df[df["batter"] == batter]
        b_hand = b_meta["batter_hand"].iloc[0] if not b_meta.empty and "batter_hand" in b_meta.columns else "Unknown"

        for bowler in bowlers:
            bw_meta = df[df["bowler"] == bowler]
            bw_style = bw_meta["bowler_subtype"].iloc[0] if not bw_meta.empty and "bowler_subtype" in bw_meta.columns else "Unknown"

            # 1. Direct H2H
            h2h = df[(df["batter"] == batter) & (df["bowler"] == bowler)]
            direct_balls = len(h2h[h2h["wides"] == 0])
            direct_runs = int(h2h["batter_runs"].sum()) if not h2h.empty else 0
            direct_outs = len(h2h[(h2h["is_wicket"] == 1) & (h2h["player_out"] == batter)]) if not h2h.empty else 0
            direct_dots = int(h2h["is_dot"].sum()) if not h2h.empty else 0
            direct_sr = (direct_runs / direct_balls * 100) if direct_balls > 0 else 0.0
            direct_dot_pct = (direct_dots / direct_balls * 100) if direct_balls > 0 else 0.0

            # 2. Archetype Matchup
            arch = df[(df["batter"] == batter) & (df["bowler_subtype"] == bw_style)]
            arch_balls = len(arch[arch["wides"] == 0])
            arch_runs = int(arch["batter_runs"].sum()) if not arch.empty else 0
            arch_outs = len(arch[(arch["is_wicket"] == 1) & (arch["player_out"] == batter)]) if not arch.empty else 0
            arch_dots = int(arch["is_dot"].sum()) if not arch.empty else 0
            arch_sr = (arch_runs / arch_balls * 100) if arch_balls > 0 else 0.0
            arch_dot_pct = (arch_dots / arch_balls * 100) if arch_balls > 0 else 0.0

            # Bayesian regressed archetype SR
            par_sr = archetype_par_map.get(bw_style, 130.0)
            w = BAYESIAN_PRIOR_WEIGHT_BALLS
            reg_sr = ((arch_balls * arch_sr) + (w * par_sr)) / (arch_balls + w) if arch_balls > 0 else par_sr

            # Calculate Advantage Score
            if direct_balls >= MIN_BALLS_FOR_CREDIBLE_H2H:
                # Direct H2H takes precedence
                sr_diff = (direct_sr - 130.0) / 25.0
                out_penalty = direct_outs * 1.2
                dot_factor = (30.0 - direct_dot_pct) / 15.0
                score = np.clip(sr_diff - out_penalty + dot_factor, -3.0, 3.0)
                detail = f"H2H: {direct_balls}b, {direct_runs}r, {direct_outs}w | SR {direct_sr:.1f} | Dot {direct_dot_pct:.0f}%"
            else:
                # Archetype priors
                sr_diff = (reg_sr - 130.0) / 30.0
                out_rate = (arch_outs / (arch_balls / 20.0)) if arch_balls >= 10 else 0.0
                out_penalty = out_rate * 0.8
                dot_factor = (30.0 - arch_dot_pct) / 20.0
                score = np.clip(sr_diff - out_penalty + dot_factor, -3.0, 3.0)
                detail = f"vs {bw_style}: {arch_balls}b, {arch_outs}w | Reg SR {reg_sr:.1f} | Dot {arch_dot_pct:.0f}%"

            adv_data[bowler].append(round(score, 2))
            det_data[bowler].append(detail)

    adv_df = pd.DataFrame(adv_data, index=batters)
    det_df = pd.DataFrame(det_data, index=batters)
    return adv_df, det_df


def generate_20_over_bowling_plan(
    df: pd.DataFrame,
    batting_order: List[str],
    bowling_attack: List[str],
    baselines: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Computes an optimal phase-by-phase bowling allocation (20 overs total, max 4 overs per bowler):
    - Powerplay (Overs 1-6): 6 overs
    - Middle Overs (Overs 7-15): 9 overs
    - Death Overs (Overs 16-20): 5 overs
    """
    if not bowling_attack:
        return {}

    # Calculate profile per bowler
    bowler_profiles = {}
    for b in bowling_attack:
        prof = calculate_bowler_tactical_metrics(df, b, baselines)
        pp_econ = 8.5
        pp_dot = 35.0
        mid_econ = 8.0
        mid_dot = 30.0
        dth_econ = 10.5
        dth_dot = 20.0

        if not prof.empty:
            pp = prof[prof["phase"].str.contains("Powerplay", case=False)]
            if not pp.empty:
                pp_econ = pp.iloc[0]["economy"]
                pp_dot = pp.iloc[0]["dot_pct"]

            mid = prof[prof["phase"].str.contains("Middle", case=False)]
            if not mid.empty:
                mid_econ = mid.iloc[0]["economy"]
                mid_dot = mid.iloc[0]["dot_pct"]

            dth = prof[prof["phase"].str.contains("Death", case=False)]
            if not dth.empty:
                dth_econ = dth.iloc[0]["economy"]
                dth_dot = dth.iloc[0]["dot_pct"]

        b_sub = df[df["bowler"] == b]["bowler_subtype"].iloc[0] if not df[df["bowler"] == b].empty else "Unknown"

        bowler_profiles[b] = {
            "subtype": b_sub,
            "pp_score": pp_dot / (pp_econ + 0.1),
            "mid_score": mid_dot / (mid_econ + 0.1),
            "dth_score": (dth_dot * 1.5) / (dth_econ + 0.1),
            "pp_econ": pp_econ,
            "mid_econ": mid_econ,
            "dth_econ": dth_econ,
        }

    # Allocation containers (target: 6 PP, 9 Middle, 5 Death)
    overs_allocated = {b: 0 for b in bowling_attack}
    plan = {
        "Powerplay (Overs 1-6)": [],
        "Middle (Overs 7-15)": [],
        "Death (Overs 16-20)": [],
    }

    # Step 1: Allocate Death Overs (5 overs) - Death specialists first
    death_ranked = sorted(
        bowling_attack, key=lambda b: bowler_profiles[b]["dth_score"], reverse=True
    )
    dth_needed = 5
    for b in death_ranked:
        alloc = min(2, dth_needed)
        if alloc > 0:
            plan["Death (Overs 16-20)"].append({
                "bowler": b,
                "overs": alloc,
                "role": "Death Execution / Boundary Containment",
                "subtype": bowler_profiles[b]["subtype"],
                "metric": f"Death Econ: {bowler_profiles[b]['dth_econ']:.2f}",
            })
            overs_allocated[b] += alloc
            dth_needed -= alloc
            if dth_needed == 0:
                break

    # Step 2: Allocate Powerplay (6 overs) - New ball swing / seamers / PP containment
    pp_ranked = sorted(
        bowling_attack, key=lambda b: bowler_profiles[b]["pp_score"], reverse=True
    )
    pp_needed = 6
    for b in pp_ranked:
        avail = 4 - overs_allocated[b]
        alloc = min(avail, min(2, pp_needed))
        if alloc > 0:
            plan["Powerplay (Overs 1-6)"].append({
                "bowler": b,
                "overs": alloc,
                "role": "New Ball Attack & Wicket Pressure",
                "subtype": bowler_profiles[b]["subtype"],
                "metric": f"PP Econ: {bowler_profiles[b]['pp_econ']:.2f}",
            })
            overs_allocated[b] += alloc
            pp_needed -= alloc
            if pp_needed == 0:
                break

    # Step 3: Allocate Middle Overs (9 overs) - Spinners & middle enforcers
    mid_ranked = sorted(
        bowling_attack, key=lambda b: bowler_profiles[b]["mid_score"], reverse=True
    )
    mid_needed = 9
    for b in mid_ranked:
        avail = 4 - overs_allocated[b]
        alloc = min(avail, mid_needed)
        if alloc > 0:
            plan["Middle (Overs 7-15)"].append({
                "bowler": b,
                "overs": alloc,
                "role": "Middle Phase Squeeze & Matchup Choke",
                "subtype": bowler_profiles[b]["subtype"],
                "metric": f"Middle Econ: {bowler_profiles[b]['mid_econ']:.2f}",
            })
            overs_allocated[b] += alloc
            mid_needed -= alloc
            if mid_needed == 0:
                break

    # Fill any remaining overs across bowlers with capacity
    total_alloc = sum(overs_allocated.values())
    if total_alloc < 20:
        for b in bowling_attack:
            avail = 4 - overs_allocated[b]
            if avail > 0:
                plan["Middle (Overs 7-15)"].append({
                    "bowler": b,
                    "overs": avail,
                    "role": "Middle Overs Rotation",
                    "subtype": bowler_profiles[b]["subtype"],
                    "metric": f"Middle Econ: {bowler_profiles[b]['mid_econ']:.2f}",
                })
                overs_allocated[b] += avail
                if sum(overs_allocated.values()) == 20:
                    break

    return {
        "plan": plan,
        "overs_by_bowler": overs_allocated,
        "profiles": bowler_profiles,
    }
