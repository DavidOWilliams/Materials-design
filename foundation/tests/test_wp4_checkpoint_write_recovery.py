"""R2 independent checkpoint-write interruption regressions."""
import pytest
import material_core.wp4_feedback as fb
from material_core.wp4_journal import initialize,resume,recover

@pytest.mark.parametrize("persisted_before_failure",[0,1,2])
def test_checkpoint_write_failure_retries_evaluation_and_reopens(tmp_path,monkeypatch,persisted_before_failure):
    path=tmp_path/"checkpoint.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    original=fb.evaluate
    calls=[]
    def evaluate(inputs):
        calls.append(inputs.evaluation_target)
        return original(inputs)
    monkeypatch.setattr(fb,"evaluate",evaluate)
    def checkpoint(rows):
        if len(rows)==persisted_before_failure+1:
            raise RuntimeError("checkpoint unavailable before write")
        journal.checkpoint(rows)
    with pytest.raises(RuntimeError,match="checkpoint unavailable"):
        fb.run(elements=256,budget=4,base_inputs=base,checkpoint=checkpoint,
               attempt_event=journal.event)
    before=len(calls)
    assert len(recover(path))==persisted_before_failure
    output=tmp_path/"recovered.json"
    result=resume(path,elements=256,budget=4,output=output)
    after=len(calls)
    assert after>before
    assert result["accounting"]["completed_evaluations"]==after
    assert result["accounting"]["reused_candidates"]==persisted_before_failure
    assert sum(e["kind"]=="checkpoint_failed" for e in result["attempt_events"])==1
    assert fb.reopen(output)["accounting"]==result["accounting"]
    assert fb.recompute(output)["status"]=="passed"

def test_final_feasible_checkpoint_write_failure(tmp_path,monkeypatch):
    path=tmp_path/"terminal.jsonl"
    journal,base=initialize(path,elements=4096,budget=4)
    original=fb.evaluate
    calls=[]
    def evaluate(inputs):
        calls.append(inputs.evaluation_target)
        return original(inputs)
    monkeypatch.setattr(fb,"evaluate",evaluate)
    def checkpoint(rows):
        if len(rows)==3:
            raise RuntimeError("final checkpoint unavailable")
        journal.checkpoint(rows)
    with pytest.raises(RuntimeError,match="final checkpoint"):
        fb.run(elements=4096,budget=4,base_inputs=base,checkpoint=checkpoint,
               attempt_event=journal.event)
    before=len(calls)
    result=resume(path,elements=4096,budget=4,output=tmp_path/"final.json")
    assert result["stop_reason"]=="qualified_scenario_feasible"
    assert len(calls)==before+1
    assert result["accounting"]["completed_evaluations"]==len(calls)
    assert result["accounting"]["reused_candidates"]==2
    assert fb.reopen(tmp_path/"final.json")["stop_reason"]=="qualified_scenario_feasible"
    assert fb.recompute(tmp_path/"final.json")["status"]=="passed"

def test_alternate_duty_checkpoint_write_failure_and_repeated_resume(tmp_path,monkeypatch):
    from material_core.wp3_adapters import resolve_provider,ALTERNATE
    path=tmp_path/"alternate.jsonl"
    base=resolve_provider(ALTERNATE,17,"explore",4096,31.).baseline()
    journal,base=initialize(path,elements=4096,budget=4,base_inputs=base)
    original=fb.evaluate
    calls=[]
    def evaluate(inputs):
        calls.append(inputs.evaluation_target)
        return original(inputs)
    monkeypatch.setattr(fb,"evaluate",evaluate)
    def checkpoint(rows):
        if len(rows)==2: raise RuntimeError("alternate checkpoint write failure")
        journal.checkpoint(rows)
    with pytest.raises(RuntimeError,match="alternate checkpoint"):
        fb.run(elements=4096,budget=4,base_inputs=base,checkpoint=checkpoint,
               attempt_event=journal.event)
    before=len(calls)
    first=resume(path,elements=4096,budget=4,output=tmp_path/"first.json")
    assert len(calls)==before+1
    assert first["accounting"]["completed_evaluations"]==len(calls)
    assert first["accounting"]["reused_candidates"]==1
    assert fb.reopen(tmp_path/"first.json")["accounting"]==first["accounting"]
    assert fb.recompute(tmp_path/"first.json")["status"]=="passed"
    before=len(calls)
    second=resume(path,elements=4096,budget=4,output=tmp_path/"second.json")
    assert len(calls)==before
    assert second["accounting"]["reused_candidates"]==len(first["records"])
    assert second["accounting"]["completed_evaluations"]==first["accounting"]["completed_evaluations"]
    assert fb.reopen(tmp_path/"second.json")["accounting"]==second["accounting"]
    assert fb.recompute(tmp_path/"second.json")["status"]=="passed"
