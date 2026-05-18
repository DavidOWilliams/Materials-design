from copy import deepcopy
from pathlib import Path

import src.material_system_scope_planner as planner


def _ids(records, id_field):
    return [record[id_field] for record in records]


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
    assert planner.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_candidate_generators_include_hot_section_core_generators():
    design_space = planner.hot_section_demo_design_space()

    generator_ids = _ids(
        planner.candidate_generators_from_design_space(design_space), "generator_id"
    )

    assert "metallic_reference_generator" in generator_ids
    assert "cmc_reference_generator" in generator_ids
    assert "coating_component_generator" in generator_ids
    assert "gradient_template_generator" in generator_ids


def test_candidate_generators_do_not_include_research_generator_when_research_false():
    design_space = planner.hot_section_demo_design_space()

    generator_ids = _ids(
        planner.candidate_generators_from_design_space(design_space), "generator_id"
    )

    assert "research_mode_candidate_generator" not in generator_ids


def test_candidate_generators_include_research_generator_only_when_allowed():
    design_space = planner.hot_section_demo_design_space()
    design_space["allowed_architecture_families"].append("research_generated_system")
    design_space["research_mode_allowed"] = True

    generator_ids = _ids(
        planner.candidate_generators_from_design_space(design_space), "generator_id"
    )

    assert "research_mode_candidate_generator" in generator_ids


def test_system_assemblers_include_hot_section_assemblers():
    design_space = planner.hot_section_demo_design_space()

    assembler_ids = _ids(
        planner.system_assemblers_from_design_space(design_space), "assembler_id"
    )

    assert "substrate_plus_coating_assembler" in assembler_ids
    assert "cmc_ebc_system_assembler" in assembler_ids
    assert "spatially_graded_am_system_assembler" in assembler_ids


def test_system_assemblers_do_not_include_research_wrapper_when_research_false():
    design_space = planner.hot_section_demo_design_space()

    assembler_ids = _ids(
        planner.system_assemblers_from_design_space(design_space), "assembler_id"
    )

    assert "research_generated_system_wrapper" not in assembler_ids


def test_source_plan_includes_hot_section_core_sources():
    design_space = planner.hot_section_demo_design_space()

    source_ids = _ids(planner.source_plan_from_design_space(design_space), "source_id")

    assert "coating_reference_sources" in source_ids
    assert "gradient_template_sources" in source_ids
    assert "process_route_sources" in source_ids
    assert "criteria_reference_sources" in source_ids
    assert "evidence_maturity_sources" in source_ids
    assert "model_estimate_sources" in source_ids


def test_source_plan_includes_measurement_feedback_sources_only_when_allowed():
    design_space = planner.hot_section_demo_design_space()
    source_ids = _ids(planner.source_plan_from_design_space(design_space), "source_id")
    assert "measurement_feedback_sources" not in source_ids

    design_space["measurement_feedback_allowed"] = True
    design_space["measurement_permissions"]["measurement_feedback"] = True
    source_ids = _ids(planner.source_plan_from_design_space(design_space), "source_id")
    assert "measurement_feedback_sources" in source_ids


def test_criteria_scope_requires_model_records_when_model_support_allowed():
    design_space = planner.hot_section_demo_design_space()

    scope = planner.criteria_valuation_scope_from_design_space(design_space)

    assert scope["require_confidence"] is True
    assert scope["require_uncertainty"] is True
    assert scope["require_evidence_basis"] is True
    assert scope["require_model_provenance"] is True


def test_criteria_scope_carries_measurement_provenance_and_traceability_flags():
    design_space = planner.hot_section_demo_design_space()

    scope = planner.criteria_valuation_scope_from_design_space(design_space)

    assert scope["require_measurement_provenance"] is True
    assert scope["require_before_after_traceability"] is True


def test_optimisation_scope_preserves_key_permissions():
    design_space = planner.hot_section_demo_design_space()

    scope = planner.optimisation_scope_from_design_space(design_space)

    assert scope["optimise_existing_candidates_first"] is True
    assert scope["coating_refinements_allowed"] is True
    assert scope["gradient_refinements_allowed"] is True


def test_model_adapter_scope_keeps_all_live_calls_disabled():
    design_space = planner.hot_section_demo_design_space()

    adapters = planner.model_adapter_scope_from_design_space(design_space)

    assert adapters
    assert all(adapter["live_call_allowed"] is False for adapter in adapters)


def test_model_adapter_scope_enables_hot_section_model_adapters():
    design_space = planner.hot_section_demo_design_space()

    adapters = {
        adapter["adapter_id"]: adapter
        for adapter in planner.model_adapter_scope_from_design_space(design_space)
    }

    assert adapters["computational_model_adapter"]["enabled"] is True
    assert adapters["surrogate_model_adapter"]["enabled"] is True
    assert adapters["process_window_explorer_adapter"]["enabled"] is True
    assert adapters["property_prediction_adapter"]["enabled"] is True


