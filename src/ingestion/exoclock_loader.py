import json, urllib.request, pandas as pd
EXOCLOCK_URL = 'https://www.exoclock.space/database/planets_json'
def fetch_exoclock():
    with urllib.request.urlopen(EXOCLOCK_URL) as f:
        data = json.loads(f.read())
    rows=[]
    for k,v in data.items():
        row={'id':k}
        if isinstance(v,dict): row.update(v)
        rows.append(row)
    return pd.DataFrame(rows)
