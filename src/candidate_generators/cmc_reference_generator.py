from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.design_space import COMPOSITE_ARCHITECTURE
from src.material_system_schema import MaterialSystemCandidate
from src.reference_data.material_system_loaders import (
    load_cmc_systems,
    reference_record_to_material_system_candidate,
)


def _as_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _composites_allowed(design_space: Mapping[str, Any] | None) -> bool:
    if design_space is None:
        return True
    allowed = set(
        _as_list(design_space.get("allowed_candidate_classes"))
        + _as_list(design_space.get("allowed_system_classes"))
    )
    architectures = set(_as_list(design_space.get("system_architectures")))
    flags = design_space.get("architecture_flags") or {}
    allow_flag = isinstance(flags, Mapping) and flags.get("allow_composite_architecture") is True
    return (
        "ceramic_matrix_composite" in allowed
        or "hybrid" in allowed
        or COMPOSITE_ARCHITECTURE in architectures
        or allow_flag
    )


def _as_reference_candidate(record: Mapping[str, Any]) -> MaterialSystemCandidate:
    candidate = reference_record_to_material_system_candidate(record, "cmc_systems")
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
    candidate.update(
        {
            "candidate_id": record["reference_id"],
            "candidate_class": "ceramic_matrix_composite",
            "system_class": "ceramic_matrix_composite",
            "system_classes": ["ceramic_matrix_composite"],
            "system_architecture_type": "composite_architecture",
            "system_name": record.get("system_name"),
            "name": record.get("system_name"),
            "process_route": record.get("process_route"),
            "evidence_package": evidence_package,
            "evidence": evidence_package,
            "generated_candidate_flag": False,
            "research_generated": False,
            "research_mode_flag": False,
        }
    )
    return candidate


def generate_cmc_reference_candidates(
    design_space: Mapping[str, Any] | None = None,
) -> list[MaterialSystemCandidate]:
    if not _composites_allowed(design_space):
        return []
    return [_as_reference_candidate(record) for record in load_cmc_systems()]
