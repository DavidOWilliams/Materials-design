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


def _summarize_coating_spallation(candidate: Mapping[str, Any]) -> dict[str, Any]:
    profile = _mapping(candidate.get("coating_spallation_adhesion"))
    if not profile:
        return {"present": False}
    return {
        "present": True,
        "coating_system_label": _text(profile.get("coating_system_label"), "Unknown coating system"),
        "coating_system_kind": _text(profile.get("coating_system_kind"), "unknown"),
        "bond_coat_or_interface_dependency": _text(
            profile.get("bond_coat_or_interface_dependency"),
            "unknown",
        ),
        "adhesion_or_spallation_risk": _text(profile.get("adhesion_or_spallation_risk"), "unknown"),
        "cte_mismatch_risk": _text(profile.get("cte_mismatch_risk"), "unknown"),
        "thermal_cycling_damage_risk": _text(profile.get("thermal_cycling_damage_risk"), "unknown"),
        "environmental_attack_risk": _text(profile.get("environmental_attack_risk"), "unknown"),
        "inspection_difficulty": _text(profile.get("inspection_difficulty"), "unknown"),
        "repairability_constraint": _text(profile.get("repairability_constraint"), "unknown"),
        "required_validation_evidence": [
            _text(item) for item in _as_list(profile.get("required_validation_evidence")) if _text(item)
        ],
        "inspection_and_repair_notes": [
            _text(item) for item in _as_list(profile.get("inspection_and_repair_notes")) if _text(item)
        ],
        "coating_concerns": [_text(item) for item in _as_list(profile.get("coating_concerns")) if _text(item)],
        "not_a_life_prediction": profile.get("not_a_life_prediction") is True,
        "not_a_qualification_claim": profile.get("not_a_qualification_claim") is True,
    }


def _summarize_graded_am_transition(candidate: Mapping[str, Any]) -> dict[str, Any]:
    profile = _mapping(candidate.get("graded_am_transition_zone_risk"))
    if not profile:
        return {"present": False}
    return {
        "present": True,
        "gradient_system_label": _text(profile.get("gradient_system_label"), "Unknown gradient system"),
        "gradient_system_kind": _text(profile.get("gradient_system_kind"), "unknown"),
        "transition_zone_complexity": _text(profile.get("transition_zone_complexity"), "unknown"),
        "residual_stress_risk": _text(profile.get("residual_stress_risk"), "unknown"),
        "cracking_or_delamination_risk": _text(profile.get("cracking_or_delamination_risk"), "unknown"),
        "process_window_sensitivity": _text(profile.get("process_window_sensitivity"), "unknown"),
        "through_depth_inspection_difficulty": _text(
            profile.get("through_depth_inspection_difficulty"),
            "unknown",
        ),
        "repairability_constraint": _text(profile.get("repairability_constraint"), "unknown"),
        "qualification_burden": _text(profile.get("qualification_burden"), "unknown"),
        "required_validation_evidence": [
            _text(item) for item in _as_list(profile.get("required_validation_evidence")) if _text(item)
        ],
        "inspection_and_repair_notes": [
            _text(item) for item in _as_list(profile.get("inspection_and_repair_notes")) if _text(item)
        ],
        "gradient_concerns": [_text(item) for item in _as_list(profile.get("gradient_concerns")) if _text(item)],
        "not_a_process_qualification_claim": profile.get("not_a_process_qualification_claim") is True,
        "not_a_life_prediction": profile.get("not_a_life_prediction") is True,
        "not_a_final_recommendation": profile.get("not_a_final_recommendation") is True,
    }


def _summarize_application_fit(candidate: Mapping[str, Any]) -> dict[str, Any]:
    fit = _mapping(candidate.get("application_requirement_fit"))
    if not fit:
        return {"present": False}
    return {
        "present": True,
        "fit_status": _text(fit.get("fit_status"), "unknown"),
        "matched_required_primary_functions": [
            _text(item) for item in _as_list(fit.get("matched_required_primary_functions")) if _text(item)
        ],
        "missing_required_primary_functions": [
            _text(item) for item in _as_list(fit.get("missing_required_primary_functions")) if _text(item)
        ],
        "major_cautions": [_text(item) for item in _as_list(fit.get("major_cautions")) if _text(item)],
        "critical_blockers": [_text(item) for item in _as_list(fit.get("critical_blockers")) if _text(item)],
        "required_next_evidence": [
            _text(item) for item in _as_list(fit.get("required_next_evidence")) if _text(item)
        ],
    }


