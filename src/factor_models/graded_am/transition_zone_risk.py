from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


_LOW_MATURITY = {"D", "E", "F"}
_GRADIENT_CUES = (
    "gradient",
    "graded surface",
    "transition zone",
    "transition-zone",
    "additive",
    "composition gradient",
    "porosity gradient",
    "microstructure gradient",
    "hard-surface gradient",
    "hard surface gradient",
    "oxidation gradient",
    "thermal gradient",
    "multi-material transition",
    "multimaterial transition",
    "directed energy deposition",
    "powder bed fusion",
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=str)
    return [value]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _blob(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_blob(item)}" for key, item in value.items()).lower()
    if isinstance(value, (list, tuple, set)):
        return " ".join(_blob(item) for item in value).lower()
    return _text(value).lower()


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _field_text(candidate: Mapping[str, Any]) -> str:
    fields = {
        "candidate_id": candidate.get("candidate_id"),
        "system_name": candidate.get("system_name") or candidate.get("name"),
        "summary": candidate.get("summary"),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "base_material_family": candidate.get("base_material_family"),
        "constituents": candidate.get("constituents"),
        "gradient_architecture": candidate.get("gradient_architecture"),
        "process_route_details": candidate.get("process_route_details"),
        "route_risks": candidate.get("route_risks"),
        "route_benefits": candidate.get("route_benefits"),
        "route_validation_gaps": candidate.get("route_validation_gaps"),
        "inspection_plan": candidate.get("inspection_plan"),
        "repairability": candidate.get("repairability"),
        "qualification_route": candidate.get("qualification_route"),
        "surface_function_profile": candidate.get("surface_function_profile"),
        "processing_routes": candidate.get("processing_routes"),
        "process_route": candidate.get("process_route"),
        "risks": candidate.get("risks"),
        "assumptions": candidate.get("assumptions"),
        "provenance": candidate.get("provenance"),
    }
    return _blob({key: value for key, value in fields.items() if value not in (None, "", [], {})})


def _matched_terms(text: str, terms: Sequence[str]) -> list[str]:
    return [term for term in terms if term in text]


def _level_count(records: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(_text(record.get(field), "unknown") for record in records).items()))


def _kind_label(kind: str) -> str:
    return {
        "oxidation_resistant_surface_gradient": "Oxidation-resistant surface gradient",
        "thermal_barrier_or_porosity_gradient": "Thermal-barrier or porosity gradient",
        "wear_or_hard_surface_gradient": "Wear or hard-surface gradient",
        "metal_ceramic_transition_gradient": "Metal-ceramic transition gradient",
        "repair_or_build_up_gradient": "Repair or build-up gradient",
        "residual_stress_managed_gradient": "Residual-stress-managed gradient",
        "generic_spatial_gradient": "Generic spatial gradient",
        "not_gradient_relevant": "Not gradient relevant",
    }[kind]


