import numpy as np
import pandas as pd


def compute_ttv_features(df):

    current_oc = pd.to_numeric(
        df.get("current_oc_min"),
        errors="coerce"
    )

    # --- Core amplitude ---
    df["ttv_amplitude_min"] = current_oc.abs()
    df["ttv_amplitude_min"] = df["ttv_amplitude_min"].fillna(0)

    # --- Derived TTV flag (inferred, not ExoClock)
    df["ttv_flag"] = (
        df["ttv_amplitude_min"] > 10
    ).astype(int)

    # --- Continuous signal strength
    df["ttv_signal_strength"] = np.clip(
        df["ttv_amplitude_min"] / 20, 0, 1)

    # --- Optional classification (good for explainability)
    df["ttv_significance_class"] = np.select(
        [
            df["ttv_amplitude_min"] > 20,
            df["ttv_amplitude_min"] > 10,
            df["ttv_amplitude_min"] > 5
        ],
        ["strong", "moderate", "weak"],
        default="none"
    )

    return df
