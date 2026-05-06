from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import EVIDENCE_MATURITY_LEVELS


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
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


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    for value in (
        evidence.get("maturity"),
        evidence.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        maturity = _text(value).upper()
        if maturity in EVIDENCE_MATURITY_LEVELS:
            return maturity
    return "unknown"


def _limit_ids(limiting_factors: Sequence[Mapping[str, Any]], *terms: str) -> list[str]:
    output: list[str] = []
    lowered_terms = tuple(term.lower() for term in terms)
    for index, factor in enumerate(limiting_factors):
        text = _blob(factor)
        if not terms or any(term in text for term in lowered_terms):
            output.append(_text(factor.get("factor"), f"limiting_factor_{index}"))
    return output


def _operator(
    *,
    operator_type: str,
    candidate: Mapping[str, Any],
    applies_to: Sequence[str],
    description: str,
    expected_benefit: str,
    new_risks: Sequence[str],
    evidence_maturity_impact: str = "none",
) -> dict[str, Any]:
    return {
        "operator_id": f"{_candidate_id(candidate)}::{operator_type}",
        "operator_type": operator_type,
        "candidate_id": _candidate_id(candidate),
        "applies_to_limiting_factors": list(applies_to),
        "description": description,
        "expected_benefit": expected_benefit,
        "new_risks": list(new_risks),
        "evidence_maturity_impact": evidence_maturity_impact,
        "generated_candidate_flag": False,
        "research_mode_required": False,
        "status": "suggested_not_applied",
    }


def _append_once(output: list[dict[str, Any]], operator: dict[str, Any]) -> None:
    if operator["operator_type"] not in {item["operator_type"] for item in output}:
        output.append(operator)


def select_refinement_operators(
    candidate: Mapping[str, Any],
    limiting_factors: Sequence[Mapping[str, Any]],
    package_context: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Suggest deterministic refinement operators without generating variants."""
    del package_context

    candidate_class = _candidate_class(candidate)
    architecture = _architecture(candidate)
    maturity = _evidence_maturity(candidate)
    text = f"{_blob(candidate)} {_blob(limiting_factors)}"
    output: list[dict[str, Any]] = []

    environmental_limits = _limit_ids(
        limiting_factors,
        "oxidation",
        "corrosion",
        "steam",
        "recession",
        "thermal",
        "surface",
    )
    if environmental_limits:
        if candidate_class in {"ceramic_matrix_composite", "monolithic_ceramic"}:
            _append_once(
                output,
                _operator(
                    operator_type="add_or_refine_environmental_barrier_coating",
                    candidate=candidate,
                    applies_to=environmental_limits,
                    description="Add or refine an EBC concept in the candidate-system description.",
                    expected_benefit="Makes oxidation, steam or recession protection explicit.",
                    new_risks=["EBC adhesion, recession durability and repair limits must be validated."],
                ),
            )
        _append_once(
            output,
            _operator(
                operator_type="add_or_refine_thermal_barrier_coating",
                candidate=candidate,
                applies_to=environmental_limits,
                description="Compare with or refine a thermal-barrier coating system concept.",
                expected_benefit="Surfaces thermal-margin and oxidation-protection tradeoffs.",
                new_risks=["Coating life, bond-coat oxidation and spallation risk may increase."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="add_near_surface_oxidation_gradient",
                candidate=candidate,
                applies_to=environmental_limits,
                description="Consider a deterministic near-surface oxidation-resistance gradient.",
                expected_benefit="Creates a coating alternative for surface-driven oxidation limits.",
                new_risks=["Transition-zone qualification and inspectability remain unresolved."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="compare_with_coating_enabled_alternative",
                candidate=candidate,
                applies_to=environmental_limits,
                description="Compare this record with coating-enabled alternatives already in the package.",
                expected_benefit="Keeps surface protection as a system architecture comparison.",
                new_risks=["No winner is selected by this skeleton."],
            ),
        )

    wear_limits = _limit_ids(limiting_factors, "wear", "fretting", "erosion", "contact")
    if wear_limits:
        _append_once(
            output,
            _operator(
                operator_type="add_wear_resistant_surface_gradient",
                candidate=candidate,
                applies_to=wear_limits,
                description="Consider a hard or wear-resistant surface gradient.",
                expected_benefit="Targets local contact/wear limits without changing the bulk record.",
                new_risks=["Residual stress and surface inspection burden may increase."],
            ),
        )
    if "spallation" in text or "mismatch" in text or "cte" in text:
        mismatch_limits = _limit_ids(limiting_factors, "spallation", "mismatch", "cte", "interface")
        _append_once(
            output,
            _operator(
                operator_type="compare_with_spatial_gradient_alternative",
                candidate=candidate,
                applies_to=mismatch_limits,
                description="Compare the coating-enabled system with spatial-gradient alternatives.",
                expected_benefit="Tests whether a graded transition could reduce discrete-interface risk.",
                new_risks=["Graded route maturity and certification risk may be lower than coating references."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="add_transition_gradient",
                candidate=candidate,
                applies_to=mismatch_limits,
                description="Add a transition-gradient concept to address interface mismatch.",
                expected_benefit="Could reduce abrupt property mismatch at the surface architecture.",
                new_risks=["No variant is generated; process window and inspection risks remain."],
            ),
        )

    if candidate_class == "coating_enabled" or architecture == "substrate_plus_coating":
        coating_limits = _limit_ids(limiting_factors, "coating", "interface", "spallation", "inspection")
        _append_once(
            output,
            _operator(
                operator_type="replace_coating_with_surface_gradient",
                candidate=candidate,
                applies_to=coating_limits,
                description="Compare a surface-gradient alternative to the discrete coating stack.",
                expected_benefit="Makes coating-vs-gradient architecture tradeoffs explicit.",
                new_risks=["Gradient evidence and repairability may be weaker than coating references."],
            ),
        )

    if candidate_class == "spatially_graded_am" or architecture == "spatial_gradient":
        graded_limits = _limit_ids(limiting_factors, "graded", "transition", "process", "inspect", "evidence")
        _append_once(
            output,
            _operator(
                operator_type="downgrade_to_exploratory_research_option",
                candidate=candidate,
                applies_to=graded_limits,
                description="Keep the graded AM record as exploratory until process-specific evidence exists.",
                expected_benefit="Prevents accidental maturity upgrade or recommendation-ready treatment.",
                new_risks=["May reduce apparent near-term feasibility."],
                evidence_maturity_impact="no_upgrade",
            ),
        )

    if candidate_class == "monolithic_ceramic" or "brittle" in text or "proof" in text:
        ceramic_limits = _limit_ids(limiting_factors, "brittle", "proof", "thermal shock", "ceramic")
        _append_once(
            output,
            _operator(
                operator_type="switch_monolithic_ceramic_to_cmc",
                candidate=candidate,
                applies_to=ceramic_limits,
                description="Compare the monolithic ceramic with a CMC architecture.",
                expected_benefit="Surfaces damage tolerance and thermal-shock alternatives.",
                new_risks=["CMC interphase, fiber and EBC dependencies must be validated."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="increase_inspection_or_proof_testing_burden",
                candidate=candidate,
                applies_to=ceramic_limits,
                description="Require explicit proof testing and inspection burden in downstream evaluation.",
                expected_benefit="Keeps brittle fracture and flaw sensitivity visible.",
                new_risks=["Inspection cost and acceptance criteria may become limiting."],
            ),
        )

    route_limits = _limit_ids(limiting_factors, "missing route", "process.missing", "route detail")
    if route_limits:
        _append_once(
            output,
            _operator(
                operator_type="improve_process_route_definition",
                candidate=candidate,
                applies_to=route_limits,
                description="Require a more explicit processing and inspection route.",
                expected_benefit="Improves traceability of manufacturing and qualification assumptions.",
                new_risks=["May expose additional cost, scale-up or inspection risks."],
            ),
        )

    if maturity in {"D", "E", "F"} or _limit_ids(limiting_factors, "low_maturity", "evidence maturity"):
        evidence_limits = _limit_ids(limiting_factors, "evidence", "maturity", "certification")
        _append_once(
            output,
            _operator(
                operator_type="require_additional_evidence_before_recommendation",
                candidate=candidate,
                applies_to=evidence_limits,
                description="Require additional evidence before any recommendation treatment.",
                expected_benefit="Prevents evidence maturity D/E/F candidates from appearing final.",
                new_risks=["No performance improvement is implied by this skeleton action."],
                evidence_maturity_impact="no_upgrade",
            ),
        )

    if not output:
        _append_once(
            output,
            _operator(
                operator_type="require_additional_evidence_before_recommendation",
                candidate=candidate,
                applies_to=_limit_ids(limiting_factors),
                description="Keep the candidate in transparent review until more evidence is available.",
                expected_benefit="Provides a conservative fallback when no specific operator applies.",
                new_risks=["No design change is generated."],
                evidence_maturity_impact="none",
            ),
        )

    return output


def summarize_refinement_operators(traces: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize suggested operators across optimisation traces."""
    options = [
        option
        for trace in traces
        for option in _as_list(trace.get("refinement_options"))
        if isinstance(option, Mapping)
    ]
    operator_type_counts = Counter(_text(option.get("operator_type"), "unknown") for option in options)
    status_counts = Counter(_text(option.get("status"), "unknown") for option in options)
    return {
        "trace_count": len(traces),
        "total_refinement_option_count": len(options),
        "operator_type_counts": dict(sorted(operator_type_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "generated_candidate_count": sum(
            1 for option in options if option.get("generated_candidate_flag") is True
        ),
        "research_mode_required_count": sum(
            1 for option in options if option.get("research_mode_required") is True
        ),
    }
