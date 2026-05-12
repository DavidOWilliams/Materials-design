import json
from pathlib import Path

from src.recommendation_builder import build_recommendation_package
from src.coating_vs_gradient_diagnostics import attach_coating_vs_gradient_diagnostic
from src.decision_readiness import attach_decision_readiness
from src.factor_models.coatings.spallation_adhesion import attach_coating_spallation_adhesion
from src.optimisation.deterministic_optimizer import attach_deterministic_optimisation
from src.process_route_enrichment import attach_process_route_enrichment
from src.recommendation_narrative import attach_recommendation_narrative
from src.surface_function_model import attach_surface_function_profiles
from src.validation_plan import build_validation_plan
import src.ui_view_models as ui_view_models
from src.ui_view_models import (
    build_candidate_card_view_model,
    build_coating_vs_gradient_view_model,
    build_optimisation_summary_view_model,
    build_package_summary_view_model,
    build_recommendation_package_view_model,
    package_to_json_safe_dict,
    render_markdown_report,
)


def _schema():
    return {
        "schema_version": "2.0",
        "prompt_raw": "Build 4 view model test",
        "coating_allowed": True,
        "composite_allowed": True,
        "graded_architecture_allowed": True,
        "research_generated_allowed": False,
        "ambiguities": [],
        "interpreter_trace": [],
    }


def _design_space():
    return {
        "design_space_version": "test",
        "allowed_candidate_classes": [
            "ceramic_matrix_composite",
            "coating_enabled",
            "spatially_graded_am",
        ],
        "system_architectures": [
            "composite_architecture",
            "substrate_plus_coating",
            "spatial_gradient",
        ],
        "architecture_flags": {
            "allow_substrate_plus_coating": True,
            "allow_spatial_gradients": True,
            "allow_composite_architecture": True,
            "allow_research_mode_candidates": False,
        },
        "research_mode_enabled": False,
    }


def _candidate_systems():
    return [
        {
            "candidate_id": "cmc-1",
            "candidate_class": "ceramic_matrix_composite",
            "system_architecture_type": "composite_architecture",
            "name": "SiC/SiC CMC with EBC",
            "constituents": [
                {"name": "SiC matrix", "role": "matrix"},
                {"name": "SiC fiber", "role": "fiber"},
                {"name": "BN interphase", "role": "interphase"},
            ],
            "environmental_barrier_coating": {"name": "rare-earth silicate EBC"},
            "source_type": "curated_engineering_reference",
            "evidence_maturity": "C",
        },
        {
            "candidate_id": "coating-1",
            "candidate_class": "coating_enabled",
            "system_architecture_type": "substrate_plus_coating",
            "name": "Ni superalloy with TBC",
            "coating_or_surface_system": {
                "coating_type": "thermal barrier coating",
                "failure_modes": ["spallation", "CTE mismatch"],
            },
            "source_type": "curated_coating_reference",
            "evidence_maturity": "B",
        },
        {
            "candidate_id": "graded-1",
            "candidate_class": "spatially_graded_am",
            "system_architecture_type": "spatial_gradient",
            "name": "Exploratory surface gradient",
            "gradient_architecture": {
                "gradient_types": ["composition"],
                "manufacturing_route": "directed energy deposition",
                "transition_risks": ["cracking"],
            },
            "source_type": "curated_graded_template",
            "evidence_maturity": "E",
        },
    ]


def _package():
    return build_recommendation_package(_schema(), _design_space(), _candidate_systems(), run_id="view-model-test")


def _optimised_package():
    return build_validation_plan(attach_recommendation_narrative(attach_decision_readiness(attach_coating_vs_gradient_diagnostic(
        attach_deterministic_optimisation(
            attach_coating_spallation_adhesion(
                attach_surface_function_profiles(attach_process_route_enrichment(_package()))
            )
        )
    ))))


def test_candidate_card_preserves_candidate_class_and_system_architecture_type():
    package = _package()
    card = build_candidate_card_view_model(package["candidate_systems"][0])

    assert card["candidate_class"] == "ceramic_matrix_composite"
    assert card["system_architecture_type"] == "composite_architecture"
    assert card["candidate_id"] == "cmc-1"


def test_coating_enabled_candidate_card_includes_coating_surface_summary():
    package = _package()
    coating = next(candidate for candidate in package["candidate_systems"] if candidate["candidate_id"] == "coating-1")
    card = build_candidate_card_view_model(coating)

    assert card["candidate_class"] == "coating_enabled"
    assert card["coating_or_surface_summary"]["present"] is True
    assert "thermal barrier" in card["coating_or_surface_summary"]["summary"].lower()


def test_spatially_graded_am_candidate_card_includes_gradient_summary():
    package = _package()
    graded = next(candidate for candidate in package["candidate_systems"] if candidate["candidate_id"] == "graded-1")
    card = build_candidate_card_view_model(graded)

    assert card["candidate_class"] == "spatially_graded_am"
    assert card["gradient_summary"]["present"] is True
    assert card["gradient_summary"]["gradient_types"] == ["composition"]


