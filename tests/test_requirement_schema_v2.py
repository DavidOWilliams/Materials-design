from copy import deepcopy
from pathlib import Path

import src.requirement_schema_v2 as schema_v2


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


def test_default_requirement_schema_v2_returns_all_required_sections():
    schema = schema_v2.default_requirement_schema_v2()

    assert schema["schema_version"] == "requirement_schema_v2"
    for section_name in schema_v2.REQUIREMENT_SCHEMA_SECTIONS:
        assert section_name in schema


def test_default_schema_enables_existing_candidates_and_deterministic_refinements():
    schema = schema_v2.default_requirement_schema_v2()

    assert schema["optimisation_intent"]["optimise_existing_candidates_first"] is True
    assert schema["optimisation_intent"]["allow_deterministic_refinements"] is True


def test_default_schema_requires_confidence_uncertainty_and_evidence_basis():
    schema = schema_v2.default_requirement_schema_v2()

    assert schema["criteria_valuation_intent"]["include_confidence_bands"] is True
    assert schema["criteria_valuation_intent"]["include_uncertainty_drivers"] is True
    assert schema["criteria_valuation_intent"]["include_evidence_basis"] is True


def test_bool_section_returns_all_fields_with_requested_default():
    section = schema_v2.bool_section(("a", "b"), default=True)

    assert section == {"a": True, "b": True}


def test_normalise_bool_handles_bools_and_common_true_false_strings():
    assert schema_v2.normalise_bool(True) is True
    assert schema_v2.normalise_bool(False) is False
    for value in ["true", "yes", "1", "on"]:
        assert schema_v2.normalise_bool(value) is True
    for value in ["false", "no", "0", "off", "unknown", 1]:
        assert schema_v2.normalise_bool(value) is False


def test_normalise_bool_section_ignores_unknown_fields_and_fills_missing_fields():
    section = schema_v2.normalise_bool_section(
        "material_system_intent",
        {"allow_spatial_gradients": "yes", "unexpected": True},
    )

    assert "unexpected" not in section
    assert section["allow_spatial_gradients"] is True
    assert section["allow_bulk_material_only"] is False
    assert set(section) == set(schema_v2.MATERIAL_SYSTEM_INTENT_FIELDS)


def test_merge_requirement_schema_v2_does_not_mutate_overrides():
    overrides = {
        "material_system_intent": {"allow_bulk_material_only": "yes"},
        "active_criteria": ["temperature_capability"],
    }
    original = deepcopy(overrides)

    schema_v2.merge_requirement_schema_v2(overrides)

    assert overrides == original


def test_merge_requirement_schema_v2_applies_valid_boolean_overrides():
    schema = schema_v2.merge_requirement_schema_v2(
        {
            "material_system_intent": {"allow_substrate_plus_coating": "on"},
            "optimisation_intent": {"allow_gradient_refinements": "true"},
        }
    )

    assert schema["material_system_intent"]["allow_substrate_plus_coating"] is True
    assert schema["optimisation_intent"]["allow_gradient_refinements"] is True
    assert schema["optimisation_intent"]["optimise_existing_candidates_first"] is True


def test_merge_requirement_schema_v2_ignores_unknown_top_level_keys():
    schema = schema_v2.merge_requirement_schema_v2({"unknown": {"value": True}})

    assert "unknown" not in schema


