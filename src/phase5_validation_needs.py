from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.recommendation_tiers import run_recommendation_tiers


VALIDATION_CATEGORIES: tuple[str, ...] = (
    "evidence_maturity",
    "dominated_option_review",
    "research_mode_gate",
    "coating_interface_review",
    "spatial_gradient_feasibility",
    "inspection_repair_review",
    "certification_caution_review",
    "frontier_review",
    "general_engineering_review",
)

VALIDATION_PRIORITIES: tuple[str, ...] = (
    "high",
    "medium",
    "low",
)

VALIDATION_STATUSES: tuple[str, ...] = (
    "proposed_validation_need",
    "research_mode_validation_required",
    "engineering_review_required",
)

PLAN_STATUSES: tuple[str, ...] = (
    "validation_needs_available",
    "no_validation_needs_identified",
    "research_mode_validation_required",
)


class ValidationNeed(TypedDict, total=False):
    need_id: str
    candidate_id: str
    category: str
    priority: str
    validation_activity: str
    trigger: str
    rationale: str
    linked_cautions: list[str]
    linked_tier: str
    linked_frontier_status: str
    linked_evidence_band: str
    status: str
    warnings: list[str]


class CandidateValidationNeeds(TypedDict, total=False):
    candidate_id: str
    system_name: str
    tier: str
    tier_label: str
    frontier_status: str
    evidence_maturity: str
    evidence_band: str
    research_mode_exposure: bool
    validation_need_count: int
    validation_needs: list[ValidationNeed]
    plan_status: str
    notes: list[str]
    warnings: list[str]


class ValidationNeedsRun(TypedDict, total=False):
    candidate_count: int
    plan_count: int
    validation_need_count: int
    research_mode_enabled: bool
    candidate_validation_needs: list[CandidateValidationNeeds]
    validation_summary: dict[str, Any]
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


def normalise_token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def validation_priority_for_tier(tier: str) -> str:
    tier_value = _as_string(tier)
    if tier_value in ("research_only_suggestion", "exploratory_option"):
        return "high"
    if tier_value in ("mature_reference_option", "parked_not_preferred"):
        return "low"
    if tier_value == "validation_needed_option":
        return "medium"
    return "medium"


def need_status_for_category(
    category: str,
    *,
    research_mode_exposure: bool = False,
) -> str:
    if category == "research_mode_gate":
        return "research_mode_validation_required"
    if research_mode_exposure:
        return "research_mode_validation_required"
    if category == "certification_caution_review":
        return "engineering_review_required"
    return "proposed_validation_need"


def validation_need(
    *,
    candidate_id: str,
    category: str,
    priority: str,
    validation_activity: str,
    trigger: str,
    rationale: str,
    linked_cautions: Sequence[str],
    linked_tier: str,
    linked_frontier_status: str,
    linked_evidence_band: str,
    research_mode_exposure: bool = False,
) -> ValidationNeed:
    warnings: list[str] = []
    if research_mode_exposure:
        warnings.append("Research-mode exposure requires gated validation review.")
    if category == "certification_caution_review":
        warnings.append("This review need does not imply certification approval.")

    return {
        "need_id": (
            f"{candidate_id}:{category}:{normalise_token(trigger) or 'general'}"
        ),
        "candidate_id": candidate_id,
        "category": category,
        "priority": priority,
        "validation_activity": validation_activity,
        "trigger": trigger,
        "rationale": rationale,
        "linked_cautions": list(linked_cautions),
        "linked_tier": linked_tier,
        "linked_frontier_status": linked_frontier_status,
        "linked_evidence_band": linked_evidence_band,
        "status": need_status_for_category(
            category,
            research_mode_exposure=research_mode_exposure,
        ),
        "warnings": warnings,
    }


def cautions_contain(cautions: Sequence[str], *tokens: str) -> bool:
    for caution in cautions:
        caution_text = str(caution).lower()
        caution_token = normalise_token(caution)
        for token in tokens:
            token_text = str(token).lower()
            token_normalised = normalise_token(token)
            if token_text in caution_text or token_normalised in caution_token:
                return True
    return False


def _add_need(
    needs: list[ValidationNeed],
    seen_keys: set[tuple[str, str]],
    *,
    candidate_id: str,
    category: str,
    priority: str,
    validation_activity: str,
    trigger: str,
    rationale: str,
    linked_cautions: Sequence[str],
    linked_tier: str,
    linked_frontier_status: str,
    linked_evidence_band: str,
    research_mode_exposure: bool = False,
) -> None:
    key = (category, trigger)
    if key in seen_keys:
        return
    seen_keys.add(key)
    needs.append(
        validation_need(
            candidate_id=candidate_id,
            category=category,
            priority=priority,
            validation_activity=validation_activity,
            trigger=trigger,
            rationale=rationale,
            linked_cautions=linked_cautions,
            linked_tier=linked_tier,
            linked_frontier_status=linked_frontier_status,
            linked_evidence_band=linked_evidence_band,
            research_mode_exposure=research_mode_exposure,
        )
    )


