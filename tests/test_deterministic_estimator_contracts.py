from copy import deepcopy
from pathlib import Path

import src.deterministic_estimator_contracts as contracts
from src.candidate_criteria_valuation import (
    hot_section_demo_candidate_criteria_valuation_plan,
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
    assert contracts.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_slugify_identifier_creates_safe_lowercase_ids():
    assert contracts.slugify_identifier("Work Item / Estimator") == "work_item_estimator"
    assert contracts.slugify_identifier("!!!") == "unknown"


def test_estimator_label_returns_readable_label_and_unknown_fallback():
    assert (
        contracts.estimator_label("thermal_environment_rule_estimator")
        == "Thermal environment rule estimator"
    )
    assert contracts.estimator_label("new_estimator") == "New estimator"


def test_preferred_estimator_maps_temperature_capability():
    assert (
        contracts.preferred_estimator_id_for_criterion("temperature_capability")
        == "thermal_environment_rule_estimator"
    )


def test_preferred_estimator_maps_gradient_transition_risk():
    assert (
        contracts.preferred_estimator_id_for_criterion("gradient_transition_risk")
        == "gradient_feasibility_rule_estimator"
    )


def test_estimator_capability_sets_contract_only_flags():
    capability = contracts.estimator_capability("manufacturability_rule_estimator")

    assert capability["deterministic_only"] is True
    assert capability["live_model_call_allowed"] is False
    assert capability["live_source_retrieval_allowed"] is False
    assert capability["implementation_status"] == "contract_only"


def test_estimator_capabilities_returns_one_record_per_estimator_id():
    capabilities = contracts.estimator_capabilities()

    assert len(capabilities) == len(contracts.DETERMINISTIC_ESTIMATOR_IDS)
    assert [capability["estimator_id"] for capability in capabilities] == list(
        contracts.DETERMINISTIC_ESTIMATOR_IDS
    )


def test_work_item_supports_deterministic_estimation_for_hot_section_item():
    work_item = hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]

    assert contracts.work_item_supports_deterministic_estimation(work_item) is True


def test_work_item_supports_deterministic_estimation_false_for_blocked_item():
    work_item = hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]
    work_item["valuation_status"] = "blocked_invalid_candidate"

    assert contracts.work_item_supports_deterministic_estimation(work_item) is False


def test_estimator_request_id_for_creates_stable_id():
    assert contracts.estimator_request_id_for("work 1", "estimator/A") == (
        "deterministic_work_1_estimator_a"
    )


def test_estimator_request_for_work_item_creates_planned_request_with_live_flags_false():
    work_item = hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]

    request = contracts.estimator_request_for_work_item(work_item)

    assert request["request_status"] == "planned"
    assert request["live_model_call_allowed"] is False
    assert request["live_source_retrieval_allowed"] is False


def test_estimator_request_for_work_item_does_not_mutate_work_item():
    work_item = hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]
    original = deepcopy(work_item)

    contracts.estimator_request_for_work_item(work_item)

    assert work_item == original


def test_estimator_requests_from_plan_creates_one_request_per_work_item():
    plan = hot_section_demo_candidate_criteria_valuation_plan()

    requests = contracts.estimator_requests_from_valuation_plan(plan)

    assert len(requests) == len(plan["work_items"])


def test_placeholder_result_for_request_creates_placeholder_with_live_flags_false():
    request = contracts.estimator_requests_from_valuation_plan(
        hot_section_demo_candidate_criteria_valuation_plan()
    )[0]

    result = contracts.placeholder_result_for_request(request)

    assert result["result_status"] == "placeholder_only"
    assert result["live_model_call_allowed"] is False
    assert result["live_source_retrieval_allowed"] is False


def test_placeholder_result_reuses_or_creates_valid_criterion_value():
    request = contracts.estimator_requests_from_valuation_plan(
        hot_section_demo_candidate_criteria_valuation_plan()
    )[0]

    result = contracts.placeholder_result_for_request(request)

    assert result["criterion_value"]["schema_version"] == contracts.CRITERION_VALUE_SCHEMA_VERSION


def test_build_contract_plan_does_not_mutate_candidate_criteria_plan():
    plan = hot_section_demo_candidate_criteria_valuation_plan()
    original = deepcopy(plan)

    contracts.build_deterministic_estimator_contract_plan(plan)

    assert plan == original


def test_build_contract_plan_disables_live_flags():
    plan = contracts.hot_section_demo_deterministic_estimator_contract_plan()

    assert plan["live_model_call_allowed"] is False
    assert plan["live_source_retrieval_allowed"] is False


