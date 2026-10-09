"""
Tactical Dossier Builder.
Produces 1-Page Pre-Match Scouting Briefs incorporating:
- Recency Era (2022–2024 vs Career)
- Venue-Adjusted True Strike Rate (TSR)
- Bayesian-Regressed Archetype Vulnerabilities
- Dugout Action Directives
"""

from typing import Optional
import pandas as pd

from src.engine.true_metrics import calculate_batter_tactical_metrics
from src.engine.matchups import get_archetype_matrix


def build_batter_dossier(
    df: pd.DataFrame,
    batter: str,
    baselines: Optional[pd.DataFrame] = None,
    era_label: str = "Career (2008–2024)",
    venue: Optional[str] = None,
) -> str:
    """
    Constructs a printable Markdown tactical opposition report for dugout briefings.
    """
    b_df = df[df["batter"] == batter]
    if b_df.empty:
        return f"# Tactical Dossier: {batter}\n\nNo deliveries found for this player in selected dataset slice."

    b_hand = b_df["batter_hand"].iloc[0] if "batter_hand" in b_df.columns else "Unknown"
    role = b_df["batter_role"].iloc[0] if "batter_role" in b_df.columns else "Batter"
    total_runs = int(b_df["batter_runs"].sum())
    total_balls = len(b_df[b_df["wides"] == 0])
    overall_sr = round((total_runs / total_balls * 100), 1) if total_balls > 0 else 0.0

    profile = calculate_batter_tactical_metrics(df, batter, baselines)
    arch_matrix = get_archetype_matrix(df, batter, baselines)

    venue_str = f" | **Venue Focus:** {venue}" if venue and venue != "All Venues" else ""

    lines = [
        f"# 🏏 IPL TACTICAL OPPOSITION DOSSIER: {batter.upper()}",
        f"**Profile:** `{b_hand}` ({role}) | **Filter:** `{era_label}`{venue_str}",
        f"**Sample Size:** {total_balls:,} balls faced | **Runs:** {total_runs:,} | **Overall SR:** {overall_sr}",
        "---",
        "## 1. Micro-Phase Breakdown & True Strike Rate (TSR)",
    ]

    if not profile.empty:
        lines.append("| Phase | Balls | Runs | Outs | Raw SR | True SR (TSR) | Dot % | Boundary % | Balls/Bdry |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        for _, row in profile.iterrows():
            tsr_sign = "+" if row["true_sr"] >= 0 else ""
            lines.append(
                f"| {row['phase']} | {row['balls']:,} | {row['runs']:,} | {row['dismissals']} | "
                f"{row['strike_rate']} | {tsr_sign}{row['true_sr']} | {row['dot_pct']}% | {row['boundary_pct']}% | {row['balls_per_boundary']} |"
            )
    else:
        lines.append("No phase breakdown available in this slice.")

    lines.append("\n## 2. Bowling Archetype Vulnerability Matrix (Bayesian Regressed)")
    if not arch_matrix.empty:
        lines.append("| Bowling Archetype | Balls | Outs | Avg | Raw SR | Regressed SR | Dot % | Bdry % | Sample Credibility |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")
        for _, row in arch_matrix.iterrows():
            lines.append(
                f"| {row['bowling_archetype']} | {row['balls']:,} | {row['dismissals']} | "
                f"{row['average']} | {row['raw_strike_rate']} | **{row['regressed_sr']}** | {row['dot_pct']}% | {row['boundary_pct']}% | {row['sample_credibility']} |"
            )
    else:
        lines.append("No archetype data available.")

    lines.append("\n## 3. 🎯 Dugout Tactical Directives & Bowling Plan")
    if not arch_matrix.empty:
        # Identify choke archetype (lowest regressed SR with at least 15 balls)
        sig = arch_matrix[arch_matrix["balls"] >= 15]
        if not sig.empty:
            containment = sig.sort_values(by="regressed_sr").iloc[0]
            lines.append(
                f"- **🛡️ Primary Choke Matchup:** Deploy **{containment['bowling_archetype']}** "
                f"(Restricts batter to regressed SR {containment['regressed_sr']} with {containment['dot_pct']}% dot ball pressure)."
            )
            danger = sig.sort_values(by="regressed_sr", ascending=False).iloc[0]
            if danger["regressed_sr"] >= 140:
                lines.append(
                    f"- **⚠️ Red Alert Matchup:** Avoid feeding **{danger['bowling_archetype']}** "
                    f"(Batter accelerates at regressed SR {danger['regressed_sr']})."
                )

    if not profile.empty:
        death_row = profile[profile["phase"].str.contains("Death", case=False)]
        if not death_row.empty and death_row.iloc[0]["true_sr"] > 25:
            lines.append(f"- **⚡ Death Phase Threat:** Elite death acceleration (TSR: +{death_row.iloc[0]['true_sr']}). Use wide yorkers or hard into pitch.")

    lines.append("- **Field Setting Directives:** Set deep boundary riders according to scoring quadrants.")

    return "\n".join(lines)
