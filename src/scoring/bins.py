def bin_ephemeris(x):
    return 1 if x<2 else 2 if x<5 else 3 if x<10 else 4 if x<15 else 5

def bin_observability(x):
    return 1 if x<0.25 else 2 if x<0.5 else 3 if x<0.75 else 4 if x<0.95 else 5
