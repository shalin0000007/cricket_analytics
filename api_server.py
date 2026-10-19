import os
import sys
import time
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure src modules are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db.query_engine import get_query_engine
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
)
from src.reports.dossier_builder import build_batter_dossier
from src.core.constants import ERA_RECENT_START_YEAR, ERA_ALL_TIME_START_YEAR

app = FastAPI(
    title='DUGOUT OS Tactical Intelligence API',
    description='Zero-copy DuckDB OLAP Tactical Cricket Engine',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

engine = get_query_engine()

@app.get('/api/health')
def health_check():
    return {
        'status': 'online',
        'engine_ready': engine.is_ready(),
        'timestamp': time.time(),
    }

@app.get('/api/players/search')
def search_players(min_year: int = Query(ERA_RECENT_START_YEAR)):
    t0 = time.perf_counter()
    batters = engine.get_top_batters(min_year=min_year)
    bowlers = engine.get_top_bowlers(min_year=min_year)
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'batters': batters,
        'bowlers': bowlers,
        'query_ms': round(ms, 2)
    }

@app.get('/api/duel')
def get_duel(
    batter: str = Query('V Kohli'),
    bowler: str = Query('JJ Bumrah'),
    min_year: int = Query(ERA_RECENT_START_YEAR),
    venue: Optional[str] = Query(None)
):
    t0 = time.perf_counter()
    v_param = venue if venue and venue != 'All Venues' else None
    df = engine.get_deliveries(min_year=min_year, venue=v_param)
    baselines = compute_contextual_baselines(df, venue=v_param)
    
    verdict = get_dugout_tactical_verdict(df, batter, bowler, baselines)
    
    # Extract historical delivery strip
    h2h_deliveries = df[(df['batter'] == batter) & (df['bowler'] == bowler)]
    balls_list = []
    if not h2h_deliveries.empty:
        for _, row in h2h_deliveries.iterrows():
            balls_list.append({
                'over': int(row.get('over', 0)),
                'ball': int(row.get('ball', 0)),
                'runs': int(row.get('batter_runs', 0)),
                'isDot': bool(row.get('is_dot', 0) == 1),
                'isFour': bool(row.get('is_four', 0) == 1),
                'isSix': bool(row.get('is_six', 0) == 1),
                'isWicket': bool(row.get('is_wicket', 0) == 1),
                'wicketKind': str(row.get('wicket_kind', '')),
                'date': str(row.get('date', '')),
                'matchId': str(row.get('match_id', '')),
            })

    # Archetype Matrix for batter
    arch_matrix = get_archetype_matrix(df, batter, baselines)
    arch_records = arch_matrix.to_dict(orient='records') if not arch_matrix.empty else []

    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'verdict': verdict,
        'balls': balls_list,
        'archetype_matrix': arch_records,
        'query_ms': round(ms, 2)
    }

@app.get('/api/radar')
def get_radar(
    player: str = Query('V Kohli'),
    role: str = Query('batter'),
    min_year: int = Query(ERA_RECENT_START_YEAR)
):
    t0 = time.perf_counter()
    df = engine.get_deliveries(min_year=min_year)
    
    if role == 'bowler':
        radar_data = calculate_bowler_radar_percentiles(df, player)
    else:
        radar_data = calculate_batter_radar_percentiles(df, player)
        
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'player': player,
        'role': role,
        'radar': radar_data or {},
        'query_ms': round(ms, 2)
    }

class SquadRequest(BaseModel):
    batters: List[str]
    bowlers: List[str]
    min_year: int = ERA_RECENT_START_YEAR
    venue: Optional[str] = None

@app.post('/api/squad')
def get_squad_tactics(req: SquadRequest):
    t0 = time.perf_counter()
    v_param = req.venue if req.venue and req.venue != 'All Venues' else None
    df = engine.get_deliveries(min_year=req.min_year, venue=v_param)
    baselines = compute_contextual_baselines(df, venue=v_param)
    
    adv_df, det_df = compute_team_matchup_matrix(df, req.batters, req.bowlers, baselines)
    plan = generate_20_over_bowling_plan(df, req.batters, req.bowlers, baselines)
    
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'advantage_matrix': adv_df.to_dict(),
        'details_matrix': det_df.to_dict(),
        'bowling_plan': plan,
        'query_ms': round(ms, 2)
    }

@app.get('/api/true-metrics')
def get_true_metrics(
    player: str = Query('V Kohli'),
    role: str = Query('batter'),
    min_year: int = Query(ERA_RECENT_START_YEAR),
    venue: Optional[str] = Query(None)
):
    t0 = time.perf_counter()
    v_param = venue if venue and venue != 'All Venues' else None
    df = engine.get_deliveries(min_year=min_year, venue=v_param)
    baselines = compute_contextual_baselines(df, venue=v_param)
    
    if role == 'bowler':
        metrics_df = calculate_bowler_tactical_metrics(df, player, baselines)
    else:
        metrics_df = calculate_batter_tactical_metrics(df, player, baselines)
        
    records = metrics_df.to_dict(orient='records') if not metrics_df.empty else []
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'player': player,
        'role': role,
        'metrics': records,
        'query_ms': round(ms, 2)
    }

@app.get('/api/venues')
def get_venues(min_year: int = Query(ERA_RECENT_START_YEAR)):
    t0 = time.perf_counter()
    v_table = engine.get_venue_par_table(min_year=min_year)
    records = v_table.to_dict(orient='records') if not v_table.empty else []
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'venues': records,
        'query_ms': round(ms, 2)
    }

@app.get('/api/dossier')
def get_dossier(
    batter: str = Query('V Kohli'),
    min_year: int = Query(ERA_RECENT_START_YEAR),
    venue: Optional[str] = Query(None)
):
    t0 = time.perf_counter()
    v_param = venue if venue and venue != 'All Venues' else None
    df = engine.get_deliveries(min_year=min_year, venue=v_param)
    baselines = compute_contextual_baselines(df, venue=v_param)
    era_label = 'Recent 2022-2024' if min_year >= 2022 else 'Career 2008-2024'
    
    dossier_md = build_batter_dossier(df, batter, baselines, era_label=era_label, venue=venue)
    ms = (time.perf_counter() - t0) * 1000.0
    return {
        'batter': batter,
        'dossier_markdown': dossier_md,
        'query_ms': round(ms, 2)
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
