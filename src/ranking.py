from __future__ import annotations

from typing import Tuple

import pandas as pd


def rank_candidates(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if df is None or len(df) == 0:
        return df, df

    if "final_rank_score" in df.columns:
        sort_col = "final_rank_score"
    elif "scientific_rerank_score" in df.columns:
        sort_col = "scientific_rerank_score"
    else:
        sort_col = "overall_score"

    ranked = df.sort_values(sort_col, ascending=False).reset_index(drop=True)
    top = ranked.head(5).copy()

    remainder = ranked.iloc[5:].copy()
    if remainder.empty:
        return top, remainder

    tradeoff_mask = (
        remainder["overall_score"].between(55, 74)
        | (remainder.get("through_life_cost_score", pd.Series(index=remainder.index, dtype=float)).fillna(0) >= 72)
        | (remainder.get("sustainability_score_v1", pd.Series(index=remainder.index, dtype=float)).fillna(0) >= 72)
        | (remainder.get("manufacturability_score", pd.Series(index=remainder.index, dtype=float)).fillna(0) >= 72)
        | (remainder.get("route_suitability_score", pd.Series(index=remainder.index, dtype=float)).fillna(0) >= 72)
    )

    near_miss = remainder[tradeoff_mask].copy()
    if near_miss.empty:
        near_miss = remainder.head(3).copy()
    else:
        near_miss = near_miss.head(3).copy()

    return top, near_miss
