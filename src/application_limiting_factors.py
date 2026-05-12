from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.application_requirement_fit import (
    assess_candidate_application_requirement_fit,
    classify_architecture_path,
)


ANALYSIS_STATUSES = {
    "analysed_for_application",
    "poor_fit_suppressed",
    "exploratory_context_only",
    "research_context_only",
    "insufficient_information",
}

_FIT_TO_ANALYSIS_STATUS = {
    "plausible_with_validation": "analysed_for_application",
    "poor_fit_for_profile": "poor_fit_suppressed",
    "exploratory_only_for_profile": "exploratory_context_only",
    "research_only_for_profile": "research_context_only",
    "insufficient_information": "insufficient_information",
}


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


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"))


def _application_fit(candidate: Mapping[str, Any], profile: Mapping[str, Any] | None) -> Mapping[str, Any]:
    existing = _mapping(candidate.get("application_requirement_fit"))
    if existing:
        return existing
    return assess_candidate_application_requirement_fit(candidate, profile)


def _assessment_boundaries() -> dict[str, bool]:
    return {
        "ranking_performed": False,
        "controlled_shortlist_created": False,
        "validation_plan_created": False,
        "optimisation_performed": False,
        "pareto_analysis_performed": False,
        "candidate_filtering_performed": False,
        "generated_candidate_variants": False,
        "final_recommendation_created": False,
        "live_model_calls_made": False,
    }


def _base_analysis(
    candidate: Mapping[str, Any],
    fit: Mapping[str, Any],
    fit_status: str,
    analysis_status: str,
) -> dict[str, Any]:
    output = {
        "profile_id": _text(fit.get("profile_id")),
        "architecture_path": _text(fit.get("architecture_path"), classify_architecture_path(candidate)),
        "fit_status": fit_status,
        "analysis_status": analysis_status,
        "limiting_factors": [],
        "cautions": [],
        "required_evidence": [],
        "suggested_actions": [],
        "suppressed_reasons": [],
        "assessment_boundaries": _assessment_boundaries(),
    }
    candidate_id = _candidate_id(candidate) or _text(fit.get("candidate_id"))
    if candidate_id:
        output["candidate_id"] = candidate_id
    return output


def _missing_required_evidence(fit: Mapping[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "evidence_id": f"missing_required_function:{function_id}",
            "required_item": _text(function_id),
            "reason": f"Required application service function is not evidenced: {_text(function_id)}.",
        }
        for function_id in _as_list(fit.get("missing_required_primary_service_functions"))
        if _text(function_id)
    ]


def _validation_issue_evidence(fit: Mapping[str, Any]) -> list[dict[str, str]]:
    evidence = []
    for issue in _as_list(fit.get("validation_issues")):
        record = _mapping(issue)
        message = _text(record.get("message"))
        if not message:
            continue
        evidence.append(
            {
                "evidence_id": _text(record.get("issue_id"), "validation_issue"),
                "required_item": "application_path_validation",
                "reason": message,
            }
        )
    return evidence


def _gap_constraint_evidence(fit: Mapping[str, Any]) -> list[dict[str, str]]:
    evidence = []
    for constraint in _as_list(fit.get("gap_constraints")):
        record = _mapping(constraint)
        constraint_id = _text(record.get("constraint_id"))
        if not constraint_id:
            continue
        evidence.append(
            {
                "evidence_id": f"gap_constraint:{constraint_id}",
                "required_item": constraint_id,
                "reason": (
                    f"Application constraint '{constraint_id}' is not yet satisfied; "
                    f"observed value is '{_text(record.get('observed_value'), 'unknown')}'."
                ),
            }
        )
    return evidence


def _plausible_analysis(analysis: dict[str, Any], fit: Mapping[str, Any]) -> None:
    for function_id in _as_list(fit.get("missing_required_primary_service_functions")):
        function_text = _text(function_id)
        if function_text:
            analysis["limiting_factors"].append(
                {
                    "factor_id": f"missing_required_function:{function_text}",
                    "severity": "validation_required",
                    "reason": f"Missing required application service-function evidence: {function_text}.",
                }
            )
    for issue in _as_list(fit.get("validation_issues")):
        record = _mapping(issue)
        message = _text(record.get("message"))
        if message:
            analysis["limiting_factors"].append(
                {
                    "factor_id": _text(record.get("issue_id"), "application_validation_issue"),
                    "severity": _text(record.get("severity"), "validation_required"),
                    "reason": message,
                }
            )

    analysis["required_evidence"].extend(_missing_required_evidence(fit))
    analysis["required_evidence"].extend(_validation_issue_evidence(fit))
    analysis["required_evidence"].extend(_gap_constraint_evidence(fit))
    analysis["suggested_actions"].extend(
        [
            "review application evidence package",
            "run thermal-cycling validation review",
            "run oxidation/steam exposure validation review",
        ]
    )
    constraint_ids = {
        _text(item.get("constraint_id"))
        for item in _as_list(fit.get("gap_constraints"))
        if isinstance(item, Mapping)
    }
    if {"inspection_difficulty", "repair"} & constraint_ids:
        analysis["suggested_actions"].append("review inspection and repair evidence")


def _poor_fit_analysis(analysis: dict[str, Any]) -> None:
    analysis["suppressed_reasons"].append(
        "Candidate is a poor fit for this application profile; detailed improvement analysis is suppressed."
    )
    analysis["suggested_actions"].extend(
        [
            "park for this profile",
            "consider under a different application profile",
        ]
    )


def _exploratory_analysis(analysis: dict[str, Any]) -> None:
    analysis["cautions"].extend(
        [
            "Low maturity application fit; treat as exploratory context only.",
            "Validation uncertainty remains high for this application profile.",
        ]
    )
    analysis["suggested_actions"].extend(
        [
            "scope exploratory validation only",
            "define research questions before application use",
        ]
    )


def _research_analysis(analysis: dict[str, Any]) -> None:
    analysis["cautions"].append(
        "Research maturity only; do not treat as application-ready evidence."
    )
    analysis["suggested_actions"].extend(
        [
            "monitor research evidence",
            "perform concept validation only",
        ]
    )


def _insufficient_information_analysis(analysis: dict[str, Any], fit: Mapping[str, Any]) -> None:
    analysis["required_evidence"].extend(_missing_required_evidence(fit))
    analysis["required_evidence"].extend(_gap_constraint_evidence(fit))
    if not analysis["required_evidence"]:
        analysis["required_evidence"].append(
            {
                "evidence_id": "missing_application_requirement_fit",
                "required_item": "application_requirement_fit",
                "reason": "Application fit information is missing or insufficient for limiting-factor analysis.",
            }
        )
    analysis["cautions"].append("Insufficient information; no application recommendation is inferred.")


def analyze_candidate_application_limiting_factors(
    candidate: Mapping[str, Any],
    profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return deterministic application limiting-factor analysis for one candidate."""
    fit = _application_fit(candidate, profile)
    fit_status = _text(
        fit.get("application_fit_status") or fit.get("fit_status"),
        "insufficient_information",
    )
    analysis_status = _FIT_TO_ANALYSIS_STATUS.get(fit_status, "insufficient_information")
    analysis = _base_analysis(candidate, fit, fit_status, analysis_status)

    if analysis_status == "analysed_for_application":
        _plausible_analysis(analysis, fit)
    elif analysis_status == "poor_fit_suppressed":
        _poor_fit_analysis(analysis)
    elif analysis_status == "exploratory_context_only":
        _exploratory_analysis(analysis)
    elif analysis_status == "research_context_only":
        _research_analysis(analysis)
    else:
        _insufficient_information_analysis(analysis, fit)

    return analysis