def _gradient_architecture(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(candidate.get("gradient_architecture"))


def _gradient_architecture_summary(candidate: Mapping[str, Any]) -> str:
    gradient = _gradient_architecture(candidate)
    if gradient:
        types = [_text(item) for item in _as_list(gradient.get("gradient_types")) if _text(item)]
        manufacturing = _text(gradient.get("manufacturing_route"))
        notes = _text(gradient.get("notes"))
        parts = []
        if types:
            parts.append(", ".join(types))
        if manufacturing:
            parts.append(manufacturing)
        if notes:
            parts.append(notes)
        return " - ".join(parts) if parts else "spatial gradient architecture"
    routes = [_text(_mapping(item).get("route_name") or item) for item in _as_list(candidate.get("processing_routes")) if _text(_mapping(item).get("route_name") or item)]
    return "; ".join(routes) if routes else "gradient architecture not specified"


def _gradient_type(candidate: Mapping[str, Any]) -> str:
    gradient = _gradient_architecture(candidate)
    types = [_text(item) for item in _as_list(gradient.get("gradient_types")) if _text(item)]
    if types:
        return ", ".join(types)
    text = _field_text(candidate)
    if "porosity" in text:
        return "porosity"
    if "microstructure" in text:
        return "microstructure"
    if "composition" in text:
        return "composition"
    return "unknown"


def _surface_function_summary(candidate: Mapping[str, Any]) -> str:
    profile = _mapping(candidate.get("surface_function_profile"))
    functions = [
        _text(item)
        for item in _as_list(profile.get("primary_surface_functions")) + _as_list(profile.get("secondary_surface_functions"))
        if _text(item)
    ]
    if functions:
        return ", ".join(functions[:6])
    return _text(candidate.get("summary"), "surface function not specified")


def _raise_level(current: str, minimum: str) -> str:
    rank = {"low": 1, "medium": 2, "high": 3, "very_high": 4, "unknown": -1}
    if current == "unknown":
        return minimum
    return current if rank.get(current, 0) >= rank.get(minimum, 0) else minimum


def is_graded_am_transition_relevant_candidate(candidate: Mapping[str, Any]) -> bool:
    """Return whether transition-zone diagnostics are relevant for this candidate."""
    if _candidate_class(candidate) == "spatially_graded_am":
        return True
    if _architecture(candidate) == "spatial_gradient":
        return True
    text = _field_text(candidate)
    return any(cue in text for cue in _GRADIENT_CUES)


def classify_gradient_architecture(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a graded architecture using conservative deterministic cues."""
    if not is_graded_am_transition_relevant_candidate(candidate):
        return {
            "gradient_system_kind": "not_gradient_relevant",
            "gradient_system_label": _kind_label("not_gradient_relevant"),
            "classification_confidence": "high",
            "classification_evidence_terms": [],
            "conservative_notes": ["No spatial-gradient, additive or transition-zone cues were visible."],
        }
    text = _field_text(candidate)
    rules = [
        (
            "oxidation_resistant_surface_gradient",
            ("oxidation", "environmental", "corrosion", "steam", "oxide-forming", "oxide forming"),
        ),
        (
            "thermal_barrier_or_porosity_gradient",
            ("thermal barrier", "porosity", "thermal gradient", "insulating", "thermal expansion"),
        ),
        ("wear_or_hard_surface_gradient", ("wear", "hard surface", "hard-surface", "contact", "hardness", "carbide")),
        (
            "metal_ceramic_transition_gradient",
            ("metal-ceramic", "metal ceramic", "metal-to-ceramic", "multi-material", "multimaterial", "ceramic-rich"),
        ),
        ("repair_or_build_up_gradient", ("repair", "buildup", "build-up", "restoration")),
        ("residual_stress_managed_gradient", ("residual stress", "stress managed", "stress relief")),
    ]
    matches = [(kind, _matched_terms(text, terms)) for kind, terms in rules]
    matches = [(kind, terms) for kind, terms in matches if terms]
    if matches:
        kind, terms = matches[0]
        confidence = "high" if len(set(terms)) >= 2 or _candidate_class(candidate) == "spatially_graded_am" else "medium"
    else:
        kind = "generic_spatial_gradient"
        terms = _matched_terms(text, _GRADIENT_CUES)
        confidence = "medium" if terms else "low"
    notes = ["Classification is deterministic and conservative; it is not a process qualification claim."]
    if kind == "generic_spatial_gradient":
        notes.append("Gradient role is visible but the architecture is not specific enough for a narrower class.")
    return {
        "gradient_system_kind": kind,
        "gradient_system_label": _kind_label(kind),
        "classification_confidence": confidence,
        "classification_evidence_terms": list(dict.fromkeys(terms)),
        "conservative_notes": notes,
    }


def build_graded_am_transition_zone_profile(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic transition-zone diagnostic profile for a graded AM system."""
    classification = classify_gradient_architecture(candidate)
    kind = classification["gradient_system_kind"]
    maturity = _evidence_maturity(candidate)
    text = _field_text(candidate)
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))
    inspection_burden = _text(inspection.get("inspection_burden"), "unknown")
    repairability_level = _text(repairability.get("repairability_level"), "unknown")
    qualification_burden = _text(qualification.get("qualification_burden"), "unknown")

    profile = {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "evidence_maturity": maturity,
        **classification,
        "gradient_architecture_summary": _gradient_architecture_summary(candidate),
        "gradient_type": _gradient_type(candidate),
        "surface_function_summary": _surface_function_summary(candidate),
        "transition_zone_complexity": "unknown",
        "residual_stress_risk": "unknown",
        "cracking_or_delamination_risk": "unknown",
        "process_window_sensitivity": "unknown",
        "through_depth_inspection_difficulty": "unknown",
        "repairability_constraint": "unknown",
        "qualification_burden": qualification_burden,
        "maturity_constraint": "",
        "key_failure_modes": [],
        "gradient_strengths": [],
        "gradient_concerns": [],
        "required_validation_evidence": [],
        "inspection_and_repair_notes": [],
        "not_a_process_qualification_claim": True,
        "not_a_life_prediction": True,
        "not_a_final_recommendation": True,
    }
    if kind == "not_gradient_relevant":
        profile["gradient_concerns"] = ["Graded AM transition-zone diagnostics are not relevant to this candidate."]
        return profile

    strengths = [_text(item) for item in _as_list(candidate.get("route_benefits")) if _text(item)]
    concerns = [_text(item) for item in _as_list(candidate.get("route_risks")) if _text(item)]
    validation = [_text(item) for item in _as_list(candidate.get("route_validation_gaps")) if _text(item)]
    failure_modes: list[str] = []
    notes: list[str] = []

    if kind == "oxidation_resistant_surface_gradient":
        profile.update(
            {
                "transition_zone_complexity": "high",
                "residual_stress_risk": "medium",
                "cracking_or_delamination_risk": "high" if "cracking" in text else "medium",
                "process_window_sensitivity": "high",
            }
        )
        failure_modes.extend(["transition-zone cracking", "composition-control drift", "environmental underperformance"])
        strengths.append("oxidation-resistant surface function is explicit")
        concerns.extend(["environmental validation", "through-depth composition verification", "transition-zone risk"])
        validation.extend(["environmental exposure evidence", "through-depth composition evidence", "transition-zone property evidence"])
    elif kind == "thermal_barrier_or_porosity_gradient":
        profile.update(
            {
                "transition_zone_complexity": "high",
                "residual_stress_risk": "high" if "thermal expansion" in text else "medium",
                "cracking_or_delamination_risk": "high",
                "process_window_sensitivity": "high",
            }
        )
        failure_modes.extend(["thermal-cycle cracking", "delamination", "porosity-control drift", "through-depth property scatter"])
        strengths.append("thermal-barrier or porosity-gradient intent is explicit")
        concerns.extend(["thermal cycling durability", "porosity control", "through-depth verification", "qualification immaturity"])
        validation.extend(["thermal cycling evidence", "porosity mapping evidence", "through-depth thermal/property verification"])
    elif kind == "wear_or_hard_surface_gradient":
        profile.update(
            {
                "transition_zone_complexity": "medium",
                "residual_stress_risk": "high",
                "cracking_or_delamination_risk": "high",
                "process_window_sensitivity": "medium",
            }
        )
        failure_modes.extend(["hard-zone cracking", "residual-stress distortion", "fatigue debit", "surface finishing damage"])
        strengths.append("wear or hard-surface function is explicit")
        concerns.extend(["residual stress", "surface integrity", "hardness mapping", "finishing response"])
        validation.extend(["residual stress evidence", "hardness mapping evidence", "surface integrity evidence", "fatigue compatibility evidence"])
    elif kind == "metal_ceramic_transition_gradient":
        profile.update(
            {
                "transition_zone_complexity": "high",
                "residual_stress_risk": "high",
                "cracking_or_delamination_risk": "high",
                "process_window_sensitivity": "high",
            }
        )
        failure_modes.extend(["chemical incompatibility", "transition-zone cracking", "delamination", "residual stress"])
        concerns.extend(["interface compatibility", "transition-zone complexity", "process-window sensitivity"])
        validation.extend(["metal/ceramic compatibility evidence", "transition-zone microstructure evidence", "cracking/delamination evidence"])
    elif kind == "repair_or_build_up_gradient":
        profile.update(
            {
                "transition_zone_complexity": "medium",
                "residual_stress_risk": "high",
                "cracking_or_delamination_risk": "medium",
                "process_window_sensitivity": "high",
            }
        )
        failure_modes.extend(["repair repeatability limits", "bond-line defects", "residual-stress cracking"])
        strengths.append("repair-oriented restoration role is explicit")
        concerns.extend(["repeatability", "local restoration constraints", "acceptance criteria"])
        validation.extend(["repair repeatability evidence", "local acceptance criteria", "bond-line inspection evidence"])
    elif kind == "residual_stress_managed_gradient":
        profile.update(
            {
                "transition_zone_complexity": "medium",
                "residual_stress_risk": "high",
                "cracking_or_delamination_risk": "medium",
                "process_window_sensitivity": "high",
            }
        )
        failure_modes.extend(["residual-stress scatter", "process-window drift", "through-depth property scatter"])
        strengths.append("residual-stress management intent is explicit")
        concerns.extend(["residual stress verification", "process parameter sensitivity", "through-depth property scatter"])
        validation.extend(["residual stress mapping evidence", "process-window evidence", "through-depth property verification"])
    else:
        profile.update(
            {
                "transition_zone_complexity": "medium",
                "residual_stress_risk": "medium",
                "cracking_or_delamination_risk": "medium",
                "process_window_sensitivity": "medium",
            }
        )
        failure_modes.extend(["transition-zone cracking", "property scatter", "process-window sensitivity"])
        concerns.extend(["transition-zone verification", "process repeatability", "inspection and repair assumptions"])
        validation.extend(["transition-zone property evidence", "process repeatability evidence", "through-depth inspection evidence"])

    if "residual stress" in text:
        profile["residual_stress_risk"] = _raise_level(profile["residual_stress_risk"], "high")
    if any(term in text for term in ("cracking", "crack", "delamination")):
        profile["cracking_or_delamination_risk"] = _raise_level(profile["cracking_or_delamination_risk"], "high")
    if any(term in text for term in ("process window", "repeatability", "composition control", "porosity control")):
        profile["process_window_sensitivity"] = _raise_level(profile["process_window_sensitivity"], "high")

    if inspection_burden == "high":
        profile["through_depth_inspection_difficulty"] = "high"
    elif inspection_burden == "medium":
        profile["through_depth_inspection_difficulty"] = "medium"
    elif inspection_burden == "low":
        profile["through_depth_inspection_difficulty"] = "low"
    else:
        profile["through_depth_inspection_difficulty"] = "medium"

    if repairability_level == "poor":
        profile["repairability_constraint"] = "high"
    elif repairability_level == "limited":
        profile["repairability_constraint"] = "high" if kind in {"repair_or_build_up_gradient", "metal_ceramic_transition_gradient"} else "medium"
    elif repairability_level == "moderate":
        profile["repairability_constraint"] = "medium"
    elif repairability_level == "good":
        profile["repairability_constraint"] = "low"
    else:
        profile["repairability_constraint"] = "medium"

    if maturity in _LOW_MATURITY:
        profile["maturity_constraint"] = (
            f"Evidence maturity {maturity} keeps this graded AM system exploratory or validation-limited."
        )
        concerns.append(profile["maturity_constraint"])
        validation.append("higher maturity graded AM transition-zone evidence")
    if qualification_burden in {"high", "very_high"}:
        concerns.append(f"Process-route enrichment exposes {qualification_burden} qualification burden.")
    elif maturity in _LOW_MATURITY:
        profile["qualification_burden"] = "high"

    if inspection_burden == "high":
        notes.append("Process-route enrichment exposes high inspection burden for through-depth verification.")
    else:
        notes.append("Through-depth inspection approach should remain explicit for gradient verification.")
    if repairability_level in {"limited", "poor"}:
        notes.append(f"Process-route enrichment exposes {repairability_level} repairability.")
    else:
        notes.append("Repair acceptance criteria should be validated before any restoration use.")

    profile["key_failure_modes"] = list(dict.fromkeys(_text(item) for item in failure_modes if _text(item)))[:8]
    profile["gradient_strengths"] = list(dict.fromkeys(_text(item) for item in strengths if _text(item)))[:6]
    profile["gradient_concerns"] = list(dict.fromkeys(_text(item) for item in concerns if _text(item)))[:8]
    profile["required_validation_evidence"] = list(dict.fromkeys(_text(item) for item in validation if _text(item)))[:8]
    profile["inspection_and_repair_notes"] = list(dict.fromkeys(_text(item) for item in notes if _text(item)))[:6]
    return profile


