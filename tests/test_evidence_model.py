from src.evidence_model import (
    evaluate_candidate_evidence,
    evaluate_candidates_evidence,
    maturity_from_source,
    summarize_evidence_maturity,
)


def test_existing_valid_maturity_is_preserved():
    candidate = evaluate_candidate_evidence(
        {
            "candidate_id": "qualified-1",
            "candidate_class": "metallic",
            "system_name": "Qualified alloy",
            "source_type": "materials_project",
            "evidence_package": {
                "maturity": "B",
                "source_reference": "existing reference",
                "known_strengths": "known use",
            },
        }
    )

    assert candidate["evidence_maturity"] == "B"
    assert candidate["evidence_package"]["maturity"] == "B"
    assert candidate["evidence_package"]["source_reference"] == "existing reference"
    assert candidate["evidence_package"]["known_strengths"] == "known use"


def test_invalid_or_missing_maturity_is_assigned_conservatively():
    invalid = evaluate_candidate_evidence(
        {
            "candidate_class": "metallic",
            "system_name": "Invalid evidence row",
            "source_type": "unknown",
            "evidence_package": {"maturity": "Z"},
        }
    )
    missing = evaluate_candidate_evidence(
        {
            "candidate_class": "metallic",
            "system_name": "Missing evidence row",
        }
    )

    assert invalid["evidence_maturity"] == "E"
    assert missing["evidence_maturity"] == "E"
    assert invalid["evidence_package"]["confidence"] == 0.32


def test_engineering_analogue_with_named_analogue_maps_to_b():
    candidate = {
        "candidate_class": "metallic",
        "system_name": "IN718 analogue",
        "source_type": "engineering_analogue",
        "matched_alloy_name": "IN718",
    }

    evaluated = evaluate_candidate_evidence(candidate)

    assert maturity_from_source(candidate) == "B"
    assert evaluated["evidence_maturity"] == "B"
    assert evaluated["evidence_package"]["maturity_label"] == "Mature aerospace analogue"


def test_curated_engineering_reference_maps_to_c():
    candidate = evaluate_candidate_evidence(
        {
            "candidate_class": "monolithic_ceramic",
            "system_name": "Curated SiC",
            "source_type": "curated_engineering_reference",
        }
    )

    assert candidate["evidence_maturity"] == "C"
    assert candidate["evidence_package"]["confidence"] == 0.62


def test_materials_project_and_database_map_to_e():
    mp_candidate = evaluate_candidate_evidence(
        {
            "candidate_class": "metallic",
            "system_name": "Ni3Al",
            "source_type": "materials_project",
        }
    )
    database_candidate = evaluate_candidate_evidence(
        {
            "candidate_class": "metallic",
            "system_name": "Database row",
            "source_type": "database_exploratory",
        }
    )

    assert mp_candidate["evidence_maturity"] == "E"
    assert database_candidate["evidence_maturity"] == "E"


def test_generated_and_research_map_to_f_and_flags_are_retained():
    generated = evaluate_candidate_evidence(
        {
            "candidate_class": "research_generated",
            "system_name": "Generated concept",
            "source_type": "research_model_generated",
            "generated_candidate_flag": True,
        }
    )
    research = evaluate_candidate_evidence(
        {
            "candidate_class": "research_generated",
            "system_name": "Research concept",
            "research_mode_flag": True,
        }
    )

    assert generated["evidence_maturity"] == "F"
    assert generated["generated_candidate_flag"] is True
    assert research["evidence_maturity"] == "F"
    assert research["research_mode_flag"] is True


def test_graded_am_templates_are_not_upgraded_above_d_unless_explicit():
    inferred = evaluate_candidate_evidence(
        {
            "candidate_class": "spatially_graded_am",
            "system_name": "Curated graded template",
            "source_type": "curated_engineering_reference",
        }
    )
    explicit = evaluate_candidate_evidence(
        {
            "candidate_class": "spatially_graded_am",
            "system_name": "Explicit mature gradient",
            "source_type": "curated_engineering_reference",
            "evidence_package": {"maturity": "C"},
        }
    )

    assert inferred["evidence_maturity"] == "D"
    assert explicit["evidence_maturity"] == "C"


def test_low_maturity_candidates_receive_certification_risk_flags():
    for maturity in ("D", "E", "F"):
        candidate = evaluate_candidate_evidence(
            {
                "candidate_class": "metallic",
                "system_name": f"Candidate {maturity}",
                "evidence_package": {"maturity": maturity},
            }
        )

        assert any("not qualification-ready" in flag for flag in candidate["certification_risk_flags"])


def test_e_and_f_candidates_receive_uncertainty_flags():
    exploratory = evaluate_candidate_evidence(
        {
            "candidate_class": "metallic",
            "system_name": "MP row",
            "source_type": "materials_project",
        }
    )
    generated = evaluate_candidate_evidence(
        {
            "candidate_class": "research_generated",
            "system_name": "Generated row",
            "generated_candidate_flag": True,
        }
    )

    assert any("exploratory evidence" in flag for flag in exploratory["uncertainty_flags"])
    assert any("unvalidated research" in flag for flag in generated["uncertainty_flags"])


def test_summarize_evidence_maturity_counts_a_to_f_and_generated_research_flags():
    summary = summarize_evidence_maturity(
        [
            {"candidate_class": "metallic", "system_name": "A", "evidence_package": {"maturity": "A"}},
            {"candidate_class": "metallic", "system_name": "B", "evidence_package": {"maturity": "B"}},
            {"candidate_class": "metallic", "system_name": "C", "source_type": "curated_engineering_reference"},
            {"candidate_class": "metallic", "system_name": "D", "source_type": "literature_reference"},
            {"candidate_class": "metallic", "system_name": "E", "source_type": "materials_project"},
            {
                "candidate_class": "research_generated",
                "system_name": "F",
                "source_type": "research_model_generated",
                "generated_candidate_flag": True,
                "research_mode_flag": True,
            },
        ]
    )

    assert summary["maturity_counts"] == {
        "A": 1,
        "B": 1,
        "C": 1,
        "D": 1,
        "E": 1,
        "F": 1,
    }
    assert summary["generated_candidate_count"] == 1
    assert summary["research_mode_candidate_count"] == 1


def test_evaluate_candidates_evidence_preserves_count_and_does_not_filter():
    candidates = [
        {"candidate_class": "metallic", "system_name": "One", "source_type": "materials_project"},
        {"candidate_class": "unknown", "system_name": "Two"},
        {"system_name": "Three", "generated_candidate_flag": True},
    ]

    evaluated = evaluate_candidates_evidence(candidates)

    assert len(evaluated) == len(candidates)
    assert [candidate["system_name"] for candidate in evaluated] == ["One", "Two", "Three"]
