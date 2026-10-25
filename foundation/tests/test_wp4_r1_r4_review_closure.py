"""Independent reviewer R1-R4 regression challenges."""
import json
import re
import pytest
from material_core.wp4_feedback import run,save,reopen,_digest
from material_core.wp4_export import export
from material_core.wp4_alternate import alternate_duty
from material_core.wp4_journal import Journal,resume,recover,read_attempts

def test_r1_resealed_three_candidate_feedback_disabled_is_rejected(tmp_path):
    dossier=run(elements=4096,budget=4)
    assert len(dossier["records"])==3
    dossier["config"]["feedback"]=False
    dossier["stop_reason"]="feedback_disabled"
    path=tmp_path/"contradictory.json"
    path.write_text(json.dumps(dict(record=dossier,record_sha256=_digest(dossier))))
    with pytest.raises(ValueError,match="Feedback-disabled"):
        reopen(path)

def test_r2_cumulative_work_and_failed_attempts_durable(tmp_path):
    path=tmp_path/"interrupted.jsonl"
    journal=Journal(path)
    def fail(rows):
        journal.checkpoint(rows)
        if len(rows)==2: raise RuntimeError("simulated crash")
    with pytest.raises(RuntimeError):
        run(elements=4096,budget=4,checkpoint=fail,attempt_event=journal.event)
    assert len(recover(path))==2
    resumed=resume(path,elements=4096,budget=4)
    assert resumed["evaluations"]==4
    assert resumed["cumulative_evaluations"]==7 # first baseline+2, second baseline+3
    assert resumed["replayed_evaluations"]==3
    assert len([e for e in read_attempts(path) if e["kind"]=="candidate_completed"])==5

def test_r2_failed_candidate_attempt_is_durable(tmp_path):
    path=tmp_path/"fail.jsonl"
    journal=Journal(path)
    def broken(rows):
        raise RuntimeError("checkpoint write failed")
    with pytest.raises(RuntimeError):
        run(elements=256,budget=1,checkpoint=broken,attempt_event=journal.event)
    events=read_attempts(path)
    assert any(e["kind"]=="candidate_started" for e in events)
    assert any(e["kind"]=="candidate_completed" for e in events)
    assert any(e["kind"]=="checkpoint_failed" for e in events)

def test_r3_export_contains_real_sha256(tmp_path):
    record=run(elements=256,budget=1)
    p=tmp_path/"export.json"
    save(p,record)
    result=export(p)
    assert re.fullmatch(r"[0-9a-f]{64}",result["intended_baseline_hash"])
    assert result["intended_baseline_hash"]==record["records"][0]["intended_hash"]

def test_r4_alternate_uses_shared_campaign_and_is_replayable(tmp_path):
    alternate=alternate_duty(elements=4096,budget=4)
    campaign=alternate["campaign"]
    assert campaign["baseline_intended_inputs"]["brief"]["duty"]==alternate["duty"]
    assert campaign["records"][0]["estimated_inputs"]["evaluation_target"]=="estimated"
    assert campaign["proposals"]==len(campaign["records"])
    path=tmp_path/"alternate.json"
    save(path,campaign)
    assert reopen(path)["stop_reason"]==campaign["stop_reason"]
