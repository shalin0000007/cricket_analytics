# 🏏 IPL Tactical Matchup & Strategy Engine (`cric-analytics`)
### *Next-Gen Cricket Intelligence, Micro-Phase Matchups & Dugout Decision Support*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Data Engine](https://img.shields.io/badge/Data%20Engine-Pandas%20%7C%20NumPy-orange?logo=pandas)](https://pandas.pydata.org)
[![Data Source](https://img.shields.io/badge/Data%20Source-Cricsheet%20v1.3.0-green)](https://cricsheet.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## 🎯 Executive Overview
Modern T20 and IPL cricket is won in micro-phases. Traditional aggregate metrics (like career batting average or economy rate) fail to capture crucial situational nuance:
- How does a middle-order batter perform against **Left-Arm Orthodox spin** specifically during **Overs 7–11**?
- What is a bowler's **Dot Ball Pressure Rate** when defending fewer than 8 runs/over at the death?
- Which tactical bowling change yields the highest wicket probability based on empirical historical matchups?

This repository houses an end-to-end **Cricket Performance & Tactical Analytics Engine** that ingests ball-by-ball match data (Cricsheet JSON schema v1.3.0) and generates actionable, dugout-ready tactical intelligence.

---

## 🏗️ System Architecture

```
                    CRICSHEET JSON (v1.3.0)
                             │
                             ▼
                ┌─────────────────────────┐
                │     src/parser.py       │  Ball-by-ball ETL Pipeline
                │  - Delivery flattening  │  Over/ball normalizer
                │  - Phase classification │  Extras & wicket categorizer
                └────────────┬────────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │    src/analytics.py     │  Matchup & Tactical Matrix
                │  - Head-to-Head (H2H)   │  Strike rate, Dot %
                │  - Phase breakdown      │  Bowler pressure index
                └────────────┬────────────┘
                             │
                             ▼
                 [Interactive Dugout Cheat-Sheet]
                 Streamlit / Plotly Tactical Radar
```

---

## ⚡ Core Capabilities

### 1. Granular Tactical Phase Segmentation
Categorizes every delivery into modern strategic phases:
- **T20 / IPL:** Powerplay (Overs 0–5) | Middle Overs (Overs 6–14) | Death Overs (Overs 15–19)
- **ODI:** Powerplay 1 (Overs 0–9) | Middle Overs (Overs 10–39) | Death Overs (Overs 40–49)

### 2. Head-to-Head (H2H) Micro-Matchup Engine
Computes real-time situational stats between any batter-bowler pair:
- Balls Faced, Runs Scored, Dismissals, Batting Average
- **Strike Rate** & **Dot Ball Percentage**
- Boundary Frequency (Balls per boundary)

### 3. Bowler Pressure Index & Dot Rate
Calculates true bowling impact beyond standard economy:
- Dot Ball percentage (`dot_pct`)
- Non-boundary runs conceded
- Legal delivery calculation (filtering out wides & no-balls)

---

## 🚀 Quickstart & Setup

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/shalingonge/cricket-analytics-engine.git
cd cricket-analytics-engine

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ingest Ball-by-Ball Data
Drop any match JSON from [cricsheet.org](https://cricsheet.org/) into `data/raw/`:
```bash
python src/parser.py
```

### 3. Run Tactical Matchup Queries
```bash
python src/analytics.py
```

---

## 🔬 Sample Output (Head-to-Head Matchup)
```python
H2H AT Carey vs C Bosch: {
    'batter': 'AT Carey',
    'bowler': 'C Bosch',
    'balls_faced': 12,
    'runs_scored': 9,
    'dismissals': 1,
    'strike_rate': 75.0,
    'dot_percentage': 58.33,
    'fours': 1,
    'sixes': 0,
    'average': 9.0
}
```
*Dugout takeaway: High dot ball pressure (58.3%) and a sub-80 strike rate make Bosch an ideal defensive matchup against Carey in middle overs.*

---

## 🔮 Roadmap: The IoT & Biomechanics Expansion
As a Computer Science & IoT engineer, the next phase bridges data analytics with physical telemetry:
- [ ] **Smart Bat Sensor Telemetry:** Ingesting IMU (MPU-6050 / BNO055) bat-swing acceleration and twist angles over BLE.
- [ ] **Wagon Wheel & Pitch Map Integration:** 3D coordinate mapping for dismissal hotspot clustering.
- [ ] **Monte Carlo Mega-Auction Simulator:** Optimization model for purse allocation and replacement value (WAR).

---

## 👨‍💻 Author
**Shalin Gonge**  
*B.Tech in Computer Science & Engineering (IoT)* — **Vishwakarma Institute of Technology (VIT Pune)**  
- GitHub: [@shalingonge](https://github.com/shalingonge)
- Focus: Low-Level Systems, High-Frequency Data Pipelines & Sports Analytics
