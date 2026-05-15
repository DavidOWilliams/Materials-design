from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from src.contracts import EVIDENCE_MATURITY_LEVELS
from src.requirement_schema_v2 import RequirementSchemaV2


class SchemaValidationResult(TypedDict, total=False):
    valid: bool
    errors: List[str]
    warnings: List[str]


_DICT_FIELDS = {
    "component",
    "mechanical",
    "thermal",
    "environment",
    "manufacturing",
    "lifecycle",
    "hard_constraints",
    "soft_objectives",
}

_LIST_FIELDS = {
    "material_family_inclusions",
    "material_family_exclusions",
    "ambiguities",
    "assumptions",
    "interpreter_trace",
}

_BOOL_OR_NONE_FIELDS = {
    "coating_allowed",
    "composite_allowed",
    "graded_architecture_allowed",
    "research_generated_allowed",
}

_KNOWN_DESIGN_INTENTS = {
    "selection",
    "substitution",
    "new_material_system",
    "coating_or_surface_system",
    "graded_am_system",
    "research_exploration",
}


def _is_dict(value: Any) -> bool:
    return isinstance(value, dict)


def _is_list(value: Any) -> bool:
    return isinstance(value, list)


def validate_requirement_schema_v2(requirements: RequirementSchemaV2) -> SchemaValidationResult:
    """Lightweight shape validation for Phase 1 Build 4 requirement contracts."""
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(requirements, dict):
        return {
            "valid": False,
            "errors": ["RequirementSchemaV2 must be a dictionary-like object."],
            "warnings": [],
        }

    schema_version = requirements.get("schema_version")
    if schema_version is not None and not isinstance(schema_version, str):
        errors.append("schema_version must be a string when provided.")

    design_intent = requirements.get("design_intent")
    if design_intent is not None:
        if not isinstance(design_intent, str):
            errors.append("design_intent must be a string when provided.")
        elif design_intent not in _KNOWN_DESIGN_INTENTS:
            warnings.append(f"Unknown design_intent: {design_intent}")

    prompt_raw = requirements.get("prompt_raw")
    prompt_normalized = requirements.get("prompt_normalized")
    if prompt_raw is not None and not isinstance(prompt_raw, str):
        errors.append("prompt_raw must be a string when provided.")
    if prompt_normalized is not None and not isinstance(prompt_normalized, str):
        errors.append("prompt_normalized must be a string when provided.")
    if not prompt_raw and not prompt_normalized:
        warnings.append("No prompt text supplied in prompt_raw or prompt_normalized.")

    for field in _DICT_FIELDS:
        value = requirements.get(field)
        if value is not None and not _is_dict(value):
            errors.append(f"{field} must be a dictionary when provided.")

    for field in _LIST_FIELDS:
        value = requirements.get(field)
        if value is not None and not _is_list(value):
            errors.append(f"{field} must be a list when provided.")

    for field in _BOOL_OR_NONE_FIELDS:
        value = requirements.get(field)
        if value is not None and not isinstance(value, bool):
            errors.append(f"{field} must be a boolean or None when provided.")

    confidence = requirements.get("interpreter_confidence")
    if confidence is not None:
        if not isinstance(confidence, (int, float)):
            errors.append("interpreter_confidence must be numeric when provided.")
        elif confidence < 0 or confidence > 1:
            warnings.append("interpreter_confidence is outside the expected 0..1 range.")

    lifecycle = requirements.get("lifecycle") or {}
    if isinstance(lifecycle, dict):
        maturity_floor = lifecycle.get("evidence_maturity_floor")
        if maturity_floor is not None and maturity_floor not in EVIDENCE_MATURITY_LEVELS:
            errors.append("lifecycle.evidence_maturity_floor must be one of A, B, C, D, E or F.")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def assert_requirement_schema_v2(requirements: RequirementSchemaV2) -> None:
    """Raise ValueError when the lightweight RequirementSchemaV2 shape check fails."""
    result = validate_requirement_schema_v2(requirements)
    if not result["valid"]:
        raise ValueError("; ".join(result["errors"]))
