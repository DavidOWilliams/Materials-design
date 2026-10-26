"""Append-only checkpoint journal for WP4 candidate artifacts.

Crash recovery is limited to last fully written record; no mid-kernel restart.
A single writer owns the file. This is not a transactional multi-writer store.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

class Journal:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if self.path.exists():
            raise FileExistsError("WP4 journal is immutable; use recover")
        with self.path.open("x",encoding="utf-8") as f:
            f.flush()
            os.fsync(f.fileno())
        self.previous="0"*64

    def event(self,kind,detail):
        """Durable event ledger in a separate sidecar file."""
        path=Path(str(self.path)+".attempts.jsonl")
        existing=read_attempts(self.path,missing_ok=True)
        previous=(existing[-1]["_event_sha256"] if existing else "0"*64)
        payload=dict(sequence=len(existing),previous=previous,kind=kind,detail=detail)
        event=dict(payload=payload,sha256=digest(payload))
        with path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(event,sort_keys=True)+"\n")
            f.flush()
            os.fsync(f.fileno())

    def checkpoint(self,records):
        if len(records)!=self.count()+1:
            raise ValueError("Checkpoint must append exactly one candidate")
        record=records[-1]
        payload=dict(sequence=len(records)-1,previous=self.previous,record=record)
        envelope=dict(payload=payload,sha256=digest(payload))
        line=json.dumps(envelope,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n"
        with self.path.open("a",encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
        self.previous=envelope["sha256"]

    def count(self):
        return len(recover(self.path))

def recover(path):
    path=Path(path)
    records=[]
    previous="0"*64
    with path.open("r",encoding="utf-8") as f:
        for line in f:
            if not line.endswith("\n"):
                raise ValueError("Truncated WP4 checkpoint record")
            envelope=json.loads(line)
            payload=envelope["payload"]
            if digest(payload)!=envelope["sha256"] or payload["previous"]!=previous:
                raise ValueError("Corrupt WP4 checkpoint chain")
            if payload["sequence"]!=len(records) or payload["record"]["index"]!=len(records):
                raise ValueError("WP4 checkpoint sequence mismatch")
            records.append(payload["record"])
            previous=envelope["sha256"]
    return records

def manifest_path(path):
    return Path(str(path)+".manifest.json")

def initialize(path, *, elements=4096,mass_limit=31.,layer=.005,feed=.25,budget=4,
               feedback=True,route="synthetic_ideal_planar_deposition",base_inputs=None,process_version=1):
    """Freeze source inputs and process identity before executing a solver."""
    from .wp4_feedback import starting_inputs,scenario,REVISION_ID,EVALUATOR_ID,VERSION
    from .wp4_registry import resolve
    base=base_inputs if base_inputs is not None else starting_inputs(elements,mass_limit)
    process=scenario(layer,feed,route,version=process_version)
    identity,_=resolve(process)
    config=dict(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
                budget=budget,feedback=feedback,route=route,process_version=process_version)
    if process_version != 1: config["process_version"] = process_version
    manifest=dict(schema_version=1,algorithm=VERSION,config=config,
                  baseline_intended_inputs=base.model_dump(mode="json"),
                  process=process.model_dump(mode="json"),
                  transformer_identity=identity,revision_identity=REVISION_ID,
                  evaluator_identity=EVALUATOR_ID)
    journal=Journal(path)
    mp=manifest_path(path)
    with mp.open("x",encoding="utf-8") as f:
        json.dump(dict(manifest=manifest,sha256=digest(manifest)),f,sort_keys=True)
        f.flush();os.fsync(f.fileno())
    return journal,base

def read_manifest(path):
    mp=manifest_path(path)
    if not mp.exists():
        raise ValueError("Legacy journal missing original configuration and baseline; exact continuation unavailable")
    obj=json.loads(mp.read_text())
    if digest(obj["manifest"])!=obj["sha256"]:
        raise ValueError("Corrupt recovery manifest")
    return obj["manifest"]

def read_attempts(path,missing_ok=False):
    sidecar=Path(str(path)+".attempts.jsonl")
    if not sidecar.exists():
        if missing_ok: return []
        raise ValueError("Missing durable attempt history; exact work accounting unavailable")
    events=[]
    previous="0"*64
    for line in sidecar.read_text().splitlines(keepends=True):
        if not line.endswith("\n"):
            raise ValueError("Truncated attempt event")
        envelope=json.loads(line)
        payload=envelope["payload"]
        if (digest(payload)!=envelope["sha256"] or payload["previous"]!=previous or
            payload["sequence"]!=len(events)):
            raise ValueError("Corrupt durable attempt event chain")
        events.append(dict(kind=payload["kind"],detail=payload["detail"],
                           _event_sha256=envelope["sha256"],_event_previous=payload["previous"],
                           _event_sequence=payload["sequence"]))
        previous=envelope["sha256"]
    return events

def resume(path, *, elements=4096,mass_limit=31.,layer=.005,feed=.25,budget=4,
           feedback=True,route="synthetic_ideal_planar_deposition",verify=False,
           output=None,process_version=1):
    """Continue from persisted completed candidates without numerical replay.

    Optional numerical verification is separate and explicitly counted.
    """
    from .wp4_feedback import run,reopen,save,_digest
    from .contracts import RunInputs
    path=Path(path)
    manifest=read_manifest(path)
    expected=dict(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
                  budget=budget,feedback=feedback,route=route)
    if process_version != 1: expected["process_version"] = process_version
    if manifest["config"]!=expected:
        raise ValueError("Resume configuration mismatch; original configuration is immutable")
    from .wp4_feedback import VERSION,REVISION_ID,EVALUATOR_ID
    from .wp4_registry import resolve
    from .contracts import ProcessScenario
    base=RunInputs.model_validate_json(json.dumps(manifest["baseline_intended_inputs"]))
    process=ProcessScenario.model_validate_json(json.dumps(manifest["process"]))
    if (manifest["algorithm"]!=VERSION or manifest["revision_identity"]!=REVISION_ID or
        manifest["evaluator_identity"]!=EVALUATOR_ID or
        manifest["transformer_identity"]!=resolve(process)[0]):
        raise ValueError("Unavailable recovery implementation identity")
    prior=recover(path)
    events=read_attempts(path)
    # A checkpointed candidate must have an observed completed evaluation.
    for i in range(len(prior)):
        if not any(e["kind"]=="candidate_evaluation_completed" and e["detail"]==i for e in events):
            raise ValueError("Historical completed candidate lacks durable evaluation event")
    if not any(e["kind"]=="baseline_evaluation_completed" for e in events):
        raise ValueError("Historical baseline lacks durable completion event")
    journal=object.__new__(Journal)
    journal.path=path
    journal.previous="0"*64
    if prior:
        with path.open(encoding="utf-8") as f:
            for line in f:
                journal.previous=json.loads(line)["sha256"]
    # Validate complete stored prefix with the same campaign invariants.
    # Reopening does not invoke numerical physics.
    if prior:
        from .wp4_feedback import _assemble
        from .contracts import Evaluation
        baseline_event=next((e for e in events if e["kind"]=="baseline_evaluation_completed"),None)
        if baseline_event is None or not isinstance(baseline_event["detail"],dict):
            raise ValueError("Missing persisted baseline evaluation; legacy journal cannot resume")
        baseline=Evaluation.model_validate_json(json.dumps(baseline_event["detail"]))
        from .wp4_feedback import _terminal_for_prefix
        stop=_terminal_for_prefix(base,prior,budget,feedback)
        provisional=_assemble(base,baseline,process,manifest["transformer_identity"],
             elements,mass_limit,layer,feed,budget,feedback,route,prior,stop or "cancelled")
        temp=Path(str(path)+".validation.tmp.json")
        temp.write_text(json.dumps(dict(record=provisional,record_sha256=_digest(provisional))))
        try: reopen(temp)
        finally: temp.unlink()
    else:
        baseline_event=next((e for e in events if e["kind"]=="baseline_evaluation_completed"),None)
        if baseline_event is None:
            raise ValueError("Interrupted baseline without persisted evaluation; exact resume unsupported")
        from .contracts import Evaluation
        baseline=Evaluation.model_validate_json(json.dumps(baseline_event["detail"]))
        from .wp4_feedback import _assemble
        provisional=_assemble(base,baseline,process,manifest["transformer_identity"],
            elements,mass_limit,layer,feed,budget,feedback,route,[],"cancelled")
    # Store baseline result in resume record; no numerical baseline recomputation.
    def checkpoint(rows):
        journal.checkpoint(rows)
    journal.event("continuation_started",dict(reused_candidates=len(prior),
        checkpoint_sha256=journal.previous))
    result=run(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,
        budget=budget,feedback=feedback,route=route,process_version=process_version,base_inputs=base,
        resume_record=provisional,checkpoint=checkpoint,attempt_event=journal.event)
    events=read_attempts(path)
    completed=sum(e["kind"] in ("baseline_evaluation_completed","candidate_evaluation_completed") for e in events)
    failed=sum(e["kind"] in ("baseline_evaluation_failed","candidate_evaluation_failed") for e in events)
    started=sum(e["kind"] in ("baseline_evaluation_started","candidate_evaluation_started") for e in events)
    result["accounting"]=dict(completed_evaluations=completed,failed_evaluations=failed,
        started_evaluations=started,unresolved_evaluation_starts=max(0,started-completed-failed),
        transform_attempts=sum(e["kind"]=="transform_started" for e in events),
        transform_failures=sum(e["kind"]=="transform_failed" for e in events),
        reused_candidates=len(prior),reused_baseline=True,
        verification_evaluations=0,unknown_historical_effort=False)
    result["cumulative_evaluations"]=completed+failed
    result["cumulative_attempts"]=started
    result["attempt_events"]=events
    if verify:
        if output is None:
            raise ValueError("Verification requires output dossier")
        from .wp4_feedback import recompute
        # Verification uses a separate ephemeral dossier; historical journal remains immutable.
        temp=Path(str(output)+".verification-pending.tmp")
        save(temp,result)
        try:
            recompute(temp)
        finally:
            temp.unlink()
        result["accounting"]["verification_evaluations"]=len(result["records"])+1
        result["verification"]=dict(status="passed",evaluations=len(result["records"])+1,
            method="separate numerical recomputation of baseline and achieved candidates")
    # Never report a successful continuation that cannot reopen its own evidence.
    from .wp4_feedback import _validate_recovery_evidence
    _validate_recovery_evidence(result)
    if output is not None:
        save(output,result)
        reopen(output)
    return result
