import pandas as pd

from src.source_orchestrator import (
    BUILD31_METALLIC_SOURCE,
    CERAMIC_REFERENCE_SOURCE,
    CMC_REFERENCE_SOURCE,
    COATING_ENABLED_REFERENCE_SOURCE,
    GRADED_AM_TEMPLATE_SOURCE,
    generate_candidate_sources,
    summarise_source_mix,
)


def _design_space(
    *,
    classes=None,
    architectures=None,
    gradients=False,
    composites=True,
    coatings=True,
    research=False,
):
    allowed_classes = (
        [
            "monolithic_ceramic",
            "ceramic_matrix_composite",
            "coating_enabled",
        ]
        if classes is None
        else classes
    )
    allowed_architectures = (
        ["bulk_material", "composite_architecture", "substrate_plus_coating"]
        if architectures is None
        else architectures
    )
    return {
        "allowed_candidate_classes": allowed_classes,
        "allowed_system_classes": allowed_classes,
        "system_architectures": allowed_architectures,
        "architecture_flags": {
            "allow_spatial_gradients": gradients,
            "allow_composite_architecture": composites,
            "allow_substrate_plus_coating": coatings,
            "allow_research_mode_candidates": research,
        },
        "research_mode_enabled": research,
    }


def test_build31_rows_are_wrapped_only_when_dataframe_is_supplied():
    design_space = _design_space(classes=[], architectures=[], composites=False, coatings=False)

    without_df = generate_candidate_sources(design_space=design_space)
    assert without_df["diagnostics"]["build31_adapter_used"] is False
    assert without_df["diagnostics"]["build31_metallic_count"] == 0
    assert without_df["candidate_systems"] == []

    df = pd.DataFrame(
        [
            {
                "candidate_id": "metal-1",
                "candidate_source": "engineering_analogue",
                "matched_alloy_name": "IN718",
                "composition_concept": "Engineering analogue: IN718",
            }
        ]
    )
    with_df = generate_candidate_sources(design_space=design_space, build31_candidates_df=df)

    assert with_df["diagnostics"]["build31_adapter_used"] is True
    assert with_df["diagnostics"]["build31_metallic_count"] == 1
    assert with_df["candidate_systems"][0]["candidate_id"] == "metal-1"
    assert with_df["candidate_systems"][0]["source_label"] == BUILD31_METALLIC_SOURCE


def test_source_mix_summary_distinguishes_enabled_sources():
    df = pd.DataFrame(
        [
            {
                "candidate_id": "metal-1",
                "candidate_source": "engineering_analogue",
                "matched_alloy_name": "IN718",
            }
        ]
    )
    design_space = _design_space(
        classes=[
            "monolithic_ceramic",
            "ceramic_matrix_composite",
            "coating_enabled",
            "spatially_graded_am",
        ],
        architectures=[
            "bulk_material",
            "composite_architecture",
            "substrate_plus_coating",
            "spatial_gradient",
        ],
        gradients=True,
    )

    result = generate_candidate_sources(design_space=design_space, build31_candidates_df=df)
    summary = result["source_mix_summary"]

    assert summary["source_counts"][BUILD31_METALLIC_SOURCE] == 1
    assert summary["source_counts"][CERAMIC_REFERENCE_SOURCE] >= 1
    assert summary["source_counts"][CMC_REFERENCE_SOURCE] >= 1
    assert summary["source_counts"][COATING_ENABLED_REFERENCE_SOURCE] >= 1
    assert summary["source_counts"][GRADED_AM_TEMPLATE_SOURCE] >= 1
    assert summarise_source_mix(result["candidate_systems"]) == summary


def test_graded_am_candidates_are_absent_when_spatial_gradients_are_false():
    result = generate_candidate_sources(design_space=_design_space(gradients=False))

    assert result["diagnostics"]["graded_am_template_count"] == 0
    assert GRADED_AM_TEMPLATE_SOURCE not in result["source_mix_summary"]["source_counts"]


def test_graded_am_candidates_are_present_when_spatial_gradients_are_true():
    design_space = _design_space(
        classes=["spatially_graded_am"],
        architectures=["spatial_gradient"],
        gradients=True,
        composites=False,
        coatings=False,
    )

    result = generate_candidate_sources(design_space=design_space)

    assert result["diagnostics"]["graded_am_template_count"] >= 1
    assert result["source_mix_summary"]["source_counts"][GRADED_AM_TEMPLATE_SOURCE] >= 1
    assert all(
        candidate["candidate_class"] == "spatially_graded_am"
        for candidate in result["candidate_systems"]
    )


def test_research_mode_enabled_does_not_trigger_live_model_calls():
    design_space = _design_space(research=True)

    result = generate_candidate_sources(design_space=design_space)

    assert result["diagnostics"]["research_mode_enabled"] is True
    assert result["diagnostics"]["live_model_calls_made"] is False
    assert result["diagnostics"]["materials_project_calls_made"] is False
    assert any("research adapters are disabled" in warning for warning in result["warnings"])


def test_no_candidates_warning_with_restrictive_design_space():
    restrictive_design_space = _design_space(
        classes=[],
        architectures=[],
        gradients=False,
        composites=False,
        coatings=False,
    )

    result = generate_candidate_sources(design_space=restrictive_design_space)

    assert result["candidate_systems"] == []
    assert result["diagnostics"]["total_candidate_count"] == 0
    assert result["warnings"] == [
        "No Build 4 candidate systems were returned by enabled sources."
    ]
