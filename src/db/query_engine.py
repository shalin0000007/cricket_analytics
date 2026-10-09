"""
Embedded OLAP Query Engine powered by DuckDB over Parquet.
Provides zero-copy, sub-50ms analytics slicing across 300k+ deliveries:
- Recency filtering (Recent Form [2022–2024] vs Career [2008–2024])
- Venue & Ground-level isolation
- Micro-phase matchup extraction
"""

import os
from typing import Optional, List, Dict, Any
import duckdb
import pandas as pd


def normalize_venue_name(venue: Optional[str]) -> str:
    """Consolidates common venue name variations in IPL records."""
    if not isinstance(venue, str):
        return "Unknown"
    v = venue.lower()
    if "wankhede" in v:
        return "Wankhede Stadium"
    elif "chinnaswamy" in v:
        return "M Chinnaswamy Stadium"
    elif "eden gardens" in v:
        return "Eden Gardens"
    elif "chidambaram" in v or "chepauk" in v:
        return "MA Chidambaram Stadium (Chepauk)"
    elif "kotla" in v or "arun jaitley" in v:
        return "Arun Jaitley Stadium (Kotla)"
    elif "rajiv gandhi" in v or "uppal" in v:
        return "Rajiv Gandhi Stadium (Hyderabad)"
    elif "narendra modi" in v or "motera" in v:
        return "Narendra Modi Stadium (Ahmedabad)"
    elif "ekana" in v or "lucknow" in v:
        return "BRSABV Ekana Stadium (Lucknow)"
    elif "dharamsala" in v or "himachal" in v:
        return "HPCA Stadium (Dharamsala)"
    elif "sawai mansingh" in v:
        return "Sawai Mansingh Stadium (Jaipur)"
    return venue.strip()


class TacticalQueryEngine:
    """
    In-process DuckDB query engine bound to the processed Parquet store.
    """

    def __init__(self, parquet_path: Optional[str] = None):
        if parquet_path is None:
            parquet_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "processed", "ipl_deliveries.parquet"
            )
        self.parquet_path = parquet_path.replace("\\", "/")
        self.con = duckdb.connect()

        # Register view if parquet file exists
        if os.path.exists(self.parquet_path):
            self.con.execute(f"""
                CREATE OR REPLACE VIEW deliveries AS 
                SELECT 
                    *,
                    TRY_CAST(SUBSTRING(date, 1, 4) AS INT) AS season_year
                FROM read_parquet('{self.parquet_path}');
            """)

    def is_ready(self) -> bool:
        return os.path.exists(self.parquet_path)

    def query(self, sql: str, params: Optional[List[Any]] = None) -> pd.DataFrame:
        """Executes raw SQL query directly on parquet view."""
        if params:
            return self.con.execute(sql, params).df()
        return self.con.execute(sql).df()

    def get_deliveries(
        self,
        batter: Optional[str] = None,
        bowler: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        venue: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Retrieves a filtered delivery slice with sub-second execution.
        """
        conditions = ["1=1"]
        params = []

        if batter:
            conditions.append("batter = ?")
            params.append(batter)
        if bowler:
            conditions.append("bowler = ?")
            params.append(bowler)
        if min_year:
            conditions.append("season_year >= ?")
            params.append(min_year)
        if max_year:
            conditions.append("season_year <= ?")
            params.append(max_year)
        if venue and venue != "All Venues":
            conditions.append("venue LIKE ?")
            params.append(f"%{venue}%")

        where_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM deliveries WHERE {where_clause}"
        return self.con.execute(sql, params).df()

    def get_top_batters(self, min_year: Optional[int] = None, limit: Optional[int] = None) -> List[str]:
        """Returns batters ordered by total runs. If limit is None, returns all players."""
        year_cond = f"WHERE season_year >= {min_year}" if min_year else ""
        limit_clause = f"LIMIT {limit}" if limit else ""
        sql = f"""
            SELECT batter, SUM(batter_runs) as total_runs
            FROM deliveries
            {year_cond}
            GROUP BY batter
            ORDER BY total_runs DESC
            {limit_clause}
        """
        df = self.con.execute(sql).df()
        return df["batter"].tolist()

    def get_top_bowlers(self, min_year: Optional[int] = None, limit: Optional[int] = None) -> List[str]:
        """Returns bowlers ordered by total wickets. If limit is None, returns all players."""
        year_cond = f"WHERE season_year >= {min_year}" if min_year else ""
        limit_clause = f"LIMIT {limit}" if limit else ""
        sql = f"""
            SELECT bowler, SUM(is_wicket) as total_wkts
            FROM deliveries
            {year_cond}
            GROUP BY bowler
            ORDER BY total_wkts DESC
            {limit_clause}
        """
        df = self.con.execute(sql).df()
        return df["bowler"].tolist()

    def get_venue_par_table(self, min_year: Optional[int] = None) -> pd.DataFrame:
        """
        Calculates Par RPO and Par SR per venue across phases.
        """
        year_cond = f"WHERE season_year >= {min_year}" if min_year else ""
        sql = f"""
            SELECT 
                venue,
                COUNT(*) AS total_balls,
                ROUND(SUM(total_runs) * 6.0 / NULLIF(COUNT(CASE WHEN wides = 0 THEN 1 END), 0), 2) AS par_rpo,
                ROUND(AVG(CASE WHEN phase = 'Powerplay (0-6)' AND wides = 0 THEN batter_runs END) * 100, 1) AS pp_par_sr,
                ROUND(AVG(CASE WHEN phase = 'Middle Overs (7-15)' AND wides = 0 THEN batter_runs END) * 100, 1) AS mid_par_sr,
                ROUND(AVG(CASE WHEN phase = 'Death Overs (16-20)' AND wides = 0 THEN batter_runs END) * 100, 1) AS dth_par_sr
            FROM deliveries
            {year_cond}
            GROUP BY venue
            HAVING total_balls >= 1000
            ORDER BY par_rpo DESC
        """
        return self.con.execute(sql).df()


# Singleton factory
_GLOBAL_ENGINE: Optional[TacticalQueryEngine] = None


def get_query_engine() -> TacticalQueryEngine:
    global _GLOBAL_ENGINE
    if _GLOBAL_ENGINE is None:
        _GLOBAL_ENGINE = TacticalQueryEngine()
    return _GLOBAL_ENGINE
