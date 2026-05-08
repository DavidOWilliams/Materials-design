import json

from src.factor_models.graded_am.transition_zone_risk import (
    attach_graded_am_transition_zone_risk,
    build_graded_am_transition_zone_profile,
    build_graded_am_transition_zone_summary,
    classify_gradient_architecture,
    is_graded_am_transition_relevant_candidate,
)
from src.ui_view_models import package_to_json_safe_dict
from tools.build4_review_pack_exporter import build_full_build4_package


def _oxidation_gradient():
    return {
        "candidate_id": "oxidation-gradient-test",
        "candidate_class": "spatially_graded_am",
        "system_architecture_type": "spatial_gradient",
        "name": "Surface oxidation-resistant gradient",
        "gradient_architecture": {
            "gradient_types": ["composition"],
            "manufacturing_route": "directed energy deposition with composition transition",
            "transition_risks": ["composition control", "cracking"],
        },
        "summary": "Oxidation resistant surface gradient with oxide-forming additions.",
        "inspection_plan": {"inspection_burden": "high"},
        "repairability": {"repairability_level": "limited"},
        "qualification_route": {"qualification_burden": "high"},
        "evidence_maturity": "E",
    }


def _thermal_gradient():
    return {
        "candidate_id": "thermal-gradient-test",
        "candidate_class": "spatially_graded_am",
        "system_architecture_type": "spatial_gradient",
        "name": "Thermal barrier porosity gradient",
        "gradient_architecture": {
            "gradient_types": ["porosity_and_composition"],
            "manufacturing_route": "multi-material additive manufacturing",
            "transition_risks": ["delamination", "porosity control", "thermal cycling evidence gaps"],
        },
        "summary": "Thermal barrier gradient with porosity and thermal expansion transition intent.",
        "inspection_plan": {"inspection_burden": "high"},
        "repairability": {"repairability_level": "poor"},
        "qualification_route": {"qualification_burden": "very_high"},
        "evidence_maturity": "F",
    }


def _wear_gradient():
    return {
        "candidate_id": "wear-gradient-test",
        "candidate_class": "spatially_graded_am",
        "system_architecture_type": "spatial_gradient",
        "name": "Wear hard-surface gradient",
        "gradient_architecture": {
            "gradient_types": ["composition_and_microstructure"],
            "manufacturing_route": "hybrid additive repair",
            "transition_risks": ["residual stress", "hard-zone cracking", "machining response"],
        },
        "summary": "Hard surface wear gradient with hardness mapping needs.",
        "inspection_plan": {"inspection_burden": "medium"},
        "repairability": {"repairability_level": "moderate"},
        "qualification_route": {"qualification_burden": "high"},
        "evidence_maturity": "D",
    }


def _coating_candidate():
    return {
        "candidate_id": "coating-test",
        "candidate_class": "coating_enabled",
        "system_architecture_type": "substrate_plus_coating",
        "name": "Thermal barrier coating",
        "coating_or_surface_system": {"coating_type": "TBC"},
        "evidence_maturity": "B",
    }


def test_relevance_for_surface_oxidation_thermal_wear_and_non_gradient_coating():
    assert is_graded_am_transition_relevant_candidate(_oxidation_gradient()) is True
    assert is_graded_am_transition_relevant_candidate(_thermal_gradient()) is True
    assert is_graded_am_transition_relevant_candidate(_wear_gradient()) is True
    assert is_graded_am_transition_relevant_candidate(_coating_candidate()) is False


def test_classification_for_oxidation_thermal_and_wear_gradients():
    assert classify_gradient_architecture(_oxidation_gradient())["gradient_system_kind"] == "oxidation_resistant_surface_gradient"
    assert classify_gradient_architecture(_thermal_gradient())["gradient_system_kind"] == "thermal_barrier_or_porosity_gradient"
    assert classify_gradient_architecture(_wear_gradient())["gradient_system_kind"] == "wear_or_hard_surface_gradient"


def test_transition_zone_profile_exposes_complexity_and_inspection():
    profile = build_graded_am_transition_zone_profile(_thermal_gradient())

    assert profile["transition_zone_complexity"] == "high"
    assert profile["through_depth_inspection_difficulty"] == "high"
    assert profile["not_a_process_qualification_claim"] is True
    assert profile["not_a_life_prediction"] is True
    assert profile["not_a_final_recommendation"] is True


def test_low_maturity_gradient_surfaces_maturity_constraint():
    profile = build_graded_am_transition_zone_profile(_wear_gradient())

    assert "Evidence maturity D" in profile["maturity_constraint"]


def test_attach_preserves_candidate_count_order_and_decision_fields():
    package = {
        "candidate_systems": [_oxidation_gradient(), _coating_candidate(), _wear_gradient()],
        "ranked_recommendations": [],
        "pareto_front": [],
        "warnings": [],
    }
    enriched = attach_graded_am_transition_zone_risk(package)

    assert [candidate["candidate_id"] for candidate in enriched["candidate_systems"]] == [
        "oxidation-gradient-test",
        "coating-test",
        "wear-gradient-test",
    ]
    assert len(enriched["candidate_systems"]) == len(package["candidate_systems"])
    assert "graded_am_transition_zone_risk" not in package["candidate_systems"][0]
    assert "graded_am_transition_zone_risk" in enriched["candidate_systems"][0]
    assert enriched["ranked_recommendations"] == []
    assert enriched["pareto_front"] == []


def test_gradient_summary_has_relevant_candidate_count():
    package = attach_graded_am_transition_zone_risk(
        {"candidate_systems": [_oxidation_gradient(), _thermal_gradient(), _coating_candidate()]}
    )
    summary = build_graded_am_transition_zone_summary(package["candidate_systems"])

    assert summary["relevant_candidate_count"] > 0
    assert summary["gradient_system_kind_counts"]["oxidation_resistant_surface_gradient"] == 1
    assert summary["gradient_system_kind_counts"]["thermal_barrier_or_porosity_gradient"] == 1


def test_review_pack_package_includes_gradient_summary_and_preserves_boundaries():
    package = build_full_build4_package()
    safe = package_to_json_safe_dict(package)

    assert package["graded_am_transition_zone_summary"]["relevant_candidate_count"] > 0
    assert package["optimisation_summary"]["generated_candidate_count"] == 0
    assert package["diagnostics"]["live_model_calls_made"] is False
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    json.dumps(safe)
