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
from src.reports.dossier_builder import build_batter_dossier
from src.core.constants import ERA_RECENT_START_YEAR, ERA_ALL_TIME_START_YEAR

st.set_page_config(
    page_title="IPL Dugout Tactical Matchup & Strategy Engine",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1a1e29;
        border-radius: 8px;
        padding: 14px 18px;
        border-left: 4px solid #38bdf8;
        margin-bottom: 12px;
    }
    .big-stat {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
    }
    .stat-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-bowler {
        background-color: #ef4444;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
    }
    .badge-batter {
        background-color: #22c55e;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

engine = get_query_engine()

if not engine.is_ready():
    st.error("Parquet database not found. Please run `python src/ingest_pipeline.py --download` first.")
    st.stop()

# Header
st.title("🏏 IPL Tactical Matchup & Dugout Decision Engine")
st.caption("Next-Gen Cricket Intelligence | Micro-Phase Matchups | Venue & Era Normalization | DuckDB OLAP Engine")
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

# Fetch Dynamic Top Players based on selected era
top_batters = engine.get_top_batters(min_year=min_year, limit=60)
top_bowlers = engine.get_top_bowlers(min_year=min_year, limit=60)

st.sidebar.subheader("🎯 Player Matchup")
selected_batter = st.sidebar.selectbox(
    "Select Batter",
    top_batters,
    index=0 if top_batters else 0,
)
selected_bowler = st.sidebar.selectbox(
    "Select Bowler",
    top_bowlers,
    index=min(1, len(top_bowlers) - 1) if top_bowlers else 0,
)

# Load Filtered Dataset via DuckDB
@st.cache_data
def get_cached_slice(min_y: int, venue: str):
    return engine.get_deliveries(min_year=min_y, venue=venue if venue != "All Venues" else None)

slice_df = get_cached_slice(min_year, selected_venue)
baselines = compute_contextual_baselines(slice_df, venue=selected_venue)

# Metadata Display in Sidebar
b_meta = slice_df[slice_df["batter"] == selected_batter]
b_hand = b_meta["batter_hand"].iloc[0] if not b_meta.empty and "batter_hand" in b_meta.columns else "Unknown"
b_role = b_meta["batter_role"].iloc[0] if not b_meta.empty and "batter_role" in b_meta.columns else "Batter"

bw_meta = slice_df[slice_df["bowler"] == selected_bowler]
bowler_style = bw_meta["bowler_subtype"].iloc[0] if not bw_meta.empty and "bowler_subtype" in bw_meta.columns else "Unknown"

st.sidebar.markdown(f"**{selected_batter}**: `{b_hand}` ({b_role})")
st.sidebar.markdown(f"**{selected_bowler}**: `{bowler_style}`")

# Main Dashboard Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚔️ Dugout Matchup (H2H & Archetype)",
    "📊 Batter Phase Dynamics & TSR",
    "🎯 Bowler Control & Pressure (TER)",
    "🏟️ Venue Par Benchmarks",
    "📑 Tactical Opposition Dossier",
])

# ----------------- TAB 1: DUGOUT MATCHUP -----------------
with tab1:
    st.subheader(f"Tactical Matchup: {selected_batter} ({b_hand}) vs {selected_bowler} ({bowler_style})")
    verdict_info = get_dugout_tactical_verdict(slice_df, selected_batter, selected_bowler, baselines)

    # Tactical Verdict Banner
    if verdict_info["level"] == "bowler_advantage":
        st.error(f"🛡️ **VERDICT: {verdict_info['verdict']}**\n\n{verdict_info['advice']}")
    elif verdict_info["level"] == "batter_advantage":
        st.warning(f"🔥 **VERDICT: {verdict_info['verdict']}**\n\n{verdict_info['advice']}")
    else:
        st.info(f"⚖️ **VERDICT: {verdict_info['verdict']}**\n\n{verdict_info['advice']}")

    st.caption(f"**Decision Basis:** `{verdict_info['decision_source']}` | **Recency:** `{era_choice}`")

    # 1. Direct H2H
    st.markdown("### 1. Direct Head-to-Head Record")
    if verdict_info["direct_balls"] == 0:
        st.info(f"💡 No direct deliveries recorded between **{selected_batter}** and **{selected_bowler}** in this slice. Archetype priors used above.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Balls Faced", verdict_info["direct_balls"])
        c2.metric("Runs Scored", verdict_info["direct_runs"])
        c3.metric("Strike Rate", f"{verdict_info['direct_sr']}")
        c4.metric("Dot Ball %", f"{verdict_info['direct_dot_pct']}%")
        c5.metric("Dismissals", verdict_info["direct_outs"])

    # 2. Archetype Context
    st.markdown(f"### 2. Archetype Matchup: {selected_batter} vs {bowler_style}")
    if verdict_info["archetype_balls"] > 0:
        ca1, ca2, ca3, ca4, ca5 = st.columns(5)
        ca1.metric("Archetype Balls", verdict_info["archetype_balls"])
        ca2.metric("Archetype Runs", verdict_info["archetype_runs"])
        ca3.metric("Archetype SR", f"{verdict_info['archetype_sr']}")
        ca4.metric("Archetype Dot %", f"{verdict_info['archetype_dot_pct']}%")
        ca5.metric("Dismissals vs Archetype", verdict_info["archetype_outs"])
    else:
        st.write("Insufficient archetype deliveries in this slice.")

# ----------------- TAB 2: BATTER PHASE DYNAMICS & TSR -----------------
with tab2:
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

# ----------------- TAB 3: BOWLER PRESSURE MATRIX -----------------
with tab3:
    st.subheader(f"🎯 Bowler Control: {selected_bowler} ({bowler_style})")
    bowler_profile = calculate_bowler_tactical_metrics(slice_df, selected_bowler, baselines)

    if not bowler_profile.empty:
        st.markdown(f"#### Phase Breakdown for {selected_bowler}")
        st.dataframe(bowler_profile, use_container_width=True)

    # General bowler comparison
    all_bowler_stats = []
    for b in top_bowlers[:20]:
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

# ----------------- TAB 4: VENUE PAR BENCHMARKS -----------------
with tab4:
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

# ----------------- TAB 5: TACTICAL OPPOSITION DOSSIER -----------------
with tab5:
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
