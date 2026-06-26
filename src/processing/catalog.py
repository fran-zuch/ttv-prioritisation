import pandas as pd
import numpy as np

def to_numeric(df, cols):
    for c in cols:
        if c not in df.columns:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def prepare_catalog(df):
    df = df.copy()

    cols = [
        "ephem_mid_time",
        "ephem_period",
        "t0_bjd_tdb",
        "t0_unc",
        "period_days",
        "period_unc",
        "duration_hr",
        "depth_mmag",
        "mag_V",
        "gaia_g_mag",
        "current_oc_min",
        "last_obs_jd",
        "events_per_month",
        "snr_proxy",
    ]
    df = to_numeric(df, cols)

    # Canonical ephemeris fields
    df["T0"] = df["t0_bjd_tdb"].fillna(df["ephem_mid_time"])
    df["P"] = df["period_days"].fillna(df["ephem_period"])
    df["T0_unc_days"] = df["t0_unc"].fillna(0)
    df["P_unc_days"] = df["period_unc"].fillna(0)

    # Ensure core descriptive fields exist
    defaults = {
        "name": None,
        "exoclock_priority": None,
        "recent_activity_flag": False,
        "network_needed": False,
        "campaign_flag": False,
        "ttv_flag": 0,
    }

    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default

    df["recent_activity_flag"] = df["recent_activity_flag"].fillna(False).astype(bool)
    df["network_needed"] = df["network_needed"].fillna(False).astype(bool)
    df["campaign_flag"] = df["campaign_flag"].fillna(False).astype(bool)
    df["ttv_flag"] = pd.to_numeric(df["ttv_flag"], errors="coerce").fillna(0).astype(int)

    return df
