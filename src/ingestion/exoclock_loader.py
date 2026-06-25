import json, urllib.request, pandas as pd

EXOCLOCK_URL = 'https://www.exoclock.space/database/planets_json'

def fetch_exoclock():

    # ✅ Fetch raw JSON
    with urllib.request.urlopen(EXOCLOCK_URL) as f:
        data = json.loads(f.read())

    rows = []
    for k, v in data.items():
        row = {'planet_name': k}
        if isinstance(v, dict):
            row.update(v)
        rows.append(row)

    df = pd.DataFrame(rows)

    # ✅ ---- STANDARDISE COLUMN NAMES ----

    rename_map = {
        'v_mag': 'mag_V',
        'depth_r_mmag': 'depth_mmag',  # fallback if depth missing
        'depth_mmag': 'depth_mmag',
        'duration_hr': 'duration_hr',
    }

    df = df.rename(columns=rename_map)

    # ✅ Ensure key columns exist
    required_cols = [
        'planet_name',
        'exoclock_priority',
        'depth_mmag',
        'duration_hr',
        'mag_V',
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # ✅ ---- DERIVED FIELDS FOR PIPELINE ----

    # ✅ Observational cadence → events_per_month (approx)
    if 'period_days' in df.columns:
        df['events_per_month'] = 30 / df['period_days']
    else:
        df['events_per_month'] = None

    # ✅ Literature activity (used in S5)
    if 'literature_midtimes_recent' in df.columns:
        df['recent_activity_flag'] = df['literature_midtimes_recent'] > 0
    else:
        df['recent_activity_flag'] = False

    # ✅ Network needed (for S6)
    if 'duration_hr' in df.columns:
        df['network_needed'] = df['duration_hr'] > 3
    else:
        df['network_needed'] = False

    # ✅ Campaign flag (optional but powerful)
    df['campaign_flag'] = df['exoclock_priority'] == 'alert'

    # ✅ Instrument proxy (future S3 improvements)
    if 'expected_transit_snr_tess' in df.columns:
        df['snr_proxy'] = df['expected_transit_snr_tess']
    else:
        df['snr_proxy'] = None

    return df
