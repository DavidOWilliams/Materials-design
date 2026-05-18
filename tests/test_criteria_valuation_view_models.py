from __future__ import annotations

import copy
from pathlib import Path

from src.criteria_valuation_package import hot_section_demo_criteria_valuation_package
from src.criteria_valuation_view_models import (
    CRITERIA_VALUATION_VIEW_MODEL_SCHEMA_VERSION,
    VIEW_MODEL_SECTION_IDS,
    action_worklist_row,
    action_worklist_rows_from_package,
    build_criteria_valuation_view_model,
    candidate_summary_card,
    candidate_summary_cards_from_package,
    criteria_valuation_view_model_summary,
    criterion_value_row,
    criterion_value_rows_from_package,
    display_badge,
    evidence_gap_row,
    evidence_gap_rows_from_package,
    hard_constraints_panel_from_package,
    hot_section_demo_criteria_valuation_view_model,
    humanise_identifier,
    readiness_badges_from_package,
    readiness_panel_from_package,
    review_use_case_panel_from_package,
    safe_count,
    safety_badges_from_package,
    safety_panel_from_package,
    severity_for_action_status,
    severity_for_coverage_status,
    severity_for_package_status,
    severity_for_readiness_level,
    slugify_identifier,
    unique_preserve_order,
    validate_badge,
    validate_criteria_valuation_view_model,
    validate_summary_card,
    validate_table_row,
    validate_view_model_section,
    view_model_section,
)


def _package() -> dict:
    return hot_section_demo_criteria_valuation_package()


def _view_model() -> dict:
    return hot_section_demo_criteria_valuation_view_model()


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
    assert unique_preserve_order(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]


def test_slugify_identifier_creates_safe_lowercase_ids() -> None:
    assert slugify_identifier("Hot Section / Candidate 01") == "hot_section_candidate_01"


def test_humanise_identifier_returns_readable_fallback() -> None:
    assert humanise_identifier(None) == "Not specified"
    assert humanise_identifier("thermal_cycling") == "Thermal cycling"


def test_safe_count_counts_lists_and_dicts_and_returns_zero_otherwise() -> None:
    assert safe_count([1, 2]) == 2
    assert safe_count({"a": 1}) == 1
    assert safe_count("abc") == 0


def test_display_badge_normalises_unknown_badge_type_and_severity() -> None:
    badge = display_badge(
        "x", badge_type="surprise", label="Unknown", severity="loud"
    )

    assert badge["badge_type"] == "readiness"
    assert badge["severity"] == "neutral"


def test_severity_for_package_status_maps_placeholder_only_to_warning() -> None:
    assert severity_for_package_status("placeholder_only") == "warning"


def test_severity_for_readiness_level_maps_blocked_invalid_input_to_critical() -> None:
    assert severity_for_readiness_level("blocked_invalid_input") == "critical"


def test_severity_for_coverage_status_maps_placeholder_only_to_warning() -> None:
    assert severity_for_coverage_status("placeholder_only") == "warning"


def test_severity_for_action_status_maps_placeholder_only_to_warning() -> None:
    assert severity_for_action_status("placeholder_only") == "warning"


def test_safety_badges_from_package_includes_disabled_live_call_badges() -> None:
    labels = [badge["label"] for badge in safety_badges_from_package(_package())]

    assert "Live model calls disabled" in labels
    assert "Live source retrieval disabled" in labels
    assert "Measurement execution disabled" in labels


def test_readiness_badges_from_package_includes_package_status_and_readiness_level() -> None:
    labels = [badge["label"] for badge in readiness_badges_from_package(_package())]

    assert any(label.startswith("Package status:") for label in labels)
    assert any(label.startswith("Readiness:") for label in labels)


def test_view_model_section_creates_required_fields_and_empty_status() -> None:
    section = view_model_section("warnings_panel", payload=[])

    assert section["section_id"] == "warnings_panel"
    assert section["section_status"] == "empty"
    assert section["item_count"] == 0


