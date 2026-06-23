from astropy.time import Time
import numpy as np

def compute_time_to_window(tmid_utc):
    now=Time.now(); event=Time(tmid_utc)
    d=event.jd-now.jd
    return d if d>0 else None

def compute_observability(df):
    times = []
    for r in df.itertuples():
        times.append(compute_time_to_window(r.Tmid_utc))
    df['time_to_window_days'] = times
    # Convert times to numpy array, replacing None with 0 or NaN as appropriate
    times_array = np.array([t if t is not None else 0 for t in times], dtype=float)
    df['obs_frac'] = np.clip(1 - (times_array / 7), 0, 1)
    return df
