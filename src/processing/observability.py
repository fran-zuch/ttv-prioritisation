"""
Astropy-based observability calculations.

This structure is conceptually informed by ExoClock observability tools
(altitude constraints, night filtering, and visibility evaluation),
but all computations are independently implemented for this project
and adapted for integration into a quantitative scoring pipeline.

Therefore, it replaces earlier ExoClock-style implementations with a fully
independent Astropy-based approach, computing altitude, airmass, and
visibility constraints for transit events.
"""

import numpy as np
import pandas as pd

from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun, get_body
from astropy.time import Time
import astropy.units as u


# -----------------------------------------------------------------------------
# Observatory setup
# -----------------------------------------------------------------------------

def build_observatory(lat, lon, elevation=0):
    return EarthLocation(
        lat=lat * u.deg,
        lon=lon * u.deg,
        height=elevation * u.m
    )


# -----------------------------------------------------------------------------
# Core calculations
# -----------------------------------------------------------------------------

def compute_altaz(target_coord, location, times):
    frame = AltAz(obstime=times, location=location)
    altaz = target_coord.transform_to(frame)
    return altaz.alt, altaz.az


def compute_airmass(alt):
    alt_deg = alt.to(u.deg).value
    airmass = 1 / np.sin(np.deg2rad(alt_deg))
    airmass[alt_deg < 0] = np.nan
    return airmass


def compute_sun_alt(location, times):
    sun = get_sun(times)
    frame = AltAz(obstime=times, location=location)
    return sun.transform_to(frame).alt


def compute_moon_sep(location, times, target_coord):
    moon = get_body("moon", times, location=location)
    return moon.separation(target_coord)


# -----------------------------------------------------------------------------
# Time grid around transit
# -----------------------------------------------------------------------------

def build_time_grid(mid_time, window_hours=4, cadence_min=2):
    half_window = (window_hours / 2) * u.hour
    cadence = cadence_min * u.min

    times = mid_time + np.arange(
        -half_window.value,
        half_window.value,
        cadence.to(u.hour).value
    ) * u.hour

    return Time(times)


# -----------------------------------------------------------------------------
# Main processing function (THIS is your pipeline entry point)
# -----------------------------------------------------------------------------

def compute_observability(df, config):
    """
    Adds observability metrics to dataframe.

    Expected df columns:
        ra, dec, Tmid_utc
    """
    
    # ✅ Convert to datetime first
    df["Tmid_utc"] = pd.to_datetime(
        df["Tmid_utc"],
        format="ISO8601",   # preferred
        errors="coerce"
    )

    
    # ✅ Drop anything broken
    df = df.dropna(subset=["Tmid_utc"])

    location = build_observatory(
        config["lat"],
        config["lon"],
        config.get("elevation", 0)
    )

    results = []
    
    for _, row in df.iterrows():
        
        try:
    
            # ✅ Validate inputs
            if pd.isna(row.get("ra")) or pd.isna(row.get("dec")):
                raise ValueError("Missing coordinates")
    
            if pd.isna(row.get("Tmid_utc")):
                raise ValueError("Invalid Tmid_utc after parsing")
    
            # ✅ Build target
            target = SkyCoord(
                ra=row["ra"] * u.deg,
                dec=row["dec"] * u.deg
            )
    
            mid_time =Time(pd.to_datetime(row["Tmid_utc"]).to_pydatetime())
            
            print("mid_time:", row["Tmid_utc"], type(row["Tmid_utc"]))
    
            times = build_time_grid(mid_time)
    
            # --- Compute ---
            alt, az = compute_altaz(target, location, times)
            airmass = compute_airmass(alt)
            sun_alt = compute_sun_alt(location, times)
    
            altitude_ok = alt > (config.get("min_alt", 20) * u.deg)
            sun_ok = sun_alt < (config.get("max_sun_alt", -18) * u.deg)
            moon_ok = compute_moon_sep(location, times, target) > (
                config.get("min_moon_sep", 30) * u.deg
            )
    
            good = altitude_ok & sun_ok & moon_ok
    
            obs_frac = np.sum(good) / len(good)
    
            results.append({
                "obs_frac": obs_frac,
                "obs_max_alt": np.nanmax(alt.value),
                "obs_min_alt": np.nanmin(alt.value),
                "obs_mean_airmass": np.nanmean(airmass),
                "obs_visible": int(np.any(good)),
                "obs_peak_time_jd": times[np.argmax(alt)].jd
            })
    
        except Exception as e:
    
            # ✅ SAFE fallback (NO reference to 'good' here!)
            results.append({
                "obs_frac": 0,
                "obs_max_alt": np.nan,
                "obs_min_alt": np.nan,
                "obs_mean_airmass": np.nan,
                "obs_visible": 0,
                "obs_peak_time_jd": np.nan
            })
            
    return df.join(pd.DataFrame(results))
