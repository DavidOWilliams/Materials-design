from __future__ import annotations

import copy
from pathlib import Path

from src.criteria_coverage_summary import (
    hot_section_demo_criteria_coverage_summary_plan,
)
from src.evidence_gap_action_worklist import (
    EVIDENCE_GAP_ACTION_WORKLIST_PLAN_SCHEMA_VERSION,
    action_id_for_gap,
    action_priority_for_gap,
    action_status_for_gap,
    action_type_counts,
    action_type_for_gap,
    action_work_items_by_candidate,
    build_evidence_gap_action_worklist_plan,
    downstream_use_for_action,
    evidence_gap_action_work_item,
    evidence_gap_action_work_items_from_plan,
    evidence_gap_action_worklist_summary,
    evidence_gap_records_from_plan,
    expected_output_record_type_for_gap,
    hot_section_demo_evidence_gap_action_worklist_plan,
    required_input_records_for_action,
    slugify_identifier,
    unique_preserve_order,
    validate_action_work_item,
    validate_evidence_gap_action_worklist_plan,
)


def _coverage_plan() -> dict:
    return hot_section_demo_criteria_coverage_summary_plan()


def _first_gap(gap_type: str | None = None) -> dict:
    gaps = evidence_gap_records_from_plan(_coverage_plan())
    if gap_type is None:
        return copy.deepcopy(gaps[0])
    for gap in gaps:
        if gap.get("gap_type") == gap_type:
            return copy.deepcopy(gap)
    raise AssertionError(f"No gap of type {gap_type!r} found")


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
    assert slugify_identifier("Action / Hot Section 1") == "action_hot_section_1"


def test_evidence_gap_records_from_plan_returns_deep_copied_hot_section_gaps() -> None:
    plan = _coverage_plan()
    gaps = evidence_gap_records_from_plan(plan)
    gaps[0]["reason"] = "changed"

    assert plan["evidence_gap_records"][0]["reason"] != "changed"


def test_action_type_for_gap_maps_placeholder_value_to_deterministic_estimator() -> None:
    assert action_type_for_gap(_first_gap("placeholder_value")) == "deterministic_estimator"


def test_action_type_for_gap_maps_missing_model_provenance_to_computational_model() -> None:
    assert action_type_for_gap(_first_gap("missing_model_provenance")) == "computational_model"


def test_action_type_for_gap_maps_missing_measurement_feedback_to_measurement_feedback() -> None:
    gap = _first_gap()
    gap["gap_type"] = "missing_measurement_feedback"
    gap["next_action_type"] = "measurement_feedback"

    assert action_type_for_gap(gap) == "measurement_feedback"


def test_expected_output_record_type_for_gap_maps_placeholder_value() -> None:
    assert (
        expected_output_record_type_for_gap(_first_gap("placeholder_value"))
        == "criterion_value_update"
    )


def test_action_priority_for_gap_normalises_unknown_severity_to_medium() -> None:
    gap = _first_gap()
    gap["severity"] = "urgent"

    assert action_priority_for_gap(gap) == "medium"


def test_action_priority_for_gap_returns_high_for_invalid_criterion_value() -> None:
    gap = _first_gap()
    gap["gap_type"] = "invalid_criterion_value"
    gap["severity"] = "low"

    assert action_priority_for_gap(gap) == "high"


def test_action_id_for_gap_creates_stable_action_id() -> None:
    gap = {
        "candidate_id": "Candidate A",
        "criterion_id": "oxidation_resistance",
        "gap_type": "placeholder_value",
    }

    assert action_id_for_gap(gap) == "action_candidate_a_oxidation_resistance_placeholder_value"


def test_action_status_for_gap_returns_placeholder_for_model_and_measurement_actions() -> None:
    model_gap = _first_gap("missing_model_provenance")
    measurement_gap = _first_gap()
    measurement_gap["gap_type"] = "missing_measurement_feedback"
    measurement_gap["next_action_type"] = "measurement_feedback"

    assert action_status_for_gap(model_gap, "computational_model") == "placeholder_only"
    assert action_status_for_gap(measurement_gap, "measurement_feedback") == "placeholder_only"


def test_required_input_records_for_action_includes_deterministic_estimator_inputs() -> None:
    records = required_input_records_for_action(
        _first_gap("placeholder_value"), "deterministic_estimator"
    )

    assert "candidate_criteria_valuation_work_item" in records
    assert "deterministic_estimator_request" in records


def test_downstream_use_for_action_includes_result_integration_for_deterministic() -> None:
    uses = downstream_use_for_action(
        _first_gap("placeholder_value"), "deterministic_estimator"
    )

    assert "criteria_result_integration" in uses


def test_evidence_gap_action_work_item_creates_required_fields_and_live_flags_false() -> None:
    item = evidence_gap_action_work_item(_first_gap("placeholder_value"))

    assert item["action_type"] == "deterministic_estimator"
    assert item["live_model_call_allowed"] is False
    assert item["live_source_retrieval_allowed"] is False
    assert item["measurement_execution_allowed"] is False


def test_evidence_gap_action_work_item_does_not_mutate_gap() -> None:
    gap = _first_gap()
    before = copy.deepcopy(gap)

    evidence_gap_action_work_item(gap)

    assert gap == before


