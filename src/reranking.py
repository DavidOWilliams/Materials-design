from __future__ import annotations

from typing import Dict, Any

import pandas as pd


def scientific_rerank(df: pd.DataFrame, requirements: Dict[str, Any]) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return df

    out = df.copy()
    target_temp = requirements.get("operating_temperature", 850)

    out["family_fit_score"] = out["material_family"].astype(str).apply(
        lambda x: 12 if "Ni-based" in x else
                  10 if "Co-based" in x else
                  10 if "Refractory" in x else
                  7 if "Fe-Ni" in x else
                  7 if "Ti-alloy" in x else 0
    )

    out["chemistry_fit_score"] = (
        out["alloy_likeness_score"].fillna(0) * 0.12
        + out["n_elements"].fillna(0) * 1.5
    )

    out["evidence_score"] = (
        out["is_stable"].astype(int) * 8
        + (~out["theoretical"].astype(bool)).astype(int) * 8
        + (1 - out["energy_above_hull"].clip(lower=0, upper=1.0)) * 10
    )

    temp_bonus = 0
    if target_temp >= 900:
        temp_bonus = 2
    elif target_temp >= 850:
        temp_bonus = 1

    out["scientific_rerank_score"] = (
        out["overall_score"]
        + out["family_fit_score"]
        + out["chemistry_fit_score"]
        + out["evidence_score"]
        + temp_bonus
    ).round(2)

    out["rerank_reason"] = (
        "Ordered using baseline proxy score plus family-fit, chemistry-fit, and evidence-strength preferences."
    )

    return out