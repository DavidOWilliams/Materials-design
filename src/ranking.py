from __future__ import annotations
import pandas as pd
from typing import Tuple

def rank_candidates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ranked = df.sort_values("overall_score", ascending=False).reset_index(drop=True)
    top = ranked.head(5).copy()
    near_miss = ranked[(ranked["overall_score"] >= 55) & (ranked["overall_score"] < 70)].copy()
    return top, near_miss.head(3)
