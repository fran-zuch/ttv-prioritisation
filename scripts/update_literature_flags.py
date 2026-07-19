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
        last 36 months
    """

    twelve_months_ago = (
        datetime.utcnow() - timedelta(days=365)
    ).strftime("%Y-%m-01")

    three_years_ago = (
        datetime.utcnow() - timedelta(days=365*3)
    ).strftime("%Y-%m-01")

    query_12m = (
        f'(title:"{target_name}" OR abstract:"{target_name}") '
        f'AND database:astronomy '
        f'AND pubdate:[{twelve_months_ago} TO *]'
    )
    
    query_36m = (
        f'(title:"{target_name}" OR abstract:"{target_name}") '
        f'AND database:astronomy '
        f'AND pubdate:[{three_years_ago} TO *]'
    )
    
    return query_12m, query_36m


def query_ads(target_name: str):
    
    query = build_query(target_name)

    print(
        f"ADS Query: {query}",
        flush=True
    )

    params = {
        "q": query,
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
        
        latest_title = None
        latest_bibcode = None
        
        if docs:
            latest_title = (
                docs[0].get("title", [""])[0]
                if docs[0].get("title")
                else None
            )

        latest_bibcode = docs[0].get("bibcode")

        print(
            f"{target_name}: {result['response']['numFound']} matches",
            flush=True
        )
        
        for d in docs[:3]:
            print(
                f"  {d.get('pubdate')} | {d.get('title')}",
                flush=True
            )

        paper_count = result["response"]["numFound"]

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
            "papers_last_12m": papers_last_12m,
            "papers_last_36m": papers_last_36m,
            "last_paper_date": latest_date,
            "latest_title": latest_title,
            "latest_bibcode": latest_bibcode,
            "recent_activity_flag": papers_last_12m > 0,
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

    targets = fetch_exoclock()
    
    #targets = pd.DataFrame({"planet_name": ["K2-237b"]})

    print(
    f"Loaded {len(targets)} targets",
    flush=True
    )
    
    print(
        f"Columns: {targets.columns.tolist()}",
        flush=True
    )

    if "planet_name" in targets.columns:
        names = targets["planet_name"].dropna().unique()[:25]
    elif "name" in targets.columns:
        names = targets["name"].dropna().unique()[:25]
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
    
       # Be nice to ADS
        time.sleep(0.5)

    print(
        f"Completed queries for {len(rows)} targets",
        flush=True
    )

    df = pd.DataFrame(rows)

    print(
        f"Writing {len(df)} rows to CSV",
        flush=True
    )

    df.to_csv(CSV_OUT, index=False)

    with open(JSON_OUT, "w") as f:
        json.dump(cache, f, indent=2)

    print(
        f"Saved: {CSV_OUT}",
        flush=True
    )

    print(
        f"Saved: {JSON_OUT}",
        flush=True
    )

if __name__ == "__main__":
    main()


