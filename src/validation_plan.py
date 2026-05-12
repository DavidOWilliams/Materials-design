from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

from src.controlled_shortlist import build_controlled_shortlist


VALIDATION_PLAN_CATEGORIES = {
    "baseline_reference_validation",
    "validation_required_before_engineering_use",
    "exploratory_validation_only",
    "research_validation_only",
    "parked_no_validation_for_this_profile",
    "insufficient_information",
}

_BUCKET_TO_CATEGORY = {
    "near_term_comparison_references": "baseline_reference_validation",
    "validation_needed_options": "validation_required_before_engineering_use",
    "exploratory_context_only": "exploratory_validation_only",
    "research_only_context": "research_validation_only",
    "poor_fit_for_profile": "parked_no_validation_for_this_profile",
    "insufficient_information": "insufficient_information",
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


def _candidate_lookup(candidates: list[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    return {_candidate_id(candidate): candidate for candidate in candidates}


def _candidate_name(entry: Mapping[str, Any], candidate: Mapping[str, Any]) -> str:
    return _text(
        entry.get("candidate_name")
        or candidate.get("candidate_name")
        or candidate.get("name")
        or candidate.get("system_name"),
        _text(entry.get("candidate_id"), _candidate_id(candidate)),
    )


def _needs_controlled_shortlist(package: Mapping[str, Any]) -> bool:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    if not _mapping(package.get("controlled_shortlist")):
        return True
    return any(
        not _mapping(candidate.get("application_requirement_fit"))
        or not _mapping(candidate.get("application_limiting_factor_analysis"))
        for candidate in candidates
    )


def _plan_boundaries() -> dict[str, bool]:
    return {
        "is_qualification_approval": False,
        "is_certification_approval": False,
        "is_final_recommendation": False,
        "is_ranking": False,
        "creates_candidate_variants": False,
    }


def _entry_boundaries() -> dict[str, bool]:
    return dict(_plan_boundaries())


def _objectives(category: str) -> list[str]:
    return {
        "baseline_reference_validation": [
            "Confirm reference evidence remains applicable to the target service environment.",
            "Identify residual qualification gaps before engineering comparison use.",
        ],
        "validation_required_before_engineering_use": [
            "Close application-specific thermal cycling and oxidation/steam evidence gaps.",
            "Confirm inspection, repair, interface, and qualification assumptions before engineering use.",
        ],
        "exploratory_validation_only": [
            "Scope feasibility evidence without implying engineering readiness.",
            "Define evidence maturity uplift path.",
        ],
        "research_validation_only": [
            "Track research evidence and concept feasibility only.",
            "Avoid engineering-use validation claims.",
        ],
        "parked_no_validation_for_this_profile": [
            "Record why the candidate is parked for this profile.",
            "Limit activity to possible reassessment under a different application profile.",
        ],
        "insufficient_information": [
            "Identify missing information required for application validation planning.",
            "Complete data checks before assigning validation work.",
        ],
    }[category]


def _activities(category: str, entry: Mapping[str, Any]) -> list[str]:
    activities = {
        "baseline_reference_validation": [
            "reference evidence review",
            "service-environment comparison",
            "inspection/repair evidence review",
            "qualification-gap review",
        ],
        "validation_required_before_engineering_use": [
            "thermal-cycling validation",
            "oxidation/steam exposure validation",
            "interface/coating durability review",
            "inspection/repair evidence review",
            "qualification-gap review",
        ],
        "exploratory_validation_only": [
            "feasibility scoping",
            "early coupon/screening studies",
            "manufacturability review",
            "evidence-maturity uplift plan",
        ],
        "research_validation_only": [
            "research monitoring",
            "concept feasibility evidence",
            "no engineering-use validation claim",
        ],
        "parked_no_validation_for_this_profile": [
            "parked-for-profile rationale",
            "optional reassessment under a different application profile",
        ],
        "insufficient_information": [
            "missing information requests",
            "data-completeness checks",
        ],
    }[category]
    suggested = [_text(item) for item in _as_list(entry.get("suggested_actions")) if _text(item)]
    return list(dict.fromkeys(activities + suggested))


def _validation_entry(bucket: str, entry: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    category = _BUCKET_TO_CATEGORY[bucket]
    return {
        "candidate_id": _text(entry.get("candidate_id"), _candidate_id(candidate)),
        "candidate_name": _candidate_name(entry, candidate),
        "candidate_class": _text(entry.get("candidate_class") or candidate.get("candidate_class") or candidate.get("system_class")),
        "architecture_path": _text(entry.get("architecture_path")),
        "fit_status": _text(entry.get("fit_status")),
        "analysis_status": _text(entry.get("analysis_status")),
        "controlled_shortlist_bucket": bucket,
        "validation_category": category,
        "evidence_maturity": _text(entry.get("evidence_maturity"), "unknown"),
        "validation_objectives": _objectives(category),
        "required_evidence": [item for item in _as_list(entry.get("required_evidence")) if item],
        "suggested_validation_activities": _activities(category, entry),
        "cautions": [_text(item) for item in _as_list(entry.get("cautions")) if _text(item)],
        "boundaries": _entry_boundaries(),
    }


def _validation_entries(package: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    by_id = _candidate_lookup(candidates)
    shortlist = _mapping(package.get("controlled_shortlist"))
    buckets = _mapping(shortlist.get("buckets"))
    entries = []
    for bucket in _BUCKET_ORDER:
        for bucket_entry in _as_list(buckets.get(bucket)):
            entry = _mapping(bucket_entry)
            candidate = by_id.get(_text(entry.get("candidate_id")), {})
            entries.append(_validation_entry(bucket, entry, candidate))
    return entries


def build_validation_plan(package: Mapping[str, Any]) -> dict[str, Any]:
    working_package = build_controlled_shortlist(package) if _needs_controlled_shortlist(package) else dict(package)
    candidates = [candidate for candidate in _as_list(working_package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    source_candidate_ids = [_candidate_id(candidate) for candidate in candidates]
    entries = _validation_entries(working_package)
    category_counts = dict(Counter(entry["validation_category"] for entry in entries))
    profile = _mapping(working_package.get("application_profile"))
    shortlist = _mapping(working_package.get("controlled_shortlist"))
    profile_id = _text(profile.get("profile_id") or shortlist.get("profile_id"))

    output = dict(working_package)
    output["candidate_systems"] = [dict(candidate) for candidate in candidates]
    output["validation_plan"] = {
        "validation_plan_status": "validation_plan_created",
        "profile_id": profile_id,
        "entries": entries,
        "boundaries": _plan_boundaries(),
    }
    output["validation_plan_summary"] = {
        "profile_id": profile_id,
        "candidate_count": len(candidates),
        "validation_category_counts": category_counts,
        "total_validation_entries": len(entries),
        "ranking_performed": False,
        "candidate_filtering_performed": False,
        "pareto_analysis_performed": False,
        "generated_candidate_count": 0,
        "live_model_calls_made": False,
        "qualification_approval_granted": False,
        "certification_approval_granted": False,
    }

    diagnostics = dict(_mapping(working_package.get("diagnostics")))
    diagnostics.update(
        {
            "validation_plan_created": True,
            "validation_plan_candidate_count": len(candidates),
            "validation_plan_candidate_order_preserved": source_candidate_ids
            == [_candidate_id(candidate) for candidate in output["candidate_systems"]],
            "validation_plan_ranking_performed": False,
            "validation_plan_filtering_performed": False,
            "validation_plan_certification_approval": False,
            "validation_plan_qualification_approval": False,
        }
    )
    output["diagnostics"] = diagnostics

    return output
