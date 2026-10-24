"""Independent WP2 correction regressions, deliberately outside original 116 tests."""
import json
import subprocess
import sys
import pytest

from material_core.contracts import (
    Constraint, Quantity, RunInputs, ConstraintMetric, quantity, Evaluation)
from material_core.wp2_numerical import (
    evaluate, compatible_comparison, context_for_run, numerical_comparison_eligible,
    property_pack_hash, exploratory_numerical_eligible)
from material_core.wp2_scenarios import make_wp2_fixture, make_wp2_achieved_fixture
from material_core.store import RunStore


def edited(x, action, *, refresh=True):
    raw=x.model_dump(mode='json')
    action(raw)
    if raw['materials']!=x.model_dump(mode='json')['materials']:
        from material_core.contracts import MaterialRecord
        raw['settings']['property_pack_hash']=property_pack_hash(tuple(
            MaterialRecord.model_validate_json(json.dumps(m)) for m in raw['materials']))
    candidate=RunInputs.model_validate_json(json.dumps(raw))
    if refresh:
        raw['settings']['evaluation_context_hash']=context_for_run(candidate)
        candidate=RunInputs.model_validate_json(json.dumps(raw))
    return candidate


def bound(label, relation, limit):
    return Constraint(id=label,metric_id='areal_mass',
        relation=relation,limit=quantity('areal_mass',limit),
        applicability='Synthetic engineering scenario').model_dump(mode='json')


def test_two_sided_and_equality_bounds_and_persistence(tmp_path):
    x=make_wp2_fixture('layered')
    x=edited(x, lambda r:r['brief'].__setitem__('constraints',[
        bound('floor','ge',29),bound('ceiling','le',31)]))
    y=evaluate(x)
    assert len(y.constraint_metrics)==1
    assert [o.constraint_id for o in y.constraint_outcomes]==['floor','ceiling']
    assert [o.outcome for o in y.constraint_outcomes]==['satisfied','satisfied']
    assert exploratory_numerical_eligible(y,x.brief)
    s=RunStore(tmp_path);rid=s.create(x);s.finish(rid,y)
    reopened=s.load(rid).evaluation
    assert reopened.constraint_outcomes==y.constraint_outcomes
    program="""import sys
from material_core.store import RunStore
s=RunStore(sys.argv[1]).load(sys.argv[2])
assert len(s.evaluation.constraint_metrics)==1
assert len(s.evaluation.constraint_outcomes)==2
print('passed')
"""
    assert 'passed' in subprocess.run([sys.executable,'-c',program,str(tmp_path),rid],
        capture_output=True,text=True,check=True).stdout
    for limits,expected in [
        ((30,30),('satisfied','satisfied')),
        ((31,31),('violated','satisfied')),
        ((29,29),('satisfied','violated')),
        ((31,29),('violated','violated'))]:
        a=edited(x,lambda r:r['brief'].__setitem__('constraints',[
            bound('floor','ge',limits[0]),bound('ceiling','le',limits[1])]))
        e=evaluate(a)
        assert tuple(o.outcome for o in e.constraint_outcomes)==expected
        assert e.feasibility==('conditional' if all(v=='satisfied' for v in expected) else 'infeasible')


def test_contradictory_bounds_are_not_silently_satisfied():
    x=make_wp2_fixture()
    z=edited(x,lambda r:r['brief'].__setitem__('constraints',[
        bound('minimum','ge',32),bound('maximum','le',28)]))
    e=evaluate(z)
    assert e.feasibility=='infeasible'
    assert all(o.outcome=='violated' for o in e.constraint_outcomes)


def test_conflicting_units_rejected_even_without_objective():
    x=make_wp2_fixture()
    def mutate(r):
        r['brief']['objectives']=[o for o in r['brief']['objectives'] if o['id']!='areal_mass']
        r['brief']['constraints']=[bound('mass','le',31),
            Constraint(id='stress',metric_id='areal_mass',relation='ge',
                limit=quantity('stress',1),applicability='bad fixture').model_dump(mode='json')]
    with pytest.raises(ValueError,match='Conflicting constraint units'):
        edited(x,mutate)


