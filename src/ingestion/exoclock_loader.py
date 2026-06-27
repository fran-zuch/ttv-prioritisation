import json
import urllib.request
import pandas as pd
import numpy as np

EXOCLOCK_URL = "https://www.exoclock.space/database/planets_json"


def hms_to_deg(hms):
    if pd.isna(hms):
        return np.nan
    try:
        h, m, s = [float(x.strip()) for x in str(hms).split(":")]
        return 15 * (h + m/60 + s/3600)
    except:
        return np.nan


def dms_to_deg(dms):
    if pd.isna(dms):
        return np.nan
    try:
        dms = str(dms).strip()
        sign = -1 if dms.startswith("-") else 1
        d, m, s = [float(x) for x in dms.replace("+","").replace("-","").split(":")]
        return sign * (d + m/60 + s/3600)
    except:
        return np.nan


def fetch_exoclock():
    with urllib.request.urlopen(EXOCLOCK_URL, timeout=30) as f:
        data = json.loads(f.read().decode("utf-8"))

    rows = []
    for k, v in data.items():
        row = {"name": k}
        if isinstance(v, dict):
            row.update(v)
        rows.append(row)

    df = pd.DataFrame(rows)

    rename_map = {
        "planet_name": "name",
        "v_mag": "mag_V",
        "depth_r_mmag": "depth_mmag",
        "ephem_mid_time": "last_obs_jd",
        "min_telescope_inches": "min_telescope_inches",
        "priority": "exoclock_priority",
        "total_observations": "n_obs_total",
        "total_observations_recent": "n_obs_recent",
        "ra_j2000": "ra",
        "dec_j2000": "dec",
    }

    df = df.rename(columns=rename_map)

    # Convert RA/DEC from sexagesimal to degrees
    df["ra"] = df["ra"].apply(hms_to_deg)
    df["dec"] = df["dec"].apply(dms_to_deg)
    
    print(df[["name", "ra", "dec"]].head())

    df["ra"] = pd.to_numeric(df["ra"], errors="coerce")
    df["dec"] = pd.to_numeric(df["dec"], errors="coerce")

    print("RA/DEC after conversion:")
    print(df[["ra", "dec"]].head())
    print(df[["ra", "dec"]].dtypes)


    # Ensure required columns exist
    required_cols = [...]
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    return df
