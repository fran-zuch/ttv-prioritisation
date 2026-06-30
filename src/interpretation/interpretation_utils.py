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
        sigma = r.get("pred_sigma_min", 0)
        if pd.isna(sigma): return "ephemeris uncertainty unknown"
        if sigma > 30: return "high ephemeris uncertainty"
            elif sigma > 10:
                return "moderate ephemeris uncertainty"
        else:
            return "well constrained ephemeris"

    def interpret_science(r):
        priority = str(r.get("exoclock_priority", "")).lower()
        n = int(r.get("n_obs_recent", 0))

        # Priority explanation
        priority_text = {
            "alert": "ExoClock alert target",
            "high": "high ExoClock priority",
            "medium": "medium ExoClock priority",
            "low": "low ExoClock priority"
        }.get(priority, "uncategorised target")
    
        # Monitoring explanation
        if n == 0:
            monitoring = "no observations in the last year"
        elif n <= 2:
            monitoring = f"{n} observations in the last year"
        elif n <= 5:
            monitoring = f"{n} observations in the last year (moderately monitored)"
        else:
            monitoring = f"{n} observations in the last year (well monitored)"
    
        return f"{priority_text}; {monitoring}"
    
    # General Sore interpretation
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
    df['science_interpretation'] = df.apply(interpret_science,axis=1)

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
# 3. Score breakdown
# ==========================================================
def build_score_breakdown(df):
    df = df.copy()

    def panel(r):
        return {
            "priority": r.get('score_interpretation'),
            "score": r.get('final_score'),
            "visibility": r.get('obs_interpretation'),
            "ephemeris": r.get('ephemeris_interpretation'),
            "science": r.get('science_interpretation'),
            "coordination": r.get('synergy_explanation'),
            "network": bool(r.get('network_needed')),
            "campaign": bool(r.get('campaign_flag')),
        }

    df['score_breakdown'] = df.apply(panel, axis=1)
    return df
