from __future__ import annotations

from typing import TypedDict

from src.design_space_builder import (
    build_design_space_from_requirement,
    hot_section_demo_design_space,
    validate_design_space,
)


SCOPE_PLAN_SCHEMA_VERSION = "material_system_scope_plan_v1"

GENERATOR_IDS: tuple[str, ...] = (
    "metallic_reference_generator",
    "ceramic_reference_generator",
    "cmc_reference_generator",
    "pmc_reference_generator",
    "coating_component_generator",
    "gradient_template_generator",
    "hybrid_reference_generator",
    "research_mode_candidate_generator",
)

ASSEMBLER_IDS: tuple[str, ...] = (
    "bulk_material_assembler",
    "substrate_plus_coating_assembler",
    "cmc_ebc_system_assembler",
    "pmc_system_assembler",
    "hybrid_system_assembler",
    "spatially_graded_am_system_assembler",
    "research_generated_system_wrapper",
)

SOURCE_IDS: tuple[str, ...] = (
    "metallic_reference_sources",
    "ceramic_reference_sources",
    "cmc_reference_sources",
    "pmc_reference_sources",
    "coating_reference_sources",
    "gradient_template_sources",
    "process_route_sources",
    "criteria_reference_sources",
    "evidence_maturity_sources",
    "model_estimate_sources",
    "measurement_feedback_sources",
)

CRITERIA_VALUATION_SCOPE_FIELDS: tuple[str, ...] = (
    "active_criteria",
    "active_criteria_families",
    "require_confidence",
    "require_uncertainty",
    "require_evidence_basis",
    "require_model_provenance",
    "require_measurement_provenance",
    "require_before_after_traceability",
)

MODEL_ADAPTER_PLACEHOLDER_IDS: tuple[str, ...] = (
    "computational_model_adapter",
    "surrogate_model_adapter",
    "specialist_ai_model_adapter",
    "literature_extractor_adapter",
    "process_window_explorer_adapter",
    "property_prediction_adapter",
    "generative_research_suggestion_adapter",
)

MEASUREMENT_FEEDBACK_SCOPE_FIELDS: tuple[str, ...] = (
    "measurement_feedback_allowed",
    "test_result_ingestion_allowed",
    "model_confidence_update_allowed",
    "active_learning_suggestions_allowed",
    "measurement_provenance_required",
    "before_after_traceability_required",
)


class GeneratorScope(TypedDict, total=False):
    generator_id: str
    label: str
    architecture_families: list[str]
    enabled: bool
    reason: str
    research_only: bool


class AssemblerScope(TypedDict, total=False):
    assembler_id: str
    label: str
    enabled: bool
    reason: str
    required_inputs: list[str]


class CriteriaValuationScope(TypedDict, total=False):
    active_criteria: list[str]
    active_criteria_families: list[str]
    require_confidence: bool
    require_uncertainty: bool
    require_evidence_basis: bool
    require_model_provenance: bool
    require_measurement_provenance: bool
    require_before_after_traceability: bool


class ModelAdapterScope(TypedDict, total=False):
    adapter_id: str
    label: str
    enabled: bool
    live_call_allowed: bool
    research_only: bool
    reason: str


class MeasurementFeedbackScope(TypedDict, total=False):
    measurement_feedback_allowed: bool
    test_result_ingestion_allowed: bool
    model_confidence_update_allowed: bool
    active_learning_suggestions_allowed: bool
    measurement_provenance_required: bool
    before_after_traceability_required: bool


