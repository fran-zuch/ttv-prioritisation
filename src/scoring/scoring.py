import pandas as pd
from .bins import *

def compute_scores(df):
    def urgency(r):
        s=r['pred_sigma_min']; t=r['time_since_last_obs_days']
        return s if t is None else s*(1+(t/100))
    df['S1']=df.apply(urgency,axis=1).apply(bin_ephemeris)
    df['S4']=df['obs_frac'].apply(bin_observability)
    df['final_score']=df[['S1','S4']].mean(axis=1)
    return df.sort_values('final_score',ascending=False)
