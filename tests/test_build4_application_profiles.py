import pytest

from src.application_profiles import (
    build_default_application_profiles,
    get_default_application_profile,
    normalise_application_profile,
    validate_application_profile,
)


def test_build_default_application_profiles_returns_required_ids():
    profiles = build_default_application_profiles()

    assert {
        "hot_section_thermal_cycling_oxidation",
        "cmc_ebc_steam_oxidation_component",
        "erosion_wear_surface_component",
        "repairable_coated_metallic_component",
        "exploratory_graded_surface_architecture",
    } <= set(profiles)


def test_get_default_application_profile_returns_deep_copy():
    first = get_default_application_profile()
    second = get_default_application_profile()

    first["required_primary_service_functions"].append("mutated")

    assert "mutated" not in second["required_primary_service_functions"]


def test_unknown_profile_id_raises_clear_value_error():
    with pytest.raises(ValueError, match="Available profile IDs"):
        get_default_application_profile("unknown-profile")


def test_validate_application_profile_returns_no_warnings_for_defaults():
    for profile in build_default_application_profiles().values():
        assert validate_application_profile(profile) == []


def test_normalise_application_profile_does_not_mutate_input():
    profile = {
        "profile_id": "test",
        "display_name": "Test",
        "required_primary_service_functions": ["oxidation_resistance", "thermal_barrier", "oxidation_resistance"],
    }
    original = dict(profile)

    normalised = normalise_application_profile(profile)

    assert profile == original
    assert normalised["required_primary_service_functions"] == ["oxidation_resistance", "thermal_barrier"]
    assert normalised["not_a_selection_request"] is True


def test_hot_section_profile_requires_thermal_barrier_and_oxidation():
    profile = get_default_application_profile("hot_section_thermal_cycling_oxidation")

    assert {"thermal_barrier", "oxidation_resistance"} <= set(profile["required_primary_service_functions"])


def test_cmc_ebc_profile_requires_environmental_oxidation_and_steam():
    profile = get_default_application_profile("cmc_ebc_steam_oxidation_component")

    assert {
        "environmental_barrier",
        "oxidation_resistance",
        "steam_recession_resistance",
    } <= set(profile["required_primary_service_functions"])


def test_exploratory_graded_profile_allows_exploratory_and_research_only():
    profile = get_default_application_profile("exploratory_graded_surface_architecture")

    assert profile["allow_exploratory_concepts"] is True
    assert profile["allow_research_only_concepts"] is True
    assert profile["minimum_evidence_maturity_for_engineering_use"] == "E"
