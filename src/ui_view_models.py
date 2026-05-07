from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.contracts import evidence_maturity_label, evidence_maturity_treatment
from src.recommendation_builder import summarize_recommendation_package
from src.recommendation_narrative import render_recommendation_narrative_markdown


DEFERRED_CAPABILITIES = [
    "final ranking not implemented",
    "Pareto optimisation not implemented",
    "deterministic optimisation skeleton only; no variants generated",
    "Streamlit Build 4 UI not integrated",
    "live research adapters disabled",
]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


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


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _evidence(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(candidate.get("evidence_package") or candidate.get("evidence"))


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _evidence(candidate)
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _source_type(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("source_type") or candidate.get("source_label"), "unknown")


def _summarize_constituents(candidate: Mapping[str, Any]) -> list[dict[str, str]]:
    summaries: list[dict[str, str]] = []
    for item in _as_list(candidate.get("constituents")):
        constituent = _mapping(item)
        if not constituent:
            summaries.append({"name": _text(item, "unknown"), "role": "unknown", "material_family": "unknown"})
            continue
        summaries.append(
            {
                "name": _text(constituent.get("name"), "unknown"),
                "role": _text(constituent.get("role"), "unknown"),
                "material_family": _text(constituent.get("material_family"), "unknown"),
            }
        )
    return summaries


def _summarize_coating(candidate: Mapping[str, Any]) -> dict[str, Any]:
    coating = _mapping(
        candidate.get("coating_or_surface_system")
        or candidate.get("coating_system")
        or candidate.get("environmental_barrier_coating")
    )
    if not coating:
        return {"present": False, "summary": ""}
    layers = _as_list(coating.get("layers"))
    return {
        "present": True,
        "coating_type": _text(coating.get("coating_type") or coating.get("name"), "unknown"),
        "substrate_compatibility": _text(coating.get("substrate_compatibility"), "unknown"),
        "layer_count": len(layers),
        "failure_modes": [_text(item) for item in _as_list(coating.get("failure_modes")) if _text(item)],
        "summary": _text(coating.get("coating_type") or coating.get("name"), "coating or surface system"),
    }


def _summarize_gradient(candidate: Mapping[str, Any]) -> dict[str, Any]:
    gradient = _mapping(candidate.get("gradient_architecture"))
    if not gradient:
        return {"present": False, "summary": ""}
    gradient_types = [_text(item) for item in _as_list(gradient.get("gradient_types")) if _text(item)]
    return {
        "present": True,
        "gradient_types": gradient_types,
        "manufacturing_route": _text(gradient.get("manufacturing_route"), "unknown"),
        "transition_risks": [_text(item) for item in _as_list(gradient.get("transition_risks")) if _text(item)],
        "summary": ", ".join(gradient_types) if gradient_types else _text(gradient.get("notes"), "gradient architecture"),
    }


def _summarize_interfaces(candidate: Mapping[str, Any]) -> dict[str, Any]:
    interfaces = [_mapping(item) for item in _as_list(candidate.get("interfaces")) if _mapping(item)]
    return {
        "count": len(interfaces),
        "interface_types": [_text(item.get("interface_type"), "unknown_interface") for item in interfaces],
        "risk_levels": [_text(item.get("risk_level"), "unknown") for item in interfaces],
        "high_risk": [
            _text(item.get("interface_type"), "unknown_interface")
            for item in interfaces
            if _text(item.get("risk_level")) == "high"
        ],
    }


def _top_factor_signals(candidate: Mapping[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    for score in _as_list(candidate.get("factor_scores")):
        factor = _mapping(score)
        if not factor:
            continue
        signals.append(
            {
                "factor": _text(factor.get("factor") or factor.get("factor_name"), "unknown"),
                "score": factor.get("score"),
                "confidence": factor.get("confidence"),
                "reason": _text(factor.get("reason")),
                "warnings": [_text(item) for item in _as_list(factor.get("warnings")) if _text(item)],
            }
        )
    return signals[:limit]


def _candidate_warnings(candidate: Mapping[str, Any]) -> list[str]:
    warnings: list[str] = []
    for field in ("assembly_warnings", "factor_model_warnings", "normalization_warnings", "process_route_warnings"):
        for warning in _as_list(candidate.get(field)):
            text = _text(warning)
            if text and text not in warnings:
                warnings.append(text)
    return warnings


def _summarize_process_route(candidate: Mapping[str, Any]) -> dict[str, Any]:
    details = _mapping(candidate.get("process_route_details"))
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))
    process_chain = [_text(item) for item in _as_list(details.get("process_chain")) if _text(item)]
    return {
        "process_route_template_id": _text(candidate.get("process_route_template_id"), "unknown_route"),
        "process_route_display_name": _text(details.get("display_name"), "Unknown process route"),
        "process_family": _text(details.get("process_family"), "unknown"),
        "process_chain": process_chain,
        "process_chain_summary": " -> ".join(process_chain[:4]),
        "inspection_burden": _text(inspection.get("inspection_burden"), "unknown"),
        "inspection_methods": [_text(item) for item in _as_list(inspection.get("inspection_methods")) if _text(item)],
        "inspection_challenges": [
            _text(item) for item in _as_list(inspection.get("inspection_challenges")) if _text(item)
        ],
        "repairability_level": _text(repairability.get("repairability_level"), "unknown"),
        "repair_concept": _text(repairability.get("repair_concept"), "not specified"),
        "qualification_burden": _text(qualification.get("qualification_burden"), "unknown"),
        "route_risks": [_text(item) for item in _as_list(candidate.get("route_risks")) if _text(item)],
        "route_validation_gaps": [
            _text(item) for item in _as_list(candidate.get("route_validation_gaps")) if _text(item)
        ],
    }


def build_candidate_card_view_model(candidate: Mapping[str, Any]) -> dict[str, Any]:
    maturity = _evidence_maturity(candidate)
    evidence = _evidence(candidate)
    process_route = _summarize_process_route(candidate)
    surface_profile = _mapping(candidate.get("surface_function_profile"))
    readiness = _mapping(candidate.get("decision_readiness"))
    narrative_card = _mapping(candidate.get("recommendation_narrative_card"))
    constraints = [
        _mapping(item) for item in _as_list(readiness.get("constraints")) if _mapping(item)
    ]
    return {
        "candidate_id": _text(candidate.get("candidate_id"), "unknown_candidate"),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _text(candidate.get("system_architecture_type"), "unknown"),
        "source_type": _source_type(candidate),
        "evidence_maturity": maturity,
        "evidence_label": _text(evidence.get("maturity_label"), evidence_maturity_label(maturity)),
        "recommendation_treatment": _text(
            evidence.get("recommendation_treatment"),
            evidence_maturity_treatment(maturity),
        ),
        "generated_candidate_flag": candidate.get("generated_candidate_flag") is True,
        "research_mode_flag": candidate.get("research_mode_flag") is True,
        "constituents_summary": _summarize_constituents(candidate),
        "coating_or_surface_summary": _summarize_coating(candidate),
        "gradient_summary": _summarize_gradient(candidate),
        "interface_summary": _summarize_interfaces(candidate),
        "process_route_summary": process_route,
        "process_route_display_name": process_route["process_route_display_name"],
        "process_family": process_route["process_family"],
        "process_chain_summary": process_route["process_chain_summary"],
        "inspection_burden": process_route["inspection_burden"],
        "inspection_methods": process_route["inspection_methods"],
        "inspection_challenges": process_route["inspection_challenges"],
        "repairability_level": process_route["repairability_level"],
        "repair_concept": process_route["repair_concept"],
        "qualification_burden": process_route["qualification_burden"],
        "route_risks": process_route["route_risks"],
        "route_validation_gaps": process_route["route_validation_gaps"],
        "primary_surface_functions": [
            _text(item) for item in _as_list(surface_profile.get("primary_surface_functions")) if _text(item)
        ],
        "secondary_surface_functions": [
            _text(item) for item in _as_list(surface_profile.get("secondary_surface_functions")) if _text(item)
        ],
        "unknown_surface_function_flag": surface_profile.get("unknown_surface_function_flag") is True,
        "readiness_category": _text(readiness.get("readiness_category"), "unknown_readiness"),
        "readiness_label": _text(readiness.get("readiness_label"), "Unknown decision readiness"),
        "readiness_status": _text(readiness.get("readiness_status"), "unknown"),
        "readiness_confidence": _text(readiness.get("readiness_confidence"), "low"),
        "allowed_use": _text(readiness.get("allowed_use"), "not specified"),
        "disallowed_use": _text(readiness.get("disallowed_use"), "not specified"),
        "required_next_evidence": [
            _text(item) for item in _as_list(readiness.get("required_next_evidence")) if _text(item)
        ],
        "top_readiness_constraints": [
            {
                "constraint_id": _text(item.get("constraint_id")),
                "category": _text(item.get("category"), "unknown"),
                "severity": _text(item.get("severity"), "unknown"),
                "reason": _text(item.get("reason")),
                "source_field": _text(item.get("source_field")),
            }
            for item in constraints[:4]
        ],
        "narrative_role": _text(narrative_card.get("narrative_role"), "unknown_role"),
        "responsible_use": _text(narrative_card.get("responsible_use")),
        "main_strengths": [_text(item) for item in _as_list(narrative_card.get("main_strengths")) if _text(item)],
        "main_cautions": [_text(item) for item in _as_list(narrative_card.get("main_cautions")) if _text(item)],
        "evidence_gaps": [_text(item) for item in _as_list(narrative_card.get("evidence_gaps")) if _text(item)],
        "top_factor_signals": _top_factor_signals(candidate),
        "warnings": _candidate_warnings(candidate),
        "certification_risk_flags": [_text(item) for item in _as_list(candidate.get("certification_risk_flags")) if _text(item)],
        "uncertainty_flags": [_text(item) for item in _as_list(candidate.get("uncertainty_flags")) if _text(item)],
    }


def build_package_summary_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    summary = summarize_recommendation_package(package)
    diagnostics = dict(_mapping(package.get("diagnostics")))
    optimisation_summary = _mapping(package.get("optimisation_summary"))
    comparison = _mapping(
        package.get("coating_vs_gradient_comparison")
        or optimisation_summary.get("coating_vs_gradient_comparison")
    )
    return {
        **summary,
        "source_mix_summary": dict(_mapping(package.get("source_mix_summary"))),
        "diagnostics": diagnostics,
        "warnings": [_text(item) for item in _as_list(package.get("warnings")) if _text(item)],
        "live_model_calls_made": diagnostics.get("live_model_calls_made") is True,
        "optimisation_status": _text(optimisation_summary.get("status"), summary.get("optimisation_status")),
        "total_limiting_factor_count": optimisation_summary.get("total_limiting_factor_count", 0),
        "total_refinement_option_count": optimisation_summary.get("total_refinement_option_count", 0),
        "generated_candidate_count": optimisation_summary.get("generated_candidate_count", 0),
        "coating_vs_gradient_comparison_required": comparison.get("comparison_required") is True,
        "process_route_summary": dict(_mapping(package.get("process_route_summary"))),
        "surface_function_coverage_summary": dict(_mapping(package.get("surface_function_coverage_summary"))),
        "surface_function_required_coverage": dict(_mapping(package.get("surface_function_required_coverage"))),
        "decision_readiness_summary": dict(_mapping(package.get("decision_readiness_summary"))),
        "evidence_maturity_summary": dict(_mapping(package.get("evidence_maturity_summary"))),
        "factor_summary": dict(_mapping(package.get("factor_summary"))),
        "interface_risk_summary": dict(
            _mapping(_mapping(package.get("system_assembly_summary")).get("interface_risk_summary"))
        ),
    }


def build_optimisation_summary_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    optimisation_summary = _mapping(package.get("optimisation_summary"))
    return {
        "status": _text(optimisation_summary.get("status"), "unknown"),
        "candidate_count": optimisation_summary.get("candidate_count", 0),
        "trace_count": optimisation_summary.get("trace_count", 0),
        "total_limiting_factor_count": optimisation_summary.get("total_limiting_factor_count", 0),
        "displayed_limiting_factor_count": optimisation_summary.get("displayed_limiting_factor_count", 0),
        "full_limiting_factor_count": optimisation_summary.get("full_limiting_factor_count", 0),
        "total_hard_limit_count": optimisation_summary.get("total_hard_limit_count", 0),
        "total_advisory_warning_count": optimisation_summary.get("total_advisory_warning_count", 0),
        "total_evidence_maturity_limit_count": optimisation_summary.get(
            "total_evidence_maturity_limit_count", 0
        ),
        "total_route_risk_count": optimisation_summary.get("total_route_risk_count", 0),
        "total_certification_limit_count": optimisation_summary.get("total_certification_limit_count", 0),
        "average_limiting_factors_per_candidate": optimisation_summary.get(
            "average_limiting_factors_per_candidate", 0.0
        ),
        "total_refinement_option_count": optimisation_summary.get("total_refinement_option_count", 0),
        "generated_candidate_count": optimisation_summary.get("generated_candidate_count", 0),
        "live_model_calls_made": optimisation_summary.get("live_model_calls_made") is True,
        "severity_counts": dict(_mapping(optimisation_summary.get("severity_counts"))),
        "operator_type_counts": dict(_mapping(optimisation_summary.get("operator_type_counts"))),
        "warnings": [_text(item) for item in _as_list(optimisation_summary.get("warnings")) if _text(item)],
    }


def build_coating_vs_gradient_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    optimisation_summary = _mapping(package.get("optimisation_summary"))
    comparison = _mapping(
        package.get("coating_vs_gradient_comparison")
        or optimisation_summary.get("coating_vs_gradient_comparison")
    )
    return {
        "comparison_required": comparison.get("comparison_required") is True,
        "coating_enabled_candidate_ids": [
            _text(item) for item in _as_list(comparison.get("coating_enabled_candidate_ids")) if _text(item)
        ],
        "spatial_gradient_candidate_ids": [
            _text(item) for item in _as_list(comparison.get("spatial_gradient_candidate_ids")) if _text(item)
        ],
        "shared_limiting_factor_themes": [
            _text(item) for item in _as_list(comparison.get("shared_limiting_factor_themes")) if _text(item)
        ],
        "comparison_notes": [
            _text(item) for item in _as_list(comparison.get("comparison_notes")) if _text(item)
        ],
        "warnings": [_text(item) for item in _as_list(comparison.get("warnings")) if _text(item)],
    }


def build_coating_vs_gradient_diagnostic_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    diagnostic = _mapping(package.get("coating_vs_gradient_diagnostic"))
    return {
        "diagnostic_status": _text(diagnostic.get("diagnostic_status"), "not_available"),
        "comparison_required": diagnostic.get("comparison_required") is True,
        "coating_enabled_candidate_ids": [
            _text(item) for item in _as_list(diagnostic.get("coating_enabled_candidate_ids")) if _text(item)
        ],
        "spatial_gradient_candidate_ids": [
            _text(item) for item in _as_list(diagnostic.get("spatial_gradient_candidate_ids")) if _text(item)
        ],
        "coating_profiles": [
            dict(item) for item in _as_list(diagnostic.get("coating_profiles")) if isinstance(item, Mapping)
        ],
        "gradient_profiles": [
            dict(item) for item in _as_list(diagnostic.get("gradient_profiles")) if isinstance(item, Mapping)
        ],
        "pairwise_comparisons": [
            dict(item) for item in _as_list(diagnostic.get("pairwise_comparisons")) if isinstance(item, Mapping)
        ],
        "shared_surface_function_themes": [
            _text(item) for item in _as_list(diagnostic.get("shared_surface_function_themes")) if _text(item)
        ],
        "coating_common_strengths": [
            _text(item) for item in _as_list(diagnostic.get("coating_common_strengths")) if _text(item)
        ],
        "gradient_common_strengths": [
            _text(item) for item in _as_list(diagnostic.get("gradient_common_strengths")) if _text(item)
        ],
        "coating_common_risks": [
            _text(item) for item in _as_list(diagnostic.get("coating_common_risks")) if _text(item)
        ],
        "gradient_common_risks": [
            _text(item) for item in _as_list(diagnostic.get("gradient_common_risks")) if _text(item)
        ],
        "evidence_maturity_observations": dict(_mapping(diagnostic.get("evidence_maturity_observations"))),
        "inspection_repair_observations": dict(_mapping(diagnostic.get("inspection_repair_observations"))),
        "qualification_observations": dict(_mapping(diagnostic.get("qualification_observations"))),
        "validation_gap_observations": dict(_mapping(diagnostic.get("validation_gap_observations"))),
        "summary_notes": [_text(item) for item in _as_list(diagnostic.get("summary_notes")) if _text(item)],
        "warnings": [_text(item) for item in _as_list(diagnostic.get("warnings")) if _text(item)],
    }


def build_surface_function_coverage_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(package.get("surface_function_coverage_summary"))
    required_coverage = _mapping(package.get("surface_function_required_coverage"))
    required_functions = [
        dict(item) for item in _as_list(package.get("required_surface_functions")) if isinstance(item, Mapping)
    ]
    return {
        "required_surface_functions": required_functions,
        "function_to_candidate_ids": dict(_mapping(summary.get("function_to_candidate_ids"))),
        "candidate_to_function_ids": dict(_mapping(summary.get("candidate_to_function_ids"))),
        "coating_enabled_function_counts": dict(_mapping(summary.get("coating_enabled_function_counts"))),
        "spatial_gradient_function_counts": dict(_mapping(summary.get("spatial_gradient_function_counts"))),
        "shared_coating_gradient_functions": [
            _text(item) for item in _as_list(summary.get("shared_coating_gradient_functions")) if _text(item)
        ],
        "functions_only_seen_in_coatings": [
            _text(item) for item in _as_list(summary.get("functions_only_seen_in_coatings")) if _text(item)
        ],
        "functions_only_seen_in_gradients": [
            _text(item) for item in _as_list(summary.get("functions_only_seen_in_gradients")) if _text(item)
        ],
        "unknown_surface_function_candidate_ids": [
            _text(item) for item in _as_list(summary.get("unknown_surface_function_candidate_ids")) if _text(item)
        ],
        "coverage_notes": [_text(item) for item in _as_list(required_coverage.get("coverage_notes")) if _text(item)],
        "warnings": [
            _text(item)
            for item in _as_list(summary.get("warnings")) + _as_list(required_coverage.get("warnings"))
            if _text(item)
        ],
        "covered_required_function_ids": [
            _text(item) for item in _as_list(required_coverage.get("covered_required_function_ids")) if _text(item)
        ],
        "uncovered_required_function_ids": [
            _text(item) for item in _as_list(required_coverage.get("uncovered_required_function_ids")) if _text(item)
        ],
    }


def build_decision_readiness_summary_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(package.get("decision_readiness_summary"))
    return {
        "candidate_count": summary.get("candidate_count", 0),
        "readiness_category_counts": dict(_mapping(summary.get("readiness_category_counts"))),
        "readiness_status_counts": dict(_mapping(summary.get("readiness_status_counts"))),
        "evidence_maturity_counts": dict(_mapping(summary.get("evidence_maturity_counts"))),
        "candidates_by_readiness_category": dict(_mapping(summary.get("candidates_by_readiness_category"))),
        "candidates_by_readiness_status": dict(_mapping(summary.get("candidates_by_readiness_status"))),
        "not_decision_ready_candidate_ids": [
            _text(item) for item in _as_list(summary.get("not_decision_ready_candidate_ids")) if _text(item)
        ],
        "research_only_candidate_ids": [
            _text(item) for item in _as_list(summary.get("research_only_candidate_ids")) if _text(item)
        ],
        "exploratory_only_candidate_ids": [
            _text(item) for item in _as_list(summary.get("exploratory_only_candidate_ids")) if _text(item)
        ],
        "usable_as_reference_candidate_ids": [
            _text(item) for item in _as_list(summary.get("usable_as_reference_candidate_ids")) if _text(item)
        ],
        "usable_with_caveats_candidate_ids": [
            _text(item) for item in _as_list(summary.get("usable_with_caveats_candidate_ids")) if _text(item)
        ],
        "blocking_constraint_count": summary.get("blocking_constraint_count", 0),
        "high_constraint_count": summary.get("high_constraint_count", 0),
        "common_constraint_categories": dict(_mapping(summary.get("common_constraint_categories"))),
        "warnings": [_text(item) for item in _as_list(summary.get("warnings")) if _text(item)],
    }


def build_recommendation_narrative_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    narrative = _mapping(package.get("recommendation_narrative"))
    return {
        "narrative_status": _text(narrative.get("narrative_status"), "not_available"),
        "executive_summary": [_text(item) for item in _as_list(narrative.get("executive_summary")) if _text(item)],
        "mature_comparison_references": [
            _text(item) for item in _as_list(narrative.get("mature_comparison_references")) if _text(item)
        ],
        "engineering_analogue_options": [
            _text(item) for item in _as_list(narrative.get("engineering_analogue_options")) if _text(item)
        ],
        "exploratory_options": [_text(item) for item in _as_list(narrative.get("exploratory_options")) if _text(item)],
        "research_only_options": [_text(item) for item in _as_list(narrative.get("research_only_options")) if _text(item)],
        "not_decision_ready_options": [
            _text(item) for item in _as_list(narrative.get("not_decision_ready_options")) if _text(item)
        ],
        "coating_vs_gradient_considerations": [
            _text(item) for item in _as_list(narrative.get("coating_vs_gradient_considerations")) if _text(item)
        ],
        "key_evidence_gaps": [_text(item) for item in _as_list(narrative.get("key_evidence_gaps")) if _text(item)],
        "process_inspection_repair_considerations": [
            _text(item) for item in _as_list(narrative.get("process_inspection_repair_considerations")) if _text(item)
        ],
        "decision_readiness_overview": dict(_mapping(narrative.get("decision_readiness_overview"))),
        "next_validation_steps": [
            _text(item) for item in _as_list(narrative.get("next_validation_steps")) if _text(item)
        ],
        "deferred_capabilities": [
            _text(item) for item in _as_list(narrative.get("deferred_capabilities")) if _text(item)
        ],
        "safety_disclaimer": _text(narrative.get("safety_disclaimer")),
        "candidate_narrative_cards": [
            dict(item) for item in _as_list(narrative.get("candidate_narrative_cards")) if isinstance(item, Mapping)
        ],
        "warnings": [_text(item) for item in _as_list(narrative.get("warnings")) if _text(item)],
    }


def build_optimisation_trace_card(trace: Mapping[str, Any]) -> dict[str, Any]:
    limiting_factors = [_mapping(item) for item in _as_list(trace.get("limiting_factors")) if _mapping(item)]
    refinement_options = [_mapping(item) for item in _as_list(trace.get("refinement_options")) if _mapping(item)]
    return {
        "candidate_id": _text(trace.get("candidate_id"), "unknown_candidate"),
        "candidate_class": _text(trace.get("candidate_class"), "unknown"),
        "system_architecture_type": _text(trace.get("system_architecture_type"), "unknown"),
        "evidence_maturity": _text(trace.get("evidence_maturity"), "unknown"),
        "status": _text(trace.get("status"), "unknown"),
        "limiting_factor_count": trace.get("limiting_factor_count", len(limiting_factors)),
        "displayed_limiting_factor_count": trace.get("displayed_limiting_factor_count", len(limiting_factors)),
        "hard_limit_count": trace.get("hard_limit_count", 0),
        "advisory_warning_count": trace.get("advisory_warning_count", 0),
        "evidence_maturity_limit_count": trace.get("evidence_maturity_limit_count", 0),
        "route_risk_count": trace.get("route_risk_count", 0),
        "certification_limit_count": trace.get("certification_limit_count", 0),
        "refinement_option_count": trace.get("refinement_option_count", len(refinement_options)),
        "displayed_refinement_option_count": trace.get("displayed_refinement_option_count", len(refinement_options)),
        "top_limiting_factors": [
            {
                "factor": _text(item.get("factor"), "unknown_factor"),
                "namespace": _text(item.get("namespace"), "unknown"),
                "severity": _text(item.get("severity"), "unknown"),
                "category": _text(item.get("category"), "unknown"),
                "normalised_score": item.get("normalised_score"),
                "reason": _text(item.get("reason")),
            }
            for item in limiting_factors
        ],
        "top_refinement_options": [
            {
                "operator_type": _text(item.get("operator_type"), "unknown_operator"),
                "status": _text(item.get("status"), "unknown"),
                "description": _text(item.get("description")),
                "expected_benefit": _text(item.get("expected_benefit")),
                "generated_candidate_flag": item.get("generated_candidate_flag") is True,
            }
            for item in refinement_options
        ],
        "variants_generated_count": len(_as_list(trace.get("variants_generated"))),
        "before_after_delta_count": len(_as_list(trace.get("before_after_deltas"))),
        "warnings": [_text(item) for item in _as_list(trace.get("warnings")) if _text(item)],
    }


def build_recommendation_package_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [
        candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)
    ]
    traces = [
        trace for trace in _as_list(package.get("optimisation_trace")) if isinstance(trace, Mapping)
    ]
    return {
        "summary": build_package_summary_view_model(package),
        "optimisation_summary_view": build_optimisation_summary_view_model(package),
        "coating_vs_gradient_comparison_view": build_coating_vs_gradient_view_model(package),
        "coating_vs_gradient_diagnostic_view": build_coating_vs_gradient_diagnostic_view_model(package),
        "surface_function_coverage_view": build_surface_function_coverage_view_model(package),
        "decision_readiness_summary_view": build_decision_readiness_summary_view_model(package),
        "recommendation_narrative_view": build_recommendation_narrative_view_model(package),
        "optimisation_trace_cards": [build_optimisation_trace_card(trace) for trace in traces],
        "candidate_cards": [build_candidate_card_view_model(candidate) for candidate in candidates],
        "warnings": [_text(item) for item in _as_list(package.get("warnings")) if _text(item)],
        "diagnostics": dict(_mapping(package.get("diagnostics"))),
        "deferred_capabilities": list(DEFERRED_CAPABILITIES),
    }


