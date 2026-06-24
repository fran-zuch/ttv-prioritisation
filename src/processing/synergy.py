from scoring.bins import bin_synergy

def compute_s6_synergy(df):

    def synergy_score(r):

        events = r.get('events_per_month')
        network = r.get('network_needed', False)
        campaign = r.get('campaign_flag', False)

        score = bin_synergy(events, network)

        if campaign:
            score += 1

        if events and events > 8:
            score += 1

        return min(score, 5)

    df['S6'] = df.apply(synergy_score, axis=1)
    return df
