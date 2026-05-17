from __future__ import annotations

import copy
from pathlib import Path

from src.candidate_criteria_valuation import (
    hot_section_demo_candidate_criteria_valuation_plan,
)
from src.criteria_result_integration import (
    CANDIDATE_CRITERION_VALUE_SET_SCHEMA_VERSION,
    CRITERIA_RESULT_INTEGRATION_PLAN_SCHEMA_VERSION,
    INTEGRATED_VALUE_RECORD_SCHEMA_VERSION,
    build_criteria_result_integration_plan,
    candidate_ids_from_candidate_criteria_plan,
    candidate_placeholder_values_from_plan,
    candidate_value_set,
    candidate_value_sets_from_integrated_records,
    criterion_value_key,
    criterion_values_by_candidate_from_value_sets,
    criteria_result_integration_summary,
    estimator_result_id,
    fallback_integrated_records_from_placeholders,
    hot_section_demo_criteria_result_integration_plan,
    integrate_estimator_results,
    integrated_value_record_from_result,
    is_placeholder_criterion_value,
    slugify_identifier,
    unique_preserve_order,
    valid_estimator_results_from_plan,
    validate_candidate_value_set,
    validate_criteria_result_integration_plan,
    validate_integrated_value_record,
)
from src.deterministic_estimator_contracts import (
    hot_section_demo_deterministic_estimator_contract_plan,
)


def _candidate_plan() -> dict:
    return hot_section_demo_candidate_criteria_valuation_plan()


def _estimator_plan() -> dict:
    return hot_section_demo_deterministic_estimator_contract_plan()


def _first_result() -> dict:
    return copy.deepcopy(_estimator_plan()["placeholder_results"][0])


