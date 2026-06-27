import numpy as np

def compute_instrument_features(df, telescope="PIRATE"):

    def instrument_difficulty(r):
        mag = r.get('mag_V')
        depth = r.get('depth_mmag')
        duration = r.get('duration_hours')

        if (
            mag is None or depth is None
            or not np.isfinite(mag)
            or not np.isfinite(depth)
        ):
            return 0

        score = 0

        if mag < 10:
            score += 3
        elif mag < 12:
            score += 2
        elif mag < 13:
            score += 1

        if depth > 10:
            score += 3
        elif depth > 5:
            score += 2
        elif depth > 2:
            score += 1

        if duration is not None and not np.isnan(duration) and duration > 3:
            score -= 1

        if telescope == "PIRATE":
            if mag > 13:
                score -= 1
            if depth < 2:
                score -= 1

        return max(0, score)

    df['instrument_difficulty'] = df.apply(instrument_difficulty, axis=1)
    
    max_score = 6
    df['instrument_difficulty_norm'] = np.clip(df['instrument_difficulty'] / max_score, 0, 1)

    return df


def estimate_required_aperture(mag_V, depth_mmag):
    if (
        mag_V is None or depth_mmag is None
        or not np.isfinite(mag_V)
        or not np.isfinite(depth_mmag)
    ):
        return np.nan


    if depth_mmag <= 0:
        return np.nan

    mag_term = 10 ** (0.2 * (mag_V - 10))
    depth_term = np.sqrt(10.0 / depth_mmag)

    aperture = 4.5 * mag_term * depth_term

    return np.clip(aperture, 4.0, 40.0)


def add_instrument_constraints(df, telescope_aperture=24.0):
    df = df.copy()

    df["required_aperture"] = df.apply(
        lambda r: estimate_required_aperture(
            r.get("mag_V"),
            r.get("depth_mmag")
        ),
        axis=1
    )

    df["aperture_ratio"] = telescope_aperture / df["required_aperture"]
    df.loc[~np.isfinite(df["aperture_ratio"]), "aperture_ratio"] = np.nan

    df["instrument_flag"] = np.select(
        [
            df["required_aperture"].isna(),
            df["aperture_ratio"] >= 1.0,
            df["aperture_ratio"] >= 0.75,
        ],
        [
            "Unknown",
            "OK",
            "Marginal"
        ],
        default="Not suitable"
    )

    df["instrument_feasible"] = df["instrument_flag"].isin(["OK", "Marginal"])

    return df


def add_instrument_penalty(df, alpha=2.0):
    df = df.copy()

    def penalty(r):
        if r is None or not np.isfinite(r):
            return 1.0
        if r >= 1:
            return 1.0
        return np.exp(-alpha * (1 - r))

    df["instrument_penalty"] = df["aperture_ratio"].apply(penalty)

    return df