def test_model_adapter_scope_blocks_generative_when_research_mode_false():
    design_space = planner.hot_section_demo_design_space()
    design_space["model_permissions"]["generative_research_suggestions"] = True
    design_space["research_mode_allowed"] = False

    adapters = {
        adapter["adapter_id"]: adapter
        for adapter in planner.model_adapter_scope_from_design_space(design_space)
    }

    assert adapters["generative_research_suggestion_adapter"]["enabled"] is False
    assert (
        adapters["generative_research_suggestion_adapter"]["reason"]
        == "Research mode is not allowed."
    )


def test_measurement_feedback_scope_maps_measurement_flags():
    design_space = planner.hot_section_demo_design_space()
    design_space["measurement_permissions"]["measurement_feedback"] = True
    design_space["measurement_permissions"]["test_result_ingestion"] = True
    design_space["measurement_permissions"]["model_confidence_update"] = True
    design_space["measurement_permissions"]["active_learning_suggestions"] = True

    scope = planner.measurement_feedback_scope_from_design_space(design_space)

    assert scope["measurement_feedback_allowed"] is True
    assert scope["test_result_ingestion_allowed"] is True
    assert scope["model_confidence_update_allowed"] is True
    assert scope["active_learning_suggestions_allowed"] is True
    assert scope["measurement_provenance_required"] is True
    assert scope["before_after_traceability_required"] is True


def test_build_scope_plan_from_design_space_does_not_mutate_input_design_space():
    design_space = planner.hot_section_demo_design_space()
    original = deepcopy(design_space)

    planner.build_scope_plan_from_design_space(design_space)

    assert design_space == original


def test_build_scope_plan_includes_expected_hot_section_scope_items():
    scope_plan = planner.hot_section_demo_scope_plan()

    generator_ids = _ids(scope_plan["candidate_generators"], "generator_id")
    assembler_ids = _ids(scope_plan["system_assemblers"], "assembler_id")
    source_ids = _ids(scope_plan["source_plan"], "source_id")

    assert "metallic_reference_generator" in generator_ids
    assert "cmc_reference_generator" in generator_ids
    assert "coating_component_generator" in generator_ids
    assert "gradient_template_generator" in generator_ids
    assert "substrate_plus_coating_assembler" in assembler_ids
    assert "cmc_ebc_system_assembler" in assembler_ids
    assert "spatially_graded_am_system_assembler" in assembler_ids
    assert "coating_reference_sources" in source_ids
    assert "gradient_template_sources" in source_ids
    assert "model_estimate_sources" in source_ids


def test_validate_scope_plan_returns_valid_for_hot_section_demo_with_warnings_allowed():
    result = planner.validate_scope_plan(planner.hot_section_demo_scope_plan())

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_scope_plan_errors_if_unknown_generator_id_is_present():
    scope_plan = planner.hot_section_demo_scope_plan()
    scope_plan["candidate_generators"].append(
        planner.generator_scope(
            "unknown_generator",
            label="Unknown generator",
            architecture_families=[],
        )
    )

    result = planner.validate_scope_plan(scope_plan)

    assert result["is_valid"] is False
    assert (
        "candidate_generators contains unsupported generator_id: unknown_generator."
        in result["errors"]
    )


def test_validate_scope_plan_errors_if_model_adapter_allows_live_call():
    scope_plan = planner.hot_section_demo_scope_plan()
    scope_plan["model_adapter_scope"][0]["live_call_allowed"] = True

    result = planner.validate_scope_plan(scope_plan)

    assert result["is_valid"] is False
    assert any("live_call_allowed must be false" in error for error in result["errors"])


def test_scope_plan_summary_returns_counts_and_no_live_model_calls():
    summary = planner.scope_plan_summary(planner.hot_section_demo_scope_plan())

    assert summary["schema_version"] == planner.SCOPE_PLAN_SCHEMA_VERSION
    assert summary["candidate_generator_count"] > 0
    assert summary["enabled_candidate_generator_count"] > 0
    assert summary["system_assembler_count"] > 0
    assert summary["enabled_system_assembler_count"] > 0
    assert summary["source_count"] > 0
    assert summary["live_model_call_count"] == 0


def test_hot_section_demo_scope_plan_flags_comparison_and_research_mode():
    scope_plan = planner.hot_section_demo_scope_plan()

    assert scope_plan["coating_vs_gradient_comparison_required"] is True
    assert scope_plan["research_mode_allowed"] is False


def test_hot_section_demo_scope_plan_has_no_approval_or_certification_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(planner.hot_section_demo_scope_plan())
    )


def test_material_system_scope_planner_does_not_import_forbidden_modules():
    source = Path("src/material_system_scope_planner.py").read_text(encoding="utf-8")
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
