from copy import deepcopy
import json

from src.phase5_cockpit_review_export import (
    EXPORT_SCHEMA_VERSION,
    badge_labels,
    build_cockpit_review_export_package_from_view_model,
    build_export_manifest,
    build_markdown_report,
    export_package_to_json_string,
    make_json_safe,
    markdown_escape,
    markdown_for_candidate_summary,
    markdown_table,
    metric_map,
    run_phase5_cockpit_review_export,
    summarise_candidate_card,
    summarise_cards,
)


class OddObject:
    def __str__(self) -> str:
        return "odd-object"


def _metric(metric_id: str, value: str) -> dict:
    return {
        "metric_id": metric_id,
        "label": metric_id.replace("_", " ").title(),
        "value": value,
        "tone": "info",
        "help_text": "",
    }


def _badge(label: str) -> dict:
    return {
        "badge_id": label.lower().replace(" ", "_"),
        "label": label,
        "tone": "info",
        "tooltip": "",
    }


def _card(candidate_id: str = "C-1") -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"System {candidate_id}",
        "headline": f"System {candidate_id} - Validation-needed option",
        "tier": "validation_needed_option",
        "tier_label": "Validation-needed option",
        "frontier_status": "on_frontier",
        "evidence_maturity": "C",
        "evidence_band": "engineering_reference",
        "plan_status": "validation_needs_available",
        "research_mode_exposure": False,
        "badges": [_badge("Validation-needed option"), _badge("No certification claim")],
        "metrics": [
            _metric("validation_need_count", "7"),
            _metric("high_priority_need_count", "2"),
        ],
        "priority_validation_needs": [
            {
                "need_id": "need-1",
                "category": "frontier_review",
                "priority": "high",
                "validation_activity": "Review frontier trade-offs.",
                "trigger": "on_frontier",
                "status": "proposed_validation_need",
                "warnings": [],
            }
        ],
        "caution_summary": [
            "No certification or qualification approval is implied.",
        ],
        "review_actions": [
            "Review frontier trade-offs.",
            "Confirm evidence basis.",
        ],
        "detail_sections": [],
        "notes": [],
        "warnings": ["Card warning"],
    }


def _view_model(cards: list[dict] | None = None) -> dict:
    card_list = cards if cards is not None else [_card("C-1")]
    return {
        "candidate_count": len(card_list),
        "card_count": len(card_list),
        "research_mode_enabled": False,
        "overview_metrics": [
            _metric("candidate_count", str(len(card_list))),
            _metric("validation_need_count", "7"),
        ],
        "cards": card_list,
        "charts": [
            {
                "chart_id": "tier_distribution",
                "title": "Tier Distribution",
                "chart_type": "bar",
                "data": [{"label": "validation_needed_option", "value": len(card_list)}],
                "notes": [],
                "warnings": [],
            }
        ],
        "global_notes": ["Decision cockpit view model is presentation data only."],
        "global_warnings": ["Global warning"],
    }


def _pipeline_candidate(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"Nickel DED System {candidate_id}",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "limiting_factors": [],
    }


def test_make_json_safe_recursively_converts_mapping_tuple_and_object():
    value = {"a": (1, OddObject()), 3: {"nested": OddObject()}}

    safe = make_json_safe(value)

    assert safe == {"a": [1, "odd-object"], "3": {"nested": "odd-object"}}


def test_metric_map_returns_first_metric_value_by_id():
    metrics = [
        _metric("validation_need_count", "3"),
        _metric("validation_need_count", "5"),
        _metric("candidate_count", "1"),
    ]

    assert metric_map(metrics) == {
        "validation_need_count": "3",
        "candidate_count": "1",
    }


def test_badge_labels_returns_labels_in_order():
    assert badge_labels([_badge("A"), {"badge_id": "missing"}, _badge("B")]) == ["A", "B"]


def test_summarise_candidate_card_preserves_identity_tier_and_status():
    summary = summarise_candidate_card(_card("C-9"))

    assert summary["candidate_id"] == "C-9"
    assert summary["system_name"] == "System C-9"
    assert summary["tier_label"] == "Validation-needed option"
    assert summary["frontier_status"] == "on_frontier"
    assert summary["plan_status"] == "validation_needs_available"


def test_summarise_candidate_card_builds_metric_map_and_actions():
    summary = summarise_candidate_card(_card())

    assert summary["key_metrics"]["validation_need_count"] == "7"
    assert summary["priority_actions"] == [
        "Review frontier trade-offs.",
        "Confirm evidence basis.",
    ]


