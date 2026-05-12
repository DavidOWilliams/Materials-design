from src.application_requirement_fit import (
    assess_application_requirement_fit,
    attach_application_requirement_fit,
    summarize_application_requirement_fit,
)


def _candidate(**overrides):
    candidate = {
        "candidate_id": "candidate-1",
        "evidence_maturity": "C",
        "surface_function_profile": {
            "primary_service_functions": [
                "oxidation_resistance",
                "thermal_barrier",
            ],
            "secondary_service_functions": [
                "thermal_cycling_tolerance",
            ],
            "surface_functions": [
                {"function_id": "oxidation_resistance"},
                {"function_id": "thermal_barrier"},
                {"function_id": "thermal_cycling_tolerance"},
            ],
        },
        "inspection_plan": {"inspection_burden": "high"},
        "repairability": {
            "repairability_level": "moderate",
            "repair_concept": "localized repair is possible",
        },
        "qualification_route": {"qualification_burden": "very_high"},
    }
    candidate.update(overrides)
    return candidate


def test_assesses_single_candidate_against_default_profile():
    fit = assess_application_requirement_fit(_candidate())

    assert fit["candidate_id"] == "candidate-1"
    assert fit["profile_id"] == "hot_section_thermal_cycling_oxidation"
    assert fit["profile_name"] == "Hot-section thermal cycling and oxidation"
    assert fit["fit_status"] == "meets_core_requirements"
    assert fit["application_fit_status"] == fit["fit_status"]


def test_required_and_desired_service_function_matches_are_reported_exactly():
    fit = assess_application_requirement_fit(_candidate())

    assert fit["required_primary_service_functions"] == [
        "oxidation_resistance",
        "thermal_barrier",
    ]
    assert fit["matched_required_primary_service_functions"] == [
        "oxidation_resistance",
        "thermal_barrier",
    ]
    assert fit["missing_required_primary_service_functions"] == []
    assert fit["desired_secondary_service_functions"] == [
        "thermal_cycling_tolerance",
    ]
    assert fit["matched_desired_secondary_service_functions"] == [
        "thermal_cycling_tolerance",
    ]
    assert fit["missing_desired_secondary_service_functions"] == []


def test_missing_required_primary_function_prevents_core_fit():
    candidate = _candidate(
        surface_function_profile={
            "primary_service_functions": ["oxidation_resistance"],
            "secondary_service_functions": ["thermal_cycling_tolerance"],
        }
    )

    fit = assess_application_requirement_fit(candidate)

    assert fit["fit_status"] == "poor_fit_for_profile"
    assert fit["application_fit_status"] == "poor_fit_for_profile"
    assert fit["matched_required_primary_service_functions"] == ["oxidation_resistance"]
    assert fit["missing_required_primary_service_functions"] == ["thermal_barrier"]


def test_missing_secondary_function_is_reported_without_blocking_required_fit():
    candidate = _candidate(
        surface_function_profile={
            "primary_service_functions": [
                "oxidation_resistance",
                "thermal_barrier",
            ],
            "secondary_service_functions": [],
        }
    )

    fit = assess_application_requirement_fit(candidate)

    assert fit["fit_status"] == "partially_meets_core_requirements"
    assert fit["missing_required_primary_service_functions"] == []
    assert fit["missing_desired_secondary_service_functions"] == [
        "thermal_cycling_tolerance",
    ]


def test_constraint_checks_include_all_default_profile_constraints():
    fit = assess_application_requirement_fit(_candidate())

    assert [check["constraint_id"] for check in fit["constraint_checks"]] == [
        "thermal_exposure",
        "thermal_cycling",
        "oxidation_steam_exposure",
        "inspection_difficulty",
        "repair",
        "certification_sensitivity",
        "minimum_evidence_maturity",
    ]
    assert fit["gap_constraints"] == []


def test_evidence_below_minimum_maturity_creates_gap():
    fit = assess_application_requirement_fit(_candidate(evidence_maturity="D"))

    evidence_check = next(
        check for check in fit["constraint_checks"] if check["constraint_id"] == "minimum_evidence_maturity"
    )

    assert fit["fit_status"] == "partially_meets_core_requirements"
    assert evidence_check["required_value"] == "C"
    assert evidence_check["observed_value"] == "D"
    assert evidence_check["status"] == "gap"
    assert evidence_check in fit["gap_constraints"]


def test_assessment_boundaries_are_carried_without_assessment_side_effects():
    candidate = _candidate()
    fit = assess_application_requirement_fit(candidate)

    assert fit["assessment_boundaries"] == {
        "ranks_candidates": False,
        "shortlists_candidates": False,
        "validates_plan": False,
        "generates_variants": False,
        "populates_pareto_output": False,
    }
    assert "application_requirement_fit" not in candidate


