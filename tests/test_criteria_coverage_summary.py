from __future__ import annotations

import copy
from pathlib import Path

from src.criteria_coverage_summary import (
    CRITERIA_COVERAGE_SUMMARY_PLAN_SCHEMA_VERSION,
    candidate_coverage_status_from_counts,
    candidate_coverage_summaries_from_plan,
    candidate_coverage_summary,
    criterion_coverage_record,
    criterion_coverage_status,
    criterion_value_candidate_id,
    criterion_values_from_candidate_value_set,
    criteria_coverage_summary,
    evidence_basis_status,
    evidence_gap_record,
    evidence_gaps_for_coverage_record,
    gap_id_for,
    hot_section_demo_criteria_coverage_summary_plan,
    measurement_feedback_status,
    model_provenance_status,
    portfolio_coverage_summary,
    recommended_next_action_type_for_value,
    slugify_identifier,
    uncertainty_assessment_status,
    unique_preserve_order,
    validate_candidate_coverage_summary,
    validate_criteria_coverage_summary_plan,
    validate_criterion_coverage_record,
    validate_evidence_gap_record,
    build_criteria_coverage_summary_plan,
)
from src.criteria_result_integration import (
    hot_section_demo_criteria_result_integration_plan,
)


def _integration_plan() -> dict:
    return hot_section_demo_criteria_result_integration_plan()


def _hot_value_set() -> dict:
    return copy.deepcopy(_integration_plan()["candidate_value_sets"][0])


def _hot_value() -> dict:
    return copy.deepcopy(_hot_value_set()["criterion_values"][0])


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
    assert slugify_identifier("Hot Section / Gap 1") == "hot_section_gap_1"


def test_criterion_values_from_candidate_value_set_returns_deep_copied_values() -> None:
    value_set = _hot_value_set()
    values = criterion_values_from_candidate_value_set(value_set)
    values[0]["estimated_value"] = "changed"

    assert value_set["criterion_values"][0]["estimated_value"] == "pending"


def test_criterion_value_candidate_id_returns_fallback_candidate_id() -> None:
    assert criterion_value_candidate_id({}, "candidate_fallback") == "candidate_fallback"


def test_criterion_coverage_status_returns_placeholder_for_hot_placeholder_value() -> None:
    assert criterion_coverage_status(_hot_value()) == "placeholder"


def test_evidence_basis_status_returns_placeholder_only_for_placeholder_evidence() -> None:
    assert evidence_basis_status(_hot_value()) == "placeholder_only"


def test_model_provenance_status_returns_missing_when_required_and_empty() -> None:
    assert model_provenance_status(_hot_value(), model_provenance_required=True) == "missing"


def test_model_provenance_status_returns_not_required_when_not_required() -> None:
    assert model_provenance_status(_hot_value()) == "not_required"


def test_measurement_feedback_status_returns_not_required_when_not_required() -> None:
    assert measurement_feedback_status(_hot_value()) == "not_required"


def test_uncertainty_assessment_status_returns_not_assessed_for_placeholder_value() -> None:
    assert uncertainty_assessment_status(_hot_value()) == "not_assessed"


def test_recommended_next_action_type_returns_deterministic_estimator_for_placeholder() -> None:
    value = _hot_value()
    assert (
        recommended_next_action_type_for_value(value, "placeholder")
        == "deterministic_estimator"
    )


def test_criterion_coverage_record_creates_required_fields_and_does_not_mutate_value() -> None:
    value = _hot_value()
    before = copy.deepcopy(value)

    record = criterion_coverage_record(value, model_provenance_required=True)

    assert value == before
    assert record["coverage_status"] == "placeholder"
    assert record["criterion_id"] == value["criterion_id"]
    assert record["model_provenance_status"] == "missing"


def test_gap_id_for_creates_stable_gap_id() -> None:
    assert gap_id_for("Candidate A", "oxidation_resistance", "placeholder_value") == (
        "gap_candidate_a_oxidation_resistance_placeholder_value"
    )


def test_evidence_gap_record_creates_suitability_flags() -> None:
    deterministic_gap = evidence_gap_record(
        "candidate_a",
        "criterion_a",
        "placeholder_value",
        reason="Placeholder.",
    )
    model_gap = evidence_gap_record(
        "candidate_a",
        "criterion_a",
        "missing_model_provenance",
        reason="Missing model provenance.",
    )
    measurement_gap = evidence_gap_record(
        "candidate_a",
        "criterion_a",
        "missing_measurement_feedback",
        reason="Missing measurement feedback.",
    )

    assert deterministic_gap["suitable_for_deterministic_estimator"] is True
    assert model_gap["suitable_for_computational_model"] is True
    assert measurement_gap["suitable_for_measurement_feedback"] is True


def test_evidence_gaps_for_coverage_record_creates_placeholder_value_gap() -> None:
    record = criterion_coverage_record(_hot_value(), model_provenance_required=True)

    gaps = evidence_gaps_for_coverage_record(record)

    assert any(gap["gap_type"] == "placeholder_value" for gap in gaps)


def test_candidate_coverage_status_from_counts_returns_placeholder_only_for_all_placeholders() -> None:
    assert candidate_coverage_status_from_counts(3, 0, 3, 0, 6) == "placeholder_only"


