from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import pandas as pd

from src.evaluation import apply_decision_profile, evaluate_candidates
from src.factor_registry import evaluate_active_factor_models
from src.manufacturing_recipes import attach_manufacturing_recipes
from src.requirement_schema import FACTOR_LABELS, FACTOR_SCORE_COLUMNS

PERFORMANCE_FACTORS = {
    "creep",
    "toughness",
    "temperature",
    "lightweight",
    "oxidation",
    "hot_corrosion",
    "wear",
    "erosion",
    "fatigue",
    "thermal_fatigue",
}

DECISION_FACTORS = {
    "through_life_cost",
    "sustainability",
    "manufacturability",
    "route_suitability",
    "supply_risk",
    "repairability",
    "certification_maturity",
    "recipe_support",
}


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


def _active_factor_weights(requirements: Dict[str, Any]) -> Dict[str, float]:
    weights = dict(requirements.get("active_factor_weights") or requirements.get("scope_plan", {}).get("active_factor_weights", {}) or {})
    # Backward-compatible fallback if a caller did not come through the new interpreter.
    if not weights:
        legacy = dict(requirements.get("weights", {}) or {})
        weights = {
            "creep": float(legacy.get("creep_priority", 0.25)),
            "toughness": float(legacy.get("toughness_priority", 0.20)),
            "temperature": float(legacy.get("temperature_priority", 0.25)),
            "through_life_cost": float(legacy.get("cost_priority", 0.15)),
            "sustainability": float(legacy.get("sustainability_priority", 0.15)),
            "manufacturability": 0.20,
            "route_suitability": 0.20,
            "supply_risk": 0.12,
            "evidence_maturity": 0.15,
            "recipe_support": 0.15,
        }
    return weights


def _score_pairs_for(row: pd.Series, factors: List[str], factor_weights: Dict[str, float]) -> List[Tuple[float, float]]:
    pairs: List[Tuple[float, float]] = []
    for factor in factors:
        score_col = FACTOR_SCORE_COLUMNS.get(factor)
        if not score_col or score_col not in row.index:
            continue
        try:
            score = float(row.get(score_col, 0.0) or 0.0)
        except Exception:
            score = 0.0
        weight = float(factor_weights.get(factor, 0.0) or 0.0)
        if weight > 0:
            pairs.append((score, weight))
    return pairs


def _build_strengths_and_watchouts(row: pd.Series, active_factors: List[str]) -> Tuple[str, str, str, str]:
    labelled_scores: List[Tuple[str, float]] = []
    for factor in active_factors:
        score_col = FACTOR_SCORE_COLUMNS.get(factor)
        if not score_col or score_col not in row.index:
            continue
        try:
            score = float(row.get(score_col, 0.0) or 0.0)
        except Exception:
            score = 0.0
        labelled_scores.append((FACTOR_LABELS.get(factor, factor.replace("_", " ").title()), score))

    # Always include recipe/evidence if present because they are useful confidence signals.
    for factor in ["recipe_support", "evidence_maturity"]:
        score_col = FACTOR_SCORE_COLUMNS.get(factor)
        label = FACTOR_LABELS.get(factor, factor)
        if score_col in row.index and not any(existing_label == label for existing_label, _ in labelled_scores):
            labelled_scores.append((label, float(row.get(score_col, 0.0) or 0.0)))

    if not labelled_scores:
        labelled_scores = [("Overall", float(row.get("overall_score", 0.0) or 0.0))]

    strengths = sorted(labelled_scores, key=lambda item: item[1], reverse=True)[:2]
    watchouts = sorted(labelled_scores, key=lambda item: item[1])[:2]

    strength_labels = "; ".join(f"{label} ({int(score)})" for label, score in strengths)
    watchout_labels = "; ".join(f"{label} ({int(score)})" for label, score in watchouts)

    primary_strength = strengths[0][0] if strengths else ""
    primary_watchout = watchouts[0][0] if watchouts else ""
    return strength_labels, watchout_labels, primary_strength, primary_watchout


def _confidence(row: pd.Series) -> str:
    evidence = float(row.get("evidence_maturity_score", 0.0) or 0.0)
    temperature_score = float(row.get("temperature_score", 0.0) or 0.0)
    recipe_support = float(row.get("recipe_support_score", 0.0) or 0.0)
    active_factor_avg = float(row.get("active_factor_average_score", 60.0) or 60.0)
    if evidence < 45 or temperature_score < 55 or active_factor_avg < 45:
        return "Low"
    if evidence >= 70 and temperature_score >= 65 and recipe_support >= 65 and active_factor_avg >= 65:
        return "Medium-High"
    return "Medium"


