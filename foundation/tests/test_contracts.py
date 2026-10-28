import json
import math
import pytest
from pydantic import ValidationError
from material_core.contracts import *
from material_core.demo import make_fixture
from material_core.thermal import evaluate
from material_core.assumptions import AssumptionRegistry


def edit(model, **changes):
    raw=model.model_dump(mode='json');raw.update(changes)
    return type(model).model_validate_json(json.dumps(raw))

@pytest.mark.parametrize('field,value',[('value',float('nan')),('value',float('inf')),('value',True),('value','2'),('unit','mm'),('value',0),('value',-1),('unexpected',1)])
def test_reject_invalid_quantities(field,value):
    with pytest.raises(ValueError): edit(quantity('length',.01),**{field:value})


def test_dimensions_unknown_fields_and_versions():
    x=make_fixture()
    with pytest.raises(ValueError): edit(x.brief,thickness=quantity('temperature',300).model_dump(mode='json'))
    with pytest.raises(ValueError): edit(x,schema_version='2.0')
    with pytest.raises(ValueError): edit(x,unregistered_solver_argument=1)
    with pytest.raises(ValueError): quantity('length',True)
    assert Uncertainty(dimension='length',unit='m',value=0.).value==0


def test_immutable_roundtrip():
    x=make_fixture('gradient')
    copy=RunInputs.model_validate_json(x.canonical_json())
    assert copy==x and copy.content_hash==x.content_hash
    with pytest.raises(ValidationError): x.design.id='changed'
    assert isinstance(x.materials,tuple)


def test_composition_and_architecture_consistency():
    x=make_fixture('layered'); layers=x.design.architecture.layers
    with pytest.raises(ValueError): edit(layers[0].composition,fractions=[{'material_id':'scenario_A','fraction':.5}])
    with pytest.raises(ValueError): edit(layers[0].composition,fractions=[{'material_id':'scenario_A','fraction':.5},{'material_id':'scenario_A','fraction':.5}])
    with pytest.raises(ValueError): edit(layers[0],start=.6)
    raw=x.design.architecture.model_dump(mode='json');raw['layers'][1]['start']=.4
    with pytest.raises(ValueError): Layered.model_validate_json(json.dumps(raw))
    raw=make_fixture('gradient').design.architecture.model_dump(mode='json');raw['knots'][1]['position']=.0
    with pytest.raises(ValueError): Gradient.model_validate_json(json.dumps(raw))
    with pytest.raises(ValueError): edit(x,materials=[])


def test_no_fixed_constituent_layer_or_objective_counts():
    p=make_fixture().provenance[0]
    comp=Composition(basis='mass',fractions=tuple(ConstituentFraction(material_id=f'm{i}',fraction=.25) for i in range(4)))
    layers=tuple(Layer(start=i/5,end=(i+1)/5,composition=comp) for i in range(5))
    assert len(Layered(layers=layers,interface_condition='unresolved').layers)==5
    assert len(Gradient(knots=tuple(Knot(position=i/4,composition=comp) for i in range(5))).knots)==5
    # Representation support does not imply recovered solver support.
    x=make_fixture('layered')
    newlayers=tuple(Layer(start=i/4,end=(i+1)/4,composition=x.design.architecture.layers[0].composition) for i in range(4))
    d=edit(x.design,architecture=Layered(layers=newlayers,interface_condition='perfect').model_dump(mode='json'))
    x=edit(x,design=d.model_dump(mode='json'))
    assert evaluate(x).status=='unsupported'


