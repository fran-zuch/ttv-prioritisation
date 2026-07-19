"""
Weekly literature activity update.

Reads targets from ExoClock,
queries NASA ADS / SciX,
and generates:

    output/literature_flags.csv
    output/literature_cache.json

Requires:

    ADS_API_TOKEN

which has been set as a GitHub Actions secret.
"""
print("=== ADS Literature Update Starting ===", flush=True)

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

from ingestion.exoclock_loader import fetch_exoclock


ADS_URL = "https://api.adsabs.harvard.edu/v1/search/query"

ADS_TOKEN = os.getenv("ADS_API_TOKEN")

if not ADS_TOKEN:
    raise RuntimeError(
        "ADS_API_TOKEN environment variable not found"
    )


HEADERS = {
    "Authorization": f"Bearer {ADS_TOKEN}"
}


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_OUT = OUTPUT_DIR / "literature_flags.csv"
JSON_OUT = OUTPUT_DIR / "literature_cache.json"


def build_query(target_name: str) -> str:
    """
    Version 1:
        Search target name in TITLE only.

    Restrict to:
        astronomy database
        refereed papers
        last 12 months
    """

    twelve_months_ago = (
        datetime.utcnow() - timedelta(days=365)
    ).strftime("%Y-%m-01")

    return (
        f'title:"{target_name}" '
        f'AND database:astronomy '
        f'AND property:refereed '
        f'AND pubdate:[{twelve_months_ago} TO *]'
    )


def query_ads(target_name: str):

    params = {
        "q": build_query(target_name),
        "fl": "bibcode,title,pubdate",
        "rows": 50,
        "sort": "date desc"
    }

    response = requests.get(
        ADS_URL,
        headers=HEADERS,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json()


def process_target(target_name):

    try:

        result = query_ads(target_name)

        docs = result["response"]["docs"]

        paper_count = len(docs)

        pubdates = [
            d.get("pubdate")
            for d in docs
            if d.get("pubdate")
        ]

        bibcodes = [
            d.get("bibcode")
            for d in docs
            if d.get("bibcode")
        ]

        latest_date = (
            max(pubdates)
            if pubdates
            else None
        )

        return {
            "name": target_name,
            "papers_last_12m": paper_count,
            "last_paper_date": latest_date,
            "recent_activity_flag": paper_count > 0,
            "bibcodes": bibcodes
        }

    except Exception as e:

        print(f"Error: {target_name} -> {e}")

        return {
            "name": target_name,
            "papers_last_12m": 0,
            "last_paper_date": None,
            "recent_activity_flag": False,
            "bibcodes": []
        }


def main():

    print("Loading ExoClock targets...")

    #targets = fetch_exoclock()
    
    targets = pd.DataFrame({"planet_name": ["K2-139b"]})

    print(
    f"Loaded {len(targets)} targets",
    flush=True
    )
    
    print(
        f"Columns: {targets.columns.tolist()}",
        flush=True
    )

    if "planet_name" in targets.columns:
        names = targets["planet_name"].dropna().unique()[:5]
    elif "name" in targets.columns:
        names = targets["name"].dropna().unique()[:5]
    else:
        raise RuntimeError(
            "Could not find target names in ExoClock data."
        )

    rows = []
    cache = {}

    total = len(names)

    for idx, target in enumerate(names, start=1):

        print(f"[{idx}/{total}] {target}")

        result = process_target(target)

        rows.append({
            "name": result["name"],
            "papers_last_12m": result["papers_last_12m"],
            "last_paper_date": result["last_paper_date"],
            "recent_activity_flag": result["recent_activity_flag"]
        })

        cache[target] = {
            "papers_last_12m": result["papers_last_12m"],
            "last_paper_date": result["last_paper_date"],
            "bibcodes": result["bibcodes"],
            "last_checked": datetime.utcnow().isoformat()
        }

        # be nice to 
