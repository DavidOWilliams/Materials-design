"""Produce machine-readable WP2 three-objective and separate-process replay evidence."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def call(*args):
    environment=dict(os.environ)
    environment['PYTHONPATH']=str(Path(__file__).resolve().parent)+(
        os.pathsep+environment.get('PYTHONPATH','') if environment.get('PYTHONPATH') else '')
    run=subprocess.run([sys.executable,'-m','material_core.wp2_demo',*args],
        capture_output=True,text=True,check=True,env=environment)
    return json.loads(run.stdout)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    results={}
    replay={}
    for architecture in ('homogeneous','layered','gradient','estimated-achieved-gradient',
                         'qualified-homogeneous','qualified-layered','qualified-gradient',
                         'qualified-estimated-achieved-gradient'):
        store=args.output/'store'/architecture
        runargs=['--store',str(store)]
        label=architecture.removeprefix('qualified-')
        if architecture.startswith('qualified-'):
            runargs+=['--elements','4096']
        if label=='estimated-achieved-gradient':
            runargs+=['--architecture','gradient','--achieved']
        else:
            runargs+=['--architecture',label]
        created=call(*runargs)
        checked=call('--store',str(store),'--replay',created['run_id'])
        if checked['replay']!='passed':
            raise AssertionError('Replay did not verify '+architecture)
        if checked['objectives']!=created['objectives']:
            raise AssertionError('Stored objectives differ from original run')
        results[architecture]=created
        replay[architecture]={
            'run_id':created['run_id'],
            'input_hash':created['input_hash'],
            'status':'passed',
            'flux_W_m2':created['objectives']['thermal_transmission']['value'],
        }
    for arch in ('homogeneous','layered','gradient','qualified-homogeneous',
                 'qualified-layered','qualified-gradient'):
        values=results[arch]['objectives']
        if set(values)!={'thermal_transmission','areal_mass','tensile_thermal_mismatch'}:
            raise AssertionError('Objective vector incomplete')
        if abs(values['areal_mass']['value']-30)>1e-7:
            raise AssertionError('Intended architecture has unequal material budget')
    for name,payload in [('wp2-numerical-results.json',results),
                         ('wp2-separate-process-replay.json',replay)]:
        (args.output/name).write_text(json.dumps(payload,indent=2,sort_keys=True)+'
')
    for arch in ('qualified-homogeneous','qualified-layered','qualified-gradient',
                 'qualified-estimated-achieved-gradient'):
        if results[arch]['numerical_quality']!='qualified':
            raise AssertionError('Refined three-objective example is not numerically qualified: '+arch)
    print(json.dumps({'status':'passed','runs':len(results),
        'scenario_numerical_quality':{k:r['numerical_quality'] for k,r in results.items()},
        'scenario_manufacturing_feasibility':{k:r['manufacturing_feasibility'] for k,r in results.items()},
        'objective_names':list(results['gradient']['objectives']),
        'scenario_curvature_per_m':{k:r['curvature_per_m'] for k,r in results.items()},
        'scenario_results':{k:{m:round(v['value'],8) for m,v in r['objectives'].items()}
             for k,r in results.items()},
        'achieved_mass_budget_feasibility':'violated' if
         results['estimated-achieved-gradient']['objectives']['areal_mass']['value']>31.
         else 'satisfied'}))


if __name__=='__main__': main()
