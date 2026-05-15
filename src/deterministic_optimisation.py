from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.coating_vs_gradient_diagnostics import build_coating_vs_gradient_diagnostic


OPTIMISATION_STATUSES: tuple[str, ...] = (
    "no_limiting_factors_supplied",
    "no_deterministic_opportunity",
    "deterministic_opportunities_identified",
    "research_mode_opportunities_identified",
)

OPPORTUNITY_FAMILIES: tuple[str, ...] = (
    "coating",
    "spatial_gradient",
)

COATING_REVIEW_REQUIREMENTS: tuple[str, ...] = (
    "substrate_interface_review",
    "inspection_review",
    "repair_review",
    "evidence_review",
)

GRADIENT_REVIEW_REQUIREMENTS: tuple[str, ...] = (
    "gradient_feasibility_review",
    "transition_zone_review",
    "inspection_review",
    "repair_review",
    "maturity_review",
)


class OptimisationOpportunity(TypedDict, total=False):
    opportunity_id: str
    candidate_id: str
    limiting_factor: str
    opportunity_family: str
    opportunity_type: str
    source_id: str
    source_name: str
    source_maturity: str
    research_mode_required: bool
    rationale: str
    expected_benefits: list[str]
    introduced_risks: list[str]
    review_required: list[str]
    status: str
    warnings: list[str]


class CandidateOptimisationAssessment(TypedDict, total=False):
    candidate_id: str
    system_name: str
    system_architecture_type: str
    candidate_class: str | None
    substrate_family: str | None
    process_routes: list[str]
    limiting_factors: list[str]
    diagnostic_status: str
    coating_option_count: int
    gradient_template_count: int
    optimisation_opportunities: list[OptimisationOpportunity]
    optimisation_status: str
    notes: list[str]
    warnings: list[str]


class DeterministicOptimisationRun(TypedDict, total=False):
    candidate_count: int
    assessment_count: int
    opportunity_count: int
    research_mode_enabled: bool
    candidate_assessments: list[CandidateOptimisationAssessment]
    optimisation_summary: dict[str, Any]
    notes: list[str]
    warnings: list[str]


def normalise_token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def _non_empty_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [item for item in values if isinstance(item, str)]


def candidate_identifier(candidate: Mapping[str, Any], fallback_index: int = 0) -> str:
    return (
        _non_empty_string(candidate.get("candidate_id"))
        or _non_empty_string(candidate.get("id"))
        or f"candidate_{fallback_index}"
    )


def candidate_system_name(candidate: Mapping[str, Any], fallback_id: str) -> str:
    return (
        _non_empty_string(candidate.get("system_name"))
        or _non_empty_string(candidate.get("name"))
        or fallback_id
    )


def candidate_architecture_type(candidate: Mapping[str, Any]) -> str:
    return (
        _non_empty_string(candidate.get("system_architecture_type"))
        or _non_empty_string(candidate.get("architecture_type"))
        or "unknown"
    )


def candidate_class(candidate: Mapping[str, Any]) -> str | None:
    return (
        _non_empty_string(candidate.get("candidate_class"))
        or _non_empty_string(candidate.get("material_family"))
        or _non_empty_string(candidate.get("base_material_family"))
    )


def substrate_family(candidate: Mapping[str, Any]) -> str | None:
    return (
        _non_empty_string(candidate.get("substrate_family"))
        or _non_empty_string(candidate.get("base_material_family"))
        or _non_empty_string(candidate.get("material_family"))
    )


def process_routes(candidate: Mapping[str, Any]) -> list[str]:
    routes = _string_list(candidate.get("process_routes"))
    if routes:
        return list(routes)

    process_route = candidate.get("process_route")
    if not isinstance(process_route, Mapping):
        return []

    extracted: list[str] = []
    for key in ("route_name", "route_family", "process"):
        value = _non_empty_string(process_route.get(key))
        if value:
            extracted.append(value)
    return extracted


