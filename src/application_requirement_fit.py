from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.application_profiles import default_application_profile
from src.contracts import EVIDENCE_MATURITY_LEVELS
from src.surface_function_model import build_candidate_surface_function_profile


_MATURITY_RANK = {level: index for index, level in enumerate(EVIDENCE_MATURITY_LEVELS)}
_PASSING_STATUSES = {"satisfied", "acknowledged"}


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


def _candidate_surface_profile(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    profile = _mapping(candidate.get("surface_function_profile"))
    if profile:
        return profile
    return build_candidate_surface_function_profile(candidate)


def _candidate_functions(candidate: Mapping[str, Any]) -> set[str]:
    profile = _candidate_surface_profile(candidate)
    function_ids = set()
    for field in (
        "primary_service_functions",
        "secondary_service_functions",
        "primary_surface_functions",
        "secondary_surface_functions",
    ):
        function_ids.update(_text(item) for item in _as_list(profile.get(field)) if _text(item))
    for item in _as_list(profile.get("surface_functions")):
        record = _mapping(item)
        function_id = _text(record.get("function_id"))
        if function_id:
            function_ids.add(function_id)
    return function_ids


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    for value in (
        evidence.get("maturity"),
        evidence.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        maturity = _text(value).upper()
        if maturity in _MATURITY_RANK:
            return maturity
    return "unknown"


def _maturity_satisfies(candidate_maturity: str, minimum_maturity: str) -> bool:
    candidate_rank = _MATURITY_RANK.get(candidate_maturity)
    minimum_rank = _MATURITY_RANK.get(_text(minimum_maturity).upper())
    return candidate_rank is not None and minimum_rank is not None and candidate_rank <= minimum_rank


def _constraint_record(
    constraint_id: str,
    required_value: str,
    observed_value: str,
    status: str,
    source_field: str,
) -> dict[str, str]:
    return {
        "constraint_id": constraint_id,
        "required_value": required_value,
        "observed_value": observed_value,
        "status": status,
        "source_field": source_field,
    }


def _constraint_checks(
    candidate: Mapping[str, Any],
    profile: Mapping[str, Any],
    candidate_functions: set[str],
) -> list[dict[str, str]]:
    constraints = _mapping(profile.get("constraints"))
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route") or candidate.get("qualification"))
    text = _blob(candidate)
    maturity = _evidence_maturity(candidate)

    checks = [
        _constraint_record(
            "thermal_exposure",
            _text(constraints.get("thermal_exposure"), "very_high"),
            "thermal_barrier" if "thermal_barrier" in candidate_functions else "not_visible",
            "satisfied" if "thermal_barrier" in candidate_functions else "gap",
            "surface_function_profile.primary_service_functions",
        ),
        _constraint_record(
            "thermal_cycling",
            _text(constraints.get("thermal_cycling"), "high"),
            "thermal_cycling_tolerance" if "thermal_cycling_tolerance" in candidate_functions else "not_visible",
            "satisfied" if "thermal_cycling_tolerance" in candidate_functions else "gap",
            "surface_function_profile.secondary_service_functions",
        ),
        _constraint_record(
            "oxidation_steam_exposure",
            _text(constraints.get("oxidation_steam_exposure"), "high"),
            "oxidation_resistance" if "oxidation_resistance" in candidate_functions else "not_visible",
            "satisfied" if "oxidation_resistance" in candidate_functions else "gap",
            "surface_function_profile.primary_service_functions",
        ),
    ]

    inspection_burden = _text(inspection.get("inspection_burden"), "unknown")
    checks.append(
        _constraint_record(
            "inspection_difficulty",
            _text(constraints.get("inspection_difficulty"), "difficult"),
            inspection_burden,
            "acknowledged" if inspection_burden in {"high", "very_high", "difficult"} else "gap",
            "inspection_plan.inspection_burden",
        )
    )

    repairability_level = _text(repairability.get("repairability_level"), "unknown")
    repair_concept = _text(repairability.get("repair_concept"))
    checks.append(
        _constraint_record(
            "repair",
            _text(constraints.get("repair"), "desired"),
            repairability_level if repairability_level != "unknown" else repair_concept or "unknown",
            "satisfied" if repairability_level in {"good", "moderate"} or repair_concept else "gap",
            "repairability",
        )
    )

    qualification_burden = _text(qualification.get("qualification_burden"), "unknown")
    certification_text_present = "certification" in text or "qualification" in text
    checks.append(
        _constraint_record(
            "certification_sensitivity",
            _text(constraints.get("certification_sensitivity"), "very_high"),
            qualification_burden,
            "acknowledged" if qualification_burden in {"high", "very_high"} or certification_text_present else "gap",
            "qualification_route.qualification_burden",
        )
    )

    minimum_maturity = _text(constraints.get("minimum_evidence_maturity"), "C").upper()
    checks.append(
        _constraint_record(
            "minimum_evidence_maturity",
            minimum_maturity,
            maturity,
            "satisfied" if _maturity_satisfies(maturity, minimum_maturity) else "gap",
            "evidence_maturity",
        )
    )

    return checks


def _fit_status(
    missing_required_functions: list[str],
    constraint_checks: list[Mapping[str, Any]],
) -> str:
    if missing_required_functions:
        return "does_not_meet_core_requirements"
    if all(_text(check.get("status")) in _PASSING_STATUSES for check in constraint_checks):
        return "meets_core_requirements"
    return "partially_meets_core_requirements"


def assess_application_requirement_fit(
    candidate: Mapping[str, Any],
    application_profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assess one candidate dictionary against a Build 4 application profile."""
    profile = dict(application_profile or default_application_profile())
    functions = _candidate_functions(candidate)
    required = [_text(item) for item in _as_list(profile.get("required_primary_service_functions")) if _text(item)]
    desired = [_text(item) for item in _as_list(profile.get("desired_secondary_service_functions")) if _text(item)]
    matched_required = [function for function in required if function in functions]
    missing_required = [function for function in required if function not in functions]
    matched_desired = [function for function in desired if function in functions]
    missing_desired = [function for function in desired if function not in functions]
    checks = _constraint_checks(candidate, profile, functions)
    gap_constraints = [dict(check) for check in checks if _text(check.get("status")) not in _PASSING_STATUSES]

    return {
        "candidate_id": _candidate_id(candidate),
        "profile_id": _text(profile.get("profile_id")),
        "profile_name": _text(profile.get("profile_name")),
        "fit_status": _fit_status(missing_required, checks),
        "required_primary_service_functions": required,
        "matched_required_primary_service_functions": matched_required,
        "missing_required_primary_service_functions": missing_required,
        "desired_secondary_service_functions": desired,
        "matched_desired_secondary_service_functions": matched_desired,
        "missing_desired_secondary_service_functions": missing_desired,
        "constraint_checks": checks,
        "gap_constraints": gap_constraints,
        "assessment_boundaries": dict(_mapping(profile.get("assessment_boundaries"))),
    }
