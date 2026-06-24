def compute_science_features(df):

    # ✅ Map ExoClock priority → numeric
    def map_priority(status):
        if status == "high":
            return 5
        elif status == "medium":
            return 3
        elif status == "low":
            return 1
        return 2  # unknown / default

    df['science_priority_numeric'] = df.get('exoclock_priority', None).apply(map_priority)

    # ✅ Literature / activity flag (pre-computed externally)
    if 'recent_activity_flag' not in df.columns:
        df['recent_activity_flag'] = False

    return df
