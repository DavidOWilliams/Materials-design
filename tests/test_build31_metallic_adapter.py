import pandas as pd

from src.candidate_generators.build31_metallic_adapter import (
    build_material_system_candidate_from_build31_row,
    wrap_build31_dataframe,
)


def test_named_engineering_analogue_maps_to_evidence_maturity_b():
    candidate = build_material_system_candidate_from_build31_row(
        {
            "candidate_id": "ea-1",
            "candidate_source": "engineering_analogue",
            "matched_alloy_name": "IN718",
            "composition_concept": "Engineering analogue: IN718",
            "material_family": "Ni superalloy",
            "base_process_route": "wrought + heat treated",
        }
    )

    assert candidate["candidate_id"] == "ea-1"
    assert candidate["candidate_class"] == "metallic"
    assert candidate["system_architecture_type"] == "bulk_material"
    assert candidate["system_name"] == "Engineering analogue: IN718"
    assert candidate["evidence_maturity"] == "B"
    assert candidate["evidence_package"]["maturity"] == "B"
    assert candidate["source_type"] == "engineering_analogue"
    assert candidate["constituents"] == [
        {
            "role": "substrate",
            "material_family": "Ni superalloy",
            "composition": {"description": "Engineering analogue: IN718"},
        }
    ]
    assert candidate["processing_routes"][0]["route_name"] == "wrought + heat treated"
    assert candidate["generated_candidate_flag"] is False
    assert candidate["research_mode_flag"] is False


def test_materials_project_row_maps_to_evidence_maturity_e():
    candidate = build_material_system_candidate_from_build31_row(
        {
            "candidate_source": "materials_project",
            "formula_pretty": "Ni3Al",
            "chemsys": "Al-Ni",
        }
    )

    assert candidate["candidate_id"] == "build31-metallic-ni3al"
    assert candidate["system_name"] == "Ni3Al"
    assert candidate["evidence_maturity"] == "E"
    assert candidate["evidence_package"]["maturity"] == "E"
    assert "Materials Project or exploratory database source" in candidate["uncertainty_flags"][-1]
    assert candidate["certification_risk_flags"] == [
        "Evidence maturity E is below conservative certification readiness."
    ]


def test_factor_scores_are_produced_from_score_columns():
    candidate = build_material_system_candidate_from_build31_row(
        {
            "candidate_id": "score-1",
            "candidate_source": "engineering_analogue",
            "creep_score": 82,
            "toughness_score": "71.5",
            "temperature_score": 90,
            "through_life_cost_score": 65,
            "sustainability_score_v1": 44,
            "manufacturability_score": 78,
            "route_suitability_score": 83,
            "supply_risk_score": 52,
            "evidence_maturity_score": 88,
            "recipe_support_score": 73,
        }
    )

    scores = {score["factor"]: score["score"] for score in candidate["factor_scores"]}

    assert scores == {
        "creep": 82.0,
        "toughness": 71.5,
        "temperature": 90.0,
        "through_life_cost": 65.0,
        "sustainability": 44.0,
        "manufacturability": 78.0,
        "route_suitability": 83.0,
        "supply_risk": 52.0,
        "evidence_maturity": 88.0,
        "recipe_support": 73.0,
    }


def test_wrap_build31_dataframe_returns_one_candidate_per_row_without_mutating_df():
    df = pd.DataFrame(
        [
            {"candidate_id": "row-1", "candidate_source": "engineering_analogue"},
            {"candidate_id": "row-2", "candidate_source": "materials_project"},
        ]
    )
    before_columns = list(df.columns)

    candidates = wrap_build31_dataframe(df)

    assert [candidate["candidate_id"] for candidate in candidates] == ["row-1", "row-2"]
    assert len(candidates) == len(df)
    assert all(candidate["candidate_class"] == "metallic" for candidate in candidates)
    assert list(df.columns) == before_columns