def test_candidate_coverage_summary_creates_coverage_and_gap_records_for_hot_value_set() -> None:
    summary = candidate_coverage_summary(
        _hot_value_set(), model_provenance_required=True
    )

    assert summary["criterion_coverage_records"]
    assert summary["evidence_gap_records"]
    assert summary["coverage_status"] == "placeholder_only"


def test_candidate_coverage_summary_does_not_mutate_value_set() -> None:
    value_set = _hot_value_set()
    before = copy.deepcopy(value_set)

    candidate_coverage_summary(value_set, model_provenance_required=True)

    assert value_set == before


def test_candidate_coverage_summaries_from_plan_creates_three_hot_summaries() -> None:
    summaries = candidate_coverage_summaries_from_plan(
        _integration_plan(), model_provenance_required=True
    )

    assert len(summaries) == 3


def test_portfolio_coverage_summary_aggregates_counts_without_ranking() -> None:
    summaries = candidate_coverage_summaries_from_plan(
        _integration_plan(), model_provenance_required=True
    )

    portfolio = portfolio_coverage_summary(summaries)

    assert portfolio["candidate_count"] == 3
    assert portfolio["total_placeholder_value_count"] > 0
    assert not _contains_forbidden_ranking_field(portfolio)


def test_build_plan_does_not_mutate_integration_plan() -> None:
    integration_plan = _integration_plan()
    before = copy.deepcopy(integration_plan)

    build_criteria_coverage_summary_plan(
        integration_plan, model_provenance_required=True
    )

    assert integration_plan == before


def test_build_plan_sets_live_flags_false() -> None:
    plan = build_criteria_coverage_summary_plan(
        _integration_plan(), model_provenance_required=True
    )

    assert plan["live_model_call_allowed"] is False
    assert plan["live_source_retrieval_allowed"] is False


def test_build_plan_has_populated_value_count_zero_for_hot_demo() -> None:
    plan = build_criteria_coverage_summary_plan(
        _integration_plan(), model_provenance_required=True
    )

    assert plan["populated_value_count"] == 0


def test_validate_criterion_coverage_record_returns_valid_for_hot_record_with_warnings_allowed() -> None:
    record = criterion_coverage_record(_hot_value(), model_provenance_required=True)

    validation = validate_criterion_coverage_record(record)

    assert validation["is_valid"] is True


def test_validate_criterion_coverage_record_errors_if_forbidden_claim_fields_appear() -> None:
    record = criterion_coverage_record(_hot_value())
    record["approved"] = True

    validation = validate_criterion_coverage_record(record)

    assert validation["is_valid"] is False
    assert any("Forbidden approval" in error for error in validation["errors"])


def test_validate_evidence_gap_record_returns_valid_for_placeholder_gap() -> None:
    gap = evidence_gap_record(
        "candidate_a",
        "criterion_a",
        "placeholder_value",
        reason="Placeholder.",
    )

    validation = validate_evidence_gap_record(gap)

    assert validation["is_valid"] is True


def test_validate_candidate_coverage_summary_returns_valid_for_hot_summary_with_warnings_allowed() -> None:
    summary = candidate_coverage_summary(
        _hot_value_set(), model_provenance_required=True
    )

    validation = validate_candidate_coverage_summary(summary)

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_criteria_coverage_summary_plan_returns_valid_for_hot_demo_with_warnings_allowed() -> None:
    validation = validate_criteria_coverage_summary_plan(
        hot_section_demo_criteria_coverage_summary_plan()
    )

    assert validation["is_valid"] is True
    assert validation["warnings"]


def test_validate_criteria_coverage_summary_plan_errors_if_live_model_call_allowed_true() -> None:
    plan = hot_section_demo_criteria_coverage_summary_plan()
    plan["live_model_call_allowed"] = True

    validation = validate_criteria_coverage_summary_plan(plan)

    assert validation["is_valid"] is False
    assert any("live_model_call_allowed" in error for error in validation["errors"])


def test_criteria_coverage_summary_returns_counts_and_live_flags() -> None:
    plan = hot_section_demo_criteria_coverage_summary_plan()

    summary = criteria_coverage_summary(plan)

    assert summary["schema_version"] == CRITERIA_COVERAGE_SUMMARY_PLAN_SCHEMA_VERSION
    assert summary["candidate_count"] == 3
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False


def test_hot_section_demo_plan_includes_three_candidate_summaries_and_placeholder_gaps() -> None:
    plan = hot_section_demo_criteria_coverage_summary_plan()

    assert len(plan["candidate_coverage_summaries"]) == 3
    assert all(
        record["coverage_status"] == "placeholder"
        for record in plan["criterion_coverage_records"]
    )
    assert any(gap["gap_type"] == "placeholder_value" for gap in plan["evidence_gap_records"])


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields() -> None:
    assert not _contains_forbidden_claim_field(
        hot_section_demo_criteria_coverage_summary_plan()
    )


def test_hot_section_demo_plan_has_no_ranking_or_winner_fields() -> None:
    assert not _contains_forbidden_ranking_field(
        hot_section_demo_criteria_coverage_summary_plan()
    )


def test_source_does_not_import_forbidden_runtime_modules() -> None:
    source = Path("src/criteria_coverage_summary.py").read_text()

    assert "import app" not in source
    assert "streamlit" not in source.lower()
    assert "phase6_decision_cockpit_prototype" not in source
    assert "phase5" not in source.lower()


def test_source_does_not_call_file_network_or_process_functions() -> None:
    source = Path("src/criteria_coverage_summary.py").read_text()

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
