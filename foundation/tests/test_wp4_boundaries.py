import pytest
from material_core.wp4_feedback import run,starting_inputs,scenario
from material_core.wp4_registry import apply
from material_core.contracts import Homogeneous,IntendedDesign,Composition,ConstituentFraction

def test_zero_budget_rejected_without_relaxation():
    with pytest.raises(ValueError,match="Positive evaluation budget"):
        run(elements=256,budget=0)

def test_feed_endpoints_are_exact():
    base=starting_inputs(elements=256)
    for a in (0.,1.):
        comp=Composition(basis="volume",fractions=(
            ConstituentFraction(material_id="scenario_A",fraction=a),
            ConstituentFraction(material_id="scenario_B",fraction=1-a)))
        design=IntendedDesign(id="endpoint",thickness=base.design.thickness,
            architecture=Homogeneous(composition=comp),
            proposal_method="endpoint test",assumptions=base.design.assumptions)
        _,commands,_=apply(design,scenario(layer=.005,feed=.25))
        assert all(cmd.composition.fractions[0].fraction==a for cmd in commands.commands)

def test_invalid_feed_grid_fails_closed():
    with pytest.raises(ValueError,match="Feed step"):
        apply(starting_inputs(elements=256).design,scenario(feed=.3))
