from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple

from src.requirement_schema import (
    BASELINE_FACTORS,
    FAMILY_KEYS,
    OPTIONAL_FACTORS,
    ScopePlan,
)


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


def _bump(priors: Dict[str, float], family: str, delta: float, rationale: Dict[str, List[str]], reason: str) -> None:
    priors[family] = _clamp(priors.get(family, 0.0) + delta)
    rationale.setdefault(family, []).append(reason)


def _set_min(priors: Dict[str, float], family: str, minimum: float, rationale: Dict[str, List[str]], reason: str) -> None:
    if priors.get(family, 0.0) < minimum:
        priors[family] = minimum
        rationale.setdefault(family, []).append(reason)


def _cap_max(priors: Dict[str, float], family: str, maximum: float, rationale: Dict[str, List[str]], reason: str) -> None:
    if priors.get(family, 0.0) > maximum:
        priors[family] = maximum
        rationale.setdefault(family, []).append(reason)


def _normalise_priors(priors: Dict[str, float]) -> Dict[str, float]:
    return {k: round(_clamp(v), 3) for k, v in priors.items()}


def _has_extreme_temperature_language(prompt_text: str) -> bool:
    prompt = str(prompt_text or "")
    return (
        any(
            term in prompt
            for term in [
                "extreme temperature",
                "extreme-temperature",
                "very high temperature",
                "very-high-temperature",
                "ultra high temperature",
                "ultra-high temperature",
                "ultra-high-temperature",
                "above 1000",
                ">1000",
                "1000°",
                "1050°",
                "1100°",
                "1150°",
                "1200°",
                "specialist processing",
            ]
        )
        or bool(re.search(r"(?:above|over|>|>=)\s*1[0-2]\d{2}\s*(?:°?c|celsius)?", prompt))
    )


def _apply_extreme_refractory_final_calibration(
    priors: Dict[str, float],
    rationale: Dict[str, List[str]],
    trace: List[str],
    *,
    temperature_c: int,
    prompt_text: str,
    inclusions: set[str],
) -> None:
    """Apply final refractory calibration after all generic hot-section and creep bumps.

    Earlier generic rules quite reasonably boost mature Ni/Co hot-section families for
    creep, but those generic bumps should not make Ni the top family when the brief is
    explicitly extreme-temperature / refractory-led. This is still only scope planning;
    it does not filter candidate survival.
    """
    explicit_refractory_language = (
        "Refractory alloy concept" in inclusions
        or "refractory" in prompt_text
        or "molybdenum" in prompt_text
        or "niobium" in prompt_text
        or "tantalum" in prompt_text
        or "tungsten" in prompt_text
    )
    extreme_temperature_language = _has_extreme_temperature_language(prompt_text)
    extreme_refractory_review = explicit_refractory_language or extreme_temperature_language or temperature_c >= 1050

    if not extreme_refractory_review:
        return

    if temperature_c >= 1000:
        priors["Refractory alloy concept"] = 1.0
        rationale.setdefault("Refractory alloy concept", []).append(
            "Final calibration: explicit extreme-temperature / refractory review makes refractory concepts the primary family."
        )
        priors["Ni-based superalloy"] = min(priors.get("Ni-based superalloy", 0.0), 0.70)
        priors["Co-based alloy"] = min(priors.get("Co-based alloy", 0.0), 0.62)
        priors["Ti alloy"] = min(priors.get("Ti alloy", 0.0), 0.18)
        priors["Fe-Ni alloy"] = min(priors.get("Fe-Ni alloy", 0.0), 0.18)
        rationale.setdefault("Ni-based superalloy", []).append(
            "Final calibration: nickel remains a comparison family rather than the primary family for explicit >1000°C / refractory review."
        )
        rationale.setdefault("Co-based alloy", []).append(
            "Final calibration: cobalt remains a comparison family rather than the primary family for explicit >1000°C / refractory review."
        )
        trace.append("Applied final extreme-temperature / refractory family calibration after generic creep bumps.")
    elif explicit_refractory_language:
        priors["Refractory alloy concept"] = max(priors.get("Refractory alloy concept", 0.0), 0.92)
        priors["Ni-based superalloy"] = min(priors.get("Ni-based superalloy", 0.0), 0.76)
        priors["Co-based alloy"] = min(priors.get("Co-based alloy", 0.0), 0.70)
        trace.append("Applied final explicit refractory family calibration.")


