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

    # ✅ Dynamic 30-day window
    start = datetime.utcnow()
    end = start + timedelta(days=30)

    start_str = start.strftime('%Y-%m-%d %H:%M')
    end_str = end.strftime('%Y-%m-%d %H:%M')

    print(f"Running window: {start_str} → {end_str}")

    # ✅ Data ingestion
    df = prepare_catalog(fetch_exoclock())

    # ✅ Expand events
    events = expand_events(df, start_str, end_str)

    # ✅ Observability (S4)
    events = compute_observability(events)

    # ✅ TTV marker (S2)
    events = compute_ttv_features(events)

    # ✅ Existing instrument scoring (difficulty → S3)
    events = compute_instrument_features(events)
    
    # ✅ NEW: physical feasibility layer
    events = add_instrument_constraints(events, telescope_aperture=24.0)
    events = add_instrument_penalty(events, alpha=2.0)

    # ✅ Scientific impact (S5)
    events = compute_science_features(events)

    # ✅ Network and community impact (S6)
    events = compute_synergy_features(events)

    # ✅ Final scoring
    events = compute_scores(events)

    # ✅ Output
    events.to_csv('outputs.csv', index=False)

    print(events[['name','S1','S2','S3','S4','S5','S6','final_score']].head())


if __name__ == '__main__':
    run()

print("RUNNING UPDATED PIPELINE - VERSION 2")