def limiting_factors_for_candidate(
    candidate: Mapping[str, Any],
    *,
    supplied_limiting_factors: Sequence[str] | None = None,
) -> list[str]:
    if supplied_limiting_factors is not None:
        return list(supplied_limiting_factors)

    if isinstance(candidate.get("limiting_factors"), list):
        return list(candidate["limiting_factors"])
    if isinstance(candidate.get("limiting_factor_ids"), list):
        return list(candidate["limiting_factor_ids"])
    return []


def _first_limiting_factor(limiting_factors: Sequence[str]) -> str:
    return str(limiting_factors[0]) if limiting_factors else ""


def _opportunity_id(candidate_id: str, family: str, source_id: str) -> str:
    return f"{candidate_id}:{family}:{source_id}"


def _rationale(family_label: str, limiting_factors: Sequence[str]) -> str:
    factors = ", ".join(str(item) for item in limiting_factors)
    return (
        f"This {family_label} option addresses one or more supplied limiting factors: "
        f"{factors}."
    )


def _coating_opportunity(
    option: Mapping[str, Any],
    *,
    candidate_id: str,
    limiting_factors: Sequence[str],
) -> OptimisationOpportunity:
    option_id = str(option.get("option_id") or "unknown_coating_option")
    return {
        "opportunity_id": _opportunity_id(candidate_id, "coating", option_id),
        "candidate_id": candidate_id,
        "limiting_factor": _first_limiting_factor(limiting_factors),
        "opportunity_family": "coating",
        "opportunity_type": option_id,
        "source_id": option_id,
        "source_name": str(option.get("option_name") or option_id),
        "source_maturity": str(option.get("evidence_maturity_default") or "unknown"),
        "research_mode_required": False,
        "rationale": _rationale("coating", limiting_factors),
        "expected_benefits": deepcopy(list(option.get("expected_benefits") or [])),
        "introduced_risks": deepcopy(list(option.get("known_risks") or [])),
        "review_required": list(COATING_REVIEW_REQUIREMENTS),
        "status": "available_for_deterministic_review",
        "warnings": [],
    }


def _gradient_opportunity(
    template: Mapping[str, Any],
    *,
    candidate_id: str,
    limiting_factors: Sequence[str],
) -> OptimisationOpportunity:
    template_id = str(template.get("template_id") or "unknown_gradient_template")
    research_mode_required = template.get("research_mode_required") is True
    return {
        "opportunity_id": _opportunity_id(candidate_id, "spatial_gradient", template_id),
        "candidate_id": candidate_id,
        "limiting_factor": _first_limiting_factor(limiting_factors),
        "opportunity_family": "spatial_gradient",
        "opportunity_type": template_id,
        "source_id": template_id,
        "source_name": str(template.get("template_name") or template_id),
        "source_maturity": str(template.get("minimum_evidence_maturity_default") or "unknown"),
        "research_mode_required": research_mode_required,
        "rationale": _rationale("spatial-gradient template", limiting_factors),
        "expected_benefits": deepcopy(list(template.get("expected_benefits") or [])),
        "introduced_risks": deepcopy(list(template.get("known_risks") or [])),
        "review_required": list(GRADIENT_REVIEW_REQUIREMENTS),
        "status": "research_mode_only"
        if research_mode_required
        else "available_for_deterministic_review",
        "warnings": ["Research-mode-only opportunity requires gated review."]
        if research_mode_required
        else [],
    }