def _select_allowed_families(priors: Dict[str, float], hard_constraints: Dict[str, Any], temperature_c: int) -> Tuple[List[str], List[str]]:
    warnings: List[str] = []
    exclusions = set(hard_constraints.get("family_exclusions", []) or [])
    inclusions = set(hard_constraints.get("family_inclusions", []) or [])

    filtered = {fam: score for fam, score in priors.items() if fam not in exclusions}
    for fam in inclusions:
        if fam in FAMILY_KEYS and fam not in exclusions:
            filtered[fam] = max(filtered.get(fam, 0.0), 0.55)

    # Keep scope useful but not over-broad. This is a query-scope decision, not a survival filter.
    threshold = 0.36
    selected = [fam for fam, score in sorted(filtered.items(), key=lambda item: item[1], reverse=True) if score >= threshold]

    if len(selected) < 2:
        selected = [fam for fam, _ in sorted(filtered.items(), key=lambda item: item[1], reverse=True)[:2]]
    elif len(selected) > 4:
        selected = selected[:4]

    # Preserve high-temp baseline family trio unless a hard exclusion prevents it.
    if temperature_c >= 850:
        for fam in ["Ni-based superalloy", "Co-based alloy", "Refractory alloy concept"]:
            if fam not in exclusions and fam not in selected and filtered.get(fam, 0.0) >= 0.30:
                selected.append(fam)
        selected = selected[:4]

    if not selected:
        selected = ["Ni-based superalloy", "Co-based alloy", "Refractory alloy concept"]
        warnings.append("Scope planner fell back to default high-temperature metallic families.")

    return selected, warnings


def _build_active_factors(schema: Dict[str, Any]) -> Tuple[List[str], List[str], Dict[str, float]]:
    factor_importance = dict(schema.get("soft_objectives", {}).get("factor_importance", {}) or {})
    failure = dict(schema.get("failure_mode_priorities", {}) or {})
    lifecycle = dict(schema.get("lifecycle_priorities", {}) or {})

    active = set(BASELINE_FACTORS)

    activation_rules = {
        "lightweight": factor_importance.get("lightweight", 0.0) >= 0.30,
        "oxidation": (failure.get("oxidation", 0.0) >= 0.40
                      or failure.get("hot_corrosion", 0.0) >= 0.35
                      or factor_importance.get("oxidation", 0.0) >= 0.30),
        "hot_corrosion": failure.get("hot_corrosion", 0.0) >= 0.35 or factor_importance.get("hot_corrosion", 0.0) >= 0.30,
        "wear": failure.get("wear", 0.0) >= 0.35 or factor_importance.get("wear", 0.0) >= 0.30,
        "erosion": failure.get("erosion", 0.0) >= 0.35 or factor_importance.get("erosion", 0.0) >= 0.30,
        "fatigue": failure.get("fatigue", 0.0) >= 0.35 or factor_importance.get("fatigue", 0.0) >= 0.30,
        "thermal_fatigue": failure.get("thermal_fatigue", 0.0) >= 0.35 or factor_importance.get("thermal_fatigue", 0.0) >= 0.30,
        "repairability": lifecycle.get("repairability", 0.0) >= 0.30 or factor_importance.get("repairability", 0.0) >= 0.30,
        "certification_maturity": lifecycle.get("certification_maturity", 0.0) >= 0.30 or factor_importance.get("certification_maturity", 0.0) >= 0.30,
    }
    for factor, should_activate in activation_rules.items():
        if should_activate:
            active.add(factor)

    weights: Dict[str, float] = {}
    for factor in active:
        base_weight = factor_importance.get(factor, 0.0)
        if factor in failure:
            base_weight = max(base_weight, float(failure.get(factor, 0.0)) * 0.65)
        if factor in lifecycle:
            base_weight = max(base_weight, float(lifecycle.get(factor, 0.0)) * 0.65)
        if factor in BASELINE_FACTORS:
            base_weight = max(base_weight, 0.10)
        weights[factor] = round(base_weight, 3)

    ordered = sorted(active, key=lambda factor: (weights.get(factor, 0.0), factor), reverse=True)
    inactive = [factor for factor in OPTIONAL_FACTORS if factor not in active]
    return ordered, inactive, weights


