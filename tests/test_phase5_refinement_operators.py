from copy import deepcopy

from src.refinement_operators import (
    build_before_state,
    build_refinement_proposal,
    build_refinement_proposals_for_candidate,
    candidate_id,
    operator_for_opportunity,
    proposed_after_state,
    run_refinement_proposals,
    system_name,
)


def _candidate() -> dict:
    return {
        "candidate_id": "C-1",
        "system_name": "Nickel DED System",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "evidence_package": {"coupon": {"status": "screened"}},
    }


def _coating_opportunity() -> dict:
    return {
        "opportunity_id": "C-1:coating:oxidation_protection_coating",
        "candidate_id": "C-1",
        "opportunity_family": "coating",
        "opportunity_type": "oxidation_protection_coating",
        "source_id": "oxidation_protection_coating",
        "source_name": "Oxidation protection coating",
        "source_maturity": "deterministic_reference",
        "research_mode_required": False,
        "expected_benefits": ["reduced oxidation exposure"],
        "introduced_risks": ["coating spallation"],
        "review_required": ["substrate_interface_review"],
        "status": "available_for_deterministic_review",
        "warnings": [],
    }


def _gradient_opportunity() -> dict:
    return {
        "opportunity_id": "C-1:spatial_gradient:surface_oxidation_gradient",
        "candidate_id": "C-1",
        "opportunity_family": "spatial_gradient",
        "opportunity_type": "surface_oxidation_gradient",
        "source_id": "surface_oxidation_gradient",
        "source_name": "Surface oxidation gradient",
        "source_maturity": "research_template",
        "research_mode_required": True,
        "expected_benefits": ["graded oxidation resistance"],
        "introduced_risks": ["gradient inspection complexity"],
        "review_required": ["gradient_feasibility_review"],
        "status": "research_mode_only",
        "warnings": ["Research-mode-only opportunity requires gated review."],
    }


def test_candidate_id_uses_candidate_id_then_id_then_fallback():
    assert candidate_id({"candidate_id": "C-1", "id": "legacy"}, 7) == "C-1"
    assert candidate_id({"id": "legacy"}, 7) == "legacy"
    assert candidate_id({}, 7) == "candidate_7"


def test_system_name_uses_system_name_then_name_then_fallback():
    assert system_name({"system_name": "System A", "name": "Legacy"}, "C-1") == "System A"
    assert system_name({"name": "Legacy"}, "C-1") == "Legacy"
    assert system_name({}, "C-1") == "C-1"


def test_build_before_state_deep_copies_nested_surface_and_gradient_state():
    candidate = {
        "coating_or_surface_system": {"layers": [{"name": "bond coat"}]},
        "gradient_architecture": {"zones": [{"name": "surface"}]},
    }

    before = build_before_state(candidate)
    before["coating_or_surface_system"]["layers"][0]["name"] = "changed"
    before["gradient_architecture"]["zones"][0]["name"] = "changed"

    assert candidate["coating_or_surface_system"]["layers"][0]["name"] == "bond coat"
    assert candidate["gradient_architecture"]["zones"][0]["name"] == "surface"


def test_operator_for_opportunity_maps_oxidation_protection_coating():
    assert (
        operator_for_opportunity({"source_id": "oxidation_protection_coating"})
        == "add_oxidation_protection_coating"
    )


def test_operator_for_opportunity_maps_surface_oxidation_gradient():
    assert (
        operator_for_opportunity({"source_id": "surface_oxidation_gradient"})
        == "add_surface_oxidation_gradient"
    )


def test_operator_for_opportunity_returns_unsupported_for_unknown_source_id():
    assert operator_for_opportunity({"source_id": "unknown_option"}) == "unsupported_opportunity_type"


def test_proposed_after_state_for_coating_adds_surface_system_and_architecture():
    after = proposed_after_state(
        {"system_architecture_type": "monolithic", "process_route": {}, "evidence_package": {}},
        _coating_opportunity(),
    )

    assert after["system_architecture_type"] == "coating_enabled"
    assert after["coating_or_surface_system"]["option_id"] == "oxidation_protection_coating"
    assert after["coating_or_surface_system"]["known_risks"] == ["coating spallation"]


def test_proposed_after_state_for_spatial_gradient_adds_gradient_and_architecture():
    after = proposed_after_state(
        {"system_architecture_type": "monolithic", "process_route": {}, "evidence_package": {}},
        _gradient_opportunity(),
    )

    assert after["system_architecture_type"] == "spatially_graded_am_system"
    assert after["gradient_architecture"]["gradient_template_id"] == "surface_oxidation_gradient"
    assert after["gradient_architecture"]["research_mode_required"] is True


