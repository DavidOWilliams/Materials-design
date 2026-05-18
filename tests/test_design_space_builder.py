from copy import deepcopy
from pathlib import Path

import src.design_space_builder as builder
from src.requirement_schema_v2 import (
    default_requirement_schema_v2,
    hot_section_demo_requirement_schema_v2,
    merge_requirement_schema_v2,
)


def _walk_keys_and_values(value):
    if isinstance(value, dict):
        items = []
        for key, nested in value.items():
            items.append(str(key))
            items.extend(_walk_keys_and_values(nested))
        return items
    if isinstance(value, list):
        items = []
        for nested in value:
            items.extend(_walk_keys_and_values(nested))
        return items
    return [str(value)]


def test_unique_preserve_order_removes_duplicates_and_preserves_order():
    assert builder.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_architecture_families_maps_coating_composites_and_gradients():
    schema = merge_requirement_schema_v2(
        {
            "material_system_intent": {
                "allow_substrate_plus_coating": True,
                "allow_composite_architecture": True,
                "allow_spatial_gradients": True,
            }
        }
    )

    families = builder.architecture_families_from_requirement(schema)

    assert "substrate_plus_coating_system" in families
    assert "coating_enabled_system" in families
    assert "cmc_system" in families
    assert "pmc_system" in families
    assert "spatially_graded_am_system" in families


def test_architecture_families_do_not_include_research_without_permission():
    schema = merge_requirement_schema_v2(
        {"material_system_intent": {"allow_substrate_plus_coating": True}}
    )

    assert (
        "research_generated_system"
        not in builder.architecture_families_from_requirement(schema)
    )


def test_coating_options_return_options_when_coating_enabled():
    schema = merge_requirement_schema_v2(
        {"material_system_intent": {"allow_substrate_plus_coating": True}}
    )

    options = builder.coating_options_from_requirement(schema)

    assert "thermal_barrier_coating" in options
    assert "environmental_barrier_coating" in options
    assert "oxidation_protection_coating" in options
    assert "bond_coat_interface_system" in options


def test_coating_options_include_wear_when_context_suggests_contact_damage():
    schema = merge_requirement_schema_v2(
        {
            "material_system_intent": {"allow_substrate_plus_coating": True},
            "active_criteria": ["contact_damage_resistance"],
        }
    )

    assert "wear_resistant_coating" in builder.coating_options_from_requirement(schema)


def test_gradient_options_map_surface_to_core_and_coating_alternative_intent():
    schema = merge_requirement_schema_v2(
        {
            "material_system_intent": {"allow_spatial_gradients": True},
            "spatial_property_intent": {
                "surface_to_core_property_needs": True,
                "coating_replacement_allowed": True,
                "gradient_as_coating_alternative": True,
            },
        }
    )

    options = builder.gradient_options_from_requirement(schema)

    assert "surface_oxidation_gradient" in options
    assert "thermal_barrier_gradient" in options
    assert "tough_core_hard_surface_gradient" in options


def test_gradient_options_map_local_zone_intent_to_local_zone_and_wear_gradients():
    schema = merge_requirement_schema_v2(
        {
            "material_system_intent": {"allow_spatial_gradients": True},
            "spatial_property_intent": {"local_zone_requirements": True},
        }
    )

    options = builder.gradient_options_from_requirement(schema)

    assert "local_zone_property_gradient" in options
    assert "surface_wear_gradient" in options


def test_process_routes_include_am_routes_when_gradients_are_enabled():
    schema = merge_requirement_schema_v2(
        {"material_system_intent": {"allow_spatial_gradients": True}}
    )

    routes = builder.process_routes_from_requirement(schema)

    assert "additive_manufacturing" in routes
    assert "directed_energy_deposition" in routes
    assert "laser_powder_bed_fusion" in routes


def test_process_routes_include_cvi_and_pip_for_composite_architecture():
    schema = merge_requirement_schema_v2(
        {"material_system_intent": {"allow_composite_architecture": True}}
    )

    routes = builder.process_routes_from_requirement(schema)

    assert "cvi" in routes
    assert "pip" in routes


def test_active_criteria_families_include_cost_and_sustainability_from_priorities():
    schema = merge_requirement_schema_v2(
        {
            "cost_priorities": {"lifecycle_cost": True},
            "sustainability_priorities": {"embodied_carbon": True},
        }
    )

    families = builder.active_criteria_families_from_requirement(schema)

    assert "through_life_cost" in families
    assert "sustainability" in families


def test_active_criteria_families_include_model_confidence_when_model_support_enabled():
    schema = merge_requirement_schema_v2(
        {"model_support_intent": {"allow_computational_models": True}}
    )

    assert "model_confidence" in builder.active_criteria_families_from_requirement(schema)


def test_active_criteria_families_include_measurement_feedback_readiness():
    schema = merge_requirement_schema_v2(
        {"measurement_feedback_intent": {"allow_measurement_feedback": True}}
    )

    assert (
        "measurement_feedback_readiness"
        in builder.active_criteria_families_from_requirement(schema)
    )


def test_optimisation_permissions_map_refinement_permissions():
    schema = merge_requirement_schema_v2(
        {
            "optimisation_intent": {
                "allow_deterministic_refinements": True,
                "allow_coating_refinements": True,
                "allow_gradient_refinements": True,
            }
        }
    )

    permissions = builder.optimisation_permissions_from_requirement(schema)

    assert permissions["deterministic_refinements_allowed"] is True
    assert permissions["coating_refinements_allowed"] is True
    assert permissions["gradient_refinements_allowed"] is True


