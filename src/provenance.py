from __future__ import annotations
import pandas as pd

def add_provenance(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["provenance"] = (
        "Retrieved from Materials Project summary data, then filtered and labeled using prototype alloy-family rules and engineering proxy scoring."
    )
    return out