class MaterialSystemScopePlan(TypedDict, total=False):
    schema_version: str
    source_design_space_version: str
    candidate_generators: list[dict]
    system_assemblers: list[dict]
    source_plan: list[dict]
    coating_options_in_scope: list[str]
    gradient_options_in_scope: list[str]
    process_routes_in_scope: list[str]
    criteria_valuation_scope: dict
    optimisation_scope: dict
    model_adapter_scope: list[dict]
    measurement_feedback_scope: dict
    research_mode_allowed: bool
    coating_vs_gradient_comparison_required: bool
    spatial_property_optimisation_required: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class ScopePlanValidationResult(TypedDict, total=False):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


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


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def generator_scope(
    generator_id: str,
    *,
    label: str,
    architecture_families: list[str],
    enabled: bool = True,
    reason: str = "",
    research_only: bool = False,
) -> dict:
    return {
        "generator_id": generator_id,
        "label": label,
        "architecture_families": list(architecture_families),
        "enabled": bool(enabled),
        "reason": reason,
        "research_only": bool(research_only),
    }


def assembler_scope(
    assembler_id: str,
    *,
    label: str,
    enabled: bool = True,
    reason: str = "",
    required_inputs: list[str] | None = None,
) -> dict:
    return {
        "assembler_id": assembler_id,
        "label": label,
        "enabled": bool(enabled),
        "reason": reason,
        "required_inputs": list(required_inputs or []),
    }


def source_scope(
    source_id: str,
    *,
    label: str,
    enabled: bool = True,
    reason: str = "",
) -> dict:
    return {
        "source_id": source_id,
        "label": label,
        "enabled": bool(enabled),
        "reason": reason,
    }


def _allowed_architectures(design_space: dict) -> list[str]:
    architectures = design_space.get("allowed_architecture_families", [])
    if not isinstance(architectures, list):
        return []
    return [str(architecture) for architecture in architectures]


def candidate_generators_from_design_space(design_space: dict) -> list[dict]:
    architectures = _allowed_architectures(design_space)
    research_mode_allowed = bool_value(design_space, "research_mode_allowed")
    generators: list[dict] = []

    def add(record: dict) -> None:
        if record["generator_id"] not in [item["generator_id"] for item in generators]:
            generators.append(record)

    if "metallic_system" in architectures or "bulk_material" in architectures:
        add(
            generator_scope(
                "metallic_reference_generator",
                label="Metallic reference generator",
                architecture_families=["metallic_system", "bulk_material"],
                reason="Metallic or bulk material architectures are in scope.",
            )
        )
    if "monolithic_ceramic_system" in architectures:
        add(
            generator_scope(
                "ceramic_reference_generator",
                label="Ceramic reference generator",
                architecture_families=["monolithic_ceramic_system"],
                reason="Monolithic ceramic architectures are in scope.",
            )
        )
    if "cmc_system" in architectures:
        add(
            generator_scope(
                "cmc_reference_generator",
                label="CMC reference generator",
                architecture_families=["cmc_system"],
                reason="Ceramic matrix composite architectures are in scope.",
            )
        )
    if "pmc_system" in architectures:
        add(
            generator_scope(
                "pmc_reference_generator",
                label="PMC reference generator",
                architecture_families=["pmc_system"],
                reason="Polymer matrix composite architectures are in scope.",
            )
        )
    if (
        "substrate_plus_coating_system" in architectures
        or "coating_enabled_system" in architectures
    ):
        add(
            generator_scope(
                "coating_component_generator",
                label="Coating component generator",
                architecture_families=[
                    "substrate_plus_coating_system",
                    "coating_enabled_system",
                ],
                reason="Coating-enabled architectures are in scope.",
            )
        )
    if "spatially_graded_am_system" in architectures:
        add(
            generator_scope(
                "gradient_template_generator",
                label="Gradient template generator",
                architecture_families=["spatially_graded_am_system"],
                reason="Spatially graded architectures are in scope.",
            )
        )
    if "hybrid_system" in architectures:
        add(
            generator_scope(
                "hybrid_reference_generator",
                label="Hybrid reference generator",
                architecture_families=["hybrid_system"],
                reason="Hybrid material-system architectures are in scope.",
            )
        )
    if "research_generated_system" in architectures and research_mode_allowed:
        add(
            generator_scope(
                "research_mode_candidate_generator",
                label="Research-mode candidate generator",
                architecture_families=["research_generated_system"],
                reason="Research-mode architecture is explicitly allowed.",
                research_only=True,
            )
        )
    return generators


