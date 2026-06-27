def compute_science_features(df):

    # ✅ Ensure column exists safely
    if 'exoclock_priority' not in df.columns:
        df['exoclock_priority'] = None

    # ✅ Map ExoClock priority → numeric
    def map_priority(status):
        if status == "alert":
            return 5
         elif status == "high":
            return 4            
        elif status == "medium":
            return 3
        elif status == "low":
            return 1
        return 2  # default / unknown

    df['science_priority_numeric'] = df['exoclock_priority'].apply(map_priority)

    # ✅ Ensure literature flag exists
    if 'recent_activity_flag' not in df.columns:
        df['recent_activity_flag'] = False

    df['recent_activity_flag'] = df['recent_activity_flag'].astype(bool)

    return df
