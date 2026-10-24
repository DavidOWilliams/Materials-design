"""WP3 mixed-space campaign and paired sampling comparison.

Bounded synthetic software demonstration. Never claims a physical manufacturing
result, globally optimal search, or validated ceramic material performance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from .store import RunStore
from .wp2_numerical import evaluate, numerical_comparison_eligible
from .wp3_adapters import resolve_provider, DEFAULT, SUPPORTED
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
        provider=DEFAULT, seed=seed,
        evaluation_budget=budget,method=method,elements=elements,
        mass_limit=float(mass_limit),
        starting_design="scenario-adapter-owned",
        numerical_policy="WP2 mesh doubling on every evaluated design",
        comparison_mode="numerical-only",
        objectives=(),constraints=(),brief_hash="",property_pack_hash="",
        resource_contract="total proposal slots across resumes, including failed and invalid proposals",
    )


def _proposal(provider,index):
    return provider.start() if index==0 else provider.proposal(index-1)


def _derived(ledger, store, adapter=None):
    """Reconstruct reporting from immutable run rows, not from claimed summaries.

    A failed/created numerical attempt may have run either neither, one, or both
    mesh solves; only persisted completed WP2 results confirm both solves.
    """
    result=json.loads(_canonical(ledger))
    attempts=0
    completed=0
    hits=0
    invalid=0
    failed=0
    uncertain=0
    hashes=set()
    previous=None
    if adapter is None:
        cfg=result["config"]
        adapter=resolve_provider(cfg["provider"],cfg["seed"],cfg["method"],
                                 cfg["elements"],cfg["mass_limit"])
    baseline=adapter.baseline()
    if ([x.id for x in baseline.brief.objectives]!=result["config"]["objectives"] or
            [x.id for x in baseline.brief.constraints]!=result["config"]["constraints"] or
            baseline.brief.content_hash!=result["config"]["brief_hash"] or
            baseline.settings.property_pack_hash!=result["config"]["property_pack_hash"]):
        raise ValueError("Persisted brief, objectives, constraints or catalogue identity mismatch")
    for index,item in enumerate(result["proposals"]):
        if item.get("index")!=index:
            raise ValueError("Proposal sequence/index mismatch")
        status=item.get("status")
        if status=="invalid":
            if not item.get("reason") or "run_id" in item:
                raise ValueError("Invalid proposal evidence mismatch")
            invalid+=1
            continue
        if status not in ("created","complete","failed"):
            raise ValueError("Unknown proposal status")
        saved=store.load(item["run_id"])
        if saved.inputs.content_hash!=item.get("input_hash"):
            raise ValueError("Proposal input identity mismatch")
        proposal=item.get("proposal")
        if not isinstance(proposal,dict):
            raise ValueError("Proposal description missing")
        adapter.validate(proposal,saved.inputs)
        if (saved.inputs.brief.content_hash!=result["config"]["brief_hash"] or
                saved.inputs.settings.property_pack_hash!=result["config"]["property_pack_hash"]):
            raise ValueError("Candidate brief or catalogue differs from declared campaign")
        if item.get("parent_run_id") != saved.parent_run_id:
            raise ValueError("Parent run link mismatch")
        if list(saved.inputs.design.parent_hashes)!=item.get("parent_design_hashes"):
            raise ValueError("Parent design lineage mismatch")
        if saved.parent_run_id!=previous and previous is not None:
            raise ValueError("Proposal sequence parent mismatch")
        previous=item["run_id"]
        if item.get("cache_hit") is True:
            hits+=1
            if status!="complete":
                raise ValueError("Cached entry must be completed")
        else:
            if item.get("cache_hit") is not False:
                raise ValueError("Evaluation attempt cache flag missing")
            attempts+=1
            hashes.add(item["input_hash"])
        if status=="complete":
            if saved.evaluation is None or saved.status!="complete":
                raise ValueError("Completed proposal has no complete run")
            evaluation=saved.evaluation
            if evaluation.content_hash!=item.get("evaluation_hash"):
                raise ValueError("Completed evaluation identity mismatch")
            completed+=int(item.get("cache_hit") is False)
            item.update(objectives={m.objective_id:
                None if m.value is None else m.value.value
                for m in evaluation.metrics},
                constraints={c.constraint_id:c.outcome
                             for c in evaluation.constraint_outcomes},
                numerical_quality=evaluation.numerical_quality,
                manufacturing_feasibility=evaluation.manufacturing_feasibility,
                evidence_maturity=evaluation.evidence_status,
                hard_constraint_feasibility=evaluation.feasibility,
                qualified=numerical_comparison_eligible(evaluation,saved.inputs.brief))
        elif status=="failed":
            if saved.status!="failed":
                raise ValueError("Failed proposal has no matching failed run")
            if item.get("reason")!=saved.failure_reason:
                raise ValueError("Failed proposal reason differs from durable run")
            failed+=1
            uncertain+=1
        elif status=="created":
            if saved.status not in ("created","complete"):
                raise ValueError("Interrupted proposal run state mismatch")
            uncertain+=1
    result.update(
        evaluation_attempts=attempts,
        unique_evaluations=len(hashes),
        successful_evaluations=completed,
        cache_hits=hits,
        failed_attempts=failed,
        invalid_proposals=invalid,
        nominal_kernel_solves=completed,
        refinement_kernel_solves=completed,
        confirmed_numerical_solves=2*completed,
        uncertain_evaluation_attempts=uncertain,
        kernel_solve_count_uncertain=bool(uncertain))
    _reconstruct(result,store)
    return result


def _save_search(path,ledger,store,adapter=None):
    derived=_derived(ledger,store,adapter)
    # Preserve live proposal object identity while evaluating: replacing the
    # proposal list would detach the active item's post-evaluation updates.
    for original,reconstructed in zip(ledger["proposals"],derived["proposals"]):
        original.update(reconstructed)
    ledger.update({k:v for k,v in derived.items() if k!="proposals"})
    _write_ledger(path,ledger)


def open_search(path, *, verify_decision=True, recovery=False):
    """Validate all derived reporting without rewriting evidence.

    Recovery mode tolerates *only* stale derived fields where a created run
    remains to be reconciled. Finished ledger corruption always fails closed.
    """
    path=Path(path)
    ledger=json.loads(path.read_text())
    if ledger.get("schema_version")!=SCHEMA:
        raise ValueError("Unsupported search ledger schema")
    config=ledger.get("config")
    if not isinstance(config,dict) or ledger.get("configuration_hash")!=hashlib.sha256(_canonical(config).encode()).hexdigest():
        raise ValueError("Search configuration changed")
    if not isinstance(ledger.get("proposals"),list):
        raise ValueError("Invalid proposal ledger")
    if len(ledger["proposals"])>config["evaluation_budget"]:
        raise ValueError("Budget overrun in ledger")
    store=RunStore(path.parent/"run-store")
    reason=ledger.get("stop_reason")
    allowed={"running","cancelled","wall_time_budget_exhausted",
             "evaluation_budget_exhausted"}
    if reason not in allowed:
        raise ValueError("Unsupported campaign stop_reason: "+str(reason))
    proposals=ledger["proposals"]
    count=len(proposals)
    pending=[p for p in proposals if p.get("status")=="created"]
    terminal=ledger.get("termination_event")
    if reason=="running":
        if terminal is not None:
            raise ValueError("Running campaign carries terminal event")
        # A crash after the last evaluation but before its terminal journal
        # update can leave a full campaign running; resume finalizes it.
    else:
        if pending:
            raise ValueError("Terminated campaign retains pending work")
        if not isinstance(terminal,dict) or terminal!={"reason":reason,"proposal_slots":count}:
            raise ValueError("Campaign termination event mismatch")
        if reason=="evaluation_budget_exhausted" and count!=config["evaluation_budget"]:
            raise ValueError("Budget exhaustion requires all proposal slots consumed")
        if reason in ("cancelled","wall_time_budget_exhausted") and count>=config["evaluation_budget"]:
            raise ValueError("Early stop cannot claim full-budget exhaustion")
    expected=_derived(ledger,store)
    checked=("evaluation_attempts","unique_evaluations","successful_evaluations",
             "cache_hits","failed_attempts","invalid_proposals",
             "nominal_kernel_solves","refinement_kernel_solves",
             "confirmed_numerical_solves","uncertain_evaluation_attempts",
             "kernel_solve_count_uncertain")
    for name in checked:
        # A narrow escape route permits pre-correction crashed, incomplete
        # ledgers to be recovered. It never approves a completed corrupted log.
        if name not in ledger or ledger[name]!=expected[name]:
            # Old interrupted, incomplete ledgers may not yet have the new
            # counters. Only a pending run allows explicit recovery/migration.
            raise ValueError("Campaign accounting mismatch: "+name)
    for original,reconstructed in zip(ledger["proposals"],expected["proposals"]):
        if original.get("status")=="complete":
            for name in ("objectives","constraints","numerical_quality",
                         "manufacturing_feasibility","evidence_maturity",
                         "hard_constraint_feasibility","qualified"):
                if original.get(name)!=reconstructed.get(name):
                    raise ValueError("Persisted evaluation summary mismatch: "+name)
    if verify_decision:
        if _canonical(expected.get("qualified_comparison"))!=_canonical(ledger.get("qualified_comparison")):
            raise ValueError("Persisted qualified comparison disagrees with immutable evaluations")
    return ledger


def recompute_search(path):
    """Numerically recompute persisted evaluations, distinct from artifact checking."""
    record=open_search(path)
    if record["config"]["evaluation_adapter"]!="wp2-bounded-2":
        raise ValueError("Unavailable evaluator for numerical recomputation: "+record["config"]["evaluation_adapter"])
    store=RunStore(Path(path).parent/"run-store")
    checked=0
    for item in record["proposals"]:
        if item["status"]!="complete":
            continue
        saved=store.load(item["run_id"])
        fresh=evaluate(saved.inputs)
        if fresh.content_hash!=saved.evaluation.content_hash:
            raise ValueError("Numerical recomputation mismatch at proposal "+str(item["index"]))
        checked+=1
    return dict(recomputed=checked,replay="passed",algorithm=record["config"]["algorithm"])


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
               resume=False,wall_time_seconds=None,
               provider_factory=None,evaluation_adapter=None,
               provider_identity=None,evaluator_identity=None):
    """Restart is append-only; terminal records and completed runs are never overwritten.

    Cancellation is cooperative between evaluations. On unexpected process
    interruption, a ledger 'created' run is checked and either recovered if
    already finished or marked failed and retained before a new proposal.
    """
    if provider_factory is not None:
        raise ValueError("Unregistered factory cannot provide durable independent replay")
    if evaluator_identity not in (None,"wp2-bounded-2") and evaluation_adapter is None:
        raise ValueError("Unavailable evaluator implementation: "+str(evaluator_identity))
    if wall_time_seconds is not None and (
            type(wall_time_seconds) not in (int,float)
            or not math.isfinite(wall_time_seconds) or wall_time_seconds<0):
        raise ValueError("Invalid wall-time budget")
    config=_config(seed,budget,method,elements,mass_limit)
    selected=provider_identity or DEFAULT
    provider=resolve_provider(selected,seed,method,elements,mass_limit)
    base=provider.baseline()
    config["provider"]=selected
    config["objectives"]=[o.id for o in base.brief.objectives]
    config["constraints"]=[c.id for c in base.brief.constraints]
    config["brief_hash"]=base.brief.content_hash
    config["property_pack_hash"]=base.settings.property_pack_hash
    config["evaluation_adapter"]=evaluator_identity or "wp2-bounded-2"
    config["wall_time_seconds"]=None if wall_time_seconds is None else float(wall_time_seconds)
    path=Path(path)
    store=RunStore(path.parent/"run-store")
    if resume:
        ledger=open_search(path,recovery=True)
        if _canonical(ledger["config"])!=_canonical(config):
            raise ValueError("Cannot resume with a different campaign configuration")
        if ledger["stop_reason"]=="evaluation_budget_exhausted":
            return ledger
        ledger.setdefault("stop_history",[]).append(ledger["stop_reason"])
        ledger["stop_reason"]="running"
        ledger["termination_event"]=None
        for item in ledger["proposals"]:
            if item["status"]=="created":
                old=store.load(item["run_id"])
                if old.evaluation is not None and old.status=="complete":
                    item.update(status="complete",evaluation_hash=old.evaluation.content_hash)
                else:
                    if old.status=="created":
                        store.fail(item["run_id"],"Interrupted work; not automatically completed")
                    item.update(status="failed",reason=store.load(item["run_id"]).failure_reason)
    else:
        if path.exists():
            raise FileExistsError("Search ledger exists; open or resume instead")
        ledger=dict(schema_version=SCHEMA,config=config,
            configuration_hash=hashlib.sha256(_canonical(config).encode()).hexdigest(),
            proposals=[],stop_history=[],unique_evaluations=0,cache_hits=0,
            nominal_kernel_solves=0,refinement_kernel_solves=0,
            invalid_proposals=0,failed_attempts=0,stop_reason="running",
            qualified_comparison=None,termination_event=None)
    actual_evaluator=evaluation_adapter or evaluate
    # Reconstruct the seeded generator state even when reopening.
    for i in range(len(ledger["proposals"])):
        _proposal(provider,i)
    start=time.monotonic()
    _save_search(path,ledger,store,provider)
    for i in range(len(ledger["proposals"]),budget):
        if cancel_requested is not None and cancel_requested():
            ledger["stop_reason"]="cancelled"
            break
        if wall_time_seconds is not None and time.monotonic()-start>=wall_time_seconds:
            ledger["stop_reason"]="wall_time_budget_exhausted"
            break
        proposal=_proposal(provider,i)
        previous=next((p for p in reversed(ledger["proposals"]) if "run_id" in p),None)
        parent_run_id=None if previous is None else previous["run_id"]
        parent_hashes=() if previous is None else (store.load(parent_run_id).inputs.design.content_hash,)
        try:
            inputs=provider.build(proposal,parent_hashes)
        except (ValueError,TypeError) as exc:
            ledger["proposals"].append(dict(index=i,proposal=proposal,
                    status="invalid",reason=str(exc)))
            _save_search(path,ledger,store,provider)
            continue
        item=dict(index=i,proposal=proposal,input_hash=inputs.content_hash,
                  parent_run_id=parent_run_id, parent_design_hashes=list(parent_hashes))
        cached=store.find_complete(inputs.content_hash)
        if cached:
            saved=cached[0]
            item.update(run_id=saved.run_id,status="complete",
                evaluation_hash=saved.evaluation.content_hash,cache_hit=True)
        else:
            run_id=store.create(inputs,parent_run_id=parent_run_id)
            item.update(run_id=run_id,status="created",cache_hit=False)
            ledger["proposals"].append(item)
            _save_search(path,ledger,store,provider)
            try:
                result=actual_evaluator(inputs)
                store.finish(run_id,result)
                item.update(status="complete",evaluation_hash=result.content_hash)
            except Exception as exc:
                store.fail(run_id,str(exc))
                item.update(status="failed",reason=str(exc))
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
        _save_search(path,ledger,store,provider)
    else:
        ledger["stop_reason"]="evaluation_budget_exhausted"
    ledger["termination_event"]={"reason":ledger["stop_reason"],"proposal_slots":len(ledger["proposals"])}
    ledger["elapsed_seconds_this_execution"]=time.monotonic()-start
    _reconstruct(ledger,store)
    _save_search(path,ledger,store,provider)
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
            ledger=run_search(base/(str(seed)+"-"+method)/"campaign.json",
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
                cache_hits=ledger["cache_hits"],
                evaluation_attempts=ledger["evaluation_attempts"],
                confirmed_numerical_solves=ledger["confirmed_numerical_solves"],
                uncertain_evaluation_attempts=ledger["uncertain_evaluation_attempts"],
                kernel_solve_count_uncertain=ledger["kernel_solve_count_uncertain"],
                ledger=str(seed)+"-"+method+"/campaign.json")
        pairs.append(row)
    result=dict(schema_version=1,seeds=list(seeds),budget=budget,
        measured_outcome="qualified and Pareto portfolio coverage; no superiority presupposed",
        pairs=pairs)
    _write_ledger(base/"comparison.json",result)
    return result


def reopen_paired(path):
    """Verify reported paired totals against each independently validated run store."""
    root=Path(path)
    record=json.loads((root/"comparison.json").read_text())
    if record.get("schema_version")!=1 or not isinstance(record.get("pairs"),list):
        raise ValueError("Unsupported paired comparison")
    if record.get("seeds")!=[p.get("seed") for p in record["pairs"]]:
        raise ValueError("Paired seed identity mismatch")
    for seed_record in record["pairs"]:
        seed=seed_record["seed"]
        for method in ("explore","sampling"):
            reported=seed_record[method]
            expected_path=str(seed)+"-"+method+"/campaign.json"
            if reported.get("ledger")!=expected_path:
                raise ValueError("Paired ledger path mismatch")
            campaign=open_search(root/expected_path)
            if (campaign["config"]["seed"]!=seed or
                    campaign["config"]["method"]!=method or
                    campaign["config"]["evaluation_budget"]!=record["budget"]):
                raise ValueError("Paired campaign configuration mismatch")
            actual={
                "qualified_count":sum(p.get("qualified",False) for p in campaign["proposals"]),
                "constraint_satisfying_count":sum(
                    p.get("hard_constraint_feasibility")=="conditional"
                    for p in campaign["proposals"]),
                "pareto_count":len((campaign["qualified_comparison"] or {}).get("pareto_ids",[])),
                "unique_evaluations":campaign["unique_evaluations"],
                "kernel_solves":campaign["confirmed_numerical_solves"],
                "cache_hits":campaign["cache_hits"],
                "evaluation_attempts":campaign["evaluation_attempts"],
                "confirmed_numerical_solves":campaign["confirmed_numerical_solves"],
                "uncertain_evaluation_attempts":campaign["uncertain_evaluation_attempts"],
                "kernel_solve_count_uncertain":campaign["kernel_solve_count_uncertain"],
                "ledger":expected_path,
            }
            if _canonical(reported)!=_canonical(actual):
                raise ValueError("Paired summary disagrees with immutable campaign evidence")
    return record


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger")
    p.add_argument("--paired")
    p.add_argument("--seed",type=int,default=17)
    p.add_argument("--budget",type=int,default=9)
    p.add_argument("--elements",type=int,default=4096)
    p.add_argument("--mass-limit",type=float,default=31.)
    p.add_argument("--method",choices=["explore","sampling"],default="explore")
    p.add_argument("--provider",choices=list(SUPPORTED),default=DEFAULT)
    p.add_argument("--resume",action="store_true")
    p.add_argument("--reopen",action="store_true")
    p.add_argument("--recompute",action="store_true")
    p.add_argument("--paired-reopen",action="store_true")
    args=p.parse_args()
    if args.paired and args.paired_reopen:
        result=reopen_paired(args.paired)
    elif args.paired:
        result=compare_paired(args.paired,budget=args.budget,
                              elements=args.elements,mass_limit=args.mass_limit)
    elif args.ledger:
        result=(recompute_search(args.ledger) if args.recompute else
                open_search(args.ledger) if args.reopen else
                run_search(args.ledger,seed=args.seed,budget=args.budget,
                    elements=args.elements,mass_limit=args.mass_limit,
                    method=args.method,resume=args.resume,provider_identity=args.provider))
    else:
        p.error("--ledger or --paired required")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
