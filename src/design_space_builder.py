from __future__ import annotations

from typing import Any, TypedDict

from src.requirement_schema_v2 import (
    default_requirement_schema_v2,
    hot_section_demo_requirement_schema_v2,
    merge_requirement_schema_v2,
    validate_requirement_schema_v2,
)


DESIGN_SPACE_SCHEMA_VERSION = "material_system_design_space_v1"

ARCHITECTURE_FAMILIES: tuple[str, ...] = (
    "bulk_material",
    "metallic_system",
    "monolithic_ceramic_system",
    "cmc_system",
    "pmc_system",
    "substrate_plus_coating_system",
    "coating_enabled_system",
    "hybrid_system",
    "spatially_graded_am_system",
    "research_generated_system",
)

COATING_OPTIONS: tuple[str, ...] = (
    "thermal_barrier_coating",
    "environmental_barrier_coating",
    "oxidation_protection_coating",
    "wear_resistant_coating",
    "bond_coat_interface_system",
)

GRADIENT_OPTIONS: tuple[str, ...] = (
    "surface_oxidation_gradient",
    "surface_wear_gradient",
    "thermal_barrier_gradient",
    "tough_core_hard_surface_gradient",
    "metal_to_ceramic_transition_gradient",
    "local_zone_property_gradient",
    "multi_material_transition_gradient",
)

PROCESS_ROUTE_OPTIONS: tuple[str, ...] = (
    "casting",
    "forging",
    "wrought_processing",
    "powder_metallurgy",
    "additive_manufacturing",
    "directed_energy_deposition",
    "laser_powder_bed_fusion",
    "hot_isostatic_pressing",
    "heat_treatment",
    "coating_deposition",
    "cvi",
    "pip",
    "machining",
    "joining",
    "inspection_ndt",
    "repair_process",
)

CRITERIA_FAMILIES: tuple[str, ...] = (
    "functional_performance",
    "failure_mode_resilience",
    "system_compatibility",
    "manufacturability",
    "inspection_repair",
    "through_life_cost",
    "sustainability",
    "supply_risk",
    "evidence_maturity",
    "qualification_risk",
    "gradient_specific_feasibility",
    "model_confidence",
    "measurement_feedback_readiness",
)

MODEL_PERMISSION_FIELDS: tuple[str, ...] = (
    "computational_models",
    "surrogate_models",
    "specialist_ai_models",
    "literature_extractors",
    "process_window_exploration",
    "property_prediction",
    "generative_research_suggestions",
)

MEASUREMENT_PERMISSION_FIELDS: tuple[str, ...] = (
    "measurement_feedback",
    "test_result_ingestion",
    "model_confidence_update",
    "active_learning_suggestions",
    "measurement_provenance_required",
    "before_after_traceability_required",
)


class DesignSpaceValidationResult(TypedDict, total=False):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


class MaterialSystemDesignSpace(TypedDict, total=False):
    schema_version: str
    source_schema_version: str
    allowed_architecture_families: list[str]
    allowed_coating_options: list[str]
    allowed_gradient_options: list[str]
    allowed_process_routes: list[str]
    active_criteria: list[str]
    active_criteria_families: list[str]
    optimisation_permissions: dict[str, bool]
    model_permissions: dict[str, bool]
    measurement_permissions: dict[str, bool]
    research_mode_allowed: bool
    coating_vs_gradient_comparison_required: bool
    spatial_property_optimisation_required: bool
    computational_model_support_allowed: bool
    measurement_feedback_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


