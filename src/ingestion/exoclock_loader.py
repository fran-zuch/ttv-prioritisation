import json
import urllib.request
import pandas as pd
import numpy as np

EXOCLOCK_URL = "https://www.exoclock.space/database/planets_json"

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
        "last_observed_midpoint": "last_obs_jd",
        "min_telescope_inches": "min_telescope_inches",
        "priority": "exoclock_priority",
        "total_observations": "n_obs_total",
        "recent_observations": "n_obs_recent",
        "ra_j2000": "ra",
        "dec_j2000": "dec",
    }

    df = df.rename(columns=rename_map)

    # Ensure numeric coords
    df["ra"] = pd.to_numeric(df.get("ra"), errors="coerce")
    df["dec"] = pd.to_numeric(df.get("dec"), errors="coerce")

    # Ensure required columns exist
    required_cols = [...]
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    return df
