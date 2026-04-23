from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple

import pandas as pd

DECISION_PROFILES: Dict[str, Dict[str, Any]] = {
    "Balanced": {
        "label": "Balanced",
        "performance_weight": 0.55,
        "decision_weight": 0.30,
        "evidence_weight": 0.15,
        "decision_factor_weights": {
            "through_life_cost": 0.24,
            "sustainability": 0.22,
            "manufacturability": 0.22,
            "route_suitability": 0.20,
            "supply_risk": 0.12,
        },
        "summary": "Balances engineering performance with decision factors and evidence.",
    },
    "Performance-first": {
        "label": "Performance-first",
        "performance_weight": 0.68,
        "decision_weight": 0.20,
        "evidence_weight": 0.12,
        "decision_factor_weights": {
            "through_life_cost": 0.18,
            "sustainability": 0.14,
            "manufacturability": 0.26,
            "route_suitability": 0.24,
            "supply_risk": 0.18,
        },
        "summary": "Favors thermal/performance fit while still exposing delivery risks.",
    },
    "Cost & sustainability-aware": {
        "label": "Cost & sustainability-aware",
        "performance_weight": 0.45,
        "decision_weight": 0.40,
        "evidence_weight": 0.15,
        "decision_factor_weights": {
            "through_life_cost": 0.32,
            "sustainability": 0.30,
            "manufacturability": 0.16,
            "route_suitability": 0.10,
            "supply_risk": 0.12,
        },
        "summary": "Places extra emphasis on cost, sustainability, and material criticality.",
    },
    "AM route-first": {
        "label": "AM route-first",
        "performance_weight": 0.48,
        "decision_weight": 0.37,
        "evidence_weight": 0.15,
        "decision_factor_weights": {
            "through_life_cost": 0.16,
            "sustainability": 0.18,
            "manufacturability": 0.24,
            "route_suitability": 0.30,
            "supply_risk": 0.12,
        },
        "summary": "Prioritizes practical route fit for additive manufacturing-led selection.",
    },
}

PROFILE_ORDER = list(DECISION_PROFILES.keys())

ELEMENT_SUSTAINABILITY_PENALTIES = {
    "Co": 14,
    "W": 12,
    "Ta": 12,
    "Nb": 8,
    "Mo": 8,
    "Ni": 6,
    "Hf": 8,
    "Cr": 2,
    "V": 3,
}

ELEMENT_COST_PENALTIES = {
    "Co": 16,
    "W": 14,
    "Ta": 14,
    "Nb": 10,
    "Mo": 10,
    "Ni": 8,
    "Hf": 12,
    "Ti": 5,
    "V": 4,
}

ELEMENT_SUPPLY_RISK_PENALTIES = {
    "Co": 18,
    "W": 12,
    "Ta": 12,
    "Nb": 8,
    "Mo": 8,
    "Ni": 6,
    "Hf": 10,
    "V": 5,
}

REFRACTORY_ELEMENTS = {"Mo", "Nb", "Ta", "W", "Hf"}


def apply_decision_profile(requirements: Dict[str, Any], profile_name: str | None) -> Dict[str, Any]:
    profile_key = profile_name if profile_name in DECISION_PROFILES else "Balanced"
    updated = deepcopy(requirements)
    updated["downstream_profile_name"] = profile_key
    updated["downstream_profile"] = deepcopy(DECISION_PROFILES[profile_key])
    updated["decision_factor_weights"] = deepcopy(
        DECISION_PROFILES[profile_key]["decision_factor_weights"]
    )
    return updated


def _parse_elements(chemsys: Any) -> List[str]:
    if chemsys is None:
        return []
    if not isinstance(chemsys, str):
        chemsys = str(chemsys)
    return [part.strip() for part in chemsys.split("-") if part.strip()]


