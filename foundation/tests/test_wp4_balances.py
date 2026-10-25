import pytest
from material_core.wp4_feedback import run

def test_quantisation_signed_balance_and_geometry():
    row=run(elements=256,budget=2)["records"][0]
    b=row["balances"]
    assert b["amount_unit"]=="m3/m2"
    assert sum(b["intended"].values())==pytest.approx(0.01)
    assert sum(b["estimated"].values())==pytest.approx(0.01)
    assert b["signed_estimated_minus_intended"]["scenario_A"]==pytest.approx(-b["signed_estimated_minus_intended"]["scenario_B"])
    assert b["maximum_layer_average_fraction_error"]>=0
    assert b["integrated_absolute_fraction_error_m"]>=0
