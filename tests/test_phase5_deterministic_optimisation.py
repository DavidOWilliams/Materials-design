from copy import deepcopy

from src.deterministic_optimisation import (
    build_optimisation_opportunities,
    candidate_identifier,
    candidate_system_name,
    limiting_factors_for_candidate,
    normalise_token,
    process_routes,
    run_deterministic_optimisation,
)


def test_normalise_token_handles_spaces_hyphens_casing_and_none():
    assert normalise_token(" Surface Oxidation-Limit ") == "surface_oxidation_limit"
    assert normalise_token(None) == ""


def test_candidate_identifier_uses_candidate_id_then_id_then_fallback():
    assert candidate_identifier({"candidate_id": "C-1", "id": "legacy"}, 7) == "C-1"
    assert candidate_identifier({"id": "legacy"}, 7) == "legacy"
    assert candidate_identifier({}, 7) == "candidate_7"


def test_candidate_system_name_uses_system_name_then_name_then_fallback():
    assert candidate_system_name({"system_name": "System A", "name": "Legacy"}, "C-1") == "System A"
    assert candidate_system_name({"name": "Legacy"}, "C-1") == "Legacy"
    assert candidate_system_name({}, "C-1") == "C-1"


def test_process_routes_extracts_route_name_and_route_family_from_process_route_mapping():
    candidate = {
        "process_route": {
            "route_name": "DED",
            "route_family": "additive_manufacturing",
            "ignored": "not returned",
        }
    }

    assert process_routes(candidate) == ["DED", "additive_manufacturing"]


def test_limiting_factors_for_candidate_prioritises_supplied_limiting_factors():
    candidate = {"limiting_factors": ["wear"], "limiting_factor_ids": ["oxidation"]}

    assert limiting_factors_for_candidate(
        candidate,
        supplied_limiting_factors=["thermal_barrier"],
    ) == ["thermal_barrier"]


def test_build_optimisation_opportunities_returns_no_limiting_factors_supplied():
    assessment = build_optimisation_opportunities(
        {"candidate_id": "C-1"},
        limiting_factors=[],
    )

    assert assessment["optimisation_status"] == "no_limiting_factors_supplied"
    assert assessment["optimisation_opportunities"] == []


def test_build_optimisation_opportunities_identifies_coating_and_gradient_for_oxidation():
    assessment = build_optimisation_opportunities(
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
        },
        limiting_factors=["oxidation"],
        research_mode_enabled=False,
    )

    opportunities = assessment["optimisation_opportunities"]
    assert assessment["optimisation_status"] == "deterministic_opportunities_identified"
    assert [item["opportunity_family"] for item in opportunities] == [
        "coating",
        "spatial_gradient",
    ]
    assert [item["source_id"] for item in opportunities] == [
        "oxidation_protection_coating",
        "surface_oxidation_gradient",
    ]


def test_build_optimisation_opportunities_does_not_select_winner_or_include_ranked_field():
    assessment = build_optimisation_opportunities(
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
        },
        limiting_factors=["oxidation"],
    )

    assert "winner" not in assessment
    assert "ranked_opportunities" not in assessment
    assert "selected_opportunity" not in assessment
    for opportunity in assessment["optimisation_opportunities"]:
        assert "rank" not in opportunity
        assert "score" not in opportunity
        assert "winner" not in opportunity


def test_build_optimisation_opportunities_excludes_research_mode_only_gradient_when_disabled():
    assessment = build_optimisation_opportunities(
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
        },
        limiting_factors=["thermal_barrier"],
        research_mode_enabled=False,
    )

    assert "thermal_barrier_gradient" not in [
        item["source_id"] for item in assessment["optimisation_opportunities"]
    ]


def test_build_optimisation_opportunities_includes_research_mode_only_gradient_when_enabled():
    assessment = build_optimisation_opportunities(
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
        },
        limiting_factors=["thermal_barrier"],
        research_mode_enabled=True,
    )

    thermal_barrier = [
        item
        for item in assessment["optimisation_opportunities"]
        if item["source_id"] == "thermal_barrier_gradient"
    ][0]
    assert thermal_barrier["status"] == "research_mode_only"
    assert assessment["optimisation_status"] == "research_mode_opportunities_identified"


