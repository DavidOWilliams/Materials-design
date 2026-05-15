from __future__ import annotations

from typing import Any, Dict, List

from src.contracts import CONSTITUENT_ROLES, GRADIENT_TYPES, MATERIAL_SYSTEM_CLASSES
from src.requirement_schema_v2 import DesignSpace, RequirementSchemaV2, RequirementValue
from src.schema_validator import validate_requirement_schema_v2


BULK_SYSTEM_ARCHITECTURE = "bulk_material"
SUBSTRATE_PLUS_COATING_ARCHITECTURE = "substrate_plus_coating"
SPATIAL_GRADIENT_ARCHITECTURE = "spatial_gradient"
COMPOSITE_ARCHITECTURE = "composite_architecture"
RESEARCH_MODE_ARCHITECTURE = "research_mode_candidate"


def _as_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _flag(requirements: RequirementSchemaV2, field: str) -> bool:
    return requirements.get(field) is True


def _design_intent(requirements: RequirementSchemaV2) -> str:
    return str(requirements.get("design_intent") or "selection")


def _manufacturing(requirements: RequirementSchemaV2) -> Dict[str, Any]:
    value = requirements.get("manufacturing") or {}
    return value if isinstance(value, dict) else {}


def _lifecycle(requirements: RequirementSchemaV2) -> Dict[str, Any]:
    value = requirements.get("lifecycle") or {}
    return value if isinstance(value, dict) else {}


def _collect_target_property_windows(requirements: RequirementSchemaV2) -> Dict[str, RequirementValue]:
    windows: Dict[str, RequirementValue] = {}
    for group_name in ("mechanical", "thermal", "lifecycle"):
        group = requirements.get(group_name) or {}
        if not isinstance(group, dict):
            continue
        for key, value in group.items():
            if isinstance(value, dict) and any(marker in value for marker in ("target", "minimum", "maximum")):
                windows[f"{group_name}.{key}"] = value
    return windows


def _active_failure_modes(requirements: RequirementSchemaV2) -> List[str]:
    active: List[str] = []
    mechanical = requirements.get("mechanical") or {}
    environment = requirements.get("environment") or {}

    if isinstance(mechanical, dict):
        for key in ("fatigue", "creep", "thermal_fatigue", "wear", "impact"):
            if isinstance(mechanical.get(key), dict):
                active.append(key)

    if isinstance(environment, dict):
        for key in ("hot_corrosion", "erosion", "wear_or_sliding_contact"):
            if environment.get(key) is True:
                active.append(key)

    return sorted(set(active))


def build_design_space(requirements: RequirementSchemaV2) -> DesignSpace:
    """Build a Phase 1 Build 4 design-space contract without generating candidates."""
    validation = validate_requirement_schema_v2(requirements)
    intent = _design_intent(requirements)
    manufacturing = _manufacturing(requirements)
    lifecycle = _lifecycle(requirements)

    allow_bulk_material_only = True
    allow_substrate_plus_coating = _flag(requirements, "coating_allowed") or intent == "coating_or_surface_system"
    allow_spatial_gradients = _flag(requirements, "graded_architecture_allowed") or intent == "graded_am_system"
    allow_composite_architecture = _flag(requirements, "composite_allowed")
    allow_research_mode_candidates = _flag(requirements, "research_generated_allowed") or intent == "research_exploration"
    research_mode_enabled = allow_research_mode_candidates

    allowed_candidate_classes = ["metallic", "monolithic_ceramic"]
    system_architectures = [BULK_SYSTEM_ARCHITECTURE]

    if allow_substrate_plus_coating:
        allowed_candidate_classes.extend(["coating_enabled", "hybrid"])
        system_architectures.append(SUBSTRATE_PLUS_COATING_ARCHITECTURE)
    if allow_spatial_gradients:
        allowed_candidate_classes.extend(["spatially_graded_am", "hybrid"])
        system_architectures.append(SPATIAL_GRADIENT_ARCHITECTURE)
    if allow_composite_architecture:
        allowed_candidate_classes.extend(["ceramic_matrix_composite", "polymer_matrix_composite", "hybrid"])
        system_architectures.append(COMPOSITE_ARCHITECTURE)
    if allow_research_mode_candidates:
        allowed_candidate_classes.append("research_generated")
        system_architectures.append(RESEARCH_MODE_ARCHITECTURE)

    allowed_candidate_classes = [
        item for item in MATERIAL_SYSTEM_CLASSES if item in sorted(set(allowed_candidate_classes))
    ]
    system_architectures = sorted(set(system_architectures), key=system_architectures.index)

    allowed_routes = _as_list(manufacturing.get("preferred_routes")) + _as_list(
        manufacturing.get("acceptable_routes")
    )

    warnings = list(validation.get("warnings", []))
    if not validation.get("valid", False):
        warnings.extend(validation.get("errors", []))

    return {
        "design_space_version": "build4.phase1.foundation",
        "requirement_schema_version": str(requirements.get("schema_version") or "v2"),
        "allowed_system_classes": allowed_candidate_classes,
        "allowed_material_families": _as_list(requirements.get("material_family_inclusions")),
        "excluded_material_families": _as_list(requirements.get("material_family_exclusions")),
        "allowed_constituent_roles": list(CONSTITUENT_ROLES),
        "allowed_gradient_types": list(GRADIENT_TYPES) if allow_spatial_gradients else [],
        "allowed_manufacturing_routes": sorted(set(allowed_routes)),
        "excluded_manufacturing_routes": _as_list(manufacturing.get("disallowed_routes")),
        "target_property_windows": _collect_target_property_windows(requirements),
        "active_failure_modes": _active_failure_modes(requirements),
        "active_factor_weights": dict(requirements.get("soft_objectives") or {}),
        "evidence_maturity_floor": lifecycle.get("evidence_maturity_floor"),
        "retrieval_hints": {},
        "generation_hints": {
            "candidate_generation_enabled": False,
            "live_model_calls_enabled": False,
        },
        "warnings": warnings,
        "planner_trace": [
            "Built Build 4 Phase 1 foundation design space only.",
            "No candidate generation, UI change or live model call was performed.",
        ],
        "architecture_flags": {
            "allow_bulk_material_only": allow_bulk_material_only,
            "allow_substrate_plus_coating": allow_substrate_plus_coating,
            "allow_spatial_gradients": allow_spatial_gradients,
            "allow_composite_architecture": allow_composite_architecture,
            "allow_research_mode_candidates": allow_research_mode_candidates,
        },
        "system_architectures": system_architectures,
        "allowed_candidate_classes": allowed_candidate_classes,
        "coating_vs_gradient_comparison_required": (
            allow_substrate_plus_coating and allow_spatial_gradients
        ),
        "research_mode_enabled": research_mode_enabled,
    }
