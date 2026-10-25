from material_core.wp4_feedback import starting_inputs,scenario
from material_core.wp4_registry import apply

def test_machine_resolution_independent_of_numerical_mesh():
    coarse=starting_inputs(elements=256)
    fine=starting_inputs(elements=4096)
    process=scenario(layer=.005,feed=.25)
    _,commands_coarse,state_coarse=apply(coarse.design,process)
    _,commands_fine,state_fine=apply(fine.design,process)
    assert coarse.design.content_hash==fine.design.content_hash
    assert commands_coarse.content_hash==commands_fine.content_hash
    assert state_coarse.geometry.content_hash==state_fine.geometry.content_hash
