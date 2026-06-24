from datetime import datetime, timedelta

from ingestion.exoclock_loader import fetch_exoclock
from processing.catalog import prepare_catalog
from processing.ephemeris import expand_events
from processing.observability import compute_observability

from processing.ttv import compute_ttv_features
from processing.instrument import compute_s3_instrument
from processing.science import compute_s5_science
from processing.synergy import compute_s6_synergy

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

    # ✅ Observability
    events = compute_observability(events)

    # ✅ Feature scoring (S2–S6)
    events = compute_ttv_features(events)
    events = compute_s3_instrument(events)
    events = compute_s5_science(events)
    events = compute_s6_synergy(events)

    # ✅ Final scoring
    events = compute_scores(events)

    # ✅ Output
    events.to_csv('outputs.csv', index=False)

    print(events[['name','S1','S2','S3','S4','S5','S6','final_score']].head())


if __name__ == '__main__':
    run()