def test_evidence_gap_action_work_items_from_plan_creates_work_items_from_hot_gaps() -> None:
    items = evidence_gap_action_work_items_from_plan(_coverage_plan())

    assert items
    assert len(items) == len(_coverage_plan()["evidence_gap_records"])


def test_action_work_items_by_candidate_groups_by_candidate_id() -> None:
    items = evidence_gap_action_work_items_from_plan(_coverage_plan())

    grouped = action_work_items_by_candidate(items)

    assert set(grouped) == {
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    }


def test_action_type_counts_returns_counts_for_all_action_types() -> None:
    counts = action_type_counts(evidence_gap_action_work_items_from_plan(_coverage_plan()))

    assert set(counts) == {
        "deterministic_estimator",
        "computational_model",
        "literature_evidence_review",
        "measurement_feedback",
        "engineering_review",
    }


def test_build_plan_does_not_mutate_coverage_plan() -> None:
    coverage_plan = _coverage_plan()
    before = copy.deepcopy(coverage_plan)

    build_evidence_gap_action_worklist_plan(coverage_plan)

    assert coverage_plan == before


def test_build_plan_sets_all_live_and_execution_flags_false() -> None:
    plan = build_evidence_gap_action_worklist_plan(_coverage_plan())

    assert plan["live_model_call_allowed"] is False
    assert plan["live_source_retrieval_allowed"] is False
    assert plan["measurement_execution_allowed"] is False


def test_build_plan_includes_actions_for_three_hot_section_candidates() -> None:
    plan = build_evidence_gap_action_worklist_plan(_coverage_plan())

    assert plan["candidate_count"] == 3
    assert set(plan["action_work_items_by_candidate"]) == {
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    }


def test_validate_action_work_item_returns_valid_for_hot_item_with_warnings_allowed() -> None:
    item = evidence_gap_action_work_item(_first_gap("placeholder_value"))

    validation = validate_action_work_item(item)

    assert validation["is_valid"] is True


def test_validate_action_work_item_errors_if_live_model_call_allowed_true() -> None:
    item = evidence_gap_action_work_item(_first_gap())
    item["live_model_call_allowed"] = True

    validation = validate_action_work_item(item)

    assert validation["is_valid"] is False
    assert any("live_model_call_allowed" in error for error in validation["errors"])


def test_validate_action_work_item_errors_if_measurement_execution_allowed_true() -> None:
    item = evidence_gap_action_work_item(_first_gap())
    item["measurement_execution_allowed"] = True

    validation = validate_action_work_item(item)

    assert validation["is_valid"] is False
    assert any("measurement_execution_allowed" in error for error in validation["errors"])


def test_validate_action_work_item_errors_if_forbidden_claim_fields_appear() -> None:
    item = evidence_gap_action_work_item(_first_gap())
    item["approved"] = True

    validation = validate_action_work_item(item)

    assert validation["is_valid"] is False
    assert any("Forbidden approval" in error for error in validation["errors"])


def test_validate_plan_returns_valid_for_hot_section_demo_with_warnings_allowed() -> None:
    validation = validate_evidence_gap_action_worklist_plan(
        hot_section_demo_evidence_gap_action_worklist_plan()
    )

    assert validation["is_valid"] is True


def test_validate_plan_errors_if_live_source_retrieval_allowed_true() -> None:
    plan = hot_section_demo_evidence_gap_action_worklist_plan()
    plan["live_source_retrieval_allowed"] = True

    validation = validate_evidence_gap_action_worklist_plan(plan)

    assert validation["is_valid"] is False
    assert any("live_source_retrieval_allowed" in error for error in validation["errors"])


def test_evidence_gap_action_worklist_summary_returns_counts_and_live_flags() -> None:
    plan = hot_section_demo_evidence_gap_action_worklist_plan()

    summary = evidence_gap_action_worklist_summary(plan)

    assert summary["schema_version"] == EVIDENCE_GAP_ACTION_WORKLIST_PLAN_SCHEMA_VERSION
    assert summary["candidate_count"] == 3
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False
    assert summary["measurement_execution_allowed"] is False


def test_hot_section_demo_plan_includes_deterministic_and_literature_actions() -> None:
    plan = hot_section_demo_evidence_gap_action_worklist_plan()
    action_types = {item["action_type"] for item in plan["action_work_items"]}

    assert "deterministic_estimator" in action_types
    assert "literature_evidence_review" in action_types
    assert "computational_model" in action_types


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields() -> None:
    assert not _contains_forbidden_claim_field(
        hot_section_demo_evidence_gap_action_worklist_plan()
    )


def test_hot_section_demo_plan_has_no_ranking_or_winner_fields() -> None:
    assert not _contains_forbidden_ranking_field(
        hot_section_demo_evidence_gap_action_worklist_plan()
    )


def test_source_does_not_import_forbidden_runtime_modules() -> None:
    source = Path("src/evidence_gap_action_worklist.py").read_text()

    assert "import app" not in source
    assert "streamlit" not in source.lower()
    assert "phase6_decision_cockpit_prototype" not in source
    assert "phase5" not in source.lower()


def test_source_does_not_call_file_network_or_process_functions() -> None:
    source = Path("src/evidence_gap_action_worklist.py").read_text()

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
