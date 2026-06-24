import pandas as pd
from .bins import *
from processing.ttv import compute_s2_ttv
from processing.instrument import compute_s3_instrument
from processing.science import compute_s5_science
from processing.synergy import compute_s6_synergy

def compute_scores(df):

    # ✅ S1 (existing logic)
    def urgency(r):
        s = r['pred_sigma_min']
        t = r['time_since_last_obs_days']
        return s if t is None else s * (1 + (t / 100))

    df['S1'] = df.apply(urgency, axis=1).apply(bin_ephemeris)

    # ✅ S4 (existing)
    df['S4'] = df['obs_frac'].apply(bin_observability)

    # ✅ NEW components
    df = compute_s2_ttv(df)
    df = compute_s3_instrument(df)
    df = compute_s5_science(df)
    df = compute_s6_synergy(df)

    # ✅ FINAL weighted score (planner.yaml)
    df['final_score'] = (
        0.25 * df['S1'] +
        0.20 * df['S2'] +
        0.15 * df['S3'] +
        0.15 * df['S4'] +
        0.15 * df['S5'] +
        0.10 * df['S6']
    )

    return df.sort_values('final_score', ascending=False)

