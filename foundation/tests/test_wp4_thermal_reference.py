import pytest
from material_core.wp4_feedback import starting_inputs,scenario
from material_core.wp4_bridge import evaluate_estimated
from material_core.contracts import quantity

def test_uniform_batch_conduction_independent_closed_form():
    # Intended average A=0.15, B=0.85. Feed step .25 rounds A to .25,
    # hence k_Voigt=0.25*2+0.75*10=8 W/(m K).
    # Through-thickness resistance R=t/k=0.01/8=0.00125 m2 K/W.
    # 400 K to 300 K yields 80,000 W/m2.
    base=starting_inputs(elements=256)
    process=scenario(layer=.01,feed=.25).model_copy(
        update={"route":"synthetic_ideal_uniform_batch_deposition"})
    inputs,result=evaluate_estimated(base,process)
    metrics={m.objective_id:m.value.value for m in result.metrics if m.value is not None}
    assert metrics["thermal_transmission"]==pytest.approx(80000.,rel=1e-5)
    assert metrics["areal_mass"]==pytest.approx(.01*(.25*2000+.75*4000),rel=1e-8)
