import numpy as np

def compute_synergy_features(df):

    # ✅ Ensure fields exist
    df['events_per_month'] = df.get('events_per_month', 0)
    df['network_needed'] = df.get('network_needed', False).astype(bool)

    # ✅ Campaign indicator (explicit flag if provided)
    df['campaign_flag'] = df.get('campaign_flag', False).astype(bool)

    # ✅ Derived: how "intensive" the coordination need is
    # (higher = more benefit from multi-observer campaign)
    def campaign_intensity(r):

        events = r.get('events_per_month') or 0
        network = r.get('network_needed', False)
        campaign = r.get('campaign_flag', False)

        score = 0

        # Frequent events → coordination more useful
        if events > 8:
            score += 2
        elif events > 5:
            score += 1

        # Cross-longitude / network needed
        if network:
            score += 2

        # Explicit campaign flag
        if campaign:
            score += 2

        return score

    df['campaign_intensity'] = df.apply(campaign_intensity, axis=1)

    # ✅ Normalised version (optional but useful for plotting)
    df['campaign_intensity_norm'] = np.clip(df['campaign_intensity'] / 5, 0, 1)

    return df
