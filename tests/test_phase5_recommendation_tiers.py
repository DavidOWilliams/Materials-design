from copy import deepcopy

from src.recommendation_tiers import (
    assign_tier,
    build_recommendation_tiers_from_frontier,
    build_tier_assessment,
    evidence_band_from_maturity,
    evidence_maturity_from_frontier_candidate,
    frontier_status,
    has_research_mode_exposure,
    run_recommendation_tiers,
)


def _candidate(
    candidate_id: str = "C-1",
    *,
    maturity: str = "A",
    on_frontier: bool = True,
    vector_status: str = "tradeoff_vector_available",
    comparable: bool = True,
    warnings: list[str] | None = None,
    dominated_by: list[str] | None = None,
) -> dict:
    dimensions = [
        {
            "dimension_id": "evidence_maturity",
            "raw_value": maturity,
            "numeric_value": 6.0,
            "direction": "higher_is_better",
            "comparable_value": 6.0,
            "rationale": "evidence maturity",
        }
    ] if comparable else []
    return {
        "candidate_id": candidate_id,
        "system_name": f"System {candidate_id}",
        "vector_status": vector_status,
        "on_frontier": on_frontier,
        "dominated_by": dominated_by if dominated_by is not None else [],
        "dominates": [],
        "comparable_dimensions": dimensions,
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


def test_evidence_band_from_maturity_maps_a_b_to_mature():
    assert evidence_band_from_maturity("A") == "mature"
    assert evidence_band_from_maturity("b") == "mature"


def test_evidence_band_from_maturity_maps_c_to_engineering_reference():
    assert evidence_band_from_maturity("C") == "engineering_reference"


def test_evidence_band_from_maturity_maps_d_to_emerging():
    assert evidence_band_from_maturity("D") == "emerging"


def test_evidence_band_from_maturity_maps_e_f_to_exploratory():
    assert evidence_band_from_maturity("E") == "exploratory"
    assert evidence_band_from_maturity("f") == "exploratory"


def test_evidence_band_from_maturity_maps_unknown_and_unrecognised_to_unknown():
    assert evidence_band_from_maturity("unknown") == "unknown"
    assert evidence_band_from_maturity("screened_reference") == "unknown"


def test_evidence_maturity_from_frontier_candidate_reads_raw_value():
    assert evidence_maturity_from_frontier_candidate(_candidate(maturity="C")) == "C"


def test_has_research_mode_exposure_true_for_research_vector_status():
    assert has_research_mode_exposure(
        _candidate(vector_status="research_mode_vector_available")
    ) is True


def test_has_research_mode_exposure_true_when_warnings_mention_research():
    assert has_research_mode_exposure(
        _candidate(warnings=["Research-mode traces are present."])
    ) is True


def test_frontier_status_returns_insufficient_basis_without_comparable_dimensions():
    assert frontier_status(_candidate(comparable=False)) == "insufficient_basis"


def test_frontier_status_returns_on_frontier_when_true():
    assert frontier_status(_candidate(on_frontier=True)) == "on_frontier"


def test_frontier_status_returns_dominated_when_false():
    assert frontier_status(_candidate(on_frontier=False)) == "dominated"


def test_assign_tier_research_mode_overrides_mature_evidence():
    candidate = _candidate(
        maturity="A",
        vector_status="research_mode_vector_available",
    )

    assert assign_tier(candidate, evidence_maturity="A") == "research_only_suggestion"


def test_assign_tier_returns_parked_for_dominated_candidates():
    candidate = _candidate(on_frontier=False, dominated_by=["C-2"])

    assert assign_tier(candidate, evidence_maturity="A") == "parked_not_preferred"


def test_assign_tier_returns_mature_reference_for_on_frontier_mature_evidence():
    assert assign_tier(_candidate(maturity="A"), evidence_maturity="A") == (
        "mature_reference_option"
    )


def test_assign_tier_returns_validation_needed_for_c_or_d_maturity():
    assert assign_tier(_candidate(maturity="C"), evidence_maturity="C") == (
        "validation_needed_option"
    )
    assert assign_tier(_candidate(maturity="D"), evidence_maturity="D") == (
        "validation_needed_option"
    )


def test_assign_tier_returns_exploratory_for_e_f_or_unknown_maturity():
    assert assign_tier(_candidate(maturity="E"), evidence_maturity="E") == (
        "exploratory_option"
    )
    assert assign_tier(_candidate(maturity="F"), evidence_maturity="F") == (
        "exploratory_option"
    )
    assert assign_tier(_candidate(maturity="unknown"), evidence_maturity="unknown") == (
        "exploratory_option"
    )


def test_build_tier_assessment_rationale_states_no_final_recommendation_or_approval():
    assessment = build_tier_assessment(_candidate())

    assert any(
        "No final recommendation or approval is made" in item
        for item in assessment["rationale"]
    )


def test_build_tier_assessment_does_not_mutate_input_candidate():
    candidate = _candidate()
    original = deepcopy(candidate)

    build_tier_assessment(candidate)

    assert candidate == original


def test_build_recommendation_tiers_from_frontier_preserves_input_order():
    run = build_recommendation_tiers_from_frontier([
        _candidate("C-2"),
        _candidate("C-1"),
    ])

    assert [item["candidate_id"] for item in run["tier_assessments"]] == ["C-2", "C-1"]


def test_build_recommendation_tiers_from_frontier_has_no_sort_rank_or_winner_fields():
    run = build_recommendation_tiers_from_frontier([_candidate()])

    assert "rank" not in run
    assert "winner" not in run
    assert "score" not in run
    for assessment in run["tier_assessments"]:
        assert "rank" not in assessment
        assert "winner" not in assessment
        assert "score" not in assessment


def test_build_recommendation_tiers_from_frontier_summary_counts_by_tier():
    run = build_recommendation_tiers_from_frontier([
        _candidate("C-1", maturity="A"),
        _candidate("C-2", on_frontier=False, dominated_by=["C-1"]),
    ])

    assert run["tier_summary"]["by_tier"]["mature_reference_option"] == 1
    assert run["tier_summary"]["by_tier"]["parked_not_preferred"] == 1


def test_build_recommendation_tiers_from_frontier_warns_when_no_candidates():
    run = build_recommendation_tiers_from_frontier([])

    assert any("No frontier candidates" in warning for warning in run["warnings"])


def test_build_recommendation_tiers_from_frontier_warns_when_research_only_exists():
    run = build_recommendation_tiers_from_frontier([
        _candidate(vector_status="research_mode_vector_available"),
    ])

    assert any("research-only suggestions" in warning for warning in run["warnings"])


def test_run_recommendation_tiers_preserves_candidate_order():
    run = run_recommendation_tiers([
        _pipeline_candidate("C-1"),
        _pipeline_candidate("C-2"),
    ])

    assert [item["candidate_id"] for item in run["tier_assessments"]] == ["C-1", "C-2"]


def test_run_recommendation_tiers_includes_research_mode_warning_when_enabled():
    run = run_recommendation_tiers([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_run_recommendation_tiers_does_not_mutate_input_candidates():
    candidates = [_pipeline_candidate("C-1"), _pipeline_candidate("C-2")]
    original = deepcopy(candidates)

    run_recommendation_tiers(candidates)

    assert candidates == original
