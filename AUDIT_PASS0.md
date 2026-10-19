# 🏏 Pass 0 Audit: `cric-analytics` Engine & Data Integrity Report

**Branch:** `feature/dugout-terminal`  
**Dataset Path:** `data/processed/ipl_deliveries.parquet`  
**Date of Audit:** October 19, 2026  
**Auditor:** Lead Broadcast Graphics Designer & Information Architect

---

## 1. Verified Data Assets & Volume

| Asset | Source / File | Verified Count / Dimensions |
| :--- | :--- | :--- |
| **Delivery Store** | `data/processed/ipl_deliveries.parquet` | **295,732 total rows**, **33 columns** (covering 2008–2024 IPL deliveries) |
| **Modern Era Slice (2022–2024)** | Filtered via DuckDB `season_year >= 2022` | **87,690 deliveries** queried in **~227 ms** |
| **Player Image Registry** | `data/metadata/player_images.csv` | 16,000+ player aliases mapped to headshot URLs & team codes |
| **Player Metadata Registry** | `data/metadata/player_meta.csv` | 2.15 MB mapping player IDs to batting hand, bowling arm, and subtypes |
| **Franchise Branding** | `src/core/branding.py` | 10 official IPL franchises with hex tokens (`primary`, `secondary`, `accent`, `short`) |

---

## 2. The 33 Real Columns in `ipl_deliveries.parquet`

Every column has been verified by schema inspection:

| # | Column Name | Type | Description / Canonical Values |
| :---: | :--- | :--- | :--- |
| 1 | `match_id` | `string` | Unique match identifier (Cricsheet ID) |
| 2 | `event` | `string` | Match tournament/event (e.g., `Indian Premier League`) |
| 3 | `match_type` | `string` | Match format (`T20`) |
| 4 | `date` | `string` | Match date (`YYYY-MM-DD`) |
| 5 | `venue` | `string` | Stadium name |
| 6 | `inning` | `int64` | Inning number (`1` or `2`) |
| 7 | `batting_team` | `string` | Franchise batting |
| 8 | `over` | `int64` | 0-indexed over (`0` to `19`) |
| 9 | `ball` | `int64` | Delivery index in over (`1` to `11`) |
| 10 | `phase` | `string` | Canonical phase: `Powerplay (0-6)`, `Middle Overs (7-15)`, `Death Overs (16-20)` |
| 11 | `batter` | `string` | Striker batter name |
| 12 | `bowler` | `string` | Bowler name |
| 13 | `non_striker` | `string` | Non-striker partner name |
| 14 | `batter_runs` | `int64` | Runs off the bat (`0, 1, 2, 3, 4, 6`) |
| 15 | `extra_runs` | `int64` | Extra runs conceded |
| 16 | `total_runs` | `int64` | Total runs from delivery |
| 17 | `wides` | `int64` | Wide ball penalty runs (`0` or `>0`) |
| 18 | `noballs` | `int64` | No-ball penalty runs (`0` or `>0`) |
| 19 | `byes` | `int64` | Byes conceded |
| 20 | `legbyes` | `int64` | Leg byes conceded |
| 21 | `is_boundary` | `int64` | Flag (`1` if 4 or 6, else `0`) |
| 22 | `is_four` | `int64` | Flag (`1` if four, else `0`) |
| 23 | `is_six` | `int64` | Flag (`1` if six, else `0`) |
| 24 | `is_dot` | `int64` | Flag (`1` if total_runs == 0, else `0`) |
| 25 | `is_wicket` | `int64` | Flag (`1` if dismissal occurred, else `0`) |
| 26 | `wicket_kind` | `string` | Dismissal type (`bowled`, `caught`, `lbw`, `stumped`, `run out`, etc.) |
| 27 | `player_out` | `string` | Name of dismissed player |
| 28 | `batter_hand` | `string` | `RHB`, `LHB`, or `Unknown` |
| 29 | `batter_role` | `string` | `Opening Batter`, `Top-order Batter`, `Middle-order Batter`, `Allrounder`, etc. |
| 30 | `bowler_type` | `string` | `Pace`, `Spin`, or `Unknown` |
| 31 | `bowler_subtype` | `string` | `Right-arm Pace`, `Left-arm Pace`, `Right-arm Offbreak`, `Right-arm Legbreak`, `Left-arm Orthodox`, `Left-arm Wrist Spin` |
| 32 | `bowler_arm` | `string` | `Right-arm` or `Left-arm` |
| 33 | `matchup_archetype` | `string` | Composite string, e.g. `RHB vs Right-arm Pace`, `LHB vs Left-arm Orthodox` |

---

## 3. Real Engine Outputs (`src/engine/*`)

The tactical math engines were tested and return the following exact structures:

### A. Contextual Baselines (`src/engine/baselines.py`)
* **Function**: `compute_contextual_baselines(df, venue=None)`
* **Output DataFrame Columns**:
  `['phase', 'bowler_subtype', 'sample_balls', 'par_sr', 'par_econ', 'par_dot_pct', 'par_boundary_pct']`
* **Sample Values**:
  * Death Overs + Left-arm Pace: Par SR = `174.47`, Par Econ = `10.99`, Dot % = `27.41%`, Boundary % = `24.73%`.