def build_validation_needs_for_tier_assessment(
    assessment: Mapping[str, Any],
) -> CandidateValidationNeeds:
    candidate_id = _as_string(assessment.get("candidate_id"), "unknown_candidate")
    system_name = _as_string(assessment.get("system_name"), "unknown_system")
    tier = _as_string(assessment.get("tier"), "exploratory_option")
    tier_label = _as_string(assessment.get("tier_label"), tier)
    frontier_status = _as_string(assessment.get("frontier_status"), "insufficient_basis")
    evidence_maturity = _as_string(assessment.get("evidence_maturity"), "unknown")
    evidence_band = _as_string(assessment.get("evidence_band"), "unknown")
    research_mode_exposure = assessment.get("research_mode_exposure") is True
    cautions = _string_list(deepcopy(assessment.get("review_cautions")))
    warnings = _string_list(deepcopy(assessment.get("warnings")))
    dominated_by = _string_list(assessment.get("dominated_by"))

    needs: list[ValidationNeed] = []
    seen_keys: set[tuple[str, str]] = set()

    if evidence_band in ("exploratory", "unknown"):
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="evidence_maturity",
            priority="high",
            validation_activity="Develop evidence basis before engineering down-selection.",
            trigger="exploratory_or_unknown_evidence",
            rationale="Evidence maturity is exploratory or unknown.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )
    elif evidence_band == "emerging":
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="evidence_maturity",
            priority="medium",
            validation_activity=(
                "Define targeted tests or literature evidence checks for emerging option."
            ),
            trigger="emerging_evidence",
            rationale="Evidence maturity is emerging.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )
    elif evidence_band == "engineering_reference":
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="evidence_maturity",
            priority="medium",
            validation_activity=(
                "Confirm applicability of engineering reference evidence to the target application."
            ),
            trigger="engineering_reference_evidence",
            rationale="Evidence maturity is engineering-reference level.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )
    elif evidence_band == "mature":
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="evidence_maturity",
            priority="low",
            validation_activity=(
                "Confirm mature reference assumptions and application boundary conditions."
            ),
            trigger="mature_reference_evidence",
            rationale="Evidence maturity is mature but assumptions still need review.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )

    if research_mode_exposure or tier == "research_only_suggestion":
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="research_mode_gate",
            priority="high",
            validation_activity=(
                "Keep option in research-mode review until independent evidence supports promotion."
            ),
            trigger="research_mode_exposure",
            rationale="Research-mode exposure prevents mature-option treatment.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=True,
        )

    if frontier_status == "dominated" or dominated_by:
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="dominated_option_review",
            priority="low",
            validation_activity=(
                "Record why the option was dominated and whether it should be parked "
                "or retained for a niche constraint."
            ),
            trigger="dominated_option",
            rationale="Candidate is dominated or has dominated-by links.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )

    if cautions_contain(cautions, "coating", "interface", "substrate", "spallation", "CTE"):
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="coating_interface_review",
            priority="medium",
            validation_activity=(
                "Review substrate/coating compatibility, interface degradation, "
                "spallation and inspection implications."
            ),
            trigger="coating_or_interface_caution",
            rationale="Review cautions mention coating/interface compatibility concerns.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )

    if cautions_contain(
        cautions,
        "gradient",
        "transition-zone",
        "spatial",
        "additive",
        "process repeatability",
        "residual stress",
    ):
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="spatial_gradient_feasibility",
            priority="high",
            validation_activity=(
                "Review gradient manufacturability, transition-zone risks, "
                "inspection feasibility and maturity."
            ),
            trigger="spatial_gradient_caution",
            rationale="Review cautions mention spatial-gradient or process feasibility concerns.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )

    if cautions_contain(cautions, "inspection", "repair", "maintainability", "through-life"):
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="inspection_repair_review",
            priority="medium",
            validation_activity=(
                "Assess inspection access, repair practicality and through-life "
                "maintainability implications."
            ),
            trigger="inspection_or_repair_caution",
            rationale="Review cautions mention inspection, repair or maintainability.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )

    _add_need(
        needs,
        seen_keys,
        candidate_id=candidate_id,
        category="certification_caution_review",
        priority="medium",
        validation_activity=(
            "Document certification and qualification assumptions, risks and evidence "
            "gaps without implying approval."
        ),
        trigger="decision_support_only",
        rationale="Decision-support output cannot provide qualification or certification approval.",
        linked_cautions=cautions,
        linked_tier=tier,
        linked_frontier_status=frontier_status,
        linked_evidence_band=evidence_band,
        research_mode_exposure=research_mode_exposure,
    )

    if frontier_status == "on_frontier":
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="frontier_review",
            priority="medium",
            validation_activity=(
                "Review frontier trade-offs against engineering priorities before any down-selection."
            ),
            trigger="on_frontier",
            rationale="Candidate is on the non-dominated frontier.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )
    elif frontier_status == "insufficient_basis":
        _add_need(
            needs,
            seen_keys,
            candidate_id=candidate_id,
            category="frontier_review",
            priority="high",
            validation_activity="Add comparable evidence or dimensions before using frontier position.",
            trigger="insufficient_frontier_basis",
            rationale="Candidate has insufficient comparable basis for frontier use.",
            linked_cautions=cautions,
            linked_tier=tier,
            linked_frontier_status=frontier_status,
            linked_evidence_band=evidence_band,
            research_mode_exposure=research_mode_exposure,
        )

    _add_need(
        needs,
        seen_keys,
        candidate_id=candidate_id,
        category="general_engineering_review",
        priority=validation_priority_for_tier(tier),
        validation_activity=(
            "Perform engineering review of assumptions, cautions and proposed next evidence steps."
        ),
        trigger=tier,
        rationale="Every tiered option requires engineering review before use.",
        linked_cautions=cautions,
        linked_tier=tier,
        linked_frontier_status=frontier_status,
        linked_evidence_band=evidence_band,
        research_mode_exposure=research_mode_exposure,
    )

    if any(need.get("status") == "research_mode_validation_required" for need in needs):
        plan_status = "research_mode_validation_required"
    elif needs:
        plan_status = "validation_needs_available"
    else:
        plan_status = "no_validation_needs_identified"

    if research_mode_exposure:
        _append_unique(warnings, "Research-mode exposure requires gated validation planning.")

    return {
        "candidate_id": candidate_id,
        "system_name": system_name,
        "tier": tier,
        "tier_label": tier_label,
        "frontier_status": frontier_status,
        "evidence_maturity": evidence_maturity,
        "evidence_band": evidence_band,
        "research_mode_exposure": research_mode_exposure,
        "validation_need_count": len(needs),
        "validation_needs": needs,
        "plan_status": plan_status,
        "notes": [
            "Validation needs are review prompts, not approval steps.",
            "No certification or qualification approval is implied.",
        ],
        "warnings": warnings,
    }


