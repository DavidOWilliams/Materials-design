from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.design_space import SUBSTRATE_PLUS_COATING_ARCHITECTURE
from src.material_system_schema import MaterialSystemCandidate
from src.reference_data.material_system_loaders import (
    load_coating_systems,
    reference_record_to_material_system_candidate,
)


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _coatings_allowed(design_space: Mapping[str, Any] | None) -> bool:
    if design_space is None:
        return True
    allowed = set(
        _as_list(design_space.get("allowed_candidate_classes"))
        + _as_list(design_space.get("allowed_system_classes"))
    )
    architectures = set(_as_list(design_space.get("system_architectures")))
    flags = design_space.get("architecture_flags") or {}
    allow_flag = isinstance(flags, Mapping) and flags.get("allow_substrate_plus_coating") is True
    return (
        "coating_enabled" in allowed
        or "hybrid" in allowed
        or SUBSTRATE_PLUS_COATING_ARCHITECTURE in architectures
        or "coating_enabled" in architectures
        or allow_flag
    )


def generate_coating_component_references(
    design_space: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not _coatings_allowed(design_space):
        return []
    return [
        {
            **record,
            "component_type": "coating_component_reference",
            "standalone_bulk_candidate": False,
            "generated_candidate_flag": False,
            "research_mode_flag": False,
        }
        for record in load_coating_systems()
    ]


def _as_reference_candidate(record: Mapping[str, Any]) -> MaterialSystemCandidate:
    candidate = reference_record_to_material_system_candidate(record, "coating_systems")
    evidence_package = dict(candidate.get("evidence", {}))
    evidence_package.update(
        {
            "evidence_maturity": record.get("evidence_maturity"),
            "source_reference": record.get("source_reference"),
            "applicability_guardrails": record.get("applicability_guardrails"),
            "known_strengths": record.get("known_strengths"),
            "known_watch_outs": record.get("known_watch_outs"),
        }
    )
    system_name = f"{record.get('substrate_family')} with {record.get('coating_name')}"
    candidate.update(
        {
            "candidate_id": record["reference_id"],
            "candidate_class": "coating_enabled",
            "system_class": "coating_enabled",
            "system_classes": ["coating_enabled"],
            "system_architecture_type": "substrate_plus_coating",
            "system_name": system_name,
            "name": system_name,
            "process_route": record.get("process_route"),
            "coating_role": record.get("coating_role"),
            "substrate_family": record.get("substrate_family"),
            "evidence_package": evidence_package,
            "evidence": evidence_package,
            "generated_candidate_flag": False,
            "research_generated": False,
            "research_mode_flag": False,
        }
    )
    return candidate


def generate_coating_enabled_reference_candidates(
    design_space: Mapping[str, Any] | None = None,
) -> list[MaterialSystemCandidate]:
    if not _coatings_allowed(design_space):
        return []
    return [_as_reference_candidate(record) for record in load_coating_systems()]
