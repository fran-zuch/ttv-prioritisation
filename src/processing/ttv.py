import numpy as np

def compute_ttv_features(df):

    # ✅ Continuous TTV amplitude (minutes)
    df['ttv_amplitude_min'] = df.get('current_oc_min', 0).abs()

    # ✅ ExoClock TTV flag (if present)
    if 'ttv_flag' in df.columns:
        df['ttv_flag_numeric'] = df['ttv_flag'].astype(int)
    else:
        df['ttv_flag_numeric'] = 0

    # ✅ Optional: normalised TTV signal (for debugging / later use)
    df['ttv_signal_strength'] = np.clip(df['ttv_amplitude_min'] / 20, 0, 1)

    return df
