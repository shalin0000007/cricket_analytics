# 🏏 IPL Tactical Matchup & Strategy Engine (`cric-analytics`)
### *Next-Gen Cricket Intelligence, Micro-Phase Matchups & Dugout Decision Support*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![OLAP Engine](https://img.shields.io/badge/OLAP-DuckDB-yellow?logo=duckdb)](https://duckdb.org)
[![Data Engine](https://img.shields.io/badge/Storage-Apache%20Parquet-blue?logo=apache)](https://parquet.apache.org)
[![Data Source](https://img.shields.io/badge/Data%20Source-Cricsheet%20v1.3.0-green)](https://cricsheet.org)
[![UI](https://img.shields.io/badge/UI-Streamlit%20%7C%20Plotly-red?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🎯 Executive Overview
Modern T20 and IPL cricket is won in micro-phases and tactical matchups. Traditional aggregate metrics (like career batting average or economy rate) fail to capture situational reality:
- How does a middle-order batter perform against **Left-Arm Orthodox spin (SLA)** specifically during **Overs 7–11**?
- What is a batter's **True Strike Rate (TSR)** in the modern high-scoring era (**2022–2024**) vs their historical career?
- Which bowling change maximizes dot ball pressure and wicket probability based on empirical archetype matchups?
- How do par scores shift across venues (e.g., Wankhede vs. Ekana)?

This repository houses an end-to-end **Cricket Performance & Tactical Analytics Engine** that compiles **295,000+ IPL deliveries (2008–2024)**, queries them in sub-50ms via an embedded **DuckDB OLAP engine**, enriches them with a **16,000+ Player Archetype Registry**, and generates **Dugout Decision Cheat Sheets & Pre-Match Opposition Dossiers**.

---

## 🏗️ Refined Clean Architecture

```
cricket_analytics/
├── data/
│   ├── metadata/              # 16,000+ Player metadata registry (batting hand, bowling style)
│   ├── raw/                   # Cricsheet JSON archive (ipl_json.zip)
│   └── processed/             # ipl_deliveries.parquet (295k+ deliveries, Snappy compressed)
│
├── src/
│   ├── core/                  # Domain Models & Canonical Constants
│   │   ├── constants.py       # Tactical phases, bowling archetypes, era thresholds
│   │   └── models.py          # Typed dataclasses (BatterPhaseStats, MatchupVerdict)
│   │
│   ├── db/                    # Data Layer & Storage
│   │   └── query_engine.py    # Embedded DuckDB engine for zero-copy Parquet querying
│   │
│   ├── engine/                # Tactical Math & Intelligence
│   │   ├── baselines.py       # Contextual & venue-adjusted phase par benchmarks
│   │   ├── true_metrics.py    # True Strike Rate (TSR), True Economy Rate (TER), Pressure Index
│   │   └── matchups.py        # Micro-phase H2H & Bayesian regressed archetype matrix
│   │
│   ├── reports/               # Deliverables & Dossier Generation
│   │   └── dossier_builder.py # 1-Page Pre-Match Scouting Dossier (Markdown/PDF export)
│   │
│   ├── ingest_pipeline.py     # Bulk Cricsheet JSON -> Parquet compiler
│   ├── parser.py              # Single match parser & delivery extractor
│   └── player_registry.py     # Deterministic Cricsheet hash ID mapper
│
└── app.py                     # Streamlit Dugout Decision Dashboard
```

---

## ⚡ Core Tactical Capabilities

### 1. Recency & Era Segmentation (2022–2024 vs All-Time)
Isolates modern T20 tactical doctrine (post-mega auction, 200+ par scores, Impact Player rule) from historical career numbers. 
* Prevents 2009–2014 data from distorting 2025 match decisions.
* Top performers dynamically adapt (e.g., Shubman Gill & Sai Sudharsan top the recent run charts).

### 2. Contextual "True" Metrics Engine
* **True Strike Rate (TSR):** $\text{TSR} = \text{Actual SR} - \text{Phase/Venue Par SR}$. Quantifies acceleration relative to situational par.
* **True Economy Rate (TER):** $\text{TER} = \text{Actual Economy} - \text{Phase Par Economy}$ (Negative is elite).
* **Dot Ball Pressure Rate (`dot_pct`):** Percentage of legal balls yielding 0 runs.
* **Boundary Run Contribution:** Ratio of total runs accumulated through boundaries.

### 3. Bayesian Archetype Shrinkage (Credibility Weighting)
When sample sizes for specific batter-archetype matchups are small (e.g., 6–10 balls), raw stats are noisy. Our engine applies **Bayesian shrinkage regression** towards tournament par:
$$\text{Regressed SR} = \frac{(\text{Balls} \times \text{Raw SR}) + (W \times \text{Par SR})}{\text{Balls} + W}$$
*(where $W = 18$ balls prior weight)*

### 4. Embedded DuckDB OLAP Engine
Queries the 295,732-row database with zero-copy execution in **5–20 milliseconds**, eliminating RAM overhead and enabling instant multi-dimensional slicing.

---

## 🚀 Quickstart & Setup

### 1. Clone & Setup Environment
```bash
git clone https://github.com/shalingonge/cricket-analytics-engine.git
cd cricket-analytics-engine

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Build the Full IPL Parquet Database (One-time)
```bash
python src/ingest_pipeline.py --download
```

### 3. Launch the Interactive Dugout App
```bash
streamlit run app.py
```

### 4. Generate an Opposition Dossier from Terminal
```bash
python -c "from src.db.query_engine import get_query_engine; from src.engine.baselines import compute_contextual_baselines; from src.reports.dossier_builder import build_batter_dossier; engine = get_query_engine(); df = engine.get_deliveries(min_year=2022); baselines = compute_contextual_baselines(df); print(build_batter_dossier(df, 'Shubman Gill', baselines, era_label='Recent 2022-2024'))"
```

---

## 🔬 Sample Output (Opposition Dossier: Shubman Gill [2022–2024])

```markdown
# 🏏 IPL TACTICAL OPPOSITION DOSSIER: SHUBMAN GILL
**Profile:** `RHB` (Opening Batter) | **Filter:** `Recent Era (2022-2024)`
**Sample Size:** 2,084 balls faced | **Runs:** 3,181 | **Overall SR:** 152.6
---
## 1. Micro-Phase Breakdown & True Strike Rate (TSR)
| Phase | Balls | Runs | Outs | Raw SR | True SR (TSR) | Dot % | Boundary % | Balls/Bdry |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Death Overs (16-20) | 177 | 313 | 14 | 176.8 | +16.8 | 18.1% | 22.0% | 4.5 |
| Middle Overs (7-15) | 935 | 1,491 | 27 | 159.5 | +20.4 | 19.3% | 18.4% | 5.4 |
| Powerplay (0-6) | 972 | 1,377 | 27 | 141.7 | -8.5 | 37.8% | 22.0% | 4.5 |

## 2. Bowling Archetype Vulnerability Matrix (Bayesian Regressed)
| Bowling Archetype | Balls | Outs | Avg | Raw SR | Regressed SR | Dot % | Bdry % | Sample Credibility |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Right-arm Pace | 878 | 38 | 35.6 | 154.2 | **154.2** | 32.0% | 22.3% | High |
| Left-arm Pace | 329 | 7 | 63.6 | 135.3 | **136.3** | 25.8% | 17.6% | High |
| Right-arm Legbreak | 302 | 9 | 51.8 | 154.3 | **153.7** | 21.9% | 18.9% | High |
| Left-arm Orthodox | 291 | 4 | 114.8 | 157.7 | **157.3** | 27.8% | 19.9% | High |
| Right-arm Offbreak | 163 | 7 | 38.0 | 163.2 | **160.9** | 22.7% | 20.9% | High |
| Left-arm Wrist Spin | 48 | 1 | 90.0 | 187.5 | **175.6** | 20.8% | 20.8% | High |

## 3. 🎯 Dugout Tactical Directives & Bowling Plan
- **🛡️ Primary Choke Matchup:** Deploy **Left-arm Pace** (Restricts batter to regressed SR 136.3 with 25.8% dot ball pressure).
- **⚠️ Red Alert Matchup:** Avoid feeding **Left-arm Wrist Spin** (Batter accelerates at regressed SR 175.6).
- **Field Setting Directives:** Set deep boundary riders according to scoring quadrants.
```

---

## 👨‍💻 Author
**Shalin Gonge**  
*B.Tech in Computer Science & Engineering (IoT)* — **Vishwakarma Institute of Technology (VIT Pune)**  
- GitHub: [@shalingonge](https://github.com/shalingonge)  
- Focus: Low-Level Systems, High-Performance Query Engines & Tactical Sports Intelligence
