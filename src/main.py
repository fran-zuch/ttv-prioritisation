from ingestion.exoclock_loader import fetch_exoclock
from processing.catalog import prepare_catalog
from processing.ephemeris import expand_events
from processing.observability import compute_observability
from scoring.scoring import compute_scores

def run():
    df=prepare_catalog(fetch_exoclock())
    events=expand_events(df,'2026-06-01 00:00','2026-06-30 23:59')
    events=compute_observability(events)
    events=compute_scores(events)
    events.to_csv('outputs.csv',index=False)
    print(events.head())

if __name__=='__main__': run()
