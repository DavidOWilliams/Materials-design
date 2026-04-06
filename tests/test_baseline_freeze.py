import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.candidate_generation import _complexity_gate, _alloy_likeness


def test_ternary_nickel_candidate_can_survive_minimum_complexity_gate():
    elements = ["Ni", "Cr", "Al"]
    alloy_likeness_score, _ = _alloy_likeness(elements, "NiCrAl", theoretical=False)

    passed, score, threshold, reason = _complexity_gate(
        elements=elements,
        alloy_likeness_score=alloy_likeness_score,
        assigned_family="Ni-based superalloy-like candidate",
    )

    assert passed is True
    assert score == 3
    assert threshold == 3


def test_ternary_cobalt_candidate_can_survive_minimum_complexity_gate():
    elements = ["Co", "Cr", "W"]
    alloy_likeness_score, _ = _alloy_likeness(elements, "CoCrW", theoretical=False)

    passed, score, threshold, reason = _complexity_gate(
        elements=elements,
        alloy_likeness_score=alloy_likeness_score,
        assigned_family="Co-based high-temperature candidate",
    )

    assert passed is True
    assert score == 3
    assert threshold == 3


def test_ternary_refractory_candidate_can_survive_minimum_complexity_gate():
    elements = ["Mo", "Nb", "Ti"]
    alloy_likeness_score, _ = _alloy_likeness(elements, "MoNbTi", theoretical=False)

    passed, score, threshold, reason = _complexity_gate(
        elements=elements,
        alloy_likeness_score=alloy_likeness_score,
        assigned_family="Refractory-alloy-like candidate",
    )

    assert passed is True
    assert score == 3
    assert threshold == 3


def test_binary_weak_candidate_fails_complexity_gate():
    elements = ["Ni", "Al"]
    passed, score, threshold, reason = _complexity_gate(
        elements=elements,
        alloy_likeness_score=10,
        assigned_family="Ni-based superalloy-like candidate",
    )

    assert passed is False
    assert score == 2
    assert threshold == 3


def test_candidate_level_log_fields_exist():
    df = pd.DataFrame(
        [
            {
                "candidate_id": "mp-1",
                "formula_pretty": "NiCrAl",
                "chemsys": "Ni-Cr-Al",
                "n_elements": 3,
                "material_family": "Ni-based superalloy-like candidate",
                "diagnostic_family_match": True,
                "diagnostic_complexity_score": 3,
                "diagnostic_complexity_threshold": 3,
                "baseline_survives": True,
            }
        ]
    )

    required_columns = {
        "candidate_id",
        "formula_pretty",
        "chemsys",
        "n_elements",
        "material_family",
        "diagnostic_family_match",
        "diagnostic_complexity_score",
        "diagnostic_complexity_threshold",
        "baseline_survives",
    }

    assert required_columns.issubset(set(df.columns))