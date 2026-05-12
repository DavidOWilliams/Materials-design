from copy import deepcopy

from src.application_limiting_factors import (
    ANALYSIS_STATUSES,
    analyze_candidate_application_limiting_factors,
)


def _candidate(**overrides):
    candidate = {
        "candidate_id": "candidate-1",
        "candidate_class": "ceramic_matrix_composite",
        "architecture_path": "cmc_ebc_environmental_protection_path",
        "evidence_maturity": "B",
        "surface_function_profile": {
            "primary_service_functions": [
                "oxidation_resistance",
                "environmental_barrier",
            ],
            "secondary_service_functions": [
                "thermal_cycling_tolerance",
            ],
            "surface_functions": [
                {"function_id": "oxidation_resistance", "function_kind": "primary_service_function"},
                {"function_id": "environmental_barrier", "function_kind": "primary_service_function"},
                {"function_id": "thermal_cycling_tolerance", "function_kind": "secondary_service_function"},
            ],
        },
        "environmental_barrier_coating": {"name": "rare-earth silicate EBC"},
        "inspection_plan": {"inspection_burden": "high"},
        "repairability": {"repairability_level": "moderate"},
        "qualification_route": {"qualification_burden": "very_high"},
    }
    candidate.update(overrides)
    return candidate


def _poor_fit_candidate():
    return _candidate(
        candidate_id="poor-fit",
        candidate_class="coating_enabled",
        architecture_path="oxidation_protection_only_path",
        surface_function_profile={
            "primary_service_functions": ["oxidation_resistance"],
            "secondary_service_functions": ["thermal_cycling_tolerance"],
        },
    )


def test_analysis_statuses_contains_expected_values():
    assert ANALYSIS_STATUSES == {
        "analysed_for_application",
        "poor_fit_suppressed",
        "exploratory_context_only",
        "research_context_only",
        "insufficient_information",
    }


def test_plausible_with_validation_candidate_returns_analysed_for_application():
    analysis = analyze_candidate_application_limiting_factors(_candidate())

    assert analysis["fit_status"] == "plausible_with_validation"
    assert analysis["analysis_status"] == "analysed_for_application"


def test_plausible_candidate_missing_required_function_is_in_limiting_factors_or_required_evidence():
    analysis = analyze_candidate_application_limiting_factors(_candidate())
    combined = str(analysis["limiting_factors"] + analysis["required_evidence"])

    assert "thermal_barrier" in combined


def test_poor_fit_candidate_returns_poor_fit_suppressed():
    analysis = analyze_candidate_application_limiting_factors(_poor_fit_candidate())

    assert analysis["fit_status"] == "poor_fit_for_profile"
    assert analysis["analysis_status"] == "poor_fit_suppressed"


def test_poor_fit_candidate_suppresses_refinement_actions():
    analysis = analyze_candidate_application_limiting_factors(_poor_fit_candidate())

    assert analysis["suppressed_reasons"]
    assert analysis["suggested_actions"] == [
        "park for this profile",
        "consider under a different application profile",
    ]
    assert "refine" not in " ".join(analysis["suggested_actions"]).lower()


def test_exploratory_candidate_returns_exploratory_context_only():
    analysis = analyze_candidate_application_limiting_factors(_candidate(evidence_maturity="D"))

    assert analysis["fit_status"] == "exploratory_only_for_profile"
    assert analysis["analysis_status"] == "exploratory_context_only"


def test_exploratory_candidate_includes_low_maturity_or_validation_uncertainty_caution():
    analysis = analyze_candidate_application_limiting_factors(_candidate(evidence_maturity="E"))
    caution_text = " ".join(analysis["cautions"]).lower()

    assert "low maturity" in caution_text or "validation uncertainty" in caution_text


def test_research_candidate_returns_research_context_only():
    analysis = analyze_candidate_application_limiting_factors(_candidate(evidence_maturity="F"))

    assert analysis["fit_status"] == "research_only_for_profile"
    assert analysis["analysis_status"] == "research_context_only"


def test_insufficient_information_returns_required_evidence():
    candidate = _candidate(
        application_requirement_fit={
            "profile_id": "hot_section_thermal_cycling_oxidation",
            "architecture_path": "unknown",
            "fit_status": "insufficient_information",
            "application_fit_status": "insufficient_information",
        }
    )

    analysis = analyze_candidate_application_limiting_factors(candidate)

    assert analysis["analysis_status"] == "insufficient_information"
    assert analysis["required_evidence"]
    assert "missing" in analysis["required_evidence"][0]["reason"].lower()


def test_uses_existing_application_requirement_fit_when_present():
    candidate = _candidate(
        application_requirement_fit={
            "profile_id": "custom-profile",
            "architecture_path": "precomputed_path",
            "fit_status": "poor_fit_for_profile",
            "application_fit_status": "poor_fit_for_profile",
        }
    )

    analysis = analyze_candidate_application_limiting_factors(candidate)

    assert analysis["profile_id"] == "custom-profile"
    assert analysis["architecture_path"] == "precomputed_path"
    assert analysis["analysis_status"] == "poor_fit_suppressed"


def test_computes_application_fit_when_absent():
    candidate = _candidate()

    analysis = analyze_candidate_application_limiting_factors(candidate)

    assert "application_requirement_fit" not in candidate
    assert analysis["profile_id"] == "hot_section_thermal_cycling_oxidation"
    assert analysis["fit_status"] == "plausible_with_validation"


def test_analysis_does_not_mutate_candidate():
    candidate = _candidate()
    before = deepcopy(candidate)

    analyze_candidate_application_limiting_factors(candidate)

    assert candidate == before


def test_assessment_boundaries_exclude_downstream_decision_outputs():
    analysis = analyze_candidate_application_limiting_factors(_candidate())

    assert analysis["assessment_boundaries"] == {
        "ranking_performed": False,
        "controlled_shortlist_created": False,
        "validation_plan_created": False,
        "optimisation_performed": False,
        "pareto_analysis_performed": False,
        "candidate_filtering_performed": False,
        "generated_candidate_variants": False,
        "final_recommendation_created": False,
        "live_model_calls_made": False,
    }


def test_no_package_or_downstream_outputs_are_created():
    analysis = analyze_candidate_application_limiting_factors(_candidate())

    assert "candidate_systems" not in analysis
    assert "ranked_recommendations" not in analysis
    assert "pareto_front" not in analysis
    assert "controlled_shortlist" not in analysis
    assert "validation_plan" not in analysis
    assert "optimisation_summary" not in analysis
    assert "generated_candidates" not in analysis
    assert analysis["assessment_boundaries"]["live_model_calls_made"] is False
