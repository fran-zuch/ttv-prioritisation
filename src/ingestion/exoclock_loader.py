import json
import urllib.request
import pandas as pd
import numpy as np

EXOCLOCK_URL = "[exoclock.space](https://www.exoclock.space/database/planets_json)"


def fetch_exoclock():
    # Fetch raw JSON
    with urllib.request.urlopen(EXOCLOCK_URL) as f:
        data = json.loads(f.read())

    rows = []
    for k, v in data.items():
        row = {"name": k}   # canonical target name
        if isinstance(v, dict):
            row.update(v)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Standardise source column names -> pipeline canonical names
    rename_map = {
        "planet_name": "name",
        "v_mag": "mag_V",
        "depth_r_mmag": "depth_mmag",
        "depth_mmag": "depth_mmag",
        "duration_hr": "duration_hr",
        "duration_hours": "duration_hr",
        "ephem_mid_time": "ephem_mid_time",
        "ephem_period": "ephem_period",
        "t0_bjd_tdb": "t0_bjd_tdb",
        "t0_unc": "t0_unc",
        "period_days": "period_days",
        "period_unc": "period_unc",
        "last_observed_midpoint": "last_obs_jd",
    }
    df = df.rename(columns=rename_map)

    # Ensure required columns exist
    required_cols = [
        "name",
        "exoclock_priority",
        "depth_mmag",
        "duration_hr",
        "mag_V",
        "ephem_mid_time",
        "ephem_period",
        "t0_bjd_tdb",
        "t0_unc",
        "period_days",
        "period_unc",
        "current_oc_min",
        "last_obs_jd",
        "ttv_flag",
        "literature_midtimes_recent",
        "expected_transit_snr_tess",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # Derived fields used later in pipeline
    if "period_days" in df.columns:
        df["events_per_month"] = 30 / pd.to_numeric(df["period_days"], errors="coerce")
    else:
        df["events_per_month"] = np.nan

    if "literature_midtimes_recent" in df.columns:
        lit = pd.to_numeric(df["literature_midtimes_recent"], errors="coerce").fillna(0)
        df["recent_activity_flag"] = lit > 0
    else:
        df["recent_activity_flag"] = False

    if "duration_hr" in df.columns:
        dur = pd.to_numeric(df["duration_hr"], errors="coerce")
        df["network_needed"] = dur > 3
    else:
        df["network_needed"] = False

    df["campaign_flag"] = df["exoclock_priority"].astype(str).str.lower().eq("alert")

    if "expected_transit_snr_tess" in df.columns:
        df["snr_proxy"] = pd.to_numeric(df["expected_transit_snr_tess"], errors="coerce")
    else:
        df["snr_proxy"] = np.nan

    return df
