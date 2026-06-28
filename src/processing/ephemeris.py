import numpy as np
from astropy.time import Time
import pandas as pd


def propagate_uncertainty(T0, P, T0_sig, P_sig, Tmid):
    epochs = (Tmid - T0) / P
    return np.sqrt(T0_sig**2 + (epochs * P_sig)**2)


def compute_time_since_last_obs(last_obs_jd):
    if last_obs_jd is None:
        return None
    if not np.isfinite(last_obs_jd):
        return None
    return Time.now().tdb.jd - last_obs_jd



def expand_events(df, start_utc, end_utc):
    start = Time(start_utc)
    end = Time(end_utc)

    events = []

    for _, r in df.iterrows():
        T0 = r.get("T0")
        P = r.get("P")

        if T0 is None or P is None:
            continue
        if not np.isfinite(T0) or not np.isfinite(P):
            continue
        if P == 0:
            continue

        T0_sig = r.get("T0_unc_days", 0) or 0
        P_sig = r.get("P_unc_days", 0) or 0

        # ✅ NEW: bounded epoch calculation
        N_start = int(np.ceil((start.tdb.jd - T0) / P))
        N_end   = int(np.floor((end.tdb.jd - T0) / P))

        # safety guard
        if N_end - N_start > 200:
            continue

        for N in range(N_start, N_end + 1):
            tmid = T0 + N * P

            sigma = propagate_uncertainty(T0, P, T0_sig, P_sig, tmid) * 1440

            events.append({
                # Event-level fields
                "name": r.get("name"),
                "Tmid_utc": Time(tmid, format="jd", scale="tdb").utc.isot,
                "pred_sigma_min": sigma,
                "time_since_last_obs_days": compute_time_since_last_obs(r.get("last_obs_jd")),

                # ✅ Add (optional but recommended)
                "T0": T0,
                "P": P,
                "epoch": N,

                # Core observing fields
                "duration_hours": r.get("duration_hours"),
                "mag_V": r.get("mag_V"),
                "depth_mmag": r.get("depth_mmag"),
                "current_oc_min": r.get("current_oc_min"),
                "min_telescope_inches": r.get("min_telescope_inches"),
                "ra": r.get("ra"),
                "dec": r.get("dec"),

                # Inherited metadata needed downstream for scoring
                "exoclock_priority": r.get("exoclock_priority"),
                "recent_activity_flag": r.get("recent_activity_flag"),
                "events_per_month": r.get("events_per_month"),
                "network_needed": r.get("network_needed"),
                "campaign_flag": r.get("campaign_flag"),
                "ttv_flag": r.get("ttv_flag", 0),
                "snr_proxy": r.get("snr_proxy"),
                "last_obs_jd": r.get("last_obs_jd"),
                
            })

    return pd.DataFrame(events)
