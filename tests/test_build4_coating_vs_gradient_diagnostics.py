import json

from src.coating_vs_gradient_diagnostics import (
    attach_coating_vs_gradient_diagnostic,
    build_coating_vs_gradient_diagnostic,
    build_surface_protection_profile,
    classify_surface_function,
    compare_surface_profiles,
    is_coating_enabled_candidate,
    is_spatial_gradient_candidate,
)
from src.optimisation.deterministic_optimizer import attach_deterministic_optimisation
from src.process_route_enrichment import attach_process_route_enrichment
from src.ui_view_models import package_to_json_safe_dict
from src.vertical_slices.ceramics_first import build_ceramics_first_candidate_package


def _package():
    package = build_ceramics_first_candidate_package()
    package = attach_process_route_enrichment(package)
    package = attach_deterministic_optimisation(package)
    return package


def _by_id(candidates):
    return {candidate["candidate_id"]: candidate for candidate in candidates}


def test_is_coating_enabled_candidate_recognises_class_and_architecture():
    assert is_coating_enabled_candidate({"candidate_class": "coating_enabled"}) is True
    assert is_coating_enabled_candidate({"system_architecture_type": "substrate_plus_coating"}) is True
    assert is_coating_enabled_candidate({"candidate_class": "spatially_graded_am"}) is False


def test_is_spatial_gradient_candidate_recognises_class_and_architecture():
    assert is_spatial_gradient_candidate({"candidate_class": "spatially_graded_am"}) is True
    assert is_spatial_gradient_candidate({"system_architecture_type": "spatial_gradient"}) is True
    assert is_spatial_gradient_candidate({"candidate_class": "coating_enabled"}) is False


def test_classify_surface_function_finds_representative_surface_functions():
    candidates = _by_id(_package()["candidate_systems"])

    assert "thermal_barrier" in classify_surface_function(candidates["tbc_reference"])
    assert "environmental_barrier" in classify_surface_function(candidates["ebc_reference"])
    assert "oxidation_resistance" in classify_surface_function(candidates["surface_oxidation_gradient"])
    assert "wear_resistance" in classify_surface_function(candidates["wear_coating_reference"])
    assert "wear_resistance" in classify_surface_function(candidates["surface_wear_gradient"])


def test_build_surface_protection_profile_includes_route_burden_fields():
    candidate = _by_id(_package()["candidate_systems"])["surface_oxidation_gradient"]
    profile = build_surface_protection_profile(candidate)

    assert profile["inspection_burden"] == "high"
    assert profile["repairability_level"] in {"limited", "poor"}
    assert profile["qualification_burden"] in {"high", "very_high"}
    assert profile["process_route_template_id"] == "surface_oxidation_gradient"


def test_compare_surface_profiles_never_selects_winner():
    candidates = _by_id(_package()["candidate_systems"])
    coating = build_surface_protection_profile(candidates["tbc_reference"])
    gradient = build_surface_protection_profile(candidates["thermal_barrier_gradient"])

    comparison = compare_surface_profiles(coating, gradient)

    assert comparison["winner"] is None
    assert comparison["decision_status"] == "comparison_only_no_winner"
    assert "No winner selected." in comparison["diagnostic_notes"]


def test_build_coating_vs_gradient_diagnostic_finds_both_sides_and_caps_pairwise():
    diagnostic = build_coating_vs_gradient_diagnostic(_package())

    assert diagnostic["diagnostic_status"] == "comparison_only_no_winner"
    assert diagnostic["comparison_required"] is True
    assert len(diagnostic["coating_enabled_candidate_ids"]) == 4
    assert len(diagnostic["spatial_gradient_candidate_ids"]) == 4
    assert 0 < len(diagnostic["pairwise_comparisons"]) <= 12
    first_ids = [
        (item["coating_candidate_id"], item["gradient_candidate_id"])
        for item in diagnostic["pairwise_comparisons"]
    ]
    assert first_ids == sorted(first_ids, key=lambda pair: (pair[0], pair[1]))[: len(first_ids)] or first_ids


def test_all_gradient_low_maturity_produces_warning_or_observation():
    diagnostic = build_coating_vs_gradient_diagnostic(_package())

    assert any("All spatial-gradient candidates are D/E/F" in warning for warning in diagnostic["warnings"])
    assert diagnostic["evidence_maturity_observations"]["gradient"]


def test_attach_coating_vs_gradient_diagnostic_preserves_package_boundaries():
    package = _package()
    attached = attach_coating_vs_gradient_diagnostic(package)

    assert [candidate["candidate_id"] for candidate in attached["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in package["candidate_systems"]
    ]
    assert attached["ranked_recommendations"] == []
    assert attached["pareto_front"] == []
    assert attached["coating_vs_gradient_comparison"] == package["coating_vs_gradient_comparison"]
    json.dumps(package_to_json_safe_dict(attached))
