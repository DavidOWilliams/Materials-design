from src.decision_engine import build_decision_package
from src.recommendation_builder import (
    build_package_from_candidate_source_package,
    build_recommendation_package,
    summarize_recommendation_package,
    validate_recommendation_package_shape,
)


def _schema():
    return {
        "schema_version": "2.0",
        "prompt_raw": "High temperature aviation material-system package test.",
        "coating_allowed": True,
        "composite_allowed": True,
        "graded_architecture_allowed": True,
        "research_generated_allowed": False,
        "ambiguities": [],
        "interpreter_trace": [],
    }


def _design_space(research_mode_enabled=False):
    return {
        "design_space_version": "test",
        "allowed_candidate_classes": [
            "metallic",
            "monolithic_ceramic",
            "ceramic_matrix_composite",
            "coating_enabled",
            "spatially_graded_am",
        ],
        "system_architectures": [
            "bulk_material",
            "composite_architecture",
            "substrate_plus_coating",
            "spatial_gradient",
        ],
        "architecture_flags": {
            "allow_bulk_material_only": True,
            "allow_substrate_plus_coating": True,
            "allow_spatial_gradients": True,
            "allow_composite_architecture": True,
            "allow_research_mode_candidates": research_mode_enabled,
        },
        "research_mode_enabled": research_mode_enabled,
        "generation_hints": {"live_model_calls_enabled": False},
    }


def _candidates():
    return [
        {
            "candidate_id": "metal-1",
            "candidate_class": "metallic",
            "name": "Ni superalloy comparison",
            "source_type": "engineering_analogue",
            "matched_alloy_name": "CMSX class",
            "evidence_maturity": "B",
        },
        {
            "candidate_id": "cmc-1",
            "candidate_class": "ceramic_matrix_composite",
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
            "candidate_id": "graded-1",
            "candidate_class": "spatially_graded_am",
            "system_architecture_type": "spatial_gradient",
            "name": "Exploratory thermal barrier gradient",
            "gradient_architecture": {"gradient_types": ["composition"], "notes": "transition zone"},
            "source_type": "curated_graded_template",
            "evidence_maturity": "E",
        },
    ]


def test_build_recommendation_package_preserves_candidate_count():
    candidates = _candidates()

    package = build_recommendation_package(_schema(), _design_space(), candidates)

    assert len(package["candidate_systems"]) == len(candidates)
    assert package["diagnostics"]["candidate_count_preserved"] is True
    assert [candidate["candidate_id"] for candidate in package["candidate_systems"]] == [
        "metal-1",
        "cmc-1",
        "graded-1",
    ]


def test_returned_package_has_required_keys():
    package = build_recommendation_package(_schema(), _design_space(), _candidates(), run_id="pkg-1")

    required_keys = {
        "run_id",
        "requirement_schema",
        "design_space",
        "candidate_systems",
        "ranked_recommendations",
        "pareto_front",
        "optimisation_summary",
        "source_mix_summary",
        "evidence_maturity_summary",
        "diagnostics",
        "warnings",
        "factor_summary",
        "system_assembly_summary",
        "package_status",
    }

    assert required_keys <= package.keys()
    assert package["run_id"] == "pkg-1"


def test_ranked_recommendations_and_pareto_front_are_empty_lists():
    package = build_recommendation_package(_schema(), _design_space(), _candidates())

    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []


def test_optimisation_summary_status_is_not_implemented():
    package = build_recommendation_package(_schema(), _design_space(), _candidates())

    assert package["optimisation_summary"]["status"] == "not_implemented"
    assert package["diagnostics"]["optimisation_performed"] is False
    assert package["diagnostics"]["ranking_performed"] is False


def test_package_includes_evidence_factor_and_system_assembly_summaries():
    package = build_recommendation_package(_schema(), _design_space(), _candidates())

    assert package["evidence_maturity_summary"]["candidate_count"] == 3
    assert package["factor_summary"]["candidate_count"] == 3
    assert package["system_assembly_summary"]["candidate_count"] == 3
    assert package["factor_summary"]["factor_namespace_counts"]["metal"] == 5
    assert package["system_assembly_summary"]["candidates_with_interfaces"] >= 2


def test_summarize_recommendation_package_returns_candidate_count_and_mix_fields():
    package = build_recommendation_package(_schema(), _design_space(), _candidates())

    summary = summarize_recommendation_package(package)

    assert summary["candidate_count"] == 3
    assert summary["candidate_class_mix"]["metallic"] == 1
    assert summary["candidate_class_mix"]["ceramic_matrix_composite"] == 1
    assert summary["system_architecture_mix"]["spatial_gradient"] == 1
    assert summary["evidence_maturity_mix"]["E"] == 1
    assert summary["factor_namespace_mix"]["graded_am"] == 6
    assert summary["ranked_recommendations_count"] == 0
    assert summary["pareto_front_count"] == 0
    assert summary["optimisation_status"] == "not_implemented"


def test_validate_recommendation_package_shape_returns_no_messages_for_valid_package():
    package = build_recommendation_package(_schema(), _design_space(), _candidates())

    assert validate_recommendation_package_shape(package) == []


def test_ef_evidence_maturity_causes_package_warning():
    package = build_recommendation_package(_schema(), _design_space(), _candidates())

    assert any("E/F" in warning for warning in package["warnings"])


def test_build_package_from_candidate_source_package_works_with_minimal_source_package():
    source_package = {
        "requirement_schema": _schema(),
        "design_space": _design_space(),
        "candidate_systems": _candidates()[:2],
        "source_mix_summary": {"total_candidate_count": 2},
        "diagnostics": {"source": "test_source_package"},
        "warnings": ["source warning"],
    }

    package = build_package_from_candidate_source_package(source_package, run_id="from-source")

    assert package["run_id"] == "from-source"
    assert len(package["candidate_systems"]) == 2
    assert package["source_mix_summary"]["total_candidate_count"] == 2
    assert "source warning" in package["warnings"]
    assert package["diagnostics"]["source"] == "test_source_package"


def test_decision_engine_placeholder_does_not_rank_or_optimise():
    package = build_decision_package(_schema(), _design_space(), _candidates(), run_id="decision-1")

    assert package["run_id"] == "decision-1"
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    assert package["optimisation_summary"]["status"] == "not_implemented"
    assert package["diagnostics"]["ranking_performed"] is False
    assert package["diagnostics"]["optimisation_performed"] is False
