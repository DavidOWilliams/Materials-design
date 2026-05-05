from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any, TypeAlias

from src.candidate_normalizer import normalize_system_candidates
from src.evidence_model import evaluate_candidates_evidence
from src.factor_models.dispatcher import (
    evaluate_candidate_systems_factors,
    summarize_factor_outputs,
)
from src.material_system_schema import MaterialSystemCandidate
from src.source_orchestrator import summarise_source_mix
from src.system_assembler import assemble_material_systems, summarize_system_assembly


RecommendationPackage: TypeAlias = dict[str, Any]


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
    return [value]


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = candidate.get("evidence_package") or candidate.get("evidence") or {}
    evidence_mapping = evidence if isinstance(evidence, Mapping) else {}
    return _text(
        evidence_mapping.get("maturity")
        or evidence_mapping.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    )


def _factor_namespace(factor_score: Mapping[str, Any]) -> str:
    factor = _text(factor_score.get("factor") or factor_score.get("factor_name"), "unknown")
    return factor.split(".", 1)[0] if "." in factor else factor


def _research_mode_enabled(design_space: Mapping[str, Any]) -> bool:
    flags = design_space.get("architecture_flags") or {}
    flag_mapping = flags if isinstance(flags, Mapping) else {}
    return (
        design_space.get("research_mode_enabled") is True
        or flag_mapping.get("allow_research_mode_candidates") is True
    )


def _evidence_maturity_summary(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "candidate_count": len(candidates),
        "maturity_counts": dict(
            sorted(Counter(_evidence_maturity(candidate) for candidate in candidates).items())
        ),
    }


def _package_warnings(
    *,
    candidates: Sequence[Mapping[str, Any]],
    design_space: Mapping[str, Any],
    existing_warnings: Sequence[str] | None,
) -> list[str]:
    output = [str(warning) for warning in _as_list(existing_warnings) if str(warning).strip()]

    def append_once(message: str) -> None:
        if message not in output:
            output.append(message)

    append_once("Final ranking is not implemented; ranked_recommendations is intentionally empty.")
    append_once("Pareto analysis is not implemented; pareto_front is intentionally empty.")

    if not candidates:
        append_once("No candidate systems were provided to the recommendation package builder.")
    if _research_mode_enabled(design_space):
        append_once("Research mode is enabled in design space, but research adapters remain disabled in this skeleton.")
    if any(_evidence_maturity(candidate) in {"E", "F"} for candidate in candidates):
        append_once("Exploratory or generated evidence maturity E/F exists among candidate systems.")

    for candidate in candidates:
        candidate_id = _text(candidate.get("candidate_id"), "unknown_candidate")
        for warning in _as_list(candidate.get("assembly_warnings")):
            append_once(f"{candidate_id}: {warning}")
        for warning in _as_list(candidate.get("factor_model_warnings")):
            append_once(f"{candidate_id}: {warning}")

    return output


def build_recommendation_package(
    requirement_schema: Mapping[str, Any],
    design_space: Mapping[str, Any],
    candidate_systems: Sequence[Mapping[str, Any]],
    *,
    run_id: str | None = None,
    source_mix_summary: Mapping[str, Any] | None = None,
    diagnostics: Mapping[str, Any] | None = None,
    warnings: Sequence[str] | None = None,
) -> RecommendationPackage:
    """Build a transparent Build 4 package without ranking, optimisation or filtering."""
    source_candidates = list(candidate_systems)
    normalized_candidates = normalize_system_candidates(source_candidates)
    evidence_candidates = evaluate_candidates_evidence(normalized_candidates)
    assembled_candidates = assemble_material_systems(evidence_candidates)
    factor_candidates: list[MaterialSystemCandidate] = evaluate_candidate_systems_factors(
        assembled_candidates
    )

    source_count = len(source_candidates)
    candidate_count_preserved = (
        source_count
        == len(normalized_candidates)
        == len(evidence_candidates)
        == len(assembled_candidates)
        == len(factor_candidates)
    )

    factor_summary = summarize_factor_outputs(factor_candidates)
    system_assembly_summary = summarize_system_assembly(factor_candidates)
    evidence_summary = _evidence_maturity_summary(factor_candidates)

    package_diagnostics = {
        **dict(diagnostics or {}),
        "recommendation_builder": "build4_package_skeleton",
        "input_candidate_count": source_count,
        "normalized_candidate_count": len(normalized_candidates),
        "evidence_candidate_count": len(evidence_candidates),
        "assembled_candidate_count": len(assembled_candidates),
        "factor_evaluated_candidate_count": len(factor_candidates),
        "candidate_count_preserved": candidate_count_preserved,
        "live_model_calls_made": False,
        "materials_project_calls_made": False,
        "ranking_performed": False,
        "optimisation_performed": False,
        "pareto_analysis_performed": False,
        "candidate_filtering_performed": False,
        "research_candidates_created": False,
    }

    package: RecommendationPackage = {
        "run_id": run_id or "build4_recommendation_package_skeleton",
        "requirement_schema": dict(requirement_schema),
        "design_space": dict(design_space),
        "candidate_systems": factor_candidates,
        "ranked_recommendations": [],
        "pareto_front": [],
        "optimisation_summary": {"status": "not_implemented"},
        "source_mix_summary": dict(source_mix_summary or summarise_source_mix(factor_candidates)),
        "evidence_maturity_summary": evidence_summary,
        "diagnostics": package_diagnostics,
        "warnings": _package_warnings(
            candidates=factor_candidates,
            design_space=design_space,
            existing_warnings=warnings,
        ),
        "factor_summary": factor_summary,
        "system_assembly_summary": system_assembly_summary,
        "package_status": "skeleton_not_ranked",
    }
    return package