def test_cmc_ebc_candidate_remains_distinct_from_coating_and_graded_am():
    package = _package()
    cards = [build_candidate_card_view_model(candidate) for candidate in package["candidate_systems"]]
    by_id = {card["candidate_id"]: card for card in cards}

    assert by_id["cmc-1"]["candidate_class"] == "ceramic_matrix_composite"
    assert by_id["cmc-1"]["interface_summary"]["count"] >= 1
    assert by_id["coating-1"]["candidate_class"] == "coating_enabled"
    assert by_id["graded-1"]["candidate_class"] == "spatially_graded_am"
    assert by_id["cmc-1"]["system_architecture_type"] != by_id["coating-1"]["system_architecture_type"]
    assert by_id["cmc-1"]["system_architecture_type"] != by_id["graded-1"]["system_architecture_type"]


def test_package_summary_returns_candidate_count_and_mix_fields():
    summary = build_package_summary_view_model(_optimised_package())

    assert summary["candidate_count"] == 3
    assert summary["candidate_class_mix"]["coating_enabled"] == 1
    assert summary["system_architecture_mix"]["spatial_gradient"] == 1
    assert summary["evidence_maturity_mix"]["E"] == 1
    assert summary["factor_namespace_mix"]["graded_am"] == 6
    assert summary["live_model_calls_made"] is False
    assert summary["optimisation_status"] == "skeleton_no_variants_generated"
    assert summary["total_limiting_factor_count"] > 0
    assert summary["total_refinement_option_count"] > 0
    assert summary["generated_candidate_count"] == 0
    assert summary["coating_vs_gradient_comparison_required"] is True
    assert summary["process_route_summary"]["enriched_candidate_count"] == 3
    assert summary["coating_spallation_adhesion_summary"]["relevant_candidate_count"] > 0


def test_markdown_report_includes_not_final_recommendation():
    report = render_markdown_report(_optimised_package())

    assert "not a final recommendation" in report.lower()


def test_markdown_report_mentions_deterministic_optimisation_skeleton_boundaries():
    report = render_markdown_report(_optimised_package()).lower()

    assert "deterministic optimisation skeleton" in report
    assert "no variants were generated" in report
    assert "no final ranking was produced" in report
    assert "no pareto optimisation was performed" in report
    assert "no live model calls were made" in report
    assert "refinement operators are suggestions, not applied design changes" in report
    assert "hard limits" in report
    assert "advisory warnings" in report
    assert "evidence maturity constraints" in report
    assert "coating vs gradient comparison" in report
    assert "coating vs gradient diagnostic" in report
    assert "no winner selected" in report
    assert "surface function coverage" in report
    assert "decision readiness" in report
    assert "certification approval" in report
    assert "application requirement fit" in report
    assert "application limiting factors" in report
    assert "controlled shortlist" in report
    assert "validation plan is not qualification approval or certification approval" in report
    assert "process route, inspection and repairability" in report
    assert "coating spallation, adhesion and repair" in report
    assert "not a life prediction" in report


def test_markdown_report_mentions_research_adapters_disabled():
    report = render_markdown_report(_optimised_package()).lower()

    assert "research adapters are disabled" in report


def test_markdown_report_separates_primary_surface_functions_from_support_tags():
    report = render_markdown_report(_optimised_package()).lower()

    assert "required primary service functions" in report
    assert "support / lifecycle considerations" in report
    assert "shared coating/gradient primary service functions" in report
    assert "shared support considerations" in report


def test_package_to_json_safe_dict_can_be_serialized_with_json_dumps():
    package = _package()
    package["non_json_tuple"] = ("a", "b")
    package["non_json_set"] = {"x", "y"}
    package["non_json_object"] = object()

    safe = package_to_json_safe_dict(package)

    json.dumps(safe)
    assert safe["non_json_tuple"] == ["a", "b"]
    assert sorted(safe["non_json_set"]) == ["x", "y"]
    assert isinstance(safe["non_json_object"], str)


def test_no_candidates_are_filtered_out_by_view_model_creation():
    package = _optimised_package()
    view_model = build_recommendation_package_view_model(package)

    assert len(view_model["candidate_cards"]) == len(package["candidate_systems"])
    assert [card["candidate_id"] for card in view_model["candidate_cards"]] == [
        "cmc-1",
        "coating-1",
        "graded-1",
    ]


