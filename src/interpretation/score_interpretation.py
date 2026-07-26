import pandas as pd
import numpy as np

def build_dynamic_summary(df):

    df = df.copy()

    def clean_text(text):
        """
        Remove trailing full stops and whitespace so that
        the summary builder can safely join sentences.
        """

        if pd.isna(text):
            return ""

        text = str(text).strip()

        # remove trailing "." characters
        text = text.rstrip(". ")

        return text

    def make_summary(r):

        parts = []

        # --- Priority ---
        priority = clean_text(
            r.get('score_interpretation')
        )
        if priority:
            parts.append(priority)

        # --- Ephemeris ---
        ephem = clean_text(
            r.get('ephemeris_interpretation')
        )
        if ephem:
            parts.append(ephem)

        # --- Visibility ---
        obs = clean_text(
            r.get('obs_interpretation')
        )
        if obs:
            parts.append(obs)

        # --- TTV ---
        ttv = clean_text(
            r.get('TTV_interpretation')
        )
        if ttv:
            parts.append(ttv)

        # --- Science ---
        science = clean_text(
            r.get('science_interpretation')
        )
        if science:
            parts.append(science)

        # --- Coordination ---
        if r.get('campaign_flag'):
            parts.append("This target is part of an active campaign")

        if r.get('network_needed'):
            parts.append(
                "Multi-site coordination is recommended"
            )

        # --- Fallback ---
        if not parts:
            return "No strong prioritisation signals."

        return ". ".join(parts) + "."

    df['summary_text'] = (
        df.apply(make_summary, axis=1)
    )

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