def system_assemblers_from_design_space(design_space: dict) -> list[dict]:
    architectures = _allowed_architectures(design_space)
    research_mode_allowed = bool_value(design_space, "research_mode_allowed")
    assemblers: list[dict] = []

    def add(record: dict) -> None:
        if record["assembler_id"] not in [item["assembler_id"] for item in assemblers]:
            assemblers.append(record)

    if "bulk_material" in architectures or "metallic_system" in architectures:
        add(
            assembler_scope(
                "bulk_material_assembler",
                label="Bulk material assembler",
                reason="Bulk or metallic architectures are in scope.",
                required_inputs=["metallic_reference_generator"],
            )
        )
    if (
        "substrate_plus_coating_system" in architectures
        or "coating_enabled_system" in architectures
    ):
        add(
            assembler_scope(
                "substrate_plus_coating_assembler",
                label="Substrate-plus-coating assembler",
                reason="Coating-enabled system assembly is in scope.",
                required_inputs=[
                    "metallic_reference_generator",
                    "coating_component_generator",
                ],
            )
        )
    if "cmc_system" in architectures:
        add(
            assembler_scope(
                "cmc_ebc_system_assembler",
                label="CMC/EBC system assembler",
                reason="CMC architectures are in scope.",
                required_inputs=["cmc_reference_generator", "coating_component_generator"],
            )
        )
    if "pmc_system" in architectures:
        add(
            assembler_scope(
                "pmc_system_assembler",
                label="PMC system assembler",
                reason="PMC architectures are in scope.",
                required_inputs=["pmc_reference_generator"],
            )
        )
    if "hybrid_system" in architectures:
        add(
            assembler_scope(
                "hybrid_system_assembler",
                label="Hybrid system assembler",
                reason="Hybrid architectures are in scope.",
                required_inputs=["hybrid_reference_generator"],
            )
        )
    if "spatially_graded_am_system" in architectures:
        add(
            assembler_scope(
                "spatially_graded_am_system_assembler",
                label="Spatially graded AM system assembler",
                reason="Spatial gradient assembly is in scope.",
                required_inputs=["gradient_template_generator"],
            )
        )
    if "research_generated_system" in architectures and research_mode_allowed:
        add(
            assembler_scope(
                "research_generated_system_wrapper",
                label="Research-generated system wrapper",
                reason="Research-mode generated systems are explicitly allowed.",
                required_inputs=["research_mode_candidate_generator"],
            )
        )
    return assemblers


def source_plan_from_design_space(design_space: dict) -> list[dict]:
    architectures = _allowed_architectures(design_space)
    sources: list[dict] = []

    def add(record: dict) -> None:
        if record["source_id"] not in [item["source_id"] for item in sources]:
            sources.append(record)

    if "metallic_system" in architectures or "bulk_material" in architectures:
        add(
            source_scope(
                "metallic_reference_sources",
                label="Metallic reference sources",
                reason="Metallic or bulk material architectures are in scope.",
            )
        )
    if "monolithic_ceramic_system" in architectures:
        add(
            source_scope(
                "ceramic_reference_sources",
                label="Ceramic reference sources",
                reason="Monolithic ceramic architectures are in scope.",
            )
        )
    if "cmc_system" in architectures:
        add(
            source_scope(
                "cmc_reference_sources",
                label="CMC reference sources",
                reason="CMC architectures are in scope.",
            )
        )
    if "pmc_system" in architectures:
        add(
            source_scope(
                "pmc_reference_sources",
                label="PMC reference sources",
                reason="PMC architectures are in scope.",
            )
        )
    if design_space.get("allowed_coating_options"):
        add(
            source_scope(
                "coating_reference_sources",
                label="Coating reference sources",
                reason="Coating options are in scope.",
            )
        )
    if design_space.get("allowed_gradient_options"):
        add(
            source_scope(
                "gradient_template_sources",
                label="Gradient template sources",
                reason="Gradient options are in scope.",
            )
        )

    add(
        source_scope(
            "process_route_sources",
            label="Process route sources",
            reason="Process routes are part of every scope plan.",
        )
    )
    add(
        source_scope(
            "criteria_reference_sources",
            label="Criteria reference sources",
            reason="Criteria valuation support is part of every scope plan.",
        )
    )
    add(
        source_scope(
            "evidence_maturity_sources",
            label="Evidence maturity sources",
            reason="Evidence maturity support is part of every scope plan.",
        )
    )
    if bool_value(design_space, "computational_model_support_allowed"):
        add(
            source_scope(
                "model_estimate_sources",
                label="Model estimate sources",
                reason="Computational model support is allowed.",
            )
        )
    if bool_value(design_space, "measurement_feedback_allowed"):
        add(
            source_scope(
                "measurement_feedback_sources",
                label="Measurement feedback sources",
                reason="Measurement feedback is allowed.",
            )
        )
    return sources


