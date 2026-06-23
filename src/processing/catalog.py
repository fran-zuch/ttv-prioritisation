import pandas as pd, numpy as np

def to_numeric(df, cols):
    for c in cols:
        df[c]=pd.to_numeric(df.get(c, np.nan), errors='coerce')
    return df

def prepare_catalog(df):
    cols=['ephem_mid_time','ephem_period','t0_bjd_tdb','t0_unc','period_days','period_unc','duration_hours','depth_r_mmag','v_mag','gaia_g_mag','current_oc_min']
    df=to_numeric(df, cols)
    df['T0']=df['t0_bjd_tdb'].fillna(df['ephem_mid_time'])
    df['P']=df['period_days'].fillna(df['ephem_period'])
    df['T0_unc_days']=df['t0_unc']
    df['P_unc_days']=df['period_unc']
    df['last_obs_jd']=pd.to_numeric(df.get('last_observed_midpoint'), errors='coerce')
    return df
