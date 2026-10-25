import pytest
import material_core.wp4_feedback as fb
from material_core.wp4_journal import initialize,resume,read_attempts

def test_failed_transform_is_not_counted_as_numerical_evaluation(tmp_path,monkeypatch):
    path=tmp_path/"transform.jsonl"
    journal,base=initialize(path,elements=4096,budget=4)
    original=fb.estimated_inputs
    def fail(*args):
        raise RuntimeError("synthetic transform failure")
    monkeypatch.setattr(fb,"estimated_inputs",fail)
    with pytest.raises(RuntimeError,match="transform failure"):
        fb.run(elements=4096,budget=4,base_inputs=base,
            checkpoint=journal.checkpoint,attempt_event=journal.event)
    events=read_attempts(path)
    assert sum(e["kind"]=="baseline_evaluation_completed" for e in events)==1
    assert sum(e["kind"]=="candidate_evaluation_started" for e in events)==0
    assert sum(e["kind"]=="transform_failed" for e in events)==1
    monkeypatch.setattr(fb,"estimated_inputs",original)
    result=resume(path,elements=4096,budget=4,output=tmp_path/"recovered.json")
    assert result["accounting"]["transform_failures"]==1
    assert result["accounting"]["completed_evaluations"]==len(result["records"])+1
    assert result["accounting"]["failed_evaluations"]==0

def test_resume_rejects_config_change_before_first_checkpoint(tmp_path):
    path=tmp_path/"early.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    with pytest.raises(ValueError,match="configuration mismatch"):
        resume(path,elements=256,budget=4,feed=.5)
    assert path.read_text()==""

def test_resume_after_baseline_before_first_candidate(tmp_path):
    path=tmp_path/"early.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    def fail(*args):
        raise RuntimeError("injected")
    original=fb.estimated_inputs
    fb.estimated_inputs=fail
    try:
        with pytest.raises(RuntimeError):
            fb.run(elements=256,budget=4,base_inputs=base,attempt_event=journal.event)
    finally:
        fb.estimated_inputs=original
    result=resume(path,elements=256,budget=4,output=tmp_path/"early-resumed.json")
    assert result["accounting"]["reused_candidates"]==0
    assert result["accounting"]["completed_evaluations"]==len(result["records"])+1
