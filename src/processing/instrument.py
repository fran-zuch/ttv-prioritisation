"""
Instrument feasibility and aperture modelling.

This module provides:
- A physically motivated aperture model
- Instrument feasibility classification
- Scoring penalty for marginal/unobservable targets

The model is calibrated for small-to-medium telescopes such as
PIRATE Mk 4.5 (24-inch aperture, CCD-based photometry).

ExoClock's `min_telescope_inches` is preserved for comparison but
NOT used directly in scoring to maintain model transparency.
"""

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Difficulty heuristic (optional / legacy)
# -----------------------------------------------------------------------------

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

        # Long transits slightly harder to fully cover
        if duration is not None and np.isfinite(duration) and duration > 3:
            score -= 1

        if telescope == "PIRATE":
            if mag > 13:
                score -= 1
            if depth < 2:
                score -= 1

        return max(0, score)

    df['instrument_difficulty'] = df.apply(instrument_difficulty, axis=1)

    max_score = 6
    df['instrument_difficulty_norm'] = np.clip(
        df['instrument_difficulty'] / max_score, 0, 1
    )

    return df


# -----------------------------------------------------------------------------
# Physically motivated aperture model
# -----------------------------------------------------------------------------

def estimate_required_aperture(mag_V, depth_mmag, duration_hours=None):
    """
    Estimate minimum telescope aperture (inches) required
    to detect a transit with sufficient signal-to-noise.

    Model components:
    - Stellar brightness scaling (flux ~ 10^-0.4 mag)
    - Transit depth scaling (detectability ~ depth^-0.5)
    - Duration scaling (shorter transits are harder)

    Calibrated for ~0.5–1.0 m class telescopes (e.g. PIRATE Mk 4.5)
    """

    if (
        mag_V is None or depth_mmag is None
        or not np.isfinite(mag_V)
        or not np.isfinite(depth_mmag)
    ):
        return np.nan

    if depth_mmag <= 0:
        return np.nan

    # Brightness scaling (relative to V=10)
    mag_term = 10 ** (0.2 * (mag_V - 10))

    # Transit detectability scaling
    depth_term = np.sqrt(10.0 / depth_mmag)

    # Duration scaling (shorter = harder)
    if duration_hours is not None and np.isfinite(duration_hours):
        duration_term = np.sqrt(3.0 / duration_hours)
    else:
        duration_term = 1.0

    # Calibration constant (empirical tuning to PIRATE-class performance)
    aperture = 5.0 * mag_term * depth_term * duration_term

    return np.clip(aperture, 4.0, 50.0)


# -----------------------------------------------------------------------------
# Instrument constraints
# -----------------------------------------------------------------------------

def add_instrument_constraints(df, telescope_aperture=24.0):
    """
    Adds instrument feasibility metrics based on required aperture.

    Parameters
    ----------
    telescope_aperture : float
        Telescope diameter in inches (default = PIRATE Mk 4.5, 24")
    """

    df = df.copy()

    # ✅ Preserve ExoClock baseline (important for validation)   
    df["aperture_exoclock"] = pd.to_numeric(
        df.get("min_telescope_inches"),
        errors="coerce"
    )


    # ✅ Compute required aperture (your model)
    df["required_aperture"] = df.apply(
        lambda r: estimate_required_aperture(
            r.get("mag_V"),
            r.get("depth_mmag"),
            r.get("duration_hours")
        ),
        axis=1
    )

    # ✅ Ratio definition (CORRECT orientation)
    df["aperture_ratio"] = df["required_aperture"] / telescope_aperture

    df.loc[~np.isfinite(df["aperture_ratio"]), "aperture_ratio"] = np.nan

    # ✅ Feasibility classification
    df["instrument_flag"] = np.select(
        [
            df["required_aperture"].isna(),
            df["aperture_ratio"] <= 1.0,
            df["aperture_ratio"] <= 1.3,
        ],
        [
            "Unknown",
            "OK",
            "Marginal"
        ],
        default="Not suitable"
    )

    df["instrument_feasible"] = df["instrument_flag"].isin(["OK", "Marginal"])

    # ✅ Optional validation vs ExoClock
    df["aperture_consistency"] = (
        df["required_aperture"] / df["aperture_exoclock"]
    )

    return df


# -----------------------------------------------------------------------------
# Scoring penalty
# -----------------------------------------------------------------------------

def add_instrument_penalty(df, alpha=2.0):
    """
    Converts aperture feasibility into a smooth penalty function.
    """

    df = df.copy()

    def penalty(r):
        if r is None or not np.isfinite(r):
            return 1.0

        if r <= 1:
            return 1.0

        return np.exp(-alpha * (r - 1))

    df["instrument_penalty"] = df["aperture_ratio"].apply(penalty)

    return df
