from copy import deepcopy

from src.optimisation_trace import (
    build_change_summary,
    build_trace_record,
    build_traces_for_candidate,
    build_ui_badges,
    evidence_maturity_from_state,
    process_route_summary,
    run_optimisation_traces,
    summarise_state,
)


def _candidate() -> dict:
    return {
        "candidate_id": "C-1",
        "system_name": "Nickel DED System",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "evidence_package": {"evidence_maturity": "baseline_screen"},
    }


def _coating_proposal() -> dict:
    return {
        "proposal_id": "C-1:add_oxidation_protection_coating:oxidation_protection_coating",
        "candidate_id": "C-1",
        "opportunity_id": "C-1:coating:oxidation_protection_coating",
        "opportunity_family": "coating",
        "refinement_operator": "add_oxidation_protection_coating",
        "status": "proposed_for_deterministic_review",
        "before_state": {
            "system_architecture_type": "monolithic",
            "coating_or_surface_system": None,
            "gradient_architecture": None,
            "process_route": {"route_name": "DED"},
            "evidence_package": {"evidence_maturity": "baseline_screen"},
        },
        "proposed_after_state": {
            "system_architecture_type": "coating_enabled",
            "coating_or_surface_system": {
                "option_id": "oxidation_protection_coating",
                "evidence_maturity": "deterministic_reference",
            },
            "gradient_architecture": None,
            "process_route": {"route_name": "DED"},
            "evidence_package": {"evidence_maturity": "baseline_screen"},
        },
        "expected_benefits": ["reduced oxidation exposure"],
        "introduced_risks": ["coating spallation"],
        "review_required": ["substrate_interface_review"],
        "evidence_maturity": "deterministic_reference",
        "warnings": [],
    }


def _research_gradient_proposal() -> dict:
    proposal = _coating_proposal()
    proposal.update(
        {
            "proposal_id": "C-1:add_thermal_barrier_gradient:thermal_barrier_gradient",
            "opportunity_id": "C-1:spatial_gradient:thermal_barrier_gradient",
            "opportunity_family": "spatial_gradient",
            "refinement_operator": "add_thermal_barrier_gradient",
            "status": "research_mode_only",
            "proposed_after_state": {
                "system_architecture_type": "spatially_graded_am_system",
                "coating_or_surface_system": None,
                "gradient_architecture": {
                    "gradient_template_id": "thermal_barrier_gradient",
                    "evidence_maturity": "research_template",
                },
                "process_route": {"route_name": "DED"},
                "evidence_package": {"evidence_maturity": "baseline_screen"},
            },
            "evidence_maturity": "research_template",
            "warnings": ["Research-mode-only refinement proposal requires gated review."],
        }
    )
    return proposal


def test_evidence_maturity_from_state_returns_evidence_package_maturity():
    assert (
        evidence_maturity_from_state(
            {"evidence_package": {"evidence_maturity": "coupon_screen"}}
        )
        == "coupon_screen"
    )


def test_evidence_maturity_from_state_falls_back_to_coating_maturity():
    assert (
        evidence_maturity_from_state(
            {"coating_or_surface_system": {"evidence_maturity": "coating_reference"}}
        )
        == "coating_reference"
    )


def test_evidence_maturity_from_state_falls_back_to_gradient_maturity():
    assert (
        evidence_maturity_from_state(
            {"gradient_architecture": {"evidence_maturity": "gradient_reference"}}
        )
        == "gradient_reference"
    )


def test_process_route_summary_extracts_route_name_route_family_and_process():
    assert process_route_summary(
        {
            "process_route": {
                "route_name": "DED",
                "route_family": "additive_manufacturing",
                "process": "laser_deposition",
            }
        }
    ) == ["DED", "additive_manufacturing", "laser_deposition"]


def test_summarise_state_identifies_coating_and_gradient_presence():
    summary = summarise_state(
        {
            "system_architecture_type": "hybrid",
            "coating_or_surface_system": {"option_id": "coating"},
            "gradient_architecture": {"template_id": "gradient"},
            "process_route": {"route_name": "DED"},
            "evidence_package": {"evidence_maturity": "screened"},
        }
    )

    assert summary["has_coating_or_surface_system"] is True
    assert summary["has_gradient_architecture"] is True
    assert summary["notable_fields_present"] == [
        "coating_or_surface_system",
        "gradient_architecture",
        "process_route",
        "evidence_package",
    ]


def test_build_change_summary_detects_architecture_change():
    changes = build_change_summary(
        {"system_architecture_type": "monolithic"},
        {"system_architecture_type": "coating_enabled"},
    )

    assert any("system_architecture_type changed" in change for change in changes)