def unique_preserve_order(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        text = str(value)
        if text in seen:
            continue
        seen.add(text)
        unique_values.append(text)
    return unique_values


def bool_value(section: dict, field_name: str) -> bool:
    return isinstance(section, dict) and section.get(field_name) is True


def enabled_fields(section: dict) -> list[str]:
    if not isinstance(section, dict):
        return []
    return [field_name for field_name, value in section.items() if value is True]


def architecture_families_from_requirement(schema: dict) -> list[str]:
    material_intent = schema.get("material_system_intent", {})
    families: list[str] = []
    if bool_value(material_intent, "allow_bulk_material_only"):
        families.extend(["bulk_material", "metallic_system"])
    if bool_value(material_intent, "allow_substrate_plus_coating"):
        families.extend(
            [
                "metallic_system",
                "substrate_plus_coating_system",
                "coating_enabled_system",
            ]
        )
    if bool_value(material_intent, "allow_composite_architecture"):
        families.extend(["cmc_system", "pmc_system", "monolithic_ceramic_system"])
    if bool_value(material_intent, "allow_hybrid_systems"):
        families.append("hybrid_system")
    if bool_value(material_intent, "allow_spatial_gradients"):
        families.append("spatially_graded_am_system")
    if bool_value(material_intent, "allow_research_mode_candidates"):
        families.append("research_generated_system")
    return unique_preserve_order(families)


def _iter_text_values(value: object) -> list[str]:
    if isinstance(value, dict):
        values: list[str] = []
        for key, nested in value.items():
            values.append(str(key))
            values.extend(_iter_text_values(nested))
        return values
    if isinstance(value, list):
        values = []
        for nested in value:
            values.extend(_iter_text_values(nested))
        return values
    return [str(value)]


def _contains_any_text(schema: dict, needles: tuple[str, ...]) -> bool:
    haystack_values = list(schema.get("active_criteria", []))
    haystack_values.extend(_iter_text_values(schema.get("application_context", {})))
    haystack = " ".join(str(value).lower() for value in haystack_values)
    return any(needle in haystack for needle in needles)


def coating_options_from_requirement(schema: dict) -> list[str]:
    material_intent = schema.get("material_system_intent", {})
    optimisation_intent = schema.get("optimisation_intent", {})
    coatings_enabled = bool_value(
        material_intent, "allow_substrate_plus_coating"
    ) or bool_value(optimisation_intent, "allow_coating_refinements")
    if not coatings_enabled:
        return []

    options = [
        "thermal_barrier_coating",
        "environmental_barrier_coating",
        "oxidation_protection_coating",
        "bond_coat_interface_system",
    ]
    if _contains_any_text(schema, ("wear", "erosion", "contact damage", "contact")):
        options.append("wear_resistant_coating")
    return unique_preserve_order(options)


def gradient_options_from_requirement(schema: dict) -> list[str]:
    material_intent = schema.get("material_system_intent", {})
    optimisation_intent = schema.get("optimisation_intent", {})
    spatial_intent = schema.get("spatial_property_intent", {})
    gradients_enabled = bool_value(
        material_intent, "allow_spatial_gradients"
    ) or bool_value(optimisation_intent, "allow_gradient_refinements")
    if not gradients_enabled:
        return []

    options: list[str] = []
    if bool_value(spatial_intent, "surface_to_core_property_needs"):
        options.extend(
            [
                "surface_oxidation_gradient",
                "thermal_barrier_gradient",
                "tough_core_hard_surface_gradient",
            ]
        )
    if bool_value(spatial_intent, "coating_replacement_allowed"):
        options.extend(["surface_oxidation_gradient", "thermal_barrier_gradient"])
    if bool_value(spatial_intent, "gradient_as_coating_alternative"):
        options.extend(["surface_oxidation_gradient", "thermal_barrier_gradient"])
    if bool_value(spatial_intent, "local_zone_requirements"):
        options.extend(["local_zone_property_gradient", "surface_wear_gradient"])
    if bool_value(spatial_intent, "multi_material_transition_allowed"):
        options.extend(
            [
                "metal_to_ceramic_transition_gradient",
                "multi_material_transition_gradient",
            ]
        )

    if not options:
        options.extend(["surface_oxidation_gradient", "thermal_barrier_gradient"])
    return unique_preserve_order(options)


def process_routes_from_requirement(schema: dict) -> list[str]:
    material_intent = schema.get("material_system_intent", {})
    optimisation_intent = schema.get("optimisation_intent", {})
    routes = ["heat_treatment", "inspection_ndt"]

    if bool_value(material_intent, "allow_bulk_material_only") or bool_value(
        material_intent, "allow_substrate_plus_coating"
    ):
        routes.extend(["casting", "forging", "wrought_processing", "powder_metallurgy"])
    if coating_options_from_requirement(schema):
        routes.append("coating_deposition")
    if gradient_options_from_requirement(schema):
        routes.extend(
            [
                "additive_manufacturing",
                "directed_energy_deposition",
                "laser_powder_bed_fusion",
                "hot_isostatic_pressing",
            ]
        )
    if bool_value(material_intent, "allow_composite_architecture"):
        routes.extend(["cvi", "pip"])
    if bool_value(material_intent, "allow_hybrid_systems"):
        routes.extend(["joining", "machining"])
    if bool_value(optimisation_intent, "allow_process_route_refinements"):
        routes.append("repair_process")
    return unique_preserve_order(routes)


def active_criteria_families_from_requirement(schema: dict) -> list[str]:
    criteria_intent = schema.get("criteria_valuation_intent", {})
    material_intent = schema.get("material_system_intent", {})
    cost_priorities = schema.get("cost_priorities", {})
    sustainability_priorities = schema.get("sustainability_priorities", {})
    model_permissions = model_permissions_from_requirement(schema)
    measurement_permissions = measurement_permissions_from_requirement(schema)

    families: list[str] = []
    if bool_value(criteria_intent, "estimate_performance_criteria"):
        families.extend(["functional_performance", "failure_mode_resilience"])
    if bool_value(criteria_intent, "estimate_manufacturability"):
        families.append("manufacturability")
    if bool_value(criteria_intent, "estimate_inspection_repair"):
        families.append("inspection_repair")
    if bool_value(criteria_intent, "estimate_cost") or enabled_fields(cost_priorities):
        families.append("through_life_cost")
    if bool_value(criteria_intent, "estimate_sustainability") or enabled_fields(
        sustainability_priorities
    ):
        families.append("sustainability")
    if bool_value(criteria_intent, "estimate_supply_risk"):
        families.append("supply_risk")
    if bool_value(criteria_intent, "estimate_qualification_risk"):
        families.append("qualification_risk")

    families.append("evidence_maturity")

    if bool_value(material_intent, "allow_spatial_gradients"):
        families.append("gradient_specific_feasibility")
    if any(
        value
        for field_name, value in model_permissions.items()
        if field_name != "generative_research_suggestions"
    ):
        families.append("model_confidence")
    if (
        measurement_permissions.get("measurement_feedback") is True
        or measurement_permissions.get("test_result_ingestion") is True
    ):
        families.append("measurement_feedback_readiness")

    return unique_preserve_order(families)


def optimisation_permissions_from_requirement(schema: dict) -> dict[str, bool]:
    optimisation_intent = schema.get("optimisation_intent", {})
    return {
        "optimise_existing_candidates_first": bool_value(
            optimisation_intent, "optimise_existing_candidates_first"
        ),
        "deterministic_refinements_allowed": bool_value(
            optimisation_intent, "allow_deterministic_refinements"
        ),
        "coating_refinements_allowed": bool_value(
            optimisation_intent, "allow_coating_refinements"
        ),
        "gradient_refinements_allowed": bool_value(
            optimisation_intent, "allow_gradient_refinements"
        ),
        "class_change_refinements_allowed": bool_value(
            optimisation_intent, "allow_class_change_refinements"
        ),
        "process_route_refinements_allowed": bool_value(
            optimisation_intent, "allow_process_route_refinements"
        ),
        "model_supported_refinements_allowed": bool_value(
            optimisation_intent, "allow_model_supported_refinements"
        ),
        "stop_before_research_mode_without_permission": bool_value(
            optimisation_intent, "stop_before_research_mode_without_permission"
        ),
    }


def model_permissions_from_requirement(schema: dict) -> dict[str, bool]:
    model_support_intent = schema.get("model_support_intent", {})
    return {
        "computational_models": bool_value(
            model_support_intent, "allow_computational_models"
        ),
        "surrogate_models": bool_value(model_support_intent, "allow_surrogate_models"),
        "specialist_ai_models": bool_value(
            model_support_intent, "allow_specialist_ai_models"
        ),
        "literature_extractors": bool_value(
            model_support_intent, "allow_literature_extractors"
        ),
        "process_window_exploration": bool_value(
            model_support_intent, "allow_process_window_exploration"
        ),
        "property_prediction": bool_value(
            model_support_intent, "allow_property_prediction"
        ),
        "generative_research_suggestions": bool_value(
            model_support_intent, "allow_generative_research_suggestions"
        ),
    }


def measurement_permissions_from_requirement(schema: dict) -> dict[str, bool]:
    feedback_intent = schema.get("measurement_feedback_intent", {})
    return {
        "measurement_feedback": bool_value(feedback_intent, "allow_measurement_feedback"),
        "test_result_ingestion": bool_value(feedback_intent, "allow_test_result_ingestion"),
        "model_confidence_update": bool_value(
            feedback_intent, "allow_model_confidence_update"
        ),
        "active_learning_suggestions": bool_value(
            feedback_intent, "allow_active_learning_suggestions"
        ),
        "measurement_provenance_required": bool_value(
            feedback_intent, "require_measurement_provenance"
        ),
        "before_after_traceability_required": bool_value(
            feedback_intent, "require_before_after_traceability"
        ),
    }


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values]


