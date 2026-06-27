import numpy as np


# -----------------------------------------------------------------------------
# Helper: safe bin from normalised score (0–1 → 1–5)
# -----------------------------------------------------------------------------

def bin_from_norm(x):
    """
    Converts a normalised score (0–1) to integer bin (1–5).
    """
    if x is None or not np.isfinite(x):
        return 1
    return int(np.clip(np.ceil(x * 5), 1, 5))


# -----------------------------------------------------------------------------
# Ephemeris uncertainty (pred_sigma_min in minutes)
# -----------------------------------------------------------------------------

def bin_ephemeris(x):
    """
    Lower uncertainty = better (higher bin).
    """
    if x is None or not np.isfinite(x):
        return 1
    return (
        5 if x < 2 else
        4 if x < 5 else
        3 if x < 10 else
        2 if x < 15 else
        1
    )


# -----------------------------------------------------------------------------
# Observability fraction (obs_frac: 0–1)
# -----------------------------------------------------------------------------

def bin_observability(x):
    """
    Fraction of usable observing window.
    """
    if x is None or not np.isfinite(x):
        return 1
    return (
        1 if x < 0.25 else
        2 if x < 0.5 else
        3 if x < 0.75 else
        4 if x < 0.95 else
        5
    )


# -----------------------------------------------------------------------------
# TTV amplitude (minutes) — Raw values
# If later change to ttv_signal_strenght then this code:
#
# def bin_ttv(x):
#   if x is None or not np.isfinite(x):
#       return 1
#   return int(np.ceil(x * 5))
# -----------------------------------------------------------------------------

def bin_ttv(x):
    """
    Based on O-C amplitude in minutes.
    """
    if x is None or not np.isfinite(x):
        return 1
    return (
        1 if x < 5 else
        2 if x < 10 else
        3 if x < 15 else
        4 if x < 20 else
        5
    )


# -----------------------------------------------------------------------------
# Instrument difficulty (use NORMALISED score)
# -----------------------------------------------------------------------------

def bin_instrument(x):
    """
    Uses instrument_difficulty_norm (0–1).
    """
    return bin_from_norm(x)


# -----------------------------------------------------------------------------
# Synergy / campaign intensity (use NORMALISED score)
# -----------------------------------------------------------------------------

def bin_synergy(x):
    """
    Uses campaign_intensity_norm (0–1).
    """
    return bin_from_norm(x)
