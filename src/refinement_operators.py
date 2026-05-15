from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.deterministic_optimisation import build_optimisation_opportunities


REFINEMENT_OPERATORS: tuple[str, ...] = (
    "add_thermal_barrier_coating",
    "add_environmental_barrier_coating",
    "add_oxidation_protection_coating",
    "add_wear_resistant_coating",
    "add_bond_coat_interface_system",
    "add_surface_oxidation_gradient",
    "add_surface_wear_gradient",
    "add_thermal_barrier_gradient",
    "add_tough_core_hard_surface_gradient",
    "add_metal_to_ceramic_transition_gradient",
)

REFINEMENT_STATUSES: tuple[str, ...] = (
    "proposed_for_deterministic_review",
    "research_mode_only",
    "unsupported_opportunity_type",
)


class RefinementProposal(TypedDict, total=False):
    proposal_id: str
    candidate_id: str
    base_system_name: str
    opportunity_id: str
    opportunity_family: str
    opportunity_type: str
    refinement_operator: str
    refined_system_name: str
    refinement_summary: str
    before_state: dict[str, Any]
    proposed_after_state: dict[str, Any]
    expected_benefits: list[str]
    introduced_risks: list[str]
    review_required: list[str]
    evidence_maturity: str
    status: str
    warnings: list[str]
    trace: list[str]


class RefinementProposalSet(TypedDict, total=False):
    candidate_id: str
    system_name: str
    limiting_factors: list[str]
    proposal_count: int
    proposals: list[RefinementProposal]
    notes: list[str]
    warnings: list[str]


class RefinementRun(TypedDict, total=False):
    candidate_count: int
    proposal_set_count: int
    proposal_count: int
    research_mode_enabled: bool
    proposal_sets: list[RefinementProposalSet]
    refinement_summary: dict[str, Any]
    notes: list[str]
    warnings: list[str]


_OPERATOR_BY_SOURCE_ID: dict[str, str] = {
    "thermal_barrier_coating": "add_thermal_barrier_coating",
    "environmental_barrier_coating": "add_environmental_barrier_coating",
    "oxidation_protection_coating": "add_oxidation_protection_coating",
    "wear_resistant_coating": "add_wear_resistant_coating",
    "bond_coat_interface_system": "add_bond_coat_interface_system",
    "surface_oxidation_gradient": "add_surface_oxidation_gradient",
    "surface_wear_gradient": "add_surface_wear_gradient",
    "thermal_barrier_gradient": "add_thermal_barrier_gradient",
    "tough_core_hard_surface": "add_tough_core_hard_surface_gradient",
    "metal_to_ceramic_transition": "add_metal_to_ceramic_transition_gradient",
}