def test_summarise_candidate_card_falls_back_to_priority_need_length_for_need_count():
    card = _card()
    card["metrics"] = [_metric("validation_need_count", "not-an-int")]

    summary = summarise_candidate_card(card)

    assert summary["validation_need_count"] == 1


def test_summarise_cards_preserves_order():
    summaries = summarise_cards([_card("C-2"), _card("C-1")])

    assert [summary["candidate_id"] for summary in summaries] == ["C-2", "C-1"]


def test_build_export_manifest_includes_schema_counts_and_limitations():
    manifest = build_export_manifest(_view_model())

    assert manifest["schema_version"] == EXPORT_SCHEMA_VERSION
    assert manifest["candidate_count"] == 1
    assert manifest["card_count"] == 1
    assert manifest["chart_count"] == 1
    assert "No final recommendation is made." in manifest["limitations"]


def test_build_export_manifest_warns_when_card_count_is_zero():
    manifest = build_export_manifest(_view_model([]))

    assert any("No candidate cards" in warning for warning in manifest["warnings"])


def test_markdown_escape_escapes_pipe_and_removes_newline():
    assert markdown_escape("a|b\nc") == "a\\|b c"


def test_markdown_table_creates_simple_table():
    table = markdown_table(["A", "B"], [[1, "x|y"]])

    assert table == "| A | B |\n| --- | --- |\n| 1 | x\\|y |"


def test_markdown_for_candidate_summary_includes_heading_and_limitations():
    markdown = markdown_for_candidate_summary(summarise_candidate_card(_card("C-1")))

    assert "## C-1 - System C-1 - Validation-needed option" in markdown
    assert "decision-support only" in markdown
    assert "certification approval" in markdown


def test_build_markdown_report_includes_required_sections():
    view_model = _view_model()
    manifest = build_export_manifest(view_model)
    summaries = summarise_cards(view_model["cards"])

    markdown = build_markdown_report(
        manifest,
        view_model["overview_metrics"],
        summaries,
        view_model["charts"],
    )

    assert "# Phase 5 Cockpit Review Export" in markdown
    assert "## Limitations" in markdown
    assert "## Overview Metrics" in markdown
    assert "## Chart Data Summary" in markdown
    assert "## C-1 - System C-1 - Validation-needed option" in markdown


def test_build_package_from_view_model_includes_manifest_summaries_markdown_and_payload():
    package = build_cockpit_review_export_package_from_view_model(_view_model())

    assert package["manifest"]["export_type"] == "phase5_cockpit_review_export"
    assert package["candidate_summaries"][0]["candidate_id"] == "C-1"
    assert package["markdown_report"].startswith("# Phase 5 Cockpit Review Export")
    assert package["json_payload"]["manifest"]["schema_version"] == EXPORT_SCHEMA_VERSION


def test_build_package_from_view_model_does_not_mutate_input_view_model():
    view_model = _view_model()
    original = deepcopy(view_model)

    build_cockpit_review_export_package_from_view_model(view_model)

    assert view_model == original


def test_export_package_to_json_string_returns_valid_json():
    package = build_cockpit_review_export_package_from_view_model(_view_model())

    decoded = json.loads(export_package_to_json_string(package))

    assert decoded["manifest"]["schema_version"] == EXPORT_SCHEMA_VERSION


def test_export_package_to_json_string_serialises_payload_not_markdown_report():
    package = build_cockpit_review_export_package_from_view_model(_view_model())

    decoded = json.loads(export_package_to_json_string(package))

    assert "markdown_report" not in decoded
    assert "candidate_summaries" in decoded


def test_run_phase5_cockpit_review_export_preserves_candidate_order():
    package = run_phase5_cockpit_review_export([
        _pipeline_candidate("C-1"),
        _pipeline_candidate("C-2"),
    ])

    assert [summary["candidate_id"] for summary in package["candidate_summaries"]] == [
        "C-1",
        "C-2",
    ]


def test_run_phase5_cockpit_review_export_includes_research_mode_warning():
    package = run_phase5_cockpit_review_export([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in package["warnings"])


def test_run_phase5_cockpit_review_export_does_not_mutate_input_candidates():
    candidates = [_pipeline_candidate("C-1"), _pipeline_candidate("C-2")]
    original = deepcopy(candidates)

    run_phase5_cockpit_review_export(candidates)

    assert candidates == original


def test_package_manifest_and_summaries_do_not_include_rank_score_or_winner_fields():
    package = build_cockpit_review_export_package_from_view_model(_view_model())

    for container in (
        package,
        package["manifest"],
        package["candidate_summaries"][0],
    ):
        assert "rank" not in container
        assert "score" not in container
        assert "winner" not in container
