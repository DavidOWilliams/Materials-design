from __future__ import annotations

from typing import Any, TypedDict


MATERIAL_SYSTEM_INTENT_FIELDS: tuple[str, ...] = (
    "allow_bulk_material_only",
    "allow_substrate_plus_coating",
    "allow_spatial_gradients",
    "allow_composite_architecture",
    "allow_hybrid_systems",
    "allow_research_mode_candidates",
)

SPATIAL_PROPERTY_INTENT_FIELDS: tuple[str, ...] = (
    "surface_to_core_property_needs",
    "local_zone_requirements",
    "coating_replacement_allowed",
    "gradient_as_coating_alternative",
    "multi_material_transition_allowed",
    "location_specific_optimisation_required",
)

COST_PRIORITY_FIELDS: tuple[str, ...] = (
    "acquisition_cost",
    "manufacturing_cost",
    "inspection_cost",
    "repair_cost",
    "replacement_cost",
    "qualification_cost",
    "lifecycle_cost",
)

SUSTAINABILITY_PRIORITY_FIELDS: tuple[str, ...] = (
    "embodied_carbon",
    "critical_materials",
    "recyclability",
    "repair_life_extension",
    "process_energy_burden",
    "hazardous_substances",
    "circularity_potential",
)

OPTIMISATION_INTENT_FIELDS: tuple[str, ...] = (
    "optimise_existing_candidates_first",
    "allow_deterministic_refinements",
    "allow_coating_refinements",
    "allow_gradient_refinements",
    "allow_class_change_refinements",
    "allow_process_route_refinements",
    "allow_model_supported_refinements",
    "stop_before_research_mode_without_permission",
)

CRITERIA_VALUATION_INTENT_FIELDS: tuple[str, ...] = (
    "estimate_performance_criteria",
    "estimate_manufacturability",
    "estimate_inspection_repair",
    "estimate_cost",
    "estimate_sustainability",
    "estimate_supply_risk",
    "estimate_qualification_risk",
    "include_confidence_bands",
    "include_uncertainty_drivers",
    "include_evidence_basis",
)

MODEL_SUPPORT_INTENT_FIELDS: tuple[str, ...] = (
    "allow_computational_models",
    "allow_surrogate_models",
    "allow_specialist_ai_models",
    "allow_literature_extractors",
    "allow_process_window_exploration",
    "allow_property_prediction",
    "allow_generative_research_suggestions",
    "require_model_provenance",
    "require_model_uncertainty",
)

MEASUREMENT_FEEDBACK_INTENT_FIELDS: tuple[str, ...] = (
    "allow_measurement_feedback",
    "allow_test_result_ingestion",
    "allow_model_confidence_update",
    "allow_active_learning_suggestions",
    "require_measurement_provenance",
    "require_before_after_traceability",
)

REQUIREMENT_SCHEMA_SECTIONS: tuple[str, ...] = (
    "material_system_intent",
    "spatial_property_intent",
    "cost_priorities",
    "sustainability_priorities",
    "optimisation_intent",
    "criteria_valuation_intent",
    "model_support_intent",
    "measurement_feedback_intent",
    "hard_constraints",
    "application_context",
    "active_criteria",
    "assumptions",
    "warnings",
)

BOOLEAN_SECTION_FIELDS: dict[str, tuple[str, ...]] = {
    "material_system_intent": MATERIAL_SYSTEM_INTENT_FIELDS,
    "spatial_property_intent": SPATIAL_PROPERTY_INTENT_FIELDS,
    "cost_priorities": COST_PRIORITY_FIELDS,
    "sustainability_priorities": SUSTAINABILITY_PRIORITY_FIELDS,
    "optimisation_intent": OPTIMISATION_INTENT_FIELDS,
    "criteria_valuation_intent": CRITERIA_VALUATION_INTENT_FIELDS,
    "model_support_intent": MODEL_SUPPORT_INTENT_FIELDS,
    "measurement_feedback_intent": MEASUREMENT_FEEDBACK_INTENT_FIELDS,
}

LIST_SECTIONS: tuple[str, ...] = (
    "hard_constraints",
    "active_criteria",
    "assumptions",
    "warnings",
)


class RequirementIntentSection(TypedDict, total=False):
    values: dict[str, bool]
    assumptions: list[str]
    warnings: list[str]


