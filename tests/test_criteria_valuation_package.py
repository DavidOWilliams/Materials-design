from __future__ import annotations

import copy
from pathlib import Path

from src.criteria_coverage_summary import (
    hot_section_demo_criteria_coverage_summary_plan,
)
from src.criteria_result_integration import (
    hot_section_demo_criteria_result_integration_plan,
)
from src.criteria_valuation_package import (
    CRITERIA_VALUATION_PACKAGE_SCHEMA_VERSION,
    PACKAGE_SECTION_IDS,
    build_criteria_valuation_package,
    build_readiness_summary,
    candidate_ids_from_coverage_summaries,
    candidate_ids_from_value_sets,
    count_criterion_values,
    count_placeholder_values,
    count_populated_values,
    criteria_valuation_package_summary,
    deep_copy_dict,
    deep_copy_list,
    hot_section_demo_criteria_valuation_package,
    package_candidate_consistency_warnings,
    package_section,
    package_sections_from_payloads,
    package_status_from_counts,
    readiness_level_from_package_status,
    section_label,
    slugify_identifier,
    unique_preserve_order,
    validate_criteria_valuation_package,
    validate_package_section,
    validate_readiness_summary,
)
from src.evidence_gap_action_worklist import (
    hot_section_demo_evidence_gap_action_worklist_plan,
)


def _result_plan() -> dict:
    return hot_section_demo_criteria_result_integration_plan()


def _coverage_plan() -> dict:
    return hot_section_demo_criteria_coverage_summary_plan()


def _action_plan() -> dict:
    return hot_section_demo_evidence_gap_action_worklist_plan()


def _package() -> dict:
    return hot_section_demo_criteria_valuation_package()


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


def _contains_forbidden_ranking_field(value: object) -> bool:
    forbidden = {"rank", "winner", "best_candidate", "score"}
    if isinstance(value, dict):
        return any(
            str(key) in forbidden or _contains_forbidden_ranking_field(nested)
            for key, nested in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_ranking_field(item) for item in value)
    return False


def test_unique_preserve_order_removes_duplicates_and_preserves_order() -> None:
    assert unique_preserve_order(["a", "b", "a", "c"]) == ["a", "b", "c"]


def test_slugify_identifier_creates_safe_lowercase_ids() -> None:
    assert slugify_identifier("Criteria Package / 1") == "criteria_package_1"


def test_deep_copy_list_returns_copy_without_shared_nested_records() -> None:
    original = [{"a": {"b": 1}}]
    copied = deep_copy_list(original)
    copied[0]["a"]["b"] = 2

    assert original[0]["a"]["b"] == 1


def test_deep_copy_dict_returns_copy_without_shared_nested_records() -> None:
    original = {"a": {"b": 1}}
    copied = deep_copy_dict(original)
    copied["a"]["b"] = 2

    assert original["a"]["b"] == 1


def test_section_label_returns_readable_label_and_unknown_fallback() -> None:
    assert section_label("candidate_value_sets") == "Candidate value sets"
    assert section_label("new_section_id") == "New section id"


def test_package_section_creates_required_fields_and_item_count() -> None:
    section = package_section("warnings", ["a", "b"])

    assert section["section_id"] == "warnings"
    assert section["section_status"] == "present"
    assert section["item_count"] == 2


def test_package_section_marks_empty_payload_as_empty() -> None:
    assert package_section("warnings", [])["section_status"] == "empty"


def test_candidate_ids_from_value_sets_returns_candidate_ids_in_order() -> None:
    value_sets = _result_plan()["candidate_value_sets"]

    assert candidate_ids_from_value_sets(value_sets) == [
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    ]


def test_candidate_ids_from_coverage_summaries_returns_candidate_ids_in_order() -> None:
    summaries = _coverage_plan()["candidate_coverage_summaries"]

    assert candidate_ids_from_coverage_summaries(summaries) == [
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    ]


def test_package_candidate_consistency_warnings_returns_no_severe_errors_for_hot_demo() -> None:
    warnings = package_candidate_consistency_warnings(
        _result_plan(), _coverage_plan(), _action_plan()
    )

    assert warnings == []


def test_count_criterion_values_counts_hot_section_values() -> None:
    assert count_criterion_values(_result_plan()["candidate_value_sets"]) > 0


def test_count_populated_values_returns_zero_for_hot_section_placeholders() -> None:
    assert count_populated_values(_result_plan()["candidate_value_sets"]) == 0


def test_count_placeholder_values_returns_placeholder_values_for_hot_section() -> None:
    value_sets = _result_plan()["candidate_value_sets"]

    assert count_placeholder_values(value_sets) == count_criterion_values(value_sets)


def test_package_status_from_counts_returns_placeholder_only_for_all_placeholder_values() -> None:
    assert package_status_from_counts(3, 39, 0, 39, 100, 0) == "placeholder_only"


def test_readiness_level_from_package_status_maps_placeholder_only() -> None:
    assert readiness_level_from_package_status("placeholder_only") == "placeholder_only"


def test_build_readiness_summary_sets_live_flags_false_and_includes_review_use_cases() -> None:
    candidate_value_sets = _result_plan()["candidate_value_sets"]
    evidence_gap_records = _coverage_plan()["evidence_gap_records"]
    action_plan = _action_plan()

    summary = build_readiness_summary(
        package_status="placeholder_only",
        candidate_value_sets=candidate_value_sets,
        evidence_gap_records=evidence_gap_records,
        action_work_items=action_plan["action_work_items"],
        action_worklist_plan=action_plan,
    )

    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False
    assert summary["measurement_execution_allowed"] is False
    assert "cockpit_display" in summary["review_use_cases"]


