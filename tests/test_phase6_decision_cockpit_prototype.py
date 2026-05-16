import ast
from copy import deepcopy

import phase6_decision_cockpit_prototype as prototype


def _prototype_source():
    with open("phase6_decision_cockpit_prototype.py", encoding="utf-8") as handle:
        return handle.read()


def _imported_modules(source):
    tree = ast.parse(source)
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_build_demo_candidates_returns_four_candidates_in_order():
    candidates = prototype.build_demo_candidates()

    assert [candidate["candidate_id"] for candidate in candidates] == [
        "demo_ni_tbc_reference",
        "demo_sic_cmc_ebc_option",
        "demo_spatially_graded_am_surface",
        "demo_refractory_oxidation_protection",
    ]


def test_limiting_factors_cover_every_demo_candidate():
    candidates = prototype.build_demo_candidates()
    factors = prototype.build_demo_limiting_factors_by_candidate()

    assert set(factors) == {candidate["candidate_id"] for candidate in candidates}
    assert all(factors[candidate["candidate_id"]] for candidate in candidates)


def test_build_demo_cockpit_view_model_returns_candidate_cards():
    view_model = prototype.build_demo_cockpit_view_model()

    assert view_model["card_count"] == 4
    assert len(view_model["cards"]) == 4


def test_build_demo_review_export_package_returns_manifest_and_summaries():
    package = prototype.build_demo_review_export_package()

    assert package["manifest"]["export_type"] == "phase5_cockpit_review_export"
    assert len(package["candidate_summaries"]) == 4


def test_build_demo_feedback_package_returns_feedback_summaries():
    package = prototype.build_demo_feedback_package()

    assert len(package["feedback_summaries"]) == 4


def test_build_demo_adapter_contract_review_returns_safe_registry():
    review = prototype.build_demo_adapter_contract_review()

    assert review["registry"]["registry_status"] == "disabled_registry"
    assert review["summary"]["registry_safe"] is True


def test_flatten_chart_data_returns_rows_and_does_not_mutate():
    chart = {"data": [{"label": "a", "value": 2}, {"label": "b", "value": 1}]}
    original = deepcopy(chart)

    rows = prototype.flatten_chart_data(chart)

    assert rows == [{"label": "a", "value": 2}, {"label": "b", "value": 1}]
    assert chart == original


def test_find_metric_returns_value_or_default():
    metrics = [{"metric_id": "candidate_count", "value": "4"}]

    assert prototype.find_metric(metrics, "candidate_count") == "4"
    assert prototype.find_metric(metrics, "missing", default="n/a") == "n/a"


def test_collect_forbidden_decision_fields_detects_nested_keys():
    value = {"outer": [{"score": 1}, {"nested": {"winner": "C-1"}}]}

    assert prototype.collect_forbidden_decision_fields(value) == [
        "root.outer[0].score",
        "root.outer[1].nested.winner",
    ]


def test_demo_view_model_has_no_forbidden_decision_fields():
    view_model = prototype.build_demo_cockpit_view_model()

    assert prototype.view_model_has_no_forbidden_decision_fields(view_model) is True


def test_candidate_card_display_rows_include_required_fields():
    card = prototype.build_demo_cockpit_view_model()["cards"][0]

    rows = prototype.build_candidate_card_display_rows(card)

    assert [row["field"] for row in rows] == [
        "candidate_id",
        "system_name",
        "tier_label",
        "frontier_status",
        "evidence_band",
        "plan_status",
        "validation_need_count",
        "research_mode_exposure",
    ]


def test_prototype_safety_notes_include_required_limitations():
    notes = prototype.prototype_safety_notes()

    assert "No final recommendation is made." in notes
    assert "No qualification approval is implied." in notes
    assert "No certification approval is implied." in notes


def test_short_label_replaces_underscores_and_truncates_long_labels():
    assert prototype.short_label("validation_priority") == "Validation priority"
    assert prototype.short_label("validation_priority_distribution", max_length=10) == (
        "Validation..."
    )


def test_badge_tone_class_maps_high_caution_and_unknown():
    assert prototype.badge_tone_class("high_caution") == "badge-high-caution"
    assert prototype.badge_tone_class("unknown") == "badge-info"


def test_build_metric_card_models_preserves_overview_metric_order():
    view_model = prototype.build_demo_cockpit_view_model()

    cards = prototype.build_metric_card_models(view_model)

    assert [card["metric_id"] for card in cards] == [
        metric["metric_id"] for metric in view_model["overview_metrics"]
    ]
    assert {"metric_id", "label", "value", "tone", "help_text"} <= set(cards[0])


def test_build_candidate_board_cards_limits_review_actions():
    view_model = prototype.build_demo_cockpit_view_model()

    cards = prototype.build_candidate_board_cards(view_model)

    assert len(cards) == len(view_model["cards"])
    assert [card["candidate_id"] for card in cards] == [
        card["candidate_id"] for card in view_model["cards"]
    ]
    assert all(len(card["top_review_actions"]) <= 3 for card in cards)
    assert all(len(card["caution_summary"]) <= 3 for card in cards)


def test_build_candidate_comparison_matrix_includes_readable_candidate_rows():
    view_model = prototype.build_demo_cockpit_view_model()

    rows = prototype.build_candidate_comparison_matrix(view_model)

    assert rows[0]["Candidate"] == "Ni superalloy + TBC reference"
    assert rows[0]["Tier"] == "Mature reference option"
    assert rows[0]["Frontier"] == "On frontier"
    assert rows[0]["Research mode"] == "No"


