"""
Bulk Ingestion & Dataset Compilation Pipeline.
Downloads and compiles all Cricsheet IPL matches into an enriched,
partitioned Parquet database (ipl_deliveries.parquet).
"""

import os
import sys
import zipfile
import urllib.request
import argparse
from typing import Optional
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from parser import parse_cricsheet_json
    from player_registry import get_default_registry
except ImportError:
    from src.parser import parse_cricsheet_json
    from src.player_registry import get_default_registry

CRICSHEET_IPL_ZIP_URL = "https://cricsheet.org/downloads/ipl_json.zip"


def download_ipl_dataset(dest_zip_path: str) -> bool:
    """Downloads the official full IPL dataset from Cricsheet."""
    os.makedirs(os.path.dirname(dest_zip_path), exist_ok=True)
    if os.path.exists(dest_zip_path):
        print(f"IPL zip archive already exists at: {dest_zip_path}")
        return True

    print(f"Downloading official Cricsheet IPL dataset from {CRICSHEET_IPL_ZIP_URL}...")
    try:
        req = urllib.request.Request(
            CRICSHEET_IPL_ZIP_URL, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req) as resp, open(dest_zip_path, "wb") as f:
            f.write(resp.read())
        print(f"Download complete! Saved to {dest_zip_path} ({os.path.getsize(dest_zip_path):,} bytes)")
        return True
    except Exception as e:
        print(f"[Error] Failed to download dataset: {e}")
        return False


def build_ipl_parquet_database(
    zip_path: str,
    output_parquet: str,
    max_matches: Optional[int] = None,
    batch_size: int = 50,
) -> pd.DataFrame:
    """
    Extracts, enriches, and compiles all IPL matches directly into a Parquet database.
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Archive not found: {zip_path}")

    os.makedirs(os.path.dirname(output_parquet), exist_ok=True)
    reg = get_default_registry()

    all_frames = []
    total_parsed = 0

    with zipfile.ZipFile(zip_path, "r") as z:
        json_filenames = [f for f in z.namelist() if f.endswith(".json") and not f.startswith("README")]
        if max_matches:
            json_filenames = json_filenames[:max_matches]

        total_files = len(json_filenames)
        print(f"Found {total_files} match files to process...")

        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            for idx, json_name in enumerate(json_filenames, start=1):
                extracted_path = z.extract(json_name, tmp_dir)
                try:
                    df = parse_cricsheet_json(extracted_path, enrich=True)
                    all_frames.append(df)
                    total_parsed += 1
                except Exception as e:
                    print(f"[Warning] Skipped {json_name}: {e}")

                if idx % batch_size == 0 or idx == total_files:
                    print(f"Progress: [{idx}/{total_files}] matches parsed...")

    if not all_frames:
        print("No matches were parsed.")
        return pd.DataFrame()

    print("Concatenating all matches into unified DataFrame...")
    final_df = pd.concat(all_frames, ignore_index=True)

    print(f"Writing {len(final_df):,} enriched deliveries to Parquet: {output_parquet}...")
    final_df.to_parquet(output_parquet, index=False, engine="pyarrow", compression="snappy")
    print(f"Successfully compiled! File size: {os.path.getsize(output_parquet):,} bytes.")

    return final_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IPL Data Pipeline Ingestion")
    parser.add_argument("--download", action="store_true", help="Download ipl_json.zip from Cricsheet")
    parser.add_argument("--max-matches", type=int, default=None, help="Limit number of matches to parse")
    parser.add_argument("--zip", type=str, default="data/raw/ipl_json.zip", help="Path to zip archive")
    parser.add_argument("--out", type=str, default="data/processed/ipl_deliveries.parquet", help="Output parquet path")

    args = parser.parse_args()

    if args.download:
        download_ipl_dataset(args.zip)

    if os.path.exists(args.zip):
        build_ipl_parquet_database(args.zip, args.out, max_matches=args.max_matches)
    else:
        print(f"Zip archive not found at {args.zip}. Run with --download to fetch it.")
