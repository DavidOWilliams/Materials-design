from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from src.application_profiles import get_default_application_profile, normalise_application_profile


_MATURITY_RANK = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "F": 1}
_SUPPORT_OR_RISK_FUNCTIONS = {
    "inspection_access_or_monitoring",
    "repairability_support",
    "coating_interface_management",
    "transition_zone_management",
}
_HOT_SECTION_REQUIRED = {"thermal_barrier", "oxidation_resistance"}


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


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    maturity = _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()
    return maturity if maturity in _MATURITY_RANK else "unknown"


def _primary_service_functions(candidate: Mapping[str, Any]) -> list[str]:
    profile = _mapping(candidate.get("surface_function_profile"))
    functions = [
        _text(item)
        for item in _as_list(profile.get("primary_service_functions"))
        if _text(item) and _text(item) not in _SUPPORT_OR_RISK_FUNCTIONS
    ]
    if functions:
        return list(dict.fromkeys(functions))
    text = _blob(
        {
            "candidate_id": candidate.get("candidate_id"),
            "system_name": candidate.get("system_name") or candidate.get("name"),
            "summary": candidate.get("summary"),
            "coating": candidate.get("coating_or_surface_system") or candidate.get("coating_system"),
            "environmental_barrier_coating": candidate.get("environmental_barrier_coating"),
            "gradient": candidate.get("gradient_architecture"),
            "route_benefits": candidate.get("route_benefits"),
        }
    )
    inferred = []
    for function_id, terms in (
        ("thermal_barrier", ("tbc", "thermal barrier", "thermal protection")),
        ("environmental_barrier", ("ebc", "environmental barrier")),
        ("steam_recession_resistance", ("steam", "water vapor", "recession")),
        ("oxidation_resistance", ("oxidation", "oxidation-resistant", "corrosion")),
        ("wear_resistance", ("wear", "fretting", "hard surface")),
        ("erosion_resistance", ("erosion",)),
        ("hard_surface", ("hard surface", "hard-surface", "hard coating")),
    ):
        if any(term in text for term in terms):
            inferred.append(function_id)
    return list(dict.fromkeys(inferred))


def _secondary_service_functions(candidate: Mapping[str, Any]) -> list[str]:
    profile = _mapping(candidate.get("surface_function_profile"))
    functions = [
        _text(item)
        for item in _as_list(profile.get("secondary_service_functions"))
        if _text(item) and _text(item) not in _SUPPORT_OR_RISK_FUNCTIONS
    ]
    text = _blob(candidate)
    if "thermal_cycling_tolerance" not in functions and any(
        term in text for term in ("thermal cycling", "thermal-cycle", "thermal fatigue")
    ):
        functions.append("thermal_cycling_tolerance")
    return list(dict.fromkeys(functions))


def _readiness_status(candidate: Mapping[str, Any]) -> str:
    return _text(_mapping(candidate.get("decision_readiness")).get("readiness_status"), "unknown")


def is_hot_section_profile(profile: Mapping[str, Any]) -> bool:
    app = normalise_application_profile(profile)
    required = {_text(item) for item in _as_list(app.get("required_primary_service_functions")) if _text(item)}
    if app.get("profile_id") == "hot_section_thermal_cycling_oxidation":
        return True
    if _HOT_SECTION_REQUIRED <= required:
        return True
    text = _blob(
        {
            "profile_id": app.get("profile_id"),
            "display_name": app.get("display_name"),
            "description": app.get("description"),
            "service_environment": app.get("service_environment"),
        }
    )
    return "hot-section" in text and "thermal" in text and "oxidation" in text