def test_build_validation_burden_rows_includes_priority_counts_and_total():
    rows = prototype.build_validation_burden_rows(prototype.build_demo_cockpit_view_model())

    assert {"Candidate", "High", "Medium", "Low", "Total"} <= set(rows[0])
    assert rows[0]["Total"] == rows[0]["High"] + rows[0]["Medium"] + rows[0]["Low"]


def test_build_chart_display_models_shortens_labels_and_preserves_order():
    view_model = prototype.build_demo_cockpit_view_model()

    charts = prototype.build_chart_display_models(view_model)

    assert [chart["chart_id"] for chart in charts] == [
        chart["chart_id"] for chart in view_model["charts"]
    ]
    labels = [row["label"] for chart in charts for row in chart["rows"]]
    assert "Validation needs available" in labels
    assert any(label.endswith("...") for label in labels)


def test_build_review_export_summary_returns_compact_manifest_summary_only():
    summary = prototype.build_review_export_summary(
        prototype.build_demo_review_export_package()
    )

    assert set(summary) == {
        "export_type",
        "schema_version",
        "candidate_count",
        "card_count",
        "chart_count",
        "limitation_count",
        "warning_count",
    }
    assert summary["export_type"] == "phase5_cockpit_review_export"
    assert "limitations" not in summary
    assert "warnings" not in summary


def test_build_feedback_summary_rows_returns_readable_feedback_rows():
    rows = prototype.build_feedback_summary_rows(prototype.build_demo_feedback_package())

    assert rows[0] == {
        "Candidate": "Ni superalloy + TBC reference",
        "Feedback records": 1,
        "Follow-up required": "No",
        "Review state": "Feedback recorded",
        "Draft template count": 1,
    }


def test_build_adapter_summary_rows_reports_live_calls_disabled():
    rows = prototype.build_adapter_summary_rows(prototype.build_demo_adapter_contract_review())

    assert rows
    assert all(row["Live calls"] == "Disabled" for row in rows)
    assert all(row["Generated candidates allowed"] == "No" for row in rows)
    assert all(row["Mature evidence allowed"] == "No" for row in rows)


def test_css_styles_includes_card_and_badge_classes():
    css = prototype.css_styles()

    assert ".cockpit-card" in css
    assert ".metric-card" in css
    assert ".candidate-card" in css
    assert ".badge" in css


def test_render_badges_html_returns_badge_html_without_raw_dictionary_output():
    html = prototype.render_badges_html(["alpha < beta"], tone="caution")

    assert '<span class="badge badge-caution">' in html
    assert "alpha &lt; beta" in html
    assert "{" not in html
    assert "}" not in html


def test_build_candidate_card_html_includes_identity_and_safety_note():
    card = prototype.build_candidate_board_cards(prototype.build_demo_cockpit_view_model())[0]

    html = prototype.build_candidate_card_html(card)

    assert "Ni superalloy + TBC reference" in html
    assert "Mature reference option" in html
    assert "Decision-support only" in html


def test_build_metric_card_html_includes_metric_label_and_value():
    metric = prototype.build_metric_card_models(prototype.build_demo_cockpit_view_model())[0]

    html = prototype.build_metric_card_html(metric)

    assert "Candidates" in html
    assert ">4<" in html


def test_helper_outputs_do_not_contain_forbidden_decision_fields():
    view_model = prototype.build_demo_cockpit_view_model()
    export_package = prototype.build_demo_review_export_package()
    feedback_package = prototype.build_demo_feedback_package()
    adapter_review = prototype.build_demo_adapter_contract_review()
    helper_outputs = {
        "metric_cards": prototype.build_metric_card_models(view_model),
        "candidate_cards": prototype.build_candidate_board_cards(view_model),
        "comparison": prototype.build_candidate_comparison_matrix(view_model),
        "validation": prototype.build_validation_burden_rows(view_model),
        "charts": prototype.build_chart_display_models(view_model),
        "review_summary": prototype.build_review_export_summary(export_package),
        "feedback": prototype.build_feedback_summary_rows(feedback_package),
        "adapters": prototype.build_adapter_summary_rows(adapter_review),
    }

    assert prototype.collect_forbidden_decision_fields(helper_outputs) == []


def test_prototype_does_not_import_app_ui_or_exporter_modules():
    modules = _imported_modules(_prototype_source())
    forbidden = {
        "app",
        "src.ui_view_models",
        "ui_view_models",
        "src.build4_review_pack_exporter",
        "build4_review_pack_exporter",
        "tools.build4_review_pack_exporter",
    }

    assert not [module for module in modules if module in forbidden]


def test_prototype_source_does_not_write_files_or_offer_downloads():
    source = _prototype_source()
    forbidden_snippets = [
        "open(",
        "Path(",
        "write_text",
        "write_bytes",
        "to_csv",
        "to_json",
        "download_button",
        "st.download",
    ]

    assert not [snippet for snippet in forbidden_snippets if snippet in source]


def test_prototype_source_does_not_contain_forbidden_action_labels():
    source = _prototype_source()
    forbidden_labels = [
        "Approve",
        "Certify",
        "Qualify",
        "Winner",
        "Best candidate",
    ]

    assert not [label for label in forbidden_labels if label in source]
