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
