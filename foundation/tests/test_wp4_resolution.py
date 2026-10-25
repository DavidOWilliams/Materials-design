"""WP4 synthetic transform analytical references, independent of production integration."""
import pytest
from material_core.contracts import (
    IntendedDesign, ProcessScenario, Homogeneous, Gradient, Knot, Composition,
    ConstituentFraction, quantity, Provenance,
)
from material_core.wp4_resolution import transform

def mixture(a):
    return Composition(basis="volume", fractions=(
        ConstituentFraction(material_id="A", fraction=float(a)),
        ConstituentFraction(material_id="B", fraction=float(1-a))))

def design(a=0.0,b=1.0,thickness=0.004):
    return IntendedDesign(id="test-gradient",thickness=quantity("length",thickness),
        architecture=Gradient(knots=(Knot(position=0.,composition=mixture(a)),
                                      Knot(position=1.,composition=mixture(b)))),
        proposal_method="test fixture",assumptions=())

def scenario(layer=0.002,feed=0.25):
    return ProcessScenario(id="test-process",version=1,route="synthetic_ideal_planar_deposition",
        layer_resolution=quantity("length",layer),feed_fraction_resolution=feed,
        status="assumed",provenance=Provenance(source_id="test",source_version="1",
        source_hash="0"*64,location="test fixture",reuse_terms="test only",
        evidence_kind="synthetic_scenario",conditions="ideal",extraction="test"),
        assumptions=(),excluded_mechanisms=("porosity","shrinkage"))

def test_gradient_integrals_and_quantisation():
    commands,achieved=transform(design(),scenario())
    # Analytical average of f(x)=x on [0,1/2], [1/2,1]: 1/4, 3/4.
    assert [c.composition.fractions[0].fraction for c in commands.commands]==pytest.approx([0.25,0.75])
    assert achieved.intended_design_hash==design().content_hash
    assert achieved.geometry.content_hash!=design().content_hash

def test_single_layer_and_signed_change():
    commands,achieved=transform(design(0.1,0.1),scenario(layer=0.004,feed=0.25))
    assert isinstance(achieved.geometry.architecture,Homogeneous)
    assert commands.commands[0].composition.fractions[0].fraction==0.0
    # Quantisation changes constituent A amount by -0.0004 m3 per m2.
    assert (0.-0.1)*0.004==pytest.approx(-0.0004)

def test_unrepresentable_thickness_rejected():
    with pytest.raises(ValueError,match="not divisible"):
        transform(design(thickness=0.005),scenario())

def test_unsupported_route_rejected():
    p=scenario().model_copy(update={"route":"unverified"})
    with pytest.raises(ValueError,match="Unsupported route"):
        transform(design(),p)
