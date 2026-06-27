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

    # ----------------------------
    # 1. Ensure numeric fields
    # ----------------------------
    
    df["min_telescope_inches"] = pd.to_numeric(
        df.get("min_telescope_inches"),
        errors="coerce"
    )

    cols = [
        "ephem_mid_time",
        "ephem_period",
        "t0_bjd_tdb",
        "t0_unc",
        "period_days",
        "period_unc",
        "duration_hours",   # ✅ FIXED
        "depth_mmag",
        "mag_V",
        "gaia_g_mag",
        "current_oc_min",
        "last_obs_jd",
        "n_obs_recent",
        "expected_transit_snr_tess",
        "min_telescope_inches",
    ]
    df = to_numeric(df, cols)

    # ----------------------------
    # 2. Canonical ephemeris
    # ----------------------------
    df["T0"] = df["t0_bjd_tdb"].fillna(df["ephem_mid_time"])
    df["P"] = df["period_days"].fillna(df["ephem_period"])

    df["T0_unc_days"] = df["t0_unc"].fillna(0)
    df["P_unc_days"] = df["period_unc"].fillna(0)

    # ----------------------------
    # 3. Derived fields (moved from loader)
    # ----------------------------

    # Events per month
    df["events_per_month"] = 30 / df["P"]

    # Recent observation activity
    if "n_obs_recent" in df.columns:
        df["recent_activity_flag"] = df["n_obs_recent"].fillna(0) > 0
    else:
        df["recent_activity_flag"] = False

    # Campaign flag (alert priority)
    df["campaign_flag"] = (
        df["exoclock_priority"]
        .astype(str)
        .str.lower()
        .eq("alert")
    )

    # Network requirement (long duration)
    df["network_needed"] = df["duration_hours"] > 3

    # SNR proxy (ExoClock-provided or fallback estimate later)
    if "expected_transit_snr_tess" in df.columns:
        df["snr_proxy"] = df["expected_transit_snr_tess"]
    else:
        df["snr_proxy"] = np.nan

    # ----------------------------
    # 4. Ensure required flags exist
    # ----------------------------
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

    df["ttv_flag"] = (
        pd.to_numeric(df["ttv_flag"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    return df
