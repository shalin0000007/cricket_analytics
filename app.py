import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Ensure src modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from parser import parse_cricsheet_json
from analytics import get_head_to_head, get_batter_phase_stats, get_bowler_economy_summary

st.set_page_config(
    page_title="IPL Dugout Tactical Matchup Engine",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
    }
    .big-stat {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
    }
    .stat-label {
        font-size: 13px;
        color: #8b949e;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_match_data(file_path: str):
    return parse_cricsheet_json(file_path)


# Load Data
data_file = os.path.join(os.path.dirname(__file__), "data", "raw", "1525657.json")
if not os.path.exists(data_file):
    st.error(f"Match data not found at {data_file}")
    st.stop()

df = load_match_data(data_file)

# Header
st.title("🏏 IPL Dugout Tactical Matchup Engine")
st.caption(f"**Match Loaded:** {df['event'].iloc[0]} ({df['match_type'].iloc[0]}) | **Venue:** {df['venue'].iloc[0]} | **Date:** {df['date'].iloc[0]}")
st.divider()

# Sidebar: Tactical Selection
st.sidebar.header("🎯 Tactical Matchup Selectors")

batters = sorted(df["batter"].unique())
bowlers = sorted(df["bowler"].unique())

selected_batter = st.sidebar.selectbox("Select Batter", batters, index=0)
selected_bowler = st.sidebar.selectbox("Select Bowler", bowlers, index=min(2, len(bowlers)-1))

# Analytics Computation
h2h = get_head_to_head(df, selected_batter, selected_bowler)
batter_phases = get_batter_phase_stats(df, selected_batter)

# Main Dashboard Layout
tab1, tab2, tab3 = st.tabs(["⚔️ Head-to-Head (H2H) Matchup", "📊 Batter Phase Radar", "🎯 Bowler Economy & Pressure"])

with tab1:
    st.subheader(f"Tactical Matchup: {selected_batter} vs {selected_bowler}")

    if h2h["balls_faced"] == 0:
        st.info(f"No direct head-to-head deliveries between **{selected_batter}** and **{selected_bowler}** in this match record.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Balls Faced", h2h["balls_faced"])
        col2.metric("Runs Scored", h2h["runs_scored"])
        col3.metric("Strike Rate", f"{h2h['strike_rate']}%")
        col4.metric("Dot Ball %", f"{h2h['dot_percentage']}%")
        col5.metric("Dismissals", h2h["dismissals"])

        # Dugout Tactical Recommendation Box
        st.markdown("### 📋 Dugout Tactical Verdict")
        if h2h["strike_rate"] >= 140:
            st.success(f"🔥 **Batter Dominant:** {selected_batter} scores freely against {selected_bowler} (SR: {h2h['strike_rate']}). Consider changing bowling matchup.")
        elif h2h["dot_percentage"] >= 50 or h2h["strike_rate"] < 100:
            st.warning(f"🛡️ **Bowler Pressure:** {selected_bowler} controls this matchup ({h2h['dot_percentage']}% dots, SR: {h2h['strike_rate']}). Recommended containment matchup.")
        else:
            st.info(f"⚖️ **Balanced Battle:** Strike Rate at {h2h['strike_rate']} with standard rotation.")

with tab2:
    st.subheader(f"📈 {selected_batter} - Performance Across Tactical Phases")
    if not batter_phases.empty:
        col_l, col_r = st.columns([1, 1])
        with col_l:
            fig_sr = px.bar(
                batter_phases,
                x="phase",
                y="strike_rate",
                color="phase",
                title=f"{selected_batter} Strike Rate by Phase",
                text="strike_rate",
                template="plotly_dark"
            )
            fig_sr.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            st.plotly_chart(fig_sr, use_container_width=True)

        with col_r:
            fig_dots = px.pie(
                batter_phases,
                names="phase",
                values="runs",
                title=f"Runs Distribution by Phase",
                template="plotly_dark",
                hole=0.4
            )
            st.plotly_chart(fig_dots, use_container_width=True)

        st.dataframe(batter_phases, use_container_width=True)
    else:
        st.write("No phase data available.")

with tab3:
    st.subheader("🎯 Bowler Economy & Dot Ball Pressure Index")
    bowler_df = get_bowler_economy_summary(df)
    
    fig_bowlers = px.scatter(
        bowler_df,
        x="economy",
        y="dot_pct",
        size="balls",
        color="wickets",
        hover_name="bowler",
        text="bowler",
        title="Bowler Control Matrix (Economy vs Dot %)",
        labels={"economy": "Economy Rate (Lower is Better)", "dot_pct": "Dot Ball % (Higher is Better)"},
        template="plotly_dark"
    )
    fig_bowlers.update_traces(textposition='top center')
    st.plotly_chart(fig_bowlers, use_container_width=True)
    
    st.dataframe(bowler_df, use_container_width=True)
