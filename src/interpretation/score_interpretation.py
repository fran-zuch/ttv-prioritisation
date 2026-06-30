import pandas as pd
import numpy as np

def build_dynamic_summary(df):
    df = df.copy()

    def make_summary(r):
        parts = []

        # --- Priority ---
        priority = r.get('score_interpretation')
        if priority:
            parts.append(f"{priority}")

        # --- Ephemeris ---
        ephem = r.get('ephemeris_interpretation')
        if ephem:
            parts.append(ephem)

        # --- Visibility ---
        obs = r.get('obs_interpretation')
        if obs:
            parts.append(obs)

        # --- TTV ---
        ttv = r.get('ttv_significance_class')
        if ttv and ttv != "none":
            parts.append(f"TTV signal {ttv}")

        # --- Science ---
        science = r.get('science_interpretation')
        if science:
            parts.append(science)

        # --- Coordination ---
        if r.get('campaign_flag'):
            parts.append("part of an active campaign")

        if r.get('network_needed'):
            parts.append("requires multi-site coordination")

        # --- Fallback ---
        if not parts:
            return "No strong prioritisation signals"

        return ". ".join(parts) + "."

    df['summary_text'] = df.apply(make_summary, axis=1)

    return df
    
def add_flag_labels(df):
    def flags(r):
        labels = []
        if r['campaign_flag']:
            labels.append("📡 Campaign")
        if r['network_needed']:
            labels.append("🌍 Network")
        return ", ".join(labels) if labels else "—"

    df['flag_labels'] = df.apply(flags, axis=1)
    return df


