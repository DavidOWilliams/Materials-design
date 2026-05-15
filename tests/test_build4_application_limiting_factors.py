from copy import deepcopy

from src.application_limiting_factors import (
    ANALYSIS_STATUSES,
    analyze_candidate_application_limiting_factors,
    attach_application_limiting_factors,
    summarize_application_limiting_factors,
)
from src.application_requirement_fit import assess_candidate_application_requirement_fit


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


def _package(with_application_fit=True):
    candidates = [
        _candidate(candidate_id="candidate-1"),
        _poor_fit_candidate(),
        _candidate(candidate_id="candidate-3", evidence_maturity="D"),
    ]
    if with_application_fit:
        candidates = [
            {
                **candidate,
                "application_requirement_fit": assess_candidate_application_requirement_fit(candidate),
            }
            for candidate in candidates
        ]
    return {
        "candidate_systems": candidates,
        "application_profile": {"profile_id": "hot_section_thermal_cycling_oxidation"},
        "application_requirement_fit_summary": {"assessment_status": "preexisting"},
        "diagnostics": {"existing_diagnostic": "preserved"},
        "ranked_recommendations": [{"candidate_id": "preexisting-rank"}],
        "pareto_front": [{"candidate_id": "preexisting-pareto"}],
        "optimisation_summary": {
            "generated_candidate_count": 0,
            "live_model_calls_made": False,
        },
    }


def test_attach_application_limiting_factors_attaches_analysis_to_every_candidate():
    package = attach_application_limiting_factors(_package())

    assert all("application_limiting_factor_analysis" in candidate for candidate in package["candidate_systems"])


def test_attach_application_limiting_factors_preserves_candidate_count_and_order():
    source = _package()
    package = attach_application_limiting_factors(source)

    assert len(package["candidate_systems"]) == len(source["candidate_systems"])
    assert [candidate["candidate_id"] for candidate in package["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in source["candidate_systems"]
    ]


def test_attach_application_limiting_factors_adds_summary_with_candidate_counts():
    package = attach_application_limiting_factors(_package())
    summary = package["application_limiting_factor_summary"]

    assert summary["candidate_count"] == 3
    assert summary["assessed_candidate_count"] == 3


def test_summary_includes_analysis_fit_and_architecture_counts():
    summary = summarize_application_limiting_factors(_package()["candidate_systems"])

    assert summary["analysis_status_counts"]
    assert summary["fit_status_counts"]
    assert summary["architecture_path_counts"]
    assert summary["assessment_status"] == "application_limiting_factors_attached"


def test_attach_application_limiting_factors_updates_diagnostics_and_preserves_existing_values():
    package = attach_application_limiting_factors(_package())

    assert package["diagnostics"]["existing_diagnostic"] == "preserved"
    assert package["diagnostics"]["application_limiting_factors_attached"] is True
    assert package["diagnostics"]["application_limiting_factor_candidate_count"] == 3
    assert package["diagnostics"]["application_limiting_factor_candidate_order_preserved"] is True


def test_attach_application_limiting_factors_preserves_ranked_pareto_and_optimisation_outputs():
    source = _package()
    package = attach_application_limiting_factors(source)

    assert package["ranked_recommendations"] == source["ranked_recommendations"]
    assert package["pareto_front"] == source["pareto_front"]
    assert package["optimisation_summary"] == source["optimisation_summary"]


def test_attach_application_limiting_factors_does_not_create_shortlist_or_validation_plan():
    package = attach_application_limiting_factors(_package())

    assert "controlled_shortlist" not in package
    assert "validation_plan" not in package
    assert package["application_limiting_factor_summary"]["controlled_shortlist_created"] is False
    assert package["application_limiting_factor_summary"]["validation_plan_created"] is False


def test_attach_application_limiting_factors_summary_records_no_filtering_or_live_calls():
    package = attach_application_limiting_factors(_package())
    summary = package["application_limiting_factor_summary"]

    assert summary["candidate_filtering_performed"] is False
    assert summary["ranking_performed"] is False
    assert summary["pareto_analysis_performed"] is False
    assert summary["generated_candidate_count"] == 0
    assert summary["live_model_calls_made"] is False


def test_attach_application_limiting_factors_uses_and_preserves_existing_application_fit():
    source = _package(with_application_fit=True)
    original_fits = [candidate["application_requirement_fit"] for candidate in source["candidate_systems"]]

    package = attach_application_limiting_factors(source)

    assert [candidate["application_requirement_fit"] for candidate in package["candidate_systems"]] == original_fits
    assert package["application_profile"] == source["application_profile"]
    assert package["application_requirement_fit_summary"] == source["application_requirement_fit_summary"]


def test_attach_application_limiting_factors_attaches_application_fit_when_missing():
    package = attach_application_limiting_factors(_package(with_application_fit=False))

    assert all("application_requirement_fit" in candidate for candidate in package["candidate_systems"])
    assert all("application_limiting_factor_analysis" in candidate for candidate in package["candidate_systems"])
    assert package["diagnostics"]["application_requirement_fit_attached"] is True


def test_attach_application_limiting_factors_does_not_create_ranking_or_pareto_when_absent():
    package = attach_application_limiting_factors({"candidate_systems": [_candidate()]})

    assert "ranked_recommendations" not in package
    assert "pareto_front" not in package
    assert "controlled_shortlist" not in package
    assert "validation_plan" not in package