def criteria_valuation_scope_from_design_space(design_space: dict) -> dict:
    active_families = list(design_space.get("active_criteria_families", []))
    computational_support = bool_value(design_space, "computational_model_support_allowed")
    measurement_permissions = design_space.get("measurement_permissions", {})
    require_model_records = "model_confidence" in active_families or computational_support
    return {
        "active_criteria": list(design_space.get("active_criteria", [])),
        "active_criteria_families": active_families,
        "require_confidence": require_model_records,
        "require_uncertainty": require_model_records,
        "require_evidence_basis": True,
        "require_model_provenance": computational_support,
        "require_measurement_provenance": bool_value(
            measurement_permissions, "measurement_provenance_required"
        ),
        "require_before_after_traceability": bool_value(
            measurement_permissions, "before_after_traceability_required"
        ),
    }


def optimisation_scope_from_design_space(design_space: dict) -> dict:
    permissions = design_space.get("optimisation_permissions", {})
    return {
        "optimise_existing_candidates_first": bool_value(
            permissions, "optimise_existing_candidates_first"
        ),
        "deterministic_refinements_allowed": bool_value(
            permissions, "deterministic_refinements_allowed"
        ),
        "coating_refinements_allowed": bool_value(
            permissions, "coating_refinements_allowed"
        ),
        "gradient_refinements_allowed": bool_value(
            permissions, "gradient_refinements_allowed"
        ),
        "class_change_refinements_allowed": bool_value(
            permissions, "class_change_refinements_allowed"
        ),
        "process_route_refinements_allowed": bool_value(
            permissions, "process_route_refinements_allowed"
        ),
        "model_supported_refinements_allowed": bool_value(
            permissions, "model_supported_refinements_allowed"
        ),
        "research_mode_allowed": bool_value(design_space, "research_mode_allowed"),
        "stop_before_research_mode_without_permission": bool_value(
            permissions, "stop_before_research_mode_without_permission"
        ),
        "coating_vs_gradient_comparison_required": bool_value(
            design_space, "coating_vs_gradient_comparison_required"
        ),
        "spatial_property_optimisation_required": bool_value(
            design_space, "spatial_property_optimisation_required"
        ),
    }