def test_validate_requirement_schema_v2_returns_valid_for_default_schema_with_warnings_allowed():
    result = schema_v2.validate_requirement_schema_v2(
        schema_v2.default_requirement_schema_v2()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_requirement_schema_v2_returns_errors_when_required_sections_are_missing():
    schema = schema_v2.default_requirement_schema_v2()
    del schema["model_support_intent"]

    result = schema_v2.validate_requirement_schema_v2(schema)

    assert result["is_valid"] is False
    assert "model_support_intent must be a dictionary." in result["errors"]


def test_validate_requirement_schema_v2_warns_when_gradients_have_no_spatial_intent():
    schema = schema_v2.merge_requirement_schema_v2(
        {"material_system_intent": {"allow_spatial_gradients": True}}
    )

    result = schema_v2.validate_requirement_schema_v2(schema)

    assert (
        "Spatial gradients are allowed, but no spatial property intent is enabled."
        in result["warnings"]
    )


def test_validate_requirement_schema_v2_warns_when_model_refinements_have_no_model_family():
    schema = schema_v2.merge_requirement_schema_v2(
        {"optimisation_intent": {"allow_model_supported_refinements": True}}
    )

    result = schema_v2.validate_requirement_schema_v2(schema)

    assert (
        "Model-supported refinements are allowed, but no computational, surrogate, or specialist AI model family is enabled."
        in result["warnings"]
    )


def test_validate_requirement_schema_v2_warns_when_generative_suggestions_without_research_mode():
    schema = schema_v2.merge_requirement_schema_v2(
        {"model_support_intent": {"allow_generative_research_suggestions": True}}
    )

    result = schema_v2.validate_requirement_schema_v2(schema)

    assert (
        "Generative research suggestions are allowed, but research-mode candidates are disabled."
        in result["warnings"]
    )


def test_requirement_schema_summary_lists_enabled_intents():
    schema = schema_v2.merge_requirement_schema_v2(
        {
            "material_system_intent": {"allow_substrate_plus_coating": True},
            "active_criteria": ["oxidation_resistance", "lifecycle_cost"],
        }
    )

    summary = schema_v2.requirement_schema_summary(schema)

    assert "allow_substrate_plus_coating" in summary["enabled_material_system_intents"]
    assert summary["active_criteria_count"] == 2


def test_hot_section_demo_requirement_schema_v2_validates_without_errors():
    result = schema_v2.validate_requirement_schema_v2(
        schema_v2.hot_section_demo_requirement_schema_v2()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []


def test_hot_section_demo_enables_coating_and_gradient_but_not_research_mode():
    schema = schema_v2.hot_section_demo_requirement_schema_v2()

    assert schema["optimisation_intent"]["allow_coating_refinements"] is True
    assert schema["optimisation_intent"]["allow_gradient_refinements"] is True
    assert schema["material_system_intent"]["allow_research_mode_candidates"] is False


def test_hot_section_demo_includes_cost_and_sustainability_priorities():
    schema = schema_v2.hot_section_demo_requirement_schema_v2()

    assert schema["cost_priorities"]["lifecycle_cost"] is True
    assert schema["cost_priorities"]["qualification_cost"] is True
    assert schema["sustainability_priorities"]["embodied_carbon"] is True
    assert schema["sustainability_priorities"]["critical_materials"] is True


def test_hot_section_demo_includes_model_support_fields_for_future_model_phases():
    schema = schema_v2.hot_section_demo_requirement_schema_v2()

    assert schema["model_support_intent"]["allow_computational_models"] is True
    assert schema["model_support_intent"]["allow_surrogate_models"] is True
    assert schema["model_support_intent"]["allow_process_window_exploration"] is True
    assert schema["model_support_intent"]["allow_property_prediction"] is True
    assert schema["model_support_intent"]["require_model_provenance"] is True
    assert schema["model_support_intent"]["require_model_uncertainty"] is True


def test_hot_section_demo_includes_measurement_provenance_for_future_feedback_phases():
    schema = schema_v2.hot_section_demo_requirement_schema_v2()

    assert schema["measurement_feedback_intent"]["require_measurement_provenance"] is True
    assert schema["measurement_feedback_intent"]["require_before_after_traceability"] is True


def test_requirement_schema_v2_does_not_import_forbidden_modules():
    source = Path("src/requirement_schema_v2.py").read_text(encoding="utf-8")
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
        "from src.contracts",
        "import src.contracts",
    ]

    assert not [snippet for snippet in forbidden if snippet in source]


def test_schema_outputs_contain_no_approval_or_certification_claim_fields():
    outputs = [
        schema_v2.default_requirement_schema_v2(),
        schema_v2.hot_section_demo_requirement_schema_v2(),
    ]
    forbidden_fields = {"certification_approval", "qualification_approval"}

    for output in outputs:
        assert not forbidden_fields.intersection(_walk_keys_and_values(output))
