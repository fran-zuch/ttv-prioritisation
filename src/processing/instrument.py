from scoring.bins import bin_instrument

def compute_s3_instrument(df, telescope="PIRATE"):

    def instr_score(r):

        mag = r.get('mag_V')
        depth = r.get('depth_mmag')
        duration = r.get('duration_hr')

        if mag is None or depth is None:
            return 1

        score = bin_instrument(mag, depth)

        if telescope == "PIRATE":
            if mag > 13:
                score -= 1
            if depth < 2:
                score -= 1
            if duration and duration > 3:
                score -= 1

        return max(1, min(score, 5))

    df['S3'] = df.apply(instr_score, axis=1)
    return df
