import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Ensure src modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db.query_engine import get_query_engine, normalize_venue_name
from src.engine.baselines import compute_contextual_baselines
from src.engine.true_metrics import (
    calculate_batter_tactical_metrics,
    calculate_bowler_tactical_metrics,
)
from src.engine.matchups import get_archetype_matrix, get_dugout_tactical_verdict
from src.engine.team_tactics import (
    compute_team_matchup_matrix,
    generate_20_over_bowling_plan,
)
from src.engine.radar import (
    calculate_batter_radar_percentiles,
    calculate_bowler_radar_percentiles,
    render_statsbomb_radar,
)
from src.core.branding import get_visual_registry, IPL_TEAM_BRANDING
from src.reports.dossier_builder import build_batter_dossier
from src.core.constants import ERA_RECENT_START_YEAR, ERA_ALL_TIME_START_YEAR

st.set_page_config(
    page_title="IPL Dugout Tactical Matchup & Strategy Engine",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Cyberpunk / Dugout War Room Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .stApp {
        background-color: #07090e;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(22, 28, 42, 0.8) 0%, rgba(13, 17, 26, 0.9) 100%);
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 12px;
    }
    
    .plan-card {
        background: rgba(18, 24, 38, 0.85);
        border-radius: 10px;
        padding: 14px 16px;
        border-left: 4px solid #38bdf8;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 10px;
    }
    
    .winner-val {
        color: #10b981;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

engine = get_query_engine()
visual_reg = get_visual_registry()

if not engine.is_ready():
    st.error("Parquet database not found. Please run `python src/ingest_pipeline.py --download` first.")
    st.stop()

# Header
st.title("🏏 IPL Tactical Matchup & Dugout Decision Engine")
st.caption("Next-Gen Cricket Intelligence | 1-to-1 Matchup Duels & Player Comparisons | StatsBomb Radars | DuckDB OLAP Engine")
st.divider()

# Sidebar: Tactical Selection & Filters
st.sidebar.header("⚙️ Tactical Filters & Era")

era_choice = st.sidebar.radio(
    "Recency Window",
    ["Recent Form (2022–2024)", "Career All-Time (2008–2024)"],
    index=0,
    help="Recent form isolates modern high-scoring par scores post-2022 mega-auction.",
)
min_year = ERA_RECENT_START_YEAR if "Recent" in era_choice else ERA_ALL_TIME_START_YEAR

# Venue Selection
venue_options = [
    "All Venues",
    "Wankhede Stadium",
    "M Chinnaswamy Stadium",
    "Eden Gardens",
    "Chepauk",
    "Narendra Modi Stadium",
    "Ekana Stadium",
    "Arun Jaitley Stadium",
    "Rajiv Gandhi Stadium",
]
selected_venue = st.sidebar.selectbox("Venue Context", venue_options, index=0)

# Fetch ALL available players in selected era without artificial limits!
all_batters = engine.get_top_batters(min_year=min_year)
all_bowlers = engine.get_top_bowlers(min_year=min_year)

st.sidebar.subheader("🎯 Primary Matchup Selectors")

# Intuitive defaults
default_b_idx = all_batters.index("V Kohli") if "V Kohli" in all_batters else 0
default_bw_idx = all_bowlers.index("JJ Bumrah") if "JJ Bumrah" in all_bowlers else 0

selected_batter = st.sidebar.selectbox(
    f"Select Batter ({len(all_batters)} players available)",
    all_batters,
    index=default_b_idx,
)
selected_bowler = st.sidebar.selectbox(
    f"Select Bowler ({len(all_bowlers)} players available)",
    all_bowlers,
    index=default_bw_idx,
)

# Load Filtered Dataset via DuckDB
@st.cache_data
def get_cached_slice(min_y: int, venue: str):
    return engine.get_deliveries(min_year=min_y, venue=venue if venue != "All Venues" else None)

slice_df = get_cached_slice(min_year, selected_venue)
baselines = compute_contextual_baselines(slice_df, venue=selected_venue)

# Metadata Display in Sidebar with Headshots
b_meta = slice_df[slice_df["batter"] == selected_batter]
b_hand = b_meta["batter_hand"].iloc[0] if not b_meta.empty and "batter_hand" in b_meta.columns else "Unknown"
b_role = b_meta["batter_role"].iloc[0] if not b_meta.empty and "batter_role" in b_meta.columns else "Batter"
batter_img = visual_reg.get_player_image(selected_batter)

bw_meta = slice_df[slice_df["bowler"] == selected_bowler]
bowler_style = bw_meta["bowler_subtype"].iloc[0] if not bw_meta.empty and "bowler_subtype" in bw_meta.columns else "Unknown"
bowler_img = visual_reg.get_player_image(selected_bowler)

# Sidebar Player Cards with Avatars
st.sidebar.markdown(f"""
<div style='background:#111622; padding:12px; border-radius:10px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.08);'>
    <div style='display:flex; align-items:center; gap:12px;'>
        <img src='{batter_img}' style='width:46px; height:46px; border-radius:50%; border:2px solid #38bdf8; object-fit:cover;' />
        <div>
            <b>{selected_batter}</b><br>
            <small style='color:#38bdf8;'>{b_hand} | {b_role}</small>
        </div>
    </div>
</div>
<div style='background:#111622; padding:12px; border-radius:10px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.08);'>
    <div style='display:flex; align-items:center; gap:12px;'>
        <img src='{bowler_img}' style='width:46px; height:46px; border-radius:50%; border:2px solid #f43f5e; object-fit:cover;' />
        <div>
            <b>{selected_bowler}</b><br>
            <small style='color:#f43f5e;'>{bowler_style}</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# IPL Team Presets for Probable XI
IPL_TEAMS_PRESETS = {
    "Chennai Super Kings": {
        "batters": ["RD Gaikwad", "S Dube", "AM Rahane", "RA Jadeja", "MS Dhoni", "MM Ali"],
        "bowlers": ["Mustafizur Rahman", "RA Jadeja", "M Pathirana", "TU Deshpande", "DL Chahar"],
    },
    "Mumbai Indians": {
        "batters": ["RG Sharma", "Ishan Kishan", "SA Yadav", "Tilak Varma", "HH Pandya", "TH David"],
        "bowlers": ["JJ Bumrah", "P Chawla", "G Coetzee", "N Thushara", "HH Pandya"],
    },
    "Kolkata Knight Riders": {
        "batters": ["PD Salt", "Sunil Narine", "VR Iyer", "SS Iyer", "RK Singh", "AD Russell"],
        "bowlers": ["MA Starc", "CV Varun", "Sunil Narine", "Harshit Rana", "AD Russell"],
    },
    "Royal Challengers Bengaluru": {
        "batters": ["V Kohli", "F du Plessis", "RM Patidar", "GJ Maxwell", "C Green", "KD Karthik"],
        "bowlers": ["Mohammed Siraj", "LH Ferguson", "Yash Dayal", "KV Sharma", "C Green"],
    },
    "Rajasthan Royals": {
        "batters": ["YBK Jaiswal", "JC Buttler", "SV Samson", "R Parag", "SO Hetmyer", "Dhruv Jurel"],
        "bowlers": ["TA Boult", "Avesh Khan", "YS Chahal", "R Ashwin", "Sandeep Sharma"],
    },
    "Sunrisers Hyderabad": {
        "batters": ["TM Head", "Abhishek Sharma", "RA Tripathi", "AK Markram", "H Klaasen", "NK Reddy"],
        "bowlers": ["PJ Cummins", "B Kumar", "T Natarajan", "M Markande", "JD Unadkat"],
    },
    "Gujarat Titans": {
        "batters": ["Shubman Gill", "WP Saha", "B Sai Sudharsan", "DA Miller", "R Tewatia", "Rashid Khan"],
        "bowlers": ["Rashid Khan", "MM Sharma", "Noor Ahmad", "Umesh Yadav", "SH Johnson"],
    },
    "Delhi Capitals": {
        "batters": ["DA Warner", "PP Shaw", "MR Marsh", "RR Pant", "T Stubbs", "AR Patel"],
        "bowlers": ["A Nortje", "KK Ahmed", "AR Patel", "Kuldeep Yadav", "Mukesh Kumar"],
    },
    "Lucknow Super Giants": {
        "batters": ["KL Rahul", "Q de Kock", "D Padikkal", "N Pooran", "MP Stoinis", "Ayush Badoni"],
        "bowlers": ["Naveen-ul-Haq", "Mayank Yadav", "Ravi Bishnoi", "KH Pandya", "Mohsin Khan"],
    },
    "Punjab Kings": {
        "batters": ["S Dhawan", "JM Bairstow", "PR Prabhsimran Singh", "SM Curran", "JM Sharma", "Shashank Singh"],
        "bowlers": ["K Rabada", "Arshdeep Singh", "SM Curran", "HV Patel", "RD Chahar"],
    },
}

# Main Dashboard Tabs - Organised with 1-to-1 Comparisons Front and Center!
tab_h2h, tab_compare, tab_radar, tab_squad, tab_phase, tab_bowler, tab_venue, tab_dossier = st.tabs([
    "⚔️ 1-to-1 Batter vs Bowler Duel",
    "🥊 1-to-1 Player Comparison (Tale of the Tape)",
    "🕸️ StatsBomb Tactical Radars",
    "📋 Probable XI Squad Heatmap & 20-Over Plan",
    "📊 Batter Phase Dynamics & TSR",
    "🎯 Bowler Control & Pressure (TER)",
    "🏟️ Venue Par Benchmarks",
    "📑 Tactical Opposition Dossier",
])

# ----------------- TAB 1: 1-TO-1 BATTER VS BOWLER DUEL -----------------
with tab_h2h:
    st.subheader(f"⚔️ 1-to-1 Direct Duel: {selected_batter} vs {selected_bowler}")

    # Player Hero Banner with Headshots
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(30,41,59,0.7) 0%, rgba(15,23,42,0.9) 100%); padding: 18px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); margin-bottom: 20px;'>
        <div style='display:flex; justify-content:space-around; align-items:center;'>
            <div style='display:flex; align-items:center; gap:16px;'>
                <img src='{batter_img}' style='width:76px; height:76px; border-radius:50%; border:3px solid #38bdf8; box-shadow:0 0 15px rgba(56,189,248,0.4); object-fit:cover;' />
                <div>
                    <h2 style='margin:0; font-size:24px;'>{selected_batter}</h2>
                    <span style='color:#38bdf8; font-weight:600;'>{b_hand}</span> • <span style='color:#94a3b8;'>{b_role}</span>
                </div>
            </div>
            <div style='font-size:28px; font-weight:800; color:#e2e8f0;'>VS</div>
            <div style='display:flex; align-items:center; gap:16px;'>
                <div>
                    <h2 style='margin:0; font-size:24px; text-align:right;'>{selected_bowler}</h2>
                    <span style='color:#f43f5e; font-weight:600;'>{bowler_style}</span>
                </div>
                <img src='{bowler_img}' style='width:76px; height:76px; border-radius:50%; border:3px solid #f43f5e; box-shadow:0 0 15px rgba(244,63,94,0.4); object-fit:cover;' />
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    verdict_info = get_dugout_tactical_verdict(slice_df, selected_batter, selected_bowler, baselines)

    # Tactical Verdict Banner
    if verdict_info["level"] == "bowler_advantage":
        st.error(f"🛡️ **TACTICAL VERDICT: {verdict_info['verdict']}**\n\n{verdict_info['advice']}")
    elif verdict_info["level"] == "batter_advantage":
        st.warning(f"🔥 **TACTICAL VERDICT: {verdict_info['verdict']}**\n\n{verdict_info['advice']}")
    else:
        st.info(f"⚖️ **TACTICAL VERDICT: {verdict_info['verdict']}**\n\n{verdict_info['advice']}")

    st.caption(f"**Decision Basis:** `{verdict_info['decision_source']}` | **Era:** `{era_choice}`")

    # Direct H2H Metrics
    st.markdown("### 1. Direct Head-to-Head Duel")
    if verdict_info["direct_balls"] == 0:
        st.info(f"💡 No direct deliveries recorded between **{selected_batter}** and **{selected_bowler}** in this slice. Archetype matchup used below.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Balls Faced", verdict_info["direct_balls"])
        c2.metric("Runs Scored", verdict_info["direct_runs"])
        c3.metric("Strike Rate", f"{verdict_info['direct_sr']}")
        c4.metric("Dot Ball %", f"{verdict_info['direct_dot_pct']}%")
        c5.metric("Dismissals", verdict_info["direct_outs"])

        # Phase breakdown of direct H2H
        direct_balls_df = slice_df[(slice_df["batter"] == selected_batter) & (slice_df["bowler"] == selected_bowler)]
        if not direct_balls_df.empty:
            st.markdown("#### Phase-by-Phase Direct Battles")
            direct_phase_rows = []
            for p_name, p_sub in direct_balls_df.groupby("phase"):
                l_b = len(p_sub[p_sub["wides"] == 0])
                r = int(p_sub["batter_runs"].sum())
                outs = len(p_sub[(p_sub["is_wicket"] == 1) & (p_sub["player_out"] == selected_batter)])
                dots = int(p_sub["is_dot"].sum())
                sr = round(r / l_b * 100, 1) if l_b > 0 else 0.0
                dot_pct = round(dots / l_b * 100, 1) if l_b > 0 else 0.0
                direct_phase_rows.append({
                    "Phase": p_name,
                    "Balls": l_b,
                    "Runs": r,
                    "Dismissals": outs,
                    "Strike Rate": sr,
                    "Dot %": f"{dot_pct}%",
                })
            if direct_phase_rows:
                st.dataframe(pd.DataFrame(direct_phase_rows), use_container_width=True)

    # Archetype Matchup
    st.markdown(f"### 2. Archetype Context: {selected_batter} vs {bowler_style}")
    if verdict_info["archetype_balls"] > 0:
        ca1, ca2, ca3, ca4, ca5 = st.columns(5)
        ca1.metric("Archetype Balls", verdict_info["archetype_balls"])
        ca2.metric("Archetype Runs", verdict_info["archetype_runs"])
        ca3.metric("Archetype SR", f"{verdict_info['archetype_sr']}")
        ca4.metric("Archetype Dot %", f"{verdict_info['archetype_dot_pct']}%")
        ca5.metric("Dismissals vs Archetype", verdict_info["archetype_outs"])
    else:
        st.write(f"No balls faced by {selected_batter} against {bowler_style} in this dataset.")

# ----------------- TAB 2: 1-TO-1 PLAYER COMPARISON (TALE OF THE TAPE) -----------------
with tab_compare:
    st.subheader("🥊 1-to-1 Player Comparison (Tale of the Tape)")
    st.caption("Side-by-side tactical breakdown and overlaid 8-axis StatsBomb radar between any two IPL players.")

    comp_category = st.radio("Comparison Category", ["Batter vs Batter", "Bowler vs Bowler"], horizontal=True)

    if comp_category == "Batter vs Batter":
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            p1 = st.selectbox(
                "Select Batter 1",
                all_batters,
                index=all_batters.index("V Kohli") if "V Kohli" in all_batters else 0,
                key="b_comp_1",
            )
        with c_col2:
            default_p2 = all_batters.index("RG Sharma") if "RG Sharma" in all_batters else 1
            p2 = st.selectbox(
                "Select Batter 2",
                all_batters,
                index=default_p2,
                key="b_comp_2",
            )

        p1_img = visual_reg.get_player_image(p1)
        p2_img = visual_reg.get_player_image(p2)
        p1_meta = slice_df[slice_df["batter"] == p1]
        p2_meta = slice_df[slice_df["batter"] == p2]
        p1_hand = p1_meta["batter_hand"].iloc[0] if not p1_meta.empty and "batter_hand" in p1_meta.columns else "Unknown"
        p2_hand = p2_meta["batter_hand"].iloc[0] if not p2_meta.empty and "batter_hand" in p2_meta.columns else "Unknown"

        # Side-by-side hero header
        st.markdown(f"""
        <div style='background:#111622; padding:16px; border-radius:12px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.08);'>
            <div style='display:flex; justify-content:space-around; align-items:center;'>
                <div style='display:flex; align-items:center; gap:14px;'>
                    <img src='{p1_img}' style='width:64px; height:64px; border-radius:50%; border:3px solid #38bdf8; object-fit:cover;' />
                    <div>
                        <h3 style='margin:0;'>{p1}</h3>
                        <span style='color:#38bdf8;'>{p1_hand}</span>
                    </div>
                </div>
                <div style='font-size:24px; font-weight:800; color:#e2e8f0;'>VS</div>
                <div style='display:flex; align-items:center; gap:14px;'>
                    <div>
                        <h3 style='margin:0; text-align:right;'>{p2}</h3>
                        <span style='color:#f43f5e;'>{p2_hand}</span>
                    </div>
                    <img src='{p2_img}' style='width:64px; height:64px; border-radius:50%; border:3px solid #f43f5e; object-fit:cover;' />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Calculate metrics for both
        p1_l = slice_df[(slice_df["batter"] == p1) & (slice_df["wides"] == 0)]
        p2_l = slice_df[(slice_df["batter"] == p2) & (slice_df["wides"] == 0)]

        p1_runs = int(p1_l["batter_runs"].sum()) if not p1_l.empty else 0
        p2_runs = int(p2_l["batter_runs"].sum()) if not p2_l.empty else 0

        p1_balls = len(p1_l)
        p2_balls = len(p2_l)

        p1_sr = round(p1_runs / p1_balls * 100, 1) if p1_balls > 0 else 0.0
        p2_sr = round(p2_runs / p2_balls * 100, 1) if p2_balls > 0 else 0.0

        p1_dots = round(p1_l["is_dot"].sum() / p1_balls * 100, 1) if p1_balls > 0 else 0.0
        p2_dots = round(p2_l["is_dot"].sum() / p2_balls * 100, 1) if p2_balls > 0 else 0.0

        p1_bdry = round(p1_l["is_boundary"].sum() / p1_balls * 100, 1) if p1_balls > 0 else 0.0
        p2_bdry = round(p2_l["is_boundary"].sum() / p2_balls * 100, 1) if p2_balls > 0 else 0.0

        # Tale of the Tape Grid
        st.markdown("### 📊 Tale of the Tape")
        t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns(5)
        t_col1.metric("Total Runs", f"{p1_runs:,}", delta=f"{p1_runs - p2_runs:+,} vs {p2}")
        t_col2.metric("Balls Faced", f"{p1_balls:,}", delta=f"{p1_balls - p2_balls:+,} vs {p2}")
        t_col3.metric("Strike Rate", f"{p1_sr}", delta=f"{p1_sr - p2_sr:+.1f} vs {p2}")
        t_col4.metric("Dot Ball % (Lower is better)", f"{p1_dots}%", delta=f"{p2_dots - p1_dots:+.1f}% adv" if p1_dots < p2_dots else f"{p1_dots - p2_dots:+.1f}% risk")
        t_col5.metric("Boundary %", f"{p1_bdry}%", delta=f"{p1_bdry - p2_bdry:+.1f}% vs {p2}")

        # Overlaid StatsBomb Radar
        st.markdown("### 🕸️ Overlaid 8-Axis Percentile Radar")
        b_r1 = calculate_batter_radar_percentiles(slice_df, p1)
        b_r2 = calculate_batter_radar_percentiles(slice_df, p2)

        if b_r1 and b_r2:
            fig_comp_radar = render_statsbomb_radar(
                b_r1,
                name1=p1,
                color1="#38bdf8",
                data2=b_r2,
                name2=p2,
                color2="#f43f5e",
                title=f"{p1} (Cyan) vs {p2} (Coral) - Tactical Radar",
            )
            st.plotly_chart(fig_comp_radar, use_container_width=True)

    else:  # Bowler vs Bowler
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            bw1 = st.selectbox(
                "Select Bowler 1",
                all_bowlers,
                index=all_bowlers.index("JJ Bumrah") if "JJ Bumrah" in all_bowlers else 0,
                key="bw_comp_1",
            )
        with c_col2:
            default_bw2 = all_bowlers.index("Rashid Khan") if "Rashid Khan" in all_bowlers else (1 if len(all_bowlers) > 1 else 0)
            bw2 = st.selectbox(
                "Select Bowler 2",
                all_bowlers,
                index=default_bw2,
                key="bw_comp_2",
            )

        bw1_img = visual_reg.get_player_image(bw1)
        bw2_img = visual_reg.get_player_image(bw2)
        bw1_meta = slice_df[slice_df["bowler"] == bw1]
        bw2_meta = slice_df[slice_df["bowler"] == bw2]
        bw1_style = bw1_meta["bowler_subtype"].iloc[0] if not bw1_meta.empty and "bowler_subtype" in bw1_meta.columns else "Unknown"
        bw2_style = bw2_meta["bowler_subtype"].iloc[0] if not bw2_meta.empty and "bowler_subtype" in bw2_meta.columns else "Unknown"

        st.markdown(f"""
        <div style='background:#111622; padding:16px; border-radius:12px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.08);'>
            <div style='display:flex; justify-content:space-around; align-items:center;'>
                <div style='display:flex; align-items:center; gap:14px;'>
                    <img src='{bw1_img}' style='width:64px; height:64px; border-radius:50%; border:3px solid #10b981; object-fit:cover;' />
                    <div>
                        <h3 style='margin:0;'>{bw1}</h3>
                        <span style='color:#10b981;'>{bw1_style}</span>
                    </div>
                </div>
                <div style='font-size:24px; font-weight:800; color:#e2e8f0;'>VS</div>
                <div style='display:flex; align-items:center; gap:14px;'>
                    <div>
                        <h3 style='margin:0; text-align:right;'>{bw2}</h3>
                        <span style='color:#fbbf24;'>{bw2_style}</span>
                    </div>
                    <img src='{bw2_img}' style='width:64px; height:64px; border-radius:50%; border:3px solid #fbbf24; object-fit:cover;' />
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bw1_l = slice_df[(slice_df["bowler"] == bw1) & (slice_df["wides"] == 0)]
        bw2_l = slice_df[(slice_df["bowler"] == bw2) & (slice_df["wides"] == 0)]

        bw1_balls = len(bw1_l)
        bw2_balls = len(bw2_l)

        bw1_b = slice_df[slice_df["bowler"] == bw1]
        bw2_b = slice_df[slice_df["bowler"] == bw2]

        bw1_runs = int(bw1_b["total_runs"].sum() - bw1_b["byes"].sum() - bw1_b["legbyes"].sum()) if not bw1_b.empty else 0
        bw2_runs = int(bw2_b["total_runs"].sum() - bw2_b["byes"].sum() - bw2_b["legbyes"].sum()) if not bw2_b.empty else 0

        bw1_wkts = len(bw1_b[(bw1_b["is_wicket"] == 1) & (~bw1_b["wicket_kind"].isin(["run out", "retired hurt"]))]) if not bw1_b.empty else 0
        bw2_wkts = len(bw2_b[(bw2_b["is_wicket"] == 1) & (~bw2_b["wicket_kind"].isin(["run out", "retired hurt"]))]) if not bw2_b.empty else 0

        bw1_econ = round(bw1_runs / (bw1_balls / 6.0), 2) if bw1_balls > 0 else 0.0
        bw2_econ = round(bw2_runs / (bw2_balls / 6.0), 2) if bw2_balls > 0 else 0.0

        bw1_dots = round(bw1_l["is_dot"].sum() / bw1_balls * 100, 1) if bw1_balls > 0 else 0.0
        bw2_dots = round(bw2_l["is_dot"].sum() / bw2_balls * 100, 1) if bw2_balls > 0 else 0.0

        st.markdown("### 📊 Tale of the Tape")
        tb_col1, tb_col2, tb_col3, tb_col4 = st.columns(4)
        tb_col1.metric("Wickets", f"{bw1_wkts}", delta=f"{bw1_wkts - bw2_wkts:+} vs {bw2}")
        tb_col2.metric("Overs Bowled", f"{bw1_balls // 6}.{bw1_balls % 6}", delta=f"{bw1_balls - bw2_balls:+} balls vs {bw2}")
        tb_col3.metric("Economy Rate (Lower is better)", f"{bw1_econ}", delta=f"{bw2_econ - bw1_econ:+.2f} econ adv" if bw1_econ < bw2_econ else f"{bw1_econ - bw2_econ:+.2f} higher")
        tb_col4.metric("Dot Ball %", f"{bw1_dots}%", delta=f"{bw1_dots - bw2_dots:+.1f}% vs {bw2}")

        st.markdown("### 🕸️ Overlaid 8-Axis Percentile Radar")
        bw_r1 = calculate_bowler_radar_percentiles(slice_df, bw1)
        bw_r2 = calculate_bowler_radar_percentiles(slice_df, bw2)

        if bw_r1 and bw_r2:
            fig_bw_radar_comp = render_statsbomb_radar(
                bw_r1,
                name1=bw1,
                color1="#10b981",
                data2=bw_r2,
                name2=bw2,
                color2="#fbbf24",
                title=f"{bw1} (Emerald) vs {bw2} (Gold) - Tactical Radar",
            )
            st.plotly_chart(fig_bw_radar_comp, use_container_width=True)

# ----------------- TAB 3: STATSBOMB PERCENTILE RADARS -----------------
with tab_radar:
    st.subheader("🕸️ 8-Axis Tactical Percentile Radars")
    st.caption("Percentile rank (0–100%) against all qualified tournament players. Shaded area represents tactical dominance.")

    r_col1, r_col2 = st.columns([1, 1])

    with r_col1:
        st.markdown(f"#### 🏏 Batter Radar: {selected_batter}")
        compare_batter = st.selectbox(
            "Overlay Comparison Batter (Optional)",
            ["None"] + [b for b in all_batters if b != selected_batter],
            index=0,
            key="comp_b_single",
        )
        b_radar1 = calculate_batter_radar_percentiles(slice_df, selected_batter)

        if b_radar1:
            b_radar2 = None
            if compare_batter != "None":
                b_radar2 = calculate_batter_radar_percentiles(slice_df, compare_batter)

            fig_b_radar = render_statsbomb_radar(
                b_radar1,
                name1=selected_batter,
                color1="#38bdf8",
                data2=b_radar2,
                name2=compare_batter if compare_batter != "None" else None,
                color2="#f43f5e",
                title=f"{selected_batter} Tactical Profile",
            )
            st.plotly_chart(fig_b_radar, use_container_width=True)
        else:
            st.info(f"Insufficient balls faced by {selected_batter} in this slice.")

    with r_col2:
        st.markdown(f"#### 🎯 Bowler Radar: {selected_bowler}")
        compare_bowler = st.selectbox(
            "Overlay Comparison Bowler (Optional)",
            ["None"] + [b for b in all_bowlers if b != selected_bowler],
            index=0,
            key="comp_bw_single",
        )
        bw_radar1 = calculate_bowler_radar_percentiles(slice_df, selected_bowler)

        if bw_radar1:
            bw_radar2 = None
            if compare_bowler != "None":
                bw_radar2 = calculate_bowler_radar_percentiles(slice_df, compare_bowler)

            fig_bw_radar = render_statsbomb_radar(
                bw_radar1,
                name1=selected_bowler,
                color1="#10b981",
                data2=bw_radar2,
                name2=compare_bowler if compare_bowler != "None" else None,
                color2="#fbbf24",
                title=f"{selected_bowler} Tactical Profile",
            )
            st.plotly_chart(fig_bw_radar, use_container_width=True)
        else:
            st.info(f"Insufficient balls bowled by {selected_bowler} in this slice.")

# ----------------- TAB 4: PROBABLE XI & BOWLING PLAN -----------------
with tab_squad:
    st.subheader("📋 Pre-Match Squad Tactical Heatmap & 20-Over Allocation Plan")
    st.caption("Used by IPL coaches to identify matchup chokes and pre-plan bowler overs against opposition batting orders.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        opp_team = st.selectbox("Select Opposition Batting Team", list(IPL_TEAMS_PRESETS.keys()), index=0)
        default_batters = IPL_TEAMS_PRESETS[opp_team]["batters"]
        active_batters = st.multiselect(
            "Opposition Batting Lineup (Edit order / players)",
            options=all_batters,
            default=[b for b in default_batters if b in all_batters],
        )

    with col_t2:
        our_team = st.selectbox("Select Our Bowling Attack Team", list(IPL_TEAMS_PRESETS.keys()), index=1)
        default_bowlers = IPL_TEAMS_PRESETS[our_team]["bowlers"]
        active_bowlers = st.multiselect(
            "Our Bowling Attack (Select 5–6 bowlers)",
            options=all_bowlers,
            default=[b for b in default_bowlers if b in all_bowlers],
        )

    if not active_batters or not active_bowlers:
        st.warning("Please select at least 1 batter and 1 bowler to generate squad matrix.")
    else:
        adv_matrix, det_matrix = compute_team_matchup_matrix(slice_df, active_batters, active_bowlers, baselines)

        st.markdown("### 1. Tactical Matchup Heatmap Matrix")
        st.caption("🔴 Red = High Dismissal Risk / Bowler Choke | 🔵 Blue/Green = Batter Attack Hazard | ⚪ White = Par")

        fig_heat = px.imshow(
            adv_matrix,
            labels=dict(x="Bowler", y="Batter", color="Advantage Score"),
            x=active_bowlers,
            y=active_batters,
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=0.0,
            text_auto=True,
            aspect="auto",
            template="plotly_dark",
            title=f"Matchup Heatmap: {opp_team} Batters vs {our_team} Attack",
        )
        fig_heat.update_layout(height=420)
        st.plotly_chart(fig_heat, use_container_width=True)

        # 20-Over Bowling Plan
        st.markdown("### 2. Automated 20-Over Bowling Plan Allocation")
        bowling_plan = generate_20_over_bowling_plan(slice_df, active_batters, active_bowlers, baselines)

        if bowling_plan and "plan" in bowling_plan:
            cp1, cp2, cp3 = st.columns(3)
            with cp1:
                st.markdown("#### ⚡ Powerplay (Overs 1–6)")
                st.caption("New ball swing & early wicket pressure")
                for entry in bowling_plan["plan"].get("Powerplay (Overs 1-6)", []):
                    st.markdown(
                        f"""<div class='plan-card'>
                        <b>{entry['bowler']}</b>: {entry['overs']} Over(s)<br>
                        <small style='color: #38bdf8;'>{entry['subtype']}</small><br>
                        <small style='color: #94a3b8;'>{entry['role']}</small><br>
                        <b>{entry['metric']}</b>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            with cp2:
                st.markdown("#### 🌀 Middle Overs (Overs 7–15)")
                st.caption("Spin choke & matchup restrictions")
                for entry in bowling_plan["plan"].get("Middle (Overs 7-15)", []):
                    st.markdown(
                        f"""<div class='plan-card'>
                        <b>{entry['bowler']}</b>: {entry['overs']} Over(s)<br>
                        <small style='color: #38bdf8;'>{entry['subtype']}</small><br>
                        <small style='color: #94a3b8;'>{entry['role']}</small><br>
                        <b>{entry['metric']}</b>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            with cp3:
                st.markdown("#### 🎯 Death Overs (Overs 16–20)")
                st.caption("Yorkers & boundary suppression")
                for entry in bowling_plan["plan"].get("Death (Overs 16-20)", []):
                    st.markdown(
                        f"""<div class='plan-card'>
                        <b>{entry['bowler']}</b>: {entry['overs']} Over(s)<br>
                        <small style='color: #38bdf8;'>{entry['subtype']}</small><br>
                        <small style='color: #94a3b8;'>{entry['role']}</small><br>
                        <b>{entry['metric']}</b>
                        </div>""",
                        unsafe_allow_html=True,
                    )

            # Quota Summary
            st.markdown("#### Bowler Quota Verification (Max 4 overs per bowler)")
            quota_cols = st.columns(len(bowling_plan["overs_by_bowler"]))
            for idx, (b_name, b_ov) in enumerate(bowling_plan["overs_by_bowler"].items()):
                quota_cols[idx].metric(b_name, f"{b_ov} / 4 ov")

# ----------------- TAB 5: BATTER PHASE DYNAMICS & TSR -----------------
with tab_phase:
    st.subheader(f"📈 {selected_batter} - Phase Breakdown & True Strike Rate (TSR)")
    batter_profile = calculate_batter_tactical_metrics(slice_df, selected_batter, baselines)
    arch_matrix = get_archetype_matrix(slice_df, selected_batter, baselines)

    if not batter_profile.empty:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            fig_tsr = px.bar(
                batter_profile,
                x="phase",
                y="true_sr",
                color="true_sr",
                color_continuous_scale="RdYlGn",
                title=f"{selected_batter} - True Strike Rate (TSR) vs Par",
                labels={"true_sr": "True Strike Rate (TSR)", "phase": "Phase"},
                text="true_sr",
                template="plotly_dark",
            )
            fig_tsr.update_traces(texttemplate='%{text:+.1f}', textposition='outside')
            st.plotly_chart(fig_tsr, use_container_width=True)

        with col_r:
            fig_dots = px.bar(
                batter_profile,
                x="phase",
                y=["dot_pct", "boundary_pct"],
                barmode="group",
                title=f"{selected_batter} - Dot % vs Boundary % by Phase",
                template="plotly_dark",
                labels={"value": "Percentage (%)", "variable": "Metric"},
            )
            st.plotly_chart(fig_dots, use_container_width=True)

        st.markdown("#### Phase Summary Table")
        st.dataframe(batter_profile, use_container_width=True)

    if not arch_matrix.empty:
        st.markdown(f"#### 🎯 {selected_batter} vs Bowling Archetypes (Bayesian Regressed)")
        st.dataframe(arch_matrix, use_container_width=True)

# ----------------- TAB 6: BOWLER PRESSURE MATRIX -----------------
with tab_bowler:
    st.subheader(f"🎯 Bowler Control: {selected_bowler} ({bowler_style})")
    bowler_profile = calculate_bowler_tactical_metrics(slice_df, selected_bowler, baselines)

    if not bowler_profile.empty:
        st.markdown(f"#### Phase Breakdown for {selected_bowler}")
        st.dataframe(bowler_profile, use_container_width=True)

    # General bowler comparison
    all_bowler_stats = []
    for b in all_bowlers[:25]:
        b_p = calculate_bowler_tactical_metrics(slice_df, b, baselines)
        if not b_p.empty:
            b_balls = b_p["balls"].sum()
            b_runs = b_p["runs"].sum()
            b_wkts = b_p["wickets"].sum()
            b_dots = b_p["dot_pct"].mean()
            b_econ = round(b_runs / (b_balls / 6.0), 2) if b_balls > 0 else 0.0
            all_bowler_stats.append({
                "bowler": b,
                "subtype": slice_df[slice_df["bowler"] == b]["bowler_subtype"].iloc[0] if not slice_df[slice_df["bowler"] == b].empty else "Unknown",
                "balls": b_balls,
                "runs": b_runs,
                "wickets": b_wkts,
                "economy": b_econ,
                "avg_dot_pct": round(b_dots, 1),
            })
    if all_bowler_stats:
        b_df_matrix = pd.DataFrame(all_bowler_stats)
        fig_b = px.scatter(
            b_df_matrix,
            x="economy",
            y="avg_dot_pct",
            size="balls",
            color="subtype",
            hover_name="bowler",
            text="bowler",
            title="Top Bowlers Control Matrix (Economy vs Dot %)",
            labels={"economy": "Economy (Lower is Better)", "avg_dot_pct": "Dot % (Higher is Better)"},
            template="plotly_dark",
        )
        fig_b.update_traces(textposition='top center')
        st.plotly_chart(fig_b, use_container_width=True)

# ----------------- TAB 7: VENUE PAR BENCHMARKS -----------------
with tab_venue:
    st.subheader("🏟️ Stadium Par Score & Run Rate Benchmarks")
    venue_table = engine.get_venue_par_table(min_year=min_year)
    if not venue_table.empty:
        st.dataframe(venue_table, use_container_width=True)
        fig_venue = px.bar(
            venue_table.head(10),
            x="venue",
            y="par_rpo",
            color="par_rpo",
            color_continuous_scale="Viridis",
            title="Highest Scoring IPL Stadiums (Par Runs Per Over)",
            template="plotly_dark",
        )
        st.plotly_chart(fig_venue, use_container_width=True)

# ----------------- TAB 8: TACTICAL OPPOSITION DOSSIER -----------------
with tab_dossier:
    st.subheader(f"📑 1-Page Pre-Match Opposition Dossier: {selected_batter}")
    dossier_text = build_batter_dossier(
        slice_df,
        selected_batter,
        baselines,
        era_label=era_choice,
        venue=selected_venue,
    )
    st.markdown(dossier_text)
    st.download_button(
        label=f"📥 Download Dossier ({selected_batter}.md)",
        data=dossier_text,
        file_name=f"{selected_batter.lower().replace(' ', '_')}_{era_choice.split()[0].lower()}_dossier.md",
        mime="text/markdown",
    )
