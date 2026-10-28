"""Contract-level tests for WP3 Pareto decisions; no physics claims."""
import pytest
from material_core.wp3_pareto import Candidate, Objective, nondominated

OBJECTIVES = [Objective("heat", "min"), Objective("strength", "max")]

def c(name, heat, strength, eligible=True, context="same"):
    return Candidate(name, {"heat": heat, "strength": strength}, eligible, context)

def test_mixed_directions_and_order():
    candidates = [c("a", 2, 8), c("b", 3, 9), c("c", 4, 7)]
    assert nondominated(candidates, OBJECTIVES)["pareto_ids"] == ["a", "b"]
    assert nondominated(list(reversed(candidates)), list(reversed(OBJECTIVES)))["pareto_ids"] == ["a", "b"]

def test_ties_and_missing():
    result = nondominated([c("z", 1, 1), c("a", 1, 1), c("m", None, 5)], OBJECTIVES)
    assert result["pareto_ids"] == ["a"]
    assert "tie" in result["excluded"]["z"]
    assert "missing" in result["excluded"]["m"]

def test_unqualified_favourable_result_excluded():
    result = nondominated([c("safe", 4, 4), c("unqualified", 0, 999, False)], OBJECTIVES)
    assert result["pareto_ids"] == ["safe"]
    assert "unqualified" in result["excluded"]

def test_context_mismatch_rejected():
    with pytest.raises(ValueError, match="Incompatible"):
        nondominated([c("a", 1, 1), c("b", 2, 2, context="different")], OBJECTIVES)

def test_invalid_objectives():
    with pytest.raises(ValueError):
        Objective("heat", "lower")
    with pytest.raises(ValueError):
        nondominated([c("a", 1, 1)], [Objective("heat", "min"), Objective("heat", "max")])

def test_empty_and_no_feasible():
    assert nondominated([], OBJECTIVES)["pareto_ids"] == []
    result = nondominated([c("x", 1, 1, False)], OBJECTIVES)
    assert result["pareto_ids"] == []