def _cmc_ebc_candidate(maturity="C", **overrides):
    candidate = _candidate(
        candidate_id="cmc-ebc-1",
        candidate_class="ceramic_matrix_composite",
        architecture_path="cmc_ebc_environmental_protection_path",
        evidence_maturity=maturity,
        surface_function_profile={
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
        environmental_barrier_coating={"name": "rare-earth silicate EBC"},
    )
    candidate.update(overrides)
    return candidate


def test_b_maturity_cmc_ebc_missing_thermal_barrier_is_plausible_with_validation():
    fit = assess_application_requirement_fit(_cmc_ebc_candidate(maturity="B"))

    assert fit["fit_status"] == "plausible_with_validation"
    assert fit["application_fit_status"] == "plausible_with_validation"
    assert fit["matched_required_primary_service_functions"] == ["oxidation_resistance"]
    assert fit["missing_required_primary_service_functions"] == ["thermal_barrier"]


def test_c_maturity_cmc_ebc_environmental_barrier_text_is_plausible_with_validation():
    candidate = _cmc_ebc_candidate(
        maturity="C",
        architecture_path="",
        notes="SiC/SiC CMC with environmental barrier coating for hot-section oxidation and steam protection.",
    )

    fit = assess_application_requirement_fit(candidate)

    assert fit["fit_status"] == "plausible_with_validation"
    assert fit["application_fit_status"] == fit["fit_status"]


def test_cmc_ebc_candidate_still_lists_missing_literal_thermal_barrier_evidence():
    fit = assess_application_requirement_fit(_cmc_ebc_candidate(maturity="C"))

    assert fit["missing_required_primary_service_functions"] == ["thermal_barrier"]
    assert "thermal_barrier" not in fit["matched_required_primary_service_functions"]


def test_cmc_ebc_candidate_includes_architecture_path_validation_issue():
    fit = assess_application_requirement_fit(_cmc_ebc_candidate(maturity="C"))

    assert fit["validation_issues"] == [
        {
            "issue_id": "cmc_ebc_missing_literal_thermal_barrier_tag",
            "severity": "validation_required",
            "message": (
                "CMC/EBC environmental-protection path lacks a literal thermal_barrier tag "
                "but remains plausible as an architecture-path difference requiring validation."
            ),
        }
    ]


def test_d_or_e_maturity_cmc_ebc_environmental_protection_is_exploratory_only_for_profile():
    for maturity in ("D", "E"):
        fit = assess_application_requirement_fit(_cmc_ebc_candidate(maturity=maturity))

        assert fit["fit_status"] == "exploratory_only_for_profile"
        assert fit["application_fit_status"] == "exploratory_only_for_profile"


def test_f_maturity_cmc_ebc_environmental_protection_is_research_only_for_profile():
    fit = assess_application_requirement_fit(_cmc_ebc_candidate(maturity="F"))

    assert fit["fit_status"] == "research_only_for_profile"
    assert fit["application_fit_status"] == "research_only_for_profile"


def test_oxidation_protection_only_path_missing_thermal_barrier_remains_poor_fit_for_profile():
    candidate = _candidate(
        architecture_path="oxidation_protection_only_path",
        surface_function_profile={
            "primary_service_functions": ["oxidation_resistance"],
            "secondary_service_functions": ["thermal_cycling_tolerance"],
        },
    )

    fit = assess_application_requirement_fit(candidate)

    assert fit["fit_status"] == "poor_fit_for_profile"
    assert fit["application_fit_status"] == "poor_fit_for_profile"
    assert fit["missing_required_primary_service_functions"] == ["thermal_barrier"]


def test_support_and_risk_tags_do_not_satisfy_required_or_desired_service_functions():
    candidate = _candidate(
        surface_function_profile={
            "primary_service_functions": ["oxidation_resistance"],
            "secondary_service_functions": [],
            "surface_functions": [
                {
                    "function_id": "inspection_access_or_monitoring",
                    "function_kind": "support_or_lifecycle_consideration",
                },
                {
                    "function_id": "coating_interface_management",
                    "function_kind": "risk_or_interface_consideration",
                },
                {
                    "function_id": "thermal_cycling_tolerance",
                    "function_kind": "support_or_lifecycle_consideration",
                },
            ],
        }
    )

    fit = assess_application_requirement_fit(candidate)

    assert fit["matched_required_primary_service_functions"] == ["oxidation_resistance"]
    assert fit["missing_required_primary_service_functions"] == ["thermal_barrier"]
    assert fit["matched_desired_secondary_service_functions"] == []
    assert fit["missing_desired_secondary_service_functions"] == ["thermal_cycling_tolerance"]


def _package():
    return {
        "candidate_systems": [
            _candidate(candidate_id="candidate-1"),
            _cmc_ebc_candidate(candidate_id="candidate-2", maturity="B"),
            _candidate(
                candidate_id="candidate-3",
                architecture_path="oxidation_protection_only_path",
                surface_function_profile={
                    "primary_service_functions": ["oxidation_resistance"],
                    "secondary_service_functions": ["thermal_cycling_tolerance"],
                },
            ),
        ],
        "diagnostics": {"existing_diagnostic": "preserved"},
        "ranked_recommendations": [{"candidate_id": "preexisting-rank"}],
        "pareto_front": [{"candidate_id": "preexisting-pareto"}],
        "optimisation_summary": {
            "generated_candidate_count": 0,
            "live_model_calls_made": False,
        },
    }


def test_attach_application_requirement_fit_attaches_fit_to_every_candidate():
    package = attach_application_requirement_fit(_package())

    assert all("application_requirement_fit" in candidate for candidate in package["candidate_systems"])


def test_attach_application_requirement_fit_preserves_candidate_count_and_order():
    source = _package()
    package = attach_application_requirement_fit(source)

    assert len(package["candidate_systems"]) == len(source["candidate_systems"])
    assert [candidate["candidate_id"] for candidate in package["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in source["candidate_systems"]
    ]


def test_attach_application_requirement_fit_adds_default_application_profile():
    package = attach_application_requirement_fit(_package())

    assert package["application_profile"]["profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_attach_application_requirement_fit_adds_summary_with_candidate_counts():
    package = attach_application_requirement_fit(_package())
    summary = package["application_requirement_fit_summary"]

    assert summary["candidate_count"] == 3
    assert summary["assessed_candidate_count"] == 3


def test_summary_includes_status_and_architecture_path_counts():
    summary = summarize_application_requirement_fit(_package()["candidate_systems"])

    assert summary["application_fit_status_counts"]
    assert summary["architecture_path_counts"]
    assert summary["assessment_status"] == "application_requirement_fit_attached"


def test_attach_application_requirement_fit_updates_diagnostics_and_preserves_existing_values():
    package = attach_application_requirement_fit(_package())

    assert package["diagnostics"]["existing_diagnostic"] == "preserved"
    assert package["diagnostics"]["application_requirement_fit_attached"] is True
    assert package["diagnostics"]["application_requirement_fit_profile_id"] == "hot_section_thermal_cycling_oxidation"
    assert package["diagnostics"]["application_requirement_fit_candidate_count"] == 3
    assert package["diagnostics"]["application_requirement_fit_candidate_order_preserved"] is True


def test_attach_application_requirement_fit_does_not_change_ranked_recommendations_or_pareto_front():
    source = _package()
    package = attach_application_requirement_fit(source)

    assert package["ranked_recommendations"] == source["ranked_recommendations"]
    assert package["pareto_front"] == source["pareto_front"]


def test_attach_application_requirement_fit_preserves_optimisation_generated_count_and_live_model_flag():
    package = attach_application_requirement_fit(_package())

    assert package["optimisation_summary"]["generated_candidate_count"] == 0
    assert package["optimisation_summary"]["live_model_calls_made"] is False
    assert package["application_requirement_fit_summary"]["generated_candidate_count"] == 0
    assert package["application_requirement_fit_summary"]["live_model_calls_made"] is False


def test_attach_application_requirement_fit_does_not_create_shortlist_or_validation_plan():
    package = attach_application_requirement_fit(_package())

    assert "controlled_shortlist" not in package
    assert "validation_plan" not in package
    assert package["application_requirement_fit_summary"]["controlled_shortlist_created"] is False
    assert package["application_requirement_fit_summary"]["validation_plan_created"] is False


def test_attach_application_requirement_fit_summary_records_no_filtering_ranking_or_pareto():
    package = attach_application_requirement_fit(_package())
    summary = package["application_requirement_fit_summary"]

    assert summary["candidate_filtering_performed"] is False
    assert summary["ranking_performed"] is False
    assert summary["pareto_analysis_performed"] is False


def test_attach_application_requirement_fit_keeps_support_and_risk_tags_out_of_required_matches():
    package = attach_application_requirement_fit(
        {
            "candidate_systems": [
                _candidate(
                    candidate_id="support-risk-only",
                    surface_function_profile={
                        "primary_service_functions": ["oxidation_resistance"],
                        "secondary_service_functions": [],
                        "surface_functions": [
                            {
                                "function_id": "thermal_barrier",
                                "function_kind": "support_or_lifecycle_consideration",
                            },
                            {
                                "function_id": "thermal_cycling_tolerance",
                                "function_kind": "risk_or_interface_consideration",
                            },
                        ],
                    },
                )
            ],
        }
    )
    fit = package["candidate_systems"][0]["application_requirement_fit"]

    assert fit["matched_required_primary_service_functions"] == ["oxidation_resistance"]
    assert fit["missing_required_primary_service_functions"] == ["thermal_barrier"]
    assert fit["matched_desired_secondary_service_functions"] == []