def _non_empty_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _mapping_value(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _append_refinement_note(state: dict[str, Any], note: str) -> None:
    existing_notes = state.get("refinement_notes")
    notes = list(existing_notes) if isinstance(existing_notes, list) else []
    notes.append(note)
    state["refinement_notes"] = notes


def candidate_id(candidate: Mapping[str, Any], fallback_index: int = 0) -> str:
    return (
        _non_empty_string(candidate.get("candidate_id"))
        or _non_empty_string(candidate.get("id"))
        or f"candidate_{fallback_index}"
    )


def system_name(candidate: Mapping[str, Any], fallback_id: str) -> str:
    return (
        _non_empty_string(candidate.get("system_name"))
        or _non_empty_string(candidate.get("name"))
        or fallback_id
    )


def build_before_state(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "system_architecture_type": deepcopy(
            _mapping_value(
                candidate,
                "system_architecture_type",
                "architecture_type",
                default="unknown",
            )
        ),
        "coating_or_surface_system": deepcopy(
            _mapping_value(
                candidate,
                "coating_or_surface_system",
                "coating_system",
                default=None,
            )
        ),
        "gradient_architecture": deepcopy(candidate.get("gradient_architecture")),
        "process_route": deepcopy(candidate.get("process_route", {})),
        "evidence_package": deepcopy(
            _mapping_value(candidate, "evidence_package", "evidence", default={})
        ),
    }


def operator_for_opportunity(opportunity: Mapping[str, Any]) -> str:
    source_ids = (
        _non_empty_string(opportunity.get("source_id")),
        _non_empty_string(opportunity.get("opportunity_type")),
        _non_empty_string(opportunity.get("opportunity_family")),
    )
    for source_id in source_ids:
        if source_id in _OPERATOR_BY_SOURCE_ID:
            return _OPERATOR_BY_SOURCE_ID[source_id]
    return "unsupported_opportunity_type"


def proposed_after_state(
    before_state: Mapping[str, Any],
    opportunity: Mapping[str, Any],
) -> dict[str, Any]:
    after_state = deepcopy(dict(before_state))
    family = _non_empty_string(opportunity.get("opportunity_family"))
    evidence_maturity = str(opportunity.get("source_maturity") or "unknown")

    if family == "coating":
        if after_state.get("system_architecture_type") != "cmc_plus_ebc":
            after_state["system_architecture_type"] = "coating_enabled"
        after_state["coating_or_surface_system"] = {
            "option_id": str(
                opportunity.get("source_id")
                or opportunity.get("opportunity_type")
                or "unknown_coating_option"
            ),
            "option_name": str(opportunity.get("source_name") or "unknown coating option"),
            "evidence_maturity": evidence_maturity,
            "expected_benefits": deepcopy(list(opportunity.get("expected_benefits") or [])),
            "known_risks": deepcopy(list(opportunity.get("introduced_risks") or [])),
            "review_required": deepcopy(list(opportunity.get("review_required") or [])),
        }
        _append_refinement_note(
            after_state,
            "Proposed coating refinement only; not validated, selected or qualified.",
        )
    elif family == "spatial_gradient":
        after_state["system_architecture_type"] = "spatially_graded_am_system"
        after_state["gradient_architecture"] = {
            "gradient_template_id": str(
                opportunity.get("source_id")
                or opportunity.get("opportunity_type")
                or "unknown_gradient_template"
            ),
            "gradient_type": str(
                opportunity.get("opportunity_type")
                or opportunity.get("source_id")
                or "unknown_gradient_template"
            ),
            "evidence_maturity": evidence_maturity,
            "gradient_benefit_claim": deepcopy(list(opportunity.get("expected_benefits") or [])),
            "gradient_risks": deepcopy(list(opportunity.get("introduced_risks") or [])),
            "review_required": deepcopy(list(opportunity.get("review_required") or [])),
            "research_mode_required": opportunity.get("research_mode_required") is True,
        }
        _append_refinement_note(
            after_state,
            "Proposed spatial-gradient refinement only; not validated, selected or qualified.",
        )
    else:
        _append_refinement_note(
            after_state,
            "No supported refinement operator was found; before-state values are retained.",
        )

    return after_state


def build_refinement_proposal(
    candidate: Mapping[str, Any],
    opportunity: Mapping[str, Any],
    *,
    candidate_index: int = 0,
) -> RefinementProposal:
    base_candidate_id = candidate_id(candidate, candidate_index)
    base_system_name = system_name(candidate, base_candidate_id)
    before = build_before_state(candidate)
    refinement_operator = operator_for_opportunity(opportunity)
    after = proposed_after_state(before, opportunity)
    source_id = str(opportunity.get("source_id") or opportunity.get("opportunity_type") or "unknown")
    source_name = str(opportunity.get("source_name") or source_id)
    evidence_maturity = str(opportunity.get("source_maturity") or "unknown")

    if refinement_operator == "unsupported_opportunity_type":
        status = "unsupported_opportunity_type"
    elif (
        opportunity.get("status") == "research_mode_only"
        or opportunity.get("research_mode_required") is True
    ):
        status = "research_mode_only"
    else:
        status = "proposed_for_deterministic_review"

    warnings = deepcopy(list(opportunity.get("warnings") or []))
    if status == "research_mode_only":
        warnings.append("Research-mode-only refinement proposal requires gated review.")
    if status == "unsupported_opportunity_type":
        warnings.append("Unsupported opportunity type; no deterministic refinement operator exists.")

    opportunity_id = str(opportunity.get("opportunity_id") or source_id)

    return {
        "proposal_id": f"{base_candidate_id}:{refinement_operator}:{source_id}",
        "candidate_id": base_candidate_id,
        "base_system_name": base_system_name,
        "opportunity_id": opportunity_id,
        "opportunity_family": str(opportunity.get("opportunity_family") or "unknown"),
        "opportunity_type": str(opportunity.get("opportunity_type") or source_id),
        "refinement_operator": refinement_operator,
        "refined_system_name": f"{base_system_name} + {source_name}",
        "refinement_summary": (
            "Controlled deterministic refinement proposal derived from optimisation "
            f"opportunity {opportunity_id}; this is not a validated new candidate."
        ),
        "before_state": before,
        "proposed_after_state": after,
        "expected_benefits": deepcopy(list(opportunity.get("expected_benefits") or [])),
        "introduced_risks": deepcopy(list(opportunity.get("introduced_risks") or [])),
        "review_required": deepcopy(list(opportunity.get("review_required") or [])),
        "evidence_maturity": evidence_maturity,
        "status": status,
        "warnings": warnings,
        "trace": [
            f"Base candidate ID: {base_candidate_id}",
            f"Opportunity ID: {opportunity_id}",
            f"Refinement operator: {refinement_operator}",
            "No ranking, winner selection or certification claim has been made.",
        ],
    }


def build_refinement_proposals_for_candidate(
    candidate: Mapping[str, Any],
    *,
    limiting_factors: Sequence[str],
    candidate_index: int = 0,
    research_mode_enabled: bool = False,
) -> RefinementProposalSet:
    base_candidate_id = candidate_id(candidate, candidate_index)
    assessment = build_optimisation_opportunities(
        candidate,
        limiting_factors=list(limiting_factors),
        candidate_index=candidate_index,
        research_mode_enabled=research_mode_enabled,
    )
    proposals = [
        build_refinement_proposal(
            candidate,
            opportunity,
            candidate_index=candidate_index,
        )
        for opportunity in assessment.get("optimisation_opportunities", [])
    ]

    return {
        "candidate_id": base_candidate_id,
        "system_name": system_name(candidate, base_candidate_id),
        "limiting_factors": list(limiting_factors),
        "proposal_count": len(proposals),
        "proposals": proposals,
        "notes": [
            "Refinement proposals are controlled engineering concepts, not validated candidates.",
            "No score, rank, winner selection or qualification approval is produced.",
        ],
        "warnings": deepcopy(list(assessment.get("warnings") or [])),
    }


def _limiting_factors_for_run_candidate(
    candidate: Mapping[str, Any],
    *,
    base_candidate_id: str,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None,
    default_limiting_factors: Sequence[str] | None,
) -> list[str]:
    if (
        limiting_factors_by_candidate is not None
        and base_candidate_id in limiting_factors_by_candidate
    ):
        return list(limiting_factors_by_candidate[base_candidate_id])
    if default_limiting_factors is not None:
        return list(default_limiting_factors)
    if isinstance(candidate.get("limiting_factors"), list):
        return list(candidate["limiting_factors"])
    if isinstance(candidate.get("limiting_factor_ids"), list):
        return list(candidate["limiting_factor_ids"])
    return []


def _summary(proposal_sets: Sequence[RefinementProposalSet]) -> dict[str, Any]:
    by_status = {status: 0 for status in REFINEMENT_STATUSES}
    by_operator = {operator: 0 for operator in REFINEMENT_OPERATORS}
    by_operator["unsupported_opportunity_type"] = 0
    by_family = {"coating": 0, "spatial_gradient": 0}

    for proposal_set in proposal_sets:
        for proposal in proposal_set.get("proposals", []):
            status = proposal.get("status", "unknown")
            operator = proposal.get("refinement_operator", "unknown")
            family = proposal.get("opportunity_family", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            by_operator[operator] = by_operator.get(operator, 0) + 1
            by_family[family] = by_family.get(family, 0) + 1

    return {
        "by_status": by_status,
        "by_refinement_operator": by_operator,
        "by_opportunity_family": by_family,
    }


def run_refinement_proposals(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> RefinementRun:
    proposal_sets: list[RefinementProposalSet] = []

    for index, candidate in enumerate(candidates):
        base_candidate_id = candidate_id(candidate, index)
        limiting_factors = _limiting_factors_for_run_candidate(
            candidate,
            base_candidate_id=base_candidate_id,
            limiting_factors_by_candidate=limiting_factors_by_candidate,
            default_limiting_factors=default_limiting_factors,
        )
        proposal_sets.append(
            build_refinement_proposals_for_candidate(
                candidate,
                limiting_factors=limiting_factors,
                candidate_index=index,
                research_mode_enabled=research_mode_enabled,
            )
        )

    proposal_count = sum(proposal_set.get("proposal_count", 0) for proposal_set in proposal_sets)
    warnings: list[str] = []
    if research_mode_enabled:
        warnings.append("Research mode is enabled; refinement proposals require gated review.")

    return {
        "candidate_count": len(candidates),
        "proposal_set_count": len(proposal_sets),
        "proposal_count": proposal_count,
        "research_mode_enabled": research_mode_enabled,
        "proposal_sets": proposal_sets,
        "refinement_summary": _summary(proposal_sets),
        "notes": [
            "This run converts deterministic opportunities into controlled refinement proposals.",
            "It does not score, rank, select, certify or create unconstrained generated candidates.",
        ],
        "warnings": warnings,
    }