def build_candidate_card_view_model(candidate: Mapping[str, Any]) -> dict[str, Any]:
    maturity = _evidence_maturity(candidate)
    evidence = _evidence(candidate)
    process_route = _summarize_process_route(candidate)
    surface_profile = _mapping(candidate.get("surface_function_profile"))
    readiness = _mapping(candidate.get("decision_readiness"))
    narrative_card = _mapping(candidate.get("recommendation_narrative_card"))
    coating_spallation = _summarize_coating_spallation(candidate)
    graded_am_transition = _summarize_graded_am_transition(candidate)
    application_fit = _summarize_application_fit(candidate)
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
        "coating_spallation_adhesion": coating_spallation,
        "coating_system_label": coating_spallation.get("coating_system_label", ""),
        "bond_coat_or_interface_dependency": coating_spallation.get("bond_coat_or_interface_dependency", ""),
        "adhesion_or_spallation_risk": coating_spallation.get("adhesion_or_spallation_risk", ""),
        "cte_mismatch_risk": coating_spallation.get("cte_mismatch_risk", ""),
        "thermal_cycling_damage_risk": coating_spallation.get("thermal_cycling_damage_risk", ""),
        "environmental_attack_risk": coating_spallation.get("environmental_attack_risk", ""),
        "inspection_difficulty": coating_spallation.get("inspection_difficulty", ""),
        "repairability_constraint": coating_spallation.get("repairability_constraint", ""),
        "coating_required_validation_evidence": coating_spallation.get("required_validation_evidence", []),
        "graded_am_transition_zone_risk": graded_am_transition,
        "gradient_system_label": graded_am_transition.get("gradient_system_label", ""),
        "transition_zone_complexity": graded_am_transition.get("transition_zone_complexity", ""),
        "residual_stress_risk": graded_am_transition.get("residual_stress_risk", ""),
        "cracking_or_delamination_risk": graded_am_transition.get("cracking_or_delamination_risk", ""),
        "process_window_sensitivity": graded_am_transition.get("process_window_sensitivity", ""),
        "through_depth_inspection_difficulty": graded_am_transition.get("through_depth_inspection_difficulty", ""),
        "gradient_repairability_constraint": graded_am_transition.get("repairability_constraint", ""),
        "gradient_qualification_burden": graded_am_transition.get("qualification_burden", ""),
        "graded_am_required_validation_evidence": graded_am_transition.get("required_validation_evidence", []),
        "application_requirement_fit": application_fit,
        "application_fit_status": application_fit.get("fit_status", ""),
        "application_matched_required_primary_functions": application_fit.get(
            "matched_required_primary_functions",
            [],
        ),
        "application_missing_required_primary_functions": application_fit.get(
            "missing_required_primary_functions",
            [],
        ),
        "application_major_cautions": application_fit.get("major_cautions", []),
        "application_required_next_evidence": application_fit.get("required_next_evidence", []),
        "primary_surface_functions": [
            _text(item) for item in _as_list(surface_profile.get("primary_surface_functions")) if _text(item)
        ],
        "secondary_surface_functions": [
            _text(item) for item in _as_list(surface_profile.get("secondary_surface_functions")) if _text(item)
        ],
        "primary_service_functions": [
            _text(item) for item in _as_list(surface_profile.get("primary_service_functions")) if _text(item)
        ],
        "secondary_service_functions": [
            _text(item) for item in _as_list(surface_profile.get("secondary_service_functions")) if _text(item)
        ],
        "support_or_lifecycle_considerations": [
            _text(item)
            for item in _as_list(surface_profile.get("support_or_lifecycle_considerations"))
            if _text(item)
        ],
        "risk_or_interface_considerations": [
            _text(item)
            for item in _as_list(surface_profile.get("risk_or_interface_considerations"))
            if _text(item)
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
        "coating_spallation_adhesion_summary": dict(
            _mapping(package.get("coating_spallation_adhesion_summary"))
        ),
        "graded_am_transition_zone_summary": dict(_mapping(package.get("graded_am_transition_zone_summary"))),
        "application_requirement_fit": dict(_mapping(package.get("application_requirement_fit"))),
        "application_profile": dict(_mapping(package.get("application_profile"))),
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
        "shared_primary_service_functions": [
            _text(item) for item in _as_list(diagnostic.get("shared_primary_service_functions")) if _text(item)
        ],
        "shared_support_considerations": [
            _text(item) for item in _as_list(diagnostic.get("shared_support_considerations")) if _text(item)
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


def build_coating_spallation_adhesion_summary_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(package.get("coating_spallation_adhesion_summary"))
    return {
        "candidate_count": summary.get("candidate_count", 0),
        "relevant_candidate_count": summary.get("relevant_candidate_count", 0),
        "coating_system_kind_counts": dict(_mapping(summary.get("coating_system_kind_counts"))),
        "bond_coat_or_interface_dependency_counts": dict(
            _mapping(summary.get("bond_coat_or_interface_dependency_counts"))
        ),
        "adhesion_or_spallation_risk_counts": dict(_mapping(summary.get("adhesion_or_spallation_risk_counts"))),
        "cte_mismatch_risk_counts": dict(_mapping(summary.get("cte_mismatch_risk_counts"))),
        "thermal_cycling_damage_risk_counts": dict(_mapping(summary.get("thermal_cycling_damage_risk_counts"))),
        "environmental_attack_risk_counts": dict(_mapping(summary.get("environmental_attack_risk_counts"))),
        "inspection_difficulty_counts": dict(_mapping(summary.get("inspection_difficulty_counts"))),
        "repairability_constraint_counts": dict(_mapping(summary.get("repairability_constraint_counts"))),
        "qualification_burden_counts": dict(_mapping(summary.get("qualification_burden_counts"))),
        "high_spallation_risk_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_spallation_risk_candidate_ids")) if _text(item)
        ],
        "high_interface_dependency_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_interface_dependency_candidate_ids")) if _text(item)
        ],
        "high_inspection_difficulty_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_inspection_difficulty_candidate_ids")) if _text(item)
        ],
        "high_repairability_constraint_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_repairability_constraint_candidate_ids")) if _text(item)
        ],
        "high_qualification_burden_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_qualification_burden_candidate_ids")) if _text(item)
        ],
        "low_maturity_relevant_candidate_ids": [
            _text(item) for item in _as_list(summary.get("low_maturity_relevant_candidate_ids")) if _text(item)
        ],
        "required_validation_evidence_themes": [
            _text(item) for item in _as_list(summary.get("required_validation_evidence_themes")) if _text(item)
        ],
        "warnings": [_text(item) for item in _as_list(summary.get("warnings")) if _text(item)],
    }


