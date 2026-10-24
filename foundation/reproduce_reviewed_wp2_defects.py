"""Reproduce independent review defects on EXACT old WP2 reviewed commit.

Run with the reviewed checkout's Python environment and PYTHONPATH. This script
must not be imported as an ordinary pytest test of the corrected branch.
"""
import json
from pathlib import Path
from material_core.wp2_kernel import Cell, evaluate_cells
from material_core.wp2_scenarios import make_wp2_fixture, make_wp2_achieved_fixture
from material_core.wp2_numerical import (
    evaluate, compatible_comparison, comparison_context_hash)
from material_core.contracts import RunInputs, Constraint, ProcessScenario, quantity

def revised(raw):
    from material_core.contracts import CoupledThermomechanicalSettings, Brief
    b=Brief.model_validate_json(json.dumps(raw['brief']))
    settings=CoupledThermomechanicalSettings.model_validate_json(json.dumps(raw['settings']))
    raw['settings']['evaluation_context_hash']=comparison_context_hash(
        b,settings,raw.get('evaluation_target','intended'))
    return RunInputs.model_validate_json(json.dumps(raw))

def main():
    x=make_wp2_fixture('homogeneous',elements=128)
    stress=evaluate(x).metrics[2].value.value
    assert 1000 < stress < 10000,stress
    print('REPRO A: homogeneous 128-element spurious stress Pa:',stress)
    reviewed=Path('reviewed/foundation/tests/test_wp2_kernel.py').read_text()
    assert r'\n    # linear profile' in reviewed
    print('REPRO B: literal escaped newline comments found in refinement test')

    raw=x.model_dump(mode='json')
    raw['brief']['constraints'].append(Constraint(id='floor',metric_id='areal_mass',
        relation='ge',limit=quantity('areal_mass',29.),
        applicability='software case').model_dump(mode='json'))
    two=revised(raw)
    try:
        evaluate(two)
    except ValueError as error:
        assert 'Duplicate constraint metric IDs' in str(error),str(error)
    else:
        raise AssertionError('Original C defect absent')
    print('REPRO C: duplicate metric rejection reproduced')

    z=make_wp2_achieved_fixture();original=evaluate(z)
    r=z.model_dump(mode='json')
    r['process']['route']='different print route'
    process=ProcessScenario.model_validate_json(json.dumps(r['process']))
    r['estimated_state']['process_hash']=process.content_hash
    altered=revised(r)
    assert compatible_comparison(original,evaluate(altered))
    r=z.model_dump(mode='json')
    r['estimated_state']['feasibility']='unknown'
    r['brief']['constraints']=[]
    unknown=revised(r)
    out=evaluate(unknown)
    assert out.status=='complete' and out.feasibility=='conditional' and out.comparison_eligible(unknown.brief)
    print('REPRO D: process mismatch and unknown manufacturability admitted')

    r=x.model_dump(mode='json')
    r['brief']['hot_boundary']['value']=900.
    r['settings']['temperature_max']['value']=1000.
    widened=revised(r)
    assert evaluate(widened).status=='complete'
    print('REPRO E: settings widened original unchanged 290–410 K property evidence to 900 K')
    print('All five reviewed defects reproduced on original source')

if __name__=='__main__':main()
