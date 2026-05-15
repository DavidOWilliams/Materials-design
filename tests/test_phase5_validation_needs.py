from copy import deepcopy

from src.phase5_validation_needs import (
    build_validation_needs_for_tier_assessment,
    build_validation_needs_from_tiers,
    cautions_contain,
    need_status_for_category,
    run_phase5_validation_needs,
    validation_need,
    validation_priority_for_tier,
)


def _assessment(
    candidate_id: str = "C-1",
    *,
    tier: str = "validation_needed_option",
    frontier_status: str = "on_frontier",
    evidence_band: str = "engineering_reference",
    research_mode_exposure: bool = False,
    review_cautions: list[str] | None = None,
    warnings: list[str] | None = None,
    dominated_by: list[str] | None = None,
) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"System {candidate_id}",
        "tier": tier,
        "tier_label": tier.replace("_", " ").title(),
        "frontier_status": frontier_status,
        "evidence_maturity": "C",
        "evidence_band": evidence_band,
        "research_mode_exposure": research_mode_exposure,
        "dominated_by": dominated_by if dominated_by is not None else [],
        "dominates": [],
        "review_cautions": review_cautions if review_cautions is not None else [],
        "warnings": warnings if warnings is not None else [],
        "notes": [],
    }


def _pipeline_candidate(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"Nickel DED System {candidate_id}",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "limiting_factors": [],
    }


def _categories(plan: dict) -> list[str]:
    return [need["category"] for need in plan["validation_needs"]]


def _need(plan: dict, category: str) -> dict:
    return [
        need for need in plan["validation_needs"] if need["category"] == category
    ][0]


def test_validation_priority_maps_research_and_exploratory_to_high():
    assert validation_priority_for_tier("research_only_suggestion") == "high"
    assert validation_priority_for_tier("exploratory_option") == "high"


def test_validation_priority_maps_mature_and_parked_to_low():
    assert validation_priority_for_tier("mature_reference_option") == "low"
    assert validation_priority_for_tier("parked_not_preferred") == "low"


def test_need_status_for_research_mode_gate_is_research_required():
    assert need_status_for_category("research_mode_gate") == (
        "research_mode_validation_required"
    )


def test_need_status_for_certification_caution_is_engineering_review():
    assert need_status_for_category("certification_caution_review") == (
        "engineering_review_required"
    )


def test_validation_need_builds_need_id_and_certification_warning():
    need = validation_need(
        candidate_id="C-1",
        category="certification_caution_review",
        priority="medium",
        validation_activity="Document assumptions.",
        trigger="Decision Support Only",
        rationale="No approval.",
        linked_cautions=["caution"],
        linked_tier="validation_needed_option",
        linked_frontier_status="on_frontier",
        linked_evidence_band="engineering_reference",
    )

    assert need["need_id"] == "C-1:certification_caution_review:decision_support_only"
    assert any("does not imply certification approval" in warning for warning in need["warnings"])


def test_cautions_contain_matches_raw_and_normalised_text():
    cautions = [
        "Coating spallation needs review.",
        "Transition zone maturity is uncertain.",
    ]

    assert cautions_contain(cautions, "spallation") is True
    assert cautions_contain(cautions, "transition-zone") is True


def test_build_validation_needs_adds_high_priority_evidence_need_for_exploratory():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(evidence_band="exploratory")
    )

    need = _need(plan, "evidence_maturity")
    assert need["priority"] == "high"
    assert need["trigger"] == "exploratory_or_unknown_evidence"


def test_build_validation_needs_adds_research_mode_gate_for_research_only():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(
            tier="research_only_suggestion",
            research_mode_exposure=True,
        )
    )

    assert "research_mode_gate" in _categories(plan)
    assert plan["plan_status"] == "research_mode_validation_required"


def test_build_validation_needs_adds_dominated_option_review():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(
            frontier_status="dominated",
            dominated_by=["C-2"],
        )
    )

    assert "dominated_option_review" in _categories(plan)


def test_build_validation_needs_adds_coating_interface_review_for_cautions():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(review_cautions=["Coating spallation and interface risk."])
    )

    assert "coating_interface_review" in _categories(plan)


def test_build_validation_needs_adds_spatial_gradient_feasibility_for_cautions():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(review_cautions=["Transition-zone gradient review is needed."])
    )

    assert "spatial_gradient_feasibility" in _categories(plan)


def test_build_validation_needs_adds_inspection_repair_review_for_cautions():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(review_cautions=["Inspection and repair access should be checked."])
    )

    assert "inspection_repair_review" in _categories(plan)


def test_build_validation_needs_always_adds_certification_caution_review():
    plan = build_validation_needs_for_tier_assessment(_assessment())

    assert "certification_caution_review" in _categories(plan)


def test_build_validation_needs_adds_frontier_review_for_on_frontier():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(frontier_status="on_frontier")
    )

    frontier_need = _need(plan, "frontier_review")
    assert frontier_need["trigger"] == "on_frontier"


def test_build_validation_needs_adds_frontier_review_for_insufficient_basis():
    plan = build_validation_needs_for_tier_assessment(
        _assessment(frontier_status="insufficient_basis")
    )

    frontier_need = _need(plan, "frontier_review")
    assert frontier_need["trigger"] == "insufficient_frontier_basis"
    assert frontier_need["priority"] == "high"


def test_build_validation_needs_always_adds_general_engineering_review():
    plan = build_validation_needs_for_tier_assessment(_assessment())

    assert "general_engineering_review" in _categories(plan)


def test_build_validation_needs_does_not_mutate_input_assessment():
    assessment = _assessment(review_cautions=["coating caution"])
    original = deepcopy(assessment)

    build_validation_needs_for_tier_assessment(assessment)

    assert assessment == original


def test_build_validation_needs_from_tiers_preserves_input_order():
    run = build_validation_needs_from_tiers([
        _assessment("C-2"),
        _assessment("C-1"),
    ])

    assert [plan["candidate_id"] for plan in run["candidate_validation_needs"]] == [
        "C-2",
        "C-1",
    ]


def test_build_validation_needs_from_tiers_summary_counts_category_and_priority():
    run = build_validation_needs_from_tiers([
        _assessment(evidence_band="exploratory"),
    ])

    summary = run["validation_summary"]
    assert summary["by_category"]["evidence_maturity"] == 1
    assert summary["by_category"]["certification_caution_review"] == 1
    assert summary["by_priority"]["high"] >= 1


def test_build_validation_needs_from_tiers_warns_when_empty():
    run = build_validation_needs_from_tiers([])

    assert any("No tier assessments" in warning for warning in run["warnings"])


def test_build_validation_needs_from_tiers_warns_for_research_mode_required():
    run = build_validation_needs_from_tiers([
        _assessment(
            tier="research_only_suggestion",
            research_mode_exposure=True,
        )
    ])

    assert any("research-mode validation" in warning for warning in run["warnings"])


def test_run_phase5_validation_needs_preserves_candidate_order():
    run = run_phase5_validation_needs([
        _pipeline_candidate("C-1"),
        _pipeline_candidate("C-2"),
    ])

    assert [plan["candidate_id"] for plan in run["candidate_validation_needs"]] == [
        "C-1",
        "C-2",
    ]


def test_run_phase5_validation_needs_includes_research_mode_warning_when_enabled():
    run = run_phase5_validation_needs([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_run_phase5_validation_needs_does_not_mutate_input_candidates():
    candidates = [_pipeline_candidate("C-1"), _pipeline_candidate("C-2")]
    original = deepcopy(candidates)

    run_phase5_validation_needs(candidates)

    assert candidates == original
