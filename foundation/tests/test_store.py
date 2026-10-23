"""Behavioural checks of durable snapshots, corruption and state transitions."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest
from material_core.contracts import DecisionRecord, RunInputs
from material_core.demo import make_fixture
from material_core.store import (ArtifactIntegrityError, RunStore,
                                 StateTransitionError, UnsupportedStoreVersion)
from material_core.thermal import evaluate


def test_run_survives_independent_process_and_replays(tmp_path):
    store = RunStore(tmp_path)
    inputs = make_fixture('gradient')
    run_id = store.create(inputs)
    result = evaluate(inputs)
    store.finish(run_id,result)
    script = '''
import json, sys
from material_core.store import RunStore
from material_core.demo import verify_replay
r=RunStore(sys.argv[1]).load(sys.argv[2])
verify_replay(r.inputs,r.evaluation)
print(json.dumps({'hash':r.input_hash,'input':r.inputs.model_dump(mode='json'),'result':r.evaluation.model_dump(mode='json')}))
'''
    process = subprocess.run([sys.executable,'-c',script,str(tmp_path),run_id],
                             capture_output=True,text=True,check=True)
    reopened=json.loads(process.stdout)
    assert reopened['hash']==inputs.content_hash
    assert reopened['input']==inputs.model_dump(mode='json')
    assert reopened['result']==result.model_dump(mode='json')
    assert store.find_complete(inputs.content_hash)[0].run_id==run_id


def test_identical_inputs_share_artifact_but_not_run_identity(tmp_path):
    store=RunStore(tmp_path)
    a=make_fixture()
    first,second=store.create(a),store.create(make_fixture())
    assert first!=second
    assert len(list(store.artifacts.glob('*.json')))==1
    assert store.load(first).input_hash==store.load(second).input_hash


def test_created_failed_and_incomplete_runs_survive_restart(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    interrupted=store.create(inputs)
    failed=store.create(inputs)
    store.fail(failed,'Worker terminated before calculation')
    raw=inputs.model_dump(mode='json')
    raw['brief']['objectives'].append(dict(raw['brief']['objectives'][0], id='mass',dimension='areal_mass',unit='kg/m2'))
    more=RunInputs.model_validate_json(json.dumps(raw))
    incomplete=store.create(more)
    store.finish(incomplete,evaluate(more))
    reopened=RunStore(tmp_path)
    assert reopened.load(interrupted).status=='created'
    assert reopened.load(interrupted).evaluation is None
    assert reopened.load(failed).failure_reason=='Worker terminated before calculation'
    result=reopened.load(incomplete)
    assert result.status=='incomplete'
    assert result.evaluation.metrics[1].value is None
    assert not result.evaluation.comparison_eligible(more.brief)
    assert reopened.find_complete(more.content_hash)==()


def test_terminal_results_cannot_be_overwritten(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    run_id=store.create(inputs)
    result=evaluate(inputs)
    store.finish(run_id,result)
    with pytest.raises(StateTransitionError): store.finish(run_id,result)
    with pytest.raises(StateTransitionError): store.fail(run_id,'overwrite')
    assert store.load(run_id).evaluation==result


def test_mismatched_input_solver_and_objectives_rejected(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    run_id=store.create(inputs)
    with pytest.raises(ValueError,match='input identity'):
        store.finish(run_id,evaluate(make_fixture('gradient')))
    result=evaluate(inputs)
    changed=result.model_copy(update={'solver':result.solver.model_copy(update={'version':'other'})})
    with pytest.raises(ValueError,match='solver identity'): store.finish(run_id,changed)
    badmetric=result.metrics[0].model_copy(update={'objective_id':'other'})
    with pytest.raises(ValueError,match='unrequested'):
        store.finish(run_id,result.model_copy(update={'metrics':(badmetric,)}))
    assert store.load(run_id).status=='created'


def test_unknown_schema_and_corruption_are_explicit(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    run_id=store.create(inputs)
    path=store.artifact_path(inputs.content_hash)
    original=path.read_bytes()
    path.write_bytes(original+b' ')
    with pytest.raises(ArtifactIntegrityError,match='checksum'): store.load(run_id)
    with pytest.raises(ArtifactIntegrityError,match='corrupted'): store.create(inputs)
    path.unlink()
    with pytest.raises(ArtifactIntegrityError,match='Missing'): store.load(run_id)
    with sqlite3.connect(store.database) as db: db.execute('PRAGMA user_version=99')
    with pytest.raises(UnsupportedStoreVersion): RunStore(tmp_path)


def test_missing_result_artifact_and_metadata_inconsistency(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    run_id=store.create(inputs)
    result=evaluate(inputs)
    store.finish(run_id,result)
    store.artifact_path(result.content_hash).unlink()
    with pytest.raises(ArtifactIntegrityError,match='Missing'): store.load(run_id)
    other=store.create(inputs)
    with sqlite3.connect(store.database) as db:
        db.execute("UPDATE runs SET status='complete',finished_at='now' WHERE run_id=?",(other,))
    with pytest.raises(ArtifactIntegrityError,match='lacks result'): store.load(other)


def test_lineage_requires_parent_design_and_retains_decisions(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    first=store.create(inputs)
    changed=make_fixture('gradient')
    with pytest.raises(ValueError,match='parent design'): store.create(changed,parent_run_id=first)
    raw=changed.model_dump(mode='json')
    raw['design']['parent_hashes']=[inputs.design.content_hash]
    revision=RunInputs.model_validate_json(json.dumps(raw))
    second=store.create(revision,parent_run_id=first)
    assert store.load(second).parent_run_id==first
    assert store.load(second).inputs.design.parent_hashes==(inputs.design.content_hash,)
    decision=DecisionRecord(id='review1',compared_run_ids=(first,second),action='defer',
        rationale='Numerical examples have no measured validation',reviewer='WP1 software check',
        evidence_hashes=(inputs.content_hash,),assumption_refs=inputs.brief.assumptions,
        revisit_trigger='Complete D1 and then request scientific review')
    digest=store.save_decision(decision)
    assert RunStore(tmp_path).load_decision('review1')==decision
    assert store.save_decision(decision)==digest
    with pytest.raises(StateTransitionError):
        store.save_decision(decision.model_copy(update={'action':'retain'}))


def test_model_copy_cannot_bypass_store_validation(tmp_path):
    store=RunStore(tmp_path)
    inputs=make_fixture()
    corrupt=inputs.model_copy(update={'schema_version':'99'})
    with pytest.raises(ValueError): store.create(corrupt)
    run_id=store.create(inputs)
    result=evaluate(inputs)
    corrupt_metric=result.metrics[0].model_copy(update={'value':result.metrics[0].value.model_copy(update={'value':float('nan')})})
    with pytest.raises(ValueError): store.finish(run_id,result.model_copy(update={'metrics':(corrupt_metric,)}))
    assert store.load(run_id).status=='created'


def test_unknown_artifact_schema_not_silently_loaded(tmp_path):
    import hashlib
    store=RunStore(tmp_path)
    inputs=make_fixture()
    run_id=store.create(inputs)
    raw=inputs.model_dump(mode='json')
    raw['schema_version']='2.0'
    data=json.dumps(raw,sort_keys=True,separators=(',',':')).encode()
    digest=hashlib.sha256(data).hexdigest()
    store.artifact_path(digest).write_bytes(data)
    with sqlite3.connect(store.database) as db:
        db.execute('UPDATE runs SET input_hash=? WHERE run_id=?',(digest,run_id))
    with pytest.raises(ArtifactIntegrityError,match='unsupported artifact schema'):
        store.load(run_id)


def test_estimated_and_measured_identities_and_unknowns_survive_storage(tmp_path):
    from material_core.contracts import ProcessScenario, EstimatedAchievedState, MeasuredAchievedState, Observation
    from test_contracts import edit
    x=make_fixture()
    p=x.provenance[0]
    process=ProcessScenario(id='assumed-resolution',version=1,route='layer/feed resolution',layer_resolution=None,
        feed_fraction_resolution=None,status='unresolved',provenance=p,assumptions=x.design.assumptions,
        excluded_mechanisms=('mixing lag','shrinkage','porosity'))
    estimated=EstimatedAchievedState(id='estimate',intended_design_hash=x.design.content_hash,process_hash=process.content_hash,
        geometry=None,observations=(),estimator_id='unresolved',estimator_version='1',feasibility='unknown',
        conditions='No manufactured fields predicted',assumptions=x.design.assumptions)
    mp=edit(p,evidence_kind='published_measurement')
    measured=MeasuredAchievedState(id='measurement',intended_design_hash=x.design.content_hash,specimen_id='specimen',
        measurement_stage='fired',observations=(Observation(name='porosity',value=None,uncertainty=None,
        missing_reason='Measurement absent',provenance=mp),),failure_status='failed',provenance=mp)
    x=edit(x,process=process.model_dump(mode='json'),estimated_state=estimated.model_dump(mode='json'),measured_state=measured.model_dump(mode='json'))
    s=RunStore(tmp_path);rid=s.create(x);loaded=RunStore(tmp_path).load(rid).inputs
    assert loaded.estimated_state.kind=='estimated_achieved_state'
    assert loaded.measured_state.kind=='measured_achieved_state'
    assert loaded.estimated_state.geometry is None
    assert loaded.measured_state.observations[0].value is None
    assert loaded.measured_state.failure_status=='failed'


def test_assumption_update_invalidates_cache_and_preserves_history(tmp_path):
    from material_core.assumptions import AssumptionRegistry
    x=make_fixture();s=RunStore(tmp_path);rid=s.create(x);s.finish(rid,evaluate(x))
    reg=AssumptionRegistry.from_builtin();reg.update('A06',expected_version=1,provisional_answer='Revisit effective property evidence')
    raw=x.model_dump(mode='json')
    refs={a.id:a.version for a in x.brief.assumptions};refs['A06']=2
    raw['assumption_snapshots']=[json.dumps(a) for a in reg.snapshot(refs)]
    for key in ('brief','design'):
        for a in raw[key]['assumptions']:
            if a['id']=='A06':a['version']=2
    new=RunInputs.model_validate_json(json.dumps(raw))
    assert not s.find_complete(new.content_hash)
    assert s.load(rid).inputs.assumption_snapshots==x.assumption_snapshots
    assert s.find_complete(x.content_hash)[0].run_id==rid