### B. True Tactical Metrics (`src/engine/true_metrics.py`)
* **Batter Metrics** (`calculate_batter_tactical_metrics`):
  `['phase', 'balls', 'runs', 'dismissals', 'strike_rate', 'true_sr', 'dot_pct', 'boundary_pct', 'boundary_run_pct', 'balls_per_boundary']`
  * Example (V Kohli Death Overs 2022-24): Balls = 167, Runs = 304, Strike Rate = 182.0, **True SR (TSR) = +22.0**.
* **Bowler Metrics** (`calculate_bowler_tactical_metrics`):
  `['phase', 'overs', 'balls', 'runs', 'wickets', 'economy', 'true_economy', 'dot_pct', 'boundary_pct']`
  * Example (JJ Bumrah Death Overs 2022-24): 65.5 overs, 29 wkts, Economy = 7.25, **True Economy (TER) = -2.78** (elite suppression).

### C. Matchups & Bayesian Shrinkage (`src/engine/matchups.py`)
* **Archetype Matrix** (`get_archetype_matrix`):
  `['bowling_archetype', 'balls', 'runs', 'dismissals', 'average', 'raw_strike_rate', 'regressed_sr', 'dot_pct', 'boundary_pct', 'sample_credibility']`
  * Uses prior weight $W=18$ balls to shrink low-sample matchups towards archetype baseline.
* **Tactical Verdict** (`get_dugout_tactical_verdict`):
  * Keys: `batter`, `batter_hand`, `bowler`, `bowler_subtype`, `direct_balls`, `direct_runs`, `direct_outs`, `direct_sr`, `direct_dot_pct`, `archetype_balls`, `archetype_runs`, `archetype_outs`, `archetype_sr`, `archetype_dot_pct`, `decision_source`, `verdict`, `level` (`bowler_advantage`, `batter_advantage`, or `neutral`), and `advice`.

### D. 8-Axis Percentile Radars (`src/engine/radar.py`)
* **Batter Radar** (8 Dimensions, 0–100 percentile):
  1. `Powerplay Velocity`
  2. `Middle Phase Control`
  3. `Death Finishing Power`
  4. `Boundary Frequency`
  5. `Dot Avoidance`
  6. `Dismissal Resistance`
  7. `Spin Mastery`
  8. `Pace Acceleration`
* **Bowler Radar** (8 Dimensions, 0–100 percentile):
  1. `Powerplay Control`
  2. `Middle Overs Choke`
  3. `Death Yorker Control`
  4. `Dot Ball Mastery`
  5. `Boundary Suppression`
  6. `Wicket Strike Rate`
  7. `Powerplay Dot Pressure`
  8. `Workhorse Volume`

### E. Team Tactics & 20-Over Allocator (`src/engine/team_tactics.py`)
* **Matchup Matrix** (`compute_team_matchup_matrix`):
  * Numerical advantage scores from `-3.0` (Bowler Choke) to `+3.0` (Batter Advantage).
* **20-Over Bowling Plan** (`generate_20_over_bowling_plan`):
  * Keys: `plan` (divided into Powerplay 1-6, Middle 7-15, Death 16-20), `overs_by_bowler` (verifies 4-over maximum quota per bowler), and `profiles`.

### F. Scouting Dossier (`src/reports/dossier_builder.py`)
* **Output**: Formatted 1-Page Pre-Match Markdown scouting dossier containing micro-phase breakdown, Bayesian archetype matrix, and dugout directives.

---

## 4. Data Honesty & Gap Analysis

To maintain 100% data authenticity with no fabricated statistics:

| Blueprint / Concept | Data Reality in Repo | Honest Alternative Implemented |
| :--- | :--- | :--- |
| **Bowling Speed (e.g. "145kph")** | **NOT in dataset**. Cricsheet does not record radar speeds. | **Zero speed numbers displayed**. We classify bowlers strictly by verified `bowler_subtype` (Pace, Spin, Orthodox, Wrist Spin, etc.) and phase economy suppression. |
| **Pitch Coordinates & Length/Line Maps** | **NOT in dataset**. No Hawk-Eye ball coordinates. | **No pitch heatmaps or fabricated length zones**. The Delivery Field is plotted strictly on real data: `X = Over (1-20)` vs `Y = Outcome Lane (Dot, 1, 2, 3, 4, 6, W)`. |
| **Wagon Wheels & 3D Trajectories** | **NOT in dataset**. No shot direction angles or 3D ball coordinates. | **No fake wagon wheels**. We display authentic cricket visuals: the **Historical Ball-by-Ball Encounter Strip** (every real delivery), the **Over-by-Over Manhattan Bar Chart**, and the **Cumulative Worm**. |
| **Field Placements** | **NOT in dataset**. Field coordinates are not logged ball-by-ball. | The Dugout Directives use the engine's verified rule-based tactical directives from `get_dugout_tactical_verdict` and `build_batter_dossier`. |

---

## 5. Baseline Streamlit App Screenshot & Review

The existing Streamlit application was run locally on `http://localhost:8501` and inspected via the headless browser subagent:

* **Screenshot Path**: `streamlit_baseline_dashboard_1792402246449.png`
* **Observations**:
  1. Relies on standard Streamlit layout with vertical column stacks.
  2. Uses generic `plotly_dark` styling with basic circular avatar crops.
  3. Noticeable rerun delay whenever dropdown filters change.
  4. Features are isolated into 8 distinct horizontal tabs without unified dugout telemetry or tactile flow.
