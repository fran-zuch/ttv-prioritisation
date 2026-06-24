import numpy as np

def compute_synergy_features(df):

    # ✅ Ensure columns exist safely
    if 'events_per_month' not in df.columns:
        df['events_per_month'] = 0

    if 'network_needed' not in df.columns:
        df['network_needed'] = False
    else:
        df['network_needed'] = df['network_needed'].astype(bool)

    if 'campaign_flag' not in df.columns:
        df['campaign_flag'] = False
    else:
        df['campaign_flag'] = df['campaign_flag'].astype(bool)

    # ✅ Derived metric: coordination intensity
    def campaign_intensity(r):

        events = r.get('events_per_month') or 0
        network = r.get('network_needed', False)
        campaign = r.get('campaign_flag', False)

        score = 0

        # ✅ Event frequency (improved gradient)
        if events > 10:
            score += 3
        elif events > 7:
            score += 2
        elif events > 4:
            score += 1

        # ✅ Network coordination needed (major driver)
        if network:
            score += 2

        # ✅ Explicit campaign (strong signal)
        if campaign:
            score += 2

        # ✅ OPTIONAL (future): visibility-based coordination need
        # if r.get('visible_fraction', 1.0) < 0.5:
        #     score += 1

        return score

    df['campaign_intensity'] = df.apply(campaign_intensity, axis=1)

    # ✅ Normalised version (useful for plots)
    df['campaign_intensity_norm'] = np.clip(df['campaign_intensity'] / 5, 0, 1)

    return df