def test_context_process_assumptions_solver_and_geometry():
    a=make_wp2_fixture('homogeneous')
    b=make_wp2_fixture('layered')
    assert compatible_comparison(evaluate(a),evaluate(b))
    est=make_wp2_achieved_fixture()
    y=evaluate(est)
    assert not compatible_comparison(evaluate(a),y)
    # Re-link to the changed process without changing candidate geometry.
    from material_core.contracts import ProcessScenario
    raw=est.model_dump(mode='json')
    raw['process']['route']='another versioned deposition route'
    process=ProcessScenario.model_validate_json(json.dumps(raw['process']))
    raw['estimated_state']['process_hash']=process.content_hash
    provisional=RunInputs.model_validate_json(json.dumps(raw))
    raw['settings']['evaluation_context_hash']=context_for_run(provisional)
    altered=RunInputs.model_validate_json(json.dumps(raw))
    assert not compatible_comparison(y,evaluate(altered))
    raw=a.model_dump(mode='json')
    snapshot=json.loads(raw['assumption_snapshots'][0])
    snapshot['provisional_answer']='This changed interpretation requires a different context'
    snapshot.pop('content_hash',None)
    from material_core.assumptions import AssumptionRecord
    raw['assumption_snapshots'][0]=json.dumps(AssumptionRecord.from_dict(snapshot).to_dict())
    provisional=RunInputs.model_validate_json(json.dumps(raw))
    raw['settings']['evaluation_context_hash']=context_for_run(provisional)
    changed=RunInputs.model_validate_json(json.dumps(raw))
    assert not compatible_comparison(evaluate(a),evaluate(changed))


def test_manufacturing_unknown_retained_and_numerical_only_comparison(tmp_path):
    x=make_wp2_achieved_fixture()
    z=edited(x,lambda r:(
        r['estimated_state'].__setitem__('feasibility','unknown'),
        r['brief'].__setitem__('constraints',[])))
    y=evaluate(z)
    assert y.status=='complete'
    assert y.manufacturing_feasibility=='unknown'
    assert y.feasibility=='conditional'
    assert not y.comparison_eligible(z.brief)
    assert exploratory_numerical_eligible(y,z.brief)
    s=RunStore(tmp_path);rid=s.create(z);s.finish(rid,y)
    assert s.load(rid).evaluation.manufacturing_feasibility=='unknown'
    invalid=edited(x,lambda r:r['estimated_state'].__setitem__('feasibility','infeasible'))
    e=evaluate(invalid)
    assert e.manufacturing_feasibility=='infeasible'
    assert not e.comparison_eligible(invalid.brief)


def test_narrow_property_domain_enforced_against_broadened_settings():
    x=make_wp2_fixture()
    assert evaluate(x).status=='complete'
    def widen(r):
        r['brief']['hot_boundary']['value']=900.
        r['settings']['temperature_max']['value']=1000.
    y=edited(x,widen)
    result=evaluate(y)
    assert result.status=='unsupported'
    assert 'property evidence applicability' in ' '.join(result.limitations)
    for temperature in (290.,410.):
        z=edited(x,lambda r:r['brief']['hot_boundary'].__setitem__('value',temperature))
        assert evaluate(z).status=='complete'
    wider=make_wp2_fixture(property_domain=(280.,1000.))
    assert wider.settings.property_pack_hash!=x.settings.property_pack_hash
    permitted=edited(wider,lambda r:(
        r['brief']['hot_boundary'].__setitem__('value',900.),
        r['settings']['temperature_max'].__setitem__('value',1000.)))
    assert evaluate(permitted).status=='complete'


def test_incompatible_and_missing_property_domains_fail_closed():
    x=make_wp2_fixture()
    def remove_domain(r):
        del r['materials'][0]['properties'][0]['temperature_min']
        del r['materials'][0]['properties'][0]['temperature_max']
    missing=edited(x,remove_domain)
    assert evaluate(missing).status=='unsupported'
    assert 'Missing machine-checkable' in ' '.join(evaluate(missing).limitations)
    def shorten(r):
        r['materials'][1]['properties'][1]['temperature_max']['value']=320.
    shortened=edited(x,shorten)
    assert evaluate(shortened).status=='unsupported'
