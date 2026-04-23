from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd

from src.evaluation import apply_decision_profile, evaluate_candidates


def _normalised_weighted_average(score_pairs: List[Tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in score_pairs if weight > 0)
    if total_weight <= 0:
        return 0.0
    total_value = sum(score * weight for score, weight in score_pairs if weight > 0)
    return round(total_value / total_weight, 2)


def _performance_reason(temp_penalty: int) -> str:
    if temp_penalty <= 0:
        return "Based on the baseline performance proxies without an added operating-temperature demand penalty."
    return f"Based on the baseline performance proxies with a {temp_penalty}-point operating-temperature demand penalty."


def _build_strengths_and_watchouts(row: pd.Series) -> Tuple[str, str, str, str]:
    labelled_scores = [
        ("Creep", float(row.get("creep_score", 0.0))),
        ("Temperature", float(row.get("temperature_score", 0.0))),
        ("Through-life cost", float(row.get("through_life_cost_score", 0.0))),
        ("Sustainability", float(row.get("sustainability_score_v1", 0.0))),
        ("Manufacturability", float(row.get("manufacturability_score", 0.0))),
        ("Route fit", float(row.get("route_suitability_score", 0.0))),
        ("Evidence", float(row.get("evidence_maturity_score", 0.0))),
    ]
    strengths = sorted(labelled_scores, key=lambda item: item[1], reverse=True)[:2]
    watchouts = sorted(labelled_scores, key=lambda item: item[1])[:2]

    strength_labels = "; ".join(f"{label} ({int(score)})" for label, score in strengths)
    watchout_labels = "; ".join(f"{label} ({int(score)})" for label, score in watchouts)

    primary_strength = strengths[0][0] if strengths else ""
    primary_watchout = watchouts[0][0] if watchouts else ""
    return strength_labels, watchout_labels, primary_strength, primary_watchout


def _confidence(row: pd.Series) -> str:
    evidence = float(row.get("evidence_maturity_score", 0.0))
    temperature_score = float(row.get("temperature_score", 0.0))
    if evidence < 45 or temperature_score < 55:
        return "Low"
    if evidence >= 70 and temperature_score >= 65:
        return "Medium-High"
    return "Medium"


def _notes(row: pd.Series) -> str:
    strength = row.get("primary_strength", "performance")
    watchout = row.get("primary_watchout", "cost")
    return f"Strongest signal: {strength}. Main watch-out: {watchout}."


def score_candidates(df: pd.DataFrame, requirements: Dict[str, Any]) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return df

    profile_name = requirements.get("downstream_profile_name", "Balanced")
    profiled_requirements = apply_decision_profile(requirements, profile_name)

    scored = df.copy()
    w = profiled_requirements["weights"]
    temp = profiled_requirements["operating_temperature"]

    temp_penalty = 0
    if temp >= 900:
        temp_penalty = 8
    elif temp >= 850:
        temp_penalty = 4

    scored["creep_score"] = scored["base_creep_score"]
    scored["toughness_score"] = scored["base_toughness_score"]
    scored["temperature_score"] = (scored["base_temp_score"] - temp_penalty).clip(lower=0)
    scored["temperature_reason"] = _performance_reason(temp_penalty)
    scored["creep_reason"] = (
        "Based on the baseline creep proxy derived from family fit, stability, chemistry complexity, and alloy-likeness cues."
    )
    scored["toughness_reason"] = (
        "Based on the baseline toughness proxy derived from family, density, chemistry complexity, and theory/stability cues."
    )

    scored = evaluate_candidates(scored, profiled_requirements)

    scored["cost_score"] = scored["through_life_cost_score"]
    scored["sustainability_score"] = scored["sustainability_score_v1"]

    scored["performance_summary_score"] = scored.apply(
        lambda row: _normalised_weighted_average(
            [
                (float(row["creep_score"]), float(w.get("creep_priority", 0.0))),
                (float(row["toughness_score"]), float(w.get("toughness_priority", 0.0))),
                (float(row["temperature_score"]), float(w.get("temperature_priority", 0.0))),
            ]
        ),
        axis=1,
    )

    decision_factor_weights = profiled_requirements.get("decision_factor_weights", {})
    scored["decision_summary_score"] = scored.apply(
        lambda row: _normalised_weighted_average(
            [
                (float(row["through_life_cost_score"]), float(decision_factor_weights.get("through_life_cost", 0.0))),
                (float(row["sustainability_score_v1"]), float(decision_factor_weights.get("sustainability", 0.0))),
                (float(row["manufacturability_score"]), float(decision_factor_weights.get("manufacturability", 0.0))),
                (float(row["route_suitability_score"]), float(decision_factor_weights.get("route_suitability", 0.0))),
                (float(row["supply_risk_score"]), float(decision_factor_weights.get("supply_risk", 0.0))),
            ]
        ),
        axis=1,
    )

    profile = profiled_requirements["downstream_profile"]
    scored["overall_score"] = (
        scored["performance_summary_score"] * float(profile["performance_weight"])
        + scored["decision_summary_score"] * float(profile["decision_weight"])
        + scored["evidence_maturity_score"] * float(profile["evidence_weight"])
    ).round(2)

    scored["decision_profile_name"] = profiled_requirements["downstream_profile_name"]
    scored["decision_profile_summary"] = profile.get("summary", "")

    strength_cols = scored.apply(_build_strengths_and_watchouts, axis=1, result_type="expand")
    strength_cols.columns = ["strengths", "watch_outs", "primary_strength", "primary_watchout"]
    for column in strength_cols.columns:
        scored[column] = strength_cols[column]

    scored["confidence"] = scored.apply(_confidence, axis=1)
    scored["notes"] = scored.apply(_notes, axis=1)

    return scored