class RequirementSchemaV2(TypedDict, total=False):
    schema_version: str
    source: str
    application_context: dict[str, Any]
    material_system_intent: dict[str, bool]
    spatial_property_intent: dict[str, bool]
    cost_priorities: dict[str, bool]
    sustainability_priorities: dict[str, bool]
    optimisation_intent: dict[str, bool]
    criteria_valuation_intent: dict[str, bool]
    model_support_intent: dict[str, bool]
    measurement_feedback_intent: dict[str, bool]
    hard_constraints: list[str]
    active_criteria: list[str]
    assumptions: list[str]
    warnings: list[str]


class RequirementSchemaValidationResult(TypedDict, total=False):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


class RequirementValue(TypedDict, total=False):
    target: Any
    minimum: Any
    maximum: Any
    unit: str | None
    priority: float
    mandatory: bool
    rationale: str


class DesignSpace(TypedDict, total=False):
    design_space_version: str
    requirement_schema_version: str
    allowed_system_classes: list[str]
    allowed_material_families: list[str]
    excluded_material_families: list[str]
    allowed_constituent_roles: list[str]
    allowed_gradient_types: list[str]
    allowed_manufacturing_routes: list[str]
    excluded_manufacturing_routes: list[str]
    target_property_windows: dict[str, RequirementValue]
    active_failure_modes: list[str]
    active_factor_weights: dict[str, float]
    evidence_maturity_floor: str | None
    retrieval_hints: dict[str, Any]
    generation_hints: dict[str, Any]
    warnings: list[str]
    planner_trace: list[str]


def bool_section(
    field_names: list[str] | tuple[str, ...], *, default: bool = False
) -> dict[str, bool]:
    return {field_name: bool(default) for field_name in field_names}


def default_requirement_schema_v2() -> dict:
    schema = {
        "schema_version": "requirement_schema_v2",
        "source": "default",
        "application_context": {},
        "material_system_intent": bool_section(MATERIAL_SYSTEM_INTENT_FIELDS),
        "spatial_property_intent": bool_section(SPATIAL_PROPERTY_INTENT_FIELDS),
        "cost_priorities": bool_section(COST_PRIORITY_FIELDS),
        "sustainability_priorities": bool_section(SUSTAINABILITY_PRIORITY_FIELDS),
        "optimisation_intent": bool_section(OPTIMISATION_INTENT_FIELDS),
        "criteria_valuation_intent": bool_section(CRITERIA_VALUATION_INTENT_FIELDS),
        "model_support_intent": bool_section(MODEL_SUPPORT_INTENT_FIELDS),
        "measurement_feedback_intent": bool_section(MEASUREMENT_FEEDBACK_INTENT_FIELDS),
        "hard_constraints": [],
        "active_criteria": [],
        "assumptions": [],
        "warnings": [],
    }
    schema["optimisation_intent"].update(
        {
            "optimise_existing_candidates_first": True,
            "allow_deterministic_refinements": True,
        }
    )
    schema["criteria_valuation_intent"].update(
        {
            "include_confidence_bands": True,
            "include_uncertainty_drivers": True,
            "include_evidence_basis": True,
        }
    )
    schema["model_support_intent"].update(
        {
            "require_model_provenance": True,
            "require_model_uncertainty": True,
        }
    )
    schema["measurement_feedback_intent"].update(
        {
            "require_measurement_provenance": True,
            "require_before_after_traceability": True,
        }
    )
    return schema


def allowed_field_names_for_section(section_name: str) -> tuple[str, ...]:
    return BOOLEAN_SECTION_FIELDS.get(section_name, ())


def normalise_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalised = value.strip().lower()
        if normalised in {"true", "yes", "1", "on"}:
            return True
        if normalised in {"false", "no", "0", "off"}:
            return False
    return False


def normalise_bool_section(section_name: str, values: dict | None) -> dict[str, bool]:
    allowed_fields = allowed_field_names_for_section(section_name)
    incoming = values if isinstance(values, dict) else {}
    return {
        field_name: normalise_bool(incoming.get(field_name, False))
        for field_name in allowed_fields
    }


