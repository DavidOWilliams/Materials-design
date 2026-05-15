from src.factor_models.dispatcher import (
    evaluate_candidate_system_factors,
    evaluate_candidate_systems_factors,
    summarize_factor_outputs,
)


def _factor_names(candidate):
    return {score["factor"] for score in candidate["factor_scores"]}


def _warnings(candidate):
    return " ".join(candidate.get("factor_model_warnings", [])).lower()


def test_dispatcher_preserves_input_length_and_order():
    candidates = [
        {"candidate_id": "metal-1", "candidate_class": "metallic", "name": "Ni superalloy", "evidence_maturity": "B"},
        {"candidate_id": "ceramic-1", "candidate_class": "monolithic_ceramic", "name": "SiC", "evidence_maturity": "C"},
        {"candidate_id": "unknown-1", "candidate_class": "unobtanium", "name": "Unknown", "evidence_maturity": "E"},
    ]

    evaluated = evaluate_candidate_systems_factors(candidates)

    assert len(evaluated) == len(candidates)
    assert [candidate["candidate_id"] for candidate in evaluated] == ["metal-1", "ceramic-1", "unknown-1"]


def test_metal_candidate_receives_metal_factors():
    candidate = evaluate_candidate_system_factors(
        {
            "candidate_id": "metal-1",
            "candidate_class": "metallic",
            "name": "Ni superalloy + bond coat + TBC",
            "source_type": "engineering_analogue",
            "matched_alloy_name": "CMSX class superalloy",
            "evidence_maturity": "B",
        }
    )

    factors = _factor_names(candidate)

    assert "metal.temperature_capability" in factors
    assert "metal.creep_and_fatigue_basis" in factors
    assert all(score["candidate_class"] == "metallic" for score in candidate["factor_scores"])
    assert "build 3.1 metallic factors remain separate" in _warnings(candidate)


def test_monolithic_ceramic_receives_ceramic_factors_and_brittleness_warning():
    candidate = evaluate_candidate_system_factors(
        {
            "candidate_id": "ceramic-1",
            "candidate_class": "monolithic_ceramic",
            "name": "Monolithic silicon carbide",
            "risks": ["brittle fracture risk", "flaw sensitivity"],
            "source_type": "curated_engineering_reference",
            "evidence_maturity": "C",
        }
    )

    factors = _factor_names(candidate)

    assert "ceramic.temperature_capability" in factors
    assert "ceramic.brittleness_fracture_risk" in factors
    assert "brittle fracture" in _warnings(candidate)


def test_sic_sic_cmc_ebc_receives_cmc_factors_and_ebc_dependency_factor():
    candidate = evaluate_candidate_system_factors(
        {
            "candidate_id": "cmc-1",
            "candidate_class": "ceramic_matrix_composite",
            "name": "SiC/SiC CMC with EBC",
            "constituents": [
                {"name": "SiC matrix", "role": "matrix"},
                {"name": "SiC fiber", "role": "fiber"},
                {"name": "BN interphase", "role": "interphase"},
            ],
            "environmental_barrier_coating": {"name": "rare-earth silicate EBC"},
            "source_type": "curated_engineering_reference",
            "evidence_maturity": "B",
        }
    )

    factors = _factor_names(candidate)

    assert "cmc.temperature_capability" in factors
    assert "cmc.ebc_dependency" in factors
    assert "ebc" in _warnings(candidate)


def test_coating_enabled_candidate_receives_coating_factors_and_spallation_warning():
    candidate = evaluate_candidate_system_factors(
        {
            "candidate_id": "coating-1",
            "candidate_class": "coating_enabled",
            "name": "Ni superalloy with TBC",
            "coating_or_surface_system": {
                "coating_type": "thermal barrier coating",
                "failure_modes": ["spallation", "CTE mismatch"],
            },
            "source_type": "curated_engineering_reference",
            "evidence_maturity": "B",
        }
    )

    factors = _factor_names(candidate)

    assert "coating.substrate_compatibility" in factors
    assert "coating.cte_mismatch_spallation_risk" in factors
    assert "spallation" in _warnings(candidate)
    assert "cte mismatch" in _warnings(candidate)


def test_spatially_graded_am_receives_factors_and_exploratory_maturity_warning():
    candidate = evaluate_candidate_system_factors(
        {
            "candidate_id": "graded-1",
            "candidate_class": "spatially_graded_am",
            "name": "Exploratory thermal-barrier gradient",
            "gradient_architecture": {
                "gradient_types": ["composition"],
                "notes": "surface to core transition with inspection gaps",
            },
            "source_type": "curated_graded_template",
            "evidence_maturity": "E",
        }
    )

    factors = _factor_names(candidate)

    assert "graded_am.gradient_functional_benefit" in factors
    assert "graded_am.transition_zone_risk" in factors
    assert "exploratory" in _warnings(candidate)
    assert candidate["evidence_maturity"] in {"D", "E", "F"}


def test_unknown_candidate_class_returns_generic_warning_factor_not_exception():
    candidate = evaluate_candidate_system_factors(
        {
            "candidate_id": "unknown-1",
            "candidate_class": "unknown_new_class",
            "name": "Unclassified concept",
            "evidence_maturity": "E",
        }
    )

    factors = _factor_names(candidate)

    assert "generic.unclassified_candidate_warning" in factors
    assert "unknown candidate class" in _warnings(candidate)


def test_summarize_factor_outputs_counts_candidate_class_and_factor_namespace():
    candidates = evaluate_candidate_systems_factors(
        [
            {"candidate_id": "metal-1", "candidate_class": "metallic", "name": "Ni superalloy", "evidence_maturity": "B"},
            {"candidate_id": "ceramic-1", "candidate_class": "monolithic_ceramic", "name": "SiC brittle", "evidence_maturity": "C"},
            {"candidate_id": "graded-1", "candidate_class": "spatially_graded_am", "gradient_architecture": {"notes": "transition"}, "evidence_maturity": "F"},
        ]
    )

    summary = summarize_factor_outputs(candidates)

    assert summary["candidate_count"] == 3
    assert summary["candidate_class_counts"]["metallic"] == 1
    assert summary["candidate_class_counts"]["monolithic_ceramic"] == 1
    assert summary["factor_namespace_counts"]["metal"] == 5
    assert summary["factor_namespace_counts"]["ceramic"] == 5
    assert summary["factor_namespace_counts"]["graded_am"] == 6
    assert summary["candidates_with_factor_scores"] == 3


def test_no_candidates_are_filtered_out():
    candidates = [
        {"candidate_id": "metal-1", "candidate_class": "metallic", "evidence_maturity": "B"},
        {"candidate_id": "cmc-1", "candidate_class": "ceramic_matrix_composite", "evidence_maturity": "C"},
        {"candidate_id": "unknown-1", "candidate_class": "unknown_new_class", "evidence_maturity": "F"},
    ]

    evaluated = evaluate_candidate_systems_factors(candidates)

    assert len(evaluated) == 3
    assert [candidate["candidate_id"] for candidate in evaluated] == [
        "metal-1",
        "cmc-1",
        "unknown-1",
    ]
    assert all(candidate["factor_scores"] for candidate in evaluated)
