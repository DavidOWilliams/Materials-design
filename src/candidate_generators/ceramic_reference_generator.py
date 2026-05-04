from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.material_system_schema import MaterialSystemCandidate
from src.reference_data.material_system_loaders import (
    load_ceramic_references,
    reference_record_to_material_system_candidate,
)


def _allowed_classes(design_space: Mapping[str, Any]) -> set[str]:
    values = design_space.get("allowed_candidate_classes") or design_space.get("allowed_system_classes") or []
    if not isinstance(values, list):
        return set()
    return {str(value) for value in values}


def _ceramics_allowed(design_space: Mapping[str, Any] | None) -> bool:
    if design_space is None:
        return True
    allowed = _allowed_classes(design_space)
    if not allowed:
        return False
    return bool(
        allowed
        & {
            "monolithic_ceramic",
            "ceramic_matrix_composite",
            "coating_enabled",
            "hybrid",
            "research_generated",
        }
    )


def _as_reference_candidate(record: Mapping[str, Any]) -> MaterialSystemCandidate:
    candidate = reference_record_to_material_system_candidate(record, "ceramic_references")
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
            "candidate_class": "monolithic_ceramic",
            "system_class": "monolithic_ceramic",
            "system_classes": ["monolithic_ceramic"],
            "system_architecture_type": record.get("system_architecture_type") or "bulk_material",
            "system_name": record.get("material_name"),
            "name": record.get("material_name"),
            "process_route": record.get("process_route"),
            "evidence_package": evidence_package,
            "evidence": evidence_package,
            "generated_candidate_flag": False,
            "research_generated": False,
            "research_mode_flag": False,
        }
    )
    return candidate


def generate_ceramic_reference_candidates(
    design_space: Mapping[str, Any] | None = None,
) -> list[MaterialSystemCandidate]:
    if not _ceramics_allowed(design_space):
        return []
    return [_as_reference_candidate(record) for record in load_ceramic_references()]