def _normalise_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def merge_requirement_schema_v2(overrides: dict | None) -> dict:
    schema = default_requirement_schema_v2()
    if not isinstance(overrides, dict):
        return schema

    supplied_version = overrides.get("schema_version")
    if supplied_version == "requirement_schema_v2":
        schema["schema_version"] = supplied_version
    elif supplied_version is not None:
        schema["warnings"].append(
            "Unsupported schema_version override ignored; using requirement_schema_v2."
        )

    if "source" in overrides:
        schema["source"] = str(overrides["source"])

    if isinstance(overrides.get("application_context"), dict):
        schema["application_context"] = dict(overrides["application_context"])

    for section_name in BOOLEAN_SECTION_FIELDS:
        if section_name not in overrides:
            continue
        base_section = dict(schema[section_name])
        normalised_overrides = normalise_bool_section(section_name, overrides.get(section_name))
        for field_name in allowed_field_names_for_section(section_name):
            if isinstance(overrides.get(section_name), dict) and field_name in overrides[section_name]:
                base_section[field_name] = normalised_overrides[field_name]
        schema[section_name] = base_section

    for section_name in LIST_SECTIONS:
        if section_name in overrides:
            schema[section_name] = _normalise_list(overrides[section_name])

    return schema


def validate_requirement_schema_v2(schema: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(schema, dict):
        return {
            "is_valid": False,
            "errors": ["RequirementSchemaV2 must be a dictionary."],
            "warnings": [],
        }

    if schema.get("schema_version") != "requirement_schema_v2":
        errors.append("schema_version must be requirement_schema_v2.")

    for section_name, field_names in BOOLEAN_SECTION_FIELDS.items():
        section = schema.get(section_name)
        if not isinstance(section, dict):
            errors.append(f"{section_name} must be a dictionary.")
            continue
        for field_name in field_names:
            if field_name not in section:
                errors.append(f"{section_name}.{field_name} is required.")
            elif not isinstance(section[field_name], bool):
                errors.append(f"{section_name}.{field_name} must be a boolean.")

    for section_name in LIST_SECTIONS:
        if not isinstance(schema.get(section_name), list):
            errors.append(f"{section_name} must be a list.")

    if not isinstance(schema.get("application_context"), dict):
        errors.append("application_context must be a dictionary.")

    material_intent = schema.get("material_system_intent", {})
    spatial_intent = schema.get("spatial_property_intent", {})
    optimisation_intent = schema.get("optimisation_intent", {})
    model_support_intent = schema.get("model_support_intent", {})
    measurement_feedback_intent = schema.get("measurement_feedback_intent", {})

    if isinstance(material_intent, dict) and not any(
        bool(material_intent.get(field_name))
        for field_name in MATERIAL_SYSTEM_INTENT_FIELDS
        if field_name != "allow_research_mode_candidates"
    ):
        warnings.append("No material-system architecture option is enabled.")

    if (
        isinstance(material_intent, dict)
        and isinstance(spatial_intent, dict)
        and material_intent.get("allow_spatial_gradients") is True
        and not any(bool(spatial_intent.get(field_name)) for field_name in SPATIAL_PROPERTY_INTENT_FIELDS)
    ):
        warnings.append(
            "Spatial gradients are allowed, but no spatial property intent is enabled."
        )

    if (
        isinstance(optimisation_intent, dict)
        and isinstance(model_support_intent, dict)
        and optimisation_intent.get("allow_model_supported_refinements") is True
        and not any(
            model_support_intent.get(field_name) is True
            for field_name in (
                "allow_computational_models",
                "allow_surrogate_models",
                "allow_specialist_ai_models",
            )
        )
    ):
        warnings.append(
            "Model-supported refinements are allowed, but no computational, surrogate, or specialist AI model family is enabled."
        )

    if (
        isinstance(measurement_feedback_intent, dict)
        and measurement_feedback_intent.get("allow_measurement_feedback") is True
        and measurement_feedback_intent.get("require_measurement_provenance") is not True
    ):
        warnings.append(
            "Measurement feedback is allowed, but measurement provenance is not required."
        )

    if (
        isinstance(model_support_intent, dict)
        and isinstance(material_intent, dict)
        and model_support_intent.get("allow_generative_research_suggestions") is True
        and material_intent.get("allow_research_mode_candidates") is not True
    ):
        warnings.append(
            "Generative research suggestions are allowed, but research-mode candidates are disabled."
        )

    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }


def _enabled_fields(section: dict | None, field_names: tuple[str, ...]) -> list[str]:
    if not isinstance(section, dict):
        return []
    return [field_name for field_name in field_names if section.get(field_name) is True]