def build_package_from_candidate_source_package(
    source_package: Mapping[str, Any],
    *,
    run_id: str | None = None,
) -> RecommendationPackage:
    """Build a recommendation package from source-orchestrator or vertical-slice output."""
    requirement_schema = source_package.get("requirement_schema") or {}
    design_space = source_package.get("design_space") or {}
    candidate_systems = source_package.get("candidate_systems") or []
    return build_recommendation_package(
        requirement_schema=requirement_schema if isinstance(requirement_schema, Mapping) else {},
        design_space=design_space if isinstance(design_space, Mapping) else {},
        candidate_systems=[
            candidate for candidate in _as_list(candidate_systems) if isinstance(candidate, Mapping)
        ],
        run_id=run_id or _text(source_package.get("run_id")) or None,
        source_mix_summary=source_package.get("source_mix_summary")
        if isinstance(source_package.get("source_mix_summary"), Mapping)
        else None,
        diagnostics=source_package.get("diagnostics")
        if isinstance(source_package.get("diagnostics"), Mapping)
        else None,
        warnings=[
            str(warning) for warning in _as_list(source_package.get("warnings")) if str(warning).strip()
        ],
    )


def summarize_recommendation_package(package: Mapping[str, Any]) -> dict[str, Any]:
    """Return compact counts and visibility flags for a recommendation package."""
    candidates = [
        candidate
        for candidate in _as_list(package.get("candidate_systems"))
        if isinstance(candidate, Mapping)
    ]
    design_space = package.get("design_space") or {}
    design_space_mapping = design_space if isinstance(design_space, Mapping) else {}
    factor_namespace_mix = Counter(
        _factor_namespace(score)
        for candidate in candidates
        for score in _as_list(candidate.get("factor_scores"))
        if isinstance(score, Mapping)
    )
    optimisation_summary = package.get("optimisation_summary") or {}
    optimisation_mapping = optimisation_summary if isinstance(optimisation_summary, Mapping) else {}

    return {
        "run_id": _text(package.get("run_id")),
        "package_status": _text(package.get("package_status"), "unknown"),
        "candidate_count": len(candidates),
        "candidate_class_mix": dict(sorted(Counter(_candidate_class(candidate) for candidate in candidates).items())),
        "system_architecture_mix": dict(sorted(Counter(_architecture(candidate) for candidate in candidates).items())),
        "evidence_maturity_mix": dict(
            sorted(Counter(_evidence_maturity(candidate) for candidate in candidates).items())
        ),
        "factor_namespace_mix": dict(sorted(factor_namespace_mix.items())),
        "candidates_with_interfaces": sum(1 for candidate in candidates if _as_list(candidate.get("interfaces"))),
        "warning_count": len(_as_list(package.get("warnings"))),
        "research_mode_enabled": _research_mode_enabled(design_space_mapping),
        "ranked_recommendations_count": len(_as_list(package.get("ranked_recommendations"))),
        "pareto_front_count": len(_as_list(package.get("pareto_front"))),
        "optimisation_status": _text(optimisation_mapping.get("status"), "unknown"),
    }


def validate_recommendation_package_shape(package: Mapping[str, Any]) -> list[str]:
    """Return non-throwing validation messages for package shape inconsistencies."""
    messages: list[str] = []
    required_fields = (
        "run_id",
        "requirement_schema",
        "design_space",
        "candidate_systems",
        "ranked_recommendations",
        "pareto_front",
        "optimisation_summary",
        "source_mix_summary",
        "evidence_maturity_summary",
        "diagnostics",
        "warnings",
        "factor_summary",
        "system_assembly_summary",
        "package_status",
    )
    for field in required_fields:
        if field not in package:
            messages.append(f"Missing required package field: {field}.")

    if "candidate_systems" in package and not isinstance(package.get("candidate_systems"), list):
        messages.append("candidate_systems must be a list.")
    if "ranked_recommendations" in package and not isinstance(package.get("ranked_recommendations"), list):
        messages.append("ranked_recommendations must be a list.")
    if "pareto_front" in package and not isinstance(package.get("pareto_front"), list):
        messages.append("pareto_front must be a list.")
    if "warnings" in package and not isinstance(package.get("warnings"), list):
        messages.append("warnings must be a list.")

    candidates = _as_list(package.get("candidate_systems"))
    diagnostics = package.get("diagnostics") or {}
    diagnostics_mapping = diagnostics if isinstance(diagnostics, Mapping) else {}
    reported_count = diagnostics_mapping.get("input_candidate_count")
    if reported_count is not None and reported_count != len(candidates):
        messages.append("diagnostics.input_candidate_count does not match candidate_systems length.")

    optimisation_summary = package.get("optimisation_summary") or {}
    if isinstance(optimisation_summary, Mapping):
        if optimisation_summary.get("status") != "not_implemented":
            messages.append("optimisation_summary.status should be not_implemented for this skeleton.")
    elif "optimisation_summary" in package:
        messages.append("optimisation_summary must be a mapping.")

    if _as_list(package.get("ranked_recommendations")):
        messages.append("ranked_recommendations should be empty in this skeleton.")
    if _as_list(package.get("pareto_front")):
        messages.append("pareto_front should be empty in this skeleton.")

    return messages
