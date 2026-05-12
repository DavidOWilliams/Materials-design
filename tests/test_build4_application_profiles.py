from src.application_profiles import (
    DEFAULT_APPLICATION_PROFILE_ID,
    default_application_profile,
    get_application_profile,
    list_application_profiles,
    resolve_application_profile,
)


def test_default_profile_id_is_hot_section_thermal_cycling_oxidation():
    profile = default_application_profile()

    assert DEFAULT_APPLICATION_PROFILE_ID == "hot_section_thermal_cycling_oxidation"
    assert profile["profile_id"] == "hot_section_thermal_cycling_oxidation"


def test_default_profile_name_is_hot_section_thermal_cycling_and_oxidation():
    profile = default_application_profile()

    assert profile["profile_name"] == "Hot-section thermal cycling and oxidation"


def test_required_primary_functions_are_exactly_oxidation_resistance_and_thermal_barrier():
    profile = default_application_profile()

    assert profile["required_primary_service_functions"] == [
        "oxidation_resistance",
        "thermal_barrier",
    ]


def test_desired_secondary_function_is_exactly_thermal_cycling_tolerance():
    profile = default_application_profile()

    assert profile["desired_secondary_service_functions"] == [
        "thermal_cycling_tolerance",
    ]


def test_all_default_profile_constraints_are_present():
    profile = default_application_profile()

    assert profile["constraints"] == {
        "thermal_exposure": "very_high",
        "thermal_cycling": "high",
        "oxidation_steam_exposure": "high",
        "inspection_difficulty": "difficult",
        "repair": "desired",
        "certification_sensitivity": "very_high",
        "minimum_evidence_maturity": "C",
    }


def test_assessment_boundaries_exclude_assessment_outputs():
    profile = default_application_profile()

    assert profile["assessment_boundaries"] == {
        "ranks_candidates": False,
        "shortlists_candidates": False,
        "validates_plan": False,
        "generates_variants": False,
        "populates_pareto_output": False,
    }


def test_default_application_profile_returns_defensive_copy():
    profile = default_application_profile()
    profile["profile_id"] = "mutated"
    profile["required_primary_service_functions"].append("mutated")
    profile["constraints"]["thermal_exposure"] = "mutated"
    profile["assessment_boundaries"]["ranks_candidates"] = True

    next_profile = default_application_profile()

    assert next_profile["profile_id"] == "hot_section_thermal_cycling_oxidation"
    assert next_profile["required_primary_service_functions"] == [
        "oxidation_resistance",
        "thermal_barrier",
    ]
    assert next_profile["constraints"]["thermal_exposure"] == "very_high"
    assert next_profile["assessment_boundaries"]["ranks_candidates"] is False


def test_list_application_profiles_includes_default_profile():
    profiles = list_application_profiles()

    assert {
        "profile_id": "hot_section_thermal_cycling_oxidation",
        "profile_name": "Hot-section thermal cycling and oxidation",
    } in profiles


def test_get_application_profile_returns_default_profile_for_default_id():
    profile = get_application_profile("hot_section_thermal_cycling_oxidation")

    assert profile == default_application_profile()


def test_resolve_application_profile_none_returns_default_profile():
    profile = resolve_application_profile()

    assert profile == default_application_profile()


def test_resolve_application_profile_default_id_returns_default_profile():
    profile = resolve_application_profile("hot_section_thermal_cycling_oxidation")

    assert profile == default_application_profile()


def test_unknown_profile_id_raises_value_error_with_available_profile_ids():
    try:
        get_application_profile("unknown_profile")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown application profile ID.")

    assert "unknown_profile" in message
    assert "hot_section_thermal_cycling_oxidation" in message


def test_registry_returned_profiles_are_defensive_copies():
    profile = get_application_profile("hot_section_thermal_cycling_oxidation")
    profile["profile_id"] = "mutated"
    profile["required_primary_service_functions"].append("mutated")
    profile["constraints"]["thermal_exposure"] = "mutated"

    resolved = resolve_application_profile("hot_section_thermal_cycling_oxidation")

    assert resolved == default_application_profile()
    assert resolved["profile_id"] == "hot_section_thermal_cycling_oxidation"
    assert resolved["required_primary_service_functions"] == [
        "oxidation_resistance",
        "thermal_barrier",
    ]
    assert resolved["constraints"]["thermal_exposure"] == "very_high"
