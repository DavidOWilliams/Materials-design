import json
from pathlib import Path

from tools.build4_review_pack_exporter import (
    FULL_REPORT_FILENAME,
    INDEX_FILENAME,
    PACKAGE_FILENAME,
    SECTION_FILENAMES,
    SUMMARY_FILENAME,
    VIEW_MODEL_FILENAME,
    build_full_build4_package,
    build_review_pack_summary,
    main,
    render_review_pack_index,
    split_full_report_into_sections,
    write_review_pack,
)
from src.ui_view_models import build_recommendation_package_view_model, render_markdown_report


def test_build_full_build4_package_returns_enriched_candidate_package():
    package = build_full_build4_package()

    assert package["candidate_systems"]
    assert package["process_route_summary"]
    assert package["surface_function_coverage_summary"]
    assert package["coating_spallation_adhesion_summary"]
    assert package["optimisation_summary"]
    assert package["coating_vs_gradient_diagnostic"]
    assert package["decision_readiness_summary"]
    assert package["recommendation_narrative"]
    assert package["application_profile"]["profile_id"] == "hot_section_thermal_cycling_oxidation"
    assert package["application_requirement_fit_summary"]
    assert package["application_limiting_factor_summary"]
    assert package["controlled_shortlist_summary"]
    assert package["validation_plan_summary"]
    assert all("application_requirement_fit" in candidate for candidate in package["candidate_systems"])
    assert all("application_limiting_factor_analysis" in candidate for candidate in package["candidate_systems"])