def test_build_contract_plan_creates_placeholder_results():
    plan = contracts.hot_section_demo_deterministic_estimator_contract_plan()

    assert plan["estimator_request_count"] == len(plan["estimator_requests"])
    assert plan["placeholder_result_count"] == len(plan["placeholder_results"])


def test_validate_estimator_request_validates_hot_section_request():
    request = contracts.hot_section_demo_deterministic_estimator_contract_plan()[
        "estimator_requests"
    ][0]

    result = contracts.validate_estimator_request(request)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_estimator_request_errors_if_live_model_call_true():
    request = contracts.hot_section_demo_deterministic_estimator_contract_plan()[
        "estimator_requests"
    ][0]
    request["live_model_call_allowed"] = True

    result = contracts.validate_estimator_request(request)

    assert result["is_valid"] is False
    assert "live_model_call_allowed must be false." in result["errors"]


def test_validate_estimator_request_errors_for_forbidden_claim_fields():
    request = contracts.hot_section_demo_deterministic_estimator_contract_plan()[
        "estimator_requests"
    ][0]
    request["certification_approval"] = True

    result = contracts.validate_estimator_request(request)

    assert result["is_valid"] is False
    assert any("Forbidden approval or certification" in error for error in result["errors"])


def test_validate_estimator_result_validates_hot_section_placeholder_result():
    result_record = contracts.hot_section_demo_deterministic_estimator_contract_plan()[
        "placeholder_results"
    ][0]

    result = contracts.validate_estimator_result(result_record)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_estimator_result_errors_if_live_source_retrieval_true():
    result_record = contracts.hot_section_demo_deterministic_estimator_contract_plan()[
        "placeholder_results"
    ][0]
    result_record["live_source_retrieval_allowed"] = True

    result = contracts.validate_estimator_result(result_record)

    assert result["is_valid"] is False
    assert "live_source_retrieval_allowed must be false." in result["errors"]


def test_validate_contract_plan_validates_hot_section_demo():
    result = contracts.validate_deterministic_estimator_contract_plan(
        contracts.hot_section_demo_deterministic_estimator_contract_plan()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_contract_plan_errors_if_plan_live_model_call_true():
    plan = contracts.hot_section_demo_deterministic_estimator_contract_plan()
    plan["live_model_call_allowed"] = True

    result = contracts.validate_deterministic_estimator_contract_plan(plan)

    assert result["is_valid"] is False
    assert "live_model_call_allowed must be false." in result["errors"]


def test_deterministic_estimator_contract_summary_returns_counts_and_live_flags():
    plan = contracts.hot_section_demo_deterministic_estimator_contract_plan()

    summary = contracts.deterministic_estimator_contract_summary(plan)

    assert summary["schema_version"] == (
        contracts.DETERMINISTIC_ESTIMATOR_CONTRACT_PLAN_SCHEMA_VERSION
    )
    assert summary["estimator_capability_count"] == len(
        contracts.DETERMINISTIC_ESTIMATOR_IDS
    )
    assert summary["estimator_request_count"] == len(plan["estimator_requests"])
    assert summary["placeholder_result_count"] == len(plan["placeholder_results"])
    assert summary["deterministic_estimation_allowed"] is True
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False


def test_hot_section_demo_plan_includes_expected_criteria_requests():
    plan = contracts.hot_section_demo_deterministic_estimator_contract_plan()
    criteria = {request["criterion_id"] for request in plan["estimator_requests"]}

    assert {
        "temperature_capability",
        "oxidation_resistance",
        "coating_spallation_risk",
        "gradient_transition_risk",
        "lifecycle_cost",
        "embodied_carbon",
    } <= criteria


def test_hot_section_demo_plan_has_placeholder_results_only():
    plan = contracts.hot_section_demo_deterministic_estimator_contract_plan()

    assert {result["result_status"] for result in plan["placeholder_results"]} == {
        "placeholder_only"
    }


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(
            contracts.hot_section_demo_deterministic_estimator_contract_plan()
        )
    )


def test_deterministic_estimator_contracts_does_not_import_forbidden_modules():
    source = Path("src/deterministic_estimator_contracts.py").read_text(encoding="utf-8")
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


def test_deterministic_estimator_contracts_do_not_call_io_network_or_process_tools():
    source = Path("src/deterministic_estimator_contracts.py").read_text(encoding="utf-8")
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
