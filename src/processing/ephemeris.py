import numpy as np
from astropy.time import Time
import pandas as pd

def propagate_uncertainty(T0,P,T0_sig,P_sig,Tmid):
    epochs=(Tmid-T0)/P
    return np.sqrt(T0_sig**2 + (epochs*P_sig)**2)

def compute_time_since_last_obs(last_obs_jd):
    if last_obs_jd is None or not np.isfinite(last_obs_jd): return None
    return Time.now().tdb.jd - last_obs_jd

def expand_events(df,start_utc,end_utc):
    start=Time(start_utc); end=Time(end_utc)
    events=[]
    for _,r in df.iterrows():
        T0,P=r['T0'],r['P']
        if not np.isfinite(T0) or not np.isfinite(P): continue
        N=int((start.tdb.jd-T0)/P)-1
        while True:
            tmid=T0+N*P
            if tmid>end.tdb.jd: break
            if tmid>=start.tdb.jd:
                sigma=propagate_uncertainty(T0,P,r['T0_unc_days'] or 0,r['P_unc_days'] or 0,tmid)*1440
                events.append({
                    'name':r.get('name'),
                    'Tmid_utc':Time(tmid,format='jd',scale='tdb').utc.isot,
                    'duration_hr':r.get('duration_hours'),
                    'mag_V':r.get('v_mag'),
                    'depth_mmag':r.get('depth_r_mmag'),
                    'current_oc_min':r.get('current_oc_min'),
                    'pred_sigma_min':sigma,
                    'time_since_last_obs_days':compute_time_since_last_obs(r.get('last_obs_jd'))
                })
            N+=1
    return pd.DataFrame(events)
