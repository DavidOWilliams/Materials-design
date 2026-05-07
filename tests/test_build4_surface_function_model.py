import json

from src.process_route_enrichment import attach_process_route_enrichment
from src.surface_function_model import (
    attach_surface_function_profiles,
    build_surface_function_coverage_summary,
    classify_function_kind,
    compare_required_surface_functions_to_candidates,
    infer_candidate_surface_functions,
    infer_required_surface_functions,
    load_surface_function_taxonomy,
)
from src.ui_view_models import package_to_json_safe_dict
from src.vertical_slices.ceramics_first import build_ceramics_first_candidate_package


def _package():
    return attach_surface_function_profiles(
        attach_process_route_enrichment(build_ceramics_first_candidate_package())
    )


def _by_id(package):
    return {candidate["candidate_id"]: candidate for candidate in package["candidate_systems"]}


def _function_ids(candidate):
    return {item["function_id"] for item in infer_candidate_surface_functions(candidate)}


def test_surface_function_taxonomy_json_loads():
    taxonomy = load_surface_function_taxonomy()

    assert "thermal_barrier" in taxonomy
    assert "unknown_surface_function" in taxonomy
    json.dumps(taxonomy)


def test_classify_function_kind_separates_service_and_support_functions():
    assert classify_function_kind("thermal_barrier") == "primary_service_function"
    assert classify_function_kind("inspection_access_or_monitoring") == "support_or_lifecycle_consideration"
    assert classify_function_kind("coating_interface_management") == "risk_or_interface_consideration"


def test_infer_required_surface_functions_detects_ceramics_first_surface_needs():
    source = build_ceramics_first_candidate_package()
    required = infer_required_surface_functions(source["requirement_schema"], source["design_space"])
    function_ids = {item["function_id"] for item in required}

    assert {"oxidation_resistance", "inspection_access_or_monitoring"} <= function_ids
    assert "thermal_barrier" in function_ids or "thermal_cycling_tolerance" in function_ids
    assert "environmental_barrier" in function_ids or "steam_recession_resistance" in function_ids


def test_representative_candidates_get_expected_surface_functions():
    candidates = _by_id(_package())

    assert "thermal_barrier" in _function_ids(candidates["demo_ni_superalloy_bondcoat_tbc_comparison"])
    assert "thermal_barrier" in _function_ids(candidates["tbc_reference"])
    assert _function_ids(candidates["sic_sic_cmc_ebc_anchor"]) & {
        "environmental_barrier",
        "steam_recession_resistance",
    }
    assert _function_ids(candidates["ebc_reference"]) & {
        "environmental_barrier",
        "steam_recession_resistance",
    }
    assert "wear_resistance" in _function_ids(candidates["wear_coating_reference"])
    assert {"oxidation_resistance", "transition_zone_management"} <= _function_ids(
        candidates["surface_oxidation_gradient"]
    )
    assert {"thermal_barrier", "transition_zone_management"} <= _function_ids(
        candidates["thermal_barrier_gradient"]
    )
    assert "environmental_barrier" in _function_ids(candidates["rare_earth_silicate_ebc_stack"])
    assert "oxidation_resistance" in _function_ids(candidates["oxidation_hot_corrosion_coating"])
    assert "erosion_resistance" in _function_ids(candidates["erosion_resistant_coating_system"])
    assert {"wear_resistance", "hard_surface"} & _function_ids(candidates["wear_hard_surface_gradient_variant"])
    assert "transition_zone_management" in _function_ids(candidates["metal_ceramic_transition_gradient_concept"])


def test_candidate_surface_profiles_include_function_kind_groups():
    candidates = _by_id(_package())
    coating_profile = candidates["demo_ni_superalloy_bondcoat_tbc_comparison"]["surface_function_profile"]
    gradient_profile = candidates["thermal_barrier_gradient"]["surface_function_profile"]

    assert "thermal_barrier" in coating_profile["primary_service_functions"]
    assert coating_profile["support_or_lifecycle_considerations"]
    assert "transition_zone_management" in gradient_profile["secondary_service_functions"]
    assert all("function_kind" in item for item in coating_profile["surface_functions"])
    assert candidates["rare_earth_silicate_ebc_stack"]["surface_function_profile"]["primary_service_functions"]
    assert candidates["thermal_porosity_gradient_variant"]["surface_function_profile"]["primary_service_functions"]


def test_attach_surface_function_profiles_preserves_candidate_count_and_order():
    source = attach_process_route_enrichment(build_ceramics_first_candidate_package())
    enriched = attach_surface_function_profiles(source)

    assert [candidate["candidate_id"] for candidate in enriched["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in source["candidate_systems"]
    ]
    assert all(candidate["surface_function_profile"] for candidate in enriched["candidate_systems"])
    assert enriched["ranked_recommendations"] == []
    assert enriched["pareto_front"] == []


def test_build_surface_function_coverage_summary_returns_shared_coating_gradient_functions():
    package = _package()
    summary = build_surface_function_coverage_summary(package)

    assert summary["candidate_count"] == len(package["candidate_systems"])
    assert summary["shared_coating_gradient_functions"]
    assert summary["function_to_candidate_ids"]
    assert summary["primary_service_function_to_candidate_ids"]
    assert summary["support_consideration_to_candidate_ids"]
    assert summary["shared_coating_gradient_primary_service_functions"]
    assert summary["shared_coating_gradient_support_considerations"]
    assert summary["coating_enabled_function_counts"]
    assert summary["spatial_gradient_function_counts"]


def test_support_only_required_coverage_is_not_primary_service_coverage():
    package = {
        "requirement_schema": {},
        "design_space": {},
        "required_surface_functions": [
            {
                "function_id": "inspection_access_or_monitoring",
                "display_name": "Inspection access or monitoring",
                "function_kind": "support_or_lifecycle_consideration",
            }
        ],
        "candidate_systems": [
            {
                "candidate_id": "inspection-only",
                "candidate_class": "coating_enabled",
                "system_architecture_type": "substrate_plus_coating",
                "surface_function_profile": {
                    "surface_functions": [
                        {
                            "function_id": "inspection_access_or_monitoring",
                            "function_kind": "support_or_lifecycle_consideration",
                        }
                    ],
                    "primary_service_functions": [],
                    "secondary_service_functions": [],
                    "support_or_lifecycle_considerations": ["inspection_access_or_monitoring"],
                    "risk_or_interface_considerations": [],
                },
            }
        ],
    }

    summary = build_surface_function_coverage_summary(package)
    comparison = compare_required_surface_functions_to_candidates(package)

    assert summary["covered_required_primary_service_functions"] == []
    assert summary["uncovered_required_primary_service_functions"] == []
    assert comparison["covered_required_primary_service_function_ids"] == []
    assert comparison["covered_required_support_consideration_ids"] == ["inspection_access_or_monitoring"]


def test_compare_required_surface_functions_to_candidates_is_descriptive_not_ranking():
    comparison = compare_required_surface_functions_to_candidates(_package())

    assert comparison["required_function_ids"]
    assert comparison["covered_required_function_ids"]
    assert comparison["covered_required_primary_service_function_ids"]
    assert "covered_required_support_consideration_ids" in comparison
    assert "rank" not in comparison
    assert "winner" not in comparison
    assert any("descriptive" in note for note in comparison["coverage_notes"])


def test_surface_function_package_remains_json_safe():
    json.dumps(package_to_json_safe_dict(_package()))