def build_graded_am_transition_zone_summary(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    candidate_list = [candidate for candidate in candidates if isinstance(candidate, Mapping)]
    profiles = []
    for candidate in candidate_list:
        profile = _mapping(candidate.get("graded_am_transition_zone_risk"))
        if not profile and is_graded_am_transition_relevant_candidate(candidate):
            profile = build_graded_am_transition_zone_profile(candidate)
        if profile and profile.get("gradient_system_kind") != "not_gradient_relevant":
            profiles.append(dict(profile))

    themes = sorted(
        {
            _text(item)
            for profile in profiles
            for item in _as_list(profile.get("required_validation_evidence"))
            if _text(item)
        }
    )
    maturity_counts = Counter("constrained" if _text(profile.get("maturity_constraint")) else "not_flagged" for profile in profiles)
    warnings = []
    if any(profile.get("transition_zone_complexity") == "high" for profile in profiles):
        warnings.append("High graded AM transition-zone complexity is visible.")
    if any(profile.get("residual_stress_risk") == "high" for profile in profiles):
        warnings.append("High graded AM residual-stress risk is visible.")
    if any(profile.get("through_depth_inspection_difficulty") == "high" for profile in profiles):
        warnings.append("High graded AM through-depth inspection difficulty is visible.")
    if any(_text(profile.get("evidence_maturity")).upper() in _LOW_MATURITY for profile in profiles):
        warnings.append("D/E/F maturity appears on one or more graded AM systems.")

    return {
        "candidate_count": len(candidate_list),
        "relevant_candidate_count": len(profiles),
        "gradient_system_kind_counts": _level_count(profiles, "gradient_system_kind"),
        "transition_zone_complexity_counts": _level_count(profiles, "transition_zone_complexity"),
        "residual_stress_risk_counts": _level_count(profiles, "residual_stress_risk"),
        "cracking_or_delamination_risk_counts": _level_count(profiles, "cracking_or_delamination_risk"),
        "process_window_sensitivity_counts": _level_count(profiles, "process_window_sensitivity"),
        "through_depth_inspection_difficulty_counts": _level_count(profiles, "through_depth_inspection_difficulty"),
        "repairability_constraint_counts": _level_count(profiles, "repairability_constraint"),
        "qualification_burden_counts": _level_count(profiles, "qualification_burden"),
        "maturity_constraint_counts": dict(sorted(maturity_counts.items())),
        "high_transition_complexity_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("transition_zone_complexity") == "high"
        ],
        "high_residual_stress_risk_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("residual_stress_risk") == "high"
        ],
        "high_cracking_or_delamination_risk_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("cracking_or_delamination_risk") == "high"
        ],
        "high_process_window_sensitivity_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("process_window_sensitivity") == "high"
        ],
        "high_inspection_difficulty_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("through_depth_inspection_difficulty") == "high"
        ],
        "high_repairability_constraint_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("repairability_constraint") == "high"
        ],
        "high_qualification_burden_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("qualification_burden") in {"high", "very_high"}
        ],
        "low_maturity_gradient_candidate_ids": [
            profile["candidate_id"] for profile in profiles if _text(profile.get("evidence_maturity")).upper() in _LOW_MATURITY
        ],
        "required_validation_evidence_themes": themes,
        "warnings": warnings,
    }


