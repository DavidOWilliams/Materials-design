"""P1 equal-proposal comparator. Synthetic, in-model evidence only.

Both arms receive identical seeded WP3 proposals. The feedback arm may revise a
proposal using the *preceding own-arm* achieved mass violation; the blind arm
cannot observe achieved-state outputs while selecting the next candidate.
This is a bounded density-guided correction, not multiobjective optimisation.
"""
from __future__ import annotations
import hashlib
import json
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
                  numerical_cpu_ns=0, manufacturing_cpu_ns=0,
                  proposal_cpu_ns=0, final_scoring_evaluations=0)
    # Both arms use an independently instantiated provider with the same seed.
    for index in range(budget):
        start = process_time_ns()
        spec, base = _candidate(provider, index)
        if feedback and previous_feedback is not None:
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
            base = _replace_design(base, revised)
        proposal_ns = process_time_ns() - start
        totals["proposal_cpu_ns"] += proposal_ns
        totals["proposals"] += 1
        row = dict(index=index, seed=seed, proposal=spec,
                   intended_hash=base.design.content_hash,
                   revision_applied=bool(feedback and previous_feedback is not None),
                   status="pending", proposal_cpu_ns=proposal_ns,
                   manufacturing_cpu_ns=0, numerical_cpu_ns=0)
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
            totals["manufacturing_cpu_ns"] += process_time_ns() - start
            row.update(status="transform_failed", error=repr(exc))
            rows.append(row)
            previous_feedback = None
            continue
        start = process_time_ns()
        totals["cache_misses"] += 1  # caching deliberately disabled for parity
        try:
            result = evaluate(achieved)
            totals["numerical_evaluations"] += 1
            row["numerical_cpu_ns"] = process_time_ns() - start
            totals["numerical_cpu_ns"] += row["numerical_cpu_ns"]
            observation = _feedback(result, float(mass_limit))
            row.update(status="complete", evaluation_hash=result.content_hash,
                       objectives={m.objective_id: (
                           None if m.value is None else m.value.value)
                           for m in result.metrics},
                       qualified=numerical_comparison_eligible(result, achieved.brief),
                       feasibility=result.feasibility,
                       manufacturing_feasibility=result.manufacturing_feasibility,
                       numerical_quality=result.numerical_quality)
            previous_feedback = observation if feedback else None
        except Exception as exc:
            totals["failed_evaluations"] += 1
            totals["numerical_cpu_ns"] += process_time_ns() - start
            row.update(status="evaluation_failed", error=repr(exc))
            previous_feedback = None
        rows.append(row)
    record = dict(config=config, config_sha256=digest(config),
                  rows=rows, accounting=totals, measured_evidence=None,
                  claim="synthetic in-model comparison only",
                  matched_cpu_budget=False, final_independent_scoring=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Refuse accidental replacement even if the file appears during execution.
    with path.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return record

def compare(a, b):
    """Audit paired trial identity and nominal numerical-work budget."""
    x, y = (json.loads(Path(p).read_text()) for p in (a, b))
    for record in (x, y):
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


def score_saved(path):
    """Rebuild and recompute every candidate with the same synthetic evaluator.

    This is common *in-model* scoring, NOT an independent physical process model.
    Search budgets exclude these separate, individually counted solves.
    """
    data=json.loads(Path(path).read_text())
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
        results.append(dict(index=i,achieved_objectives=scores,
                            feasible=bool(numerical_comparison_eligible(
                                result, achieved.brief) and
                                result.feasibility=="conditional" and
                                result.manufacturing_feasibility=="conditional"),
                            evaluation_hash=result.content_hash))
        previous_feedback=(_feedback(result,cfg["mass_limit"])
                           if cfg["feedback"] else None)
    return dict(config_sha256=data["config_sha256"],
                common_scorer="WP4 achieved state + WP2 numerical evaluator",
                scoring_evaluations=len(results),results=results,
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
