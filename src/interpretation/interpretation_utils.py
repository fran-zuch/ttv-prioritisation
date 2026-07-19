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
        if pd.isna(p): return "The visibility is unknown"
        if p > 0.8: return "There is excellent visibility"
        elif p > 0.5: return "There is mmoderate visibility"
        elif p > 0.3: return "There is going to be limited visibility"
        else: return "The visibility is poor"

    # Ephemeris
    def interpret_ephemeris(r):

        sigma = r.get("pred_sigma_min")
        days = r.get("time_since_last_obs_days")
    
        if pd.isna(sigma):
            return (
                "Insufficient information is available to assess "
                "ephemeris maintenance priority."
            )
    
        if sigma > 15:
            return (
                f"Predicted transit timing uncertainty has grown to "
                f"approximately {sigma:.1f} minutes, indicating that "
                f"additional observations would improve ephemeris precision."
            )
    
        if pd.notna(days) and days > 365:
            return (
                f"The ephemeris remains relatively well constrained "
                f"({sigma:.1f} minute uncertainty), but the target has not "
                f"been observed recently and would benefit from maintenance "
                f"observations."
            )
    
        return (
            f"The ephemeris is currently well constrained with an estimated "
            f"timing uncertainty of approximately {sigma:.1f} minutes."
        )
        

    def interpret_science(r):
        priority = str(r.get("exoclock_priority", "")).lower()
        n = pd.to_numeric(r.get("n_obs_recent",0), errors="coerce")
        
        if pd.isna(n): n = 0
        n = int(n)

        # Priority explanation
        priority_text = {
            "alert": "This is an ExoClock alert target",
            "high": "This target has a high ExoClock priority",
            "medium": "This target has a medium ExoClock priority",
            "low": "This target has a low ExoClock priority"
        }.get(priority, "This is an uncategorised target")
    
        # Monitoring explanation
        if n == 0:
            monitoring = "there have been no observations in the last years"
        elif n <= 2:
            monitoring = f"{n} observations recorded in the last year"
        elif n <= 5:
            monitoring = f"{n} observations in the last year (moderately monitored)"
        else:
            monitoring = f"{n} observations in the last year (well monitored)"
    
        return f"{priority_text}; {monitoring}"
    
    # General Sore interpretation
    def interpret_score(r):
        p = r.get('final_score_pct')
        if pd.isna(p): return "This score is unavailable"
        if p > 0.8: return "This is a top priority target"
        elif p > 0.6: return "This is a high priority target"
        elif p > 0.4: return "This is a moderate priority target"
        else: return "This is a lower priority target"

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
            parts.append("For this target, multi-site coordination is recommended.")

        if r.get('campaign_flag'):
            parts.append("This target has been - or currently is - part of an active campaign.")

        obs = r.get('obs_frac')
        if obs is not None and np.isfinite(obs) and obs < 0.5:
            parts.append("This target has only partial visibility.")

        if not parts:
            return "There is no special coordination required."

        return ".join(parts)

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
