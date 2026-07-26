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

    # Instrument explanation
    def interpret_instrument(r):
        mag = r.get("mag_V")
        depth = r.get("depth_mmag")
        aperture = r.get("required_aperture")
        flag = r.get("instrument_flag", "Unknown")
    
        if pd.isna(mag) or pd.isna(depth):
            return "Instrument suitability could not be assessed."
    
        # Brightness assessment
        if mag < 11:
            mag_text = (
                f"The target is bright (V={mag:.1f}), "
                "which supports high signal-to-noise photometry."
            )
        elif mag < 13:
            mag_text = (
                f"The target has moderate brightness (V={mag:.1f}), "
                "making precision photometry achievable with PIRATE."
            )
        else:
            mag_text = (
                f"The target is relatively faint (V={mag:.1f}), "
                "which may reduce photometric precision and require longer exposures."
            )
    
        # Transit depth assessment
        if depth >= 10:
            depth_text = (
                f"The transit depth is large ({depth:.1f} mmag), "
                "producing a strong observational signal."
            )
        elif depth >= 3:
            depth_text = (
                f"The transit depth is moderate ({depth:.1f} mmag), "
                "providing a detectable signal under good observing conditions."
            )
        else:
            depth_text = (
                f"The transit depth is shallow ({depth:.1f} mmag), "
                "requiring higher photometric precision for reliable detection."
            )
    
        return (
            f"{flag}. "
            f"{mag_text} "
            f"{depth_text} "
            f"Estimated minimum aperture requirement is "
            f"{aperture:.0f} inches."
        )

    # TTV explainer
    def interpret_ttv(r):
        amp = r.get("ttv_amplitude_min", 0)
    
        if amp > 20:
            return (
                f"Strong transit timing variation signal detected. "
                f"Current timing offset is approximately {amp:.1f} minutes."
            )
    
        elif amp > 10:
            return (
                f"Moderate transit timing variation signal detected. "
                f"Current timing offset is approximately {amp:.1f} minutes."
            )
    
        elif amp > 5:
            return (
                f"Weak transit timing variation signal detected. "
                f"Current timing offset is approximately {amp:.1f} minutes."
            )
    
        return (
            "No significant transit timing variation signal currently detected."
        )
    

    # Observability
    def interpret_obs(r):
        frac = r.get("obs_frac")
        max_alt = r.get("obs_max_alt")
        airmass = r.get("obs_mean_airmass")
    
        if pd.isna(frac):
            return "Observability could not be assessed."
    
        visible_pct = frac * 100
    
        # --- Visibility assessment ---
        if frac > 0.8:
            summary = (
                f"Excellent observability. Approximately "
                f"{visible_pct:.0f}% of the transit is observable.")
    
        elif frac > 0.5:
            summary = (
                f"Moderate observability. Approximately "
                f"{visible_pct:.0f}% of the transit is observable.")
    
        elif frac > 0.3:
            summary = (
                f"Limited observability. Approximately "
                f"{visible_pct:.0f}% of the transit is observable.")
    
        else:
            summary = (
                f"Poor observability. Only "
                f"{visible_pct:.0f}% of the transit is observable.")
    
        # --- Additional context ---
        details = []
    
        if pd.notna(max_alt):
    
            if max_alt >= 70:
    
                details.append(
                    f"Peak altitude reaches {max_alt:.0f}°, placing the target "
                    "high in the sky where atmospheric effects are minimal."
                )
    
            elif max_alt >= 50:
    
                details.append(
                    f"Peak altitude reaches {max_alt:.0f}°, meaning the target "
                    "rises well above the horizon and should provide good "
                    "observing conditions."
                )
    
            elif max_alt >= 30:
    
                details.append(
                    f"Peak altitude reaches {max_alt:.0f}°, providing adequate "
                    "visibility, although atmospheric effects will be greater "
                    "than for higher-altitude targets."
                )
    
            else:
    
                details.append(
                    f"Peak altitude reaches only {max_alt:.0f}°, so observations "
                    "may be affected by increased atmospheric extinction and "
                    "turbulence."
                )
    
        if pd.notna(airmass):
    
            if airmass < 1.5:
    
                details.append(
                    f"Average airmass is {airmass:.2f}, indicating excellent "
                    "observing conditions because the target is viewed through "
                    "relatively little atmosphere."
                )
    
            elif airmass < 2.0:
    
                details.append(
                    f"Average airmass is {airmass:.2f}, indicating good observing "
                    "conditions with only modest atmospheric attenuation."
                )
    
            elif airmass < 3.0:
    
                details.append(
                    f"Average airmass is {airmass:.2f}, suggesting moderate "
                    "atmospheric effects which may reduce photometric precision."
                )
    
            else:
    
                details.append(
                    f"Average airmass is {airmass:.2f}, indicating that the target "
                    "is observed through a large column of atmosphere, potentially "
                    "degrading data quality."
                )
    
        return summary + " " + " ".join(details)

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
        n = pd.to_numeric(r.get("n_obs_recent", 0), errors="coerce")
    
        p12 = pd.to_numeric(r.get("papers_last_12m", 0), errors="coerce")
        p36 = pd.to_numeric(r.get("papers_last_36m", 0), errors="coerce")
    
        latest_title = (str(r.get("latest_title", "")).strip())
    
        if pd.isna(n):
            n = 0
    
        if pd.isna(p12):
            p12 = 0
    
        if pd.isna(p36):
            p36 = 0
    
        # --------------------------------------------------
        # ExoClock Priority
        # --------------------------------------------------
    
        priority_text = {
            "alert":
                "This is an ExoClock alert target.",
            "high":
                "This target has a high ExoClock priority.",
            "medium":
                "This target has a medium ExoClock priority.",
            "low":
                "This target has a low ExoClock priority."
        }.get(
            priority,
            "This target is not currently assigned an ExoClock priority."
        )
    
        # --------------------------------------------------
        # Monitoring Activity
        # --------------------------------------------------
    
        if n == 0:
            monitoring = (
                "No recent transit observations have "
                "been reported.")
    
        elif n <= 2:    
            monitoring = (
                f"{n} recent transit observations "
                "have been recorded.")
    
        elif n <= 5:
            monitoring = (
                f"{n} recent observations indicate "
                "moderate monitoring coverage.")
    
        else:
            monitoring = (
                f"{n} recent observations indicate "
                "strong monitoring coverage.")
    
        # --------------------------------------------------
        # Literature Activity
        # --------------------------------------------------
    
        if p12 == 0 and p36 == 0:
            literature = (
                "No recent literature activity was identified.")
    
        elif p12 > 0:    
            literature = (
                f"{int(p12)} papers were identified "
                f"in the last 12 months and "
                f"{int(p36)} papers in the last "
                f"36 months.")
    
        else:
            literature = (
                f"No papers were identified in the "
                f"last 12 months, but "
                f"{int(p36)} publications were found "
                f"over the last 36 months.")
    
        # --------------------------------------------------
        # Latest Publication
        # --------------------------------------------------
    
        if latest_title:
            latest_pub = (
                f'Latest publication: "{latest_title}".')
        else:
            latest_pub = ""
        return (
            f"{priority_text} "
            f"{monitoring} "
            f"{literature} "
            f"{latest_pub}"
        ).strip()
    
    # General Sore interpretation
    def interpret_score(r):
        p = r.get('final_score_pct')
        if pd.isna(p): return "This score is unavailable"
        if p > 0.8: return "This is a top priority target"
        elif p > 0.6: return "This is a high priority target"
        elif p > 0.4: return "This is a moderate priority target"
        else: return "This is a lower priority target"

    df['TTV_interpretation'] = df.apply(interpret_ttv, axis=1)
    df['Instrument_interpretation'] = df.apply(interpret_instrument, axis=1)
    df['obs_interpretation'] = df.apply(interpret_obs, axis=1)
    df['ephemeris_interpretation'] = df.apply(interpret_ephemeris, axis=1)
    df['science_interpretation'] = df.apply(interpret_science,axis=1)
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
            parts.append("For this target, multi-site coordination is recommended.")

        if r.get('campaign_flag'):
            parts.append("This target has been - or currently is - part of an active campaign.")

        obs = r.get('obs_frac')
        if obs is not None and np.isfinite(obs) and obs < 0.5:
            parts.append("This target has only partial visibility.")

        if not parts:
            return "There is no special coordination required."

        return " ".join(parts)

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
