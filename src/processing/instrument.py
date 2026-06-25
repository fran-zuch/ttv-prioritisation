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

# ============================================================
# NEW: Instrument feasibility (aperture-based)
# ============================================================

def estimate_required_aperture(mag_V, depth_mmag):
    """
    Approximate required telescope aperture (inches).
    
    Heuristic:
    - fainter stars → larger aperture
    - shallower transits → larger aperture
    """
    if mag_V is None or depth_mmag is None:
        return 40.0  # treat as difficult
    
    depth = max(depth_mmag / 1000.0, 1e-4)

    mag_term = 10 ** (0.2 * (mag_V - 10))
    depth_term = 1.0 / depth

    aperture = 4.0 * mag_term * depth_term

    return np.clip(aperture, 4.0, 40.0)

def add_instrument_constraints(df, telescope_aperture=24.0):
    df = df.copy()

    # Required aperture per target
    df["required_aperture"] = df.apply(
        lambda r: estimate_required_aperture(
            r.get("mag_V"),
            r.get("depth_mmag")
        ),
        axis=1
    )

    # Aperture ratio
    df["aperture_ratio"] = telescope_aperture / df["required_aperture"]

    # Feasibility flags
    df["instrument_flag"] = np.select(
        [
            df["aperture_ratio"] >= 1.0,
            df["aperture_ratio"] >= 0.75,
        ],
        [
            "OK",
            "Marginal"
        ],
        default="Not suitable"
    )

    df["instrument_feasible"] = df["aperture_ratio"] >= 0.75

    return df

def add_instrument_penalty(df, alpha=2.0):
    df = df.copy()

    def penalty(r):
        if r >= 1:
            return 1.0
        return np.exp(-alpha * (1 - r))

    df["instrument_penalty"] = df["aperture_ratio"].apply(penalty)

    return df