def _clamp(value: float, lower: float = 10.0, upper: float = 95.0) -> float:
    return max(lower, min(upper, float(value)))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _route_family_label(material_family: str) -> str:
    family = str(material_family or "")
    if "Ni-based" in family:
        return "ni"
    if "Co-based" in family:
        return "co"
    if "Refractory" in family:
        return "refractory"
    if "Ti-alloy" in family:
        return "ti"
    if "Fe-Ni" in family:
        return "fe_ni"
    return "other"


def _formula_looks_intermetallic(formula: str) -> bool:
    if not formula:
        return False
    import re

    tokens = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", formula)
    if not tokens:
        return False
    counts: List[float] = []
    for _, raw in tokens:
        if raw == "":
            counts.append(1.0)
        else:
            try:
                counts.append(float(raw))
            except Exception:
                counts.append(1.0)
    return len(counts) <= 3 and all(count <= 3 for count in counts)


def _top_penalty_elements(elements: List[str], penalty_map: Dict[str, int], top_n: int = 3) -> List[str]:
    ranked = sorted(
        [(element, penalty_map.get(element, 0)) for element in set(elements) if penalty_map.get(element, 0) > 0],
        key=lambda item: item[1],
        reverse=True,
    )
    return [name for name, _ in ranked[:top_n]]