def build_optimisation_opportunities(
    candidate: Mapping[str, Any],
    *,
    limiting_factors: Sequence[str],
    candidate_index: int = 0,
    research_mode_enabled: bool = False,
) -> CandidateOptimisationAssessment:
    candidate_id = candidate_identifier(candidate, candidate_index)
    system_name = candidate_system_name(candidate, candidate_id)
    architecture_type = candidate_architecture_type(candidate)
    class_value = candidate_class(candidate)
    substrate_value = substrate_family(candidate)
    routes = process_routes(candidate)
    copied_limiting_factors = list(limiting_factors)

    diagnostic = build_coating_vs_gradient_diagnostic(
        copied_limiting_factors,
        candidate_class=class_value,
        substrate_family=substrate_value,
        process_routes=routes,
        research_mode_enabled=research_mode_enabled,
    )

    opportunities: list[OptimisationOpportunity] = []
    for option in diagnostic.get("coating_options_considered", []):
        opportunities.append(
            _coating_opportunity(
                option,
                candidate_id=candidate_id,
                limiting_factors=copied_limiting_factors,
            )
        )
    for template in diagnostic.get("gradient_templates_considered", []):
        opportunities.append(
            _gradient_opportunity(
                template,
                candidate_id=candidate_id,
                limiting_factors=copied_limiting_factors,
            )
        )

    research_mode_only_present = any(
        opportunity.get("status") == "research_mode_only" for opportunity in opportunities
    )
    if not copied_limiting_factors:
        optimisation_status = "no_limiting_factors_supplied"
    elif not opportunities:
        optimisation_status = "no_deterministic_opportunity"
    elif research_mode_only_present:
        optimisation_status = "research_mode_opportunities_identified"
    else:
        optimisation_status = "deterministic_opportunities_identified"

    notes = [
        "This is a deterministic opportunity scan, not final optimisation approval.",
        "No score, rank, winner or refined candidate variant is produced.",
    ]
    warnings = list(diagnostic.get("warnings", []))
    if research_mode_only_present:
        warnings.append("Research-mode-only opportunities require gated specialist review.")

    return {
        "candidate_id": candidate_id,
        "system_name": system_name,
        "system_architecture_type": architecture_type,
        "candidate_class": class_value,
        "substrate_family": substrate_value,
        "process_routes": routes,
        "limiting_factors": copied_limiting_factors,
        "diagnostic_status": str(diagnostic.get("comparison_status") or "unknown"),
        "coating_option_count": int(diagnostic.get("coating_option_count") or 0),
        "gradient_template_count": int(diagnostic.get("gradient_template_count") or 0),
        "optimisation_opportunities": opportunities,
        "optimisation_status": optimisation_status,
        "notes": notes,
        "warnings": warnings,
    }


def _summary(
    assessments: Sequence[CandidateOptimisationAssessment],
) -> dict[str, Any]:
    by_status = {status: 0 for status in OPTIMISATION_STATUSES}
    by_family = {family: 0 for family in OPPORTUNITY_FAMILIES}

    for assessment in assessments:
        status = assessment.get("optimisation_status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        for opportunity in assessment.get("optimisation_opportunities", []):
            family = opportunity.get("opportunity_family", "unknown")
            by_family[family] = by_family.get(family, 0) + 1

    return {
        "by_optimisation_status": by_status,
        "by_opportunity_family": by_family,
    }


def run_deterministic_optimisation(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> DeterministicOptimisationRun:
    assessments: list[CandidateOptimisationAssessment] = []

    for index, candidate in enumerate(candidates):
        candidate_id = candidate_identifier(candidate, index)
        if (
            limiting_factors_by_candidate is not None
            and candidate_id in limiting_factors_by_candidate
        ):
            limiting_factors = limiting_factors_for_candidate(
                candidate,
                supplied_limiting_factors=limiting_factors_by_candidate[candidate_id],
            )
        elif default_limiting_factors is not None:
            limiting_factors = limiting_factors_for_candidate(
                candidate,
                supplied_limiting_factors=default_limiting_factors,
            )
        else:
            limiting_factors = limiting_factors_for_candidate(candidate)

        assessments.append(
            build_optimisation_opportunities(
                candidate,
                limiting_factors=limiting_factors,
                candidate_index=index,
                research_mode_enabled=research_mode_enabled,
            )
        )

    opportunity_count = sum(
        len(assessment.get("optimisation_opportunities", [])) for assessment in assessments
    )
    warnings: list[str] = []
    if research_mode_enabled:
        warnings.append("Research mode is enabled; exploratory opportunities require gated review.")

    return {
        "candidate_count": len(candidates),
        "assessment_count": len(assessments),
        "opportunity_count": opportunity_count,
        "research_mode_enabled": research_mode_enabled,
        "candidate_assessments": assessments,
        "optimisation_summary": _summary(assessments),
        "notes": [
            "This controller produces deterministic opportunities only.",
            "It does not score, rank, select, certify or generate candidate variants.",
        ],
        "warnings": warnings,
    }
