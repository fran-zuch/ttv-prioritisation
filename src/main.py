from datetime import datetime, timedelta
import os

from ingestion.exoclock_loader import fetch_exoclock
from processing.catalog import prepare_catalog
from processing.ephemeris import expand_events
from processing.observability import compute_observability
from processing.ttv import compute_ttv_features
from processing.instrument import (
    compute_instrument_features,
    add_instrument_constraints,
    add_instrument_penalty
)
from processing.science import compute_science_features
from processing.synergy import compute_synergy_features
from scoring.scoring import compute_scores

from interpretation.interpretation_utils import (
    add_dynamic_interpretation,
    add_synergy_explanations,
    add_recency_labels,
    build_score_breakdown
)
from interpretation.score_interpretation import (
    build_dynamic_summary,
    add_flag_labels
)

def run():

    print("RUNNING UPDATED PIPELINE - VERSION 2")

    # --- Dynamic 30-day window ---
    start = datetime.utcnow()
    end = start + timedelta(days=30)

    start_str = start.strftime('%Y-%m-%d %H:%M')
    end_str = end.strftime('%Y-%m-%d %H:%M')

    print(f"Running window: {start_str} → {end_str}")

    # --- Ingestion ---
    df = prepare_catalog(fetch_exoclock())
    
    print(df[["name", "min_telescope_inches"]].head())

    # --- Ephemeris calculation ---
    events = expand_events(df, start_str, end_str)
    events = events.drop_duplicates(subset='event_id')
    print("Total events:", len(events))
    print("Unique events:", len(events[['name','epoch','Tmid_utc']].drop_duplicates()))
    print("After dedup:", len(events))


    if events.empty:
        print("No observable events found in window.")
        return
  
    # --- Observability ---
    obs_config = {
        "lat": 28.3,
        "lon": -16.5,
        "elevation": 2400,
        "min_alt": 20,
        "max_sun_alt": -18,
        "min_moon_sep": 30
    }
    print("Starting observability calculation")

    try:
        events = compute_observability(events, obs_config)
        print ("Observability COMPLETE")
    except Exception as e:
        print("Observability FAILED", e)
        

    print(events[["Tmid_utc"]].head())
    print(type(events["Tmid_utc"].iloc[0]))

    print(events[["obs_frac", "obs_max_alt"]].head())

    # --- TTV ---
    events = compute_ttv_features(events)
    
    # --- Instrument input validation ---
    required_cols = ["mag_V", "depth_mmag", "duration_hours"]
    
    missing = [c for c in required_cols if c not in events.columns]
    if missing:
        raise ValueError(f"Missing required instrument columns: {missing}")
    
    print(events[required_cols].describe())
        
    # --- Instrument ---
    events = compute_instrument_features(events)
    events = add_instrument_constraints(events, telescope_aperture=24.0)
    events = add_instrument_penalty(events, alpha=2.0)

    print(events[[
        "name",
        "mag_V",
        "depth_mmag",
        "duration_hours",
        "required_aperture",
        "aperture_exoclock",
        "aperture_ratio",
        "instrument_flag"
    ]].head())

    # --- Science ---
    events = compute_science_features(events)

    # --- Synergy ---
    events = compute_synergy_features(events)

    # --- Scoring ---
    events = compute_scores(events)

    # --- Interpretation ---
    events = add_dynamic_interpretation(events)
    events = add_synergy_explanations(events)
    events = add_recency_labels(events)
    events = build_score_breakdown(events)
    events = build_dynamic_summary(events)

    # ---- UI Enrichment ----
    events = add_flag_labels(events)

    # --- Output ---
    # Path to the repo root (one level above src/)
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Path to the output folder
    OUTPUT_DIR = os.path.join(ROOT, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    filename = os.path.join(
        OUTPUT_DIR,
        f"outputs_{start.strftime('%Y%m%d')}.csv"
    )
    
    events.to_csv(filename, index=False)

    print("Saving to:", filename)

    
    # ✅ ALSO write latest pointer file
    # events.to_csv("outputs.csv", index=False)


    print(events[['name','S1','S2','S3','S4','S5','S6','final_score']].head())


if __name__ == '__main__':
    run()
