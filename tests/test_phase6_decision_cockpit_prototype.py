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