def build_design_space_from_requirement(schema: dict) -> dict:
    requirement_schema = merge_requirement_schema_v2(schema)
    validation = validate_requirement_schema_v2(requirement_schema)

    architecture_families = architecture_families_from_requirement(requirement_schema)
    coating_options = coating_options_from_requirement(requirement_schema)
    gradient_options = gradient_options_from_requirement(requirement_schema)
    process_routes = process_routes_from_requirement(requirement_schema)
    optimisation_permissions = optimisation_permissions_from_requirement(
        requirement_schema
    )
    model_permissions = model_permissions_from_requirement(requirement_schema)
    measurement_permissions = measurement_permissions_from_requirement(requirement_schema)

    research_mode_allowed = bool_value(
        requirement_schema.get("material_system_intent", {}),
        "allow_research_mode_candidates",
    )
    computational_model_support_allowed = any(
        value
        for field_name, value in model_permissions.items()
        if field_name != "generative_research_suggestions"
    )
    measurement_feedback_allowed = (
        measurement_permissions["measurement_feedback"] is True
        or measurement_permissions["test_result_ingestion"] is True
    )

    return {
        "schema_version": DESIGN_SPACE_SCHEMA_VERSION,
        "source_schema_version": str(requirement_schema.get("schema_version", "")),
        "allowed_architecture_families": architecture_families,
        "allowed_coating_options": coating_options,
        "allowed_gradient_options": gradient_options,
        "allowed_process_routes": process_routes,
        "active_criteria": _string_list(requirement_schema.get("active_criteria", [])),
        "active_criteria_families": active_criteria_families_from_requirement(
            requirement_schema
        ),
        "optimisation_permissions": optimisation_permissions,
        "model_permissions": model_permissions,
        "measurement_permissions": measurement_permissions,
        "research_mode_allowed": research_mode_allowed,
        "coating_vs_gradient_comparison_required": bool(
            coating_options and gradient_options
        ),
        "spatial_property_optimisation_required": bool_value(
            requirement_schema.get("spatial_property_intent", {}),
            "location_specific_optimisation_required",
        )
        or bool_value(
            requirement_schema.get("material_system_intent", {}),
            "allow_spatial_gradients",
        ),
        "computational_model_support_allowed": computational_model_support_allowed,
        "measurement_feedback_allowed": measurement_feedback_allowed,
        "assumptions": unique_preserve_order(
            _string_list(requirement_schema.get("assumptions", []))
            + ["Design space derived from RequirementSchema v2."]
        ),
        "warnings": unique_preserve_order(
            _string_list(requirement_schema.get("warnings", []))
            + _string_list(validation.get("warnings", []))
        ),
        "hard_constraints": _string_list(requirement_schema.get("hard_constraints", [])),
    }


