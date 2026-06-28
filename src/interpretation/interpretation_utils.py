import numpy as np
import pandas as pd


# ==========================================================
# 1. Dynamic interpretation
# ==========================================================
def add_dynamic_interpretation(df):
    df = df.copy()

    # Percentiles
    df['obs_frac_pct'] = df['obs_frac'].rank(pct=True)
    df['final_score_pct'] = df['final_score'].rank(pct=True)

    # Observability
    def interpret_obs(r):
        p = r.get('obs_frac_pct')
        if pd.isna(p): return "visibility unknown"
        if p > 0.8: return "excellent visibility"
        elif p > 0.5: return "moderate visibility"
        elif p > 0.3: return "limited visibility"
        else: return "poor visibility"

    # Ephemeris
    def interpret_ephemeris(r):
        t = r.get('time_since_last_obs_days')
        if t is None or not np.isfinite(t):
            return "no prior observations"
        if t > 3000: return "ephemeris likely degraded"
        elif t > 1000: return "ephemeris uncertainty increasing"
        elif t > 100: return "moderately recent observations"
        else: return "recently observed"

    # Score
    def interpret_score(r):
        p = r.get('final_score_pct')
        if pd.isna(p): return "score unavailable"
        if p > 0.8: return "top priority target"
        elif p > 0.6: return "high priority target"
        elif p > 0.4: return "moderate priority target"
        else: return "lower priority target"

    df['obs_interpretation'] = df.apply(interpret_obs, axis=1)
    df['ephemeris_interpretation'] = df.apply(interpret_ephemeris, axis=1)
    df['score_interpretation'] = df.apply(interpret_score, axis=1)

    return df


# ==========================================================
# 2. Synergy explanation
# ==========================================================
def add_synergy_explanations(df):
    df = df.copy()

    def explain(r):
        parts = []

        if r.get('network_needed'):
            parts.append("multi-site coordination required")

        if r.get('campaign_flag'):
            parts.append("active campaign target")

        obs = r.get('obs_frac')
        if obs is not None and np.isfinite(obs) and obs < 0.5:
            parts.append("partial visibility")

        if not parts:
            return "no special coordination required"

        return "; ".join(parts)

    df['synergy_explanation'] = df.apply(explain, axis=1)
    return df


# ==========================================================
# 3. Recency labels
# ==========================================================
def add_recency_labels(df):
    df = df.copy()

    def format_days(days):
        if days is None or not np.isfinite(days):
            return "no recorded observation"
        if days < 1: return "observed today"
        elif days < 7: return f"{int(days)} days ago"
        elif days < 30: return f"{int(days/7)} weeks ago"
        elif days < 365: return f"{int(days/30)} months ago"
        else: return f"{int(days/365)} years ago"

    df['recency_text'] = df['time_since_last_obs_days'].apply(format_days)
    return df


# ==========================================================
# 4. Score breakdown
# ==========================================================
def build_score_breakdown(df):
    df = df.copy()

    def panel(r):
        return {
            "priority": r.get('score_interpretation'),
            "score": r.get('final_score'),
            "visibility": r.get('obs_interpretation'),
            "ephemeris": r.get('ephemeris_interpretation'),
            "last_obs": r.get('recency_text'),
            "coordination": r.get('synergy_explanation'),
            "network": bool(r.get('network_needed')),
            "campaign": bool(r.get('campaign_flag')),
        }

    df['score_breakdown'] = df.apply(panel, axis=1)
    return df
