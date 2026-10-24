"""WP3 provider: real WP2 evaluation, fixed catalogue and architecture freedom."""
import pytest
from material_core.wp2_numerical import evaluate, compatible_comparison
from material_core.wp3_provider import make_catalogue_base, propose, BoundedProvider


def test_constituent_and_architecture_variations_share_context():
    examples=[
        propose(architecture=a,pair=p,fraction=.65,elements=256)
        for a,p in (
            ("homogeneous",("scenario_A","scenario_B")),
            ("layered",("scenario_A","scenario_C")),
            ("gradient",("scenario_C","scenario_B")),
        )
    ]
    assert {x.design.architecture.kind for x in examples} == {"homogeneous","layered","gradient"}
    assert len({x.settings.property_pack_hash for x in examples})==1
    assert len({x.settings.evaluation_context_hash for x in examples})==1
    assert all(len(x.materials)==3 for x in examples)
    results=[evaluate(x) for x in examples]
    assert all(x.status=="complete" for x in results)
    assert all(x.manufacturing_feasibility=="unknown" for x in results)
    assert all(compatible_comparison(results[0],x) for x in results[1:])


def test_seed_and_supported_bounds():
    a=BoundedProvider(19)
    b=BoundedProvider(19)
    assert [a.proposal(i) for i in range(14)] == [b.proposal(i) for i in range(14)]
    assert {BoundedProvider(19).proposal(i)["architecture"] for i in range(9)} == {
        "homogeneous","layered","gradient"}
    for fraction in (-.1,1.1,True):
        with pytest.raises(ValueError):
            propose(architecture="gradient",pair=("scenario_A","scenario_B"),fraction=fraction)
    with pytest.raises(ValueError):
        propose(architecture="gradient",pair=("scenario_A","scenario_X"),fraction=.5)
    assert make_catalogue_base(elements=256).settings.property_pack_id=="wp3-neutral-A-B-C"
