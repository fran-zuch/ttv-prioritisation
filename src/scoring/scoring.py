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

    # ✅ S4 — Observability
    df['S4'] = df['obs_frac'].apply(bin_observability)

    # ✅ S5 — Science score
    df['S5'] = df['science_priority_numeric']
    
    # ✅ Boost for recent research / activity
    df.loc[df['recent_activity_flag'] == True, 'S5'] += 1
    
    df['S5'] = df['S5'].clip(upper=5)

    # ✅ Final weighted score
    df['final_score'] = (
        0.25 * df['S1'] +
        0.20 * df['S2'] +
        0.15 * df['S3'] +
        0.15 * df['S4'] +
        0.15 * df['S5'] +
        0.10 * df['S6']
    )

    return df.sort_values('final_score', ascending=False)
