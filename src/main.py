from datetime import datetime, timedelta

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

    # --- Expand events ---
    events = expand_events(df, start_str, end_str)

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

    events = compute_observability(events, obs_config)

    # --- TTV ---
    events = compute_ttv_features(events)

    # --- Instrument ---
    events = compute_instrument_features(events)
    events = add_instrument_constraints(events, telescope_aperture=24.0)
    events = add_instrument_penalty(events, alpha=2.0)

    # --- Science ---
    events = compute_science_features(events)

    # --- Synergy ---
    events = compute_synergy_features(events)

    # --- Scoring ---
    events = compute_scores(events)

    # --- Output ---
    filename = f"outputs_{start.strftime('%Y%m%d')}.csv"
    events.to_csv(filename, index=False)

    print(events[['name','S1','S2','S3','S4','S5','S6','final_score']].head())


if __name__ == '__main__':
    run()
