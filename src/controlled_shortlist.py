from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from src.application_limiting_factors import attach_application_limiting_factors


SHORTLIST_BUCKETS = {
    "near_term_comparison_references",
    "validation_needed_options",
    "exploratory_context_only",
    "research_only_context",
    "poor_fit_for_profile",
    "insufficient_information",
}

_BUCKET_ORDER = [
    "near_term_comparison_references",
    "validation_needed_options",
    "exploratory_context_only",
    "research_only_context",
    "poor_fit_for_profile",
    "insufficient_information",
]


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
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _candidate_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_name") or candidate.get("name") or candidate.get("system_name"), _candidate_id(candidate))


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _has_application_fit(candidate: Mapping[str, Any]) -> bool:
    return bool(_mapping(candidate.get("application_requirement_fit")))


def _has_application_limiting_analysis(candidate: Mapping[str, Any]) -> bool:
    return bool(_mapping(candidate.get("application_limiting_factor_analysis")))


def _ensure_application_layers(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    if any(not _has_application_fit(candidate) or not _has_application_limiting_analysis(candidate) for candidate in candidates):
        return attach_application_limiting_factors(package)
    return dict(package)


def _bucket_for(candidate: Mapping[str, Any]) -> str:
    analysis = _mapping(candidate.get("application_limiting_factor_analysis"))
    fit = _mapping(candidate.get("application_requirement_fit"))
    fit_status = _text(analysis.get("fit_status") or fit.get("application_fit_status") or fit.get("fit_status"))
    analysis_status = _text(analysis.get("analysis_status"))
    maturity = _evidence_maturity(candidate)

    if fit_status == "insufficient_information" or analysis_status == "insufficient_information":
        return "insufficient_information"
    if fit_status == "poor_fit_for_profile" or analysis_status == "poor_fit_suppressed":
        return "poor_fit_for_profile"
    if fit_status == "research_only_for_profile" or analysis_status == "research_context_only":
        return "research_only_context"
    if fit_status == "exploratory_only_for_profile" or analysis_status == "exploratory_context_only":
        return "exploratory_context_only"
    if fit_status == "plausible_with_validation" and analysis_status == "analysed_for_application":
        if maturity in {"A", "B"} and not analysis.get("required_evidence") and not fit.get("validation_issues"):
            return "near_term_comparison_references"
        return "validation_needed_options"
    return "insufficient_information"


def _rationale(bucket: str, analysis: Mapping[str, Any]) -> str:
    fit_status = _text(analysis.get("fit_status"), "unknown")
    analysis_status = _text(analysis.get("analysis_status"), "unknown")
    if bucket == "near_term_comparison_references":
        return "Plausible application fit with mature evidence and no open application evidence request."
    if bucket == "validation_needed_options":
        return "Plausible application fit, but application evidence or validation remains needed."
    if bucket == "exploratory_context_only":
        return "Exploratory maturity or context-only application status."
    if bucket == "research_only_context":
        return "Research-only application context."
    if bucket == "poor_fit_for_profile":
        return "Poor fit for this application profile; retained only for controlled comparison context."
    return f"Insufficient information for controlled shortlist placement: {fit_status}/{analysis_status}."


def _bucket_entry(candidate: Mapping[str, Any], bucket: str) -> dict[str, Any]:
    analysis = _mapping(candidate.get("application_limiting_factor_analysis"))
    fit = _mapping(candidate.get("application_requirement_fit"))
    return {
        "candidate_id": _candidate_id(candidate),
        "candidate_name": _candidate_name(candidate),
        "candidate_class": _text(candidate.get("candidate_class") or candidate.get("system_class")),
        "architecture_path": _text(analysis.get("architecture_path") or fit.get("architecture_path")),
        "fit_status": _text(analysis.get("fit_status") or fit.get("application_fit_status") or fit.get("fit_status")),
        "analysis_status": _text(analysis.get("analysis_status")),
        "evidence_maturity": _evidence_maturity(candidate),
        "rationale": _rationale(bucket, analysis),
        "cautions": [item for item in _as_list(analysis.get("cautions")) if _text(item)],
        "required_evidence": [item for item in _as_list(analysis.get("required_evidence")) if item],
        "suggested_actions": [item for item in _as_list(analysis.get("suggested_actions")) if _text(item)],
    }


def _boundaries() -> dict[str, bool]:
    return {
        "is_ranking": False,
        "is_final_recommendation": False,
        "is_validation_plan": False,
        "implies_qualification_or_certification_approval": False,
    }


def _empty_buckets() -> dict[str, list[dict[str, Any]]]:
    return {bucket: [] for bucket in _BUCKET_ORDER}


def build_controlled_shortlist(package: Mapping[str, Any]) -> dict[str, Any]:
    working_package = _ensure_application_layers(package)
    source_candidates = [
        candidate
        for candidate in _as_list(working_package.get("candidate_systems"))
        if isinstance(candidate, Mapping)
    ]
    source_candidate_ids = [_candidate_id(candidate) for candidate in source_candidates]
    buckets = _empty_buckets()
    for candidate in source_candidates:
        bucket = _bucket_for(candidate)
        buckets[bucket].append(_bucket_entry(candidate, bucket))

    bucket_counts = {bucket: len(entries) for bucket, entries in buckets.items()}
    profile = _mapping(working_package.get("application_profile"))
    profile_id = _text(profile.get("profile_id"))
    if not profile_id:
        first_analysis = _mapping(source_candidates[0].get("application_limiting_factor_analysis")) if source_candidates else {}
        profile_id = _text(first_analysis.get("profile_id"))

    output = dict(working_package)
    output["candidate_systems"] = [dict(candidate) for candidate in source_candidates]
    output["controlled_shortlist"] = {
        "shortlist_status": "controlled_shortlist_created",
        "profile_id": profile_id,
        "buckets": buckets,
        "boundaries": _boundaries(),
    }
    output["controlled_shortlist_summary"] = {
        "profile_id": profile_id,
        "candidate_count": len(source_candidates),
        "bucket_counts": bucket_counts,
        "total_bucketed_candidate_count": sum(bucket_counts.values()),
        "ranking_performed": False,
        "candidate_filtering_performed": False,
        "pareto_analysis_performed": False,
        "validation_plan_created": False,
        "generated_candidate_count": 0,
        "live_model_calls_made": False,
    }

    diagnostics = dict(_mapping(working_package.get("diagnostics")))
    diagnostics.update(
        {
            "controlled_shortlist_created": True,
            "controlled_shortlist_candidate_count": len(source_candidates),
            "controlled_shortlist_candidate_order_preserved": source_candidate_ids
            == [_candidate_id(candidate) for candidate in output["candidate_systems"]],
            "controlled_shortlist_ranking_performed": False,
            "controlled_shortlist_filtering_performed": False,
        }
    )
    output["diagnostics"] = diagnostics

    return output
