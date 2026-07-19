# src/ingestion/literature_loader.py

import pandas as pd
from pathlib import Path

def load_literature_flags():

    path = Path("output/literature_flags.csv")

    if not path.exists():
        return pd.DataFrame()

    return pd.read_csv(path)
