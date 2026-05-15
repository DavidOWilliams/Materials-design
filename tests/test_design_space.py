from src.design_space import build_design_space


def test_build_design_space_sets_coating_gradient_comparison_flag():
    design_space = build_design_space(
        {
            "schema_version": "v2",
            "prompt_raw": "Hot wear seal with coating and gradient options.",
            "coating_allowed": True,
            "graded_architecture_allowed": True,
            "manufacturing": {
                "preferred_routes": ["laser powder bed fusion"],
                "disallowed_routes": ["casting"],
            },
            "environment": {
                "hot_corrosion": True,
                "wear_or_sliding_contact": True,
            },
        }
    )

    assert design_space["architecture_flags"]["allow_substrate_plus_coating"] is True
    assert design_space["architecture_flags"]["allow_spatial_gradients"] is True
    assert design_space["coating_vs_gradient_comparison_required"] is True
    assert "coating_enabled" in design_space["allowed_candidate_classes"]
    assert "spatially_graded_am" in design_space["allowed_candidate_classes"]
    assert design_space["research_mode_enabled"] is False
    assert design_space["generation_hints"]["candidate_generation_enabled"] is False
    assert design_space["generation_hints"]["live_model_calls_enabled"] is False


def test_build_design_space_keeps_research_mode_disabled_by_default():
    design_space = build_design_space(
        {
            "schema_version": "v2",
            "prompt_raw": "Select a conventional mature structural aviation material.",
            "design_intent": "selection",
        }
    )

    assert design_space["architecture_flags"]["allow_bulk_material_only"] is True
    assert design_space["architecture_flags"]["allow_research_mode_candidates"] is False
    assert design_space["research_mode_enabled"] is False
    assert "research_generated" not in design_space["allowed_candidate_classes"]


def test_build_design_space_enables_research_only_when_explicit():
    design_space = build_design_space(
        {
            "schema_version": "v2",
            "prompt_raw": "Explore a generated high temperature material concept.",
            "research_generated_allowed": True,
        }
    )

    assert design_space["architecture_flags"]["allow_research_mode_candidates"] is True
    assert design_space["research_mode_enabled"] is True
    assert "research_generated" in design_space["allowed_candidate_classes"]
