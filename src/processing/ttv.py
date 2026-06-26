import numpy as np
import pandas as pd

def compute_ttv_features(df):
    current_oc = pd.to_numeric(df.get("current_oc_min", 0), errors="coerce").fillna(0)
    df["ttv_amplitude_min"] = current_oc.abs()

    if "ttv_flag" in df.columns:
        df["ttv_flag_numeric"] = pd.to_numeric(df["ttv_flag"], errors="coerce").fillna(0).astype(int)
    else:
        df["ttv_flag_numeric"] = 0

    df["ttv_signal_strength"] = np.clip(df["ttv_amplitude_min"] / 20, 0, 1)

    return df
