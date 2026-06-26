import pandas as pd
from .bins import *

def compute_scores(df):

    # ✅ S1 — Ephemeris urgency
    def urgency(r):
        s = r['pred_sigma_min']
        t = r['time_since_last_obs_days']
        return s if t is None else s * (1 + (t / 100))

    df['S1'] = df.apply(urgency, axis=1).apply(bin_ephemeris)

    # ✅ S2 — TTV scoring (NEW clean implementation)
    df['S2'] = df['ttv_amplitude_min'].apply(bin_ttv)

    # ✅ Boost if ExoClock flagged
    df.loc[df['ttv_flag_numeric'] == 1, 'S2'] += 1

    df['S2'] = df['S2'].clip(upper=5)
    
    # ✅ S3 — Instrument feasibility
    df['S3'] = df['instrument_difficulty'].apply(bin_instrument)

    # ✅ S4 — Observability
    df['S4'] = df['obs_frac'].apply(bin_observability)

    # ✅ S5 — Science score
    df['S5'] = df['science_priority_numeric']
    
    # ✅ Boost for recent research / activity
    df.loc[df['recent_activity_flag'] == True, 'S5'] += 1
    
    df['S5'] = df['S5'].clip(upper=5)

    # ✅ S6 — Synergy / campaign need
    df['S6'] = df['campaign_intensity'].apply(bin_synergy)

    # ✅ Optional: slight boost for explicit campaigns
    df.loc[df['campaign_flag'] == True, 'S6'] += 1
    
    df['S6'] = df['S6'].clip(upper=5)

    # ✅ Final weighted score
    df['base_score'] = (
        0.25 * df['S1'] +
        0.20 * df['S2'] +
        0.15 * df['S3'] +
        0.15 * df['S4'] +
        0.15 * df['S5'] +
        0.10 * df['S6']
    )
    
    # ✅ Apply instrument feasibility penalty
    df['final_score'] = df['base_score'] * df['instrument_penalty']

   # ✅ Group by feasibility first (optional but recommended)
    priority_map = {
        "OK": 0,
        "Marginal": 1,
        "Unknown": 2,
        "Not suitable": 3
    }

    
    df["priority_group"] = df["instrument_flag"].map(priority_map)
    
    return df.sort_values(
        ["priority_group", "final_score"],
        ascending=[True, False]
    )
