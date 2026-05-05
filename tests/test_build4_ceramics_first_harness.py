import json
from pathlib import Path

from tools.build4_ceramics_first_harness import (
    PACKAGE_JSON_FILENAME,
    REPORT_FILENAME,
    VIEW_MODEL_JSON_FILENAME,
    build_outputs,
    main,
)


def test_build_outputs_creates_all_expected_files(tmp_path):
    summary = build_outputs(tmp_path)

    assert Path(summary["report_path"]).is_file()
    assert Path(summary["package_json_path"]).is_file()
    assert Path(summary["view_model_json_path"]).is_file()
    assert (tmp_path / REPORT_FILENAME).is_file()
    assert (tmp_path / PACKAGE_JSON_FILENAME).is_file()
    assert (tmp_path / VIEW_MODEL_JSON_FILENAME).is_file()


def test_json_files_can_be_loaded_by_json_load(tmp_path):
    summary = build_outputs(tmp_path)

    with Path(summary["package_json_path"]).open(encoding="utf-8") as handle:
        package = json.load(handle)
    with Path(summary["view_model_json_path"]).open(encoding="utf-8") as handle:
        view_model = json.load(handle)

    assert package["candidate_systems"]
    assert view_model["candidate_cards"]


def test_markdown_report_contains_not_final_recommendation(tmp_path):
    summary = build_outputs(tmp_path)

    report = Path(summary["report_path"]).read_text(encoding="utf-8").lower()

    assert "not a final recommendation" in report
    assert "ranking is not implemented" in report
    assert "optimisation is not implemented" in report
    assert "research adapters are disabled" in report
    assert "not qualification-ready" in report


def test_returned_summary_includes_candidate_count_greater_than_zero(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["candidate_count"] > 0
    assert summary["candidate_class_mix"]
    assert summary["system_architecture_mix"]
    assert summary["evidence_maturity_mix"]


def test_returned_summary_has_research_mode_disabled(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["research_mode_enabled"] is False


def test_live_model_calls_made_is_false(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["live_model_calls_made"] is False


def test_main_quiet_returns_zero(tmp_path):
    assert main(["--output-dir", str(tmp_path), "--quiet"]) == 0
    assert (tmp_path / REPORT_FILENAME).is_file()


def test_harness_module_does_not_import_streamlit():
    source = Path("tools/build4_ceramics_first_harness.py").read_text(encoding="utf-8").lower()

    assert "import streamlit" not in source
    assert "from streamlit" not in source
