def bin_ephemeris(x):
    return 1 if x<2 else 2 if x<5 else 3 if x<10 else 4 if x<15 else 5

def bin_observability(x):
    return 1 if x<0.25 else 2 if x<0.5 else 3 if x<0.75 else 4 if x<0.95 else 5

def bin_ttv(x):
    return 1 if x < 2 else 2 if x < 5 else 3 if x < 10 else 4 if x < 20 else 5

def bin_instrument(mag, depth):
    mag_score = 5 if mag < 10 else 4 if mag < 11 else 3 if mag < 12 else 2 if mag < 13 else 1
    depth_score = 5 if depth > 10 else 4 if depth > 5 else 3 if depth > 2 else 2 if depth > 1 else 1
    return int((mag_score + depth_score) / 2)

def bin_synergy(events, network):
    base = 5 if events and events > 5 else 3
    if network:
        base += 1
    return min(base, 5)
