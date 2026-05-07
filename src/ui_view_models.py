from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.contracts import evidence_maturity_label, evidence_maturity_treatment
from src.recommendation_builder import summarize_recommendation_package


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
