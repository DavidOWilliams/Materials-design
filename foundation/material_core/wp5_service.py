"""WP5 bounded interface-to-WP4 adapter; no new physical calculations."""
from __future__ import annotations
import json
from pathlib import Path
from .contracts import RunInputs
from .wp4_feedback import starting_inputs, run, save, reopen, recompute
from .wp4_export import export
from .wp4_journal import initialize, resume, read_manifest, read_attempts
from .wp5_brief_editor import validate_brief


def prepared_inputs(*, elements=128, mass_limit=31.0, brief=None):
    """Retain a WP4-supported synthetic fixture; reject unsupported brief edits."""
    base = starting_inputs(elements=elements, mass_limit=mass_limit)
    if brief is None:
        return base
    candidate = validate_brief(brief)
    raw = base.model_dump(mode="json")
    old = base.brief
    # WP4's bounded scenario supports edits to the existing duty description and
    # budget only; changing physics requires a new qualified core fixture.
    allowed = {"duty", "evaluation_budget", "id", "version", "assumptions"}
    for field in old.model_fields:
        if field not in allowed and getattr(candidate, field) != getattr(old, field):
            raise ValueError("Unsupported WP4 duty/geometry/constraint edit: " + field)
    raw["brief"] = candidate.model_dump(mode="json")
    from .wp2_numerical import context_for_run
    raw["settings"]["evaluation_context_hash"] = context_for_run(
        RunInputs.model_validate_json(json.dumps(raw)))
    return RunInputs.model_validate_json(json.dumps(raw))


def execute(path, *, elements=128, mass_limit=31.0, layer=0.005,
            feed=0.25, budget=4, feedback=True, route="synthetic_ideal_planar_deposition",
            brief=None, cancel_requested=None):
    """Create immutable dossier; never overwrite or claim measured evidence."""
    path = Path(path)
    if path.exists():
        raise FileExistsError("Dossier already exists")
    if type(budget) is not int or budget < 1:
        raise ValueError("Positive budget required")
    base = prepared_inputs(elements=elements, mass_limit=mass_limit, brief=brief)
    record = run(elements=elements, mass_limit=mass_limit, layer=layer, feed=feed,
                 budget=budget, feedback=feedback, route=route,
                 base_inputs=base, cancel_requested=cancel_requested)
    save(path, record)
    return reopen(path)


def inspect(path):
    record = reopen(path)
    return {
        "algorithm": record["algorithm"],
        "brief_hash": RunInputs.model_validate_json(json.dumps(record["baseline_intended_inputs"])).brief.content_hash,
        "stop_reason": record["stop_reason"],
        "records": record["records"],
        "measured_evidence": None,
        "manufacturing_validation": "not_established",
        "export": export(path),
    }


def replay(path):
    return recompute(path)


def resume_journal(path, *, output, **config):
    """Only resume an existing WP4 journal; no mid-solver restart."""
    return resume(path, output=output, **config)


def compare_compatible(first, second):
    """Reject different duties, solver contexts, materials or process conditions."""
    a, b = reopen(first), reopen(second)
    x = RunInputs.model_validate_json(json.dumps(a["baseline_intended_inputs"]))
    y = RunInputs.model_validate_json(json.dumps(b["baseline_intended_inputs"]))
    if x.brief.content_hash != y.brief.content_hash:
        raise ValueError("Incompatible brief or duty")
    if x.materials != y.materials or x.solver != y.solver or x.settings != y.settings:
        raise ValueError("Incompatible materials, solver or settings")
    if a["process"] != b["process"]:
        raise ValueError("Incompatible process assumptions; show as separate scenarios")
    return {"first": export(first), "second": export(second),
            "comparison": "same brief, properties, solver and process scenario",
            "measured_evidence": None}
