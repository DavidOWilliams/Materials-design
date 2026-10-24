"""Bounded, seeded WP3 gradient campaign increment (synthetic reference pack).

This service is deliberately not the full WP3 search: constituent choice, alternate
architectures and fair sampling baseline are separate pending capabilities.
Completed WP2 evaluations live in the immutable RunStore. The campaign ledger is
written atomically and revalidated when opened. No manufacturability is inferred.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import time

from .store import RunStore
from .wp2_numerical import evaluate, numerical_comparison_eligible
from .wp3_qualified import qualified_pareto
from .wp3_vertical import propose_gradient


def _write_ledger(path: Path, ledger: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".pending")
    with temporary.open("w", encoding="utf8") as stream:
        json.dump(ledger, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def reopen_campaign(path):
    """Integrity-check all completed links; reopening never invokes a solver."""
    path = Path(path)
    ledger = json.loads(path.read_text(encoding="utf8"))
    if ledger.get("schema_version") != 1 or not isinstance(ledger.get("proposals"), list):
        raise ValueError("Unsupported campaign ledger")
    store = RunStore(path.parent / "run-store")
    for item in ledger["proposals"]:
        saved = store.load(item["run_id"])
        if saved.inputs.content_hash != item["input_hash"]:
            raise ValueError("Campaign input hash mismatch")
        if item["status"] == "complete":
            if saved.evaluation is None or saved.evaluation.content_hash != item["evaluation_hash"]:
                raise ValueError("Campaign evaluation hash mismatch")
        elif saved.status != "failed":
            raise ValueError("Campaign failed proposal lacks stored failure")
    return ledger


def run_campaign(path, *, seed: int, evaluation_budget: int, elements=4096,
                 cancel_requested=None):
    """One finite seeded gradient variation per WP2 evaluation.

    Evaluation budget counts attempted unique numerical evaluations; each WP2
    evaluation includes a nominal and a doubled-mesh kernel solve.
    Cancellation is checked between evaluations, not within a kernel solve.
    """
    if type(seed) is not int or type(evaluation_budget) is not int or evaluation_budget < 1:
        raise ValueError("Seed must be an integer and evaluation budget positive")
    if type(elements) is not int or elements < 2:
        raise ValueError("elements must be an integer >= 2")
    path = Path(path)
    if path.exists():
        raise FileExistsError("Campaign ledger exists; reopen it instead of overwriting")
    store = RunStore(path.parent / "run-store")
    rng = random.Random(seed)
    ledger = dict(schema_version=1, algorithm="seeded-uniform-gradient-mid-v1",
                  seed=seed, evaluation_budget=evaluation_budget, elements=elements,
                  started_at=time.time(), proposals=[], unique_evaluations=0,
                  nominal_kernel_solves=0, refinement_kernel_solves=0,
                  cache_hits=0, failed_attempts=0, stop_reason="running")
    _write_ledger(path, ledger)
    records = []
    for index in range(evaluation_budget):
        if cancel_requested is not None and cancel_requested():
            ledger["stop_reason"] = "cancelled"
            break
        # Include both known regression endpoints in the sampled portfolio.
        fraction = (0.35 if index == 0 else 0.65 if index == 1
                    else round(rng.uniform(0.05, 0.95), 10))
        inputs = propose_gradient(mid_fraction=fraction, elements=elements)
        cached = store.find_complete(inputs.content_hash)
        item = dict(index=index, fraction=fraction, input_hash=inputs.content_hash)
        if cached:
            saved = cached[0]
            result = saved.evaluation
            item["run_id"] = saved.run_id
            ledger["cache_hits"] += 1
        else:
            run_id = store.create(inputs)
            item["run_id"] = run_id
            ledger["unique_evaluations"] += 1
            ledger["nominal_kernel_solves"] += 1
            ledger["refinement_kernel_solves"] += 1
            try:
                result = evaluate(inputs)
                store.finish(run_id, result)
            except Exception as exc:
                store.fail(run_id, str(exc))
                item.update(status="failed", reason=str(exc))
                ledger["failed_attempts"] += 1
                ledger["proposals"].append(item)
                _write_ledger(path, ledger)
                continue
        item.update(status="complete", evaluation_hash=result.content_hash,
                    numerical_quality=result.numerical_quality,
                    constraint_outcomes={x.constraint_id: x.outcome for x in result.constraint_outcomes},
                    manufacturing_feasibility=result.manufacturing_feasibility,
                    numerically_eligible=numerical_comparison_eligible(result, inputs.brief))
        ledger["proposals"].append(item)
        records.append((str(index), result))
        _write_ledger(path, ledger)
    if ledger["stop_reason"] == "running":
        ledger["stop_reason"] = "evaluation_budget_exhausted"
    if records:
        brief=store.load(ledger["proposals"][0]["run_id"]).inputs.brief
        # Only complete evaluations enter comparison; incompatible contexts
        # are rejected by WP2 comparison gate rather than silently grouped.
        ledger["qualified_comparison"] = qualified_pareto(records, brief)
    else:
        ledger["qualified_comparison"] = None
    ledger["elapsed_seconds"] = time.time() - ledger["started_at"]
    _write_ledger(path, ledger)
    return reopen_campaign(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--budget", type=int, default=3)
    parser.add_argument("--elements", type=int, default=4096)
    parser.add_argument("--reopen", action="store_true")
    args=parser.parse_args()
    record=(reopen_campaign(args.ledger) if args.reopen else
            run_campaign(args.ledger, seed=args.seed,
                         evaluation_budget=args.budget, elements=args.elements))
    print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()
