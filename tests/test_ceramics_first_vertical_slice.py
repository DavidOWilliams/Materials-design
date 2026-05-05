from src.vertical_slices.ceramics_first import (
    build_ceramics_first_anchor_schema,
    build_ceramics_first_candidate_package,
    build_ceramics_first_design_space,
    build_demo_build31_metallic_rows,
    summarize_ceramics_first_package,
)


def test_anchor_schema_has_coating_composite_and_spatial_gradient_intent_enabled():
    schema = build_ceramics_first_anchor_schema()

    assert schema["schema_version"] == "2.0"
    assert schema["prompt_raw"]
    assert schema["material_system_intent"]["allow_bulk_material_only"] is True
    assert schema["material_system_intent"]["allow_substrate_plus_coating"] is True
    assert schema["material_system_intent"]["allow_spatial_gradients"] is True
    assert schema["material_system_intent"]["allow_composite_architecture"] is True
    assert schema["material_system_intent"]["allow_research_mode_candidates"] is False
    assert schema["coating_allowed"] is True
    assert schema["composite_allowed"] is True
    assert schema["graded_architecture_allowed"] is True
    assert schema["research_generated_allowed"] is False
    assert schema["spatial_property_intent"]["coating_replacement_allowed"] is True
    assert schema["spatial_property_intent"]["gradient_as_coating_alternative"] is True
    assert isinstance(schema["ambiguities"], list)
    assert isinstance(schema["interpreter_trace"], list)


def test_design_space_requires_coating_gradient_comparison_and_disables_research_mode():
    design_space = build_ceramics_first_design_space()

    assert design_space["coating_vs_gradient_comparison_required"] is True
    assert design_space["research_mode_enabled"] is False
    assert "coating_enabled" in design_space["allowed_candidate_classes"]
    assert "ceramic_matrix_composite" in design_space["allowed_candidate_classes"]
    assert "monolithic_ceramic" in design_space["allowed_candidate_classes"]
    assert "spatially_graded_am" in design_space["allowed_candidate_classes"]
    assert design_space["architecture_flags"]["allow_substrate_plus_coating"] is True
    assert design_space["architecture_flags"]["allow_composite_architecture"] is True
    assert design_space["architecture_flags"]["allow_spatial_gradients"] is True
    assert design_space["architecture_flags"]["allow_research_mode_candidates"] is False


def test_demo_build31_rows_are_in_memory_metallic_comparison_rows():
    rows = build_demo_build31_metallic_rows()

    assert len(rows) >= 1
    assert "candidate_id" in rows.columns
    assert "candidate_generation" not in rows.to_string().lower()
    assert rows["candidate_id"].str.contains("ni_superalloy", case=False).any()


def test_package_contains_candidate_systems_and_recommendation_package_shape():
    package = build_ceramics_first_candidate_package()

    assert package["run_id"]
    assert package["requirement_schema"]["schema_version"] == "2.0"
    assert package["design_space"]["research_mode_enabled"] is False
    assert package["candidate_systems"]
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    assert package["optimisation_summary"] == {"status": "not_implemented"}
    assert "source_mix_summary" in package
    assert "evidence_maturity_summary" in package
    assert "diagnostics" in package
    assert "warnings" in package


def test_package_contains_sic_sic_cmc_ebc_related_candidate():
    package = build_ceramics_first_candidate_package()
    blobs = [
        " ".join(str(candidate.get(key, "")).lower() for key in ("candidate_id", "name", "system_name"))
        + " "
        + str(candidate.get("coating_system", "")).lower()
        for candidate in package["candidate_systems"]
    ]

    assert any("sic/sic" in blob and ("ebc" in blob or "environmental barrier" in blob) for blob in blobs)


def test_package_contains_coating_enabled_system():
    package = build_ceramics_first_candidate_package()

    assert any(
        candidate.get("candidate_class") == "coating_enabled"
        or candidate.get("system_architecture_type") == "substrate_plus_coating"
        for candidate in package["candidate_systems"]
    )


def test_package_contains_spatially_graded_am_candidate_when_gradients_are_allowed():
    package = build_ceramics_first_candidate_package()

    assert package["design_space"]["architecture_flags"]["allow_spatial_gradients"] is True
    assert any(
        candidate.get("candidate_class") == "spatially_graded_am"
        or candidate.get("system_architecture_type") == "spatial_gradient"
        for candidate in package["candidate_systems"]
    )


def test_coating_enabled_and_spatially_graded_am_systems_are_distinguishable():
    package = build_ceramics_first_candidate_package()
    coating_systems = [
        candidate
        for candidate in package["candidate_systems"]
        if candidate.get("candidate_class") == "coating_enabled"
        or candidate.get("system_architecture_type") == "substrate_plus_coating"
    ]
    graded_systems = [
        candidate
        for candidate in package["candidate_systems"]
        if candidate.get("candidate_class") == "spatially_graded_am"
        or candidate.get("system_architecture_type") == "spatial_gradient"
    ]

    assert coating_systems
    assert graded_systems
    assert {candidate["candidate_class"] for candidate in coating_systems} != {
        candidate["candidate_class"] for candidate in graded_systems
    }
    assert {candidate["system_architecture_type"] for candidate in coating_systems}.isdisjoint(
        {candidate["system_architecture_type"] for candidate in graded_systems}
    )


def test_no_graded_am_candidate_has_evidence_maturity_a():
    package = build_ceramics_first_candidate_package()
    graded_systems = [
        candidate
        for candidate in package["candidate_systems"]
        if candidate.get("candidate_class") == "spatially_graded_am"
        or candidate.get("system_architecture_type") == "spatial_gradient"
    ]

    assert graded_systems
    assert all(candidate.get("evidence_maturity") != "A" for candidate in graded_systems)


def test_research_mode_false_and_diagnostics_indicate_no_live_model_calls():
    package = build_ceramics_first_candidate_package()

    assert package["design_space"]["research_mode_enabled"] is False
    assert package["diagnostics"]["research_mode_enabled"] is False
    assert package["diagnostics"]["live_model_calls_made"] is False
    assert package["diagnostics"]["materials_project_calls_made"] is False
    assert package["diagnostics"]["build31_candidate_generation_called"] is False


def test_summarize_ceramics_first_package_returns_expected_coverage_fields():
    package = build_ceramics_first_candidate_package()
    summary = summarize_ceramics_first_package(package)

    assert summary["candidate_count"] == len(package["candidate_systems"])
    assert summary["has_ni_tbc_comparison"] is True
    assert summary["has_sic_sic_cmc_ebc_anchor"] is True
    assert summary["has_monolithic_ceramic"] is True
    assert summary["has_graded_am_alternative"] is True
    assert summary["has_coating_enabled_system"] is True
    assert summary["research_mode_enabled"] is False
    assert "candidate_class_mix" in summary
    assert "system_architecture_mix" in summary
    assert "evidence_maturity_mix" in summary


def test_no_candidates_are_filtered_out_by_package_layer():
    package = build_ceramics_first_candidate_package()

    assert package["diagnostics"]["candidate_count_preserved"] is True
    assert package["diagnostics"]["total_candidate_count"] == len(package["candidate_systems"])
    assert package["source_mix_summary"]["total_candidate_count"] == len(package["candidate_systems"])
    assert package["evidence_maturity_summary"]["candidate_count"] == len(package["candidate_systems"])
