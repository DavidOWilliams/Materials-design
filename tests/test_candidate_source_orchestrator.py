from copy import deepcopy
from pathlib import Path

import src.candidate_source_orchestrator as orchestrator
from src.material_system_scope_planner import hot_section_demo_scope_plan


def _requests_by_id(plan):
    return {request["source_id"]: request for request in plan["source_requests"]}


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
    assert orchestrator.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_source_ids_from_scope_plan_returns_enabled_hot_section_source_ids():
    source_ids = orchestrator.source_ids_from_scope_plan(hot_section_demo_scope_plan())

    assert "metallic_reference_sources" in source_ids
    assert "cmc_reference_sources" in source_ids
    assert "coating_reference_sources" in source_ids
    assert "gradient_template_sources" in source_ids
    assert "model_estimate_sources" in source_ids


def test_source_request_type_maps_coating_to_component_reference():
    assert (
        orchestrator.source_request_type("coating_reference_sources")
        == "component_reference"
    )


def test_source_label_returns_readable_label_and_unknown_fallback():
    assert (
        orchestrator.source_label("metallic_reference_sources")
        == "Metallic reference sources"
    )
    assert orchestrator.source_label("new_source_id") == "New source id"


def test_source_purpose_returns_controlled_purpose_and_unknown_fallback():
    assert (
        orchestrator.source_purpose("model_estimate_sources")
        == "Reserve placeholder requests for future model-supported criterion estimates."
    )
    assert orchestrator.source_purpose("new_source_id") == (
        "No controlled purpose has been defined for this source yet."
    )


def test_source_request_sets_live_retrieval_allowed_false():
    request = orchestrator.source_request("metallic_reference_sources")

    assert request["live_retrieval_allowed"] is False


def test_source_request_normalises_unknown_status_to_planned():
    request = orchestrator.source_request("metallic_reference_sources", status="live")

    assert request["status"] == "planned"


def test_request_parameters_include_coating_options_for_coating_sources():
    params = orchestrator.request_parameters_for_source(
        "coating_reference_sources", hot_section_demo_scope_plan()
    )

    assert "thermal_barrier_coating" in params["coating_options_in_scope"]
    assert "coating_deposition" in params["process_routes_in_scope"]


def test_request_parameters_include_gradient_options_for_gradient_sources():
    params = orchestrator.request_parameters_for_source(
        "gradient_template_sources", hot_section_demo_scope_plan()
    )

    assert "surface_oxidation_gradient" in params["gradient_options_in_scope"]
    assert "directed_energy_deposition" in params["process_routes_in_scope"]


def test_request_parameters_include_enabled_model_adapter_ids_for_model_sources():
    params = orchestrator.request_parameters_for_source(
        "model_estimate_sources", hot_section_demo_scope_plan()
    )

    assert "computational_model_adapter" in params["enabled_model_adapter_ids"]
    assert "surrogate_model_adapter" in params["enabled_model_adapter_ids"]


def test_request_parameters_set_live_model_calls_false_for_model_sources():
    params = orchestrator.request_parameters_for_source(
        "model_estimate_sources", hot_section_demo_scope_plan()
    )

    assert params["live_model_call_allowed"] is False


def test_required_for_includes_comparison_for_coating_and_gradient_sources():
    scope_plan = hot_section_demo_scope_plan()

    assert "coating_vs_gradient_comparison" in orchestrator.required_for_for_source(
        "coating_reference_sources", scope_plan
    )
    assert "coating_vs_gradient_comparison" in orchestrator.required_for_for_source(
        "gradient_template_sources", scope_plan
    )


def test_source_requests_create_placeholder_for_model_estimate_sources():
    requests = _requests_by_id(
        {
            "source_requests": orchestrator.source_requests_from_scope_plan(
                hot_section_demo_scope_plan()
            )
        }
    )

    assert requests["model_estimate_sources"]["status"] == "placeholder_only"


def test_build_source_orchestration_plan_does_not_mutate_input_scope_plan():
    scope_plan = hot_section_demo_scope_plan()
    original = deepcopy(scope_plan)

    orchestrator.build_source_orchestration_plan(scope_plan)

    assert scope_plan == original


def test_build_source_orchestration_plan_disables_live_retrieval_and_model_calls():
    plan = orchestrator.build_source_orchestration_plan(hot_section_demo_scope_plan())

    assert plan["live_retrieval_allowed"] is False
    assert plan["live_model_call_allowed"] is False
    assert all(
        request["live_retrieval_allowed"] is False
        for request in plan["source_requests"]
    )


def test_validate_source_orchestration_plan_validates_hot_section_demo():
    result = orchestrator.validate_source_orchestration_plan(
        orchestrator.hot_section_demo_source_orchestration_plan()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_source_orchestration_plan_errors_for_plan_live_retrieval():
    plan = orchestrator.hot_section_demo_source_orchestration_plan()
    plan["live_retrieval_allowed"] = True

    result = orchestrator.validate_source_orchestration_plan(plan)

    assert result["is_valid"] is False
    assert "live_retrieval_allowed must be false." in result["errors"]


def test_validate_source_orchestration_plan_errors_for_request_live_retrieval():
    plan = orchestrator.hot_section_demo_source_orchestration_plan()
    plan["source_requests"][0]["live_retrieval_allowed"] = True

    result = orchestrator.validate_source_orchestration_plan(plan)

    assert result["is_valid"] is False
    assert any(
        "live_retrieval_allowed must be false" in error
        for error in result["errors"]
    )


def test_source_orchestration_summary_returns_counts_and_zero_live_flags():
    plan = orchestrator.hot_section_demo_source_orchestration_plan()

    summary = orchestrator.source_orchestration_summary(plan)

    assert summary["schema_version"] == orchestrator.SOURCE_ORCHESTRATION_SCHEMA_VERSION
    assert summary["source_request_count"] == len(plan["source_requests"])
    assert summary["enabled_request_count"] == len(plan["source_requests"])
    assert summary["model_placeholder_count"] == 1
    assert summary["live_retrieval_allowed"] is False
    assert summary["live_model_call_allowed"] is False


def test_hot_section_demo_plan_includes_expected_source_requests():
    requests = _requests_by_id(orchestrator.hot_section_demo_source_orchestration_plan())

    expected = {
        "metallic_reference_sources",
        "cmc_reference_sources",
        "coating_reference_sources",
        "gradient_template_sources",
        "process_route_sources",
        "criteria_reference_sources",
        "evidence_maturity_sources",
        "model_estimate_sources",
    }

    assert expected <= set(requests)
    assert "measurement_feedback_sources" not in requests


def test_hot_section_demo_plan_uses_placeholder_only_for_model_estimates():
    requests = _requests_by_id(orchestrator.hot_section_demo_source_orchestration_plan())

    assert requests["model_estimate_sources"]["status"] == "placeholder_only"


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(orchestrator.hot_section_demo_source_orchestration_plan())
    )


def test_candidate_source_orchestrator_does_not_import_forbidden_modules():
    source = Path("src/candidate_source_orchestrator.py").read_text(encoding="utf-8")
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


def test_candidate_source_orchestrator_does_not_call_io_network_or_process_tools():
    source = Path("src/candidate_source_orchestrator.py").read_text(encoding="utf-8")
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
