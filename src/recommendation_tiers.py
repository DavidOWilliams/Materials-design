from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.pareto_frontier import run_pareto_frontier


RECOMMENDATION_TIERS: tuple[str, ...] = (
    "mature_reference_option",
    "validation_needed_option",
    "exploratory_option",
    "research_only_suggestion",
    "parked_not_preferred",
)

TIER_LABELS: dict[str, str] = {
    "mature_reference_option": "Mature reference option",
    "validation_needed_option": "Validation-needed option",
    "exploratory_option": "Exploratory option",
    "research_only_suggestion": "Research-only suggestion",
    "parked_not_preferred": "Parked / not preferred",
}

FRONTIER_STATUSES: tuple[str, ...] = (
    "on_frontier",
    "dominated",
    "insufficient_basis",
)

EVIDENCE_BANDS: tuple[str, ...] = (
    "mature",
    "engineering_reference",
    "emerging",
    "exploratory",
    "unknown",
)


class RecommendationTierAssessment(TypedDict, total=False):
    candidate_id: str
    system_name: str
    tier: str
    tier_label: str
    frontier_status: str
    evidence_maturity: str
    evidence_band: str
    research_mode_exposure: bool
    dominated_by: list[str]
    dominates: list[str]
    review_cautions: list[str]
    rationale: list[str]
    warnings: list[str]
    notes: list[str]


class RecommendationTierRun(TypedDict, total=False):
    candidate_count: int
    assessment_count: int
    research_mode_enabled: bool
    tier_assessments: list[RecommendationTierAssessment]
    tier_summary: dict[str, Any]
    notes: list[str]
    warnings: list[str]


def _as_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    if not all(isinstance(item, str) for item in value):
        return []
    return list(value)


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def evidence_band_from_maturity(maturity: str) -> str:
    maturity_key = _as_string(maturity, "unknown").lower()
    if maturity_key in ("a", "b"):
        return "mature"
    if maturity_key == "c":
        return "engineering_reference"
    if maturity_key == "d":
        return "emerging"
    if maturity_key in ("e", "f"):
        return "exploratory"
    return "unknown"


def evidence_maturity_from_frontier_candidate(candidate: Mapping[str, Any]) -> str:
    dimensions = candidate.get("comparable_dimensions")
    if not isinstance(dimensions, list):
        return "unknown"
    for dimension in dimensions:
        if not isinstance(dimension, Mapping):
            continue
        if dimension.get("dimension_id") == "evidence_maturity":
            maturity = _as_string(dimension.get("raw_value"))
            if maturity:
                return maturity
    return "unknown"


def has_research_mode_exposure(candidate: Mapping[str, Any]) -> bool:
    if candidate.get("vector_status") == "research_mode_vector_available":
        return True
    for warning in _string_list(candidate.get("warnings")):
        if "research" in warning.lower():
            return True
    return False


