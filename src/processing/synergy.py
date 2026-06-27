import numpy as np


def compute_synergy_features(df):

    # --- Ensure inputs exist ---
    if 'events_per_month' not in df.columns:
        df['events_per_month'] = 0

    df['network_needed'] = df.get('network_needed', False)
    df['network_needed'] = df['network_needed'].fillna(False).astype(bool)

    df['campaign_flag'] = df.get('campaign_flag', False)
    df['campaign_flag'] = df['campaign_flag'].fillna(False).astype(bool)

    # --- Core scoring ---
    def campaign_intensity(r):

        events = r.get('events_per_month')
        if events is None or not np.isfinite(events):
            events = 0

        network = r.get('network_needed', False)
        campaign = r.get('campaign_flag', False)
        vis = r.get('obs_frac')

        score = 0

        # ✅ Event cadence (smooth scaling)
        score += np.clip(events / 10, 0, 1) * 3

        # ✅ Network coordination
        if network:
            score += 2

        # ✅ Explicit campaign
        if campaign:
            score += 2

        # ✅ Partial visibility → network value
        if vis is not None and np.isfinite(vis):
            if vis < 0.5:
                score += 1.5

        return score

    df['campaign_intensity'] = df.apply(campaign_intensity, axis=1)

    # ✅ Correct normalisation
    MAX_SCORE = 8.5   # updated (3 + 2 + 2 + 1.5)
    df['campaign_intensity_norm'] = np.clip(
        df['campaign_intensity'] / MAX_SCORE, 0, 1
    )

    return df
