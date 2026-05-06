from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import EVIDENCE_MATURITY_LEVELS
from src.material_system_schema import MaterialSystemCandidate
from src.optimisation.limiting_factors import (
    identify_limiting_factors,
    summarize_limiting_factors,
)
from src.optimisation.refinement_operators import (
    select_refinement_operators,
    summarize_refinement_operators,
)


SKELETON_WARNING = "Deterministic optimisation skeleton only; no variants were generated."


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


def _candidates_from_package(package: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [
        candidate
        for candidate in _as_list(package.get("candidate_systems"))
        if isinstance(candidate, Mapping)
    ]


def build_candidate_optimisation_trace(
    candidate: Mapping[str, Any],
    package_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic analyse/propose trace for one existing candidate."""
    limiting_factors = identify_limiting_factors(candidate)
    refinement_options = select_refinement_operators(candidate, limiting_factors, package_context)
    warnings = []
    if not limiting_factors:
        warnings.append("No limiting factors identified by skeleton heuristics.")
    if not refinement_options:
        warnings.append("No refinement operators suggested by skeleton heuristics.")
    return {
        "candidate_id": _candidate_id(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "evidence_maturity": _evidence_maturity(candidate),
        "limiting_factors": limiting_factors,
        "refinement_options": refinement_options,
        "status": "analysed_no_variants_generated",
        "variants_generated": [],
        "before_after_deltas": [],
        "warnings": warnings,
    }


def _theme_from_factor(record: Mapping[str, Any]) -> str:
    text = _blob(record)
    for theme, terms in (
        ("maturity", ("maturity", "evidence", "certification", "qualification")),
        ("interface", ("interface", "spallation", "mismatch", "transition", "delamination")),
        ("inspection", ("inspection", "inspectability", "proof", "repair")),
        ("oxidation_or_environment", ("oxidation", "corrosion", "steam", "recession", "thermal")),
        ("process", ("process", "route", "repeatability", "window")),
    ):
        if any(term in text for term in terms):
            return theme
    return _text(record.get("namespace"), "other")


def build_coating_vs_gradient_comparison(
    candidates: Sequence[Mapping[str, Any]],
    package_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare coating-enabled and spatial-gradient visibility without selecting a winner."""
    context = _mapping(package_context)
    design_space = _mapping(context.get("design_space"))
    coating_ids = [
        _candidate_id(candidate)
        for candidate in candidates
        if _candidate_class(candidate) == "coating_enabled"
        or _architecture(candidate) == "substrate_plus_coating"
    ]
    gradient_ids = [
        _candidate_id(candidate)
        for candidate in candidates
        if _candidate_class(candidate) == "spatially_graded_am"
        or _architecture(candidate) == "spatial_gradient"
    ]
    comparison_required = (
        design_space.get("coating_vs_gradient_comparison_required") is True
        or (bool(coating_ids) and bool(gradient_ids))
    )
    coating_themes = {
        _theme_from_factor(record)
        for candidate in candidates
        if _candidate_id(candidate) in coating_ids
        for record in identify_limiting_factors(candidate)
    }
    gradient_themes = {
        _theme_from_factor(record)
        for candidate in candidates
        if _candidate_id(candidate) in gradient_ids
        for record in identify_limiting_factors(candidate)
    }
    shared = sorted(coating_themes & gradient_themes)

    notes: list[str] = []
    warnings: list[str] = []
    if comparison_required:
        notes.extend(
            [
                "Comparison is architectural only; no winner is selected.",
                "Coating-enabled systems keep coating life, interface, inspection and repair risks visible.",
                "Spatial-gradient systems keep transition-zone, process-window, inspectability and maturity risks visible.",
                "Certification risk remains evidence-dependent and is not optimized here.",
            ]
        )
    if not coating_ids:
        warnings.append("No coating-enabled candidates are visible for coating-vs-gradient comparison.")
    if not gradient_ids:
        warnings.append("No spatial-gradient candidates are visible for coating-vs-gradient comparison.")

    return {
        "comparison_required": comparison_required,
        "coating_enabled_candidate_ids": coating_ids,
        "spatial_gradient_candidate_ids": gradient_ids,
        "shared_limiting_factor_themes": shared,
        "comparison_notes": notes,
        "warnings": warnings,
    }


def build_deterministic_optimisation_summary(package: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize the deterministic optimisation skeleton for a package."""
    candidates = _candidates_from_package(package)
    traces = [
        build_candidate_optimisation_trace(candidate, package)
        for candidate in candidates
    ]
    limiting_summary = summarize_limiting_factors(candidates)
    operator_summary = summarize_refinement_operators(traces)
    comparison = build_coating_vs_gradient_comparison(candidates, package)
    warnings = list(limiting_summary.get("warnings") or [])
    warnings.append(SKELETON_WARNING)
    return {
        "status": "skeleton_no_variants_generated",
        "candidate_count": len(candidates),
        "trace_count": len(traces),
        "total_limiting_factor_count": limiting_summary["total_limiting_factor_count"],
        "total_refinement_option_count": operator_summary["total_refinement_option_count"],
        "severity_counts": limiting_summary["severity_counts"],
        "operator_type_counts": operator_summary["operator_type_counts"],
        "coating_vs_gradient_comparison": comparison,
        "generated_candidate_count": 0,
        "live_model_calls_made": False,
        "warnings": warnings,
    }


def attach_deterministic_optimisation(package: Mapping[str, Any]) -> dict[str, Any]:
    """Attach deterministic optimisation traces to a RecommendationPackage-compatible copy."""
    output = dict(package)
    candidates: list[MaterialSystemCandidate] = [dict(candidate) for candidate in _candidates_from_package(package)]
    traces = [
        build_candidate_optimisation_trace(candidate, output)
        for candidate in candidates
    ]
    comparison = build_coating_vs_gradient_comparison(candidates, output)

    limiting_summary = summarize_limiting_factors(candidates)
    operator_summary = summarize_refinement_operators(traces)
    summary_warnings = list(limiting_summary.get("warnings") or [])
    summary_warnings.append(SKELETON_WARNING)
    optimisation_summary = {
        "status": "skeleton_no_variants_generated",
        "candidate_count": len(candidates),
        "trace_count": len(traces),
        "total_limiting_factor_count": limiting_summary["total_limiting_factor_count"],
        "total_refinement_option_count": operator_summary["total_refinement_option_count"],
        "severity_counts": limiting_summary["severity_counts"],
        "operator_type_counts": operator_summary["operator_type_counts"],
        "coating_vs_gradient_comparison": comparison,
        "generated_candidate_count": 0,
        "live_model_calls_made": False,
        "warnings": summary_warnings,
    }

    package_warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    if SKELETON_WARNING not in package_warnings:
        package_warnings.append(SKELETON_WARNING)

    output["candidate_systems"] = candidates
    output["optimisation_trace"] = traces
    output["optimisation_summary"] = optimisation_summary
    output["coating_vs_gradient_comparison"] = comparison
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    output["warnings"] = package_warnings
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "deterministic_optimisation_attached": True,
            "generated_candidate_count": 0,
            "live_model_calls_made": False,
            "ranking_performed": False,
            "pareto_analysis_performed": False,
            "candidate_filtering_performed": False,
        }
    )
    output["diagnostics"] = diagnostics
    return output
