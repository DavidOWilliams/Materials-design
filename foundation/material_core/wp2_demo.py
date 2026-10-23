"""Run and separately replay the three-objective WP2 synthetic coupon example.

From repository root:
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp2_demo \
  --store /tmp/materials-wp2 --architecture layered

The purpose is numerical verification, not certified ceramic performance.
"""
import argparse
import json
from pathlib import Path

from .store import RunStore
from .wp2_numerical import evaluate
from .wp2_scenarios import make_wp2_fixture, make_wp2_achieved_fixture


def report(result, run_id):
    return {
        'run_id':run_id,
        'input_hash':result.input_hash,
        'status':result.status,
        'feasibility':result.feasibility,
        'evidence_status':result.evidence_status,
        'comparison_context_hash':result.comparison_context_hash,
        'objectives':{
            m.objective_id:{
                'value':None if m.value is None else m.value.value,
                'unit':None if m.value is None else m.value.unit,
                'status':m.status,
            } for m in result.metrics},
        'constraints':{
            m.metric_id:{
                'value':None if m.value is None else m.value.value,
                'unit':None if m.value is None else m.value.unit,
                'status':m.status,
            } for m in result.constraint_metrics},
        'signed_flux_W_m2':result.spatial_fields.signed_hot_to_cold_flux.value
            if result.spatial_fields else None,
        'limitations':result.limitations,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--store',type=Path,required=True)
    ap.add_argument('--architecture',choices=('homogeneous','layered','gradient'),
                    default='homogeneous')
    ap.add_argument('--achieved',action='store_true',
                    help='Use an externally supplied labelled synthetic estimated profile')
    ap.add_argument('--replay',metavar='RUN_ID')
    args=ap.parse_args()
    store=RunStore(args.store)
    if args.replay:
        saved=store.load(args.replay)
        if saved.evaluation is None:
            raise ValueError('Cannot replay interrupted/failed/incomplete execution without a result')
        current=evaluate(saved.inputs)
        if current.content_hash!=saved.evaluation.content_hash:
            raise ValueError('WP2 replay changed the immutable evaluation bytes')
        print(json.dumps({**report(current,args.replay),'replay':'passed'},sort_keys=True))
        return
    if args.achieved and args.architecture!='gradient':
        ap.error('The supplied achieved-state fixture applies only to a gradient')
    x=make_wp2_achieved_fixture() if args.achieved else make_wp2_fixture(args.architecture)
    run_id=store.create(x)
    try:
        result=evaluate(x)
        store.finish(run_id,result)
    except Exception as error:
        store.fail(run_id,str(error))
        raise
    print(json.dumps(report(result,run_id),sort_keys=True))


if __name__=='__main__':
    main()