def build_graded_am_transition_zone_summary_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(package.get("graded_am_transition_zone_summary"))
    return {
        "candidate_count": summary.get("candidate_count", 0),
        "relevant_candidate_count": summary.get("relevant_candidate_count", 0),
        "gradient_system_kind_counts": dict(_mapping(summary.get("gradient_system_kind_counts"))),
        "transition_zone_complexity_counts": dict(_mapping(summary.get("transition_zone_complexity_counts"))),
        "residual_stress_risk_counts": dict(_mapping(summary.get("residual_stress_risk_counts"))),
        "cracking_or_delamination_risk_counts": dict(
            _mapping(summary.get("cracking_or_delamination_risk_counts"))
        ),
        "process_window_sensitivity_counts": dict(_mapping(summary.get("process_window_sensitivity_counts"))),
        "through_depth_inspection_difficulty_counts": dict(
            _mapping(summary.get("through_depth_inspection_difficulty_counts"))
        ),
        "repairability_constraint_counts": dict(_mapping(summary.get("repairability_constraint_counts"))),
        "qualification_burden_counts": dict(_mapping(summary.get("qualification_burden_counts"))),
        "maturity_constraint_counts": dict(_mapping(summary.get("maturity_constraint_counts"))),
        "high_transition_complexity_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_transition_complexity_candidate_ids")) if _text(item)
        ],
        "high_residual_stress_risk_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_residual_stress_risk_candidate_ids")) if _text(item)
        ],
        "high_cracking_or_delamination_risk_candidate_ids": [
            _text(item)
            for item in _as_list(summary.get("high_cracking_or_delamination_risk_candidate_ids"))
            if _text(item)
        ],
        "high_process_window_sensitivity_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_process_window_sensitivity_candidate_ids")) if _text(item)
        ],
        "high_inspection_difficulty_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_inspection_difficulty_candidate_ids")) if _text(item)
        ],
        "high_repairability_constraint_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_repairability_constraint_candidate_ids")) if _text(item)
        ],
        "high_qualification_burden_candidate_ids": [
            _text(item) for item in _as_list(summary.get("high_qualification_burden_candidate_ids")) if _text(item)
        ],
        "low_maturity_gradient_candidate_ids": [
            _text(item) for item in _as_list(summary.get("low_maturity_gradient_candidate_ids")) if _text(item)
        ],
        "required_validation_evidence_themes": [
            _text(item) for item in _as_list(summary.get("required_validation_evidence_themes")) if _text(item)
        ],
        "warnings": [_text(item) for item in _as_list(summary.get("warnings")) if _text(item)],
    }


