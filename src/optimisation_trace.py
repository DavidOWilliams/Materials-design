from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.refinement_operators import (
    build_refinement_proposals_for_candidate,
    run_refinement_proposals,
)


TRACE_BADGES: tuple[str, ...] = (
    "deterministic_review",
    "coating_refinement",
    "spatial_gradient_refinement",
    "research_mode_only",
    "unsupported_refinement",
    "requires_review",
    "no_ranking",
    "no_certification_claim",
)


class StateSummary(TypedDict, total=False):
    system_architecture_type: str
    has_coating_or_surface_system: bool
    has_gradient_architecture: bool
    process_route_summary: list[str]
    evidence_maturity: str
    notable_fields_present: list[str]


class OptimisationTraceRecord(TypedDict, total=False):
    trace_id: str
    candidate_id: str
    proposal_id: str
    opportunity_id: str
    refinement_operator: str
    status: str
    before_state_summary: StateSummary
    proposed_after_state_summary: StateSummary
    change_summary: list[str]
    expected_benefits: list[str]
    introduced_risks: list[str]
    review_required: list[str]
    evidence_maturity: str
    trace_narrative: list[str]
    warnings: list[str]
    ui_badges: list[str]


class CandidateOptimisationTrace(TypedDict, total=False):
    candidate_id: str
    system_name: str
    limiting_factors: list[str]
    trace_count: int
    traces: list[OptimisationTraceRecord]
    notes: list[str]
    warnings: list[str]


class OptimisationTraceRun(TypedDict, total=False):
    candidate_count: int
    trace_set_count: int
    trace_count: int
    research_mode_enabled: bool
    candidate_traces: list[CandidateOptimisationTrace]
    trace_summary: dict[str, Any]
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


def evidence_maturity_from_state(state: Mapping[str, Any]) -> str:
    evidence_package = state.get("evidence_package")
    if isinstance(evidence_package, Mapping):
        maturity = _as_string(evidence_package.get("evidence_maturity"))
        if maturity:
            return maturity

    coating = state.get("coating_or_surface_system")
    if isinstance(coating, Mapping):
        maturity = _as_string(coating.get("evidence_maturity"))
        if maturity:
            return maturity

    gradient = state.get("gradient_architecture")
    if isinstance(gradient, Mapping):
        maturity = _as_string(gradient.get("evidence_maturity"))
        if maturity:
            return maturity

    return "unknown"


def process_route_summary(state: Mapping[str, Any]) -> list[str]:
    process_route = state.get("process_route")
    if isinstance(process_route, Mapping):
        summary: list[str] = []
        for key in ("route_name", "route_family", "process"):
            value = _as_string(process_route.get(key))
            if value:
                summary.append(value)
        return summary
    if isinstance(process_route, str):
        value = _as_string(process_route)
        return [value] if value else []
    return []


def summarise_state(state: Mapping[str, Any]) -> StateSummary:
    notable_fields_present: list[str] = []
    for field in (
        "coating_or_surface_system",
        "gradient_architecture",
        "process_route",
        "evidence_package",
    ):
        if state.get(field):
            notable_fields_present.append(field)

    return {
        "system_architecture_type": _as_string(
            state.get("system_architecture_type"),
            "unknown",
        ),
        "has_coating_or_surface_system": bool(state.get("coating_or_surface_system")),
        "has_gradient_architecture": bool(state.get("gradient_architecture")),
        "process_route_summary": process_route_summary(state),
        "evidence_maturity": evidence_maturity_from_state(state),
        "notable_fields_present": notable_fields_present,
    }


def build_change_summary(
    before_state: Mapping[str, Any],
    proposed_after_state: Mapping[str, Any],
) -> list[str]:
    changes: list[str] = []

    before_architecture = before_state.get("system_architecture_type")
    after_architecture = proposed_after_state.get("system_architecture_type")
    if before_architecture != after_architecture:
        changes.append(
            "system_architecture_type changed from "
            f"{_as_string(before_architecture, 'unknown')} to "
            f"{_as_string(after_architecture, 'unknown')}."
        )

    tracked_fields = (
        ("coating_or_surface_system", "coating_or_surface_system"),
        ("gradient_architecture", "gradient_architecture"),
        ("process_route", "process_route"),
        ("evidence_package", "evidence_package"),
    )
    for field, label in tracked_fields:
        before_value = before_state.get(field)
        after_value = proposed_after_state.get(field)
        if before_value == after_value:
            continue
        if not before_value and after_value:
            changes.append(f"{label} added in proposed after-state.")
        elif before_value and not after_value:
            changes.append(f"{label} removed in proposed after-state.")
        else:
            changes.append(f"{label} changed in proposed after-state.")

    if not changes:
        return ["No tracked before/after state changes were recorded."]
    return changes


def build_ui_badges(proposal: Mapping[str, Any]) -> list[str]:
    status = _as_string(proposal.get("status"))
    family = _as_string(proposal.get("opportunity_family"))
    badge_checks = {
        "deterministic_review": status == "proposed_for_deterministic_review",
        "coating_refinement": family == "coating",
        "spatial_gradient_refinement": family == "spatial_gradient",
        "research_mode_only": status == "research_mode_only",
        "unsupported_refinement": status == "unsupported_opportunity_type",
        "requires_review": True,
        "no_ranking": True,
        "no_certification_claim": True,
    }

    badges: list[str] = []
    for badge in TRACE_BADGES:
        if badge_checks.get(badge) and badge not in badges:
            badges.append(badge)
    return badges


