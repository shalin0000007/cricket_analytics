"""
StatsBomb-Style 8-Axis Percentile Radar Engine.
Computes multi-dimensional tactical percentiles (0-100%) for batters and bowlers,
and renders broadcast-grade visual radar charts using Plotly.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

from src.core.constants import PHASE_POWERPLAY, PHASE_MIDDLE, PHASE_DEATH


def calculate_batter_radar_percentiles(
    df: pd.DataFrame, batter: str, min_balls: int = 30
) -> Dict[str, float]:
    """
    Computes 8-axis percentiles (0-100%) for a batter against the tournament distribution:
    1. Powerplay Velocity (PP SR)
    2. Middle Phase Control (Middle SR)
    3. Death Finishing Power (Death SR)
    4. Boundary Frequency (Balls / Boundary)
    5. Dot Ball Avoidance (Low Dot %)
    6. Dismissal Resistance (Balls / Out)
    7. Spin Mastery (SR vs Spin)
    8. Pace Attack Velocity (SR vs Pace)
    """
    if df.empty:
        return {}

    # Aggregate metrics across all qualifying batters
    legal = df[df["wides"] == 0]
    batter_totals = legal.groupby("batter").agg(
        total_balls=("ball", "count"),
        total_runs=("batter_runs", "sum"),
        total_dots=("is_dot", "sum"),
        total_bdry=("is_boundary", "sum"),
        total_outs=("is_wicket", "sum"),
    )
    qualifiers = batter_totals[batter_totals["total_balls"] >= min_balls].index

    if batter not in qualifiers and batter in batter_totals.index:
        # Include batter even if slightly below threshold
        qualifiers = qualifiers.union([batter])

    q_df = df[df["batter"].isin(qualifiers)]

    # Metrics dictionary per batter
    records = {}
    for b_name in qualifiers:
        b_balls = q_df[q_df["batter"] == b_name]
        l_balls = b_balls[b_balls["wides"] == 0]
        n_l = len(l_balls)
        if n_l == 0:
            continue

        runs = l_balls["batter_runs"].sum()
        dots = l_balls["is_dot"].sum()
        bdry = l_balls["is_boundary"].sum()
        outs = len(b_balls[(b_balls["is_wicket"] == 1) & (b_balls["player_out"] == b_name)])

        # Phase metrics
        pp = l_balls[l_balls["phase"].str.contains("Powerplay", case=False)]
        pp_sr = (pp["batter_runs"].sum() / len(pp) * 100) if len(pp) >= 15 else 125.0

        mid = l_balls[l_balls["phase"].str.contains("Middle", case=False)]
        mid_sr = (mid["batter_runs"].sum() / len(mid) * 100) if len(mid) >= 20 else 125.0

        dth = l_balls[l_balls["phase"].str.contains("Death", case=False)]
        dth_sr = (dth["batter_runs"].sum() / len(dth) * 100) if len(dth) >= 15 else 160.0

        # Archetype metrics
        spin = l_balls[l_balls["bowler_type"] == "Spin"]
        spin_sr = (spin["batter_runs"].sum() / len(spin) * 100) if len(spin) >= 20 else 120.0

        pace = l_balls[l_balls["bowler_type"] == "Pace"]
        pace_sr = (pace["batter_runs"].sum() / len(pace) * 100) if len(pace) >= 20 else 135.0

        # General ratios
        dot_pct = (dots / n_l * 100)
        bdry_rate = (n_l / bdry) if bdry > 0 else 25.0  # Lower is better
        balls_per_out = (n_l / outs) if outs > 0 else 60.0  # Higher is better

        records[b_name] = {
            "Powerplay Velocity": pp_sr,
            "Middle Phase Control": mid_sr,
            "Death Finishing Power": dth_sr,
            "Boundary Frequency": -bdry_rate,  # Inverted (more boundaries = higher score)
            "Dot Avoidance": -dot_pct,  # Inverted (fewer dots = higher score)
            "Dismissal Resistance": balls_per_out,
            "Spin Mastery": spin_sr,
            "Pace Acceleration": pace_sr,
        }

    pop_df = pd.DataFrame.from_dict(records, orient="index")
    if batter not in pop_df.index:
        return {}

    # Compute percentiles for target batter
    target_vals = pop_df.loc[batter]
    percentiles = {}
    for col in pop_df.columns:
        pct = stats.percentileofscore(pop_df[col], target_vals[col], kind="rank")
        percentiles[col] = round(float(pct), 1)

    return percentiles


def calculate_bowler_radar_percentiles(
    df: pd.DataFrame, bowler: str, min_balls: int = 30
) -> Dict[str, float]:
    """
    Computes 8-axis percentiles (0-100%) for a bowler against the tournament distribution:
    1. Powerplay Containment (Low PP Econ)
    2. Middle Phase Choke (Low Mid Econ)
    3. Death Yorker Discipline (Low Death Econ)
    4. Dot Ball Mastery (Overall Dot %)
    5. Boundary Suppression (Low Bdry %)
    6. Wicket Taking Strike Rate (Low Balls/Wicket)
    7. Powerplay Dot Pressure (PP Dot %)
    8. Workhorse Volume (Total Balls)
    """
    if df.empty:
        return {}

    legal = df[df["wides"] == 0]
    bowler_totals = legal.groupby("bowler").agg(
        total_balls=("ball", "count"),
        total_wkts=("is_wicket", "sum"),
    )
    qualifiers = bowler_totals[bowler_totals["total_balls"] >= min_balls].index

    if bowler not in qualifiers and bowler in bowler_totals.index:
        qualifiers = qualifiers.union([bowler])

    q_df = df[df["bowler"].isin(qualifiers)]

    records = {}
    for b_name in qualifiers:
        b_balls = q_df[q_df["bowler"] == b_name]
        l_balls = b_balls[b_balls["wides"] == 0]
        n_l = len(l_balls)
        if n_l == 0:
            continue

        runs = (b_balls["total_runs"].sum() - b_balls["byes"].sum() - b_balls["legbyes"].sum())
        wkts = len(b_balls[(b_balls["is_wicket"] == 1) & (~b_balls["wicket_kind"].isin(["run out", "retired hurt"]))])
        dots = l_balls["is_dot"].sum()
        bdry = l_balls["is_boundary"].sum()

        pp = l_balls[l_balls["phase"].str.contains("Powerplay", case=False)]
        pp_runs = pp["total_runs"].sum()
        pp_econ = (pp_runs / (len(pp) / 6.0)) if len(pp) >= 18 else 8.5
        pp_dots = (pp["is_dot"].sum() / len(pp) * 100) if len(pp) >= 18 else 35.0

        mid = l_balls[l_balls["phase"].str.contains("Middle", case=False)]
        mid_runs = mid["total_runs"].sum()
        mid_econ = (mid_runs / (len(mid) / 6.0)) if len(mid) >= 24 else 8.0

        dth = l_balls[l_balls["phase"].str.contains("Death", case=False)]
        dth_runs = dth["total_runs"].sum()
        dth_econ = (dth_runs / (len(dth) / 6.0)) if len(dth) >= 18 else 10.5

        overall_dot_pct = (dots / n_l * 100)
        bdry_pct = (bdry / n_l * 100)
        balls_per_wkt = (n_l / wkts) if wkts > 0 else 40.0

        records[b_name] = {
            "Powerplay Control": -pp_econ,  # Inverted
            "Middle Overs Choke": -mid_econ,  # Inverted
            "Death Yorker Control": -dth_econ,  # Inverted
            "Dot Ball Mastery": overall_dot_pct,
            "Boundary Suppression": -bdry_pct,  # Inverted
            "Wicket Strike Rate": -balls_per_wkt,  # Inverted
            "Powerplay Dot Pressure": pp_dots,
            "Workhorse Volume": n_l,
        }

    pop_df = pd.DataFrame.from_dict(records, orient="index")
    if bowler not in pop_df.index:
        return {}

    target_vals = pop_df.loc[bowler]
    percentiles = {}
    for col in pop_df.columns:
        pct = stats.percentileofscore(pop_df[col], target_vals[col], kind="rank")
        percentiles[col] = round(float(pct), 1)

    return percentiles


def render_statsbomb_radar(
    data1: Dict[str, float],
    name1: str,
    color1: str = "#38bdf8",
    data2: Optional[Dict[str, float]] = None,
    name2: Optional[str] = None,
    color2: str = "#f43f5e",
    title: str = "Tactical Percentile Radar (StatsBomb Style)",
) -> go.Figure:
    """
    Renders a broadcast-grade 8-axis spider radar chart with percentile shading.
    Supports single player or side-by-side player overlay.
    """
    categories = list(data1.keys())
    values1 = list(data1.values())

    # Close the polygon loop
    r1 = values1 + [values1[0]]
    theta = categories + [categories[0]]

    fig = go.Figure()

    # Player 1 Trace
    fig.add_trace(
        go.Scatterpolar(
            r=r1,
            theta=theta,
            fill="toself",
            name=name1,
            line=dict(color=color1, width=3),
            fillcolor=f"rgba({int(color1[1:3], 16)}, {int(color1[3:5], 16)}, {int(color1[5:7], 16)}, 0.35)",
            marker=dict(size=6, color=color1),
        )
    )

    # Optional Player 2 Comparison Trace
    if data2 and name2:
        values2 = [data2.get(cat, 50.0) for cat in categories]
        r2 = values2 + [values2[0]]
        fig.add_trace(
            go.Scatterpolar(
                r=r2,
                theta=theta,
                fill="toself",
                name=name2,
                line=dict(color=color2, width=3, dash="dot"),
                fillcolor=f"rgba({int(color2[1:3], 16)}, {int(color2[3:5], 16)}, {int(color2[5:7], 16)}, 0.30)",
                marker=dict(size=6, color=color2),
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20th", "40th", "60th", "80th", "100th"],
                tickfont=dict(color="#64748b", size=10),
                gridcolor="#1e293b",
                linecolor="#334155",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#e2e8f0", family="sans-serif"),
                gridcolor="#1e293b",
                linecolor="#334155",
            ),
            bgcolor="#0b0f19",
        ),
        paper_bgcolor="#0b0f19",
        font=dict(color="#ffffff"),
        title=dict(
            text=f"<b>{title}</b><br><span style='font-size:12px; color:#94a3b8;'>Percentile rank (0–100%) against all qualified IPL players</span>",
            x=0.05,
            y=0.96,
        ),
        showlegend=True if data2 else False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13),
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        height=480,
    )

    return fig