def has_cmc_ebc_environmental_protection_path(candidate: Mapping[str, Any]) -> bool:
    candidate_class = _candidate_class(candidate)
    primary = set(_primary_service_functions(candidate))
    text = _blob(
        {
            "candidate_id": candidate.get("candidate_id"),
            "system_name": candidate.get("system_name") or candidate.get("name"),
            "candidate_class": candidate.get("candidate_class"),
            "system_architecture_type": candidate.get("system_architecture_type"),
            "coating_or_surface_system": candidate.get("coating_or_surface_system"),
            "environmental_barrier_coating": candidate.get("environmental_barrier_coating"),
            "surface_function_profile": candidate.get("surface_function_profile"),
            "cmc_ebc_environmental_durability": candidate.get("cmc_ebc_environmental_durability"),
            "coating_spallation_adhesion": candidate.get("coating_spallation_adhesion"),
            "process_route_profile": candidate.get("process_route_profile"),
            "summary": candidate.get("summary"),
        }
    )
    ebc_terms = (
        "ebc",
        "environmental barrier",
        "rare-earth silicate",
        "rare earth silicate",
        "steam recession",
        "recession",
        "cmc with ebc",
        "cmc+ebc",
        "oxidation protection",
    )
    has_environmental_function = bool(primary & {"environmental_barrier", "steam_recession_resistance"})
    has_ebc_cue = any(term in text for term in ebc_terms)
    if candidate_class == "ceramic_matrix_composite" and has_ebc_cue:
        return True
    if candidate_class == "coating_enabled" and has_environmental_function and has_ebc_cue:
        return True
    return has_environmental_function and has_ebc_cue and "cmc" in text


