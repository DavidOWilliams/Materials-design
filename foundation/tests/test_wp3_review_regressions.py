"""WP3 boundary regressions for strict eligibility and nonempty context."""
import pytest
from material_core.wp3_pareto import Candidate, Objective, nondominated
from material_core.wp3_vertical import propose_gradient

def test_reject_string_eligibility():
    with pytest.raises(ValueError, match="strict boolean"):
        nondominated([Candidate("x", {"m": 1.}, "unknown", "same")], [Objective("m", "min")])

def test_reject_empty_context():
    with pytest.raises(ValueError, match="nonempty"):
        nondominated([Candidate("x", {"m": 1.}, True, "")], [Objective("m", "min")])

def test_invalid_mid_fraction_rejected():
    for invalid in (-.01, 1.01, True, "0.5"):
        with pytest.raises(ValueError):
            propose_gradient(mid_fraction=invalid)