def _validate_list_members(
    design_space: dict,
    field_name: str,
    allowed_values: tuple[str, ...],
    errors: list[str],
) -> None:
    for value in design_space.get(field_name, []):
        if value not in allowed_values:
            errors.append(f"{field_name} contains unsupported value: {value}.")


def validate_design_space(design_space: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(design_space, dict):
        return {
            "is_valid": False,
            "errors": ["Design space must be a dictionary."],
            "warnings": [],
        }

    if design_space.get("schema_version") != DESIGN_SPACE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {DESIGN_SPACE_SCHEMA_VERSION}.")

    required_list_fields = (
        "allowed_architecture_families",
        "allowed_coating_options",
        "allowed_gradient_options",
        "allowed_process_routes",
        "active_criteria",
        "active_criteria_families",
    )
    for field_name in required_list_fields:
        if not isinstance(design_space.get(field_name), list):
            errors.append(f"{field_name} must be a list.")

    for field_name in (
        "optimisation_permissions",
        "model_permissions",
        "measurement_permissions",
    ):
        if not isinstance(design_space.get(field_name), dict):
            errors.append(f"{field_name} must be a dictionary.")

    for field_name in (
        "research_mode_allowed",
        "coating_vs_gradient_comparison_required",
        "spatial_property_optimisation_required",
        "computational_model_support_allowed",
        "measurement_feedback_allowed",
    ):
        if not isinstance(design_space.get(field_name), bool):
            errors.append(f"{field_name} must be a boolean.")

    for permission_group in (
        "optimisation_permissions",
        "model_permissions",
        "measurement_permissions",
    ):
        permissions = design_space.get(permission_group, {})
        if isinstance(permissions, dict):
            for field_name, value in permissions.items():
                if not isinstance(value, bool):
                    errors.append(f"{permission_group}.{field_name} must be a boolean.")

    if isinstance(design_space.get("allowed_architecture_families"), list):
        _validate_list_members(
            design_space,
            "allowed_architecture_families",
            ARCHITECTURE_FAMILIES,
            errors,
        )
    if isinstance(design_space.get("allowed_coating_options"), list):
        _validate_list_members(
            design_space, "allowed_coating_options", COATING_OPTIONS, errors
        )
    if isinstance(design_space.get("allowed_gradient_options"), list):
        _validate_list_members(
            design_space, "allowed_gradient_options", GRADIENT_OPTIONS, errors
        )

    if design_space.get("allowed_architecture_families") == []:
        warnings.append("No architecture families are allowed.")

    if (
        design_space.get("coating_vs_gradient_comparison_required") is True
        and (
            not design_space.get("allowed_coating_options")
            or not design_space.get("allowed_gradient_options")
        )
    ):
        warnings.append(
            "Coating versus gradient comparison is required, but coating or gradient options are empty."
        )

    model_permissions = design_space.get("model_permissions", {})
    if (
        isinstance(model_permissions, dict)
        and model_permissions.get("generative_research_suggestions") is True
        and design_space.get("research_mode_allowed") is False
    ):
        warnings.append(
            "Generative research suggestions are enabled, but research mode is not allowed."
        )

    measurement_permissions = design_space.get("measurement_permissions", {})
    if (
        design_space.get("measurement_feedback_allowed") is True
        and isinstance(measurement_permissions, dict)
        and measurement_permissions.get("measurement_provenance_required") is not True
    ):
        warnings.append(
            "Measurement feedback is allowed, but measurement provenance is not required."
        )

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def design_space_summary(design_space: dict) -> dict:
    warnings_value = design_space.get("warnings", [])
    return {
        "schema_version": design_space.get("schema_version", ""),
        "architecture_family_count": len(
            design_space.get("allowed_architecture_families", [])
        )
        if isinstance(design_space.get("allowed_architecture_families"), list)
        else 0,
        "coating_option_count": len(design_space.get("allowed_coating_options", []))
        if isinstance(design_space.get("allowed_coating_options"), list)
        else 0,
        "gradient_option_count": len(design_space.get("allowed_gradient_options", []))
        if isinstance(design_space.get("allowed_gradient_options"), list)
        else 0,
        "process_route_count": len(design_space.get("allowed_process_routes", []))
        if isinstance(design_space.get("allowed_process_routes"), list)
        else 0,
        "active_criteria_count": len(design_space.get("active_criteria", []))
        if isinstance(design_space.get("active_criteria"), list)
        else 0,
        "active_criteria_family_count": len(
            design_space.get("active_criteria_families", [])
        )
        if isinstance(design_space.get("active_criteria_families"), list)
        else 0,
        "research_mode_allowed": design_space.get("research_mode_allowed") is True,
        "coating_vs_gradient_comparison_required": design_space.get(
            "coating_vs_gradient_comparison_required"
        )
        is True,
        "computational_model_support_allowed": design_space.get(
            "computational_model_support_allowed"
        )
        is True,
        "measurement_feedback_allowed": design_space.get("measurement_feedback_allowed")
        is True,
        "warning_count": len(warnings_value) if isinstance(warnings_value, list) else 0,
    }


def hot_section_demo_design_space() -> dict:
    return build_design_space_from_requirement(hot_section_demo_requirement_schema_v2())


def default_design_space() -> dict:
    return build_design_space_from_requirement(default_requirement_schema_v2())