def attach_graded_am_transition_zone_risk(package: Mapping[str, Any]) -> dict[str, Any]:
    """Attach graded AM transition-zone diagnostics without mutating package input."""
    output = dict(package)
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    enriched_candidates = []
    for candidate in candidates:
        enriched = dict(candidate)
        if is_graded_am_transition_relevant_candidate(candidate):
            enriched["graded_am_transition_zone_risk"] = build_graded_am_transition_zone_profile(candidate)
        enriched_candidates.append(enriched)
    summary = build_graded_am_transition_zone_summary(enriched_candidates)
    output["candidate_systems"] = enriched_candidates
    output["graded_am_transition_zone_summary"] = summary
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))

    warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    warning_rules = [
        ("high_transition_complexity_candidate_ids", "high graded AM transition-zone complexity"),
        ("high_residual_stress_risk_candidate_ids", "high graded AM residual-stress risk"),
        ("high_cracking_or_delamination_risk_candidate_ids", "high graded AM cracking/delamination risk"),
        ("high_process_window_sensitivity_candidate_ids", "high graded AM process-window sensitivity"),
        ("high_inspection_difficulty_candidate_ids", "high graded AM through-depth inspection difficulty"),
        ("high_repairability_constraint_candidate_ids", "high graded AM repairability constraint"),
        ("high_qualification_burden_candidate_ids", "high or very high graded AM qualification burden"),
        ("low_maturity_gradient_candidate_ids", "D/E/F maturity on graded AM system"),
    ]
    for field, label in warning_rules:
        for candidate_id in _as_list(summary.get(field)):
            warning = f"{candidate_id}: {label} is visible in diagnostic profile."
            if warning not in warnings:
                warnings.append(warning)
    for warning in _as_list(summary.get("warnings")):
        text = _text(warning)
        if text and text not in warnings:
            warnings.append(text)
    output["warnings"] = warnings

    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "graded_am_transition_zone_risk_attached": True,
            "graded_am_transition_relevant_candidate_count": summary["relevant_candidate_count"],
        }
    )
    output["diagnostics"] = diagnostics
    return output