def test_package_sections_from_payloads_creates_one_section_per_section_id() -> None:
    result_plan = _result_plan()
    coverage_plan = _coverage_plan()
    action_plan = _action_plan()

    sections = package_sections_from_payloads(
        candidate_value_sets=result_plan["candidate_value_sets"],
        integrated_value_records=result_plan["integrated_value_records"],
        candidate_coverage_summaries=coverage_plan["candidate_coverage_summaries"],
        portfolio_coverage_summary=coverage_plan["portfolio_coverage_summary"],
        evidence_gap_records=coverage_plan["evidence_gap_records"],
        action_work_items=action_plan["action_work_items"],
        action_work_items_by_candidate=action_plan["action_work_items_by_candidate"],
        assumptions=[],
        warnings=[],
        hard_constraints=[],
    )

    assert [section["section_id"] for section in sections] == list(PACKAGE_SECTION_IDS)


def test_build_criteria_valuation_package_does_not_mutate_input_plans() -> None:
    result_plan = _result_plan()
    coverage_plan = _coverage_plan()
    action_plan = _action_plan()
    before = (copy.deepcopy(result_plan), copy.deepcopy(coverage_plan), copy.deepcopy(action_plan))

    build_criteria_valuation_package(result_plan, coverage_plan, action_plan)

    assert (result_plan, coverage_plan, action_plan) == before


def test_build_criteria_valuation_package_sets_live_flags_false() -> None:
    package = build_criteria_valuation_package(_result_plan(), _coverage_plan(), _action_plan())

    assert package["live_model_call_allowed"] is False
    assert package["live_source_retrieval_allowed"] is False
    assert package["measurement_execution_allowed"] is False


def test_build_criteria_valuation_package_includes_expected_payloads() -> None:
    package = build_criteria_valuation_package(_result_plan(), _coverage_plan(), _action_plan())

    assert package["candidate_value_sets"]
    assert package["candidate_coverage_summaries"]
    assert package["evidence_gap_records"]
    assert package["action_work_items"]


def test_validate_package_section_returns_valid_for_hot_section_with_warnings_allowed() -> None:
    section = _package()["package_sections"][0]

    validation = validate_package_section(section)

    assert validation["is_valid"] is True


def test_validate_package_section_errors_if_forbidden_claim_fields_appear() -> None:
    section = package_section("warnings", ["ok"])
    section["approved"] = True

    validation = validate_package_section(section)

    assert validation["is_valid"] is False
    assert any("Forbidden approval" in error for error in validation["errors"])


def test_validate_package_section_errors_if_ranking_fields_appear() -> None:
    section = package_section("warnings", ["ok"])
    section["score"] = 1

    validation = validate_package_section(section)

    assert validation["is_valid"] is False
    assert any("Forbidden ranking" in error for error in validation["errors"])


def test_validate_readiness_summary_returns_valid_for_hot_summary_with_warnings_allowed() -> None:
    summary = _package()["readiness_summary"]

    validation = validate_readiness_summary(summary)

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_readiness_summary_errors_if_live_model_call_allowed_true() -> None:
    summary = copy.deepcopy(_package()["readiness_summary"])
    summary["live_model_call_allowed"] = True

    validation = validate_readiness_summary(summary)

    assert validation["is_valid"] is False
    assert any("live_model_call_allowed" in error for error in validation["errors"])


def test_validate_criteria_valuation_package_returns_valid_for_hot_package_with_warnings_allowed() -> None:
    validation = validate_criteria_valuation_package(_package())

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_criteria_valuation_package_errors_if_live_source_retrieval_allowed_true() -> None:
    package = _package()
    package["live_source_retrieval_allowed"] = True

    validation = validate_criteria_valuation_package(package)

    assert validation["is_valid"] is False
    assert any("live_source_retrieval_allowed" in error for error in validation["errors"])


def test_validate_criteria_valuation_package_errors_if_ranking_fields_appear() -> None:
    package = _package()
    package["winner"] = "candidate"

    validation = validate_criteria_valuation_package(package)

    assert validation["is_valid"] is False
    assert any("Forbidden ranking" in error for error in validation["errors"])


def test_criteria_valuation_package_summary_returns_counts_and_live_flags() -> None:
    package = _package()

    summary = criteria_valuation_package_summary(package)

    assert summary["schema_version"] == CRITERIA_VALUATION_PACKAGE_SCHEMA_VERSION
    assert summary["candidate_count"] == 3
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False
    assert summary["measurement_execution_allowed"] is False


def test_hot_section_demo_package_includes_three_value_sets_and_action_items() -> None:
    package = _package()

    assert len(package["candidate_value_sets"]) == 3
    assert package["action_work_items"]


def test_hot_section_demo_package_has_no_approval_or_certification_claim_fields() -> None:
    assert not _contains_forbidden_claim_field(_package())


def test_hot_section_demo_package_has_no_ranking_or_winner_fields() -> None:
    assert not _contains_forbidden_ranking_field(_package())


def test_source_does_not_import_forbidden_runtime_modules() -> None:
    source = Path("src/criteria_valuation_package.py").read_text()

    assert "import app" not in source
    assert "streamlit" not in source.lower()
    assert "phase6_decision_cockpit_prototype" not in source
    assert "phase5" not in source.lower()


def test_source_does_not_call_file_network_or_process_functions() -> None:
    source = Path("src/criteria_valuation_package.py").read_text()

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
