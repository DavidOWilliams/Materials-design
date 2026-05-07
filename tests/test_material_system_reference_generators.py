from src.candidate_generators.ceramic_reference_generator import (
    generate_ceramic_reference_candidates,
)
from src.candidate_generators.cmc_reference_generator import (
    generate_cmc_reference_candidates,
)
from src.candidate_generators.coating_component_generator import (
    generate_coating_component_references,
    generate_coating_enabled_reference_candidates,
)
from src.candidate_generators.graded_am_template_generator import (
    generate_graded_am_template_candidates,
)


def _assert_material_system_candidate_compatible(candidate):
    assert isinstance(candidate, dict)
    assert candidate["candidate_id"]
    assert candidate["candidate_class"]
    assert candidate["system_architecture_type"]
    assert candidate["system_name"]
    assert isinstance(candidate["constituents"], list)
    assert "process_route" in candidate
    assert candidate["evidence_package"]["evidence_maturity"] == candidate["evidence_maturity"]
    assert candidate["generated_candidate_flag"] is False
    assert candidate["research_mode_flag"] is False


def test_ceramic_generator_returns_monolithic_ceramic_candidate():
    candidates = generate_ceramic_reference_candidates()

    assert candidates
    assert any(candidate["candidate_class"] == "monolithic_ceramic" for candidate in candidates)
    assert all(
        candidate["system_architecture_type"] != "substrate_plus_coating"
        for candidate in candidates
    )


def test_cmc_generator_returns_sic_sic_ebc_candidate():
    candidates = generate_cmc_reference_candidates()

    assert any(
        candidate["candidate_id"] == "sic_sic_cmc_ebc_anchor"
        and "SiC/SiC" in candidate["system_name"]
        and candidate["coating_system"]["coating_type"]
        for candidate in candidates
    )
    assert len(candidates) >= 6
    assert any(
        candidate["candidate_id"] == "porous_matrix_oxide_oxide_cmc"
        and candidate["candidate_class"] == "ceramic_matrix_composite"
        for candidate in candidates
    )


def test_coating_component_references_preserve_role_and_substrate_family():
    components = generate_coating_component_references()

    assert components
    assert all(component["coating_role"] for component in components)
    assert all(component["substrate_family"] for component in components)
    assert all(component["standalone_bulk_candidate"] is False for component in components)


def test_coating_enabled_candidates_are_not_bulk_materials():
    candidates = generate_coating_enabled_reference_candidates()

    assert candidates
    assert len(candidates) >= 10
    assert all(candidate["candidate_class"] == "coating_enabled" for candidate in candidates)
    assert all(
        candidate["system_architecture_type"] == "substrate_plus_coating"
        for candidate in candidates
    )
    assert all(candidate["system_architecture_type"] != "bulk_material" for candidate in candidates)
    assert any(candidate["candidate_id"] == "advanced_tbc_stack_variant" for candidate in candidates)
    assert any(candidate["candidate_id"] == "oxidation_hot_corrosion_coating" for candidate in candidates)


def test_graded_am_generator_is_gated_by_spatial_gradients_when_design_space_provided():
    blocked_design_space = {
        "allowed_candidate_classes": ["metallic", "monolithic_ceramic"],
        "architecture_flags": {"allow_spatial_gradients": False},
        "system_architectures": ["bulk_material"],
    }
    allowed_design_space = {
        "allowed_candidate_classes": ["spatially_graded_am"],
        "architecture_flags": {"allow_spatial_gradients": True},
        "system_architectures": ["spatial_gradient"],
    }

    assert generate_graded_am_template_candidates(blocked_design_space) == []
    assert generate_graded_am_template_candidates(allowed_design_space)


def test_no_graded_am_candidate_has_evidence_maturity_a():
    candidates = generate_graded_am_template_candidates()

    assert candidates
    assert len(candidates) >= 9
    assert all(candidate["evidence_maturity"] != "A" for candidate in candidates)
    assert any(candidate["evidence_maturity"] in {"D", "E", "F"} for candidate in candidates)
    assert all(candidate["candidate_class"] == "spatially_graded_am" for candidate in candidates)
    assert any(candidate["candidate_id"] == "repair_oriented_graded_buildup_concept" for candidate in candidates)


def test_all_generated_candidates_are_material_system_candidate_compatible_dicts():
    all_candidates = (
        generate_ceramic_reference_candidates()
        + generate_cmc_reference_candidates()
        + generate_coating_enabled_reference_candidates()
        + generate_graded_am_template_candidates()
    )

    assert all_candidates
    for candidate in all_candidates:
        _assert_material_system_candidate_compatible(candidate)
