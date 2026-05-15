import pytest

from src.material_system_schema import (
    EVIDENCE_MATURITY_LEVELS,
    SYSTEM_ARCHITECTURE_TYPES,
    assert_valid_material_system_candidate,
    evidence_maturity,
    validate_gradient_architecture,
    validate_material_system_candidate,
)


def test_system_architecture_types_include_phase5_anchor_architectures():
    assert "coating_enabled" in SYSTEM_ARCHITECTURE_TYPES
    assert "cmc_plus_ebc" in SYSTEM_ARCHITECTURE_TYPES
    assert "spatially_graded_am_system" in SYSTEM_ARCHITECTURE_TYPES


def test_evidence_maturity_levels_include_a_through_f_and_unknown():
    assert set(EVIDENCE_MATURITY_LEVELS) >= {"A", "B", "C", "D", "E", "F", "unknown"}


def test_validate_gradient_architecture_accepts_valid_surface_oxidation_gradient():
    gradient = {
        "gradient_type": "surface_oxidation_gradient",
        "spatial_direction": "surface_to_core",
        "zones": [{"zone_id": "surface", "target": "oxidation resistance"}],
        "gradient_risks": ["process-control sensitivity"],
        "process_control_requirements": ["oxygen-potential control"],
        "evidence_maturity": "D",
    }

    assert validate_gradient_architecture(gradient) == []


def test_validate_gradient_architecture_rejects_unknown_gradient_type():
    errors = validate_gradient_architecture({"gradient_type": "unknown_gradient"})

    assert any("gradient_type" in error for error in errors)


def test_validate_material_system_candidate_accepts_valid_cmc_ebc_candidate_without_gradient():
    candidate = {
        "candidate_id": "sic_sic_ebc_reference",
        "system_name": "SiC/SiC CMC + EBC reference",
        "system_architecture_type": "cmc_plus_ebc",
        "coating_or_surface_system": {"type": "environmental_barrier_coating"},
        "evidence_package": {"evidence_maturity": "B"},
    }

    assert validate_material_system_candidate(candidate) == []


def test_validate_material_system_candidate_accepts_valid_spatially_graded_am_candidate():
    candidate = {
        "candidate_id": "graded_am_surface_reference",
        "system_name": "Spatially graded AM surface alternative",
        "system_architecture_type": "spatially_graded_am_system",
        "gradient_architecture": {
            "gradient_type": "thermal_barrier_gradient",
            "spatial_direction": "surface_to_core",
            "zones": [{"zone_id": "surface"}, {"zone_id": "core"}],
            "evidence_maturity": "D",
        },
        "evidence_package": {"evidence_maturity": "D"},
    }

    assert validate_material_system_candidate(candidate) == []


def test_validate_material_system_candidate_rejects_unknown_architecture_type():
    candidate = {
        "candidate_id": "unknown_architecture",
        "system_name": "Unknown architecture",
        "system_architecture_type": "substrate_plus_mystery_layer",
    }

    errors = validate_material_system_candidate(candidate)

    assert any("system_architecture_type" in error for error in errors)


def test_validate_material_system_candidate_rejects_bulk_material_with_gradient():
    candidate = {
        "candidate_id": "bulk_with_gradient",
        "system_name": "Bulk material with gradient",
        "system_architecture_type": "bulk_material",
        "gradient_architecture": {"gradient_type": "composition_gradient"},
    }

    errors = validate_material_system_candidate(candidate)

    assert any("bulk_material systems must not carry gradient_architecture" in error for error in errors)


@pytest.mark.parametrize("maturity", ["A", "B", "C"])
def test_validate_material_system_candidate_rejects_generated_candidate_with_mature_evidence(
    maturity,
):
    candidate = {
        "candidate_id": f"generated_{maturity.lower()}",
        "system_name": "Generated concept",
        "system_architecture_type": "research_generated_system",
        "generated_candidate_flag": True,
        "evidence_package": {"evidence_maturity": maturity},
    }

    errors = validate_material_system_candidate(candidate)

    assert any("generated or research-mode candidates cannot use mature evidence" in error for error in errors)


def test_evidence_maturity_returns_unknown_when_evidence_package_missing():
    assert evidence_maturity({"candidate_id": "no_evidence"}) == "unknown"


def test_assert_valid_material_system_candidate_raises_value_error_for_invalid_candidate():
    with pytest.raises(ValueError, match="candidate_id is required"):
        assert_valid_material_system_candidate(
            {
                "system_name": "Missing identifier",
                "system_architecture_type": "not_real",
            }
        )