def detect_hot_section_architecture_path(
    candidate: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    primary = set(_primary_service_functions(candidate))
    candidate_class = _candidate_class(candidate)
    text = _blob(
        {
            "candidate_id": candidate.get("candidate_id"),
            "system_name": candidate.get("system_name") or candidate.get("name"),
            "candidate_class": candidate.get("candidate_class"),
            "system_architecture_type": candidate.get("system_architecture_type"),
            "coating_or_surface_system": candidate.get("coating_or_surface_system"),
            "environmental_barrier_coating": candidate.get("environmental_barrier_coating"),
            "surface_function_profile": candidate.get("surface_function_profile"),
            "cmc_ebc_environmental_durability": candidate.get("cmc_ebc_environmental_durability"),
            "coating_spallation_adhesion": candidate.get("coating_spallation_adhesion"),
            "gradient_architecture": candidate.get("gradient_architecture"),
        }
    )
    tbc_terms = ("tbc", "thermal barrier", "bond coat", "bondcoat", "top coat", "ceramic top coat")
    if candidate_class == "spatially_graded_am":
        return {
            "architecture_path": "graded_am_research_path",
            "path_matched_required_functions": sorted(primary & _HOT_SECTION_REQUIRED),
            "path_missing_required_functions": sorted(_HOT_SECTION_REQUIRED - primary),
            "path_cautions": ["Spatially graded AM concepts remain exploratory/research paths for this profile."],
            "path_required_next_evidence": ["graded transition-zone validation for the target hot-section application"],
            "path_rationale": ["Candidate is a spatially graded AM architecture."],
        }
    if is_hot_section_profile(profile) and (
        _HOT_SECTION_REQUIRED <= primary
        or candidate_class == "coating_enabled"
        and any(term in text for term in tbc_terms)
    ):
        return {
            "architecture_path": "coated_metallic_tbc_path",
            "path_matched_required_functions": sorted(_HOT_SECTION_REQUIRED & (primary | _HOT_SECTION_REQUIRED)),
            "path_missing_required_functions": sorted(_HOT_SECTION_REQUIRED - primary),
            "path_cautions": [],
            "path_required_next_evidence": ["coating durability and thermal-cycling validation"],
            "path_rationale": [
                "Candidate follows the coated metallic/TBC hot-section protection path.",
            ],
        }
    if is_hot_section_profile(profile) and has_cmc_ebc_environmental_protection_path(candidate):
        matched = sorted(primary & {"environmental_barrier", "steam_recession_resistance", "oxidation_resistance"})
        return {
            "architecture_path": "cmc_ebc_environmental_protection_path",
            "path_matched_required_functions": matched,
            "path_missing_required_functions": sorted(_HOT_SECTION_REQUIRED - primary),
            "path_cautions": [
                "CMC/EBC path is an alternative environmental-protection architecture, not a direct TBC equivalence.",
                "EBC dependency and oxidation/steam recession behaviour remain validation-heavy.",
                "CTE, interface/interphase compatibility, inspection, repair and qualification evidence are required.",
            ],
            "path_required_next_evidence": [
                "environment-specific EBC durability evidence",
                "steam recession evidence",
                "EBC/substrate compatibility evidence",
                "interphase recession evidence where relevant",
                "inspection and repair acceptance criteria",
                "comparison against Ni/TBC reference architecture",
            ],
            "path_rationale": [
                "Candidate has CMC/EBC or rare-earth silicate environmental-barrier cues relevant to hot-section protection.",
                "Missing literal thermal_barrier is treated as an architecture difference, not an automatic poor-fit blocker.",
            ],
        }
    if primary & {"wear_resistance", "erosion_resistance", "hard_surface"} and not primary & _HOT_SECTION_REQUIRED:
        return {
            "architecture_path": "wear_or_erosion_path",
            "path_matched_required_functions": sorted(primary & {"wear_resistance", "erosion_resistance", "hard_surface"}),
            "path_missing_required_functions": sorted(_HOT_SECTION_REQUIRED - primary),
            "path_cautions": ["Wear/erosion service functions do not satisfy the default hot-section thermal/oxidation path."],
            "path_required_next_evidence": ["changed application requirements or added thermal/oxidation protection evidence"],
            "path_rationale": ["Candidate is dominated by wear, erosion or hard-surface functions."],
        }
    if primary & {"oxidation_resistance"} and "thermal_barrier" not in primary:
        return {
            "architecture_path": "oxidation_protection_only_path",
            "path_matched_required_functions": ["oxidation_resistance"],
            "path_missing_required_functions": ["thermal_barrier"],
            "path_cautions": ["Oxidation protection alone does not satisfy the default hot-section thermal-barrier need."],
            "path_required_next_evidence": ["thermal-barrier relevance or changed application requirements"],
            "path_rationale": ["Candidate provides oxidation protection without a thermal-barrier path."],
        }
    if candidate_class == "monolithic_ceramic":
        return {
            "architecture_path": "monolithic_ceramic_path",
            "path_matched_required_functions": sorted(primary & _HOT_SECTION_REQUIRED),
            "path_missing_required_functions": sorted(_HOT_SECTION_REQUIRED - primary),
            "path_cautions": ["Monolithic ceramic record does not show a discrete hot-section protection architecture."],
            "path_required_next_evidence": ["explicit hot-section thermal and oxidation protection evidence"],
            "path_rationale": ["Candidate is a monolithic ceramic reference."],
        }
    return {
        "architecture_path": "unknown_path",
        "path_matched_required_functions": sorted(primary & _HOT_SECTION_REQUIRED),
        "path_missing_required_functions": sorted(_HOT_SECTION_REQUIRED - primary),
        "path_cautions": [],
        "path_required_next_evidence": [],
        "path_rationale": ["No deterministic hot-section architecture path was identified."],
    }


def _evidence_alignment(maturity: str, profile: Mapping[str, Any], readiness_status: str) -> str:
    if maturity == "F" or readiness_status == "research_only":
        return "research_only"
    minimum = _text(profile.get("minimum_evidence_maturity_for_engineering_use"), "C").upper()
    if maturity in _MATURITY_RANK and minimum in _MATURITY_RANK:
        return "meets_minimum" if _MATURITY_RANK[maturity] >= _MATURITY_RANK[minimum] else "below_minimum"
    return "unknown"


def _exposure_alignment(candidate: Mapping[str, Any], profile: Mapping[str, Any], matched_required: Sequence[str]) -> str:
    if not matched_required:
        return "weakly_aligned"
    text = _blob(candidate)
    matched = 0
    expected = 0
    if profile.get("thermal_exposure_level") in {"high", "very_high"}:
        expected += 1
        if any(term in text for term in ("thermal", "hot-section", "high temperature", "tbc")):
            matched += 1
    if profile.get("oxidation_or_steam_exposure") == "high":
        expected += 1
        if any(term in text for term in ("oxidation", "steam", "environmental barrier", "ebc", "recession")):
            matched += 1
    if profile.get("erosion_or_wear_exposure") == "high":
        expected += 1
        if any(term in text for term in ("wear", "erosion", "fretting", "hard surface")):
            matched += 1
    if expected == 0:
        return "unknown"
    if matched == expected:
        return "aligned"
    if matched:
        return "partially_aligned"
    return "weakly_aligned"


def _inspection_repair_alignment(candidate: Mapping[str, Any], profile: Mapping[str, Any]) -> tuple[str, list[str], list[str]]:
    cautions: list[str] = []
    blockers: list[str] = []
    inspection = _mapping(candidate.get("inspection_plan"))
    repair = _mapping(candidate.get("repairability"))
    coating = _mapping(candidate.get("coating_spallation_adhesion"))
    graded = _mapping(candidate.get("graded_am_transition_zone_risk"))
    inspection_burden = _text(inspection.get("inspection_burden"), "unknown")
    repairability = _text(repair.get("repairability_level"), "unknown")
    if profile.get("inspection_access") == "difficult" and (
        inspection_burden == "high"
        or coating.get("inspection_difficulty") == "high"
        or graded.get("through_depth_inspection_difficulty") == "high"
    ):
        cautions.append("High inspection difficulty conflicts with difficult application inspection access.")
    if profile.get("repairability_expectation") == "repair_required":
        if repairability == "poor" or coating.get("repairability_constraint") == "high" or graded.get("repairability_constraint") == "high":
            blockers.append("Repair is required but repairability is poor or highly constrained.")
        elif repairability in {"limited", "unknown"}:
            cautions.append("Repair is required but repairability evidence is limited or unknown.")
    elif profile.get("repairability_expectation") == "repair_desired" and (
        repairability in {"limited", "poor"}
        or coating.get("repairability_constraint") == "high"
        or graded.get("repairability_constraint") == "high"
    ):
        cautions.append("Repair is desired and repairability is limited or highly constrained.")
    if blockers:
        return "poor", cautions, blockers
    if cautions:
        return "caution", cautions, blockers
    if inspection_burden == "unknown" and repairability == "unknown":
        return "unknown", cautions, blockers
    return "aligned", cautions, blockers


def _certification_alignment(candidate: Mapping[str, Any], profile: Mapping[str, Any]) -> tuple[str, list[str]]:
    qualification = _mapping(candidate.get("qualification_route"))
    burden = _text(qualification.get("qualification_burden"), "unknown")
    sensitivity = _text(profile.get("certification_sensitivity"), "high")
    if sensitivity in {"high", "very_high"} and burden == "very_high":
        return "poor", ["Very high qualification burden conflicts with high certification sensitivity."]
    if sensitivity in {"high", "very_high"} and burden in {"high", "unknown"}:
        return "caution", [f"Qualification burden is {burden} for a {sensitivity} certification-sensitivity profile."]
    if burden == "unknown":
        return "unknown", ["Qualification burden is unknown."]
    return "aligned", []


def _diagnostic_evidence(candidate: Mapping[str, Any], profile: Mapping[str, Any]) -> tuple[list[str], list[str], list[str]]:
    required: list[str] = []
    cautions: list[str] = []
    blockers: list[str] = []
    coating = _mapping(candidate.get("coating_spallation_adhesion"))
    cmc = _mapping(candidate.get("cmc_ebc_environmental_durability"))
    graded = _mapping(candidate.get("graded_am_transition_zone_risk"))
    if coating:
        required.extend(_text(item) for item in _as_list(coating.get("required_validation_evidence")) if _text(item))
        if coating.get("adhesion_or_spallation_risk") == "high":
            cautions.append("High coating adhesion/spallation risk requires validation.")
    if cmc:
        required.extend(_text(item) for item in _as_list(cmc.get("required_validation_evidence")) if _text(item))
        for field in ("ebc_dependency_risk", "oxidation_recession_risk", "interface_or_interphase_risk"):
            if cmc.get(field) == "high":
                cautions.append(f"High CMC/EBC {field.replace('_', ' ')} requires validation.")
    if graded:
        required.extend(_text(item) for item in _as_list(graded.get("required_validation_evidence")) if _text(item))
        high_gradient_fields = [
            field
            for field in (
                "transition_zone_complexity",
                "residual_stress_risk",
                "cracking_or_delamination_risk",
                "process_window_sensitivity",
                "through_depth_inspection_difficulty",
            )
            if graded.get(field) == "high"
        ]
        if high_gradient_fields:
            cautions.append("High graded AM transition/process/inspection risk keeps the concept validation-dependent.")
            if not profile.get("allow_exploratory_concepts"):
                blockers.append("Graded AM concept is not engineering-fit for this non-exploratory profile without validation.")
    return list(dict.fromkeys(required)), cautions, blockers


def assess_candidate_against_application_profile(candidate: Mapping[str, Any], profile: Mapping[str, Any]) -> dict[str, Any]:
    app = normalise_application_profile(profile)
    candidate_id = _candidate_id(candidate)
    maturity = _evidence_maturity(candidate)
    readiness_status = _readiness_status(candidate)
    required = [
        item for item in _as_list(app.get("required_primary_service_functions")) if _text(item) not in _SUPPORT_OR_RISK_FUNCTIONS
    ]
    desired = [
        item for item in _as_list(app.get("desired_secondary_service_functions")) if _text(item) not in _SUPPORT_OR_RISK_FUNCTIONS
    ]
    primary = set(_primary_service_functions(candidate))
    secondary = set(_secondary_service_functions(candidate))
    matched_required = sorted(function for function in required if function in primary)
    missing_required = sorted(function for function in required if function not in primary)
    matched_desired = sorted(function for function in desired if function in secondary or function in primary)
    missing_desired = sorted(function for function in desired if function not in set(matched_desired))
    architecture_path = detect_hot_section_architecture_path(candidate, app)
    evidence_alignment = _evidence_alignment(maturity, app, readiness_status)
    exposure_alignment = _exposure_alignment(candidate, app, matched_required)
    inspection_alignment, inspection_cautions, inspection_blockers = _inspection_repair_alignment(candidate, app)
    certification_alignment, certification_cautions = _certification_alignment(candidate, app)
    diagnostic_evidence, diagnostic_cautions, diagnostic_blockers = _diagnostic_evidence(candidate, app)

    blockers = list(dict.fromkeys(inspection_blockers + diagnostic_blockers))
    cautions = list(
        dict.fromkeys(
            inspection_cautions
            + certification_cautions
            + diagnostic_cautions
            + [_text(item) for item in _as_list(architecture_path.get("path_cautions")) if _text(item)]
        )
    )
    required_next_evidence = list(
        dict.fromkeys(
            diagnostic_evidence
            + [_text(item) for item in _as_list(architecture_path.get("path_required_next_evidence")) if _text(item)]
        )
    )
    if missing_required:
        required_next_evidence.append("evidence for missing required primary service functions: " + ", ".join(missing_required))
    if missing_desired:
        required_next_evidence.append("evidence for desired secondary service functions: " + ", ".join(missing_desired))
    if evidence_alignment in {"below_minimum", "unknown"}:
        required_next_evidence.append("evidence maturity sufficient for intended application use")
    if certification_alignment in {"caution", "poor", "unknown"}:
        required_next_evidence.append("qualification and certification-route evidence")
    if inspection_alignment in {"caution", "poor", "unknown"}:
        required_next_evidence.append("inspection and repair acceptance evidence")

    if maturity == "unknown" and not primary:
        fit_status = "insufficient_information"
    elif evidence_alignment == "research_only" or maturity == "F" or readiness_status == "research_only":
        fit_status = "research_only_for_profile"
    elif not matched_required:
        fit_status = "poor_fit_for_profile" if primary else "insufficient_information"
    elif maturity in {"D", "E"} or readiness_status == "exploratory_only":
        fit_status = "exploratory_only_for_profile"
    elif missing_required:
        fit_status = "plausible_with_validation" if app.get("allow_exploratory_concepts") or maturity in {"A", "B", "C"} else "poor_fit_for_profile"
    elif blockers:
        fit_status = "plausible_with_validation"
    elif evidence_alignment == "meets_minimum" and readiness_status == "usable_as_reference" and not cautions:
        fit_status = "plausible_near_term_analogue"
    elif evidence_alignment == "meets_minimum" and readiness_status in {"usable_as_reference", "usable_with_caveats", "unknown"}:
        fit_status = "plausible_with_validation" if cautions or maturity == "C" else "plausible_near_term_analogue"
    elif evidence_alignment == "meets_minimum":
        fit_status = "plausible_with_validation"
    else:
        fit_status = "exploratory_only_for_profile"

    path_id = _text(architecture_path.get("architecture_path"), "unknown_path")
    if is_hot_section_profile(app):
        if path_id == "cmc_ebc_environmental_protection_path":
            if evidence_alignment == "research_only" or maturity == "F" or readiness_status == "research_only":
                fit_status = "research_only_for_profile"
            elif maturity in {"D", "E"} or readiness_status == "exploratory_only":
                fit_status = "exploratory_only_for_profile"
            elif maturity in {"A", "B", "C"}:
                fit_status = "plausible_with_validation"
            else:
                fit_status = "insufficient_information"
        elif path_id == "oxidation_protection_only_path":
            if evidence_alignment == "research_only" or maturity == "F" or readiness_status == "research_only":
                fit_status = "research_only_for_profile"
            elif maturity in {"D", "E"} or readiness_status == "exploratory_only":
                fit_status = "exploratory_only_for_profile"
            elif missing_required:
                fit_status = "poor_fit_for_profile"
        elif path_id == "wear_or_erosion_path":
            if evidence_alignment == "research_only" or maturity == "F" or readiness_status == "research_only":
                fit_status = "research_only_for_profile"
            else:
                fit_status = "poor_fit_for_profile"
        elif path_id == "monolithic_ceramic_path" and not matched_required:
            fit_status = "poor_fit_for_profile"
        elif path_id == "graded_am_research_path":
            if evidence_alignment == "research_only" or maturity == "F" or readiness_status == "research_only":
                fit_status = "research_only_for_profile"
            elif maturity in {"D", "E"} or readiness_status == "exploratory_only":
                fit_status = "exploratory_only_for_profile" if matched_required else "poor_fit_for_profile"

    if fit_status == "exploratory_only_for_profile" and app.get("allow_exploratory_concepts") and matched_required:
        fit_status = "plausible_with_validation"
    if maturity == "F":
        fit_status = "research_only_for_profile"

    rationale = [
        f"Matched {len(matched_required)} of {len(required)} required primary service functions.",
        f"Evidence alignment: {evidence_alignment}.",
        f"Exposure alignment: {exposure_alignment}.",
        f"Architecture path: {path_id}.",
        "Fit status is conservative decision support only.",
    ]
    rationale.extend(_text(item) for item in _as_list(architecture_path.get("path_rationale")) if _text(item))
    return {
        "candidate_id": candidate_id,
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "evidence_maturity": maturity,
        "decision_readiness_status": readiness_status,
        "profile_id": app["profile_id"],
        "fit_status": fit_status,
        "matched_required_primary_functions": matched_required,
        "missing_required_primary_functions": missing_required,
        "matched_desired_secondary_functions": matched_desired,
        "missing_desired_secondary_functions": missing_desired,
        "architecture_path": path_id,
        "architecture_path_rationale": [
            _text(item) for item in _as_list(architecture_path.get("path_rationale")) if _text(item)
        ],
        "architecture_path_matched_functions": [
            _text(item) for item in _as_list(architecture_path.get("path_matched_required_functions")) if _text(item)
        ],
        "architecture_path_missing_functions": [
            _text(item) for item in _as_list(architecture_path.get("path_missing_required_functions")) if _text(item)
        ],
        "architecture_path_cautions": [
            _text(item) for item in _as_list(architecture_path.get("path_cautions")) if _text(item)
        ],
        "exposure_alignment": exposure_alignment,
        "evidence_alignment": evidence_alignment,
        "inspection_repair_alignment": inspection_alignment,
        "certification_alignment": certification_alignment,
        "critical_blockers": blockers,
        "major_cautions": cautions,
        "required_next_evidence": list(dict.fromkeys(_text(item) for item in required_next_evidence if _text(item)))[:10],
        "fit_rationale": rationale,
        "not_a_final_selection": True,
        "no_ranking_applied": True,
    }


def build_application_requirement_fit_matrix(package: Mapping[str, Any], profile: Mapping[str, Any]) -> dict[str, Any]:
    app = normalise_application_profile(profile)
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    records = [assess_candidate_against_application_profile(candidate, app) for candidate in candidates]
    status_counts = Counter(_text(record.get("fit_status"), "unknown") for record in records)
    path_counts = Counter(_text(record.get("architecture_path"), "unknown_path") for record in records)
    by_status: dict[str, list[str]] = {}
    by_path: dict[str, list[str]] = {}
    for record in records:
        by_status.setdefault(_text(record.get("fit_status"), "unknown"), []).append(_text(record.get("candidate_id")))
        by_path.setdefault(_text(record.get("architecture_path"), "unknown_path"), []).append(
            _text(record.get("candidate_id"))
        )
    required = _as_list(app.get("required_primary_service_functions"))
    coverage = {
        function_id: [
            _text(record.get("candidate_id"))
            for record in records
            if function_id in _as_list(record.get("matched_required_primary_functions"))
        ]
        for function_id in required
    }
    blockers = Counter(
        _text(item)
        for record in records
        for item in _as_list(record.get("critical_blockers"))
        if _text(item)
    )
    cautions = Counter(
        _text(item)
        for record in records
        for item in _as_list(record.get("major_cautions"))
        if _text(item)
    )
    evidence = sorted(
        {
            _text(item)
            for record in records
            for item in _as_list(record.get("required_next_evidence"))
            if _text(item)
        }
    )
    practical = []
    if status_counts.get("plausible_near_term_analogue") or status_counts.get("plausible_with_validation"):
        practical.append("Several candidates match required functions but remain validation-dependent.")
    if status_counts.get("research_only_for_profile"):
        practical.append("Research-only concepts are retained for context only, not engineering selection.")
    if status_counts.get("exploratory_only_for_profile"):
        practical.append("Exploratory concepts require profile-specific validation before engineering use.")
    if status_counts.get("poor_fit_for_profile"):
        practical.append("Poor-fit candidates should not be advanced for this profile without changed requirements.")
    alternative_path_notes = []
    if path_counts.get("cmc_ebc_environmental_protection_path"):
        alternative_path_notes.append(
            "CMC/EBC environmental-protection paths are treated as hot-section relevant but validation-dependent."
        )
    if path_counts.get("oxidation_protection_only_path"):
        alternative_path_notes.append(
            "Oxidation-only paths do not satisfy the full default thermal-barrier plus oxidation profile."
        )
    warnings = []
    if not records:
        warnings.append("No candidates are available for application requirement-fit assessment.")
    if not any(record.get("matched_required_primary_functions") for record in records):
        warnings.append("No candidates visibly match required primary service functions.")
    return {
        "profile": app,
        "candidate_count": len(candidates),
        "fit_records": records,
        "fit_status_counts": dict(sorted(status_counts.items())),
        "candidate_ids_by_fit_status": {key: value for key, value in sorted(by_status.items())},
        "architecture_path_counts": dict(sorted(path_counts.items())),
        "candidate_ids_by_architecture_path": {key: value for key, value in sorted(by_path.items())},
        "alternative_architecture_path_notes": alternative_path_notes,
        "required_function_coverage_summary": {
            "required_primary_service_functions": list(required),
            "candidate_ids_covering_each_required_function": coverage,
            "candidate_ids_missing_all_required_functions": [
                record["candidate_id"] for record in records if not record["matched_required_primary_functions"]
            ],
            "candidate_ids_matching_all_required_functions": [
                record["candidate_id"] for record in records if not record["missing_required_primary_functions"]
            ],
            "candidate_ids_matching_some_required_functions": [
                record["candidate_id"]
                for record in records
                if record["matched_required_primary_functions"] and record["missing_required_primary_functions"]
            ],
        },
        "common_blockers": [item for item, _ in blockers.most_common(8)],
        "common_major_cautions": [item for item, _ in cautions.most_common(8)],
        "required_next_evidence_themes": evidence[:12],
        "practical_use_summary": practical,
        "warnings": warnings,
        "not_a_final_recommendation": True,
        "no_ranking_applied": True,
    }


def attach_application_requirement_fit(
    package: Mapping[str, Any],
    profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    app = normalise_application_profile(profile or get_default_application_profile("hot_section_thermal_cycling_oxidation"))
    output = dict(package)
    matrix = build_application_requirement_fit_matrix(package, app)
    records_by_id = {
        _text(record.get("candidate_id")): dict(record)
        for record in _as_list(matrix.get("fit_records"))
        if isinstance(record, Mapping)
    }
    candidates = []
    for candidate in _as_list(package.get("candidate_systems")):
        if isinstance(candidate, Mapping):
            enriched = dict(candidate)
            enriched["application_requirement_fit"] = records_by_id.get(_candidate_id(candidate), {})
            candidates.append(enriched)
    output["candidate_systems"] = candidates
    output["application_profile"] = deepcopy(app)
    output["application_requirement_fit"] = matrix
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics["application_requirement_fit_attached"] = True
    diagnostics["application_profile_id"] = app["profile_id"]
    output["diagnostics"] = diagnostics
    warnings = [_text(item) for item in _as_list(package.get("warnings")) if _text(item)]
    for warning in _as_list(matrix.get("warnings")):
        text = _text(warning)
        if text and text not in warnings:
            warnings.append(text)
    output["warnings"] = warnings
    return output
