import json
import pytest
from material_core.wp4_feedback import run
from material_core.wp4_journal import Journal,recover,resume,digest

def test_resume_recomputes_prefix_and_appends(tmp_path):
    path=tmp_path/"resume.jsonl"
    journal=Journal(path)
    def interrupt(rows):
        journal.checkpoint(rows)
        if len(rows)==1: raise RuntimeError("stop after durable candidate")
    with pytest.raises(RuntimeError):
        run(elements=256,budget=4,checkpoint=interrupt)
    assert len(recover(path))==1
    result=resume(path,elements=256,budget=4)
    assert len(recover(path))==len(result["records"])
    assert [digest(x) for x in recover(path)]==[digest(x) for x in result["records"]]

def test_resume_rejects_changed_process_without_rewriting(tmp_path):
    path=tmp_path/"resume.jsonl"
    journal=Journal(path)
    run(elements=256,budget=1,checkpoint=journal.checkpoint)
    original=path.read_bytes()
    with pytest.raises(ValueError,match="prefix differs"):
        resume(path,elements=256,budget=4,feed=.5)
    assert path.read_bytes()==original
