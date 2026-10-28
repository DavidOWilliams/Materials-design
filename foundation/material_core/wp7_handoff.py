"""Conservative, traceable WP3 -> WP4 handoff and checkpointed feedback.

Scientific restriction: only an original WP3 gradient using scenario_A/B is
compatible with the accepted WP4 two-constituent feedback policy. WP3's third
catalogue constituent is deliberately excluded, never silently substituted.
The WP3 numerical comparison and WP4 estimated achieved-state comparison
remain separate; the selected intended design is evaluated anew by WP4.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from .contracts import RunInputs, Gradient
from .store import RunStore
from .wp3_search import open_search, recompute_search
from .wp4_feedback import starting_inputs, _replace_design, run, save, reopen
from .wp4_journal import initialize, read_manifest, recover, resume
from .wp5_service import journal_status


def _hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",",":"), allow_nan=False).encode()).hexdigest()


def qualified_handoff_source(ledger_path, index, *, elements, mass_limit):
    """Validate original WP3 ledger and exact typed design, reject invalid cases."""
    ledger_path = Path(ledger_path)
    ledger = open_search(ledger_path)
    if type(index) is not int or index < 0 or index >= len(ledger["proposals"]):
        raise ValueError("Invalid WP3 candidate index")
    item = ledger["proposals"][index]
    if item["status"] != "complete" or item.get("qualified") is not True:
        raise ValueError("WP3 candidate not complete and numerically qualified")
    if ledger["config"]["elements"] != elements or ledger["config"]["mass_limit"] != mass_limit:
        raise ValueError("WP3 and WP4 mesh/mass scenario must match; no implicit rescaling")
    run_record = RunStore(ledger_path.parent / "run-store").load(item["run_id"])
    original = run_record.inputs
    design = original.design
    if not isinstance(design.architecture, Gradient):
        raise ValueError("WP4 candidate handoff presently supports gradient only")
    if any({x.material_id for x in knot.composition.fractions} != {"scenario_A", "scenario_B"}
           for knot in design.architecture.knots):
        raise ValueError("Selected gradient must use precisely scenario_A and scenario_B")
    baseline = starting_inputs(elements=elements, mass_limit=mass_limit)
    for label in ("scenario_A", "scenario_B"):
        first = next(m for m in original.materials if m.id == label)
        second = next(m for m in baseline.materials if m.id == label)
        if first != second:
            raise ValueError("Different WP3 and WP4 material property records")
    if original.brief.hot_boundary != baseline.brief.hot_boundary or original.brief.cold_boundary != baseline.brief.cold_boundary or original.brief.thickness != baseline.brief.thickness:
        raise ValueError("Incompatible thermal duty; no silent scientific substitution")
    if original.brief.objectives != baseline.brief.objectives or original.brief.constraints != baseline.brief.constraints:
        raise ValueError("Incompatible objectives or constraints")
    if original.solver != baseline.solver:
        raise ValueError("Incompatible numerical solver")
    # Reconstruct WP4's bounded two-constituent context, not a false
    # continuation of the WP3 three-constituent catalogue evaluation.
    mapped = _replace_design(baseline, design)
    evidence = {
        "schema": "wp7-ir01-handoff-v1",
        "source_ledger": str(ledger_path),
        "source_ledger_sha256": hashlib.sha256(ledger_path.read_bytes()).hexdigest(),
        "source_candidate_index": index,
        "source_run_id": item["run_id"],
        "source_input_hash": original.content_hash,
        "source_evaluation_hash": run_record.evaluation.content_hash,
        "source_design_hash": design.content_hash,
        "wp4_recontextualised_baseline_hash": mapped.content_hash,
        "scientific_status": "new WP4 estimated-state synthetic scenario; NOT pooled with WP3 intended-state Pareto",
        "measured_evidence": None,
    }
    return mapped, evidence


def _handoff_path(target):
    return Path(str(target) + ".handoff.json")


def _save_handoff(target, provenance):
    path = _handoff_path(target)
    if path.exists():
        raise FileExistsError("Handoff provenance already exists")
    path.write_text(json.dumps({"provenance": provenance, "sha256": _hash(provenance)},
                               indent=2, sort_keys=True) + "\n")
    return path


def verify_handoff(target):
    """Verify source identity, complete WP3 lineage, WP4 dossier and candidate."""
    path = _handoff_path(target)
    obj = json.loads(path.read_text())
    data = obj["provenance"]
    if _hash(data) != obj["sha256"]:
        raise ValueError("Handoff manifest integrity mismatch")
    wp4 = reopen(target)
    base = RunInputs.model_validate_json(json.dumps(wp4["baseline_intended_inputs"]))
    candidate, source = qualified_handoff_source(
        data["source_ledger"], data["source_candidate_index"],
        elements=wp4["config"]["elements"], mass_limit=wp4["config"]["mass_limit"])
    for key in ("source_ledger_sha256","source_run_id","source_input_hash",
                "source_evaluation_hash","source_design_hash",
                "wp4_recontextualised_baseline_hash"):
        if data[key] != source[key]:
            raise ValueError("Handoff source changed: " + key)
    if base.content_hash != candidate.content_hash:
        raise ValueError("WP4 baseline does not match WP3 selected intended design")
    return {"handoff": data, "wp4_records": len(wp4["records"]),
            "measured_evidence": None, "verified": True}


def execute_handoff(ledger_path, index, output, *, elements=4096, mass_limit=31.,
                    layer=.005, feed=.25, budget=4, feedback=True):
    output = Path(output)
    if output.exists() or _handoff_path(output).exists():
        raise FileExistsError("Handoff output or provenance already exists")
    base, evidence = qualified_handoff_source(ledger_path, index, elements=elements, mass_limit=mass_limit)
    result = run(elements=elements, mass_limit=mass_limit, layer=layer, feed=feed,
                 budget=budget, feedback=feedback, base_inputs=base)
    save(output, result)
    _save_handoff(output, evidence)
    verify_handoff(output)
    return result


def start_checkpointed_handoff(ledger_path, index, journal_path, *, elements=4096,
                               mass_limit=31., layer=.005, feed=.25, budget=4,
                               feedback=True, cancel_after=1):
    """Cooperative cancellation at candidate boundaries, retaining original journal."""
    journal_path = Path(journal_path)
    if type(cancel_after) is not int or cancel_after < 0 or cancel_after >= budget:
        raise ValueError("Cancellation checkpoint must be in [0,budget)")
    if journal_path.exists() or _handoff_path(journal_path).exists():
        raise FileExistsError("Checkpoint journal/provenance already exists")
    base, evidence = qualified_handoff_source(ledger_path, index, elements=elements, mass_limit=mass_limit)
    journal, base = initialize(journal_path, elements=elements, mass_limit=mass_limit,
        layer=layer, feed=feed, budget=budget, feedback=feedback, base_inputs=base)
    _save_handoff(journal_path, evidence)
    # The count is verified by the journal on each cancellation check.
    result = run(elements=elements, mass_limit=mass_limit, layer=layer, feed=feed,
        budget=budget, feedback=feedback, base_inputs=base,
        cancel_requested=lambda: journal.count() >= cancel_after,
        checkpoint=journal.checkpoint, attempt_event=journal.event)
    return {"stop_reason": result["stop_reason"], "completed": journal.count(),
            "journal": str(journal_path), "handoff": evidence}


def recover_checkpointed_handoff(journal_path, output):
    journal_path, output = Path(journal_path), Path(output)
    if output.exists() or _handoff_path(output).exists():
        raise FileExistsError("Recovered output already exists")
    document = json.loads(_handoff_path(journal_path).read_text())
    if _hash(document["provenance"]) != document["sha256"]:
        raise ValueError("Corrupt source handoff provenance")
    manifest = read_manifest(journal_path)
    expected, evidence = qualified_handoff_source(
        document["provenance"]["source_ledger"],
        document["provenance"]["source_candidate_index"],
        elements=manifest["config"]["elements"],
        mass_limit=manifest["config"]["mass_limit"])
    if expected.model_dump(mode="json") != manifest["baseline_intended_inputs"]:
        raise ValueError("Checkpoint baseline does not match selected original candidate")
    if evidence != document["provenance"]:
        raise ValueError("WP3 selection provenance has changed")
    result = resume(journal_path, output=output, **manifest["config"])
    _save_handoff(output, evidence)
    verify_handoff(output)
    return result