def model_adapter_scope_from_design_space(design_space: dict) -> list[dict]:
    permissions = design_space.get("model_permissions", {})
    research_mode_allowed = bool_value(design_space, "research_mode_allowed")
    adapter_map = {
        "computational_model_adapter": (
            "Computational model adapter",
            bool_value(permissions, "computational_models"),
            False,
            "Computational model permission is enabled.",
        ),
        "surrogate_model_adapter": (
            "Surrogate model adapter",
            bool_value(permissions, "surrogate_models"),
            False,
            "Surrogate model permission is enabled.",
        ),
        "specialist_ai_model_adapter": (
            "Specialist AI model adapter",
            bool_value(permissions, "specialist_ai_models"),
            False,
            "Specialist AI model permission is enabled.",
        ),
        "literature_extractor_adapter": (
            "Literature extractor adapter",
            bool_value(permissions, "literature_extractors"),
            False,
            "Literature extractor permission is enabled.",
        ),
        "process_window_explorer_adapter": (
            "Process window explorer adapter",
            bool_value(permissions, "process_window_exploration"),
            False,
            "Process window exploration permission is enabled.",
        ),
        "property_prediction_adapter": (
            "Property prediction adapter",
            bool_value(permissions, "property_prediction"),
            False,
            "Property prediction permission is enabled.",
        ),
    }
    scopes: list[dict] = []
    for adapter_id in MODEL_ADAPTER_PLACEHOLDER_IDS:
        if adapter_id == "generative_research_suggestion_adapter":
            requested = bool_value(permissions, "generative_research_suggestions")
            enabled = requested and research_mode_allowed
            reason = "Generative research suggestions are enabled."
            if requested and not research_mode_allowed:
                reason = "Research mode is not allowed."
            elif not requested:
                reason = "Generative research suggestions are not enabled."
            scopes.append(
                {
                    "adapter_id": adapter_id,
                    "label": "Generative research suggestion adapter",
                    "enabled": enabled,
                    "live_call_allowed": False,
                    "research_only": True,
                    "reason": reason,
                }
            )
            continue

        label, enabled, research_only, enabled_reason = adapter_map[adapter_id]
        scopes.append(
            {
                "adapter_id": adapter_id,
                "label": label,
                "enabled": enabled,
                "live_call_allowed": False,
                "research_only": research_only,
                "reason": enabled_reason if enabled else "Permission is not enabled.",
            }
        )
    return scopes


def measurement_feedback_scope_from_design_space(design_space: dict) -> dict:
    permissions = design_space.get("measurement_permissions", {})
    return {
        "measurement_feedback_allowed": bool_value(permissions, "measurement_feedback"),
        "test_result_ingestion_allowed": bool_value(permissions, "test_result_ingestion"),
        "model_confidence_update_allowed": bool_value(
            permissions, "model_confidence_update"
        ),
        "active_learning_suggestions_allowed": bool_value(
            permissions, "active_learning_suggestions"
        ),
        "measurement_provenance_required": bool_value(
            permissions, "measurement_provenance_required"
        ),
        "before_after_traceability_required": bool_value(
            permissions, "before_after_traceability_required"
        ),
    }


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values]


def build_scope_plan_from_design_space(design_space: dict) -> dict:
    validation = validate_design_space(design_space)
    candidate_generators = candidate_generators_from_design_space(design_space)
    system_assemblers = system_assemblers_from_design_space(design_space)
    coating_options = _string_list(design_space.get("allowed_coating_options", []))
    gradient_options = _string_list(design_space.get("allowed_gradient_options", []))

    warnings = unique_preserve_order(
        _string_list(design_space.get("warnings", []))
        + _string_list(validation.get("warnings", []))
    )
    if not any(generator.get("enabled") is True for generator in candidate_generators):
        warnings.append("No candidate generators are enabled.")
    if not any(assembler.get("enabled") is True for assembler in system_assemblers):
        warnings.append("No system assemblers are enabled.")
    if (
        bool_value(design_space, "coating_vs_gradient_comparison_required")
        and (not coating_options or not gradient_options)
    ):
        warnings.append(
            "Coating versus gradient comparison is required, but coating or gradient options are empty."
        )

    return {
        "schema_version": SCOPE_PLAN_SCHEMA_VERSION,
        "source_design_space_version": str(design_space.get("schema_version", "")),
        "candidate_generators": candidate_generators,
        "system_assemblers": system_assemblers,
        "source_plan": source_plan_from_design_space(design_space),
        "coating_options_in_scope": coating_options,
        "gradient_options_in_scope": gradient_options,
        "process_routes_in_scope": _string_list(
            design_space.get("allowed_process_routes", [])
        ),
        "criteria_valuation_scope": criteria_valuation_scope_from_design_space(
            design_space
        ),
        "optimisation_scope": optimisation_scope_from_design_space(design_space),
        "model_adapter_scope": model_adapter_scope_from_design_space(design_space),
        "measurement_feedback_scope": measurement_feedback_scope_from_design_space(
            design_space
        ),
        "research_mode_allowed": bool_value(design_space, "research_mode_allowed"),
        "coating_vs_gradient_comparison_required": bool_value(
            design_space, "coating_vs_gradient_comparison_required"
        ),
        "spatial_property_optimisation_required": bool_value(
            design_space, "spatial_property_optimisation_required"
        ),
        "assumptions": unique_preserve_order(
            _string_list(design_space.get("assumptions", []))
            + ["Scope plan derived from MaterialSystemDesignSpace."]
        ),
        "warnings": unique_preserve_order(warnings),
        "hard_constraints": _string_list(design_space.get("hard_constraints", [])),
    }


