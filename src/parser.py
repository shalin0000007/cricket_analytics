import json
import os
from typing import Dict, List, Any, Optional
import pandas as pd


def get_match_phase(over: int, match_type: str = "T20") -> str:
    """Categorize over into tactical phase for modern analytics."""
    if "T20" in match_type.upper() or "IPL" in match_type.upper():
        if over < 6:
            return "Powerplay (0-6)"
        elif over < 15:
            return "Middle Overs (7-15)"
        else:
            return "Death Overs (16-20)"
    else:  # ODI / 50 overs
        if over < 10:
            return "Powerplay 1 (0-10)"
        elif over < 40:
            return "Middle Overs (11-40)"
        else:
            return "Death Overs (41-50)"


def parse_cricsheet_json(file_path: str) -> pd.DataFrame:
    """
    Parses a single Cricsheet JSON match file (schema v1.3.0) 
    into a flat ball-by-ball deliveries DataFrame.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info", {})
    match_id = os.path.splitext(os.path.basename(file_path))[0]
    match_type = info.get("match_type", "T20")
    venue = info.get("venue", info.get("city", "Unknown"))
    date = info.get("dates", ["Unknown"])[0] if info.get("dates") else "Unknown"
    event_name = info.get("event", {}).get("name", "Unknown")

    deliveries_list: List[Dict[str, Any]] = []

    innings = data.get("innings", [])
    for inn_idx, inn in enumerate(innings, start=1):
        team_name = inn.get("team", f"Team {inn_idx}")
        overs_data = inn.get("overs", [])

        for over_obj in overs_data:
            over_num = over_obj.get("over", 0)
            deliveries = over_obj.get("deliveries", [])

            for ball_idx, delivery in enumerate(deliveries, start=1):
                batter = delivery.get("batter", "")
                bowler = delivery.get("bowler", "")
                non_striker = delivery.get("non_striker", "")

                runs = delivery.get("runs", {})
                batter_runs = runs.get("batter", 0)
                extra_runs = runs.get("extras", 0)
                total_runs = runs.get("total", 0)

                # Extras breakdown
                extras = delivery.get("extras", {})
                wides = extras.get("wides", 0)
                noballs = extras.get("noballs", 0)
                byes = extras.get("byes", 0)
                legbyes = extras.get("legbyes", 0)

                # Wickets breakdown
                wickets = delivery.get("wickets", [])
                is_wicket = 1 if wickets else 0
                wicket_kind = wickets[0].get("kind", "") if wickets else ""
                player_out = wickets[0].get("player_out", "") if wickets else ""

                row = {
                    "match_id": match_id,
                    "event": event_name,
                    "match_type": match_type,
                    "date": date,
                    "venue": venue,
                    "inning": inn_idx,
                    "batting_team": team_name,
                    "over": over_num,
                    "ball": ball_idx,
                    "phase": get_match_phase(over_num, match_type),
                    "batter": batter,
                    "bowler": bowler,
                    "non_striker": non_striker,
                    "batter_runs": batter_runs,
                    "extra_runs": extra_runs,
                    "total_runs": total_runs,
                    "wides": wides,
                    "noballs": noballs,
                    "byes": byes,
                    "legbyes": legbyes,
                    "is_boundary": 1 if batter_runs in (4, 6) else 0,
                    "is_four": 1 if batter_runs == 4 else 0,
                    "is_six": 1 if batter_runs == 6 else 0,
                    "is_dot": 1 if total_runs == 0 else 0,
                    "is_wicket": is_wicket,
                    "wicket_kind": wicket_kind,
                    "player_out": player_out,
                }
                deliveries_list.append(row)

    return pd.DataFrame(deliveries_list)


if __name__ == "__main__":
    sample_file = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "1525657.json")
    if os.path.exists(sample_file):
        df = parse_cricsheet_json(sample_file)
        print(f"Successfully parsed {len(df)} deliveries from {os.path.basename(sample_file)}!")
        print(f"Teams: {df['batting_team'].unique().tolist()}")
        print(f"Sample delivery head:\n", df[["over", "ball", "phase", "batter", "bowler", "batter_runs", "is_wicket"]].head(5))
    else:
        print("Sample file not found at:", sample_file)