def test_model_permissions_map_computational_surrogate_and_property_prediction():
    schema = merge_requirement_schema_v2(
        {
            "model_support_intent": {
                "allow_computational_models": True,
                "allow_surrogate_models": True,
                "allow_property_prediction": True,
            }
        }
    )

    permissions = builder.model_permissions_from_requirement(schema)

    assert permissions["computational_models"] is True
    assert permissions["surrogate_models"] is True
    assert permissions["property_prediction"] is True


def test_measurement_permissions_map_provenance_and_traceability():
    schema = merge_requirement_schema_v2(
        {
            "measurement_feedback_intent": {
                "require_measurement_provenance": True,
                "require_before_after_traceability": True,
            }
        }
    )

    permissions = builder.measurement_permissions_from_requirement(schema)

    assert permissions["measurement_provenance_required"] is True
    assert permissions["before_after_traceability_required"] is True


def test_build_design_space_from_requirement_does_not_mutate_input_schema():
    schema = hot_section_demo_requirement_schema_v2()
    original = deepcopy(schema)

    builder.build_design_space_from_requirement(schema)

    assert schema == original


def test_build_design_space_sets_coating_vs_gradient_comparison_when_both_exist():
    design_space = builder.build_design_space_from_requirement(
        hot_section_demo_requirement_schema_v2()
    )

    assert design_space["coating_vs_gradient_comparison_required"] is True


def test_build_design_space_sets_spatial_property_optimisation_for_gradients():
    schema = merge_requirement_schema_v2(
        {"material_system_intent": {"allow_spatial_gradients": True}}
    )

    design_space = builder.build_design_space_from_requirement(schema)

    assert design_space["spatial_property_optimisation_required"] is True


def test_validate_design_space_returns_valid_for_hot_section_demo_with_warnings_allowed():
    result = builder.validate_design_space(builder.hot_section_demo_design_space())

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_design_space_errors_on_unknown_architecture_family():
    design_space = builder.hot_section_demo_design_space()
    design_space["allowed_architecture_families"].append("unknown_architecture")

    result = builder.validate_design_space(design_space)

    assert result["is_valid"] is False
    assert (
        "allowed_architecture_families contains unsupported value: unknown_architecture."
        in result["errors"]
    )


def test_validate_design_space_warns_when_generative_suggestions_without_research_mode():
    design_space = builder.hot_section_demo_design_space()
    design_space["model_permissions"]["generative_research_suggestions"] = True
    design_space["research_mode_allowed"] = False

    result = builder.validate_design_space(design_space)

    assert (
        "Generative research suggestions are enabled, but research mode is not allowed."
        in result["warnings"]
    )


def test_validate_design_space_warns_when_feedback_without_measurement_provenance():
    design_space = builder.hot_section_demo_design_space()
    design_space["measurement_feedback_allowed"] = True
    design_space["measurement_permissions"]["measurement_provenance_required"] = False

    result = builder.validate_design_space(design_space)

    assert (
        "Measurement feedback is allowed, but measurement provenance is not required."
        in result["warnings"]
    )


def test_design_space_summary_returns_counts_and_booleans():
    design_space = builder.hot_section_demo_design_space()

    summary = builder.design_space_summary(design_space)

    assert summary["schema_version"] == builder.DESIGN_SPACE_SCHEMA_VERSION
    assert summary["architecture_family_count"] > 0
    assert summary["coating_option_count"] > 0
    assert summary["gradient_option_count"] > 0
    assert summary["coating_vs_gradient_comparison_required"] is True
    assert summary["research_mode_allowed"] is False


def test_hot_section_demo_design_space_includes_alternatives_and_no_research_mode():
    design_space = builder.hot_section_demo_design_space()

    assert "substrate_plus_coating_system" in design_space["allowed_architecture_families"]
    assert "coating_enabled_system" in design_space["allowed_architecture_families"]
    assert "cmc_system" in design_space["allowed_architecture_families"]
    assert "spatially_graded_am_system" in design_space["allowed_architecture_families"]
    assert "thermal_barrier_coating" in design_space["allowed_coating_options"]
    assert "environmental_barrier_coating" in design_space["allowed_coating_options"]
    assert "oxidation_protection_coating" in design_space["allowed_coating_options"]
    assert "surface_oxidation_gradient" in design_space["allowed_gradient_options"]
    assert "thermal_barrier_gradient" in design_space["allowed_gradient_options"]
    assert "directed_energy_deposition" in design_space["allowed_process_routes"]
    assert "laser_powder_bed_fusion" in design_space["allowed_process_routes"]
    assert design_space["research_mode_allowed"] is False


def test_hot_section_demo_design_space_allows_computational_model_support():
    design_space = builder.hot_section_demo_design_space()

    assert design_space["computational_model_support_allowed"] is True


def test_design_space_builder_does_not_import_forbidden_modules():
    source = Path("src/design_space_builder.py").read_text(encoding="utf-8")
    forbidden = [
        "import app",
        "from app",
        "import streamlit",
        "from streamlit",
        "phase6_decision_cockpit_prototype",
        "import src.phase5_",
        "from src.phase5_",
        "import phase5_",
        "from phase5_",
    ]

    assert not [snippet for snippet in forbidden if snippet in source]


def test_design_space_outputs_contain_no_approval_or_certification_claim_fields():
    outputs = [
        builder.build_design_space_from_requirement(default_requirement_schema_v2()),
        builder.hot_section_demo_design_space(),
    ]
    forbidden_fields = {"certification_approval", "qualification_approval"}

    for output in outputs:
        assert not forbidden_fields.intersection(_walk_keys_and_values(output))
