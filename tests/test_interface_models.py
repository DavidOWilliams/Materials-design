from src.interface_models import (
    assess_interface_risks,
    infer_interface_type,
    summarize_interface_risks,
)


def _risk_by_type(candidate, interface_type):
    risks = assess_interface_risks(candidate)
    return next(risk for risk in risks if risk["interface_type"] == interface_type)


def test_infer_interface_type_identifies_common_interface_pairs():
    assert (
        infer_interface_type(
            {"role": "substrate", "name": "Ni superalloy"},
            {"role": "coating", "name": "thermal barrier coating"},
        )
        == "substrate_coating"
    )
    assert (
        infer_interface_type(
            {"role": "matrix", "name": "SiC matrix"},
            {"role": "fiber", "name": "SiC fiber"},
        )
        == "matrix_fiber"
    )
    assert (
        infer_interface_type(
            {"role": "fiber", "name": "SiC fiber"},
            {"role": "interphase", "name": "BN interphase"},
        )
        == "fiber_interphase"
    )


def test_coating_enabled_candidate_receives_substrate_coating_interface_risk():
    candidate = {
        "candidate_id": "coat-1",
        "candidate_class": "coating_enabled",
        "coating_or_surface_system": {"coating_type": "TBC", "layers": ["bond coat", "top coat"]},
        "evidence_maturity": "C",
    }

    risk = _risk_by_type(candidate, "substrate_coating")

    assert risk["risk_level"] == "medium"
    assert "coating_enabled_system" in risk["risk_flags"]


def test_cmc_plus_ebc_candidate_receives_cmc_ebc_interface_risk():
    candidate = {
        "candidate_id": "cmc-ebc-1",
        "candidate_class": "ceramic_matrix_composite",
        "system_architecture_type": "cmc_plus_ebc",
        "environmental_barrier_coating": {"name": "rare earth silicate EBC"},
        "evidence_maturity": "C",
    }

    risk = _risk_by_type(candidate, "cmc_ebc")

    assert risk["risk_level"] == "medium"
    assert "cmc_environmental_barrier_interface" in risk["risk_flags"]


def test_cmc_constituents_receive_matrix_fiber_and_fiber_interphase_risks():
    candidate = {
        "candidate_id": "cmc-constituents-1",
        "candidate_class": "ceramic_matrix_composite",
        "constituents": [
            {"name": "SiC matrix", "role": "matrix"},
            {"name": "SiC fiber", "role": "fiber"},
            {"name": "BN interphase", "role": "interphase"},
        ],
        "evidence_maturity": "C",
    }

    interface_types = {risk["interface_type"] for risk in assess_interface_risks(candidate)}

    assert "matrix_fiber" in interface_types
    assert "fiber_interphase" in interface_types


def test_spatially_graded_am_candidate_receives_gradient_transition_zone_risk():
    candidate = {
        "candidate_id": "grad-1",
        "candidate_class": "spatially_graded_am",
        "gradient_architecture": {"gradient_types": ["composition"]},
        "evidence_maturity": "C",
    }

    risk = _risk_by_type(candidate, "gradient_transition_zone")

    assert risk["risk_level"] == "medium"
    assert "spatially_graded_am_transition_zone" in risk["risk_flags"]


def test_multi_material_gradient_receives_metal_ceramic_transition_risk():
    candidate = {
        "candidate_id": "grad-2",
        "candidate_class": "spatially_graded_am",
        "gradient_architecture": {
            "gradient_types": ["multi_material_transition"],
            "multi_material_transitions": [
                {"location": "wall", "from_value": "nickel alloy", "to_value": "zirconia ceramic"}
            ],
        },
        "evidence_maturity": "C",
    }

    risk = _risk_by_type(candidate, "metal_ceramic_transition")

    assert risk["risk_level"] == "high"
    assert "multi_material_gradient_transition" in risk["risk_flags"]


def test_low_evidence_maturity_increases_interface_risk():
    mature = {
        "candidate_id": "coat-mature",
        "candidate_class": "coating_enabled",
        "coating_or_surface_system": {"coating_type": "TBC"},
        "evidence_maturity": "C",
    }
    exploratory = {
        **mature,
        "candidate_id": "coat-exploratory",
        "evidence_maturity": "E",
    }

    assert _risk_by_type(mature, "substrate_coating")["risk_level"] == "medium"
    assert _risk_by_type(exploratory, "substrate_coating")["risk_level"] == "high"


def test_missing_coating_details_produce_unknown_risk_not_exception():
    candidate = {
        "candidate_id": "coat-missing",
        "candidate_class": "coating_enabled",
        "evidence_maturity": "C",
    }

    risk = _risk_by_type(candidate, "substrate_coating")

    assert risk["risk_level"] == "unknown"
    assert "missing_coating_or_surface_system" in risk["risk_flags"]


def test_summarize_interface_risks_counts_types_levels_and_high_risk_ids():
    candidates = [
        {
            "candidate_id": "coat-1",
            "candidate_class": "coating_enabled",
            "coating_or_surface_system": {"coating_type": "TBC"},
            "evidence_maturity": "E",
        },
        {
            "candidate_id": "grad-1",
            "candidate_class": "spatially_graded_am",
            "gradient_architecture": {"gradient_types": ["composition"]},
            "evidence_maturity": "C",
        },
    ]

    summary = summarize_interface_risks(candidates)

    assert summary["candidate_count"] == 2
    assert summary["interface_type_counts"]["substrate_coating"] == 1
    assert summary["interface_type_counts"]["gradient_transition_zone"] == 1
    assert summary["risk_level_counts"]["high"] == 1
    assert summary["high_risk_candidate_ids"] == ["coat-1"]
