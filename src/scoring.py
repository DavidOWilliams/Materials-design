from __future__ import annotations
import pandas as pd
from typing import Dict, Any

def score_candidates(df: pd.DataFrame, requirements: Dict[str, Any]) -> pd.DataFrame:
    scored = df.copy()
    w = requirements["weights"]
    temp = requirements["operating_temperature"]

    # Temperature adjustment
    temp_penalty = 0
    if temp >= 900:
        temp_penalty = 8
    elif temp >= 850:
        temp_penalty = 4

    scored["creep_score"] = scored["base_creep_score"]
    scored["toughness_score"] = scored["base_toughness_score"]
    scored["temperature_score"] = scored["base_temp_score"] - temp_penalty
    scored["cost_score"] = scored["base_cost_score"]
    scored["sustainability_score"] = scored["base_sustainability_score"]

    # Higher cost/sustainability scores in source mean "better" here
    scored["overall_score"] = (
        scored["creep_score"] * w["creep_priority"] +
        scored["toughness_score"] * w["toughness_priority"] +
        scored["temperature_score"] * w["temperature_priority"] +
        scored["cost_score"] * w["cost_priority"] +
        scored["sustainability_score"] * w["sustainability_priority"]
    ).round(2)

    def confidence(row: pd.Series) -> str:
        if row["temperature_score"] < 60:
            return "Low"
        if row["overall_score"] >= 70:
            return "Medium-High"
        return "Medium"

    scored["confidence"] = scored.apply(confidence, axis=1)
    scored["notes"] = scored.apply(
        lambda r: (
            "Strong high-temperature candidate."
            if r["overall_score"] >= 75
            else "Potential near-miss or trade-off candidate."
        ),
        axis=1,
    )
    return scored
