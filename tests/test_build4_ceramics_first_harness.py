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


def test_harness_default_run_uses_default_application_profile(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["application_profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_harness_profile_argument_for_default_profile_succeeds(tmp_path):
    summary = build_outputs(tmp_path, profile_id="hot_section_thermal_cycling_oxidation")

    assert summary["application_profile_id"] == "hot_section_thermal_cycling_oxidation"
    with Path(summary["package_json_path"]).open(encoding="utf-8") as handle:
        package = json.load(handle)
    assert package["application_profile"]["profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_harness_unknown_profile_fails_clearly(tmp_path):
    try:
        build_outputs(tmp_path, profile_id="unknown_profile")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown profile.")

    assert "unknown_profile" in message
    assert "hot_section_thermal_cycling_oxidation" in message


def test_harness_main_profile_argument_succeeds(tmp_path):
    assert main(["--output-dir", str(tmp_path), "--profile", "hot_section_thermal_cycling_oxidation", "--quiet"]) == 0
    assert (tmp_path / PACKAGE_JSON_FILENAME).is_file()


def test_harness_main_unknown_profile_exits_clearly(tmp_path, capsys):
    try:
        main(["--output-dir", str(tmp_path), "--profile", "unknown_profile", "--quiet"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("Expected SystemExit for unknown profile.")

    captured = capsys.readouterr()
    assert "unknown_profile" in captured.err
    assert "hot_section_thermal_cycling_oxidation" in captured.err


def test_json_files_can_be_loaded_by_json_load(tmp_path):
    summary = build_outputs(tmp_path)

    with Path(summary["package_json_path"]).open(encoding="utf-8") as handle:
        package = json.load(handle)
    with Path(summary["view_model_json_path"]).open(encoding="utf-8") as handle:
        view_model = json.load(handle)

    assert package["candidate_systems"]
    assert view_model["candidate_cards"]
    assert package["optimisation_summary"]["status"] == "skeleton_no_variants_generated"
    assert package["optimisation_trace"]
    assert package["process_route_summary"]
    assert package["required_surface_functions"]
    assert package["surface_function_coverage_summary"]
    assert package["coating_spallation_adhesion_summary"]
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
    assert view_model["optimisation_summary_view"]["status"] == "skeleton_no_variants_generated"
    assert view_model["optimisation_trace_cards"]
    assert view_model["summary"]["process_route_summary"]


def test_markdown_report_contains_not_final_recommendation(tmp_path):
    summary = build_outputs(tmp_path)

    report = Path(summary["report_path"]).read_text(encoding="utf-8").lower()

    assert "not a final recommendation" in report
    assert "deterministic optimisation skeleton" in report
    assert "no variants were generated" in report
    assert "no final ranking was produced" in report
    assert "no pareto optimisation was performed" in report
    assert "research adapters are disabled" in report
    assert "not qualification-ready" in report
    assert "hard limits" in report
    assert "advisory warnings" in report
    assert "coating vs gradient comparison" in report
    assert "coating vs gradient diagnostic" in report
    assert "no winner selected" in report
    assert "surface function coverage" in report
    assert "decision readiness" in report
    assert "controlled recommendation narrative" in report
    assert "application requirement fit" in report
    assert "application limiting factors" in report
    assert "controlled shortlist" in report
    assert "validation plan" in report
    assert "validation plan is not qualification approval or certification approval" in report
    assert "not final recommendation" in report
    assert "process route, inspection and repairability" in report
    assert "coating spallation, adhesion and repair" in report
    assert "not a life prediction" in report


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


def test_optimisation_outputs_preserve_deferred_decision_fields(tmp_path):
    summary = build_outputs(tmp_path)

    with Path(summary["package_json_path"]).open(encoding="utf-8") as handle:
        package = json.load(handle)

    assert package["optimisation_summary"]["generated_candidate_count"] == 0
    assert package["optimisation_summary"]["live_model_calls_made"] is False
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    assert package["controlled_shortlist_summary"]["candidate_filtering_performed"] is False
    assert package["validation_plan_summary"]["candidate_filtering_performed"] is False
    assert package["validation_plan_summary"]["qualification_approval_granted"] is False
    assert package["validation_plan_summary"]["certification_approval_granted"] is False
    json.dumps(package)


def test_application_workflow_preserves_candidate_count_and_order(tmp_path):
    summary = build_outputs(tmp_path)

    with Path(summary["package_json_path"]).open(encoding="utf-8") as handle:
        package = json.load(handle)

    candidate_ids = [candidate["candidate_id"] for candidate in package["candidate_systems"]]
    assert len(candidate_ids) == summary["candidate_count"]
    assert candidate_ids == [candidate["candidate_id"] for candidate in package["candidate_systems"]]
    assert package["application_requirement_fit_summary"]["candidate_count"] == summary["candidate_count"]
    assert package["application_limiting_factor_summary"]["candidate_count"] == summary["candidate_count"]
    assert package["controlled_shortlist_summary"]["candidate_count"] == summary["candidate_count"]
    assert package["validation_plan_summary"]["candidate_count"] == summary["candidate_count"]
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    assert package["optimisation_summary"]["generated_candidate_count"] == 0
    assert package["validation_plan_summary"]["qualification_approval_granted"] is False
    assert package["validation_plan_summary"]["certification_approval_granted"] is False


def test_returned_summary_includes_required_optimisation_console_fields(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["optimisation_status"] == "skeleton_no_variants_generated"
    assert summary["total_limiting_factor_count"] > 0
    assert summary["total_refinement_option_count"] > 0
    assert summary["generated_candidate_count"] == 0
    assert summary["live_model_calls_made"] is False
    assert summary["coating_vs_gradient_comparison_required"] is True


def test_returned_summary_includes_process_route_counts(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["process_route_enriched_candidate_count"] == summary["candidate_count"]
    assert summary["high_inspection_burden_count"] > 0
    assert summary["limited_or_poor_repairability_count"] > 0
    assert summary["high_or_very_high_qualification_burden_count"] > 0


def test_returned_summary_includes_coating_vs_gradient_diagnostic_counts(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["coating_vs_gradient_diagnostic_status"] == "comparison_only_no_winner"
    assert summary["coating_vs_gradient_pairwise_count"] > 0
    assert summary["coating_profile_count"] > 0
    assert summary["gradient_profile_count"] > 0
    assert summary["shared_surface_function_themes"]


def test_returned_summary_includes_surface_function_counts(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["required_surface_function_count"] > 0
    assert summary["covered_required_surface_function_count"] > 0
    assert summary["unknown_surface_function_candidate_count"] == 0
    assert summary["shared_coating_gradient_function_count"] > 0


def test_returned_summary_includes_coating_spallation_counts(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["coating_spallation_relevant_candidate_count"] > 0
    assert summary["high_spallation_risk_candidate_count"] > 0


def test_returned_summary_includes_decision_readiness_counts(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["decision_readiness_category_counts"]
    assert summary["decision_readiness_status_counts"]
    assert summary["usable_as_reference_count"] > 0
    assert summary["exploratory_only_candidate_count"] > 0
    assert summary["not_decision_ready_count"] == 0


def test_returned_summary_includes_recommendation_narrative_counts(tmp_path):
    summary = build_outputs(tmp_path)

    assert summary["recommendation_narrative_status"] == "controlled_narrative_no_final_recommendation"
    assert summary["mature_comparison_reference_count"] > 0
    assert summary["engineering_analogue_option_count"] > 0
    assert summary["exploratory_option_count"] > 0
    assert summary["research_only_option_count"] > 0
    assert summary["not_decision_ready_option_count"] == 0


def test_main_quiet_returns_zero(tmp_path):
    assert main(["--output-dir", str(tmp_path), "--quiet"]) == 0
    assert (tmp_path / REPORT_FILENAME).is_file()


def test_harness_module_does_not_import_streamlit():
    source = Path("tools/build4_ceramics_first_harness.py").read_text(encoding="utf-8").lower()

    assert "import streamlit" not in source
    assert "from streamlit" not in source