def test_readiness_panel_from_package_creates_present_section_with_package_metrics() -> None:
    panel = readiness_panel_from_package(_package())

    assert panel["section_status"] == "present"
    assert panel["payload"]["candidate_count"] == 3
    assert panel["payload"]["criterion_value_count"] > 0


def test_safety_panel_from_package_creates_safety_badge_payload() -> None:
    panel = safety_panel_from_package(_package())

    assert panel["payload"]["live_model_call_allowed"] is False
    assert len(panel["badges"]) >= 3


def test_candidate_summary_card_creates_metrics_without_score_or_rank() -> None:
    card = candidate_summary_card(_package()["candidate_coverage_summaries"][0])

    assert card["metrics"]["criterion_count"] > 0
    assert not _contains_forbidden_ranking_field(card)


def test_candidate_summary_cards_from_package_creates_three_hot_section_cards() -> None:
    assert len(candidate_summary_cards_from_package(_package())) == 3


def test_criterion_value_row_creates_placeholder_value_with_warning_severity() -> None:
    value_set = _package()["candidate_value_sets"][0]
    row = criterion_value_row(
        value_set["candidate_id"], value_set["criterion_values"][0]
    )

    assert row["status"] == "pending"
    assert row["severity"] == "warning"


def test_criterion_value_rows_from_package_creates_rows_for_hot_section_package() -> None:
    assert criterion_value_rows_from_package(_package())


def test_evidence_gap_row_creates_row_with_action_suitability_cells() -> None:
    row = evidence_gap_row(_package()["evidence_gap_records"][0])

    assert "suitable_for_deterministic_estimator" in row["cells"]
    assert "suitable_for_computational_model" in row["cells"]
    assert "suitable_for_measurement_feedback" in row["cells"]


def test_evidence_gap_rows_from_package_creates_rows_for_hot_section_package() -> None:
    assert evidence_gap_rows_from_package(_package())


def test_action_worklist_row_creates_row_with_action_details() -> None:
    row = action_worklist_row(_package()["action_work_items"][0])

    assert row["cells"]["action_status"] == "planned"
    assert row["cells"]["expected_output_record_type"]
    assert row["cells"]["downstream_use"]


def test_action_worklist_rows_from_package_creates_rows_for_hot_section_package() -> None:
    assert action_worklist_rows_from_package(_package())


def test_review_use_case_panel_from_package_includes_expected_review_use_cases() -> None:
    panel = review_use_case_panel_from_package(_package())
    use_case_ids = [item["use_case_id"] for item in panel["payload"]]

    assert "cockpit_display" in use_case_ids or "engineering_review" in use_case_ids


def test_build_criteria_valuation_view_model_does_not_mutate_package() -> None:
    package = _package()
    before = copy.deepcopy(package)

    build_criteria_valuation_view_model(package)

    assert package == before


def test_build_criteria_valuation_view_model_sets_live_flags_false() -> None:
    view_model = build_criteria_valuation_view_model(_package())

    assert view_model["live_model_call_allowed"] is False
    assert view_model["live_source_retrieval_allowed"] is False
    assert view_model["measurement_execution_allowed"] is False


def test_build_criteria_valuation_view_model_creates_sections_in_required_order() -> None:
    view_model = build_criteria_valuation_view_model(_package())

    assert [section["section_id"] for section in view_model["sections"]] == list(
        VIEW_MODEL_SECTION_IDS
    )


def test_validate_badge_returns_valid_for_safety_badge() -> None:
    validation = validate_badge(safety_badges_from_package(_package())[0])

    assert validation["is_valid"] is True


def test_validate_badge_errors_if_forbidden_certification_approval_fields_appear() -> None:
    badge = display_badge("claim", badge_type="safety", label="Claim")
    badge["certification_approval"] = True

    validation = validate_badge(badge)

    assert validation["is_valid"] is False
    assert any("Forbidden approval" in error for error in validation["errors"])


def test_validate_view_model_section_returns_valid_for_readiness_panel_with_warnings_allowed() -> None:
    validation = validate_view_model_section(readiness_panel_from_package(_package()))

    assert validation["is_valid"] is True


