from src.candidate_normalizer import (
    normalize_system_candidate,
    normalize_system_candidates,
    summarize_normalization,
    validate_normalized_candidate,
)


def test_missing_optional_list_fields_are_normalized_to_lists():
    candidate = normalize_system_candidate(
        {
            "candidate_id": "ceramic-1",
            "candidate_class": "monolithic_ceramic",
            "system_name": "Silicon nitride",
            "source_type": "curated_reference",
        }
    )

    assert candidate["constituents"] == []
    assert candidate["interfaces"] == []
    assert candidate["uncertainty_flags"] == []
    assert isinstance(candidate["certification_risk_flags"], list)
    assert candidate["optimisation_history"] == []
    assert candidate["factor_scores"] == []
    assert validate_normalized_candidate(candidate) == []


def test_missing_evidence_package_is_added_with_conservative_maturity():
    candidate = normalize_system_candidate(
        {
            "candidate_id": "unknown-1",
            "candidate_class": "metallic",
            "system_name": "Unknown metal",
        }
    )

    assert candidate["evidence_package"]["maturity"] == "E"
    assert candidate["evidence_maturity"] == "E"
    assert candidate["system_architecture_type"] == "bulk_material"


def test_generated_and_research_candidates_default_to_maturity_f():
    generated = normalize_system_candidate(
        {
            "candidate_class": "research_generated",
            "system_name": "Generated concept",
            "generated_candidate_flag": True,
        }
    )
    research = normalize_system_candidate(
        {
            "candidate_class": "research_generated",
            "system_name": "Research concept",
            "research_mode_flag": True,
        }
    )

    assert generated["evidence_maturity"] == "F"
    assert research["evidence_maturity"] == "F"


def test_materials_project_and_database_candidates_default_to_e():
    materials_project = normalize_system_candidate(
        {
            "candidate_class": "metallic",
            "system_name": "Ni3Al",
            "source_type": "materials_project",
        }
    )
    database = normalize_system_candidate(
        {
            "candidate_class": "metallic",
            "system_name": "Exploratory row",
            "source_type": "database_exploratory",
        }
    )

    assert materials_project["evidence_maturity"] == "E"
    assert database["evidence_maturity"] == "E"


def test_curated_and_engineering_analogue_candidates_default_to_c():
    curated = normalize_system_candidate(
        {
            "candidate_class": "monolithic_ceramic",
            "system_name": "Curated SiC",
            "source_type": "curated_reference",
        }
    )
    analogue = normalize_system_candidate(
        {
            "candidate_class": "metallic",
            "system_name": "IN718 analogue",
            "source_type": "engineering_analogue",
        }
    )

    assert curated["evidence_maturity"] == "C"
    assert analogue["evidence_maturity"] == "C"


def test_low_maturity_candidates_get_certification_risk_flags():
    candidate = normalize_system_candidate(
        {
            "candidate_id": "low-1",
            "candidate_class": "spatially_graded_am",
            "system_name": "Gradient template",
            "evidence_package": {"maturity": "D"},
        }
    )

    assert candidate["evidence_maturity"] == "D"
    assert any("not qualification-ready" in flag for flag in candidate["certification_risk_flags"])


def test_spatially_graded_am_without_gradient_architecture_gets_uncertainty_flag():
    candidate = normalize_system_candidate(
        {
            "candidate_id": "graded-1",
            "candidate_class": "spatially_graded_am",
            "system_name": "Gradient template",
            "source_type": "curated_reference",
        }
    )

    assert any("missing gradient_architecture" in flag for flag in candidate["uncertainty_flags"])


def test_coating_bulk_architecture_validation_warning_is_preserved():
    candidate = normalize_system_candidate(
        {
            "candidate_id": "coating-1",
            "candidate_class": "coating_enabled",
            "system_name": "Coated substrate",
            "system_architecture_type": "bulk_material",
            "coating_or_surface_system": {"coating_type": "TBC"},
            "source_type": "curated_reference",
        }
    )

    assert candidate["system_architecture_type"] == "bulk_material"
    assert any(
        "bulk_material while coating_or_surface_system is present" in warning
        for warning in candidate["normalization_warnings"]
    )


def test_normalize_system_candidates_preserves_length_and_does_not_filter():
    candidates = [
        {"candidate_class": "metallic", "system_name": "A", "source_type": "unknown"},
        {"candidate_class": "unknown", "system_name": "B", "source_type": "unknown"},
        {"system_name": "C"},
    ]

    normalized = normalize_system_candidates(candidates)

    assert len(normalized) == len(candidates)
    assert [candidate["system_name"] for candidate in normalized] == ["A", "B", "C"]


def test_summarize_normalization_counts_class_source_and_maturity():
    summary = summarize_normalization(
        [
            {
                "candidate_class": "metallic",
                "system_name": "MP row",
                "source_type": "materials_project",
            },
            {
                "candidate_class": "monolithic_ceramic",
                "system_name": "Curated ceramic",
                "source_type": "curated_reference",
            },
            {
                "candidate_class": "research_generated",
                "system_name": "Generated",
                "source_type": "research_model_generated",
                "generated_candidate_flag": True,
            },
        ]
    )

    assert summary["total_candidate_count"] == 3
    assert summary["candidate_class_counts"] == {
        "metallic": 1,
        "monolithic_ceramic": 1,
        "research_generated": 1,
    }
    assert summary["source_type_counts"] == {
        "curated_reference": 1,
        "materials_project": 1,
        "research_model_generated": 1,
    }
    assert summary["evidence_maturity_counts"] == {"C": 1, "E": 1, "F": 1}
