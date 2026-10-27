"""P1 equal-proposal comparator. Synthetic, in-model evidence only.

Both arms receive identical seeded WP3 proposals. The feedback arm may revise a
proposal using the *preceding own-arm* achieved mass violation; the blind arm
cannot observe achieved-state outputs while selecting the next candidate.
This is a bounded density-guided correction, not multiobjective optimisation.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
from time import process_time_ns

from .wp3_adapters import resolve_provider, DEFAULT
from .wp4_feedback import scenario, _revise, _replace_design
from .wp4_bridge import estimated_inputs
from .wp2_numerical import evaluate, numerical_comparison_eligible

SCHEMA = "p1-equal-proposals-v1"

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def _feedback(evaluation, mass_limit):
    mass = next((m.value.value for m in evaluation.metrics
                 if m.objective_id == "areal_mass" and m.value is not None), None)
    if mass is None or mass <= mass_limit:
        return None
    return {"metric": "areal_mass", "relation": "le", "actual": mass,
            "limit": mass_limit}

def _candidate(provider, index):
    spec = provider.start() if index == 0 else provider.proposal(index - 1)
    return spec, provider.build(spec, ())

def _save_checkpoint(path, record):
    """Atomic restart record; checksum guards truncated or edited snapshots."""
    checkpoint=Path(str(path)+".checkpoint.json")
    payload=dict(record=record,sha256=digest(record))
    temporary=Path(str(checkpoint)+".pending")
    if temporary.exists():
        raise FileExistsError("Unresolved partial checkpoint write")
    checkpoint.parent.mkdir(parents=True,exist_ok=True)
    with temporary.open("x",encoding="utf-8") as f:
        f.write(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+"\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temporary,checkpoint)

def _load_checkpoint(path, config):
    checkpoint=Path(str(path)+".checkpoint.json")
    if not checkpoint.exists():
        return None
    payload=json.loads(checkpoint.read_text())
    record=payload["record"]
    if payload.get("sha256")!=digest(record) or record.get("config")!=config:
        raise ValueError("Incompatible or corrupt P1 checkpoint")
    if record.get("config_sha256")!=digest(config):
        raise ValueError("P1 checkpoint config digest mismatch")
    rows=record.get("rows")
    if not isinstance(rows,list) or len(rows)>config["budget"]:
        raise ValueError("P1 checkpoint proposal count mismatch")
    if any(row.get("index")!=i or row.get("status") not in
           ("complete","evaluation_failed","transform_failed")
           for i,row in enumerate(rows)):
        raise ValueError("P1 checkpoint row/index invalid")
    totals=record.get("accounting",{})
    if totals.get("proposals")!=len(rows):
        raise ValueError("P1 checkpoint accounting count mismatch")
    for key in ("proposal_cpu_ns","manufacturing_cpu_ns","numerical_cpu_ns","feedback_cpu_ns"):
        if totals.get(key)!=sum(row.get(key,0) for row in rows):
            raise ValueError("P1 checkpoint CPU accounting mismatch: "+key)
    return record

def execute(*, seed, budget, feedback, output, elements=128, mass_limit=31.0,
            layer=0.005, feed=0.25, route="synthetic_ideal_planar_deposition",
            method="sampling"):
    """Immutable fail-closed evidence; budget counts all proposal slots.

    Numerical evaluator and manufacturing transformation are charged on both
    arms; final independent evaluation is not included. CPU timings are
    descriptive, not time-matched experiments.
    """
    if type(seed) is not int or type(budget) is not int or budget < 1:
        raise ValueError("Seed must be an integer, budget a positive integer")
    if type(feedback) is not bool or method not in ("sampling", "explore"):
        raise ValueError("Unsupported feedback flag or proposal method")
    if type(elements) is not int or elements < 2:
        raise ValueError("Invalid mesh")
    if type(mass_limit) not in (float, int) or not 0 < mass_limit < 1000:
        raise ValueError("Invalid constraint")
    path = Path(output)
    if path.exists():
        raise FileExistsError("Immutable P1 record exists")
    provider = resolve_provider(DEFAULT, seed, method, elements, mass_limit)
    process = scenario(layer, feed, route)
    config = dict(schema=SCHEMA, seed=seed, budget=budget, feedback=feedback,
                  elements=elements, mass_limit=float(mass_limit), method=method,
                  layer=layer, feed=feed, route=route, provider=DEFAULT)
    previous_feedback = None
    rows = []
    totals = dict(proposals=0, numerical_evaluations=0,
                  manufacturing_transformations=0, failed_evaluations=0,
                  failed_transformations=0, cache_hits=0, cache_misses=0,
                  feedback_calculations=0, feedback_cpu_ns=0,
                  numerical_cpu_ns=0, manufacturing_cpu_ns=0,
                  proposal_cpu_ns=0, final_scoring_evaluations=0)
    # Resume recorded candidates without charging or repeating earlier solves.
    journal=_load_checkpoint(path,config)
    if journal is not None:
        rows=journal["rows"]
        totals=journal["accounting"]
        for i,row in enumerate(rows):
            spec,_=_candidate(provider,i)
            if canonical(spec)!=canonical(row["proposal"]):
                raise ValueError("P1 checkpoint proposal stream mismatch")
        if feedback and rows and rows[-1]["status"]=="complete":
            mass=rows[-1].get("objectives",{}).get("areal_mass")
            if mass is not None and mass>float(mass_limit):
                previous_feedback=dict(metric="areal_mass",relation="le",
                                       actual=mass,limit=float(mass_limit))
    def checkpoint_after_row():
        _save_checkpoint(path,dict(config=config,config_sha256=digest(config),
                                  rows=rows,accounting=totals))
    # Both arms use an independently instantiated provider with the same seed.
    for index in range(len(rows),budget):
        start = process_time_ns()
        spec, base = _candidate(provider, index)
        revision_ns = 0
        actual_change = False
        if feedback and previous_feedback is not None:
            revision_start = process_time_ns()
            # WP4 revision policy assumes exactly two material records, while
            # the WP3 catalogue retains an unused third record for other pairs.
            # Project only the candidate's active two records for revision
            # decision; evaluate with the unchanged full WP3 property pack.
            from types import SimpleNamespace
            active = {fraction.material_id for fraction in
                      (base.design.architecture.composition.fractions
                       if hasattr(base.design.architecture, "composition")
                       else base.design.architecture.layers[0].composition.fractions
                       if hasattr(base.design.architecture, "layers")
                       else base.design.architecture.knots[0].composition.fractions)}
            scoped = SimpleNamespace(
                materials=tuple(m for m in base.materials if m.id in active))
            revised = _revise(scoped, base.design, previous_feedback)
            actual_change = revised.architecture != base.design.architecture
            base = _replace_design(base, revised)
            revision_ns = process_time_ns() - revision_start
        proposal_ns = process_time_ns() - start
        totals["proposal_cpu_ns"] += proposal_ns
        totals["proposals"] += 1
        row = dict(index=index, seed=seed, proposal=spec,
                   intended_hash=base.design.content_hash,
                   revision_attempted=bool(feedback and previous_feedback is not None),
                   revision_applied=actual_change,
                   status="pending", proposal_cpu_ns=proposal_ns,
                   manufacturing_cpu_ns=0, numerical_cpu_ns=0,
                   revision_cpu_ns=revision_ns, feedback_cpu_ns=0)
        # The blind-arm proposal is selected without feeding its achieved
        # state or numerical objective values back to the generator.
        start = process_time_ns()
        try:
            achieved = estimated_inputs(base, process)
            totals["manufacturing_transformations"] += 1
            row["manufacturing_cpu_ns"] = process_time_ns() - start
            totals["manufacturing_cpu_ns"] += row["manufacturing_cpu_ns"]
            row["achieved_inputs_hash"] = achieved.content_hash
        except Exception as exc:
            totals["failed_transformations"] += 1
            row["manufacturing_cpu_ns"] = process_time_ns() - start
            totals["manufacturing_cpu_ns"] += row["manufacturing_cpu_ns"]
            row.update(status="transform_failed", error=repr(exc))
            rows.append(row)
            previous_feedback = None
            checkpoint_after_row()
            continue
        start = process_time_ns()
        totals["cache_misses"] += 1  # caching deliberately disabled for parity
        try:
            result = evaluate(achieved)
            totals["numerical_evaluations"] += 1
            row["numerical_cpu_ns"] = process_time_ns() - start
            totals["numerical_cpu_ns"] += row["numerical_cpu_ns"]
            observation = None
            if feedback:
                fb_start = process_time_ns()
                observation = _feedback(result, float(mass_limit))
                row["feedback_cpu_ns"] = process_time_ns() - fb_start
                totals["feedback_calculations"] += 1
                totals["feedback_cpu_ns"] += row["feedback_cpu_ns"]
            row.update(status="complete", evaluation_hash=result.content_hash,
                       objectives={m.objective_id: (
                           None if m.value is None else m.value.value)
                           for m in result.metrics},
                       qualified=numerical_comparison_eligible(result, achieved.brief),
                       feasibility=result.feasibility,
                       manufacturing_feasibility=result.manufacturing_feasibility,
                       numerical_quality=result.numerical_quality)
            previous_feedback = observation
        except Exception as exc:
            totals["failed_evaluations"] += 1
            row["numerical_cpu_ns"] = process_time_ns() - start
            totals["numerical_cpu_ns"] += row["numerical_cpu_ns"]
            row.update(status="evaluation_failed", error=repr(exc))
            previous_feedback = None
        rows.append(row)
        checkpoint_after_row()
    record = dict(config=config, config_sha256=digest(config),
                  rows=rows, accounting=totals, measured_evidence=None,
                  claim="synthetic in-model comparison only",
                  matched_cpu_budget=False, final_independent_scoring=False,
                  stop_reason="proposal_budget_exhausted")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Refuse accidental replacement even if the file appears during execution.
    with path.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return record

def audit_record(record):
    """Fail closed for forged counters, row identities and cache declarations."""
    cfg=record.get("config")
    if not isinstance(cfg,dict) or record.get("config_sha256")!=digest(cfg):
        raise ValueError("P1 config digest identity mismatch")
    rows=record.get("rows")
    counters=record.get("accounting")
    if not isinstance(rows,list) or not isinstance(counters,dict) or len(rows)>cfg["budget"]:
        raise ValueError("P1 candidate budget/accounting mismatch")
    cpu=("proposal_cpu_ns","manufacturing_cpu_ns","numerical_cpu_ns","feedback_cpu_ns")
    for i,row in enumerate(rows):
        if row.get("index")!=i or row.get("status") not in (
                "complete","evaluation_failed","transform_failed"):
            raise ValueError("P1 row status/index invalid")
        for name in cpu+("revision_cpu_ns",):
            val=row.get(name)
            if type(val) is not int or val<0:
                raise ValueError("Invalid per-candidate CPU counter: "+name)
        if row["revision_cpu_ns"]>row["proposal_cpu_ns"]:
            raise ValueError("Revision CPU exceeds generation CPU")
        if not cfg["feedback"] and (row.get("revision_applied") or row["feedback_cpu_ns"]):
            raise ValueError("Blind control leaked feedback")
    for key in cpu:
        if type(counters.get(key)) is not int or counters[key]!=sum(x[key] for x in rows):
            raise ValueError("P1 CPU accounting mismatch: "+key)
    def check(key,n):
        if type(counters.get(key)) is not int or counters[key]!=n:
            raise ValueError("P1 accounting mismatch: "+key)
    check("proposals",len(rows))
    check("numerical_evaluations",sum(x["status"]=="complete" for x in rows))
    check("manufacturing_transformations",sum(x["status"]!="transform_failed" for x in rows))
    check("failed_evaluations",sum(x["status"]=="evaluation_failed" for x in rows))
    check("failed_transformations",sum(x["status"]=="transform_failed" for x in rows))
    check("cache_hits",0)
    check("cache_misses",sum(x["status"]!="transform_failed" for x in rows))
    if record.get("stop_reason") not in (None,"proposal_budget_exhausted"):
        raise ValueError("Invalid stop reason")
    if record.get("stop_reason")=="proposal_budget_exhausted" and len(rows)!=cfg["budget"]:
        raise ValueError("False budget exhaustion")
    return True

def compare(a, b):
    """Audit paired trial identity and nominal numerical-work budget."""
    x, y = (json.loads(Path(p).read_text()) for p in (a, b))
    for record in (x, y):
        audit_record(record)
        if digest(record["config"]) != record["config_sha256"]:
            raise ValueError("Configuration digest mismatch")
        if record["config"]["budget"] != len(record["rows"]):
            raise ValueError("Missing proposal attempts")
    ca, cb = x["config"], y["config"]
    if ca["feedback"] == cb["feedback"] or any(
            ca[key] != cb[key] for key in ca if key != "feedback"):
        raise ValueError("Incompatible experiment arms")
    ax, ay = x["accounting"], y["accounting"]
    matched = (ax["proposals"] == ay["proposals"] == ca["budget"] and
               ax["manufacturing_transformations"] == ay["manufacturing_transformations"] and
               ax["numerical_evaluations"] == ay["numerical_evaluations"])
    return dict(matched_numerical_work=matched, blind=ax if not ca["feedback"] else ay,
                feedback=ax if ca["feedback"] else ay,
                matched_cpu_time=False, independent_scoring=False)


def score_saved(path, *, heldout_feed=None):
    """Rebuild and recompute every candidate with the same synthetic evaluator.

    This is common *in-model* scoring, NOT an independent physical process model.
    Search budgets exclude these separate, individually counted solves.
    """
    data=json.loads(Path(path).read_text())
    audit_record(data)
    cfg=data["config"]
    if cfg["schema"]!=SCHEMA or digest(cfg)!=data["config_sha256"]:
        raise ValueError("Invalid frozen configuration identity")
    if len(data["rows"])!=cfg["budget"]:
        raise ValueError("Invalid or truncated candidate record")
    provider=resolve_provider(cfg["provider"],cfg["seed"],cfg["method"],
                              cfg["elements"],cfg["mass_limit"])
    process=scenario(cfg["layer"],cfg["feed"],cfg["route"])
    results=[]
    previous_feedback=None
    for i,row in enumerate(data["rows"]):
        if row["index"]!=i:
            raise ValueError("Candidate ordering mismatch")
        spec,base=_candidate(provider,i)
        if canonical(spec)!=canonical(row["proposal"]):
            raise ValueError("Proposal generator does not reproduce saved candidate")
        if cfg["feedback"] and previous_feedback is not None:
            from types import SimpleNamespace
            arch=base.design.architecture
            comp=(arch.composition if hasattr(arch,"composition")
                  else arch.layers[0].composition if hasattr(arch,"layers")
                  else arch.knots[0].composition)
            active={f.material_id for f in comp.fractions}
            scoped=SimpleNamespace(materials=tuple(
                m for m in base.materials if m.id in active))
            base=_replace_design(base,_revise(scoped,base.design,previous_feedback))
        if row["intended_hash"]!=base.design.content_hash:
            raise ValueError("Replayed intended design mismatch")
        achieved=estimated_inputs(base,process)
        if row.get("achieved_inputs_hash")!=achieved.content_hash:
            raise ValueError("Replayed achieved-state mismatch")
        result=evaluate(achieved)
        if row.get("status")!="complete" or row.get("evaluation_hash")!=result.content_hash:
            raise ValueError("Recomputed numerical evaluation mismatch")
        scores={m.objective_id:None if m.value is None else m.value.value
                for m in result.metrics}
        if scores!=row["objectives"]:
            raise ValueError("Stored objective values disagree with recomputation")
        scored_result = result
        scored_inputs = achieved
        if heldout_feed is not None:
            changed_process = scenario(cfg["layer"], heldout_feed, cfg["route"])
            scored_inputs = estimated_inputs(base, changed_process)
            scored_result = evaluate(scored_inputs)
            scores = {m.objective_id:None if m.value is None else m.value.value
                      for m in scored_result.metrics}
        results.append(dict(index=i,achieved_objectives=scores,
                            feasible=bool(numerical_comparison_eligible(
                                scored_result, scored_inputs.brief) and
                                scored_result.feasibility=="conditional" and
                                scored_result.manufacturing_feasibility=="conditional"),
                            evaluation_hash=scored_result.content_hash))
        previous_feedback=(_feedback(result,cfg["mass_limit"])
                           if cfg["feedback"] else None)
    return dict(config_sha256=data["config_sha256"],
                common_scorer="WP4 achieved state + WP2 numerical evaluator",
                scoring_evaluations=len(results)*(2 if heldout_feed is not None else 1),
                heldout_feed=heldout_feed,results=results,
                measured_evidence=None,
                external_process_validation=False)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--budget", type=int, required=True)
    parser.add_argument("--feedback", action="store_true")
    parser.add_argument("--elements", type=int, default=128)
    args = parser.parse_args()
    record = execute(seed=args.seed, budget=args.budget, feedback=args.feedback,
                     output=args.output, elements=args.elements)
    print(canonical({"configuration_hash": record["config_sha256"],
                     "accounting": record["accounting"]}))

if __name__ == "__main__":
    main()
