"""WP3 bounded first vertical slice: new architecture -> WP2 -> immutable store -> replay.

This is deliberately a small, auditable implementation increment, not a
completed inverse-search campaign. All data remain synthetic.
"""
from __future__ import annotations
import json
from .contracts import (Composition, ConstituentFraction, Gradient, IntendedDesign,
                        Knot, RunInputs)
from .store import RunStore
from .wp2_numerical import context_for_run, evaluate
from .wp2_scenarios import make_wp2_fixture


def propose_gradient(*, mid_fraction: float = 0.35, elements: int = 4096) -> RunInputs:
    """Generate a non-fixture three-knot intended gradient at a common duty.

    Only interior composition changes. No claimed manufacturing feasibility.
    """
    if not isinstance(mid_fraction, (int, float)) or isinstance(mid_fraction, bool):
        raise ValueError("mid_fraction must be numeric")
    if not 0.0 <= mid_fraction <= 1.0:
        raise ValueError("mid_fraction outside [0, 1]")
    x = make_wp2_fixture("gradient", elements=elements)
    def comp(a):
        return Composition(basis="volume", fractions=(
            ConstituentFraction(material_id="scenario_A", fraction=float(a)),
            ConstituentFraction(material_id="scenario_B", fraction=float(1-a))))
    arch = Gradient(knots=(Knot(position=0., composition=comp(1.)),
                           Knot(position=.5, composition=comp(mid_fraction)),
                           Knot(position=1., composition=comp(0.))))
    design = IntendedDesign(id="wp3-new-gradient-mid-"+str(mid_fraction),
                            parent_hashes=(x.design.content_hash,),
                            thickness=x.brief.thickness, architecture=arch,
                            proposal_method="WP3 deterministic interior-knot variation; synthetic",
                            assumptions=x.brief.assumptions)
    raw = x.model_dump(mode="json")
    raw["design"] = design.model_dump(mode="json")
    provisional = RunInputs.model_validate(raw)
    raw["settings"]["evaluation_context_hash"] = context_for_run(provisional)
    return RunInputs.model_validate(raw)


def execute_one(store_path, *, mid_fraction=0.35, elements=4096):
    inputs = propose_gradient(mid_fraction=mid_fraction, elements=elements)
    store = RunStore(store_path)
    run_id = store.create(inputs)
    try:
        result = evaluate(inputs)
        store.finish(run_id, result)
    except Exception as exc:
        store.fail(run_id, str(exc))
        raise
    return {"run_id": run_id, "input_hash": inputs.content_hash,
            "evaluation_hash": result.content_hash,
            "status": result.status,
            "numerical_quality": result.numerical_quality,
            "manufacturing_feasibility": result.manufacturing_feasibility}


def replay_one(store_path, run_id):
    saved = RunStore(store_path).load(run_id)
    if saved.evaluation is None:
        raise ValueError("No evaluation available for replay")
    current = evaluate(saved.inputs)
    if current.content_hash != saved.evaluation.content_hash:
        raise ValueError("Replay differs from stored immutable evaluation")
    return {"run_id": run_id, "replay": "passed",
            "evaluation_hash": current.content_hash}


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--store", required=True)
    p.add_argument("--replay")
    p.add_argument("--mid-fraction", type=float, default=.35)
    p.add_argument("--elements", type=int, default=4096)
    args = p.parse_args()
    result = (replay_one(args.store, args.replay) if args.replay else
              execute_one(args.store, mid_fraction=args.mid_fraction,
                          elements=args.elements))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