def test_view_model_includes_optimisation_summary_and_trace_cards():
    package = _optimised_package()
    view_model = build_recommendation_package_view_model(package)

    assert view_model["optimisation_summary_view"]["status"] == "skeleton_no_variants_generated"
    assert view_model["optimisation_summary_view"]["generated_candidate_count"] == 0
    assert view_model["optimisation_summary_view"]["live_model_calls_made"] is False
    assert view_model["optimisation_summary_view"]["full_limiting_factor_count"] >= (
        view_model["optimisation_summary_view"]["displayed_limiting_factor_count"]
    )
    assert "total_hard_limit_count" in view_model["optimisation_summary_view"]
    assert "total_advisory_warning_count" in view_model["optimisation_summary_view"]
    assert len(view_model["optimisation_trace_cards"]) == len(package["candidate_systems"])
    assert view_model["optimisation_trace_cards"][0]["top_limiting_factors"]
    assert view_model["optimisation_trace_cards"][0]["top_refinement_options"]
    assert len(view_model["optimisation_trace_cards"][0]["top_limiting_factors"]) <= 8
    assert len(view_model["optimisation_trace_cards"][0]["top_refinement_options"]) <= 6
    assert view_model["coating_vs_gradient_diagnostic_view"]["diagnostic_status"] == "comparison_only_no_winner"
    assert view_model["coating_spallation_adhesion_summary_view"]["relevant_candidate_count"] > 0
    assert view_model["coating_vs_gradient_diagnostic_view"]["pairwise_comparisons"]
    assert view_model["surface_function_coverage_view"]["required_surface_functions"]
    assert view_model["surface_function_coverage_view"]["shared_coating_gradient_functions"]
    assert view_model["surface_function_coverage_view"]["primary_service_function_to_candidate_ids"]
    assert view_model["surface_function_coverage_view"]["support_consideration_to_candidate_ids"]
    assert "shared_coating_gradient_primary_service_functions" in view_model["surface_function_coverage_view"]
    assert "shared_coating_gradient_support_considerations" in view_model["surface_function_coverage_view"]
    assert view_model["decision_readiness_summary_view"]["readiness_category_counts"]
    assert view_model["decision_readiness_summary_view"]["readiness_status_counts"]
    assert view_model["recommendation_narrative_view"]["narrative_status"] == (
        "controlled_narrative_no_final_recommendation"
    )
    assert len(view_model["recommendation_narrative_view"]["candidate_narrative_cards"]) == len(
        package["candidate_systems"]
    )


def test_candidate_cards_include_process_route_fields():
    package = _optimised_package()
    view_model = build_recommendation_package_view_model(package)
    by_id = {card["candidate_id"]: card for card in view_model["candidate_cards"]}

    assert by_id["cmc-1"]["process_route_display_name"]
    assert by_id["cmc-1"]["process_family"]
    assert by_id["cmc-1"]["inspection_burden"] in {"high", "medium", "unknown"}
    assert isinstance(by_id["cmc-1"]["inspection_methods"], list)
    assert by_id["cmc-1"]["repairability_level"] in {"limited", "poor", "moderate", "unknown"}
    assert by_id["cmc-1"]["qualification_burden"] in {"high", "very_high", "unknown"}
    assert isinstance(by_id["cmc-1"]["route_risks"], list)
    assert isinstance(by_id["cmc-1"]["route_validation_gaps"], list)
    assert by_id["cmc-1"]["primary_surface_functions"]
    assert by_id["cmc-1"]["primary_service_functions"]
    assert isinstance(by_id["cmc-1"]["support_or_lifecycle_considerations"], list)
    assert isinstance(by_id["cmc-1"]["risk_or_interface_considerations"], list)
    assert by_id["cmc-1"]["unknown_surface_function_flag"] is False
    assert by_id["cmc-1"]["readiness_category"]
    assert by_id["cmc-1"]["readiness_label"]
    assert by_id["cmc-1"]["readiness_status"]
    assert by_id["cmc-1"]["allowed_use"]
    assert by_id["cmc-1"]["disallowed_use"]
    assert by_id["cmc-1"]["required_next_evidence"]
    assert isinstance(by_id["cmc-1"]["top_readiness_constraints"], list)
    assert by_id["cmc-1"]["narrative_role"]
    assert by_id["cmc-1"]["responsible_use"]
    assert isinstance(by_id["cmc-1"]["main_strengths"], list)
    assert isinstance(by_id["cmc-1"]["main_cautions"], list)
    assert isinstance(by_id["cmc-1"]["evidence_gaps"], list)


def test_optimisation_summary_view_model_preserves_empty_ranking_and_pareto_boundary():
    package = _optimised_package()
    summary = build_optimisation_summary_view_model(package)

    assert summary["status"] == "skeleton_no_variants_generated"
    assert summary["generated_candidate_count"] == 0
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []


def test_coating_vs_gradient_view_model_lists_candidate_ids_and_shared_themes():
    comparison = build_coating_vs_gradient_view_model(_optimised_package())

    assert comparison["comparison_required"] is True
    assert comparison["coating_enabled_candidate_ids"] == ["coating-1"]
    assert comparison["spatial_gradient_candidate_ids"] == ["graded-1"]
    assert isinstance(comparison["shared_limiting_factor_themes"], list)


def test_view_models_do_not_import_streamlit():
    source = Path(ui_view_models.__file__).read_text(encoding="utf-8")
    assert "import streamlit" not in source.lower()
    assert "from streamlit" not in source.lower()
    assert "streamlit" not in ui_view_models.__dict__