def _recipe_note(row: pd.Series) -> str:
    recipe_mode = str(row.get("recipe_mode", "") or "")
    matched_name = str(row.get("matched_alloy_name", "") or "").strip()
    primary_route = str(row.get("manufacturing_primary_route", "") or "").strip()

    if recipe_mode == "named_analogue" and matched_name:
        return f"Manufacturing recipe is grounded in the named analogue {matched_name}."
    if recipe_mode == "analogue_guided" and matched_name:
        return f"Manufacturing recipe is analogue-guided using {matched_name} as the closest anchor."
    if primary_route:
        return "Manufacturing recipe falls back to a family-envelope route because no strong named analogue was found."
    return "Manufacturing recipe support is limited."


def _notes(row: pd.Series) -> str:
    strength = row.get("primary_strength", "performance")
    watchout = row.get("primary_watchout", "cost")
    active_summary = str(row.get("active_factor_summary", "") or "").strip()
    recipe_note = _recipe_note(row)
    if active_summary:
        return f"Strongest signal: {strength}. Main watch-out: {watchout}. Active prompt factors: {active_summary}. {recipe_note}"
    return f"Strongest signal: {strength}. Main watch-out: {watchout}. {recipe_note}"


def _active_factor_average(row: pd.Series, active_factors: List[str]) -> float:
    scores: List[float] = []
    for factor in active_factors:
        score_col = FACTOR_SCORE_COLUMNS.get(factor)
        if score_col and score_col in row.index:
            try:
                scores.append(float(row.get(score_col, 0.0) or 0.0))
            except Exception:
                pass
    if not scores:
        return 60.0
    return round(sum(scores) / len(scores), 2)


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

    # Existing deterministic downstream factors.
    scored = evaluate_candidates(scored, profiled_requirements)

    # New prompt-activated optional factors. No candidates are filtered here.
    scored = evaluate_active_factor_models(scored, profiled_requirements)

    # Recipe layer remains downstream but now receives schema/scope context and active-factor columns.
    scored = attach_manufacturing_recipes(scored, profiled_requirements)

    scored["cost_score"] = scored["through_life_cost_score"]
    scored["sustainability_score"] = scored["sustainability_score_v1"]

    active_factors = list(profiled_requirements.get("active_factor_set") or profiled_requirements.get("scope_plan", {}).get("active_factor_set", []) or [])
    if not active_factors:
        active_factors = ["creep", "toughness", "temperature", "through_life_cost", "sustainability", "manufacturability", "route_suitability", "supply_risk", "evidence_maturity", "recipe_support"]

    factor_weights = _active_factor_weights(profiled_requirements)
    # Keep legacy weights as minimums for backward compatibility.
    factor_weights["creep"] = max(float(factor_weights.get("creep", 0.0)), float(w.get("creep_priority", 0.0)))
    factor_weights["toughness"] = max(float(factor_weights.get("toughness", 0.0)), float(w.get("toughness_priority", 0.0)))
    factor_weights["temperature"] = max(float(factor_weights.get("temperature", 0.0)), float(w.get("temperature_priority", 0.0)))
    factor_weights["through_life_cost"] = max(float(factor_weights.get("through_life_cost", 0.0)), float(w.get("cost_priority", 0.0)))
    factor_weights["sustainability"] = max(float(factor_weights.get("sustainability", 0.0)), float(w.get("sustainability_priority", 0.0)))

    performance_factors = [factor for factor in active_factors if factor in PERFORMANCE_FACTORS]
    decision_factors = [factor for factor in active_factors if factor in DECISION_FACTORS]

    scored["performance_summary_score"] = scored.apply(
        lambda row: _normalised_weighted_average(_score_pairs_for(row, performance_factors, factor_weights)),
        axis=1,
    )
    scored["decision_summary_score"] = scored.apply(
        lambda row: _normalised_weighted_average(_score_pairs_for(row, decision_factors, factor_weights)),
        axis=1,
    )
    scored["active_factor_average_score"] = scored.apply(lambda row: _active_factor_average(row, active_factors), axis=1)

    profile = profiled_requirements["downstream_profile"]
    scored["overall_score"] = (
        scored["performance_summary_score"] * float(profile["performance_weight"])
        + scored["decision_summary_score"] * float(profile["decision_weight"])
        + scored["evidence_maturity_score"] * float(profile["evidence_weight"])
    ).round(2)

    scored["decision_profile_name"] = profiled_requirements["downstream_profile_name"]
    scored["decision_profile_summary"] = profile.get("summary", "")
    scored["active_factor_set"] = json.dumps(active_factors)
    scored["active_factor_weights_json"] = json.dumps(factor_weights)

    strength_cols = scored.apply(lambda row: _build_strengths_and_watchouts(row, active_factors), axis=1, result_type="expand")
    strength_cols.columns = ["strengths", "watch_outs", "primary_strength", "primary_watchout"]
    for column in strength_cols.columns:
        scored[column] = strength_cols[column]

    scored["confidence"] = scored.apply(_confidence, axis=1)
    scored["notes"] = scored.apply(_notes, axis=1)

    return scored