def frontier_status(candidate: Mapping[str, Any]) -> str:
    dimensions = candidate.get("comparable_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        return "insufficient_basis"
    if candidate.get("on_frontier") is True:
        return "on_frontier"
    if candidate.get("on_frontier") is False:
        return "dominated"
    return "insufficient_basis"


def collect_review_cautions(
    candidate: Mapping[str, Any],
    evidence_band: str,
    research_mode_exposure: bool,
) -> list[str]:
    cautions: list[str] = []
    for warning in _string_list(candidate.get("warnings")):
        _append_unique(cautions, warning)

    if _string_list(candidate.get("dominated_by")):
        _append_unique(cautions, "Candidate is dominated by one or more alternatives.")
    if research_mode_exposure:
        _append_unique(cautions, "Candidate has research-mode exposure.")
    if evidence_band in ("exploratory", "unknown"):
        _append_unique(cautions, "Candidate has exploratory or unknown evidence maturity.")

    dimensions = candidate.get("comparable_dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        _append_unique(cautions, "Candidate has limited comparable basis for tiering.")

    return cautions


def assign_tier(
    candidate: Mapping[str, Any],
    *,
    evidence_maturity: str | None = None,
) -> str:
    if has_research_mode_exposure(candidate):
        return "research_only_suggestion"

    status = frontier_status(candidate)
    if status == "insufficient_basis":
        return "exploratory_option"
    if status == "dominated":
        return "parked_not_preferred"

    maturity = (
        evidence_maturity
        if evidence_maturity is not None
        else evidence_maturity_from_frontier_candidate(candidate)
    )
    evidence_band = evidence_band_from_maturity(maturity)
    if evidence_band == "mature":
        return "mature_reference_option"
    if evidence_band in ("engineering_reference", "emerging"):
        return "validation_needed_option"
    return "exploratory_option"


def build_tier_assessment(candidate: Mapping[str, Any]) -> RecommendationTierAssessment:
    candidate_id = _as_string(candidate.get("candidate_id"), "unknown_candidate")
    system_name = _as_string(candidate.get("system_name"), "unknown_system")
    dominated_by = _string_list(deepcopy(candidate.get("dominated_by")))
    dominates = _string_list(deepcopy(candidate.get("dominates")))
    candidate_warnings = _string_list(deepcopy(candidate.get("warnings")))
    evidence_maturity = evidence_maturity_from_frontier_candidate(candidate)
    evidence_band = evidence_band_from_maturity(evidence_maturity)
    research_mode_exposure = has_research_mode_exposure(candidate)
    status = frontier_status(candidate)
    tier = assign_tier(candidate, evidence_maturity=evidence_maturity)
    review_cautions = collect_review_cautions(
        candidate,
        evidence_band,
        research_mode_exposure,
    )

    warnings = list(candidate_warnings)
    if research_mode_exposure:
        _append_unique(warnings, "Research-mode exposure prevents mature-option tiering.")

    return {
        "candidate_id": candidate_id,
        "system_name": system_name,
        "tier": tier,
        "tier_label": TIER_LABELS[tier],
        "frontier_status": status,
        "evidence_maturity": evidence_maturity,
        "evidence_band": evidence_band,
        "research_mode_exposure": research_mode_exposure,
        "dominated_by": dominated_by,
        "dominates": dominates,
        "review_cautions": review_cautions,
        "rationale": [
            f"Frontier status: {status}.",
            f"Evidence band: {evidence_band}.",
            f"Research-mode exposure present: {research_mode_exposure}.",
            "No final recommendation or approval is made.",
        ],
        "warnings": warnings,
        "notes": [
            "Tier is a decision-support label, not a final recommendation.",
            "No qualification or certification approval is implied.",
        ],
    }


def _tier_summary(
    assessments: Sequence[RecommendationTierAssessment],
) -> dict[str, Any]:
    by_tier = {tier: 0 for tier in RECOMMENDATION_TIERS}
    by_frontier_status = {status: 0 for status in FRONTIER_STATUSES}
    for assessment in assessments:
        tier = _as_string(assessment.get("tier"), "unknown")
        status = _as_string(assessment.get("frontier_status"), "insufficient_basis")
        by_tier[tier] = by_tier.get(tier, 0) + 1
        by_frontier_status[status] = by_frontier_status.get(status, 0) + 1

    return {
        "by_tier": by_tier,
        "by_frontier_status": by_frontier_status,
        "research_only_count": by_tier.get("research_only_suggestion", 0),
        "mature_reference_count": by_tier.get("mature_reference_option", 0),
        "parked_count": by_tier.get("parked_not_preferred", 0),
    }


def build_recommendation_tiers_from_frontier(
    frontier_candidates: Sequence[Mapping[str, Any]],
) -> RecommendationTierRun:
    assessments = [
        build_tier_assessment(candidate)
        for candidate in frontier_candidates
    ]
    warnings: list[str] = []
    if not frontier_candidates:
        warnings.append("No frontier candidates were supplied for tiering.")
    if any(
        assessment.get("tier") == "research_only_suggestion"
        for assessment in assessments
    ):
        warnings.append("One or more candidates are research-only suggestions.")

    return {
        "candidate_count": len(frontier_candidates),
        "assessment_count": len(assessments),
        "research_mode_enabled": False,
        "tier_assessments": assessments,
        "tier_summary": _tier_summary(assessments),
        "notes": [
            "No final recommendation is made.",
            "No winner is selected.",
            "No certification or qualification approval is implied.",
        ],
        "warnings": warnings,
    }


def run_recommendation_tiers(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> RecommendationTierRun:
    frontier_run = run_pareto_frontier(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    tier_run = build_recommendation_tiers_from_frontier(
        frontier_run.get("frontier_candidates", [])
    )
    warnings = _string_list(deepcopy(frontier_run.get("warnings")))
    warnings.extend(tier_run.get("warnings", []))
    if research_mode_enabled:
        warnings.append("Research mode is enabled; recommendation tiers may include research-only labels.")

    tier_run["candidate_count"] = int(frontier_run.get("candidate_count") or len(candidates))
    tier_run["research_mode_enabled"] = research_mode_enabled
    tier_run["warnings"] = warnings
    return tier_run
