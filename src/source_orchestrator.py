from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.candidate_generators.build31_metallic_adapter import wrap_build31_dataframe
from src.candidate_generators.ceramic_reference_generator import (
    generate_ceramic_reference_candidates,
)
from src.candidate_generators.cmc_reference_generator import (
    generate_cmc_reference_candidates,
)
from src.candidate_generators.coating_component_generator import (
    generate_coating_enabled_reference_candidates,
)
from src.candidate_generators.graded_am_template_generator import (
    generate_graded_am_template_candidates,
)
from src.design_space import build_design_space
from src.material_system_schema import MaterialSystemCandidate


BUILD31_METALLIC_SOURCE = "build31_metallic"
CERAMIC_REFERENCE_SOURCE = "ceramic_reference"
CMC_REFERENCE_SOURCE = "cmc_reference"
COATING_ENABLED_REFERENCE_SOURCE = "coating_enabled_reference"
GRADED_AM_TEMPLATE_SOURCE = "graded_am_template"


def _resolve_design_space(
    requirements: Mapping[str, Any] | None,
    design_space: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    if design_space is not None:
        return design_space
    if requirements is not None:
        return build_design_space(dict(requirements))
    return None


def _architecture_flags(design_space: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not design_space:
        return {}
    flags = design_space.get("architecture_flags") or {}
    return flags if isinstance(flags, Mapping) else {}


def _research_mode_enabled(design_space: Mapping[str, Any] | None) -> bool:
    if not design_space:
        return False
    flags = _architecture_flags(design_space)
    return (
        design_space.get("research_mode_enabled") is True
        or flags.get("allow_research_mode_candidates") is True
    )


def _spatial_gradients_requested(design_space: Mapping[str, Any] | None) -> bool:
    if not design_space:
        return False
    flags = _architecture_flags(design_space)
    architectures = design_space.get("system_architectures") or []
    return (
        design_space.get("allow_spatial_gradients") is True
        or flags.get("allow_spatial_gradients") is True
        or "spatial_gradient" in {str(item) for item in architectures}
    )


def _with_source_label(
    candidates: Sequence[Mapping[str, Any]],
    source_label: str,
) -> list[MaterialSystemCandidate]:
    labelled: list[MaterialSystemCandidate] = []
    for candidate in candidates:
        copy = dict(candidate)
        copy["source_label"] = source_label
        copy.setdefault("source_type", source_label)
        labelled.append(copy)
    return labelled


def _source_label_for_candidate(candidate: Mapping[str, Any]) -> str:
    source_label = candidate.get("source_label")
    if source_label:
        return str(source_label)

    source_type = str(candidate.get("source_type") or "")
    if source_type in {"engineering_analogue", "materials_project", "build31_metallic_baseline"}:
        return BUILD31_METALLIC_SOURCE

    provenance = candidate.get("provenance") or {}
    source_table = provenance.get("source_table") if isinstance(provenance, Mapping) else None
    if source_table == "ceramic_references":
        return CERAMIC_REFERENCE_SOURCE
    if source_table == "cmc_systems":
        return CMC_REFERENCE_SOURCE
    if source_table == "coating_systems":
        return COATING_ENABLED_REFERENCE_SOURCE
    if source_table == "graded_am_systems":
        return GRADED_AM_TEMPLATE_SOURCE

    candidate_class = str(candidate.get("candidate_class") or candidate.get("system_class") or "")
    if candidate_class == "metallic":
        return BUILD31_METALLIC_SOURCE
    if candidate_class == "monolithic_ceramic":
        return CERAMIC_REFERENCE_SOURCE
    if candidate_class == "ceramic_matrix_composite":
        return CMC_REFERENCE_SOURCE
    if candidate_class == "coating_enabled":
        return COATING_ENABLED_REFERENCE_SOURCE
    if candidate_class == "spatially_graded_am":
        return GRADED_AM_TEMPLATE_SOURCE
    return "unknown"


def summarise_source_mix(
    candidate_systems: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    source_counts = Counter(_source_label_for_candidate(candidate) for candidate in candidate_systems)
    class_counts = Counter(
        str(candidate.get("candidate_class") or candidate.get("system_class") or "unknown")
        for candidate in candidate_systems
    )
    architecture_counts = Counter(
        str(candidate.get("system_architecture_type") or "unknown")
        for candidate in candidate_systems
    )
    return {
        "total_candidate_count": len(candidate_systems),
        "source_counts": dict(sorted(source_counts.items())),
        "candidate_class_counts": dict(sorted(class_counts.items())),
        "system_architecture_counts": dict(sorted(architecture_counts.items())),
    }


def generate_candidate_sources(
    requirements: Mapping[str, Any] | None = None,
    design_space: Mapping[str, Any] | None = None,
    build31_candidates_df: Any | None = None,
) -> dict[str, Any]:
    resolved_design_space = _resolve_design_space(requirements, design_space)

    candidate_systems: list[MaterialSystemCandidate] = []
    build31_candidates: list[MaterialSystemCandidate] = []
    if build31_candidates_df is not None:
        build31_candidates = wrap_build31_dataframe(
            build31_candidates_df,
            requirements=requirements,
        )
        candidate_systems.extend(_with_source_label(build31_candidates, BUILD31_METALLIC_SOURCE))

    ceramic_candidates = generate_ceramic_reference_candidates(resolved_design_space)
    cmc_candidates = generate_cmc_reference_candidates(resolved_design_space)
    coating_candidates = generate_coating_enabled_reference_candidates(resolved_design_space)
    graded_candidates = generate_graded_am_template_candidates(resolved_design_space)

    candidate_systems.extend(_with_source_label(ceramic_candidates, CERAMIC_REFERENCE_SOURCE))
    candidate_systems.extend(_with_source_label(cmc_candidates, CMC_REFERENCE_SOURCE))
    candidate_systems.extend(
        _with_source_label(coating_candidates, COATING_ENABLED_REFERENCE_SOURCE)
    )
    candidate_systems.extend(_with_source_label(graded_candidates, GRADED_AM_TEMPLATE_SOURCE))

    research_mode_enabled = _research_mode_enabled(resolved_design_space)
    diagnostics = {
        "total_candidate_count": len(candidate_systems),
        "build31_adapter_used": build31_candidates_df is not None,
        "build31_metallic_count": len(build31_candidates),
        "ceramic_reference_count": len(ceramic_candidates),
        "cmc_reference_count": len(cmc_candidates),
        "coating_enabled_reference_count": len(coating_candidates),
        "graded_am_template_count": len(graded_candidates),
        "research_mode_enabled": research_mode_enabled,
        "live_model_calls_made": False,
        "materials_project_calls_made": False,
    }

    warnings: list[str] = []
    if not candidate_systems:
        warnings.append("No Build 4 candidate systems were returned by enabled sources.")
    if research_mode_enabled:
        warnings.append("Research mode is enabled in design space, but research adapters are disabled.")
    if _spatial_gradients_requested(resolved_design_space) and not graded_candidates:
        warnings.append("Spatial gradients were requested, but no graded AM templates were returned.")

    return {
        "candidate_systems": candidate_systems,
        "source_mix_summary": summarise_source_mix(candidate_systems),
        "diagnostics": diagnostics,
        "warnings": warnings,
    }
