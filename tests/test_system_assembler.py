from src.system_assembler import (
    assemble_material_system,
    assemble_material_systems,
    summarize_system_assembly,
)


def test_assemble_material_system_adds_interfaces_trace_and_warnings():
    candidate = {
        "candidate_id": "coat-assembly-1",
        "name": "Coated nickel system",
        "candidate_class": "coating_enabled",
        "coating_or_surface_system": {"coating_type": "TBC"},
        "source_type": "curated_engineering_reference",
    }

    assembled = assemble_material_system(candidate)

    assert assembled["candidate_id"] == "coat-assembly-1"
    assert "normalized_material_system_candidate" in assembled["assembly_trace"]
    assert "evaluated_candidate_evidence" in assembled["assembly_trace"]
    assert "assessed_interface_risks" in assembled["assembly_trace"]
    assert {interface["interface_type"] for interface in assembled["interfaces"]} == {
        "substrate_coating"
    }
    assert assembled["assembly_warnings"] == []


def test_missing_coating_details_produces_assembly_warning_not_exception():
    candidate = {
        "candidate_id": "coat-missing-assembly",
        "name": "Missing coating details",
        "candidate_class": "coating_enabled",
        "source_type": "curated_engineering_reference",
    }

    assembled = assemble_material_system(candidate)

    assert any(
        "missing coating_or_surface_system" in warning
        for warning in assembled["assembly_warnings"]
    )
    assert any(
        interface["interface_type"] == "substrate_coating"
        and interface["risk_level"] == "unknown"
        for interface in assembled["interfaces"]
    )


def test_spatially_graded_am_without_gradient_gets_warning():
    candidate = {
        "candidate_id": "graded-missing",
        "candidate_class": "spatially_graded_am",
        "source_type": "literature_reference",
    }

    assembled = assemble_material_system(candidate)

    assert any(
        "missing gradient_architecture" in warning for warning in assembled["assembly_warnings"]
    )
    assert any(
        interface["interface_type"] == "gradient_transition_zone"
        for interface in assembled["interfaces"]
    )


def test_cmc_without_constituents_or_ebc_gets_warning():
    candidate = {
        "candidate_id": "bare-cmc",
        "candidate_class": "ceramic_matrix_composite",
        "source_type": "curated_engineering_reference",
    }

    assembled = assemble_material_system(candidate)

    assert any(
        "missing constituents and EBC/coating data" in warning
        for warning in assembled["assembly_warnings"]
    )


def test_bulk_material_with_coating_gets_mislabel_warning():
    candidate = {
        "candidate_id": "bulk-with-coating",
        "candidate_class": "metallic",
        "system_architecture_type": "bulk_material",
        "coating_or_surface_system": {"coating_type": "TBC"},
        "source_type": "curated_engineering_reference",
    }

    assembled = assemble_material_system(candidate)

    assert any("may be mislabelled" in warning for warning in assembled["assembly_warnings"])
    assert any("Coating-only records" in warning for warning in assembled["assembly_warnings"])


def test_coating_primary_bulk_material_does_not_get_coating_only_warning():
    candidate = {
        "candidate_id": "coating-primary",
        "candidate_class": "metallic",
        "system_architecture_type": "bulk_material",
        "coating_or_surface_system": {"coating_type": "TBC"},
        "coating_primary": True,
        "source_type": "curated_engineering_reference",
    }

    assembled = assemble_material_system(candidate)

    assert any("may be mislabelled" in warning for warning in assembled["assembly_warnings"])
    assert not any("Coating-only records" in warning for warning in assembled["assembly_warnings"])


def test_assemble_material_systems_preserves_input_length_and_order():
    candidates = [
        {
            "candidate_id": "first",
            "candidate_class": "coating_enabled",
            "coating_or_surface_system": {"coating_type": "TBC"},
            "source_type": "curated_engineering_reference",
        },
        {
            "candidate_id": "second",
            "candidate_class": "spatially_graded_am",
            "gradient_architecture": {"gradient_types": ["composition"]},
            "source_type": "literature_reference",
        },
        {
            "candidate_id": "third",
            "candidate_class": "ceramic_matrix_composite",
            "environmental_barrier_coating": {"name": "EBC"},
            "source_type": "curated_engineering_reference",
        },
    ]

    assembled = assemble_material_systems(candidates)

    assert len(assembled) == len(candidates)
    assert [candidate["candidate_id"] for candidate in assembled] == ["first", "second", "third"]


def test_summarize_system_assembly_returns_architecture_mix_and_interface_summary():
    candidates = [
        {
            "candidate_id": "coat-summary",
            "candidate_class": "coating_enabled",
            "coating_or_surface_system": {"coating_type": "TBC"},
            "source_type": "curated_engineering_reference",
        },
        {
            "candidate_id": "graded-summary",
            "candidate_class": "spatially_graded_am",
            "gradient_architecture": {"gradient_types": ["composition"]},
            "source_type": "literature_reference",
        },
        {
            "candidate_id": "bulk-summary",
            "candidate_class": "metallic",
            "source_type": "curated_engineering_reference",
        },
    ]

    summary = summarize_system_assembly(candidates)

    assert summary["candidate_count"] == 3
    assert summary["system_architecture_mix"]["coating_enabled"] == 1
    assert summary["system_architecture_mix"]["spatially_graded_am_system"] == 1
    assert summary["system_architecture_mix"]["bulk_material"] == 1
    assert summary["candidate_class_mix"]["coating_enabled"] == 1
    assert summary["candidates_with_interfaces"] == 2
    assert summary["interface_risk_summary"]["candidate_count"] == 3
    assert summary["interface_risk_summary"]["interface_type_counts"]["substrate_coating"] == 1
    assert (
        summary["interface_risk_summary"]["interface_type_counts"]["gradient_transition_zone"]
        == 1
    )


def test_no_candidates_are_filtered_out_even_when_diagnostics_are_unknown():
    candidates = [
        {
            "candidate_id": "coating-missing",
            "candidate_class": "coating_enabled",
            "source_type": "curated_engineering_reference",
        },
        {
            "candidate_id": "graded-missing",
            "candidate_class": "spatially_graded_am",
            "source_type": "literature_reference",
        },
        {
            "candidate_id": "plain-bulk",
            "candidate_class": "metallic",
            "source_type": "curated_engineering_reference",
        },
    ]

    assembled = assemble_material_systems(candidates)
    summary = summarize_system_assembly(candidates)

    assert len(assembled) == 3
    assert summary["candidate_count"] == 3
    assert [candidate["candidate_id"] for candidate in assembled] == [
        "coating-missing",
        "graded-missing",
        "plain-bulk",
    ]
