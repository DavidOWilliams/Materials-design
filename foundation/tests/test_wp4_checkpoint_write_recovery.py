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