def test_run_deterministic_optimisation_preserves_candidate_order():
    run = run_deterministic_optimisation(
        [
            {"candidate_id": "C-1", "limiting_factors": []},
            {"candidate_id": "C-2", "limiting_factors": []},
        ]
    )

    assert [item["candidate_id"] for item in run["candidate_assessments"]] == ["C-1", "C-2"]


def test_run_deterministic_optimisation_uses_candidate_limiting_factors_over_default():
    run = run_deterministic_optimisation(
        [
            {
                "candidate_id": "C-1",
                "candidate_class": "metallic",
                "substrate_family": "nickel_alloy",
                "process_route": {"route_name": "DED"},
            }
        ],
        limiting_factors_by_candidate={"C-1": ["oxidation"]},
        default_limiting_factors=["wear"],
    )

    assessment = run["candidate_assessments"][0]
    assert assessment["limiting_factors"] == ["oxidation"]
    assert [item["source_id"] for item in assessment["optimisation_opportunities"]] == [
        "oxidation_protection_coating",
        "surface_oxidation_gradient",
    ]


def test_run_deterministic_optimisation_returns_opportunity_count_sum():
    run = run_deterministic_optimisation(
        [
            {
                "candidate_id": "C-1",
                "candidate_class": "metallic",
                "substrate_family": "nickel_alloy",
                "process_route": {"route_name": "DED"},
                "limiting_factors": ["oxidation"],
            },
            {"candidate_id": "C-2", "limiting_factors": []},
        ]
    )

    assert run["opportunity_count"] == sum(
        len(item["optimisation_opportunities"]) for item in run["candidate_assessments"]
    )


def test_run_deterministic_optimisation_summary_includes_counts_by_optimisation_status():
    run = run_deterministic_optimisation(
        [
            {"candidate_id": "C-1", "limiting_factors": []},
            {
                "candidate_id": "C-2",
                "candidate_class": "metallic",
                "substrate_family": "nickel_alloy",
                "process_route": {"route_name": "DED"},
                "limiting_factors": ["oxidation"],
            },
        ]
    )

    by_status = run["optimisation_summary"]["by_optimisation_status"]
    assert by_status["no_limiting_factors_supplied"] == 1
    assert by_status["deterministic_opportunities_identified"] == 1


def test_run_deterministic_optimisation_does_not_mutate_input_candidates():
    candidates = [
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_routes": ["DED"],
            "limiting_factors": ["oxidation"],
        }
    ]
    original = deepcopy(candidates)

    run_deterministic_optimisation(candidates)

    assert candidates == original


def test_research_mode_enabled_true_adds_run_level_warning():
    run = run_deterministic_optimisation([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_no_matching_limiting_factor_produces_no_deterministic_opportunity():
    assessment = build_optimisation_opportunities(
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
        },
        limiting_factors=["unobtainium_shortage"],
    )

    assert assessment["optimisation_status"] == "no_deterministic_opportunity"
    assert assessment["optimisation_opportunities"] == []


def test_opportunities_include_required_review_fields_for_coating_and_spatial_gradient():
    assessment = build_optimisation_opportunities(
        {
            "candidate_id": "C-1",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED"},
        },
        limiting_factors=["oxidation"],
    )

    coating = assessment["optimisation_opportunities"][0]
    gradient = assessment["optimisation_opportunities"][1]

    assert coating["opportunity_family"] == "coating"
    assert set(coating["review_required"]) == {
        "substrate_interface_review",
        "inspection_review",
        "repair_review",
        "evidence_review",
    }
    assert gradient["opportunity_family"] == "spatial_gradient"
    assert set(gradient["review_required"]) == {
        "gradient_feasibility_review",
        "transition_zone_review",
        "inspection_review",
        "repair_review",
        "maturity_review",
    }
