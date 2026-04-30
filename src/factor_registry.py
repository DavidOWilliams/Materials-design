from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import pandas as pd

from src.requirement_schema import FACTOR_LABELS, FACTOR_REASON_COLUMNS, FACTOR_SCORE_COLUMNS

REFRACTORY_ELEMENTS = {"Mo", "Nb", "Ta", "W", "Hf"}
HOT_CORROSION_ELEMENTS = {"Co", "Cr", "W", "Mo", "Ni"}
OXIDATION_ELEMENTS = {"Ni", "Co", "Cr", "Al"}
WEAR_ELEMENTS = {"Co", "Cr", "W", "Mo", "Ta"}


def _clamp(value: float, lower: float = 8.0, upper: float = 95.0) -> float:
    return max(lower, min(upper, float(value)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _parse_elements(chemsys: Any) -> List[str]:
    if chemsys is None:
        return []
    return [part.strip() for part in str(chemsys).split("-") if part.strip()]


def _family_key(row: pd.Series) -> str:
    family = str(row.get("material_family", "") or "")
    if "Ni-based" in family:
        return "ni"
    if "Co-based" in family:
        return "co"
    if "Refractory" in family:
        return "refractory"
    if "Ti-alloy" in family or "Ti-based" in family:
        return "ti"
    if "Fe-Ni" in family:
        return "fe_ni"
    return "other"


def _evidence_adjustment(row: pd.Series) -> float:
    stable = bool(row.get("is_stable", False))
    theoretical = bool(row.get("theoretical", True))
    e_hull = _safe_float(row.get("energy_above_hull"), 0.5)
    return (5.0 if stable else -3.0) + (-7.0 if theoretical else 5.0) - min(8.0, max(0.0, e_hull * 20.0))


def _score_lightweight(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    density = _safe_float(row.get("density"), 0.0)
    family = _family_key(row)
    alloy_likeness = _safe_float(row.get("alloy_likeness_score"), 50.0)

    if density <= 0:
        density_component = 45.0
        density_reason = "density unavailable"
    else:
        density_component = 92.0 - (density * 6.5)
        density_reason = f"density proxy {density:.2f} g/cm³"

    family_adjustment = {
        "ti": 18.0,
        "ni": -4.0,
        "co": -11.0,
        "refractory": -18.0,
        "fe_ni": -8.0,
        "other": 0.0,
    }.get(family, 0.0)
    score = _clamp(density_component + family_adjustment + alloy_likeness * 0.04 + _evidence_adjustment(row) * 0.35)
    reason = f"Lightweight fit reflects {density_reason}, family density expectations, and evidence confidence."
    return round(score, 2), reason


def _score_oxidation(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    elements = set(_parse_elements(row.get("chemsys")))
    family = _family_key(row)
    score = 48.0
    if family == "ni":
        score += 17.0
    elif family == "co":
        score += 11.0
    elif family == "refractory":
        score -= 8.0
    elif family == "ti":
        score += 2.0
    score += 12.0 if "Cr" in elements else 0.0
    score += 8.0 if "Al" in elements else 0.0
    score += 3.0 if elements.intersection({"W", "Mo"}) else 0.0
    score += _evidence_adjustment(row) * 0.50
    return round(_clamp(score), 2), "Oxidation proxy favours Ni/Co families and Cr/Al-bearing chemistries, with evidence adjustment."


def _score_hot_corrosion(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    elements = set(_parse_elements(row.get("chemsys")))
    family = _family_key(row)
    score = 46.0
    if family == "co":
        score += 22.0
    elif family == "ni":
        score += 13.0
    elif family == "refractory":
        score -= 6.0
    elif family == "ti":
        score -= 4.0
    score += 11.0 if "Cr" in elements else 0.0
    score += 5.0 if elements.intersection({"W", "Mo"}) else 0.0
    score += 3.0 if "Ni" in elements and family == "co" else 0.0
    score += _evidence_adjustment(row) * 0.45
    return round(_clamp(score), 2), "Hot-corrosion proxy favours Co/Ni high-temperature families with Cr and W/Mo support."


def _score_wear(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    elements = set(_parse_elements(row.get("chemsys")))
    family = _family_key(row)
    score = 45.0
    if family == "co":
        score += 24.0
    elif family == "refractory":
        score += 7.0
    elif family == "ni":
        score += 5.0
    elif family == "ti":
        score -= 5.0
    score += 8.0 if "Cr" in elements else 0.0
    score += 9.0 if elements.intersection({"W", "Mo", "Ta"}) else 0.0
    score += _evidence_adjustment(row) * 0.40
    return round(_clamp(score), 2), "Wear proxy favours Co-rich and hard refractory-containing chemistries with Cr/W/Mo/Ta support."


def _score_erosion(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    wear, _ = _score_wear(row, requirements)
    toughness = _safe_float(row.get("toughness_score"), 50.0)
    score = _clamp(wear * 0.55 + toughness * 0.45)
    return round(score, 2), "Erosion proxy combines wear-oriented chemistry with the existing toughness/damage-tolerance proxy."


def _score_fatigue(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    family = _family_key(row)
    density = _safe_float(row.get("density"), 0.0)
    toughness = _safe_float(row.get("toughness_score"), 50.0)
    score = 42.0 + toughness * 0.35
    if family == "ti":
        score += 12.0
    elif family == "ni":
        score += 8.0
    elif family == "fe_ni":
        score += 6.0
    elif family == "refractory":
        score -= 6.0
    if 0 < density <= 5.5:
        score += 5.0
    score += _evidence_adjustment(row) * 0.45
    return round(_clamp(score), 2), "Fatigue proxy combines baseline toughness, family maturity, density cues, and evidence confidence."


def _score_thermal_fatigue(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    creep = _safe_float(row.get("creep_score"), 50.0)
    temperature = _safe_float(row.get("temperature_score"), 50.0)
    oxidation, _ = _score_oxidation(row, requirements)
    score = _clamp(creep * 0.35 + temperature * 0.35 + oxidation * 0.30)
    return round(score, 2), "Thermal-fatigue proxy combines creep, temperature suitability, and oxidation/environmental resistance."


def _score_repairability(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    family = _family_key(row)
    am_preferred = bool(requirements.get("am_preferred", False))
    am_capable = str(row.get("am_capable", "no") or "no").lower() == "yes"
    manufacturability = _safe_float(row.get("manufacturability_score"), 50.0)
    score = 42.0 + manufacturability * 0.35
    if family == "ni":
        score += 8.0
    elif family == "ti":
        score += 6.0
    elif family == "fe_ni":
        score += 7.0
    elif family == "co":
        score += 2.0
    elif family == "refractory":
        score -= 12.0
    if am_preferred and am_capable:
        score += 5.0
    score += _evidence_adjustment(row) * 0.35
    return round(_clamp(score), 2), "Repairability proxy reflects manufacturability, route compatibility, family maturity, and evidence confidence."


def _score_certification_maturity(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, str]:
    family = _family_key(row)
    evidence = _safe_float(row.get("evidence_maturity_score"), 50.0)
    score = 34.0 + evidence * 0.45
    if family == "ni":
        score += 16.0
    elif family == "ti":
        score += 15.0
    elif family == "fe_ni":
        score += 9.0
    elif family == "co":
        score += 6.0
    elif family == "refractory":
        score -= 8.0
    if bool(row.get("theoretical", True)):
        score -= 8.0
    if bool(row.get("is_stable", False)):
        score += 5.0
    return round(_clamp(score), 2), "Certification-maturity proxy favours mature aerospace families and stronger evidence signals."


FACTOR_MODEL_FUNCTIONS = {
    "lightweight": _score_lightweight,
    "oxidation": _score_oxidation,
    "hot_corrosion": _score_hot_corrosion,
    "wear": _score_wear,
    "erosion": _score_erosion,
    "fatigue": _score_fatigue,
    "thermal_fatigue": _score_thermal_fatigue,
    "repairability": _score_repairability,
    "certification_maturity": _score_certification_maturity,
}


def evaluate_active_factor_models(df: pd.DataFrame, requirements: Dict[str, Any]) -> pd.DataFrame:
    """Attach prompt-activated factor scores without filtering candidates.

    Existing baseline and downstream factor columns are preserved. This function only adds
    columns for active optional factors and a JSON trace for transparent diagnostics.
    """
    if df is None or len(df) == 0:
        return df

    active_factors = list(requirements.get("active_factor_set") or requirements.get("scope_plan", {}).get("active_factor_set", []) or [])
    active_optional = [factor for factor in active_factors if factor in FACTOR_MODEL_FUNCTIONS]
    out = df.copy()

    active_factor_json_rows: List[str] = []
    active_factor_summary_rows: List[str] = []

    for idx, row in out.iterrows():
        records: List[Dict[str, Any]] = []
        for factor in active_optional:
            score, reason = FACTOR_MODEL_FUNCTIONS[factor](row, requirements)
            score_col = FACTOR_SCORE_COLUMNS[factor]
            reason_col = FACTOR_REASON_COLUMNS[factor]
            out.at[idx, score_col] = score
            out.at[idx, reason_col] = reason
            records.append(
                {
                    "factor": factor,
                    "label": FACTOR_LABELS.get(factor, factor.replace("_", " ").title()),
                    "score": score,
                    "reason": reason,
                    "method": "deterministic_prompt_activated_proxy_v1",
                }
            )
        active_factor_json_rows.append(json.dumps(records))
        if records:
            summary = "; ".join(f"{r['label']}={int(r['score'])}" for r in records)
        else:
            summary = "No optional prompt-specific factors activated."
        active_factor_summary_rows.append(summary)

    out["active_factor_scores_json"] = active_factor_json_rows
    out["active_factor_summary"] = active_factor_summary_rows
    return out


def active_factor_display_rows(row: pd.Series, active_factors: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for factor in active_factors:
        score_col = FACTOR_SCORE_COLUMNS.get(factor)
        if not score_col or score_col not in row.index:
            continue
        reason_col = FACTOR_REASON_COLUMNS.get(factor, "")
        rows.append(
            {
                "Factor": FACTOR_LABELS.get(factor, factor.replace("_", " ").title()),
                "Score": row.get(score_col),
                "Explanation": row.get(reason_col, ""),
            }
        )
    return rows