def _validation_summary(plans: Sequence[CandidateValidationNeeds]) -> dict[str, Any]:
    by_plan_status = {status: 0 for status in PLAN_STATUSES}
    by_category = {category: 0 for category in VALIDATION_CATEGORIES}
    by_priority = {priority: 0 for priority in VALIDATION_PRIORITIES}
    research_mode_plan_count = 0

    for plan in plans:
        plan_status = _as_string(plan.get("plan_status"), "no_validation_needs_identified")
        by_plan_status[plan_status] = by_plan_status.get(plan_status, 0) + 1
        if plan_status == "research_mode_validation_required":
            research_mode_plan_count += 1
        for need in plan.get("validation_needs", []):
            category = _as_string(need.get("category"), "unknown")
            priority = _as_string(need.get("priority"), "unknown")
            by_category[category] = by_category.get(category, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

    return {
        "by_plan_status": by_plan_status,
        "by_category": by_category,
        "by_priority": by_priority,
        "research_mode_plan_count": research_mode_plan_count,
    }


def build_validation_needs_from_tiers(
    tier_assessments: Sequence[Mapping[str, Any]],
) -> ValidationNeedsRun:
    plans = [
        build_validation_needs_for_tier_assessment(assessment)
        for assessment in tier_assessments
    ]
    warnings: list[str] = []
    if not tier_assessments:
        warnings.append("No tier assessments were supplied for validation-needs planning.")
    if any(
        plan.get("plan_status") == "research_mode_validation_required"
        for plan in plans
    ):
        warnings.append("One or more plans require research-mode validation review.")

    validation_need_count = sum(
        plan.get("validation_need_count", 0)
        for plan in plans
    )
    return {
        "candidate_count": len(tier_assessments),
        "plan_count": len(plans),
        "validation_need_count": validation_need_count,
        "research_mode_enabled": False,
        "candidate_validation_needs": plans,
        "validation_summary": _validation_summary(plans),
        "notes": [
            "This is validation-needs planning only.",
            "No certification or qualification approval is implied.",
        ],
        "warnings": warnings,
    }


def run_phase5_validation_needs(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> ValidationNeedsRun:
    tier_run = run_recommendation_tiers(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    validation_run = build_validation_needs_from_tiers(
        tier_run.get("tier_assessments", [])
    )
    warnings = _string_list(deepcopy(tier_run.get("warnings")))
    warnings.extend(validation_run.get("warnings", []))
    if research_mode_enabled:
        warnings.append(
            "Research mode is enabled; validation needs may include research-mode gates."
        )

    validation_run["candidate_count"] = int(tier_run.get("candidate_count") or len(candidates))
    validation_run["research_mode_enabled"] = research_mode_enabled
    validation_run["warnings"] = warnings
    return validation_run
