import ast
from pathlib import Path

from src.phase5_cockpit_review_export import run_phase5_cockpit_review_export
from src.phase5_decision_cockpit_view_models import (
    run_phase5_decision_cockpit_view_model,
)
from src.phase5_feedback_records import run_phase5_feedback_records
from src.phase5_specialist_model_adapters import (
    adapter_contract_review_summary,
    build_specialist_adapter_registry,
    candidate_allowed_for_mature_recommendation,
    run_disabled_specialist_adapter_contract_review,
    wrap_research_generated_candidate,
)


FORBIDDEN_OUTPUT_FIELDS = {
    "score",
    "rank",
    "winner",
    "certification_approval",
    "qualification_approval",
}


def _simple_candidates():
    return [
        {
            "candidate_id": "C-1",
            "system_name": "Nickel DED system 1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
            "limiting_factors": ["oxidation"],
        },
        {
            "candidate_id": "C-2",
            "system_name": "Nickel DED system 2",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
            "limiting_factors": ["wear"],
        },
    ]


def _collect_forbidden_paths(value, *, path="root"):
    hits = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if key in FORBIDDEN_OUTPUT_FIELDS:
                hits.append(next_path)
            hits.extend(_collect_forbidden_paths(item, path=next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(_collect_forbidden_paths(item, path=f"{path}[{index}]"))
    return hits


def _imported_modules(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_phase5_decision_cockpit_view_model_runs_end_to_end_on_two_candidates():
    view_model = run_phase5_decision_cockpit_view_model(_simple_candidates())

    assert view_model["candidate_count"] == 2
    assert [card["candidate_id"] for card in view_model["cards"]] == ["C-1", "C-2"]


def test_phase5_cockpit_review_export_runs_end_to_end_on_two_candidates():
    package = run_phase5_cockpit_review_export(_simple_candidates())

    assert package["manifest"]["candidate_count"] == 2
    assert [summary["candidate_id"] for summary in package["candidate_summaries"]] == [
        "C-1",
        "C-2",
    ]
    assert package["markdown_report"].startswith("# Phase 5 Cockpit Review Export")


def test_phase5_feedback_records_runs_end_to_end_on_two_candidates():
    package = run_phase5_feedback_records(_simple_candidates())

    assert package["candidate_count"] == 2
    assert [summary["candidate_id"] for summary in package["feedback_summaries"]] == [
        "C-1",
        "C-2",
    ]


def test_disabled_specialist_adapter_contract_review_reports_safe_registry():
    review = run_disabled_specialist_adapter_contract_review()

    assert review["summary"]["registry_safe"] is True
    assert adapter_contract_review_summary(build_specialist_adapter_registry())[
        "registry_safe"
    ] is True


def test_research_generated_specialist_candidate_is_blocked_from_mature_paths():
    candidate = wrap_research_generated_candidate(
        source_adapter_id="mattergen_candidate_generator",
        candidate_label="Research placeholder",
        candidate_payload={"composition_family": "placeholder"},
    )

    assert candidate["evidence_maturity"] == "F"
    assert candidate["blocked_from_mature_recommendation"] is True
    assert candidate_allowed_for_mature_recommendation(candidate) is False


def test_phase5_smoke_outputs_do_not_contain_decision_or_approval_fields():
    outputs = [
        run_phase5_decision_cockpit_view_model(_simple_candidates()),
        run_phase5_cockpit_review_export(_simple_candidates()),
        run_phase5_feedback_records(_simple_candidates()),
        run_disabled_specialist_adapter_contract_review(),
        wrap_research_generated_candidate(
            source_adapter_id="property_surrogate_estimator",
            candidate_label="Research placeholder",
        ),
    ]

    assert _collect_forbidden_paths(outputs) == []


def test_specialist_adapter_module_has_no_project_imports():
    modules = _imported_modules("src/phase5_specialist_model_adapters.py")

    assert not [module for module in modules if module == "src" or module.startswith("src.")]


def test_phase5_smoke_test_does_not_import_app_ui_or_existing_exporters():
    modules = _imported_modules(__file__)
    forbidden_modules = {
        "app",
        "src.ui_view_models",
        "ui_view_models",
        "tools.build4_review_pack_exporter",
        "build4_review_pack_exporter",
        "src.build4_review_pack_exporter",
    }

    assert not [module for module in modules if module in forbidden_modules]
