"""Produce independently inspectable R2/R4 interruption and continuation artifacts."""
import json
from pathlib import Path
import material_core.wp4_feedback as feedback
from material_core.wp4_journal import initialize,resume
from material_core.wp3_adapters import resolve_provider,ALTERNATE

out=Path("/tmp/wp4-review")
out.mkdir(parents=True,exist_ok=True)
for name,base in (
    ("default",None),
    ("alternate",resolve_provider(ALTERNATE,17,"explore",4096,31.).baseline()),
):
    path=out/(name+".jsonl")
    journal,inputs=initialize(path,elements=4096,budget=4,base_inputs=base)
    original=feedback.evaluate
    calls=[]
    def counted(inp):
        calls.append(inp.evaluation_target)
        return original(inp)
    feedback.evaluate=counted
    def stop_after_first(rows):
        journal.checkpoint(rows)
        if len(rows)==1:
            raise RuntimeError("injected interruption after durable decision")
    try:
        try:
            feedback.run(elements=4096,budget=4,base_inputs=inputs,
                checkpoint=stop_after_first,attempt_event=journal.event)
        except RuntimeError as exc:
            if "injected interruption" not in str(exc): raise
        before=list(calls)
        record=resume(path,elements=4096,budget=4,output=out/(name+"-resumed.json"))
        after=list(calls)
    finally:
        feedback.evaluate=original
    from material_core.wp4_feedback import reopen,recompute
    reopened=reopen(out/(name+"-resumed.json"))
    replay=recompute(out/(name+"-resumed.json"))
    report=dict(name=name,before_calls=before,after_calls=after,
        additional_calls=after[len(before):],actual_total_calls=len(after),
        recorded_completed=record["accounting"]["completed_evaluations"],
        reused_candidates=record["accounting"]["reused_candidates"],
        baseline_duty=reopened["baseline_intended_inputs"]["brief"]["duty"],
        replay=replay)
    assert len(after)==record["accounting"]["completed_evaluations"]
    assert record["accounting"]["reused_candidates"]==1
    assert len(after[len(before):])==len(record["records"])-1
    (out/(name+"-call-audit.json")).write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

# Independent review 2026-10-25: verify terminal feasible checkpoint and returned/persisted verification accounting.
for name,base,terminal in (
    ("default-terminal",None,3),
    ("alternate-terminal",resolve_provider(ALTERNATE,17,"explore",4096,31.).baseline(),2),
):
    path=out/(name+".jsonl")
    journal,inputs=initialize(path,elements=4096,budget=4,base_inputs=base)
    original=feedback.evaluate
    calls=[]
    def counted(inp):
        calls.append(inp.evaluation_target)
        return original(inp)
    feedback.evaluate=counted
    def stop_after_terminal(rows):
        journal.checkpoint(rows)
        if len(rows)==terminal:
            raise RuntimeError("terminal checkpoint persisted")
    try:
        try:
            feedback.run(elements=4096,budget=4,base_inputs=inputs,
                checkpoint=stop_after_terminal,attempt_event=journal.event)
        except RuntimeError as exc:
            if "terminal checkpoint persisted" not in str(exc): raise
        prior_calls=len(calls)
        result=resume(path,elements=4096,budget=4,verify=True,output=out/(name+"-verified.json"))
        total_calls=len(calls)
    finally:
        feedback.evaluate=original
    stored=reopen(out/(name+"-verified.json"))
    assert result["stop_reason"]=="qualified_scenario_feasible"
    assert result["accounting"]==stored["accounting"]
    assert result["accounting"]["completed_evaluations"]==prior_calls
    assert total_calls-prior_calls==result["accounting"]["verification_evaluations"]
    report=dict(name=name,continuation_calls=0,original_evaluator_calls=prior_calls,
        verification_calls=total_calls-prior_calls,recorded_verification=result["accounting"]["verification_evaluations"],
        returned_equals_persisted=result["accounting"]==stored["accounting"])
    (out/(name+"-verification-audit.json")).write_text(json.dumps(report,indent=2))
    print(json.dumps(report))

# R2 final checkpoint-write failure evidence: completed solver work without durable candidate.
for name,base,fail_at in (
    ("default-write-failure",None,1),
    ("alternate-write-failure",resolve_provider(ALTERNATE,17,"explore",4096,31.).baseline(),2),
    ("default-final-write-failure",None,3),
):
    path=out/(name+".jsonl")
    journal,inputs=initialize(path,elements=4096,budget=4,base_inputs=base)
    original=feedback.evaluate
    calls=[]
    def counted(inp):
        calls.append(inp.evaluation_target)
        return original(inp)
    feedback.evaluate=counted
    def fail_before_write(rows):
        if len(rows)==fail_at:
            raise RuntimeError("checkpoint unavailable before write")
        journal.checkpoint(rows)
    try:
        try:
            feedback.run(elements=4096,budget=4,base_inputs=inputs,
                checkpoint=fail_before_write,attempt_event=journal.event)
        except RuntimeError as exc:
            if "checkpoint unavailable before write" not in str(exc): raise
        before=len(calls)
        result=resume(path,elements=4096,budget=4,output=out/(name+"-resumed.json"))
        after=len(calls)
    finally:
        feedback.evaluate=original
    stored=feedback.reopen(out/(name+"-resumed.json"))
    assert stored["accounting"]==result["accounting"]
    assert result["accounting"]["completed_evaluations"]==after
    assert result["accounting"]["reused_candidates"]==fail_at-1
    assert after>before
    audit=dict(name=name,actual_before=before,actual_additional=after-before,
        actual_total=after,recorded_completed=result["accounting"]["completed_evaluations"],
        reused_checkpoints=result["accounting"]["reused_candidates"],
        repeated_evaluations=1,failed_checkpoint_events=sum(
            e["kind"]=="checkpoint_failed" for e in result["attempt_events"]))
    (out/(name+"-audit.json")).write_text(json.dumps(audit,indent=2))
    print(json.dumps(audit))
