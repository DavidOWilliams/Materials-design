"""Independent review: terminal checkpoints, event tampering, verification accounting."""
import copy,json
import pytest
import material_core.wp4_feedback as fb
from material_core.wp4_journal import initialize,resume,read_attempts

def _case(tmp_path,*,elements=4096,budget=4,feedback=True,alternate=False,stop_after=1,verify=False):
    from material_core.wp3_adapters import resolve_provider,ALTERNATE
    base=(resolve_provider(ALTERNATE,17,"explore",elements,31.).baseline()
          if alternate else None)
    path=tmp_path/("alternate.jsonl" if alternate else "default.jsonl")
    journal,base=initialize(path,elements=elements,budget=budget,feedback=feedback,base_inputs=base)
    calls=[]
    original=fb.evaluate
    def counted(inputs):
        calls.append(inputs.evaluation_target)
        return original(inputs)
    fb.evaluate=counted
    def interrupt(rows):
        journal.checkpoint(rows)
        if len(rows)==stop_after: raise RuntimeError("after checkpoint")
    try:
        with pytest.raises(RuntimeError,match="after checkpoint"):
            fb.run(elements=elements,budget=budget,feedback=feedback,base_inputs=base,
                checkpoint=interrupt,attempt_event=journal.event)
        prior=len(calls)
        output=tmp_path/"resumed.json"
        record=resume(path,elements=elements,budget=budget,feedback=feedback,output=output,verify=verify)
    finally:
        fb.evaluate=original
    assert len(calls)==record["accounting"]["completed_evaluations"]+record["accounting"]["verification_evaluations"]
    assert record["accounting"]["reused_candidates"]==stop_after
    assert fb.reopen(output)["accounting"]==record["accounting"]
    return record,output,prior,len(calls)

@pytest.mark.parametrize("alternate", [False,True])
def test_final_feasible_checkpoint_no_recompute(tmp_path,alternate):
    if alternate:
        # Alternate synthetic duty terminates after two candidates.
        record,out,prior,total=_case(tmp_path,alternate=True,stop_after=2)
    else:
        record,out,prior,total=_case(tmp_path,stop_after=3)
    assert record["stop_reason"]=="qualified_scenario_feasible"
    assert total==prior
    assert fb.recompute(out)["status"]=="passed"

def test_intermediate_checkpoint_reuses_completed(tmp_path):
    record,out,prior,total=_case(tmp_path,stop_after=1)
    assert total>prior
    assert total==len(record["records"])+1

def test_budget_terminal_checkpoint_no_recompute(tmp_path):
    record,out,prior,total=_case(tmp_path,budget=1,feedback=True,stop_after=1)
    assert record["stop_reason"]=="evaluation_budget_exhausted"
    assert total==prior

def test_feedback_disabled_terminal_checkpoint_no_recompute(tmp_path):
    record,out,prior,total=_case(tmp_path,budget=4,feedback=False,stop_after=1)
    assert record["stop_reason"]=="feedback_disabled"
    assert total==prior

def _reseal(path,record):
    path.write_text(json.dumps(dict(record=record,record_sha256=fb._digest(record))))
    return path

@pytest.mark.parametrize("mutate",[
    lambda r:r["accounting"].update(reused_candidates=-1),
    lambda r:r["attempt_events"].__setitem__(next(i for i,e in enumerate(r["attempt_events"])
        if e["kind"]=="candidate_evaluation_completed"),dict(
        r["attempt_events"][next(i for i,e in enumerate(r["attempt_events"]) if e["kind"]=="candidate_evaluation_completed")],
        detail=999)),
    lambda r:r["attempt_events"][0].update(kind="candidate_evaluation_completed"),
    lambda r:r["attempt_events"][1].update(_event_sequence=999),
    lambda r:r["attempt_events"][0].update(detail="altered"),
    lambda r:r["accounting"].update(verification_evaluations=-1),
])
def test_resealed_recovery_mutations_rejected(tmp_path,mutate):
    record,out,_,_=_case(tmp_path,stop_after=1)
    forged=copy.deepcopy(record)
    mutate(forged)
    with pytest.raises(ValueError):
        fb.reopen(_reseal(tmp_path/"forged.json",forged))
    with pytest.raises(ValueError):
        fb.recompute(tmp_path/"forged.json")

def test_verify_return_and_persisted_equal(tmp_path):
    record,out,prior,total=_case(tmp_path,stop_after=1,verify=True)
    assert record["accounting"]["verification_evaluations"]==len(record["records"])+1
    assert fb.reopen(out)["accounting"]==record["accounting"]
    assert fb.reopen(out)["verification"]==record["verification"]
    assert fb.recompute(out)["status"]=="passed"

def test_failed_verification_does_not_claim_success(tmp_path,monkeypatch):
    from material_core.wp4_journal import initialize,resume
    path=tmp_path/"failed-verification.jsonl"
    journal,base=initialize(path,elements=256,budget=4)
    def stop(rows):
        journal.checkpoint(rows)
        raise RuntimeError("interrupted")
    with pytest.raises(RuntimeError):
        fb.run(elements=256,budget=4,base_inputs=base,
            checkpoint=stop,attempt_event=journal.event)
    def fail(_):
        raise RuntimeError("injected verification failure")
    monkeypatch.setattr(fb,"recompute",fail)
    out=tmp_path/"verified.json"
    with pytest.raises(RuntimeError,match="verification failure"):
        resume(path,elements=256,budget=4,output=out,verify=True)
    assert not out.exists()
    assert not (tmp_path/"verified.json.verification-pending.tmp").exists()