def _contains_forbidden_claim_field(value: object) -> bool:
    forbidden = {
        "certification_approval",
        "qualification_approval",
        "approved",
        "certified",
    }
    if isinstance(value, dict):
        return any(
            str(key) in forbidden or _contains_forbidden_claim_field(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_claim_field(item) for item in value)
    return False


def test_unique_preserve_order_removes_duplicates_and_preserves_order() -> None:
    assert unique_preserve_order(["a", "b", "a", "c"]) == ["a", "b", "c"]


def test_slugify_identifier_creates_safe_lowercase_ids() -> None:
    assert slugify_identifier("Hot Section / Candidate 1") == "hot_section_candidate_1"


def test_candidate_ids_from_candidate_criteria_plan_returns_hot_section_candidate_ids() -> None:
    assert candidate_ids_from_candidate_criteria_plan(_candidate_plan()) == [
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    ]


def test_criterion_value_key_creates_stable_key() -> None:
    assert criterion_value_key("candidate_a", "oxidation_resistance") == (
        "candidate_a::oxidation_resistance"
    )


def test_estimator_result_id_uses_estimator_request_id_when_present() -> None:
    result = {"estimator_request_id": "request_1", "candidate_id": "c"}
    assert estimator_result_id(result) == "request_1"


def test_is_placeholder_criterion_value_detects_pending_placeholders() -> None:
    assert is_placeholder_criterion_value({"value_type": "pending"}) is True
    assert is_placeholder_criterion_value({"estimated_value": "measured"}) is False


def test_candidate_placeholder_values_from_plan_returns_deep_copied_mapping() -> None:
    plan = _candidate_plan()
    values = candidate_placeholder_values_from_plan(plan)
    values["demo_metallic_candidate"][0]["estimated_value"] = "changed"

    original = plan["criterion_values_by_candidate"]["demo_metallic_candidate"][0]
    assert original["estimated_value"] == "pending"


def test_valid_estimator_results_from_plan_returns_valid_placeholder_results_for_hot_demo() -> None:
    valid_results, skipped_records = valid_estimator_results_from_plan(_estimator_plan())

    assert valid_results
    assert skipped_records == []
    assert all(result["result_status"] == "placeholder_only" for result in valid_results)


def test_integrated_value_record_from_result_creates_integrated_placeholder_with_trace() -> None:
    record = integrated_value_record_from_result(_first_result())

    assert record["schema_version"] == INTEGRATED_VALUE_RECORD_SCHEMA_VERSION
    assert record["integration_status"] == "integrated_placeholder"
    assert record["trace"]["source"] == "deterministic_estimator_contract"


def test_integrate_estimator_results_integrates_hot_section_placeholders() -> None:
    records, skipped = integrate_estimator_results(_candidate_plan(), _estimator_plan())

    assert records
    assert skipped == []
    assert all(record["integration_status"] == "integrated_placeholder" for record in records)


def test_integrate_estimator_results_skips_duplicate_candidate_criterion_after_first() -> None:
    estimator_plan = _estimator_plan()
    duplicate = copy.deepcopy(estimator_plan["placeholder_results"][0])
    duplicate["estimator_request_id"] = "duplicate_request"
    estimator_plan["placeholder_results"].append(duplicate)

    _, skipped = integrate_estimator_results(_candidate_plan(), estimator_plan)

    assert any(
        record["integration_status"] == "skipped_duplicate_result"
        for record in skipped
    )


def test_integrate_estimator_results_skips_missing_candidate_result() -> None:
    estimator_plan = _estimator_plan()
    estimator_plan["placeholder_results"] = [copy.deepcopy(estimator_plan["placeholder_results"][0])]
    estimator_plan["placeholder_results"][0]["candidate_id"] = "missing_candidate"

    records, skipped = integrate_estimator_results(_candidate_plan(), estimator_plan)

    assert records == []
    assert skipped[0]["integration_status"] == "skipped_missing_candidate"


def test_fallback_integrated_records_from_placeholders_creates_missing_value_records() -> None:
    fallback_records = fallback_integrated_records_from_placeholders(_candidate_plan(), [])

    assert fallback_records
    assert all(
        record["integration_status"] == "fallback_placeholder"
        for record in fallback_records
    )


def test_candidate_value_set_reports_placeholder_only_when_all_values_are_placeholders() -> None:
    record = integrated_value_record_from_result(_first_result())
    value_set = candidate_value_set(record["candidate_id"], [record])

    assert value_set["schema_version"] == CANDIDATE_CRITERION_VALUE_SET_SCHEMA_VERSION
    assert value_set["value_set_status"] == "placeholder_only"


def test_candidate_value_sets_from_integrated_records_preserves_candidate_order() -> None:
    records, _ = integrate_estimator_results(_candidate_plan(), _estimator_plan())
    candidate_ids = [
        "demo_spatial_gradient_system",
        "demo_metallic_candidate",
    ]

    value_sets = candidate_value_sets_from_integrated_records(candidate_ids, records)

    assert [value_set["candidate_id"] for value_set in value_sets] == candidate_ids


def test_criterion_values_by_candidate_from_value_sets_groups_values_by_candidate() -> None:
    records, _ = integrate_estimator_results(_candidate_plan(), _estimator_plan())
    value_sets = candidate_value_sets_from_integrated_records(
        candidate_ids_from_candidate_criteria_plan(_candidate_plan()), records
    )

    grouped = criterion_values_by_candidate_from_value_sets(value_sets)

    assert "demo_metallic_candidate" in grouped
    assert grouped["demo_metallic_candidate"]


def test_build_plan_does_not_mutate_candidate_or_estimator_plans() -> None:
    candidate_plan = _candidate_plan()
    estimator_plan = _estimator_plan()
    candidate_before = copy.deepcopy(candidate_plan)
    estimator_before = copy.deepcopy(estimator_plan)

    build_criteria_result_integration_plan(candidate_plan, estimator_plan)

    assert candidate_plan == candidate_before
    assert estimator_plan == estimator_before


def test_build_plan_sets_live_flags_false() -> None:
    plan = build_criteria_result_integration_plan(_candidate_plan(), _estimator_plan())

    assert plan["live_model_call_allowed"] is False
    assert plan["live_source_retrieval_allowed"] is False


def test_build_plan_creates_three_hot_section_candidate_value_sets() -> None:
    plan = build_criteria_result_integration_plan(_candidate_plan(), _estimator_plan())

    assert plan["candidate_count"] == 3
    assert len(plan["candidate_value_sets"]) == 3


def test_validate_integrated_value_record_returns_valid_for_hot_record_with_warnings_allowed() -> None:
    record = integrated_value_record_from_result(_first_result())

    validation = validate_integrated_value_record(record)

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_integrated_value_record_errors_if_forbidden_claim_fields_appear() -> None:
    record = integrated_value_record_from_result(_first_result())
    record["approved"] = True

    validation = validate_integrated_value_record(record)

    assert validation["is_valid"] is False
    assert any("Forbidden approval" in error for error in validation["errors"])


def test_validate_candidate_value_set_returns_valid_for_hot_value_set_with_warnings_allowed() -> None:
    plan = hot_section_demo_criteria_result_integration_plan()
    value_set = plan["candidate_value_sets"][0]

    validation = validate_candidate_value_set(value_set)

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_candidate_value_set_errors_when_criterion_count_mismatch() -> None:
    value_set = candidate_value_set("candidate_a", [])
    value_set["criterion_count"] = 1

    validation = validate_candidate_value_set(value_set)

    assert validation["is_valid"] is False
    assert any("criterion_count" in error for error in validation["errors"])


def test_validate_criteria_result_integration_plan_returns_valid_for_hot_demo_with_warnings_allowed() -> None:
    validation = validate_criteria_result_integration_plan(
        hot_section_demo_criteria_result_integration_plan()
    )

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_criteria_result_integration_plan_errors_if_live_model_call_allowed_true() -> None:
    plan = hot_section_demo_criteria_result_integration_plan()
    plan["live_model_call_allowed"] = True

    validation = validate_criteria_result_integration_plan(plan)

    assert validation["is_valid"] is False
    assert any("live_model_call_allowed" in error for error in validation["errors"])


def test_criteria_result_integration_summary_returns_counts_and_live_flags() -> None:
    plan = hot_section_demo_criteria_result_integration_plan()

    summary = criteria_result_integration_summary(plan)

    assert summary["schema_version"] == CRITERIA_RESULT_INTEGRATION_PLAN_SCHEMA_VERSION
    assert summary["candidate_count"] == 3
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False


def test_hot_section_demo_plan_contains_expected_hot_section_criteria_values() -> None:
    plan = hot_section_demo_criteria_result_integration_plan()
    criterion_ids = {
        value["criterion_id"]
        for values in plan["criterion_values_by_candidate"].values()
        for value in values
    }

    assert "temperature_capability" in criterion_ids
    assert "oxidation_resistance" in criterion_ids
    assert "coating_spallation_risk" in criterion_ids
    assert "gradient_transition_risk" in criterion_ids


def test_hot_section_demo_plan_has_populated_value_count_zero() -> None:
    plan = hot_section_demo_criteria_result_integration_plan()

    assert plan["populated_value_count"] == 0
    assert plan["placeholder_value_count"] == plan["integrated_value_count"]


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields() -> None:
    assert not _contains_forbidden_claim_field(
        hot_section_demo_criteria_result_integration_plan()
    )


def test_source_does_not_import_forbidden_runtime_modules() -> None:
    source = Path("src/criteria_result_integration.py").read_text()

    assert "import app" not in source
    assert "streamlit" not in source.lower()
    assert "phase6_decision_cockpit_prototype" not in source
    assert "phase5" not in source.lower()


def test_source_does_not_call_file_network_or_process_functions() -> None:
    source = Path("src/criteria_result_integration.py").read_text()

    forbidden_tokens = (
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
    )
    assert all(token not in source for token in forbidden_tokens)
