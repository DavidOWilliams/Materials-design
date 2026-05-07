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
    for field in ("assembly_warnings", "factor_model_warnings", "normalization_warnings"):
        for warning in _as_list(candidate.get(field)):
            text = _text(warning)
            if text and text not in warnings:
                warnings.append(text)
    return warnings


def build_candidate_card_view_model(candidate: Mapping[str, Any]) -> dict[str, Any]:
    maturity = _evidence_maturity(candidate)
    evidence = _evidence(candidate)
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


def build_optimisation_trace_card(trace: Mapping[str, Any]) -> dict[str, Any]:
    limiting_factors = [_mapping(item) for item in _as_list(trace.get("limiting_factors")) if _mapping(item)]
    refinement_options = [_mapping(item) for item in _as_list(trace.get("refinement_options")) if _mapping(item)]
    return {
        "candidate_id": _text(trace.get("candidate_id"), "unknown_candidate"),
        "candidate_class": _text(trace.get("candidate_class"), "unknown"),
        "system_architecture_type": _text(trace.get("system_architecture_type"), "unknown"),
        "evidence_maturity": _text(trace.get("evidence_maturity"), "unknown"),
        "status": _text(trace.get("status"), "unknown"),
        "limiting_factor_count": len(limiting_factors),
        "refinement_option_count": len(refinement_options),
        "top_limiting_factors": [
            {
                "factor": _text(item.get("factor"), "unknown_factor"),
                "namespace": _text(item.get("namespace"), "unknown"),
                "severity": _text(item.get("severity"), "unknown"),
                "reason": _text(item.get("reason")),
            }
            for item in limiting_factors[:3]
        ],
        "top_refinement_options": [
            {
                "operator_type": _text(item.get("operator_type"), "unknown_operator"),
                "status": _text(item.get("status"), "unknown"),
                "description": _text(item.get("description")),
                "expected_benefit": _text(item.get("expected_benefit")),
                "generated_candidate_flag": item.get("generated_candidate_flag") is True,
            }
            for item in refinement_options[:3]
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
    optimisation = view_model["optimisation_summary_view"]
    comparison = view_model["coating_vs_gradient_comparison_view"]
    lines.extend(
        [
            "",
            "## Deterministic Optimisation Skeleton",
            "- Deterministic optimisation is a skeleton; no variants were generated.",
            "- No final ranking was produced.",
            "- No Pareto optimisation was performed.",
            "- No live model calls were made.",
            f"- Status: {optimisation.get('status')}",
            f"- Total limiting factor count: {optimisation.get('total_limiting_factor_count')}",
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
    lines.extend(["", "## Limiting Factors and Refinement Options"])
    lines.append("- Refinement operators are suggestions, not applied design changes.")
    for trace_card in view_model["optimisation_trace_cards"]:
        lines.extend(
            [
                f"### {trace_card['candidate_id']}",
                f"- Class: {trace_card['candidate_class']}",
                f"- Evidence maturity: {trace_card['evidence_maturity']}",
                f"- Trace status: {trace_card['status']}",
                f"- Limiting factors: {trace_card['limiting_factor_count']}",
                f"- Refinement options: {trace_card['refinement_option_count']}",
            ]
        )
        for factor in trace_card["top_limiting_factors"]:
            lines.append(
                "- Top limiting factor: "
                f"{factor['factor']} ({factor['severity']}) - {factor['reason']}"
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