def build_application_requirement_fit_view_model(package: Mapping[str, Any]) -> dict[str, Any]:
    matrix = _mapping(package.get("application_requirement_fit"))
    profile = _mapping(package.get("application_profile") or matrix.get("profile"))
    coverage = _mapping(matrix.get("required_function_coverage_summary"))
    return {
        "profile": dict(profile),
        "profile_id": _text(profile.get("profile_id"), "unknown_profile"),
        "display_name": _text(profile.get("display_name"), "Unknown application profile"),
        "description": _text(profile.get("description")),
        "required_primary_service_functions": [
            _text(item) for item in _as_list(profile.get("required_primary_service_functions")) if _text(item)
        ],
        "desired_secondary_service_functions": [
            _text(item) for item in _as_list(profile.get("desired_secondary_service_functions")) if _text(item)
        ],
        "key_profile_constraints": {
            "thermal_exposure_level": _text(profile.get("thermal_exposure_level"), "unknown"),
            "thermal_cycling_severity": _text(profile.get("thermal_cycling_severity"), "unknown"),
            "oxidation_or_steam_exposure": _text(profile.get("oxidation_or_steam_exposure"), "unknown"),
            "erosion_or_wear_exposure": _text(profile.get("erosion_or_wear_exposure"), "unknown"),
            "inspection_access": _text(profile.get("inspection_access"), "unknown"),
            "repairability_expectation": _text(profile.get("repairability_expectation"), "unknown"),
            "certification_sensitivity": _text(profile.get("certification_sensitivity"), "unknown"),
            "minimum_evidence_maturity_for_engineering_use": _text(
                profile.get("minimum_evidence_maturity_for_engineering_use"),
                "unknown",
            ),
        },
        "candidate_count": matrix.get("candidate_count", 0),
        "fit_status_counts": dict(_mapping(matrix.get("fit_status_counts"))),
        "candidate_ids_by_fit_status": {
            key: [_text(item) for item in _as_list(value) if _text(item)]
            for key, value in _mapping(matrix.get("candidate_ids_by_fit_status")).items()
        },
        "required_function_coverage_summary": dict(coverage),
        "common_blockers": [_text(item) for item in _as_list(matrix.get("common_blockers")) if _text(item)],
        "common_major_cautions": [
            _text(item) for item in _as_list(matrix.get("common_major_cautions")) if _text(item)
        ],
        "required_next_evidence_themes": [
            _text(item) for item in _as_list(matrix.get("required_next_evidence_themes")) if _text(item)
        ],
        "practical_use_summary": [
            _text(item) for item in _as_list(matrix.get("practical_use_summary")) if _text(item)
        ],
        "fit_records": [
            dict(item) for item in _as_list(matrix.get("fit_records")) if isinstance(item, Mapping)
        ],
        "warnings": [_text(item) for item in _as_list(matrix.get("warnings")) if _text(item)],
        "not_a_final_recommendation": matrix.get("not_a_final_recommendation") is True,
        "no_ranking_applied": matrix.get("no_ranking_applied") is True,
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
        "primary_service_function_to_candidate_ids": dict(
            _mapping(summary.get("primary_service_function_to_candidate_ids"))
        ),
        "secondary_service_function_to_candidate_ids": dict(
            _mapping(summary.get("secondary_service_function_to_candidate_ids"))
        ),
        "support_consideration_to_candidate_ids": dict(
            _mapping(summary.get("support_consideration_to_candidate_ids"))
        ),
        "risk_consideration_to_candidate_ids": dict(
            _mapping(summary.get("risk_consideration_to_candidate_ids"))
        ),
        "candidate_to_function_ids": dict(_mapping(summary.get("candidate_to_function_ids"))),
        "coating_enabled_function_counts": dict(_mapping(summary.get("coating_enabled_function_counts"))),
        "spatial_gradient_function_counts": dict(_mapping(summary.get("spatial_gradient_function_counts"))),
        "shared_coating_gradient_functions": [
            _text(item) for item in _as_list(summary.get("shared_coating_gradient_functions")) if _text(item)
        ],
        "shared_coating_gradient_primary_service_functions": [
            _text(item)
            for item in _as_list(summary.get("shared_coating_gradient_primary_service_functions"))
            if _text(item)
        ],
        "shared_coating_gradient_support_considerations": [
            _text(item)
            for item in _as_list(summary.get("shared_coating_gradient_support_considerations"))
            if _text(item)
        ],
        "functions_only_seen_in_coatings": [
            _text(item) for item in _as_list(summary.get("functions_only_seen_in_coatings")) if _text(item)
        ],
        "functions_only_seen_in_gradients": [
            _text(item) for item in _as_list(summary.get("functions_only_seen_in_gradients")) if _text(item)
        ],
        "functions_only_seen_in_coatings_primary": [
            _text(item) for item in _as_list(summary.get("functions_only_seen_in_coatings_primary")) if _text(item)
        ],
        "functions_only_seen_in_gradients_primary": [
            _text(item) for item in _as_list(summary.get("functions_only_seen_in_gradients_primary")) if _text(item)
        ],
        "coverage_caveats": [_text(item) for item in _as_list(summary.get("coverage_caveats")) if _text(item)],
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
        "covered_required_primary_service_function_ids": [
            _text(item)
            for item in _as_list(required_coverage.get("covered_required_primary_service_function_ids"))
            if _text(item)
        ],
        "uncovered_required_primary_service_function_ids": [
            _text(item)
            for item in _as_list(required_coverage.get("uncovered_required_primary_service_function_ids"))
            if _text(item)
        ],
        "covered_required_support_consideration_ids": [
            _text(item)
            for item in _as_list(required_coverage.get("covered_required_support_consideration_ids"))
            if _text(item)
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
        "coating_spallation_adhesion_summary_view": build_coating_spallation_adhesion_summary_view_model(package),
        "graded_am_transition_zone_summary_view": build_graded_am_transition_zone_summary_view_model(package),
        "application_requirement_fit_view": build_application_requirement_fit_view_model(package),
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
    required_primary_labels = [
        _text(item.get("function_id"))
        for item in surface_view.get("required_surface_functions", [])
        if isinstance(item, Mapping)
        and _text(item.get("function_kind")) == "primary_service_function"
    ]
    lines.extend(
        [
            "",
            "## Surface Function Coverage",
            "- Required surface functions: " + (", ".join(required_labels) or "none inferred"),
            "- Required primary service functions: " + (", ".join(required_primary_labels) or "none inferred"),
            "- Covered required functions: "
            + (", ".join(surface_view.get("covered_required_function_ids", [])) or "none visible"),
            "- Uncovered required functions: "
            + (", ".join(surface_view.get("uncovered_required_function_ids", [])) or "none"),
            "- Covered required primary service functions: "
            + (", ".join(surface_view.get("covered_required_primary_service_function_ids", [])) or "none visible"),
            "- Uncovered required primary service functions: "
            + (", ".join(surface_view.get("uncovered_required_primary_service_function_ids", [])) or "none"),
            "- Covered required support / lifecycle considerations: "
            + (", ".join(surface_view.get("covered_required_support_consideration_ids", [])) or "none visible"),
        ]
    )
    lines.extend(_markdown_table_from_mix("Function-to-candidate coverage", surface_view.get("function_to_candidate_ids", {})))
    lines.extend(
        _markdown_table_from_mix(
            "Primary service function coverage",
            surface_view.get("primary_service_function_to_candidate_ids", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Secondary service function coverage",
            surface_view.get("secondary_service_function_to_candidate_ids", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Support / lifecycle considerations",
            surface_view.get("support_consideration_to_candidate_ids", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Risk / interface considerations",
            surface_view.get("risk_consideration_to_candidate_ids", {}),
        )
    )
    lines.extend(_markdown_table_from_mix("Coating-enabled function coverage", surface_view.get("coating_enabled_function_counts", {})))
    lines.extend(_markdown_table_from_mix("Spatial-gradient function coverage", surface_view.get("spatial_gradient_function_counts", {})))
    lines.extend(
        [
            "- Shared coating/gradient functions: "
            + (", ".join(surface_view.get("shared_coating_gradient_functions", [])) or "none visible"),
            "- Shared coating/gradient primary service functions: "
            + (
                ", ".join(surface_view.get("shared_coating_gradient_primary_service_functions", []))
                or "none visible"
            ),
            "- Shared coating/gradient support considerations: "
            + (
                ", ".join(surface_view.get("shared_coating_gradient_support_considerations", []))
                or "none visible"
            ),
            "- Functions only seen in coatings: "
            + (", ".join(surface_view.get("functions_only_seen_in_coatings", [])) or "none visible"),
            "- Functions only seen in gradients: "
            + (", ".join(surface_view.get("functions_only_seen_in_gradients", [])) or "none visible"),
            "- Primary functions only seen in coatings: "
            + (", ".join(surface_view.get("functions_only_seen_in_coatings_primary", [])) or "none visible"),
            "- Primary functions only seen in gradients: "
            + (", ".join(surface_view.get("functions_only_seen_in_gradients_primary", [])) or "none visible"),
            "- Candidates with unknown surface function: "
            + (", ".join(surface_view.get("unknown_surface_function_candidate_ids", [])) or "none"),
        ]
    )
    for caveat in surface_view.get("coverage_caveats", [])[:4]:
        lines.append(f"- Coverage caveat: {caveat}")
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
    coating_spallation_view = view_model["coating_spallation_adhesion_summary_view"]
    lines.extend(
        [
            "",
            "## Coating Spallation, Adhesion and Repair",
            "- Diagnostic only.",
            "- This is not a life prediction.",
            "- This is not qualification/certification approval.",
            f"- Relevant coating candidate count: {coating_spallation_view.get('relevant_candidate_count')}",
        ]
    )
    lines.extend(
        _markdown_table_from_mix(
            "Coating system kinds",
            coating_spallation_view.get("coating_system_kind_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Bond coat / interface dependency",
            coating_spallation_view.get("bond_coat_or_interface_dependency_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Adhesion / spallation risk",
            coating_spallation_view.get("adhesion_or_spallation_risk_counts", {}),
        )
    )
    lines.extend(_markdown_table_from_mix("CTE mismatch risk", coating_spallation_view.get("cte_mismatch_risk_counts", {})))
    lines.extend(
        _markdown_table_from_mix(
            "Thermal cycling damage risk",
            coating_spallation_view.get("thermal_cycling_damage_risk_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Environmental attack risk",
            coating_spallation_view.get("environmental_attack_risk_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Inspection difficulty",
            coating_spallation_view.get("inspection_difficulty_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Repairability constraint",
            coating_spallation_view.get("repairability_constraint_counts", {}),
        )
    )
    lines.extend(
        [
            "- High adhesion/spallation risk candidates: "
            + (", ".join(coating_spallation_view.get("high_spallation_risk_candidate_ids", [])) or "none"),
            "- High interface dependency candidates: "
            + (", ".join(coating_spallation_view.get("high_interface_dependency_candidate_ids", [])) or "none"),
            "- High inspection difficulty candidates: "
            + (", ".join(coating_spallation_view.get("high_inspection_difficulty_candidate_ids", [])) or "none"),
            "- High repairability constraint candidates: "
            + (", ".join(coating_spallation_view.get("high_repairability_constraint_candidate_ids", [])) or "none"),
            "- High qualification burden candidates: "
            + (", ".join(coating_spallation_view.get("high_qualification_burden_candidate_ids", [])) or "none"),
            "- Low maturity coating-relevant candidates: "
            + (", ".join(coating_spallation_view.get("low_maturity_relevant_candidate_ids", [])) or "none"),
            "- Required validation evidence themes: "
            + (", ".join(coating_spallation_view.get("required_validation_evidence_themes", [])[:10]) or "none visible"),
        ]
    )
    for card in view_model["candidate_cards"]:
        profile = card.get("coating_spallation_adhesion") or {}
        if not profile.get("present"):
            continue
        lines.extend(
            [
                f"### Coating Diagnostic: {card['candidate_id']}",
                f"- Coating system: {card['coating_system_label']}",
                f"- Bond coat/interface dependency: {card['bond_coat_or_interface_dependency']}",
                f"- Adhesion/spallation risk: {card['adhesion_or_spallation_risk']}",
                f"- CTE mismatch risk: {card['cte_mismatch_risk']}",
                f"- Thermal cycling damage risk: {card['thermal_cycling_damage_risk']}",
                f"- Environmental attack risk: {card['environmental_attack_risk']}",
                f"- Inspection difficulty: {card['inspection_difficulty']}",
                f"- Repairability constraint: {card['repairability_constraint']}",
                "- Required validation evidence: "
                + (", ".join(card["coating_required_validation_evidence"][:5]) or "not specified"),
            ]
        )
    graded_am_view = view_model["graded_am_transition_zone_summary_view"]
    lines.extend(
        [
            "",
            "## Graded AM Transition-Zone Risk",
            "- Diagnostic only.",
            "- This is not a process qualification claim.",
            "- This is not a life prediction.",
            "- This is not qualification/certification approval.",
            f"- Relevant graded AM candidate count: {graded_am_view.get('relevant_candidate_count')}",
        ]
    )
    lines.extend(_markdown_table_from_mix("Gradient system kinds", graded_am_view.get("gradient_system_kind_counts", {})))
    lines.extend(
        _markdown_table_from_mix(
            "Transition-zone complexity",
            graded_am_view.get("transition_zone_complexity_counts", {}),
        )
    )
    lines.extend(_markdown_table_from_mix("Residual-stress risk", graded_am_view.get("residual_stress_risk_counts", {})))
    lines.extend(
        _markdown_table_from_mix(
            "Cracking / delamination risk",
            graded_am_view.get("cracking_or_delamination_risk_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Process-window sensitivity",
            graded_am_view.get("process_window_sensitivity_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Through-depth inspection difficulty",
            graded_am_view.get("through_depth_inspection_difficulty_counts", {}),
        )
    )
    lines.extend(
        _markdown_table_from_mix(
            "Repairability constraint",
            graded_am_view.get("repairability_constraint_counts", {}),
        )
    )
    lines.extend(
        [
            "- High transition-zone complexity candidates: "
            + (", ".join(graded_am_view.get("high_transition_complexity_candidate_ids", [])) or "none"),
            "- High residual-stress risk candidates: "
            + (", ".join(graded_am_view.get("high_residual_stress_risk_candidate_ids", [])) or "none"),
            "- High cracking/delamination risk candidates: "
            + (", ".join(graded_am_view.get("high_cracking_or_delamination_risk_candidate_ids", [])) or "none"),
            "- High process-window sensitivity candidates: "
            + (", ".join(graded_am_view.get("high_process_window_sensitivity_candidate_ids", [])) or "none"),
            "- High through-depth inspection difficulty candidates: "
            + (", ".join(graded_am_view.get("high_inspection_difficulty_candidate_ids", [])) or "none"),
            "- High repairability constraint candidates: "
            + (", ".join(graded_am_view.get("high_repairability_constraint_candidate_ids", [])) or "none"),
            "- High qualification burden candidates: "
            + (", ".join(graded_am_view.get("high_qualification_burden_candidate_ids", [])) or "none"),
            "- Low maturity gradient candidates: "
            + (", ".join(graded_am_view.get("low_maturity_gradient_candidate_ids", [])) or "none"),
            "- Required validation evidence themes: "
            + (", ".join(graded_am_view.get("required_validation_evidence_themes", [])[:10]) or "none visible"),
        ]
    )
    for card in view_model["candidate_cards"]:
        profile = card.get("graded_am_transition_zone_risk") or {}
        if not profile.get("present"):
            continue
        lines.extend(
            [
                f"### Graded AM Diagnostic: {card['candidate_id']}",
                f"- Gradient system: {card['gradient_system_label']}",
                f"- Transition-zone complexity: {card['transition_zone_complexity']}",
                f"- Residual-stress risk: {card['residual_stress_risk']}",
                f"- Cracking/delamination risk: {card['cracking_or_delamination_risk']}",
                f"- Process-window sensitivity: {card['process_window_sensitivity']}",
                f"- Through-depth inspection difficulty: {card['through_depth_inspection_difficulty']}",
                f"- Repairability constraint: {card['gradient_repairability_constraint']}",
                f"- Qualification burden: {card['gradient_qualification_burden']}",
                "- Required validation evidence: "
                + (", ".join(card["graded_am_required_validation_evidence"][:5]) or "not specified"),
            ]
        )
    app_fit = view_model["application_requirement_fit_view"]
    coverage = _mapping(app_fit.get("required_function_coverage_summary"))
    constraints = _mapping(app_fit.get("key_profile_constraints"))
    lines.extend(
        [
            "",
            "## Application Requirement Fit",
            "- This is not final material selection.",
            "- No ranking has been applied.",
            "- Fit status is a conservative decision-support classification only.",
            f"- Selected application profile: {app_fit.get('display_name')} ({app_fit.get('profile_id')})",
            f"- Profile description: {app_fit.get('description') or 'not specified'}",
            "- Required primary service functions: "
            + (", ".join(app_fit.get("required_primary_service_functions", [])) or "none specified"),
            "- Desired secondary service functions: "
            + (", ".join(app_fit.get("desired_secondary_service_functions", [])) or "none specified"),
            "- Key constraints: "
            + (
                ", ".join(f"{key}={value}" for key, value in constraints.items() if value)
                or "not specified"
            ),
        ]
    )
    lines.extend(_markdown_table_from_mix("Fit status counts", app_fit.get("fit_status_counts", {})))
    for status, candidate_ids in app_fit.get("candidate_ids_by_fit_status", {}).items():
        lines.append(f"- {status}: {', '.join(candidate_ids) or 'none'}")
    lines.extend(
        [
            "- Candidates missing all required primary functions: "
            + (
                ", ".join(_as_list(coverage.get("candidate_ids_missing_all_required_functions")))
                or "none"
            ),
            "- Candidates matching all required primary functions: "
            + (
                ", ".join(_as_list(coverage.get("candidate_ids_matching_all_required_functions")))
                or "none"
            ),
            "- Candidates matching some required primary functions: "
            + (
                ", ".join(_as_list(coverage.get("candidate_ids_matching_some_required_functions")))
                or "none"
            ),
            "- Common blockers: " + (", ".join(app_fit.get("common_blockers", [])[:5]) or "none visible"),
            "- Common major cautions: " + (", ".join(app_fit.get("common_major_cautions", [])[:5]) or "none visible"),
            "- Required next evidence themes: "
            + (", ".join(app_fit.get("required_next_evidence_themes", [])[:8]) or "none visible"),
        ]
    )
    for note in app_fit.get("practical_use_summary", [])[:4]:
        lines.append(f"- {note}")
    for record in app_fit.get("fit_records", [])[:12]:
        lines.extend(
            [
                f"### Application Fit: {record.get('candidate_id')}",
                f"- Fit status: {record.get('fit_status')}",
                "- Matched required primary functions: "
                + (", ".join(_as_list(record.get("matched_required_primary_functions"))) or "none"),
                "- Missing required primary functions: "
                + (", ".join(_as_list(record.get("missing_required_primary_functions"))) or "none"),
                "- Major cautions: " + ("; ".join(_as_list(record.get("major_cautions"))[:3]) or "none visible"),
                "- Required next evidence: "
                + ("; ".join(_as_list(record.get("required_next_evidence"))[:3]) or "not specified"),
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
            "- Shared primary service functions: "
            + (", ".join(diagnostic.get("shared_primary_service_functions", [])) or "none visible"),
            "- Shared support considerations: "
            + (", ".join(diagnostic.get("shared_support_considerations", [])) or "none visible"),
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
                "- Shared primary service functions: "
                + (", ".join(_as_list(pairwise.get("shared_primary_service_functions"))) or "none visible"),
                "- Shared secondary service functions: "
                + (", ".join(_as_list(pairwise.get("shared_secondary_service_functions"))) or "none visible"),
                "- Shared support considerations: "
                + (", ".join(_as_list(pairwise.get("shared_support_considerations"))) or "none visible"),
                "- Shared risk/interface considerations: "
                + (", ".join(_as_list(pairwise.get("shared_risk_considerations"))) or "none visible"),
                "- Coating-only surface functions: "
                + (", ".join(_as_list(pairwise.get("coating_only_surface_functions"))) or "none visible"),
                "- Gradient-only surface functions: "
                + (", ".join(_as_list(pairwise.get("gradient_only_surface_functions"))) or "none visible"),
                "- Coating-only primary service functions: "
                + (", ".join(_as_list(pairwise.get("coating_only_primary_service_functions"))) or "none visible"),
                "- Gradient-only primary service functions: "
                + (", ".join(_as_list(pairwise.get("gradient_only_primary_service_functions"))) or "none visible"),
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
                f"- Primary service functions: {', '.join(card['primary_service_functions']) or 'none visible'}",
                "- Support / lifecycle considerations: "
                + (", ".join(card["support_or_lifecycle_considerations"]) or "none visible"),
                "- Risk / interface considerations: "
                + (", ".join(card["risk_or_interface_considerations"]) or "none visible"),
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
