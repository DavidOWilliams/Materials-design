import pytest
from material_core.wp4_registry import apply,resolve
from material_core.wp4_feedback import starting_inputs,scenario

def test_registered_transform_identity_and_lineage():
    design=starting_inputs(elements=256).design
    process=scenario()
    identity,commands,state=apply(design,process)
    assert identity["transformer"]==state.estimator_id
    assert identity["transformer_version"]==state.estimator_version
    assert commands.process_hash==process.content_hash

def test_unregistered_process_fails_closed():
    process=scenario().model_copy(update={"route":"unregistered-process"})
    with pytest.raises(ValueError,match="Unregistered"):
        resolve(process)