def test_build_change_summary_detects_coating_added():
    changes = build_change_summary(
        {"coating_or_surface_system": None},
        {"coating_or_surface_system": {"option_id": "oxidation_protection_coating"}},
    )

    assert "coating_or_surface_system added in proposed after-state." in changes


def test_build_change_summary_detects_gradient_added():
    changes = build_change_summary(
        {"gradient_architecture": None},
        {"gradient_architecture": {"gradient_template_id": "surface_oxidation_gradient"}},
    )

    assert "gradient_architecture added in proposed after-state." in changes


def test_build_change_summary_returns_message_when_nothing_changed():
    state = {"system_architecture_type": "monolithic", "process_route": {"route_name": "DED"}}

    assert build_change_summary(state, deepcopy(state)) == [
        "No tracked before/after state changes were recorded."
    ]


def test_build_ui_badges_includes_common_audit_badges_for_all_proposals():
    badges = build_ui_badges({"status": "unsupported_opportunity_type"})

    assert "no_ranking" in badges
    assert "no_certification_claim" in badges
    assert "requires_review" in badges


def test_build_ui_badges_includes_coating_refinement_for_coating_proposals():
    badges = build_ui_badges(_coating_proposal())

    assert "coating_refinement" in badges
    assert "deterministic_review" in badges


def test_build_ui_badges_includes_gradient_and_research_mode_for_research_gradient():
    badges = build_ui_badges(_research_gradient_proposal())

    assert "spatial_gradient_refinement" in badges
    assert "research_mode_only" in badges


def test_build_trace_record_includes_before_and_after_summaries():
    trace = build_trace_record(_coating_proposal())

    assert trace["before_state_summary"]["system_architecture_type"] == "monolithic"
    assert trace["proposed_after_state_summary"]["system_architecture_type"] == "coating_enabled"


def test_build_trace_record_narrative_states_no_ranking_or_certification_claim():
    trace = build_trace_record(_coating_proposal())

    assert any(
        "No ranking, winner selection or certification claim has been made" in narrative
        for narrative in trace["trace_narrative"]
    )


def test_build_trace_record_does_not_mutate_proposal():
    proposal = _coating_proposal()
    original = deepcopy(proposal)

    build_trace_record(proposal)

    assert proposal == original


def test_build_traces_for_candidate_creates_two_traces_for_oxidation_case():
    trace_set = build_traces_for_candidate(
        _candidate(),
        limiting_factors=["oxidation"],
    )

    assert trace_set["trace_count"] == 2
    assert [trace["refinement_operator"] for trace in trace_set["traces"]] == [
        "add_oxidation_protection_coating",
        "add_surface_oxidation_gradient",
    ]


def test_build_traces_for_candidate_preserves_trace_order():
    trace_set = build_traces_for_candidate(
        _candidate(),
        limiting_factors=["oxidation"],
    )

    assert [trace["refinement_operator"] for trace in trace_set["traces"]] == [
        "add_oxidation_protection_coating",
        "add_surface_oxidation_gradient",
    ]


def test_run_optimisation_traces_preserves_candidate_order():
    run = run_optimisation_traces(
        [
            {"candidate_id": "C-1", "limiting_factors": []},
            {"candidate_id": "C-2", "limiting_factors": []},
        ]
    )

    assert [item["candidate_id"] for item in run["candidate_traces"]] == ["C-1", "C-2"]


def test_run_optimisation_traces_summary_includes_counts_by_status_and_badge():
    run = run_optimisation_traces(
        [_candidate()],
        default_limiting_factors=["oxidation"],
    )

    summary = run["trace_summary"]
    assert summary["by_status"]["proposed_for_deterministic_review"] == 2
    assert summary["by_badge"]["deterministic_review"] == 2
    assert summary["by_badge"]["requires_review"] == 2


def test_run_optimisation_traces_does_not_mutate_input_candidates():
    candidates = [_candidate()]
    candidates[0]["limiting_factors"] = ["oxidation"]
    original = deepcopy(candidates)

    run_optimisation_traces(candidates)

    assert candidates == original


def test_research_mode_enabled_true_adds_run_level_warning():
    run = run_optimisation_traces([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_no_matching_limiting_factor_produces_zero_traces():
    trace_set = build_traces_for_candidate(
        _candidate(),
        limiting_factors=["unobtainium_shortage"],
    )

    assert trace_set["trace_count"] == 0
    assert trace_set["traces"] == []
