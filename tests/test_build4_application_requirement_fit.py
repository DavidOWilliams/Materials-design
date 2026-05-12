from src.application_requirement_fit import assess_application_requirement_fit


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

    assert fit["fit_status"] == "does_not_meet_core_requirements"
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