def test_proposed_after_state_does_not_mutate_before_state():
    before = {
        "system_architecture_type": "monolithic",
        "coating_or_surface_system": {"existing": True},
        "process_route": {},
        "evidence_package": {},
    }
    original = deepcopy(before)

    proposed_after_state(before, _coating_opportunity())

    assert before == original


def test_build_refinement_proposal_creates_review_status_for_deterministic_coating():
    proposal = build_refinement_proposal(_candidate(), _coating_opportunity())

    assert proposal["status"] == "proposed_for_deterministic_review"
    assert proposal["refinement_operator"] == "add_oxidation_protection_coating"
    assert proposal["proposal_id"] == "C-1:add_oxidation_protection_coating:oxidation_protection_coating"


def test_build_refinement_proposal_creates_research_mode_status_for_gradient():
    proposal = build_refinement_proposal(_candidate(), _gradient_opportunity())

    assert proposal["status"] == "research_mode_only"
    assert any("Research-mode-only" in warning for warning in proposal["warnings"])


def test_build_refinement_proposal_trace_states_no_ranking_or_certification_claim():
    proposal = build_refinement_proposal(_candidate(), _coating_opportunity())

    assert any(
        "No ranking, winner selection or certification claim has been made" in trace
        for trace in proposal["trace"]
    )


def test_build_refinement_proposals_for_candidate_creates_coating_and_gradient_for_oxidation():
    proposal_set = build_refinement_proposals_for_candidate(
        _candidate(),
        limiting_factors=["oxidation"],
        research_mode_enabled=False,
    )

    assert proposal_set["proposal_count"] == 2
    assert [proposal["refinement_operator"] for proposal in proposal_set["proposals"]] == [
        "add_oxidation_protection_coating",
        "add_surface_oxidation_gradient",
    ]


def test_build_refinement_proposals_for_candidate_preserves_proposal_order():
    proposal_set = build_refinement_proposals_for_candidate(
        _candidate(),
        limiting_factors=["oxidation"],
    )

    assert [proposal["opportunity_family"] for proposal in proposal_set["proposals"]] == [
        "coating",
        "spatial_gradient",
    ]


def test_run_refinement_proposals_preserves_candidate_order():
    run = run_refinement_proposals(
        [
            {"candidate_id": "C-1", "limiting_factors": []},
            {"candidate_id": "C-2", "limiting_factors": []},
        ]
    )

    assert [item["candidate_id"] for item in run["proposal_sets"]] == ["C-1", "C-2"]


def test_run_refinement_proposals_uses_limiting_factors_by_candidate_before_default():
    run = run_refinement_proposals(
        [_candidate()],
        limiting_factors_by_candidate={"C-1": ["oxidation"]},
        default_limiting_factors=["wear"],
    )

    proposal_set = run["proposal_sets"][0]
    assert proposal_set["limiting_factors"] == ["oxidation"]
    assert [proposal["refinement_operator"] for proposal in proposal_set["proposals"]] == [
        "add_oxidation_protection_coating",
        "add_surface_oxidation_gradient",
    ]


def test_run_refinement_proposals_summary_includes_counts_by_status_and_operator():
    run = run_refinement_proposals(
        [_candidate()],
        default_limiting_factors=["oxidation"],
    )

    summary = run["refinement_summary"]
    assert summary["by_status"]["proposed_for_deterministic_review"] == 2
    assert summary["by_refinement_operator"]["add_oxidation_protection_coating"] == 1
    assert summary["by_refinement_operator"]["add_surface_oxidation_gradient"] == 1


def test_run_refinement_proposals_does_not_mutate_input_candidates():
    candidates = [_candidate()]
    candidates[0]["limiting_factors"] = ["oxidation"]
    original = deepcopy(candidates)

    run_refinement_proposals(candidates)

    assert candidates == original


def test_research_mode_enabled_true_adds_run_level_warning():
    run = run_refinement_proposals([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_no_matching_limiting_factor_produces_zero_proposals():
    proposal_set = build_refinement_proposals_for_candidate(
        _candidate(),
        limiting_factors=["unobtainium_shortage"],
    )

    assert proposal_set["proposal_count"] == 0
    assert proposal_set["proposals"] == []
