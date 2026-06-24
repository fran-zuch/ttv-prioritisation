#from .bins import bin_ttv

def compute_s2_ttv(df):

    def ttv_score(r):

        oc = abs(r.get('current_oc_min') or 0)
        score = bin_ttv(oc)

        # ✅ ExoClock TTV flag boost
        if r.get('ttv_flag'):
            score = min(score + 1, 5)

        return score

    df['S2'] = df.apply(ttv_score, axis=1)
    return df