def build_trace_record(proposal: Mapping[str, Any]) -> OptimisationTraceRecord:
    before_state_value = proposal.get("before_state")
    after_state_value = proposal.get("proposed_after_state")
    before_state = before_state_value if isinstance(before_state_value, Mapping) else {}
    after_state = after_state_value if isinstance(after_state_value, Mapping) else {}
    proposal_id = _as_string(proposal.get("proposal_id"), "unknown_proposal")
    refinement_operator = _as_string(
        proposal.get("refinement_operator"),
        "unknown_refinement_operator",
    )
    status = _as_string(proposal.get("status"), "unknown")

    return {
        "trace_id": f"trace:{proposal_id}",
        "candidate_id": _as_string(proposal.get("candidate_id"), "unknown_candidate"),
        "proposal_id": proposal_id,
        "opportunity_id": _as_string(proposal.get("opportunity_id"), "unknown_opportunity"),
        "refinement_operator": refinement_operator,
        "status": status,
        "before_state_summary": summarise_state(before_state),
        "proposed_after_state_summary": summarise_state(after_state),
        "change_summary": build_change_summary(before_state, after_state),
        "expected_benefits": _string_list(deepcopy(proposal.get("expected_benefits"))),
        "introduced_risks": _string_list(deepcopy(proposal.get("introduced_risks"))),
        "review_required": _string_list(deepcopy(proposal.get("review_required"))),
        "evidence_maturity": _as_string(proposal.get("evidence_maturity"), "unknown"),
        "trace_narrative": [
            f"Refinement operator used: {refinement_operator}.",
            f"Proposal status: {status}.",
            "The after-state is proposed only and is not a validated candidate.",
            "No ranking, winner selection or certification claim has been made.",
        ],
        "warnings": _string_list(deepcopy(proposal.get("warnings"))),
        "ui_badges": build_ui_badges(proposal),
    }


def build_traces_for_candidate(
    candidate: Mapping[str, Any],
    *,
    limiting_factors: Sequence[str],
    candidate_index: int = 0,
    research_mode_enabled: bool = False,
) -> CandidateOptimisationTrace:
    proposal_set = build_refinement_proposals_for_candidate(
        candidate,
        limiting_factors=list(limiting_factors),
        candidate_index=candidate_index,
        research_mode_enabled=research_mode_enabled,
    )
    traces = [
        build_trace_record(proposal)
        for proposal in proposal_set.get("proposals", [])
    ]

    return {
        "candidate_id": _as_string(proposal_set.get("candidate_id"), f"candidate_{candidate_index}"),
        "system_name": _as_string(proposal_set.get("system_name"), f"candidate_{candidate_index}"),
        "limiting_factors": _string_list(proposal_set.get("limiting_factors")),
        "trace_count": len(traces),
        "traces": traces,
        "notes": [
            "Optimisation traces are audit records for proposed refinements, not approvals.",
            "They do not rank, select, validate, qualify or certify a material system.",
        ],
        "warnings": _string_list(deepcopy(proposal_set.get("warnings"))),
    }


def _trace_summary(candidate_traces: Sequence[CandidateOptimisationTrace]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_refinement_operator: dict[str, int] = {}
    by_badge = {badge: 0 for badge in TRACE_BADGES}

    for candidate_trace in candidate_traces:
        for trace in candidate_trace.get("traces", []):
            status = _as_string(trace.get("status"), "unknown")
            operator = _as_string(trace.get("refinement_operator"), "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            by_refinement_operator[operator] = by_refinement_operator.get(operator, 0) + 1
            for badge in trace.get("ui_badges", []):
                by_badge[badge] = by_badge.get(badge, 0) + 1

    return {
        "by_status": by_status,
        "by_refinement_operator": by_refinement_operator,
        "by_badge": by_badge,
    }


def run_optimisation_traces(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> OptimisationTraceRun:
    proposal_run = run_refinement_proposals(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )

    candidate_traces: list[CandidateOptimisationTrace] = []
    for index, proposal_set in enumerate(proposal_run.get("proposal_sets", [])):
        traces = [
            build_trace_record(proposal)
            for proposal in proposal_set.get("proposals", [])
        ]
        candidate_traces.append(
            {
                "candidate_id": _as_string(proposal_set.get("candidate_id"), f"candidate_{index}"),
                "system_name": _as_string(proposal_set.get("system_name"), f"candidate_{index}"),
                "limiting_factors": _string_list(proposal_set.get("limiting_factors")),
                "trace_count": len(traces),
                "traces": traces,
                "notes": [
                    "Optimisation traces are audit records for proposed refinements, not approvals.",
                    "They do not rank, select, validate, qualify or certify a material system.",
                ],
                "warnings": _string_list(deepcopy(proposal_set.get("warnings"))),
            }
        )

    trace_count = sum(candidate_trace.get("trace_count", 0) for candidate_trace in candidate_traces)
    warnings: list[str] = []
    if research_mode_enabled:
        warnings.append("Research mode is enabled; optimisation traces require gated review.")

    return {
        "candidate_count": len(candidates),
        "trace_set_count": len(candidate_traces),
        "trace_count": trace_count,
        "research_mode_enabled": research_mode_enabled,
        "candidate_traces": candidate_traces,
        "trace_summary": _trace_summary(candidate_traces),
        "notes": [
            "This trace run packages proposed refinements for auditability only.",
            "It is intended for future UI and review-pack use and does not approve outcomes.",
        ],
        "warnings": warnings,
    }
