import pytest
from material_core.wp4_feedback import run,reopen
from material_core.wp4_journal import initialize,recover,resume,read_attempts

def test_resume_reuses_completed_numerical_work(tmp_path):
    path=tmp_path/"resume.jsonl"
    journal,base=initialize(path,elements=4096,budget=4)
    def interrupt(rows):
        journal.checkpoint(rows)
        if len(rows)==2: raise RuntimeError("interruption")
    with pytest.raises(RuntimeError):
        run(elements=4096,budget=4,base_inputs=base,checkpoint=interrupt,attempt_event=journal.event)
    assert len(recover(path))==2
    output=tmp_path/"resumed.json"
    result=resume(path,elements=4096,budget=4,output=output)
    assert len(recover(path))==3
    assert result["accounting"]["reused_candidates"]==2
    assert result["accounting"]["completed_evaluations"]==4
    assert result["accounting"]["verification_evaluations"]==0
    assert result["cumulative_evaluations"]==4
    assert reopen(output)["cumulative_evaluations"]==4

def test_resume_rejects_changed_process_without_rewriting(tmp_path):
    path=tmp_path/"resume.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    run(elements=256,budget=4,base_inputs=base,checkpoint=journal.checkpoint,attempt_event=journal.event)
    original=path.read_bytes()
    with pytest.raises(ValueError,match="configuration mismatch"):
        resume(path,elements=256,budget=4,feed=.5)
    assert path.read_bytes()==original

def test_missing_legacy_manifest_rejected(tmp_path):
    path=tmp_path/"legacy.jsonl"
    path.write_text("")
    with pytest.raises(ValueError,match="Legacy journal"):
        resume(path,elements=256)
