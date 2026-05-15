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


def dedupe_refinement_operators(operators: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for operator in operators:
        item = dict(operator)
        key = _text(item.get("operator_id")) or f"{item.get('candidate_id')}::{item.get('operator_type')}"
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


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

    environmental_limits = _limit_ids(limiting_factors, "oxidation", "corrosion", "steam", "recession")
    coating_interface_limits = _limit_ids(limiting_factors, "coating", "spallation", "mismatch", "cte", "interface")
    inspection_repair_limits = _limit_ids(limiting_factors, "inspection", "inspectability", "repair", "repairability")
    gradient_limits = _limit_ids(limiting_factors, "graded", "transition", "process", "route", "inspect", "evidence")
    certification_limits = _limit_ids(limiting_factors, "certification", "qualification", "evidence", "maturity")
    ceramic_limits = _limit_ids(limiting_factors, "brittle", "proof", "thermal shock", "ceramic", "flaw")

    if candidate_class == "coating_enabled" or architecture == "substrate_plus_coating":
        coating_limits = coating_interface_limits or environmental_limits or inspection_repair_limits
        _append_once(
            output,
            _operator(
                operator_type="refine_coating_stack_and_interface_validation",
                candidate=candidate,
                applies_to=coating_limits,
                description="Tighten coating stack, interface and adhesion validation requirements.",
                expected_benefit="Keeps coating durability and interface evidence visible without changing the design.",
                new_risks=["Validation may expose additional coating life or repair constraints."],
            ),
        )
        if inspection_repair_limits:
            _append_once(
                output,
                _operator(
                    operator_type="define_coating_inspection_and_repair_plan",
                    candidate=candidate,
                    applies_to=inspection_repair_limits,
                    description="Require explicit coating inspection, repair and acceptance criteria.",
                    expected_benefit="Makes through-life maintenance assumptions auditable.",
                    new_risks=["Inspection burden and recoat logistics may increase."],
                ),
            )
        if coating_interface_limits:
            _append_once(
                output,
                _operator(
                    operator_type="compare_with_spatial_gradient_alternative",
                    candidate=candidate,
                    applies_to=coating_interface_limits,
                    description="Compare the coating-enabled system with spatial-gradient alternatives.",
                    expected_benefit="Tests whether a graded transition could reduce discrete-interface risk.",
                    new_risks=["Graded route maturity and certification risk may be lower than coating references."],
                ),
            )

    elif candidate_class == "spatially_graded_am" or architecture == "spatial_gradient":
        _append_once(
            output,
            _operator(
                operator_type="downgrade_to_exploratory_research_option",
                candidate=candidate,
                applies_to=gradient_limits or certification_limits,
                description="Keep the graded AM record as exploratory until process-specific evidence exists.",
                expected_benefit="Prevents accidental maturity upgrade or recommendation-ready treatment.",
                new_risks=["May reduce apparent near-term feasibility."],
                evidence_maturity_impact="no_upgrade",
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="validate_gradient_transition_zone",
                candidate=candidate,
                applies_to=gradient_limits,
                description="Require explicit transition-zone validation for the spatial gradient.",
                expected_benefit="Targets cracking, residual stress and through-depth verification uncertainty.",
                new_risks=["Validation may show process-window sensitivity."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="improve_process_route_definition",
                candidate=candidate,
                applies_to=gradient_limits,
                description="Require a more explicit processing and inspection route.",
                expected_benefit="Improves traceability of manufacturing and qualification assumptions.",
                new_risks=["May expose additional cost, scale-up or inspection risks."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="compare_with_coating_enabled_alternative",
                candidate=candidate,
                applies_to=gradient_limits or environmental_limits,
                description="Compare this gradient with coating-enabled alternatives already in the package.",
                expected_benefit="Keeps mature coating analogues visible as a certification comparison.",
                new_risks=["No winner is selected by this skeleton."],
            ),
        )

    elif candidate_class == "monolithic_ceramic":
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
                applies_to=ceramic_limits or inspection_repair_limits,
                description="Require explicit proof testing and flaw inspection burden in downstream evaluation.",
                expected_benefit="Keeps brittle fracture and flaw sensitivity visible.",
                new_risks=["Inspection cost and acceptance criteria may become limiting."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="validate_thermal_shock_and_flaw_tolerance",
                candidate=candidate,
                applies_to=ceramic_limits,
                description="Require thermal-shock and flaw-tolerance evidence before recommendation treatment.",
                expected_benefit="Makes monolithic ceramic fracture constraints explicit.",
                new_risks=["May reduce apparent near-term feasibility."],
            ),
        )
        if environmental_limits:
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
                    operator_type="add_near_surface_oxidation_gradient",
                    candidate=candidate,
                    applies_to=environmental_limits,
                    description="Consider a deterministic near-surface oxidation-resistance gradient.",
                    expected_benefit="Creates a coating alternative for surface-driven oxidation limits.",
                    new_risks=["Transition-zone qualification and inspectability remain unresolved."],
                ),
            )

    elif candidate_class == "ceramic_matrix_composite":
        if environmental_limits or "ebc" in text or "environmental barrier" in text:
            _append_once(
                output,
                _operator(
                    operator_type="validate_environmental_barrier_coating",
                    candidate=candidate,
                    applies_to=environmental_limits or certification_limits,
                    description="Require EBC adhesion, recession and compatibility validation.",
                    expected_benefit="Keeps environmental protection dependency explicit.",
                    new_risks=["EBC evidence may dominate qualification burden."],
                ),
            )
        _append_once(
            output,
            _operator(
                operator_type="validate_cmc_interphase_and_fiber_architecture",
                candidate=candidate,
                applies_to=_limit_ids(limiting_factors, "interphase", "fiber", "cmc", "interface"),
                description="Require interphase, fiber architecture and matrix defect validation.",
                expected_benefit="Surfaces coupled CMC architecture risks.",
                new_risks=["Inspection or process variability may remain limiting."],
            ),
        )
        if inspection_repair_limits:
            _append_once(
                output,
                _operator(
                    operator_type="define_cmc_inspection_and_repair_plan",
                    candidate=candidate,
                    applies_to=inspection_repair_limits,
                    description="Require explicit CMC/EBC inspection and repair disposition criteria.",
                    expected_benefit="Makes through-life assumptions auditable.",
                    new_risks=["Repair route may remain limited."],
                ),
            )
        if certification_limits:
            _append_once(
                output,
                _operator(
                    operator_type="compare_with_mature_ni_tbc_reference",
                    candidate=candidate,
                    applies_to=certification_limits,
                    description="Compare certification burden against mature Ni/TBC analogue records.",
                    expected_benefit="Keeps maturity contrast visible without selecting a winner.",
                    new_risks=["Metallic analogue may carry density or thermal-margin tradeoffs."],
                ),
            )

    elif candidate_class == "metallic":
        _append_once(
            output,
            _operator(
                operator_type="define_surface_protection_system",
                candidate=candidate,
                applies_to=environmental_limits or coating_interface_limits,
                description="Define the oxidation or surface-protection route as part of the material system.",
                expected_benefit="Makes surface protection dependency explicit.",
                new_risks=["Protection route may become qualification-limiting."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="validate_oxidation_protection_route",
                candidate=candidate,
                applies_to=environmental_limits or certification_limits,
                description="Require oxidation protection and substrate compatibility validation.",
                expected_benefit="Keeps refractory or metallic surface-protection assumptions visible.",
                new_risks=["Validation may show process or repair immaturity."],
            ),
        )
        _append_once(
            output,
            _operator(
                operator_type="compare_with_coating_enabled_alternative",
                candidate=candidate,
                applies_to=environmental_limits or coating_interface_limits,
                description="Compare this record with coating-enabled alternatives already in the package.",
                expected_benefit="Keeps surface protection as a system architecture comparison.",
                new_risks=["No winner is selected by this skeleton."],
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

    route_limits = _limit_ids(limiting_factors, "missing route", "process.missing", "route detail", "validation_gap")
    if route_limits and not any(item["operator_type"] == "improve_process_route_definition" for item in output):
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

    return dedupe_refinement_operators(output)


def summarize_refinement_operators(traces: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize suggested operators across optimisation traces."""
    options = [
        option
        for trace in traces
        for option in _as_list(trace.get("refinement_options_full") or trace.get("refinement_options"))
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