def _validate_ids(
    records: object,
    id_field: str,
    allowed_ids: tuple[str, ...],
    collection_name: str,
    errors: list[str],
) -> None:
    if not isinstance(records, list):
        return
    for record in records:
        if not isinstance(record, dict):
            errors.append(f"{collection_name} entries must be dictionaries.")
            continue
        record_id = record.get(id_field)
        if record_id not in allowed_ids:
            errors.append(f"{collection_name} contains unsupported {id_field}: {record_id}.")


def validate_scope_plan(scope_plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(scope_plan, dict):
        return {
            "is_valid": False,
            "errors": ["Scope plan must be a dictionary."],
            "warnings": [],
        }

    if scope_plan.get("schema_version") != SCOPE_PLAN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCOPE_PLAN_SCHEMA_VERSION}.")

    for field_name in ("candidate_generators", "system_assemblers", "source_plan"):
        if not isinstance(scope_plan.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    for field_name in ("criteria_valuation_scope", "optimisation_scope"):
        if not isinstance(scope_plan.get(field_name), dict):
            errors.append(f"{field_name} must be a dictionary.")
    if not isinstance(scope_plan.get("model_adapter_scope"), list):
        errors.append("model_adapter_scope must be a list.")
    if not isinstance(scope_plan.get("measurement_feedback_scope"), dict):
        errors.append("measurement_feedback_scope must be a dictionary.")

    for field_name in (
        "research_mode_allowed",
        "coating_vs_gradient_comparison_required",
        "spatial_property_optimisation_required",
    ):
        if not isinstance(scope_plan.get(field_name), bool):
            errors.append(f"{field_name} must be a boolean.")

    _validate_ids(
        scope_plan.get("candidate_generators"),
        "generator_id",
        GENERATOR_IDS,
        "candidate_generators",
        errors,
    )
    _validate_ids(
        scope_plan.get("system_assemblers"),
        "assembler_id",
        ASSEMBLER_IDS,
        "system_assemblers",
        errors,
    )
    _validate_ids(
        scope_plan.get("source_plan"),
        "source_id",
        SOURCE_IDS,
        "source_plan",
        errors,
    )
    _validate_ids(
        scope_plan.get("model_adapter_scope"),
        "adapter_id",
        MODEL_ADAPTER_PLACEHOLDER_IDS,
        "model_adapter_scope",
        errors,
    )

    for adapter in scope_plan.get("model_adapter_scope", []):
        if isinstance(adapter, dict) and adapter.get("live_call_allowed") is True:
            errors.append(
                f"model_adapter_scope.{adapter.get('adapter_id')} live_call_allowed must be false."
            )

    for adapter in scope_plan.get("model_adapter_scope", []):
        if (
            isinstance(adapter, dict)
            and adapter.get("adapter_id") == "generative_research_suggestion_adapter"
            and adapter.get("enabled") is True
            and scope_plan.get("research_mode_allowed") is False
        ):
            warnings.append(
                "Generative research suggestion adapter is enabled while research mode is not allowed."
            )

    measurement_scope = scope_plan.get("measurement_feedback_scope", {})
    if (
        isinstance(measurement_scope, dict)
        and measurement_scope.get("measurement_feedback_allowed") is True
        and measurement_scope.get("measurement_provenance_required") is not True
    ):
        warnings.append(
            "Measurement feedback is allowed, but measurement provenance is not required."
        )

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def scope_plan_summary(scope_plan: dict) -> dict:
    candidate_generators = scope_plan.get("candidate_generators", [])
    system_assemblers = scope_plan.get("system_assemblers", [])
    source_plan = scope_plan.get("source_plan", [])
    criteria_scope = scope_plan.get("criteria_valuation_scope", {})
    model_adapter_scope = scope_plan.get("model_adapter_scope", [])
    warnings = scope_plan.get("warnings", [])
    return {
        "schema_version": scope_plan.get("schema_version", ""),
        "candidate_generator_count": len(candidate_generators)
        if isinstance(candidate_generators, list)
        else 0,
        "enabled_candidate_generator_count": len(
            [
                generator
                for generator in candidate_generators
                if isinstance(generator, dict) and generator.get("enabled") is True
            ]
        )
        if isinstance(candidate_generators, list)
        else 0,
        "system_assembler_count": len(system_assemblers)
        if isinstance(system_assemblers, list)
        else 0,
        "enabled_system_assembler_count": len(
            [
                assembler
                for assembler in system_assemblers
                if isinstance(assembler, dict) and assembler.get("enabled") is True
            ]
        )
        if isinstance(system_assemblers, list)
        else 0,
        "source_count": len(source_plan) if isinstance(source_plan, list) else 0,
        "coating_option_count": len(scope_plan.get("coating_options_in_scope", []))
        if isinstance(scope_plan.get("coating_options_in_scope"), list)
        else 0,
        "gradient_option_count": len(scope_plan.get("gradient_options_in_scope", []))
        if isinstance(scope_plan.get("gradient_options_in_scope"), list)
        else 0,
        "process_route_count": len(scope_plan.get("process_routes_in_scope", []))
        if isinstance(scope_plan.get("process_routes_in_scope"), list)
        else 0,
        "active_criteria_count": len(criteria_scope.get("active_criteria", []))
        if isinstance(criteria_scope, dict)
        and isinstance(criteria_scope.get("active_criteria"), list)
        else 0,
        "active_criteria_family_count": len(
            criteria_scope.get("active_criteria_families", [])
        )
        if isinstance(criteria_scope, dict)
        and isinstance(criteria_scope.get("active_criteria_families"), list)
        else 0,
        "enabled_model_adapter_count": len(
            [
                adapter
                for adapter in model_adapter_scope
                if isinstance(adapter, dict) and adapter.get("enabled") is True
            ]
        )
        if isinstance(model_adapter_scope, list)
        else 0,
        "live_model_call_count": len(
            [
                adapter
                for adapter in model_adapter_scope
                if isinstance(adapter, dict)
                and adapter.get("live_call_allowed") is True
            ]
        )
        if isinstance(model_adapter_scope, list)
        else 0,
        "measurement_feedback_allowed": bool_value(
            scope_plan.get("measurement_feedback_scope", {}),
            "measurement_feedback_allowed",
        ),
        "research_mode_allowed": bool_value(scope_plan, "research_mode_allowed"),
        "coating_vs_gradient_comparison_required": bool_value(
            scope_plan, "coating_vs_gradient_comparison_required"
        ),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_scope_plan() -> dict:
    return build_scope_plan_from_design_space(hot_section_demo_design_space())


def build_scope_plan_from_requirement(requirement_schema: dict) -> dict:
    return build_scope_plan_from_design_space(
        build_design_space_from_requirement(requirement_schema)
    )
