from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.candidate_normalizer import normalize_system_candidate
from src.evidence_model import evaluate_candidate_evidence
from src.interface_models import assess_interface_risks, summarize_interface_risks
from src.material_system_schema import MaterialSystemCandidate


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


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _candidate_classes(candidate: Mapping[str, Any]) -> set[str]:
    classes = {
        _text(candidate.get("candidate_class")).lower(),
        _text(candidate.get("system_class")).lower(),
    }
    classes.update(_text(value).lower() for value in _as_list(candidate.get("system_classes")))
    return {value for value in classes if value}


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _has_coating_or_surface_system(candidate: Mapping[str, Any]) -> bool:
    return bool(candidate.get("coating_or_surface_system") or candidate.get("coating_system"))


def _has_ebc(candidate: Mapping[str, Any]) -> bool:
    return bool(candidate.get("environmental_barrier_coating")) or "ebc" in _text(
        candidate.get("system_architecture_type")
    ).lower()


def _is_cmc_system(candidate: Mapping[str, Any]) -> bool:
    classes = _candidate_classes(candidate)
    architecture = _architecture(candidate).lower()
    return (
        "ceramic_matrix_composite" in classes
        or architecture in {"cmc_plus_ebc", "ceramic_matrix_composite"}
        or "cmc" in architecture
    )


def _is_coating_enabled(candidate: Mapping[str, Any]) -> bool:
    classes = _candidate_classes(candidate)
    architecture = _architecture(candidate).lower()
    return (
        "coating_enabled" in classes
        or architecture in {"coating_enabled", "substrate_plus_coating"}
        or _as_bool(candidate.get("coating_enabled"))
    )


def _is_spatially_graded(candidate: Mapping[str, Any]) -> bool:
    classes = _candidate_classes(candidate)
    architecture = _architecture(candidate).lower()
    return (
        "spatially_graded_am" in classes
        or "spatially_graded" in architecture
        or "spatial_gradient" in architecture
    )


def _is_coating_primary(candidate: Mapping[str, Any]) -> bool:
    return _as_bool(candidate.get("coating_primary")) or _as_bool(candidate.get("coating_led"))


def _assembly_warnings(candidate: Mapping[str, Any]) -> list[str]:
    warnings: list[str] = []
    architecture = _architecture(candidate).lower()
    constituents = _as_list(candidate.get("constituents"))

    if _is_coating_enabled(candidate) and not _has_coating_or_surface_system(candidate):
        warnings.append("Coating-enabled candidate is missing coating_or_surface_system details.")

    if _is_spatially_graded(candidate) and not candidate.get("gradient_architecture"):
        warnings.append("Spatially graded AM candidate is missing gradient_architecture details.")

    if _is_cmc_system(candidate) and not constituents and not (
        _has_ebc(candidate) or _has_coating_or_surface_system(candidate)
    ):
        warnings.append("CMC system is missing constituents and EBC/coating data.")

    if architecture == "bulk_material" and _has_coating_or_surface_system(candidate):
        warnings.append(
            "Bulk material candidate includes coating_or_surface_system and may be mislabelled."
        )

    if architecture == "bulk_material" and _has_coating_or_surface_system(candidate) and not _is_coating_primary(
        candidate
    ):
        warnings.append(
            "Coating-only records should be marked coating_primary or coating_led before treating as standalone bulk material."
        )

    return warnings


def _merge_interfaces(
    existing_interfaces: Sequence[Any],
    assessed_interfaces: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = [
        dict(item) for item in existing_interfaces if isinstance(item, Mapping)
    ]
    index_by_type = {
        _text(item.get("interface_type")): index
        for index, item in enumerate(merged)
        if _text(item.get("interface_type"))
    }

    for interface in assessed_interfaces:
        interface_type = _text(interface.get("interface_type"))
        if interface_type and interface_type in index_by_type:
            existing = merged[index_by_type[interface_type]]
            existing.update(dict(interface))
        else:
            merged.append(dict(interface))
            if interface_type:
                index_by_type[interface_type] = len(merged) - 1

    return merged


def assemble_material_system(candidate: Mapping[str, Any]) -> MaterialSystemCandidate:
    """Normalize, evidence-enrich and attach interface diagnostics to one candidate."""
    normalized = normalize_system_candidate(candidate)
    assembled: MaterialSystemCandidate = evaluate_candidate_evidence(normalized)

    trace = _as_list(assembled.get("assembly_trace"))
    trace.extend(
        [
            "normalized_material_system_candidate",
            "evaluated_candidate_evidence",
            "assessed_interface_risks",
            "checked_system_architecture_consistency",
        ]
    )

    assessed_interfaces = assess_interface_risks(assembled)
    assembled["interfaces"] = _merge_interfaces(
        _as_list(assembled.get("interfaces")),
        assessed_interfaces,
    )

    warnings = _as_list(assembled.get("assembly_warnings"))
    for warning in _assembly_warnings(assembled):
        if warning not in warnings:
            warnings.append(warning)

    assembled["assembly_trace"] = trace
    assembled["assembly_warnings"] = warnings
    return assembled


def assemble_material_systems(
    candidates: Sequence[Mapping[str, Any]],
) -> list[MaterialSystemCandidate]:
    """Assemble candidates while preserving input length and order."""
    return [assemble_material_system(candidate) for candidate in candidates]


def summarize_system_assembly(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize Build 4 assembly diagnostics without ranking or filtering."""
    assembled = assemble_material_systems(candidates)
    warnings = [
        f"{_candidate_id(candidate)}: {warning}"
        for candidate in assembled
        for warning in _as_list(candidate.get("assembly_warnings"))
    ]

    return {
        "candidate_count": len(assembled),
        "system_architecture_mix": dict(
            sorted(Counter(_architecture(candidate) for candidate in assembled).items())
        ),
        "candidate_class_mix": dict(
            sorted(
                Counter(
                    _text(
                        candidate.get("candidate_class") or candidate.get("system_class"),
                        "unknown",
                    )
                    for candidate in assembled
                ).items()
            )
        ),
        "candidates_with_interfaces": sum(
            1 for candidate in assembled if _as_list(candidate.get("interfaces"))
        ),
        "interface_risk_summary": summarize_interface_risks(assembled),
        "warnings": warnings,
    }
