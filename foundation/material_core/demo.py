"""Executable WP1 integration check. No inverse search or manufacturing model."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from .assumptions import AssumptionRegistry
from .contracts import *
from .thermal import evaluate, solver_identity


def make_fixture(architecture='homogeneous'):
    source=Path(__file__).resolve().parents[2]/'recovered_wp0'/'thermal.py'
    p=Provenance(source_id='WP0R-synthetic-fourier',source_version='2655d64f2d5a02dfeaf2a3c4c1e553cda218a89f',
        source_hash=hashlib.sha256(source.read_bytes()).hexdigest(),location='recovered_wp0/thermal.py',
        reuse_terms='Project synthetic verification fixture; no external experimental dataset',
        evidence_kind='synthetic_scenario',conditions='Steady planar 10 mm slab, 400 K / 300 K, perfect interfaces',
        extraction='Direct configuration of the recovered benchmark')
    refs=tuple(AssumptionRef(id=x,version=1) for x in ('A01','A06','A07','A12','A14'))
    registry=AssumptionRegistry.from_builtin()
    snapshots=tuple(json.dumps(r,sort_keys=True,separators=(',',':')) for r in registry.snapshot({a.id:a.version for a in refs}))
    comp=lambda x: Composition(basis='volume',fractions=(ConstituentFraction(material_id='scenario_A',fraction=float(x)),ConstituentFraction(material_id='scenario_B',fraction=float(1-x))))
    if architecture=='homogeneous': arch=Homogeneous(composition=comp(1)); ks=(2.,)
    elif architecture=='layered':
        arch=Layered(layers=(Layer(start=0.,end=.5,composition=comp(1)),Layer(start=.5,end=1.,composition=comp(0))),interface_condition='perfect');ks=(2.,10.)
    elif architecture=='gradient':
        arch=Gradient(knots=(Knot(position=0.,composition=comp(1)),Knot(position=1.,composition=comp(0))));ks=(2.,10.)
    else: raise ValueError('Unknown fixture')
    brief=Brief(id='WP1-thermal-integration',version=1,duty='Synthetic numerical verification only',thickness=quantity('length',.01),
        hot_boundary=quantity('temperature',400),cold_boundary=quantity('temperature',300),
        mechanical_condition='Not evaluated in WP1',objectives=(Objective(id='thermal_transmission',dimension='heat_flux',unit='W/m2',direction='min',applicability='Signed through-thickness Fourier flux'),),
        assumptions=refs,evaluation_budget=1)
    materials=tuple(MaterialRecord(id='scenario_'+n,version=1,label='Synthetic scenario '+n,state='Abstract conductivity fixture, not manufactured ceramic',
         chemistry='Unspecified synthetic constituent',properties=(),provenance=p) for n in ('A','B'))
    design=IntendedDesign(id='fixture-'+architecture,thickness=brief.thickness,architecture=arch,proposal_method='Recovered reference fixture',assumptions=refs)
    settings=ThermalSettings(mesh=Discretisation(elements=128),conductivity=tuple(quantity('conductivity',k) for k in ks),provenance=p)
    return RunInputs(brief=brief,design=design,materials=materials,solver=solver_identity(),settings=settings,assumption_snapshots=snapshots,provenance=(p,))


def verify_replay(inputs, saved):
    current=evaluate(inputs)
    if current.input_hash != saved.input_hash or current.status != saved.status or current.solver!=saved.solver:
        raise ValueError('Replay identity/status mismatch')
    if current.brief_hash != saved.brief_hash or current.feasibility != saved.feasibility or current.limitations != saved.limitations:
        raise ValueError('Replay brief/interpretation mismatch')
    if len(current.metrics)!=len(saved.metrics) or len(current.temperature_K)!=len(saved.temperature_K): raise ValueError('Replay output shape mismatch')
    for a,b in zip(current.metrics,saved.metrics):
        if a.objective_id!=b.objective_id or a.status!=b.status or a.explanation!=b.explanation: raise ValueError('Replay metric mismatch')
        if a.value is None or b.value is None:
            if a.value!=b.value: raise ValueError('Replay missingness mismatch')
        elif a.value.dimension!=b.value.dimension or not math.isclose(a.value.value,b.value.value,rel_tol=1e-10,abs_tol=1e-7):
            raise ValueError('Replay flux outside tolerance')
    if any(not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-8) for a,b in zip(current.temperature_K,saved.temperature_K)):
        raise ValueError('Replay temperature outside tolerance')
    if current.flux_spread is None or saved.flux_spread is None:
        if current.flux_spread != saved.flux_spread: raise ValueError('Replay conservation diagnostic missing')
    elif not math.isclose(current.flux_spread.value,saved.flux_spread.value,rel_tol=1e-10,abs_tol=1e-7):
        raise ValueError('Replay conservation diagnostic outside tolerance')
    return current


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store',type=Path,required=True)
    parser.add_argument('--architecture',choices=('homogeneous','layered','gradient'),default='homogeneous')
    parser.add_argument('--replay',metavar='RUN_ID')
    args=parser.parse_args()
    from .store import RunStore
    store=RunStore(args.store)
    if args.replay:
        saved=store.load(args.replay)
        if saved.evaluation is None: raise ValueError('Run has no completed evaluation to replay')
        result=verify_replay(saved.inputs,saved.evaluation)
        print(json.dumps({'run_id':args.replay,'input_hash':result.input_hash,'replay':'passed','rtol':1e-10,'flux_atol_W_m2':1e-7,'temperature_atol_K':1e-8}))
    else:
        inputs=make_fixture(args.architecture)
        run_id=store.create(inputs)
        try: result=evaluate(inputs); store.finish(run_id,result)
        except Exception as e:
            store.fail(run_id,str(e)); raise
        print(json.dumps({'run_id':run_id,'input_hash':inputs.content_hash,'status':result.status,'flux_W_m2':result.metrics[0].value.value}))

if __name__=='__main__': main()