def build_scope_plan(schema: Dict[str, Any]) -> ScopePlan:
    operating = schema.get("operating_envelope", {}) or {}
    hard_constraints = schema.get("hard_constraints", {}) or {}
    manufacturing = schema.get("manufacturing_intent", {}) or {}
    failure = schema.get("failure_mode_priorities", {}) or {}
    factor_importance = schema.get("soft_objectives", {}).get("factor_importance", {}) or {}
    temperature_c = int(operating.get("temperature_c", 850) or 850)
    inclusions = set(hard_constraints.get("family_inclusions", []) or [])
    prompt_text = str(schema.get("prompt_normalized", "") or "")
    explicit_refractory_intent = (
        "Refractory alloy concept" in inclusions
        or "refractory" in prompt_text
        or "molybdenum" in prompt_text
        or "niobium" in prompt_text
        or "tantalum" in prompt_text
        or "tungsten" in prompt_text
        or _has_extreme_temperature_language(prompt_text)
        or temperature_c >= 1050
    )

    priors = {
        "Ni-based superalloy": 0.42,
        "Co-based alloy": 0.34,
        "Fe-Ni alloy": 0.22,
        "Ti alloy": 0.24,
        "Refractory alloy concept": 0.26,
    }
    rationale: Dict[str, List[str]] = {family: ["Default aviation metallic-family prior."] for family in FAMILY_KEYS}
    trace: List[str] = []

    # Temperature-led family suitability.
    if temperature_c >= 1000:
        _bump(priors, "Refractory alloy concept", 0.40, rationale, "Extreme temperature strongly increases refractory relevance.")
        _bump(priors, "Ni-based superalloy", 0.18, rationale, "Extreme temperature keeps nickel superalloys relevant, but not automatically dominant.")
        _bump(priors, "Co-based alloy", 0.12, rationale, "Extreme temperature keeps cobalt hot-section alloys relevant as a secondary option.")
        _bump(priors, "Ti alloy", -0.18, rationale, "Extreme temperature reduces titanium-family suitability.")
        _bump(priors, "Fe-Ni alloy", -0.14, rationale, "Extreme temperature reduces Fe-Ni-family suitability.")
        if explicit_refractory_intent or temperature_c >= 1050:
            _set_min(priors, "Refractory alloy concept", 0.92, rationale, "Explicit refractory or >1050°C intent makes refractory concepts the primary family to review.")
            _cap_max(priors, "Ni-based superalloy", 0.76, rationale, "Explicit extreme/refractory intent caps nickel so mature references do not dominate by default.")
            _cap_max(priors, "Co-based alloy", 0.68, rationale, "Explicit extreme/refractory intent caps cobalt as a secondary family.")
        trace.append("Applied extreme-temperature family priors.")
    elif temperature_c >= 850:
        _bump(priors, "Ni-based superalloy", 0.28, rationale, "Hot-section temperature increases nickel superalloy relevance.")
        _bump(priors, "Co-based alloy", 0.20, rationale, "Hot-section temperature increases cobalt alloy relevance.")
        _bump(priors, "Refractory alloy concept", 0.16, rationale, "Hot-section temperature increases refractory concept relevance.")
        _bump(priors, "Ti alloy", -0.12, rationale, "Hot-section temperature reduces titanium-family suitability.")
        trace.append("Applied hot-section family priors.")
    elif temperature_c <= 650:
        _bump(priors, "Ti alloy", 0.30, rationale, "Moderate/elevated temperature keeps titanium lightweight structures relevant.")
        _bump(priors, "Fe-Ni alloy", 0.10, rationale, "Moderate temperature keeps Fe-Ni systems in scope.")
        trace.append("Applied moderate-temperature family priors.")

    # Failure-mode and prompt-led priors.
    if failure.get("creep", 0.0) >= 0.55:
        _bump(priors, "Ni-based superalloy", 0.24, rationale, "Creep priority favours nickel superalloy experience.")
        _bump(priors, "Co-based alloy", 0.10, rationale, "Creep priority keeps cobalt high-temperature alloys relevant.")
        _bump(priors, "Refractory alloy concept", 0.12, rationale, "Creep priority keeps refractory concepts relevant for very hot service.")
        trace.append("Applied creep-priority family priors.")

    if failure.get("hot_corrosion", 0.0) >= 0.35:
        _bump(priors, "Co-based alloy", 0.34, rationale, "Hot corrosion priority favours cobalt-family concepts.")
        _bump(priors, "Ni-based superalloy", 0.14, rationale, "Hot corrosion priority keeps nickel oxidation/corrosion alloys relevant.")
        trace.append("Applied hot-corrosion family priors.")

    if failure.get("wear", 0.0) >= 0.35:
        _bump(priors, "Co-based alloy", 0.32, rationale, "Wear/contact priority favours cobalt-family concepts.")
        _bump(priors, "Refractory alloy concept", 0.06, rationale, "Wear/contact priority can support hard refractory-containing concepts.")
        trace.append("Applied wear family priors.")

    if explicit_refractory_intent:
        _set_min(priors, "Refractory alloy concept", 0.86, rationale, "Prompt explicitly mentions refractory-family chemistry or refractory service intent.")
        if temperature_c >= 950:
            _set_min(priors, "Refractory alloy concept", 0.95, rationale, "Refractory intent combined with very high temperature makes refractory the primary family.")
            _cap_max(priors, "Ni-based superalloy", 0.74, rationale, "Refractory intent keeps nickel as a comparison family rather than the default winner.")
            _cap_max(priors, "Co-based alloy", 0.68, rationale, "Refractory intent keeps cobalt as a comparison family rather than the default winner.")
        trace.append("Applied explicit refractory family prior.")

    if factor_importance.get("lightweight", 0.0) >= 0.30 or hard_constraints.get("must_be_lightweight"):
        _bump(priors, "Ti alloy", 0.46, rationale, "Lightweight / strength-to-weight priority strongly favours titanium.")
        _bump(priors, "Fe-Ni alloy", -0.04, rationale, "Lightweight priority weakens Fe-Ni fit.")
        _bump(priors, "Co-based alloy", -0.12, rationale, "Lightweight priority weakens dense cobalt-family fit.")
        _bump(priors, "Refractory alloy concept", -0.18, rationale, "Lightweight priority weakens dense refractory-family fit.")
        if temperature_c <= 750:
            _set_min(priors, "Ti alloy", 0.72, rationale, "Temperature is compatible enough to keep titanium highly visible.")
        trace.append("Applied lightweight family priors.")

    preferred_routes = set(manufacturing.get("preferred_routes", []) or [])
    if "AM" in preferred_routes:
        _bump(priors, "Ti alloy", 0.08, rationale, "AM preference modestly favours titanium route maturity.")
        _bump(priors, "Ni-based superalloy", 0.07, rationale, "AM preference modestly favours nickel route maturity.")
        trace.append("Applied AM-route family priors.")
    if "conventional" in preferred_routes:
        _bump(priors, "Ni-based superalloy", 0.04, rationale, "Conventional route preference keeps mature wrought/cast nickel routes relevant.")
        _bump(priors, "Fe-Ni alloy", 0.05, rationale, "Conventional route preference keeps Fe-Ni systems relevant.")
        trace.append("Applied conventional-route family priors.")

    _apply_extreme_refractory_final_calibration(
        priors,
        rationale,
        trace,
        temperature_c=temperature_c,
        prompt_text=prompt_text,
        inclusions=inclusions,
    )

    priors = _normalise_priors(priors)
    allowed, warnings = _select_allowed_families(priors, hard_constraints, temperature_c)
    active, inactive, weights = _build_active_factors(schema)

    retrieval_hints = {
        "family_seed_chemsys": [],
        "expansion_policy": "family-aware conservative expansion; baseline generator remains owner of retrieval and survival",
        "forced_chemsys": None,
        "notes": [
            "Scope planner intentionally produces hints and family scope only; it does not score candidates or filter survivors.",
        ],
    }

    return {
        "scope_version": "scope_plan_v1",
        "allowed_families": allowed,
        "family_priors": priors,
        "family_rationale": {family: " ".join(bits) for family, bits in rationale.items()},
        "retrieval_hints": retrieval_hints,
        "active_factor_set": active,
        "inactive_factor_set": inactive,
        "active_factor_weights": weights,
        "scope_warnings": warnings,
        "planner_trace": trace or ["Default scope planning applied."],
    }
