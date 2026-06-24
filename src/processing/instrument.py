import numpy as np

def compute_instrument_features(df, telescope="PIRATE"):

    def instrument_difficulty(r):

        mag = r.get('mag_V')
        depth = r.get('depth_mmag')
        duration = r.get('duration_hr')

        # ✅ Handle missing data
        if mag is None or depth is None:
            return 0  # lowest quality

        score = 0

        # ✅ Magnitude (brightness)
        if mag < 10:
            score += 3
        elif mag < 12:
            score += 2
        elif mag < 13:
            score += 1

        # ✅ Transit depth (signal strength)
        if depth > 10:
            score += 3
        elif depth > 5:
            score += 2
        elif depth > 2:
            score += 1

        # ✅ Duration (very long → harder to cover)
        if duration and duration > 3:
            score -= 1

        # ✅ Telescope-specific adjustment
        if telescope == "PIRATE":
            if mag > 13:
                score -= 1
            if depth < 2:
                score -= 1

        return max(0, score)

    df['instrument_difficulty'] = df.apply(instrument_difficulty, axis=1)

    # ✅ Optional normalised version (useful for plots)
    df['instrument_difficulty_norm'] = np.clip(df['instrument_difficulty'] / 6, 0, 1)

    return df