def requirement_schema_summary(schema: dict) -> dict:
    warnings_value = schema.get("warnings", [])
    active_criteria = schema.get("active_criteria", [])
    hard_constraints = schema.get("hard_constraints", [])
    return {
        "schema_version": schema.get("schema_version", ""),
        "enabled_material_system_intents": _enabled_fields(
            schema.get("material_system_intent"), MATERIAL_SYSTEM_INTENT_FIELDS
        ),
        "enabled_spatial_property_intents": _enabled_fields(
            schema.get("spatial_property_intent"), SPATIAL_PROPERTY_INTENT_FIELDS
        ),
        "enabled_cost_priorities": _enabled_fields(
            schema.get("cost_priorities"), COST_PRIORITY_FIELDS
        ),
        "enabled_sustainability_priorities": _enabled_fields(
            schema.get("sustainability_priorities"), SUSTAINABILITY_PRIORITY_FIELDS
        ),
        "enabled_optimisation_intents": _enabled_fields(
            schema.get("optimisation_intent"), OPTIMISATION_INTENT_FIELDS
        ),
        "enabled_criteria_valuation_intents": _enabled_fields(
            schema.get("criteria_valuation_intent"), CRITERIA_VALUATION_INTENT_FIELDS
        ),
        "enabled_model_support_intents": _enabled_fields(
            schema.get("model_support_intent"), MODEL_SUPPORT_INTENT_FIELDS
        ),
        "enabled_measurement_feedback_intents": _enabled_fields(
            schema.get("measurement_feedback_intent"), MEASUREMENT_FEEDBACK_INTENT_FIELDS
        ),
        "active_criteria_count": len(active_criteria) if isinstance(active_criteria, list) else 0,
        "hard_constraints_count": len(hard_constraints) if isinstance(hard_constraints, list) else 0,
        "warnings_count": len(warnings_value) if isinstance(warnings_value, list) else 0,
    }


def hot_section_demo_requirement_schema_v2() -> dict:
    return merge_requirement_schema_v2(
        {
            "source": "hot_section_demo",
            "application_context": {
                "domain": "aviation_hot_section",
                "exposure": "thermal_cycling_and_oxidation",
                "criticality": "safety_critical",
            },
            "material_system_intent": {
                "allow_substrate_plus_coating": True,
                "allow_spatial_gradients": True,
                "allow_composite_architecture": True,
                "allow_hybrid_systems": True,
                "allow_research_mode_candidates": False,
            },
            "spatial_property_intent": {
                "surface_to_core_property_needs": True,
                "coating_replacement_allowed": True,
                "gradient_as_coating_alternative": True,
                "local_zone_requirements": True,
            },
            "cost_priorities": {
                "manufacturing_cost": True,
                "inspection_cost": True,
                "repair_cost": True,
                "qualification_cost": True,
                "lifecycle_cost": True,
            },
            "sustainability_priorities": {
                "embodied_carbon": True,
                "critical_materials": True,
                "repair_life_extension": True,
                "process_energy_burden": True,
            },
            "optimisation_intent": {
                "optimise_existing_candidates_first": True,
                "allow_deterministic_refinements": True,
                "allow_coating_refinements": True,
                "allow_gradient_refinements": True,
                "allow_process_route_refinements": True,
                "stop_before_research_mode_without_permission": True,
            },
            "criteria_valuation_intent": {
                "estimate_performance_criteria": True,
                "estimate_manufacturability": True,
                "estimate_inspection_repair": True,
                "estimate_cost": True,
                "estimate_sustainability": True,
                "estimate_qualification_risk": True,
                "include_confidence_bands": True,
                "include_uncertainty_drivers": True,
                "include_evidence_basis": True,
            },
            "model_support_intent": {
                "allow_computational_models": True,
                "allow_surrogate_models": True,
                "allow_process_window_exploration": True,
                "allow_property_prediction": True,
                "require_model_provenance": True,
                "require_model_uncertainty": True,
            },
            "measurement_feedback_intent": {
                "require_measurement_provenance": True,
                "require_before_after_traceability": True,
            },
            "active_criteria": [
                "temperature_capability",
                "oxidation_resistance",
                "thermal_cycling_resilience",
                "coating_spallation_risk",
                "gradient_transition_risk",
                "manufacturability",
                "inspection_burden",
                "repairability",
                "lifecycle_cost",
                "embodied_carbon",
                "critical_material_exposure",
                "qualification_risk",
            ],
            "assumptions": [
                "Hot-section exposure is treated as safety-critical.",
                "Model-supported estimates require confidence and uncertainty records.",
                "Research-generated candidates remain disabled unless explicitly enabled.",
            ],
            "warnings": [
                "This schema supports design-space planning and optimisation support only; it does not imply material qualification or certification approval.",
            ],
        }
    )
