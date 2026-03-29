from __future__ import annotations
import pandas as pd

def add_provenance(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["provenance"] = (
        "Generated from seeded materials dataset with rule-based requirement inference and proxy scoring."
    )
    return out
