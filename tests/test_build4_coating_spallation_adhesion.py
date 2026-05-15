import json

from src.factor_models.coatings.spallation_adhesion import (
    attach_coating_spallation_adhesion,
    build_coating_spallation_adhesion_profile,
    build_coating_spallation_adhesion_summary,
    classify_coating_system,
    is_coating_spallation_relevant_candidate,
)
from src.ui_view_models import package_to_json_safe_dict
from tools.build4_review_pack_exporter import build_full_build4_package


def _tbc_candidate():
    return {
        "candidate_id": "tbc-test",
        "candidate_class": "coating_enabled",
        "system_architecture_type": "substrate_plus_coating",
        "name": "Ni superalloy with YSZ TBC and bond coat",
        "base_material_family": "Ni superalloy",
        "coating_or_surface_system": {
            "coating_type": "thermal barrier coating",
            "layers": [{"name": "MCrAlY bond coat"}, {"name": "YSZ top coat"}],
            "failure_modes": ["spallation", "CTE mismatch", "thermal cycling durability"],
        },
        "inspection_plan": {"inspection_burden": "high"},
        "repairability": {"repairability_level": "limited"},
        "qualification_route": {"qualification_burden": "very_high"},
        "evidence_maturity": "B",
    }


def _ebc_candidate():
    return {
        "candidate_id": "ebc-test",
        "candidate_class": "ceramic_matrix_composite",
        "system_architecture_type": "composite_architecture",
        "name": "SiC/SiC CMC with rare-earth silicate EBC",
        "environmental_barrier_coating": {"name": "rare-earth silicate EBC"},
        "risks": ["water vapor durability", "steam recession", "coating defects and repair limits"],
        "repairability": {"repairability_level": "limited"},
        "inspection_plan": {"inspection_burden": "high"},
        "qualification_route": {"qualification_burden": "high"},
        "evidence_maturity": "C",
    }


def _wear_candidate():
    return {
        "candidate_id": "wear-test",
        "candidate_class": "coating_enabled",
        "system_architecture_type": "substrate_plus_coating",
        "name": "Hard wear coating on titanium substrate",
        "coating_system": {
            "coating_type": "hard wear coating",
            "failure_modes": ["adhesion", "residual stress", "substrate fatigue debit"],
        },
        "repairability": {"repairability_level": "moderate"},
        "inspection_plan": {"inspection_burden": "medium"},
        "qualification_route": {"qualification_burden": "high"},
        "evidence_maturity": "C",
    }


def _monolithic_candidate():
    return {
        "candidate_id": "sic-test",
        "candidate_class": "monolithic_ceramic",
        "system_architecture_type": "monolith",
        "name": "Monolithic silicon carbide",
        "evidence_maturity": "B",
    }


def test_relevance_for_tbc_ebc_wear_and_non_coating_ceramic():
    assert is_coating_spallation_relevant_candidate(_tbc_candidate()) is True
    assert is_coating_spallation_relevant_candidate(_ebc_candidate()) is True
    assert is_coating_spallation_relevant_candidate(_wear_candidate()) is True
    assert is_coating_spallation_relevant_candidate(_monolithic_candidate()) is False


def test_classification_for_tbc_ebc_and_wear_systems():
    assert classify_coating_system(_tbc_candidate())["coating_system_kind"] == "thermal_barrier_coating"
    assert classify_coating_system(_ebc_candidate())["coating_system_kind"] == "environmental_barrier_coating"
    assert classify_coating_system(_wear_candidate())["coating_system_kind"] == "wear_or_erosion_coating"


def test_tbc_profile_exposes_spallation_or_thermal_cycling_risk():
    profile = build_coating_spallation_adhesion_profile(_tbc_candidate())

    assert profile["adhesion_or_spallation_risk"] == "high"
    assert profile["thermal_cycling_damage_risk"] == "high"
    assert profile["not_a_life_prediction"] is True
    assert profile["not_a_qualification_claim"] is True


def test_ebc_profile_exposes_environmental_attack_and_validation():
    profile = build_coating_spallation_adhesion_profile(_ebc_candidate())

    assert profile["environmental_attack_risk"] == "high"
    assert any("recession" in item.lower() or "compatibility" in item.lower() for item in profile["required_validation_evidence"])


def test_wear_profile_exposes_adhesion_substrate_and_repair_evidence():
    profile = build_coating_spallation_adhesion_profile(_wear_candidate())

    evidence = " ".join(profile["required_validation_evidence"]).lower()
    assert "adhesion" in evidence
    assert "substrate" in evidence
    assert "repair" in evidence or "recoat" in evidence


def test_attach_preserves_candidate_count_order_and_decision_fields():
    package = {
        "candidate_systems": [_tbc_candidate(), _monolithic_candidate(), _wear_candidate()],
        "ranked_recommendations": [],
        "pareto_front": [],
        "warnings": [],
    }
    enriched = attach_coating_spallation_adhesion(package)

    assert [candidate["candidate_id"] for candidate in enriched["candidate_systems"]] == [
        "tbc-test",
        "sic-test",
        "wear-test",
    ]
    assert len(enriched["candidate_systems"]) == len(package["candidate_systems"])
    assert "coating_spallation_adhesion" not in package["candidate_systems"][0]
    assert "coating_spallation_adhesion" in enriched["candidate_systems"][0]
    assert enriched["ranked_recommendations"] == []
    assert enriched["pareto_front"] == []


def test_summary_has_relevant_candidate_count():
    package = attach_coating_spallation_adhesion(
        {"candidate_systems": [_tbc_candidate(), _ebc_candidate(), _monolithic_candidate()]}
    )
    summary = build_coating_spallation_adhesion_summary(package["candidate_systems"])

    assert summary["relevant_candidate_count"] > 0
    assert summary["coating_system_kind_counts"]["thermal_barrier_coating"] == 1
    assert summary["coating_system_kind_counts"]["environmental_barrier_coating"] == 1


def test_review_pack_package_includes_coating_summary_and_preserves_boundaries():
    package = build_full_build4_package()
    safe = package_to_json_safe_dict(package)

    assert package["coating_spallation_adhesion_summary"]["relevant_candidate_count"] > 0
    assert package["optimisation_summary"]["generated_candidate_count"] == 0
    assert package["diagnostics"]["live_model_calls_made"] is False
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    json.dumps(safe)