def test_validate_summary_card_returns_valid_for_hot_section_candidate_card() -> None:
    card = candidate_summary_cards_from_package(_package())[0]

    validation = validate_summary_card(card)

    assert validation["is_valid"] is True


def test_validate_summary_card_errors_if_ranking_winner_score_fields_appear() -> None:
    card = candidate_summary_cards_from_package(_package())[0]
    card["score"] = 1

    validation = validate_summary_card(card)

    assert validation["is_valid"] is False
    assert any("Forbidden ranking" in error for error in validation["errors"])


def test_validate_table_row_returns_valid_for_criterion_value_row() -> None:
    row = criterion_value_rows_from_package(_package())[0]

    validation = validate_table_row(row)

    assert validation["is_valid"] is True


def test_validate_table_row_errors_if_live_call_or_ranking_fields_are_added() -> None:
    row = criterion_value_rows_from_package(_package())[0]
    row["cells"]["live_model_call_allowed"] = True

    live_validation = validate_table_row(row)

    assert live_validation["is_valid"] is False
    assert any("live-call" in error for error in live_validation["errors"])

    ranked_row = criterion_value_rows_from_package(_package())[0]
    ranked_row["rank"] = 1

    ranking_validation = validate_table_row(ranked_row)

    assert ranking_validation["is_valid"] is False
    assert any("Forbidden ranking" in error for error in ranking_validation["errors"])


def test_validate_criteria_valuation_view_model_returns_valid_for_hot_section_demo() -> None:
    validation = validate_criteria_valuation_view_model(_view_model())

    assert validation["is_valid"] is True


def test_validate_criteria_valuation_view_model_errors_if_live_model_call_allowed_true() -> None:
    view_model = _view_model()
    view_model["live_model_call_allowed"] = True

    validation = validate_criteria_valuation_view_model(view_model)

    assert validation["is_valid"] is False
    assert any("live_model_call_allowed" in error for error in validation["errors"])


def test_validate_criteria_valuation_view_model_errors_if_ranking_winner_score_fields_appear() -> None:
    view_model = _view_model()
    view_model["winner"] = "candidate"

    validation = validate_criteria_valuation_view_model(view_model)

    assert validation["is_valid"] is False
    assert any("Forbidden ranking" in error for error in validation["errors"])


def test_criteria_valuation_view_model_summary_returns_counts_and_live_flags() -> None:
    summary = criteria_valuation_view_model_summary(_view_model())

    assert summary["schema_version"] == CRITERIA_VALUATION_VIEW_MODEL_SCHEMA_VERSION
    assert summary["candidate_count"] == 3
    assert summary["candidate_summary_card_count"] == 3
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False
    assert summary["measurement_execution_allowed"] is False


def test_hot_section_demo_view_model_includes_three_cards_and_non_empty_rows() -> None:
    view_model = _view_model()

    assert len(view_model["candidate_summary_cards"]) == 3
    assert view_model["criterion_value_rows"]
    assert view_model["evidence_gap_rows"]
    assert view_model["action_worklist_rows"]


def test_hot_section_demo_view_model_has_no_approval_or_certification_claim_fields() -> None:
    assert not _contains_forbidden_claim_field(_view_model())


def test_hot_section_demo_view_model_has_no_ranking_or_winner_fields() -> None:
    assert not _contains_forbidden_ranking_field(_view_model())


def test_hard_constraints_panel_from_package_is_available_for_empty_constraints() -> None:
    panel = hard_constraints_panel_from_package(_package())

    assert panel["section_id"] == "hard_constraints_panel"
    assert panel["payload"] == []


def test_source_does_not_import_forbidden_runtime_modules() -> None:
    source = Path("src/criteria_valuation_view_models.py").read_text()

    assert "import app" not in source
    assert "streamlit" not in source.lower()
    assert "phase6_decision_cockpit_prototype" not in source
    assert "phase5" not in source.lower()


def test_source_does_not_call_file_network_or_process_functions() -> None:
    source = Path("src/criteria_valuation_view_models.py").read_text()

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
