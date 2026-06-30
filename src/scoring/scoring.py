import pandas as pd
from .bins import *


def compute_scores(df):

    # --- S1: Ephemeris urgency ---
    def urgency(r):
        s = r['pred_sigma_min']
        t = r['time_since_last_obs_days']

        if not pd.notna(s):
            return 0
    
        # smoother scaling than hard cap
        time_factor = 1 + np.log1p(t / 100)
    
        return s * time_factor


    df['S1'] = df.apply(urgency, axis=1).apply(bin_ephemeris)

    # --- S2: TTV ---
    df['S2'] = df['ttv_amplitude_min'].apply(bin_ttv)
    df.loc[df['ttv_flag'] == 1, 'S2'] += 1
    df['S2'] = df['S2'].clip(upper=5)

    # --- S3: Instrument ---
    df['S3'] = df['instrument_difficulty_norm'].apply(bin_instrument)

    # --- S4: Observability ---
    df['S4'] = df['obs_frac'].apply(bin_observability)

    # --- S5: Science (priority + recency) ---
    df['S5'] = (df['science_priority_numeric'] + df['science_recency_score'])
    df['S5'] = df['S5'].clip(upper=5)

    # --- S6: Synergy ---
    df['S6'] = df['campaign_intensity_norm'].apply(bin_synergy)
    df.loc[df['campaign_flag'] == True, 'S6'] += 1
    df['S6'] = df['S6'].clip(upper=5)

    # --- Weighted score ---
    df['base_score'] = (
        0.25 * df['S1'] +
        0.20 * df['S2'] +
        0.15 * df['S3'] +
        0.15 * df['S4'] +
        0.15 * df['S5'] +
        0.10 * df['S6']
    )

    # --- Apply feasibility penalty ---
    df['final_score'] = df['base_score'] * df['instrument_penalty']

    # --- Group by feasibility ---
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