def test_exporter_default_run_uses_default_application_profile():
    package = build_full_build4_package()

    assert package["application_profile"]["profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_exporter_profile_argument_for_default_profile_succeeds():
    package = build_full_build4_package(profile_id="hot_section_thermal_cycling_oxidation")

    assert package["application_profile"]["profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_exporter_unknown_profile_fails_clearly():
    try:
        build_full_build4_package(profile_id="unknown_profile")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown profile.")

    assert "unknown_profile" in message
    assert "hot_section_thermal_cycling_oxidation" in message


def test_build_review_pack_summary_includes_review_metrics():
    package = build_full_build4_package()
    view_model = build_recommendation_package_view_model(package)
    summary = build_review_pack_summary(package, view_model)

    assert summary["candidate_count"] >= 30
    assert summary["coating_spallation_relevant_candidate_count"] > 0
    assert summary["exporter_status"] == "review_pack_created"
    assert summary["recommendation_narrative_status"] == "controlled_narrative_no_final_recommendation"
    assert summary["optimisation_status"] == "skeleton_no_variants_generated"
    assert summary["generated_candidate_count"] == 0
    assert summary["live_model_calls_made"] is False
    assert summary["ranked_recommendations_count"] == 0
    assert summary["pareto_front_count"] == 0
    assert summary["application_fit_status_counts"]
    assert summary["application_architecture_path_counts"]
    assert summary["application_limiting_factor_analysis_status_counts"]
    assert summary["controlled_shortlist_bucket_counts"]
    assert summary["validation_plan_category_counts"]


def test_render_review_pack_index_contains_required_disclaimers():
    index = render_review_pack_index(
        {
            "exporter_status": "review_pack_created",
            "candidate_count": 1,
            "generated_candidate_count": 0,
            "live_model_calls_made": False,
            "ranked_recommendations_count": 0,
            "pareto_front_count": 0,
        }
    ).lower()

    assert "build 4 material-system review pack" in index
    assert "not a final recommendation" in index
    assert "no final ranking" in index
    assert "no pareto optimisation" in index
    assert "no generated variants" in index
    assert "no live model calls" in index
    assert "not qualification or certification approval" in index


def test_split_full_report_into_expected_sections():
    package = build_full_build4_package()
    sections = split_full_report_into_sections(render_markdown_report(package))

    assert set(sections) == set(SECTION_FILENAMES)
    assert "Surface Function Coverage" in sections["surface_function_coverage"]
    assert "Process Route, Inspection and Repairability" in sections["process_route_inspection_repair"]
    assert "Coating Spallation, Adhesion and Repair" in sections["coating_spallation_adhesion"]
    assert "Deterministic Optimisation Skeleton" in sections["deterministic_optimisation_trace"]
    assert "Coating vs Gradient Diagnostic" in sections["coating_vs_gradient_diagnostic"]
    assert "Decision Readiness" in sections["decision_readiness"]
    assert "Controlled Recommendation Narrative" in sections["controlled_recommendation_narrative"]
    assert "Warnings And Deferred Capabilities" in sections["warnings_and_deferred_capabilities"]


def test_write_review_pack_creates_all_expected_files_and_json_loads(tmp_path):
    result = write_review_pack(tmp_path)

    expected_files = {
        INDEX_FILENAME,
        SUMMARY_FILENAME,
        PACKAGE_FILENAME,
        VIEW_MODEL_FILENAME,
        FULL_REPORT_FILENAME,
        *{f"sections/{filename}" for filename in SECTION_FILENAMES.values()},
    }
    written_relative = {str(Path(path).relative_to(tmp_path)) for path in result["files_written"]}

    assert expected_files == written_relative
    for relative_path in expected_files:
        assert (tmp_path / relative_path).is_file()

    with (tmp_path / SUMMARY_FILENAME).open(encoding="utf-8") as handle:
        summary = json.load(handle)
    with (tmp_path / PACKAGE_FILENAME).open(encoding="utf-8") as handle:
        package = json.load(handle)
    with (tmp_path / VIEW_MODEL_FILENAME).open(encoding="utf-8") as handle:
        view_model = json.load(handle)

    assert summary["candidate_count"] >= 30
    assert package["candidate_systems"]
    assert package["coating_spallation_adhesion_summary"]
    assert package["application_requirement_fit_summary"]
    assert package["application_limiting_factor_summary"]
    assert package["controlled_shortlist_summary"]
    assert package["validation_plan_summary"]
    assert view_model["candidate_cards"]
    assert view_model["coating_spallation_adhesion_summary_view"]["relevant_candidate_count"] > 0
    assert result["candidate_count"] >= 30
    assert result["generated_candidate_count"] == 0
    assert result["live_model_calls_made"] is False
    assert result["ranked_recommendations_count"] == 0
    assert result["pareto_front_count"] == 0
    assert result["application_profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_write_review_pack_profile_argument_for_default_profile_succeeds(tmp_path):
    result = write_review_pack(tmp_path, profile_id="hot_section_thermal_cycling_oxidation")

    assert result["application_profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_write_review_pack_index_and_sections_are_utf8_markdown(tmp_path):
    write_review_pack(tmp_path)

    index = (tmp_path / INDEX_FILENAME).read_text(encoding="utf-8").lower()
    full_report = (tmp_path / FULL_REPORT_FILENAME).read_text(encoding="utf-8").lower()
    assert "not a final recommendation" in index
    assert "not qualification or certification approval" in index
    assert "required primary service functions" in full_report
    assert "support / lifecycle considerations" in full_report
    assert "shared coating/gradient primary service functions" in full_report
    assert "coating spallation, adhesion and repair" in full_report
    assert "not a life prediction" in full_report
    assert "application requirement fit" in full_report
    assert "application limiting factors" in full_report
    assert "controlled shortlist" in full_report
    assert "validation plan" in full_report
    assert "validation plan is not qualification approval or certification approval" in full_report
    for filename in SECTION_FILENAMES.values():
        section = tmp_path / "sections" / filename
        assert section.is_file()
        assert section.read_text(encoding="utf-8").strip()


def test_main_quiet_returns_zero_and_writes_pack(tmp_path):
    assert main(["--output-dir", str(tmp_path), "--quiet"]) == 0

    assert (tmp_path / INDEX_FILENAME).is_file()
    assert (tmp_path / SUMMARY_FILENAME).is_file()


def test_exporter_main_profile_argument_succeeds(tmp_path):
    assert main(["--output-dir", str(tmp_path), "--profile", "hot_section_thermal_cycling_oxidation", "--quiet"]) == 0
    assert (tmp_path / PACKAGE_FILENAME).is_file()


def test_exporter_main_unknown_profile_exits_clearly(tmp_path, capsys):
    try:
        main(["--output-dir", str(tmp_path), "--profile", "unknown_profile", "--quiet"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected SystemExit for unknown profile.")

    captured = capsys.readouterr()
    assert "unknown_profile" in captured.err
    assert "hot_section_thermal_cycling_oxidation" in captured.err


def test_clean_output_dir_only_removes_files_inside_output_dir(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    stale_file = output_dir / "stale.txt"
    stale_file.write_text("old", encoding="utf-8")
    stale_subdir = output_dir / "old_sections"
    stale_subdir.mkdir()
    (stale_subdir / "old.md").write_text("old", encoding="utf-8")
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("keep", encoding="utf-8")

    write_review_pack(output_dir, clean_output_dir=True)

    assert not stale_file.exists()
    assert not stale_subdir.exists()
    assert outside_file.read_text(encoding="utf-8") == "keep"
    assert (output_dir / INDEX_FILENAME).is_file()


def test_review_pack_exporter_does_not_import_streamlit():
    source = Path("tools/build4_review_pack_exporter.py").read_text(encoding="utf-8").lower()

    assert "import streamlit" not in source
    assert "from streamlit" not in source
