"""Independent, small analytical reference cases for the ideal WP4 transform."""
import pytest
from material_core.contracts import (IntendedDesign,Composition,ConstituentFraction,
    Homogeneous,Layered,Layer,Gradient,Knot,quantity)
from material_core.wp4_feedback import scenario
from material_core.wp4_registry import apply
from material_core.wp4_balances import balances

def comp(a):
    return Composition(basis="volume",fractions=(
        ConstituentFraction(material_id="scenario_A",fraction=a),
        ConstituentFraction(material_id="scenario_B",fraction=1-a)))

def design(arch):
    return IntendedDesign(id="reference",thickness=quantity("length",.01),
        architecture=arch,proposal_method="independent hand reference",assumptions=())

@pytest.mark.parametrize("architecture,expected",[
    (Homogeneous(composition=comp(.5)),[.5,.5]),
    (Layered(layers=(Layer(start=0,end=.5,composition=comp(1.)),
                     Layer(start=.5,end=1,composition=comp(0.))),interface_condition="perfect"),[1.,0.]),
    (Gradient(knots=(Knot(position=0,composition=comp(1.)),
                     Knot(position=1,composition=comp(0.)))),[.75,.25]),
])
def test_analytical_reference(architecture,expected):
    d=design(architecture)
    _,cmd,state=apply(d,scenario(layer=.005,feed=.25))
    assert [c.composition.fractions[0].fraction for c in cmd.commands]==pytest.approx(expected)
    b=balances(d,cmd,state)
    assert sum(b["intended"].values())==pytest.approx(.01)
    assert sum(b["estimated"].values())==pytest.approx(.01)
    assert all(abs(v)<1e-10 for v in b["signed_estimated_minus_intended"].values())

def test_tie_goes_to_lower_first_constituent():
    d=design(Homogeneous(composition=comp(.375)))
    _,cmd,_=apply(d,scenario(layer=.005,feed=.25))
    assert cmd.commands[0].composition.fractions[0].fraction==.25

def test_layer_discontinuity_inside_machine_layer_is_integrated():
    d=design(Layered(layers=(Layer(start=0,end=.25,composition=comp(1.)),
                 Layer(start=.25,end=1,composition=comp(0.))),interface_condition="perfect"))
    _,cmd,_=apply(d,scenario(layer=.005,feed=.25))
    assert [c.composition.fractions[0].fraction for c in cmd.commands]==[.5,0.]
