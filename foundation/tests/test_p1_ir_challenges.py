"""Adversarial runtime requirements P1-IR-02 — expected results are assertions.

All cases are supplementary challenges; never become confirmatory observations.
"""
import copy
import json
from unittest.mock import patch

import pytest
import material_core.p1_comparator as p1
from material_core.p1_comparator import execute, compare, score_saved, audit_record
from foundation.p1.analysis import feasible_hypervolume

def trial(tmp_path, feedback=True, limit=31., budget=3):
    path=tmp_path/"trial.json"
    record=execute(seed=17,budget=budget,feedback=feedback,output=path,
                   elements=32,mass_limit=limit)
    return path,record

# IR-02.1: impossible cap never manufactures a feasible score.
def test_01_impossible_mass_cap_yields_no_feasible(tmp_path):
    path,record=trial(tmp_path,limit=10.)
    result=score_saved(path)
    assert len(record["rows"])==3
    assert not any(r["feasible"] for r in result["results"])
    assert feasible_hypervolume(result["results"])==0.

# IR-02.2: injected process transformer failure is recorded, not cached or omitted.
def test_02_injected_transform_failure_charged(tmp_path):
    real=p1.estimated_inputs
    with patch.object(p1,"estimated_inputs",side_effect=[ValueError("injected WP4"),real(p1._candidate(p1.resolve_provider(p1.DEFAULT,17,"sampling",32,31.),1)[1],p1.scenario())]):
        path,record=trial(tmp_path,budget=2)
    assert [r["status"] for r in record["rows"]]==["transform_failed","complete"]
    assert record["accounting"]["failed_transformations"]==1
    assert record["accounting"]["proposals"]==2
    assert record["stop_reason"]=="proposal_budget_exhausted"

# IR-02.3: solver exception remains a failed charged candidate.
def test_03_injected_numerical_failure_charged(tmp_path):
    real=p1.evaluate
    attempts=[0]
    def evaluator(value):
        attempts[0]+=1
        if attempts[0]==1: raise RuntimeError("injected WP2")
        return real(value)
    with patch.object(p1,"evaluate",side_effect=evaluator):
        _,record=trial(tmp_path,budget=2)
    assert [r["status"] for r in record["rows"]]==["evaluation_failed","complete"]
    assert record["accounting"]["failed_evaluations"]==1
    assert record["accounting"]["cache_misses"]==2

# IR-02.4: forged missing or nonfinite objective values cannot pass final scoring.
@pytest.mark.parametrize("invalid",[None,"INVALID",float("nan")])
def test_04_bad_objective_cannot_pass_replay(tmp_path,invalid):
    path,_=trial(tmp_path)
    row=json.loads(path.read_text())
    row["rows"][0]["objectives"]["areal_mass"]=invalid
    path.write_text(json.dumps(row))
    with pytest.raises((ValueError,TypeError)):
        score_saved(path)

# IR-02.5: missing/truncated evidence must be rejected.
def test_05_truncated_evidence_fails_closed(tmp_path):
    path,_=trial(tmp_path)
    data=json.loads(path.read_text())
    data["rows"].pop()
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        score_saved(path)

# IR-02.6: config digest mismatch rejects before any numerical replay.
def test_06_configuration_identity_mismatch(tmp_path):
    path,_=trial(tmp_path)
    data=json.loads(path.read_text())
    data["config"]["seed"]+=1
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="identity"):
        score_saved(path)

# IR-02.7: cache poisoning or invented hit is prohibited.
def test_07_cache_poisoning_rejected(tmp_path):
    path,_=trial(tmp_path)
    data=json.loads(path.read_text())
    data["accounting"]["cache_hits"]=1
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="cache_hits"):
        score_saved(path)

# IR-02.8: restart journal should not repeat saved prior candidates.
def test_08_interrupted_checkpoint_resume_preserves_prior_work(tmp_path):
    from unittest.mock import patch
    path=tmp_path/"interrupted.json"
    original=p1._candidate
    def stop(provider,index):
        if index==2: raise KeyboardInterrupt("simulated interruption")
        return original(provider,index)
    with patch.object(p1,"_candidate",side_effect=stop):
        with pytest.raises(KeyboardInterrupt):
            execute(seed=17,budget=4,feedback=True,output=path,elements=32)
    checkpoint=json.loads((tmp_path/"interrupted.json.checkpoint.json").read_text())["record"]
    result=execute(seed=17,budget=4,feedback=True,output=path,elements=32)
    assert result["rows"][:2]==checkpoint["rows"]
    assert result["accounting"]["proposals"]==4
    assert result["stop_reason"]=="proposal_budget_exhausted"

# IR-02.9: corrupt or negative CPU counters fail, not silently normalised.
@pytest.mark.parametrize("field,value",[("numerical_cpu_ns",-1),("feedback_cpu_ns",1.5)])
def test_09_invalid_cpu_counter_rejected(tmp_path,field,value):
    path,_=trial(tmp_path)
    data=json.loads(path.read_text())
    data["rows"][0][field]=value
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="CPU"):
        score_saved(path)

# IR-02.10: blind control has no revision or feedback calculations.
def test_10_feedback_information_isolation(tmp_path):
    path,record=trial(tmp_path,feedback=False,limit=10.)
    assert all(not r["revision_applied"] and not r.get("revision_attempted",False)
               and r["feedback_cpu_ns"]==0 for r in record["rows"])
    assert record["accounting"]["feedback_calculations"]==0
    assert score_saved(path)["scoring_evaluations"]==3

# IR-02.11: no violation is negative-control for WP4's correction rule.
def test_11_no_violation_identity_of_feedback_treatment(tmp_path):
    path,record=trial(tmp_path,feedback=True,limit=999.)
    assert all(not r["revision_applied"] for r in record["rows"])
    assert all(not r["revision_attempted"] for r in record["rows"][1:])
    assert record["accounting"]["proposals"]==3

# IR-02.12: terminal reason only after actual proposal budget exhaustion.
def test_12_exact_budget_exhaustion(tmp_path):
    path,record=trial(tmp_path,budget=2)
    assert record["stop_reason"]=="proposal_budget_exhausted"
    assert record["accounting"]["proposals"]==len(record["rows"])==2
    forged=copy.deepcopy(record)
    forged["rows"].pop()
    with pytest.raises(ValueError,match="budget exhaustion"):
        audit_record(forged)
