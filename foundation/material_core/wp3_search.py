"""WP3 mixed-space campaign and paired sampling comparison.

Bounded synthetic software demonstration. Never claims a physical manufacturing
result, globally optimal search, or validated ceramic material performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

from .store import RunStore
from .wp2_numerical import evaluate, numerical_comparison_eligible
from .wp3_provider import BoundedProvider, propose, PROVIDER_ID, CATALOGUE_ID, CATALOGUE_VERSION
from .wp3_qualified import qualified_pareto
from .wp3_campaign import _write_ledger

ALGORITHM_VERSION="wp3-mixed-search-v1"
SCHEMA=2


def _canonical(d):
    return json.dumps(d,sort_keys=True,separators=(",",":"),allow_nan=False)


def _config(seed,budget,method,elements,mass_limit):
    if type(seed) is not int or type(budget) is not int or budget<1:
        raise ValueError("Seed integer and positive evaluation budget required")
    if type(elements) is not int or elements<2:
        raise ValueError("Invalid mesh size")
    if type(mass_limit) not in (int,float) or not 0<mass_limit<1000:
        raise ValueError("Invalid mass limit")
    if method not in ("explore","sampling"):
        raise ValueError("Unsupported search method")
    return dict(schema_version=SCHEMA,algorithm=ALGORITHM_VERSION,
        provider=PROVIDER_ID,catalogue_id=CATALOGUE_ID,
        catalogue_version=CATALOGUE_VERSION, seed=seed,
        evaluation_budget=budget,method=method,elements=elements,
        mass_limit=float(mass_limit),
        starting_design="shared homogeneous A/B 0.5",
        numerical_policy="WP2 mesh doubling on every evaluated design",
        comparison_mode="numerical-only",
        objectives=("thermal_transmission","areal_mass","tensile_thermal_mismatch"),
        resource_contract="max unique WP2 evaluations including nominal and doubled mesh",
    )


def _proposal(provider,index):
    # Shared starting design in both methods. Next designs are proposed by
    # distinct, preregistered strategies under exactly the same catalogue.
    if index==0:
        return dict(architecture="homogeneous",pair=("scenario_A","scenario_B"),fraction=.5)
    return provider.proposal(index-1)


def open_search(path):
    path=Path(path)
    ledger=json.loads(path.read_text())
    if ledger.get("schema_version")!=SCHEMA:
        raise ValueError("Unsupported search ledger schema")
    config=ledger.get("config")
    if not isinstance(config,dict) or ledger.get("configuration_hash")!=hashlib.sha256(_canonical(config).encode()).hexdigest():
        raise ValueError("Search configuration changed")
    store=RunStore(path.parent/"run-store")
    if len(ledger["proposals"])>config["evaluation_budget"]:
        raise ValueError("Budget overrun in ledger")
    for item in ledger["proposals"]:
        if item["status"]=="invalid":
            if "reason" not in item:
                raise ValueError("Invalid proposal lacks reason")
            continue
        run=store.load(item["run_id"])
        if run.inputs.content_hash!=item["input_hash"]:
            raise ValueError("Input identity mismatch")
        if item["status"]=="complete":
            if run.evaluation is None or run.evaluation.content_hash!=item["evaluation_hash"]:
                raise ValueError("Evaluation identity mismatch")
        elif item["status"]=="failed" and run.status!="failed":
            raise ValueError("Failure status mismatch")
        elif item["status"]=="created" and run.status not in ("created","complete"):
            raise ValueError("Interrupted run status mismatch")
    return ledger


def _reconstruct(ledger,store):
    records=[]
    for item in ledger["proposals"]:
        if item["status"]=="complete":
            saved=store.load(item["run_id"])
            if saved.evaluation.status=="complete":
                records.append((str(item["index"]),saved.evaluation))
    if records:
        first=next(x for x in ledger["proposals"] if x["status"]=="complete")
        brief=store.load(first["run_id"]).inputs.brief
        ledger["qualified_comparison"]=qualified_pareto(records,brief)
    else:
        ledger["qualified_comparison"]=None
    return ledger


def run_search(path,*,seed=17,budget=9,method="explore",
               elements=4096,mass_limit=31.,cancel_requested=None,
               resume=False,wall_time_seconds=None):
    """Restart is append-only; terminal records and completed runs are never overwritten.

    Cancellation is cooperative between evaluations. On unexpected process
    interruption, a ledger 'created' run is checked and either recovered if
    already finished or marked failed and retained before a new proposal.
    """
    config=_config(seed,budget,method,elements,mass_limit)
    path=Path(path)
    store=RunStore(path.parent/"run-store")
    if resume:
        ledger=open_search(path)
        if _canonical(ledger["config"])!=_canonical(config):
            raise ValueError("Cannot resume with a different campaign configuration")
        if ledger["stop_reason"]=="evaluation_budget_exhausted":
            return ledger
        for item in ledger["proposals"]:
            if item["status"]=="created":
                old=store.load(item["run_id"])
                if old.evaluation is not None and old.status=="complete":
                    item.update(status="complete",evaluation_hash=old.evaluation.content_hash)
                else:
                    if old.status=="created":
                        store.fail(item["run_id"],"Interrupted work; not automatically completed")
                    item.update(status="failed",reason="Interrupted work retained")
                    ledger["failed_attempts"]+=1
    else:
        if path.exists():
            raise FileExistsError("Search ledger exists; open or resume instead")
        ledger=dict(schema_version=SCHEMA,config=config,
            configuration_hash=hashlib.sha256(_canonical(config).encode()).hexdigest(),
            proposals=[],unique_evaluations=0,cache_hits=0,
            nominal_kernel_solves=0,refinement_kernel_solves=0,
            invalid_proposals=0,failed_attempts=0,stop_reason="running",
            qualified_comparison=None)
    provider=BoundedProvider(seed,method)
    # Reconstruct the seeded generator state even when reopening.
    for i in range(len(ledger["proposals"])):
        _proposal(provider,i)
    start=time.monotonic()
    _write_ledger(path,ledger)
    for i in range(len(ledger["proposals"]),budget):
        if cancel_requested is not None and cancel_requested():
            ledger["stop_reason"]="cancelled"
            break
        if wall_time_seconds is not None and time.monotonic()-start>=wall_time_seconds:
            ledger["stop_reason"]="wall_time_budget_exhausted"
            break
        proposal=_proposal(provider,i)
        try:
            inputs=propose(**proposal,elements=elements,mass_limit=mass_limit)
        except (ValueError,TypeError) as exc:
            ledger["invalid_proposals"]+=1
            ledger["proposals"].append(dict(index=i,proposal=proposal,
                    status="invalid",reason=str(exc)))
            _write_ledger(path,ledger)
            continue
        item=dict(index=i,proposal=proposal,input_hash=inputs.content_hash)
        cached=store.find_complete(inputs.content_hash)
        if cached:
            saved=cached[0]
            item.update(run_id=saved.run_id,status="complete",
                evaluation_hash=saved.evaluation.content_hash,cache_hit=True)
            ledger["cache_hits"]+=1
        else:
            run_id=store.create(inputs)
            item.update(run_id=run_id,status="created",cache_hit=False)
            ledger["proposals"].append(item)
            _write_ledger(path,ledger)
            ledger["unique_evaluations"]+=1
            ledger["nominal_kernel_solves"]+=1
            ledger["refinement_kernel_solves"]+=1
            try:
                result=evaluate(inputs)
                store.finish(run_id,result)
                item.update(status="complete",evaluation_hash=result.content_hash)
            except Exception as exc:
                store.fail(run_id,str(exc))
                item.update(status="failed",reason=str(exc))
                ledger["failed_attempts"]+=1
            # Already appended before the solve for crash recovery.
        if cached:
            ledger["proposals"].append(item)
        if item["status"]=="complete":
            result=store.load(item["run_id"]).evaluation
            item.update(objectives={m.objective_id:None if m.value is None else m.value.value
                          for m in result.metrics},
                constraints={c.constraint_id:c.outcome for c in result.constraint_outcomes},
                numerical_quality=result.numerical_quality,
                manufacturing_feasibility=result.manufacturing_feasibility,
                evidence_maturity=result.evidence_status,
                hard_constraint_feasibility=result.feasibility,
                qualified=numerical_comparison_eligible(result,inputs.brief))
        _write_ledger(path,ledger)
    else:
        ledger["stop_reason"]="evaluation_budget_exhausted"
    ledger["elapsed_seconds_this_execution"]=time.monotonic()-start
    _reconstruct(ledger,store)
    _write_ledger(path,ledger)
    return open_search(path)


def compare_paired(path,*,seeds=(11,23,37),budget=9,elements=4096,mass_limit=31.):
    """Same starting design, catalogue, mesh, numerical policy and evaluation caps.

    Reports qualified counts, feasibility and Pareto coverage. No post hoc
    objective scaling, preference scores, or fabricated hypervolume.
    """
    if not seeds or any(type(s) is not int for s in seeds):
        raise ValueError("Paired seeds must be nonempty integer sequence")
    base=Path(path)
    if base.exists():
        raise FileExistsError("Paired comparison already exists")
    base.mkdir(parents=True)
    pairs=[]
    for seed in seeds:
        row={"seed":seed}
        for method in ("explore","sampling"):
            ledger=run_search(base/(str(seed)+"-"+method+".json"),
                seed=seed,budget=budget,method=method,
                elements=elements,mass_limit=mass_limit)
            qualified=sum(p.get("qualified",False) for p in ledger["proposals"])
            feasible=sum(p.get("hard_constraint_feasibility")=="conditional"
                         for p in ledger["proposals"])
            row[method]=dict(qualified_count=qualified,
                constraint_satisfying_count=feasible,
                pareto_count=len((ledger["qualified_comparison"] or {}).get("pareto_ids",[])),
                unique_evaluations=ledger["unique_evaluations"],
                kernel_solves=ledger["nominal_kernel_solves"]+ledger["refinement_kernel_solves"],
                cache_hits=ledger["cache_hits"],ledger=str(seed)+"-"+method+".json")
        pairs.append(row)
    result=dict(schema_version=1,seeds=list(seeds),budget=budget,
        measured_outcome="qualified and Pareto portfolio coverage; no superiority presupposed",
        pairs=pairs)
    _write_ledger(base/"comparison.json",result)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger")
    p.add_argument("--paired")
    p.add_argument("--seed",type=int,default=17)
    p.add_argument("--budget",type=int,default=9)
    p.add_argument("--elements",type=int,default=4096)
    p.add_argument("--mass-limit",type=float,default=31.)
    p.add_argument("--method",choices=["explore","sampling"],default="explore")
    p.add_argument("--resume",action="store_true")
    p.add_argument("--reopen",action="store_true")
    args=p.parse_args()
    if args.paired:
        result=compare_paired(args.paired,budget=args.budget,
                              elements=args.elements,mass_limit=args.mass_limit)
    elif args.ledger:
        result=(open_search(args.ledger) if args.reopen else
                run_search(args.ledger,seed=args.seed,budget=args.budget,
                    elements=args.elements,mass_limit=args.mass_limit,
                    method=args.method,resume=args.resume))
    else:
        p.error("--ledger or --paired required")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
