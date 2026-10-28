import pytest
from material_core.wp4_feedback import starting_inputs,scenario
from material_core.wp4_registry import apply
from material_core.wp4_bridge import evaluate_estimated
from material_core.wp4_balances import balances
from material_core.contracts import Homogeneous,quantity

def test_second_capability_is_genuinely_distinct():
    base=starting_inputs(elements=256)
    original=scenario(layer=.005,feed=.25)
    uniform=original.model_copy(update={
        "id":"wp4-uniform-batch-test",
        "route":"synthetic_ideal_uniform_batch_deposition",
        "layer_resolution":quantity("length",.01)})
    identity,commands,state=apply(base.design,uniform)
    assert identity["transformer"]=="wp4-ideal-uniform-batch"
    assert len(commands.commands)==1
    assert isinstance(state.geometry.architecture,Homogeneous)
    estimated,result=evaluate_estimated(base,uniform)
    assert estimated.evaluation_target=="estimated"
    assert result.input_hash==estimated.content_hash
    assert balances(base.design,commands,state)["amount_unit"]=="m3/m2"
    _,other_commands,_=apply(base.design,original)
    assert len(other_commands.commands)==2

def test_uniform_batch_rejects_fake_multiple_layers():
    base=starting_inputs(elements=256)
    process=scenario().model_copy(update={"route":"synthetic_ideal_uniform_batch_deposition"})
    with pytest.raises(ValueError,match="single full-thickness"):
        apply(base.design,process)