def _sustainability_components(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
    elements = _parse_elements(row.get("chemsys"))
    density = _safe_float(row.get("density"), 0.0)
    am_preferred = bool(requirements.get("am_preferred", False))

    start = 78.0
    elemental_burden = sum(ELEMENT_SUSTAINABILITY_PENALTIES.get(element, 0) for element in set(elements))
    route_modifier = 0.0
    if am_preferred and str(row.get("am_capable", "no")).lower() == "yes":
        route_modifier += 5.0
    elif am_preferred:
        route_modifier -= 3.0

    if density >= 11:
        route_modifier -= 4.0
    elif density <= 5.5 and density > 0:
        route_modifier += 2.0

    score = _clamp(start - elemental_burden + route_modifier, lower=10.0, upper=90.0)
    key_elements = _top_penalty_elements(elements, ELEMENT_SUSTAINABILITY_PENALTIES)
    reason = "Element burden is modest."
    if key_elements:
        reason = f"Penalised mainly by {', '.join(key_elements)} content."
    if route_modifier > 0:
        reason += " Partly offset by a favorable material-utilisation / route fit effect."
    elif route_modifier < 0:
        reason += " Route and density cues slightly worsen the sustainability view."
    return score, {
        "sustainability_element_burden": float(elemental_burden),
        "sustainability_route_modifier": float(route_modifier),
    }, reason


def _through_life_cost_components(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, Dict[str, float], str]:
    elements = _parse_elements(row.get("chemsys"))
    family_key = _route_family_label(str(row.get("material_family", "")))
    operating_temperature = _safe_float(requirements.get("operating_temperature"), 850.0)
    theoretical = bool(row.get("theoretical", True))
    stable = bool(row.get("is_stable", False))
    e_hull = _safe_float(row.get("energy_above_hull"), 0.5)
    am_preferred = bool(requirements.get("am_preferred", False))

    start = 76.0
    material_cost_burden = float(sum(ELEMENT_COST_PENALTIES.get(element, 0) for element in set(elements)))

    process_burden = 6.0 if am_preferred else 4.0
    if am_preferred and str(row.get("am_capable", "no")).lower() == "yes":
        process_burden -= 4.0
    if family_key == "refractory":
        process_burden += 6.0
    elif family_key == "co":
        process_burden += 2.0
    elif family_key in {"ni", "ti"}:
        process_burden += 1.0

    service_burden = 4.0
    if operating_temperature >= 950:
        service_burden += 5.0
    elif operating_temperature >= 850:
        service_burden += 2.0
    if family_key == "refractory":
        service_burden += 2.0

    uncertainty_premium = 0.0
    if theoretical:
        uncertainty_premium += 8.0
    if not stable:
        uncertainty_premium += 6.0
    uncertainty_premium += min(8.0, max(0.0, e_hull * 20.0))

    total_penalty = material_cost_burden * 0.55 + process_burden + service_burden + uncertainty_premium
    score = _clamp(start - total_penalty, lower=8.0, upper=90.0)

    reason_parts = []
    costly_elements = _top_penalty_elements(elements, ELEMENT_COST_PENALTIES)
    if costly_elements:
        reason_parts.append(f"High alloy cost burden from {', '.join(costly_elements)}")
    if process_burden >= 10:
        reason_parts.append("processing burden looks relatively high")
    if uncertainty_premium >= 8:
        reason_parts.append("uncertainty premium is significant")
    reason = ". ".join(reason_parts) + "." if reason_parts else "No major cost driver stands out from the proxy inputs."
    return score, {
        "material_cost_burden": float(material_cost_burden),
        "process_cost_burden": float(process_burden),
        "service_cost_burden": float(service_burden),
        "uncertainty_cost_burden": float(uncertainty_premium),
    }, reason


def _manufacturability_components(row: pd.Series) -> Tuple[float, Dict[str, float], str]:
    family_key = _route_family_label(str(row.get("material_family", "")))
    elements = _parse_elements(row.get("chemsys"))
    formula = str(row.get("formula_pretty", "") or "")
    alloy_likeness = _safe_float(row.get("alloy_likeness_score"), 0.0)
    theoretical = bool(row.get("theoretical", True))
    stable = bool(row.get("is_stable", False))
    e_hull = _safe_float(row.get("energy_above_hull"), 0.5)
    n_elements = int(_safe_float(row.get("n_elements"), len(elements)))
    refractory_count = len(set(elements).intersection(REFRACTORY_ELEMENTS))

    family_maturity = {
        "ni": 10.0,
        "ti": 9.0,
        "fe_ni": 8.0,
        "co": 6.0,
        "refractory": 3.0,
        "other": 0.0,
    }.get(family_key, 0.0)

    evidence_adjustment = 0.0
    evidence_adjustment += 8.0 if stable else -4.0
    evidence_adjustment += 8.0 if not theoretical else -10.0
    evidence_adjustment += max(-10.0, 8.0 - (e_hull * 25.0))

    chemistry_adjustment = 0.0
    if alloy_likeness >= 65:
        chemistry_adjustment += 8.0
    elif alloy_likeness >= 45:
        chemistry_adjustment += 3.0
    else:
        chemistry_adjustment -= 6.0

    if _formula_looks_intermetallic(formula):
        chemistry_adjustment -= 8.0
    if refractory_count >= 2:
        chemistry_adjustment -= 5.0
    if n_elements > 6:
        chemistry_adjustment -= 2.0
    elif 3 <= n_elements <= 5:
        chemistry_adjustment += 2.0

    score = _clamp(50.0 + family_maturity + evidence_adjustment + chemistry_adjustment, lower=10.0, upper=92.0)

    reason_bits: List[str] = []
    if family_key in {"ni", "ti", "fe_ni"}:
        reason_bits.append("mature engineering family helps")
    elif family_key == "refractory":
        reason_bits.append("refractory chemistry makes manufacture harder")
    if theoretical:
        reason_bits.append("theoretical-only status hurts")
    if _formula_looks_intermetallic(formula):
        reason_bits.append("intermetallic-looking stoichiometry hurts")
    if stable and not theoretical:
        reason_bits.append("stable non-theoretical evidence helps")

    return score, {
        "manufacturability_family_maturity": float(family_maturity),
        "manufacturability_evidence_adjustment": float(evidence_adjustment),
        "manufacturability_chemistry_adjustment": float(chemistry_adjustment),
    }, "; ".join(reason_bits).capitalize() + "." if reason_bits else "Manufacturability looks middle-of-the-road on the current proxy rules."


def _route_components(row: pd.Series, requirements: Dict[str, Any]) -> Tuple[float, float, float, str]:
    family_key = _route_family_label(str(row.get("material_family", "")))
    am_preferred = bool(requirements.get("am_preferred", False))
    stable = bool(row.get("is_stable", False))
    theoretical = bool(row.get("theoretical", True))
    e_hull = _safe_float(row.get("energy_above_hull"), 0.5)
    manufacturability = _safe_float(row.get("manufacturability_score"), 50.0)
    am_capable = str(row.get("am_capable", "no")).lower() == "yes"

    am_score = 48.0
    conventional_score = 58.0

    if family_key == "ti":
        am_score += 10.0
        conventional_score += 6.0
    elif family_key == "ni":
        am_score += 8.0
        conventional_score += 7.0
    elif family_key == "co":
        am_score += 5.0
        conventional_score += 5.0
    elif family_key == "fe_ni":
        am_score += 4.0
        conventional_score += 8.0
    elif family_key == "refractory":
        am_score -= 8.0
        conventional_score += 2.0

    if am_capable:
        am_score += 8.0
    else:
        am_score -= 6.0

    if stable:
        am_score += 4.0
        conventional_score += 4.0
    else:
        am_score -= 4.0
        conventional_score -= 2.0

    if theoretical:
        am_score -= 8.0
        conventional_score -= 6.0

    if e_hull > 0.15:
        am_score -= 4.0
        conventional_score -= 3.0

    manufacturability_modifier = (manufacturability - 50.0) * 0.20
    am_score += manufacturability_modifier
    conventional_score += manufacturability_modifier * 0.75

    am_score = _clamp(am_score, lower=10.0, upper=95.0)
    conventional_score = _clamp(conventional_score, lower=10.0, upper=95.0)
    selected = am_score if am_preferred else conventional_score

    if am_preferred:
        reason = "Preferred route is additive manufacturing; score reflects AM suitability."
    else:
        reason = "Preferred route is conventional processing; score reflects conventional-route suitability."
    return selected, am_score, conventional_score, reason


def _supply_risk_components(row: pd.Series) -> Tuple[float, Dict[str, float], str]:
    elements = _parse_elements(row.get("chemsys"))
    total_risk = float(sum(ELEMENT_SUPPLY_RISK_PENALTIES.get(element, 0) for element in set(elements)))
    score = _clamp(82.0 - total_risk, lower=8.0, upper=92.0)
    risk_elements = _top_penalty_elements(elements, ELEMENT_SUPPLY_RISK_PENALTIES)
    reason = "No major critical-material signal stands out."
    if risk_elements:
        reason = f"Supply-chain exposure is driven mainly by {', '.join(risk_elements)}."
    return score, {"supply_risk_burden": float(total_risk)}, reason


def _evidence_maturity_components(row: pd.Series) -> Tuple[float, Dict[str, float], str]:
    stable = bool(row.get("is_stable", False))
    theoretical = bool(row.get("theoretical", True))
    e_hull = _safe_float(row.get("energy_above_hull"), 0.5)
    alloy_likeness = _safe_float(row.get("alloy_likeness_score"), 0.0)
    plausibility = str(row.get("engineering_plausibility", "") or "")

    stable_points = 22.0 if stable else 4.0
    theoretical_points = 22.0 if not theoretical else 6.0
    hull_points = max(0.0, 20.0 - min(20.0, e_hull * 100.0))
    alloy_points = 12.0 if alloy_likeness >= 65 else 8.0 if alloy_likeness >= 45 else 4.0
    plausibility_points = 12.0 if plausibility == "Higher" else 8.0 if plausibility == "Medium" else 4.0

    score = _clamp(stable_points + theoretical_points + hull_points + alloy_points + plausibility_points,
                   lower=10.0, upper=95.0)

    reason_bits = []
    if stable:
        reason_bits.append("stable")
    if not theoretical:
        reason_bits.append("non-theoretical")
    if e_hull <= 0.05:
        reason_bits.append("low energy-above-hull")
    reason = ", ".join(reason_bits).capitalize() + " evidence boosts confidence." if reason_bits else "Evidence remains weak on current database proxies."
    return score, {
        "evidence_stability_points": float(stable_points),
        "evidence_theoretical_points": float(theoretical_points),
        "evidence_hull_points": float(hull_points),
        "evidence_alloy_points": float(alloy_points),
        "evidence_plausibility_points": float(plausibility_points),
    }, reason


def evaluate_candidates(df: pd.DataFrame, requirements: Dict[str, Any]) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return df

    evaluated = df.copy()
    sustainability_scores: List[float] = []
    sustainability_reasons: List[str] = []
    through_life_cost_scores: List[float] = []
    through_life_cost_reasons: List[str] = []
    manufacturability_scores: List[float] = []
    manufacturability_reasons: List[str] = []
    route_scores: List[float] = []
    am_route_scores: List[float] = []
    conventional_route_scores: List[float] = []
    route_reasons: List[str] = []
    supply_scores: List[float] = []
    supply_reasons: List[str] = []
    evidence_scores: List[float] = []
    evidence_reasons: List[str] = []
    contribution_rows: List[Dict[str, float]] = []

    for _, row in evaluated.iterrows():
        sustainability_score, sustainability_components, sustainability_reason = _sustainability_components(row, requirements)
        sustainability_scores.append(round(sustainability_score, 2))
        sustainability_reasons.append(sustainability_reason)

        through_life_cost_score, cost_components, cost_reason = _through_life_cost_components(row, requirements)
        through_life_cost_scores.append(round(through_life_cost_score, 2))
        through_life_cost_reasons.append(cost_reason)

        manufacturability_score, manuf_components, manuf_reason = _manufacturability_components(row)
        manufacturability_scores.append(round(manufacturability_score, 2))
        manufacturability_reasons.append(manuf_reason)

        temp_row = row.copy()
        temp_row["manufacturability_score"] = manufacturability_score
        route_score, am_score, conventional_score, route_reason = _route_components(temp_row, requirements)
        route_scores.append(round(route_score, 2))
        am_route_scores.append(round(am_score, 2))
        conventional_route_scores.append(round(conventional_score, 2))
        route_reasons.append(route_reason)

        supply_score, supply_components, supply_reason = _supply_risk_components(row)
        supply_scores.append(round(supply_score, 2))
        supply_reasons.append(supply_reason)

        evidence_score, evidence_components, evidence_reason = _evidence_maturity_components(row)
        evidence_scores.append(round(evidence_score, 2))
        evidence_reasons.append(evidence_reason)

        contribution_rows.append(
            {
                **sustainability_components,
                **cost_components,
                **manuf_components,
                **supply_components,
                **evidence_components,
            }
        )

    evaluated["sustainability_score_v1"] = sustainability_scores
    evaluated["sustainability_reason"] = sustainability_reasons
    evaluated["through_life_cost_score"] = through_life_cost_scores
    evaluated["through_life_cost_reason"] = through_life_cost_reasons
    evaluated["manufacturability_score"] = manufacturability_scores
    evaluated["manufacturability_reason"] = manufacturability_reasons
    evaluated["route_suitability_score"] = route_scores
    evaluated["am_route_score"] = am_route_scores
    evaluated["conventional_route_score"] = conventional_route_scores
    evaluated["route_suitability_reason"] = route_reasons
    evaluated["supply_risk_score"] = supply_scores
    evaluated["supply_risk_reason"] = supply_reasons
    evaluated["evidence_maturity_score"] = evidence_scores
    evaluated["evidence_maturity_reason"] = evidence_reasons

    contributions_df = pd.DataFrame(contribution_rows)
    for column in contributions_df.columns:
        evaluated[column] = contributions_df[column].round(2)

    return evaluated
