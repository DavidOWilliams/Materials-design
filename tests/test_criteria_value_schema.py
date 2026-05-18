from copy import deepcopy
from pathlib import Path

import src.criteria_value_schema as schema
from src.candidate_normalisation_contracts import (
    hot_section_demo_candidate_normalisation_plan,
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
    assert schema.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_criterion_family_maps_temperature_capability():
    assert schema.criterion_family("temperature_capability") == "functional_performance"


def test_criterion_family_maps_gradient_transition_risk():
    assert (
        schema.criterion_family("gradient_transition_risk")
        == "gradient_specific_feasibility"
    )


def test_criterion_label_returns_readable_label_and_unknown_fallback():
    assert schema.criterion_label("oxidation_resistance") == "Oxidation resistance"
    assert schema.criterion_label("new_criterion") == "New criterion"


def test_criterion_definition_includes_qualitative_and_pending_value_types():
    definition = schema.criterion_definition("temperature_capability")

    assert "qualitative_band" in definition["value_types"]
    assert "pending" in definition["value_types"]


def test_criterion_definition_sets_lower_is_better_for_cost_and_risk():
    assert schema.criterion_definition("lifecycle_cost")["higher_is_better"] is False
    assert schema.criterion_definition("qualification_risk")["higher_is_better"] is False


def test_criteria_registry_preserves_requested_order_and_removes_duplicates():
    registry = schema.criteria_registry(
        ["lifecycle_cost", "oxidation_resistance", "lifecycle_cost"]
    )

    assert [definition["criterion_id"] for definition in registry] == [
        "lifecycle_cost",
        "oxidation_resistance",
    ]


def test_evidence_basis_record_normalises_unknown_source_type_and_confidence():
    record = schema.evidence_basis_record("new_source", confidence="certain")

    assert record["source_type"] == "unknown"
    assert record["confidence"] == "unknown"


def test_uncertainty_record_creates_reducible_uncertainty_record():
    record = schema.uncertainty_record(
        "sparse_data", description="Sparse evidence", uncertainty_level="high"
    )

    assert record["driver_id"] == "sparse_data"
    assert record["uncertainty_level"] == "high"
    assert record["reducible_by_evidence"] is True


def test_model_provenance_record_forces_live_call_allowed_false():
    record = schema.model_provenance_record(
        "model-1", model_name="Placeholder", live_call_allowed=True
    )

    assert record["live_call_allowed"] is False


def test_recommended_evidence_action_returns_label_and_priority():
    action = schema.recommended_evidence_action(
        "oxidation_test", label="Oxidation test", priority="high"
    )

    assert action["label"] == "Oxidation test"
    assert action["priority"] == "high"


def test_criterion_value_placeholder_creates_pending_record_with_evidence_basis():
    value = schema.criterion_value_placeholder(
        "candidate-1", "oxidation_resistance"
    )

    assert value["schema_version"] == schema.CRITERION_VALUE_SCHEMA_VERSION
    assert value["value_type"] == "pending"
    assert value["estimated_value"] == "pending"
    assert value["evidence_basis"]


def test_criterion_values_for_candidate_creates_one_placeholder_per_criterion():
    values = schema.criterion_values_for_candidate(
        "candidate-1", ["oxidation_resistance", "lifecycle_cost"]
    )

    assert [value["criterion_id"] for value in values] == [
        "oxidation_resistance",
        "lifecycle_cost",
    ]


def test_active_criteria_from_normalisation_plan_uses_plan_or_defaults():
    hot_section = schema.active_criteria_from_normalisation_plan(
        hot_section_demo_candidate_normalisation_plan()
    )
    defaults = schema.active_criteria_from_normalisation_plan({})

    assert "oxidation_resistance" in hot_section
    assert list(schema.DEFAULT_HOT_SECTION_CRITERIA) == defaults


def test_criteria_value_placeholders_from_normalisation_plan_use_candidate_placeholder():
    values = schema.criteria_value_placeholders_from_normalisation_plan(
        hot_section_demo_candidate_normalisation_plan()
    )

    assert values
    assert {value["candidate_id"] for value in values} == {"candidate_placeholder"}


def test_build_criteria_valuation_plan_does_not_mutate_normalisation_plan():
    normalisation_plan = hot_section_demo_candidate_normalisation_plan()
    original = deepcopy(normalisation_plan)

    schema.build_criteria_valuation_plan(normalisation_plan)

    assert normalisation_plan == original


def test_build_criteria_valuation_plan_sets_live_model_call_false():
    plan = schema.build_criteria_valuation_plan(
        hot_section_demo_candidate_normalisation_plan()
    )

    assert plan["live_model_call_allowed"] is False


def test_build_criteria_valuation_plan_requires_confidence_uncertainty_and_evidence():
    plan = schema.build_criteria_valuation_plan(
        hot_section_demo_candidate_normalisation_plan()
    )

    assert plan["require_confidence"] is True
    assert plan["require_uncertainty"] is True
    assert plan["require_evidence_basis"] is True


def test_build_criteria_valuation_plan_requires_model_provenance_for_demo():
    plan = schema.build_criteria_valuation_plan(
        hot_section_demo_candidate_normalisation_plan()
    )

    assert plan["require_model_provenance"] is True


def test_validate_criterion_value_validates_placeholder_with_warnings_allowed():
    value = schema.criterion_value_placeholder("candidate-1", "oxidation_resistance")

    result = schema.validate_criterion_value(value)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert result["warnings"]


def test_validate_criterion_value_errors_if_model_provenance_allows_live_call():
    value = schema.criterion_value_placeholder("candidate-1", "oxidation_resistance")
    value["model_provenance"] = [{"model_id": "m1", "live_call_allowed": True}]

    result = schema.validate_criterion_value(value)

    assert result["is_valid"] is False
    assert any("live_call_allowed must be false" in error for error in result["errors"])


def test_validate_criterion_value_errors_for_forbidden_claim_fields():
    value = schema.criterion_value_placeholder("candidate-1", "oxidation_resistance")
    value["qualification_approval"] = True

    result = schema.validate_criterion_value(value)

    assert result["is_valid"] is False
    assert any("Forbidden approval or certification" in error for error in result["errors"])


def test_validate_criteria_valuation_plan_validates_hot_section_demo():
    result = schema.validate_criteria_valuation_plan(
        schema.hot_section_demo_criteria_valuation_plan()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_criteria_valuation_plan_errors_if_live_model_call_true():
    plan = schema.hot_section_demo_criteria_valuation_plan()
    plan["live_model_call_allowed"] = True

    result = schema.validate_criteria_valuation_plan(plan)

    assert result["is_valid"] is False
    assert "live_model_call_allowed must be false." in result["errors"]


def test_criteria_valuation_summary_returns_counts_and_live_flag():
    plan = schema.hot_section_demo_criteria_valuation_plan()

    summary = schema.criteria_valuation_summary(plan)

    assert summary["schema_version"] == schema.CRITERIA_VALUATION_PLAN_SCHEMA_VERSION
    assert summary["active_criteria_count"] == len(plan["active_criteria"])
    assert summary["criterion_definition_count"] == len(plan["criterion_definitions"])
    assert summary["criterion_value_placeholder_count"] == len(
        plan["criterion_value_placeholders"]
    )
    assert summary["live_model_call_allowed"] is False


def test_hot_section_demo_plan_includes_expected_hot_section_criteria():
    plan = schema.hot_section_demo_criteria_valuation_plan()
    active_criteria = set(plan["active_criteria"])

    expected = {
        "temperature_capability",
        "oxidation_resistance",
        "coating_spallation_risk",
        "gradient_transition_risk",
        "manufacturability",
        "lifecycle_cost",
        "embodied_carbon",
        "qualification_risk",
    }

    assert expected <= active_criteria
    assert plan["require_confidence"] is True
    assert plan["require_uncertainty"] is True
    assert plan["require_evidence_basis"] is True
    assert plan["require_model_provenance"] is True
    assert plan["live_model_call_allowed"] is False


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(schema.hot_section_demo_criteria_valuation_plan())
    )


def test_criteria_value_schema_does_not_import_forbidden_modules():
    source = Path("src/criteria_value_schema.py").read_text(encoding="utf-8")
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


def test_criteria_value_schema_does_not_call_io_network_or_process_tools():
    source = Path("src/criteria_value_schema.py").read_text(encoding="utf-8")
    forbidden = [
        "open(",
        "Path",
        "import requests",
        "from requests",
        "requests.get(",
        "requests.post(",
        "requests.Session",
        "subprocess",
        "write_text",
        "write_bytes",
        "urlopen",
        "socket",
    ]

    assert not [snippet for snippet in forbidden if snippet in source]