def _markdown_table_from_mix(title: str, mix: Mapping[str, Any]) -> list[str]:
    lines = [f"### {title}"]
    if not mix:
        return lines + ["- none"]
    return lines + [f"- {key}: {value}" for key, value in sorted(mix.items())]


def render_markdown_report(package: Mapping[str, Any]) -> str:
    view_model = build_recommendation_package_view_model(package)
    summary = view_model["summary"]
    design_space = _mapping(package.get("design_space"))
    lines = [
        "# Build 4 Package Summary",
        "",
        "This is not a final recommendation. Deterministic optimisation is a skeleton. Research adapters are disabled.",
        "No variants were generated. No final ranking was produced. No Pareto optimisation was performed. No live model calls were made.",
        "Refinement operators are suggestions, not applied design changes.",
        "Low maturity D/E/F candidates are exploratory and not qualification-ready.",
        "",
        f"- Run ID: {summary.get('run_id')}",
        f"- Package status: {summary.get('package_status')}",
        f"- Candidate count: {summary.get('candidate_count')}",
        f"- Ranked recommendations: {summary.get('ranked_recommendations_count')}",
        f"- Pareto front entries: {summary.get('pareto_front_count')}",
        f"- Optimisation status: {summary.get('optimisation_status')}",
        "",
        "## Design-Space Summary",
        f"- Research mode enabled: {summary.get('research_mode_enabled')}",
        f"- Live model calls made: {summary.get('live_model_calls_made')}",
        f"- Allowed candidate classes: {', '.join(_text(item) for item in _as_list(design_space.get('allowed_candidate_classes')))}",
        f"- System architectures: {', '.join(_text(item) for item in _as_list(design_space.get('system_architectures')))}",
        "",
        "## Candidate-System Coverage",
    ]
    lines.extend(_markdown_table_from_mix("Candidate classes", summary.get("candidate_class_mix", {})))
    lines.extend(_markdown_table_from_mix("System architectures", summary.get("system_architecture_mix", {})))
    lines.extend(["", "## Evidence Maturity"])
    lines.extend(_markdown_table_from_mix("Evidence maturity mix", summary.get("evidence_maturity_mix", {})))
    readiness_view = view_model["decision_readiness_summary_view"]
    narrative_view = view_model["recommendation_narrative_view"]
    narrative_markdown = render_recommendation_narrative_markdown(narrative_view)
    lines.extend(["", narrative_markdown.rstrip()])
    lines.extend(
        [
            "",
            "## Decision Readiness",
            "- Decision readiness is not final recommendation logic.",
            "- Decision readiness is not qualification/certification approval.",
            "- Low maturity D/E/F candidates are exploratory or research-only.",
        ]
    )
    lines.extend(_markdown_table_from_mix("Readiness categories", readiness_view.get("readiness_category_counts", {})))
    lines.extend(_markdown_table_from_mix("Readiness statuses", readiness_view.get("readiness_status_counts", {})))
    lines.extend(
        [
            "- Mature/reference candidates: "
            + (", ".join(readiness_view.get("usable_as_reference_candidate_ids", [])) or "none"),
            "- Caveated engineering candidates: "
            + (", ".join(readiness_view.get("usable_with_caveats_candidate_ids", [])) or "none"),
            "- Exploratory-only candidates: "
            + (", ".join(readiness_view.get("exploratory_only_candidate_ids", [])) or "none"),
            "- Research-only candidates: "
            + (", ".join(readiness_view.get("research_only_candidate_ids", [])) or "none"),
            "- Not-decision-ready candidates: "
            + (", ".join(readiness_view.get("not_decision_ready_candidate_ids", [])) or "none"),
        ]
    )
    lines.extend(
        _markdown_table_from_mix(
            "Common readiness constraint categories",
            readiness_view.get("common_constraint_categories", {}),
        )
    )
    for card in view_model["candidate_cards"]:
        lines.extend(
            [
                f"### Readiness: {card['candidate_id']}",
                f"- Class: {card['candidate_class']}",
                f"- Evidence maturity: {card['evidence_maturity']}",
                f"- Readiness: {card['readiness_label']}",
                f"- Readiness status: {card['readiness_status']}",
                f"- Allowed use: {card['allowed_use']}",
                f"- Disallowed use: {card['disallowed_use']}",
                "- Required next evidence: "
                + (", ".join(card["required_next_evidence"]) or "not specified"),
            ]
        )
        for constraint in card["top_readiness_constraints"]:
            lines.append(
                "- Top constraint: "
                f"{constraint['category']} ({constraint['severity']}) - {constraint['reason']}"
            )
    surface_view = view_model["surface_function_coverage_view"]
    required_labels = [
        _text(item.get("function_id"))
        for item in surface_view.get("required_surface_functions", [])
        if isinstance(item, Mapping)
    ]
    lines.extend(
        [
            "",
            "## Surface Function Coverage",
            "- Required surface functions: " + (", ".join(required_labels) or "none inferred"),
            "- Covered required functions: "
            + (", ".join(surface_view.get("covered_required_function_ids", [])) or "none visible"),
            "- Uncovered required functions: "
            + (", ".join(surface_view.get("uncovered_required_function_ids", [])) or "none"),
        ]
    )
    lines.extend(_markdown_table_from_mix("Function-to-candidate coverage", surface_view.get("function_to_candidate_ids", {})))
    lines.extend(_markdown_table_from_mix("Coating-enabled function coverage", surface_view.get("coating_enabled_function_counts", {})))
    lines.extend(_markdown_table_from_mix("Spatial-gradient function coverage", surface_view.get("spatial_gradient_function_counts", {})))
    lines.extend(
        [
            "- Shared coating/gradient functions: "
            + (", ".join(surface_view.get("shared_coating_gradient_functions", [])) or "none visible"),
            "- Functions only seen in coatings: "
            + (", ".join(surface_view.get("functions_only_seen_in_coatings", [])) or "none visible"),
            "- Functions only seen in gradients: "
            + (", ".join(surface_view.get("functions_only_seen_in_gradients", [])) or "none visible"),
            "- Candidates with unknown surface function: "
            + (", ".join(surface_view.get("unknown_surface_function_candidate_ids", [])) or "none"),
        ]
    )
    for note in surface_view.get("coverage_notes", [])[:4]:
        lines.append(f"- {note}")
    process_route_summary = _mapping(summary.get("process_route_summary"))
    lines.extend(["", "## Process Route, Inspection and Repairability"])
    lines.extend(_markdown_table_from_mix("Process families", process_route_summary.get("process_family_counts", {})))
    lines.extend(_markdown_table_from_mix("Inspection burden", process_route_summary.get("inspection_burden_counts", {})))
    lines.extend(_markdown_table_from_mix("Repairability", process_route_summary.get("repairability_level_counts", {})))
    lines.extend(_markdown_table_from_mix("Qualification burden", process_route_summary.get("qualification_burden_counts", {})))
    high_inspection = process_route_summary.get("high_inspection_burden_candidate_ids", [])
    limited_repair = process_route_summary.get("limited_or_poor_repairability_candidate_ids", [])
    high_qualification = process_route_summary.get("high_or_very_high_qualification_burden_candidate_ids", [])
    if high_inspection:
        lines.append("- High inspection burden visible for: " + ", ".join(high_inspection))
    if limited_repair:
        lines.append("- Limited or poor repairability visible for: " + ", ".join(limited_repair))
    if high_qualification:
        lines.append("- High or very high qualification burden visible for: " + ", ".join(high_qualification))
    for card in view_model["candidate_cards"]:
        lines.extend(
            [
                f"### Route: {card['candidate_id']}",
                f"- Route: {card['process_route_display_name']}",
                f"- Process family: {card['process_family']}",
                f"- Process chain: {card['process_chain_summary'] or 'not specified'}",
                f"- Inspection burden: {card['inspection_burden']}",
                f"- Inspection methods: {', '.join(card['inspection_methods']) or 'not specified'}",
                f"- Repairability: {card['repairability_level']} - {card['repair_concept']}",
                f"- Qualification burden: {card['qualification_burden']}",
                f"- Route risks: {', '.join(card['route_risks'][:3]) or 'none visible'}",
                f"- Validation gaps: {', '.join(card['route_validation_gaps'][:3]) or 'none visible'}",
            ]
        )
    optimisation = view_model["optimisation_summary_view"]
    comparison = view_model["coating_vs_gradient_comparison_view"]
    diagnostic = view_model["coating_vs_gradient_diagnostic_view"]
    lines.extend(
        [
            "",
            "## Deterministic Optimisation Skeleton",
            "- Deterministic optimisation is a skeleton.",
            "- No variants generated.",
            "- No final ranking was produced.",
            "- No Pareto optimisation was performed.",
            "- No live model calls were made.",
            "- Suggestions only — not applied.",
            f"- Status: {optimisation.get('status')}",
            f"- Full limiting-factor count: {optimisation.get('full_limiting_factor_count')}",
            f"- Displayed limiting-factor count: {optimisation.get('displayed_limiting_factor_count')}",
            f"- Hard limits: {optimisation.get('total_hard_limit_count')}",
            f"- Advisory warnings: {optimisation.get('total_advisory_warning_count')}",
            f"- Evidence maturity constraints: {optimisation.get('total_evidence_maturity_limit_count')}",
            f"- Route/interface risks: {optimisation.get('total_route_risk_count')}",
            f"- Certification constraints: {optimisation.get('total_certification_limit_count')}",
            f"- Average limiting factors per candidate: {optimisation.get('average_limiting_factors_per_candidate')}",
            f"- Total refinement option count: {optimisation.get('total_refinement_option_count')}",
            f"- Generated candidate count: {optimisation.get('generated_candidate_count')}",
            "",
            "## Coating vs Gradient Comparison",
            f"- Comparison required: {comparison.get('comparison_required')}",
            "- Coating-enabled candidate IDs: "
            + (", ".join(comparison.get("coating_enabled_candidate_ids", [])) or "none visible"),
            "- Spatial-gradient candidate IDs: "
            + (", ".join(comparison.get("spatial_gradient_candidate_ids", [])) or "none visible"),
            "- Shared limiting-factor themes: "
            + (", ".join(comparison.get("shared_limiting_factor_themes", [])) or "none visible"),
        ]
    )
    for note in comparison.get("comparison_notes", [])[:4]:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Coating vs Gradient Diagnostic",
            f"- Diagnostic status: {diagnostic.get('diagnostic_status')}",
            f"- Comparison required: {diagnostic.get('comparison_required')}",
            "- Coating-enabled candidate IDs: "
            + (", ".join(diagnostic.get("coating_enabled_candidate_ids", [])) or "none visible"),
            "- Spatial-gradient candidate IDs: "
            + (", ".join(diagnostic.get("spatial_gradient_candidate_ids", [])) or "none visible"),
            "- Shared surface-function themes: "
            + (", ".join(diagnostic.get("shared_surface_function_themes", [])) or "none visible"),
            "- Common coating strengths: "
            + (", ".join(diagnostic.get("coating_common_strengths", [])[:5]) or "none visible"),
            "- Common gradient strengths: "
            + (", ".join(diagnostic.get("gradient_common_strengths", [])[:5]) or "none visible"),
            "- Common coating risks: "
            + (", ".join(diagnostic.get("coating_common_risks", [])[:5]) or "none visible"),
            "- Common gradient risks: "
            + (", ".join(diagnostic.get("gradient_common_risks", [])[:5]) or "none visible"),
            f"- Evidence maturity observations: {diagnostic.get('evidence_maturity_observations')}",
            f"- Inspection / repairability observations: {diagnostic.get('inspection_repair_observations')}",
            f"- Qualification observations: {diagnostic.get('qualification_observations')}",
            f"- Validation gap observations: {diagnostic.get('validation_gap_observations')}",
        ]
    )
    for note in diagnostic.get("summary_notes", [])[:4]:
        lines.append(f"- {note}")
    for pairwise in diagnostic.get("pairwise_comparisons", [])[:12]:
        lines.extend(
            [
                f"### Diagnostic Pair: {pairwise.get('coating_candidate_id')} vs {pairwise.get('gradient_candidate_id')}",
                "- Shared surface functions: "
                + (", ".join(_as_list(pairwise.get("shared_surface_functions"))) or "none visible"),
                "- Coating-only surface functions: "
                + (", ".join(_as_list(pairwise.get("coating_only_surface_functions"))) or "none visible"),
                "- Gradient-only surface functions: "
                + (", ".join(_as_list(pairwise.get("gradient_only_surface_functions"))) or "none visible"),
                f"- Functional overlap: {pairwise.get('functional_overlap_status')}",
                f"- {pairwise.get('evidence_maturity_contrast')}",
                f"- {pairwise.get('inspection_contrast')}",
                f"- {pairwise.get('repairability_contrast')}",
                f"- {pairwise.get('qualification_contrast')}",
                f"- {pairwise.get('interface_contrast')}",
                f"- {pairwise.get('process_route_contrast')}",
                f"- {pairwise.get('validation_gap_contrast')}",
                "- Diagnostic notes: "
                + ("; ".join(_as_list(pairwise.get("diagnostic_notes"))) or "none"),
                "- No winner selected",
            ]
        )
    lines.extend(["", "## Limiting Factors and Refinement Options"])
    lines.append("- Suggestions only — not applied.")
    for trace_card in view_model["optimisation_trace_cards"]:
        lines.extend(
            [
                f"### {trace_card['candidate_id']}",
                f"- Class: {trace_card['candidate_class']}",
                f"- Evidence maturity: {trace_card['evidence_maturity']}",
                f"- Trace status: {trace_card['status']}",
                f"- Full limiting factors: {trace_card['limiting_factor_count']}",
                f"- Displayed limiting factors: {trace_card['displayed_limiting_factor_count']}",
                f"- Hard limits: {trace_card['hard_limit_count']}",
                f"- Advisory warnings: {trace_card['advisory_warning_count']}",
                f"- Evidence maturity constraints: {trace_card['evidence_maturity_limit_count']}",
                f"- Refinement options: {trace_card['displayed_refinement_option_count']} displayed of {trace_card['refinement_option_count']}",
            ]
        )
        for factor in trace_card["top_limiting_factors"]:
            lines.append(
                "- Top limiting factor: "
                f"{factor['factor']} ({factor['severity']}, {factor['category']}) - {factor['reason']}"
            )
        for option in trace_card["top_refinement_options"]:
            lines.append(
                "- Top refinement option: "
                f"{option['operator_type']} ({option['status']}) - {option['description']}"
            )
    if not view_model["optimisation_trace_cards"]:
        lines.append("- none")
    lines.extend(["", "## Candidate Cards"])
    for card in view_model["candidate_cards"]:
        lines.extend(
            [
                f"### {card['system_name']}",
                f"- Candidate ID: {card['candidate_id']}",
                f"- Class: {card['candidate_class']}",
                f"- Architecture: {card['system_architecture_type']}",
                f"- Evidence: {card['evidence_maturity']} ({card['evidence_label']})",
                f"- Coating/surface: {card['coating_or_surface_summary'].get('summary', '') or 'not specified'}",
                f"- Gradient: {card['gradient_summary'].get('summary', '') or 'not specified'}",
                f"- Primary surface functions: {', '.join(card['primary_surface_functions']) or 'unknown'}",
                f"- Secondary surface functions: {', '.join(card['secondary_surface_functions']) or 'none visible'}",
                f"- Decision readiness: {card['readiness_label']} ({card['readiness_status']})",
                f"- Narrative role: {card['narrative_role']}",
                f"- Responsible use: {card['responsible_use'] or 'not specified'}",
                f"- Interfaces: {', '.join(card['interface_summary'].get('interface_types', [])) or 'none visible'}",
            ]
        )
    lines.extend(["", "## Warnings And Deferred Capabilities"])
    warnings = view_model["warnings"]
    lines.extend([f"- {warning}" for warning in warnings] or ["- none"])
    lines.extend([f"- {item}" for item in view_model["deferred_capabilities"]])
    return "\n".join(lines) + "\n"


def package_to_json_safe_dict(package: Mapping[str, Any]) -> dict[str, Any]:
    def convert(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(key): convert(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [convert(item) for item in value]
        if isinstance(value, set):
            return [convert(item) for item in sorted(value, key=str)]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    return convert(dict(package))