def test_assumption_evidence_and_settings_identity():
    x=make_fixture(); assert make_fixture().content_hash==x.content_hash
    snapshots=[json.loads(s) for s in x.assumption_snapshots]
    reformatted=edit(x,assumption_snapshots=[json.dumps(s,indent=2) for s in reversed(snapshots)])
    assert reformatted.content_hash==x.content_hash
    registry=AssumptionRegistry.from_builtin()
    registry.update('A06',expected_version=1,provisional_answer='Still unresolved; changed scenario review')
    refs={r.id:r.version for r in x.brief.assumptions};refs['A06']=2
    data=x.model_dump(mode='json')
    data['assumption_snapshots']=[json.dumps(r) for r in registry.snapshot(refs)]
    for obj in ('brief','design'):
        for ref in data[obj]['assumptions']:
            if ref['id']=='A06':ref['version']=2
    assert RunInputs.model_validate_json(json.dumps(data)).content_hash!=x.content_hash
    raw=x.model_dump(mode='json');raw['settings']['mesh']['elements']=64
    assert RunInputs.model_validate_json(json.dumps(raw)).content_hash!=x.content_hash
    raw=x.model_dump(mode='json');raw['provenance'][0]['source_hash']='a'*64
    assert RunInputs.model_validate_json(json.dumps(raw)).content_hash!=x.content_hash
    raw=x.model_dump(mode='json');raw['solver']['version']='another'
    changed=RunInputs.model_validate_json(json.dumps(raw));assert changed.content_hash!=x.content_hash
    with pytest.raises(ValueError):evaluate(changed)
    with pytest.raises(ValueError):edit(x,assumption_snapshots=[])


def test_unknown_measurement_is_neither_zero_nor_estimate():
    x=make_fixture()
    p=edit(x.provenance[0],evidence_kind='measured',source_id='measurement-record')
    obs=Observation(name='porosity',value=None,uncertainty=None,missing_reason='Not measured',provenance=p)
    measured=MeasuredAchievedState(id='s1',intended_design_hash=x.design.content_hash,specimen_id='specimen1',measurement_stage='fired',observations=(obs,),failure_status='failed',provenance=p)
    assert MeasuredAchievedState.model_validate_json(measured.canonical_json()).observations[0].value is None
    with pytest.raises(ValueError): EstimatedAchievedState.model_validate_json(measured.canonical_json())
    with pytest.raises(ValueError): edit(obs,value=quantity('fraction',0).model_dump(mode='json'))
    with pytest.raises(ValueError): edit(measured,provenance=x.provenance[0].model_dump(mode='json'))
    target=edit(x,measured_state=measured.model_dump(mode='json'),evaluation_target='measured')
    assert evaluate(target).status=='unsupported'


def test_objective_eligibility_and_common_brief():
    x=make_fixture();e=evaluate(x)
    assert e.comparison_eligible(x.brief)
    newbrief=edit(x.brief,hot_boundary=quantity('temperature',500).model_dump(mode='json'))
    assert not e.comparison_eligible(newbrief)
    b=edit(x.brief,objectives=[o.model_dump(mode='json') for o in x.brief.objectives]+[Objective(id='mass',dimension='areal_mass',unit='kg/m2',direction='min',applicability='coupon').model_dump(mode='json')])
    x=edit(x,brief=b.model_dump(mode='json'));e=evaluate(x)
    assert e.status=='incomplete' and not e.comparison_eligible(b) and e.metrics[1].value is None
    with pytest.raises(ValueError): edit(e,status='complete')
    raw=e.model_dump(mode='json');raw['metrics'][0]['value']['value']=float('nan')
    with pytest.raises(ValueError):Evaluation.model_validate_json(json.dumps(raw))


def test_constraints_cannot_be_silently_satisfied():
    x=make_fixture()
    c=Constraint(id='budget',metric_id='mass',limit=quantity('areal_mass',2),relation='le',applicability='coupon')
    b=edit(x.brief,constraints=[c.model_dump(mode='json')]);x=edit(x,brief=b.model_dump(mode='json'))
    assert not evaluate(x).comparison_eligible(b)
    with pytest.raises(ValueError):edit(c,relation='approximately')

@pytest.mark.parametrize('architecture,flux',[('homogeneous',20000),('layered',100/(.005/2+.005/10)),('gradient',800/.01/math.log(5))])
def test_adapter_matches_independent_resistance(architecture,flux):
    e=evaluate(make_fixture(architecture))
    assert e.status=='complete'
    assert math.isclose(e.metrics[0].value.value,flux,rel_tol=3e-5)
    assert e.flux_spread.value<1e-5
    assert e.temperature_K[0]==400 and e.temperature_K[-1]==300
