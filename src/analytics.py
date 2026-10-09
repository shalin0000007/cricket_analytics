import pandas as pd
from typing import Dict, Any, Optional


def get_head_to_head(df: pd.DataFrame, batter: str, bowler: str) -> Dict[str, Any]:
    """
    Computes Head-to-Head (H2H) matchup analytics between a batter and bowler.
    Core metric for IPL tactical matchups and bowling changes.
    """
    matchup = df[(df["batter"] == batter) & (df["bowler"] == bowler)]
    balls_faced = len(matchup[matchup["wides"] == 0])
    runs_scored = matchup["batter_runs"].sum()
    dismissals = len(matchup[(matchup["is_wicket"] == 1) & (matchup["player_out"] == batter)])

    strike_rate = (runs_scored / balls_faced * 100) if balls_faced > 0 else 0.0
    dot_balls = len(matchup[matchup["is_dot"] == 1])
    dot_percentage = (dot_balls / balls_faced * 100) if balls_faced > 0 else 0.0
    fours = matchup["is_four"].sum()
    sixes = matchup["is_six"].sum()

    return {
        "batter": batter,
        "bowler": bowler,
        "balls_faced": balls_faced,
        "runs_scored": runs_scored,
        "dismissals": dismissals,
        "strike_rate": round(strike_rate, 2),
        "dot_percentage": round(dot_percentage, 2),
        "fours": int(fours),
        "sixes": int(sixes),
        "average": round(runs_scored / dismissals, 2) if dismissals > 0 else float("inf"),
    }


def get_batter_phase_stats(df: pd.DataFrame, batter: str) -> pd.DataFrame:
    """Computes strike rate, boundary %, and dot % across tactical phases."""
    b_df = df[df["batter"] == batter]
    if b_df.empty:
        return pd.DataFrame()

    phase_stats = []
    for phase, p_df in b_df.groupby("phase"):
        legal_balls = len(p_df[p_df["wides"] == 0])
        runs = p_df["batter_runs"].sum()
        dots = p_df["is_dot"].sum()
        boundaries = p_df["is_boundary"].sum()
        dismissals = len(p_df[(p_df["is_wicket"] == 1) & (p_df["player_out"] == batter)])

        sr = (runs / legal_balls * 100) if legal_balls > 0 else 0.0
        dot_pct = (dots / legal_balls * 100) if legal_balls > 0 else 0.0
        boundary_pct = (boundaries / legal_balls * 100) if legal_balls > 0 else 0.0

        phase_stats.append({
            "phase": phase,
            "balls": legal_balls,
            "runs": runs,
            "dismissals": dismissals,
            "strike_rate": round(sr, 1),
            "dot_pct": round(dot_pct, 1),
            "boundary_pct": round(boundary_pct, 1),
        })

    return pd.DataFrame(phase_stats)


def get_bowler_economy_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Computes overs, runs conceded, wickets, economy, and dot % for all bowlers."""
    summary = []
    for bowler, b_df in df.groupby("bowler"):
        legal_balls = len(b_df[b_df["wides"] == 0])
        overs = legal_balls // 6 + (legal_balls % 6) / 10
        runs_conceded = b_df["total_runs"].sum() - b_df["byes"].sum() - b_df["legbyes"].sum()
        wickets = len(b_df[(b_df["is_wicket"] == 1) & (~b_df["wicket_kind"].isin(["run out", "retired hurt"]))])
        dots = b_df["is_dot"].sum()

        econ = (runs_conceded / (legal_balls / 6)) if legal_balls > 0 else 0.0
        dot_pct = (dots / legal_balls * 100) if legal_balls > 0 else 0.0

        summary.append({
            "bowler": bowler,
            "overs": overs,
            "balls": legal_balls,
            "runs": runs_conceded,
            "wickets": wickets,
            "economy": round(econ, 2),
            "dot_pct": round(dot_pct, 1),
        })

    return pd.DataFrame(summary).sort_values(by="wickets", ascending=False)


if __name__ == "__main__":
    from parser import parse_cricsheet_json
    import os

    sample_file = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "1525657.json")
    if os.path.exists(sample_file):
        df = parse_cricsheet_json(sample_file)
        print("=== BOWLER SUMMARY ===")
        bowlers = get_bowler_economy_summary(df)
        print(bowlers.head(5))

        print("\n=== SAMPLE MATCHUP: Carey vs Bowler ===")
        top_scorer = df.groupby("batter")["batter_runs"].sum().idxmax()
        top_bowler = bowlers.iloc[0]["bowler"]
        h2h = get_head_to_head(df, top_scorer, top_bowler)
        print(f"H2H {top_scorer} vs {top_bowler}:", h2h)
