import numpy as np

def compute_science_features(df):

    if 'exoclock_priority' not in df.columns:
        df['exoclock_priority'] = None

    def map_priority(status):

        if pd.isna(status):
            return 0

        status = str(status).lower()

        mapping = {
            "alert": 5,
            "high": 4,
            "medium": 3,
            "low": 2
        }

        return mapping.get(status, 1)

    df['science_priority_numeric'] = (
        df['exoclock_priority']
        .apply(map_priority)
    )

    if "n_obs_recent" not in df.columns:
        df["n_obs_recent"] = 0

    df["n_obs_recent"] = (
        pd.to_numeric(
            df["n_obs_recent"],
            errors="coerce"
        )
        .fillna(0)
    )

    # Targets with fewer recent observations receive higher science priority.
    df["science_recency_score"] = (
        1 / (1 + df["n_obs_recent"])
    )

    # Still to come is a check around recent Scientific mentioning

    return df
