"""
Tactical Matchup Dossier Generator.
Generates an executive, 1-page tactical opposition scouting report
suitable for dugout tactical planning and coaches' pre-match briefings.
"""

from typing import Dict, Any, Optional
import pandas as pd

import sys
import os

# Ensure src package directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from tactical_metrics import (
        compute_phase_baselines,
        get_batter_tactical_profile,
        get_bowler_tactical_profile,
        get_archetype_matchup_matrix,
    )
except ImportError:
    from src.tactical_metrics import (
        compute_phase_baselines,
        get_batter_tactical_profile,
        get_bowler_tactical_profile,
        get_archetype_matchup_matrix,
    )


def generate_batter_tactical_dossier(
    df: pd.DataFrame, batter: str, baselines: Optional[pd.DataFrame] = None
) -> str:
    """
    Produces a high-density, formatted tactical dossier for a batter.
    Includes Phase splits, True Strike Rate, and Bowling Archetype vulnerabilities.
    """
    b_df = df[df["batter"] == batter]
    if b_df.empty:
        return f"# Tactical Dossier: {batter}\n\nNo delivery data available."

    b_hand = b_df["batter_hand"].iloc[0] if "batter_hand" in b_df.columns else "Unknown"
    role = b_df["batter_role"].iloc[0] if "batter_role" in b_df.columns else "Batter"
    total_runs = int(b_df["batter_runs"].sum())
    total_balls = len(b_df[b_df["wides"] == 0])
    overall_sr = round((total_runs / total_balls * 100), 1) if total_balls > 0 else 0.0

    profile = get_batter_tactical_profile(df, batter, baselines)
    arch_matrix = get_archetype_matchup_matrix(df, batter)

    lines = [
        f"# 🏏 TACTICAL OPPOSITION DOSSIER: {batter.upper()}",
        f"**Profile:** {b_hand} | **Role:** {role} | **Total Sample:** {total_balls} balls | **Runs:** {total_runs} (SR: {overall_sr})",
        "---",
        "## 1. Micro-Phase Breakdown & True Strike Rate (TSR)",
    ]

    if not profile.empty:
        lines.append("| Phase | Balls | Runs | Outs | Raw SR | True SR (TSR) | Dot % | Boundary % |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        for _, row in profile.iterrows():
            tsr_sign = "+" if row["true_sr"] >= 0 else ""
            lines.append(
                f"| {row['phase']} | {row['balls']} | {row['runs']} | {row['dismissals']} | "
                f"{row['strike_rate']} | {tsr_sign}{row['true_sr']} | {row['dot_pct']}% | {row['boundary_pct']}% |"
            )
    else:
        lines.append("No phase split available.")

    lines.append("\n## 2. Bowling Archetype Vulnerability Matrix")
    if not arch_matrix.empty:
        lines.append("| Bowling Archetype | Balls | Runs | Outs | Avg | SR | Dot % | Boundary % |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        for _, row in arch_matrix.iterrows():
            lines.append(
                f"| {row['bowling_archetype']} | {row['balls']} | {row['runs']} | {row['dismissals']} | "
                f"{row['average']} | {row['strike_rate']} | {row['dot_pct']}% | {row['boundary_pct']}% |"
            )
    else:
        lines.append("No archetype data available.")

    # Strategic Action Points
    lines.append("\n## 3. 🎯 Dugout Tactical Action Plan")
    if not arch_matrix.empty:
        # Find archetype with highest dot % or lowest SR (min 5 balls)
        sig = arch_matrix[arch_matrix["balls"] >= 5]
        if not sig.empty:
            containment = sig.sort_values(by="strike_rate").iloc[0]
            lines.append(
                f"- **Primary Choke Matchup:** Deploy **{containment['bowling_archetype']}** "
                f"(Restricts batter to SR {containment['strike_rate']} with {containment['dot_pct']}% dots)."
            )
            agg = sig.sort_values(by="strike_rate", ascending=False).iloc[0]
            if agg["strike_rate"] > 140:
                lines.append(
                    f"- **⚠️ Danger Matchup to Avoid:** Avoid feeding **{agg['bowling_archetype']}** "
                    f"(Batter attacks at SR {agg['strike_rate']})."
                )
    lines.append("- **Field Setting Directive:** Emphasize boundary protection in dominant scoring phases.")

    return "\n".join(lines)


if __name__ == "__main__":
    try:
        from parser import parse_cricsheet_json
    except ImportError:
        from src.parser import parse_cricsheet_json

    sample_file = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "1525657.json")
    if os.path.exists(sample_file):
        df = parse_cricsheet_json(sample_file, enrich=True)
        baselines = compute_phase_baselines(df)
        dossier = generate_batter_tactical_dossier(df, "MR Marsh", baselines)
        print(dossier)
