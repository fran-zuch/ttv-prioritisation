from .bins import bin_science

def compute_s5_science(df):

    def science_score(r):

        base = bin_science(r.get('exoclock_priority'))

        # ✅ literature / activity boost
        if r.get('recent_activity_flag'):
            base += 1

        return min(base, 5)

    df['S5'] = df.apply(science_score, axis=1)
    return df
