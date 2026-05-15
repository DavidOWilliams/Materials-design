from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.material_system_schema import MaterialSystemCandidate
from src.reference_data.material_system_loaders import (
    load_graded_am_systems,
    reference_record_to_material_system_candidate,
)


def _gradients_allowed(design_space: Mapping[str, Any] | None) -> bool:
    if design_space is None:
        return True
    if design_space.get("allow_spatial_gradients") is True:
        return True
    flags = design_space.get("architecture_flags") or {}
    if isinstance(flags, Mapping) and flags.get("allow_spatial_gradients") is True:
        return True
    return "spatial_gradient" in {
        str(item) for item in design_space.get("system_architectures", []) if str(item).strip()
    }


def _as_reference_candidate(record: Mapping[str, Any]) -> MaterialSystemCandidate:
    candidate = reference_record_to_material_system_candidate(record, "graded_am_systems")
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
            "candidate_class": "spatially_graded_am",
            "system_class": "spatially_graded_am",
            "system_classes": ["spatially_graded_am"],
            "system_architecture_type": "spatial_gradient",
            "system_name": record.get("system_name"),
            "name": record.get("system_name"),
            "process_route": record.get("process_route"),
            "evidence_package": evidence_package,
            "evidence": evidence_package,
            "evidence_maturity": record.get("evidence_maturity"),
            "generated_candidate_flag": False,
            "research_generated": False,
            "research_mode_flag": False,
        }
    )
    return candidate


def generate_graded_am_template_candidates(
    design_space: Mapping[str, Any] | None = None,
) -> list[MaterialSystemCandidate]:
    if not _gradients_allowed(design_space):
        return []
    return [_as_reference_candidate(record) for record in load_graded_am_systems()]
