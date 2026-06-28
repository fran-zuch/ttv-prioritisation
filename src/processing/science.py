import numpy as np

def compute_science_features(df):

    # --- Priority mapping ---
    if 'exoclock_priority' not in df.columns:
        df['exoclock_priority'] = None
        
    # --- Recent observation mapping ---
    if 'n_obs_recent' not in df.columns:
        df['n_obs_recent'] = 0
    else:
        df['n_obs_recent'] = df['n_obs_recent'].fillna(0)

    def map_priority(status):
        if status is None:
            return 0
        status = str(status).lower()
        mapping = {
            "alert": 5,
            "high": 4,
            "medium": 3,
            "low": 2
        }
        return mapping.get(status, 1)

    df['science_priority_numeric'] = df['exoclock_priority'].apply(map_priority)

    # --- Updated Priority Calculation using last observation timestamp AND recent observational numebers ---
    # --- Ensure inputs exist ---
    df['n_obs_recent'] = df.get('n_obs_recent', 0).fillna(0)
    days = df.get('time_since_last_obs_days')

    # --- Observation scarcity (fewer obs = higher need) ---
    df['obs_density_score'] = 1 / (1 + df['n_obs_recent'])

    # --- Time-based recency (older = more valuable) ---
    def recency_weight(t):
        if t is None or not np.isfinite(t):
            return 1.0
        return np.clip(t / 1000, 0, 1)

    df['time_recency_score'] = df['time_since_last_obs_days'].apply(recency_weight)

    # --- Combined science recency ---
    df['science_recency_score'] = (
        0.6 * df['time_recency_score'] +
        0.4 * df['obs_density_score']
    )

    # --- Placeholder for recent scientific paper mention, that still needs to be explored


    return df
