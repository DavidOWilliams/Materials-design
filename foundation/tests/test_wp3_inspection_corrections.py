"""Independent WP3 inspection corrections: attempts, interruption, derived evidence."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from material_core.wp2_numerical import evaluate
from material_core.wp3_search import run_search, open_search, recompute_search


def _fault(inputs):
    evaluate(inputs)
    raise KeyboardInterrupt("after WP2 evaluation before persistence")


def test_interrupt_after_wp2_numerical_work_then_resume(tmp_path):
    path=tmp_path/"interrupted.json"
    with pytest.raises(KeyboardInterrupt):
        run_search(path,seed=7,budget=2,elements=256,
            evaluation_adapter=_fault,evaluator_identity="fault-wrapper-v1")
    pending=open_search(path)
    assert pending["evaluation_attempts"]==1
    assert pending["unique_evaluations"]==1
    assert pending["uncertain_evaluation_attempts"]==1
    assert pending["kernel_solve_count_uncertain"] is True
    result=run_search(path,seed=7,budget=2,elements=256,resume=True,
        evaluation_adapter=evaluate,evaluator_identity="fault-wrapper-v1")
    assert [p["status"] for p in result["proposals"]]==["failed","complete"]
    assert result["evaluation_attempts"]==2
    assert result["unique_evaluations"]==2
    assert result["successful_evaluations"]==1
    assert result["failed_attempts"]==1
    assert result["nominal_kernel_solves"]==1
    assert result["refinement_kernel_solves"]==1
    assert result["confirmed_numerical_solves"]==2
    assert result["uncertain_evaluation_attempts"]==1
    assert result["kernel_solve_count_uncertain"] is True
    assert open_search(path)==result
    with pytest.raises(ValueError,match="Unavailable evaluator"):
        recompute_search(path)
    assert result["proposals"][1]["manufacturing_feasibility"]=="unknown"


def test_subprocess_hard_exit_after_real_wp2_before_result_store(tmp_path):
    path=tmp_path/"child.json"
    env=dict(os.environ)
    env["PYTHONPATH"]=str(Path(__file__).resolve().parents[1])+os.pathsep+env.get("PYTHONPATH","")
    code="""import os,sys
from material_core.wp2_numerical import evaluate
from material_core.wp3_search import run_search
def crash(inputs):
    evaluate(inputs)
    os._exit(57)
run_search(sys.argv[1],seed=21,budget=2,elements=256,
    evaluation_adapter=crash,evaluator_identity="subprocess-crash-v1")
"""
    child=subprocess.run([sys.executable,"-c",code,str(path)],env=env)
    assert child.returncode==57
    assert open_search(path)["evaluation_attempts"]==1
    out=run_search(path,seed=21,budget=2,elements=256,resume=True,
        evaluation_adapter=evaluate,evaluator_identity="subprocess-crash-v1")
    assert [p["status"] for p in out["proposals"]]==["failed","complete"]
    assert out["evaluation_attempts"]==2
    assert out["confirmed_numerical_solves"]==2
    assert out["kernel_solve_count_uncertain"]


@pytest.mark.parametrize("field,bad",[
    ("unique_evaluations",999),
    ("evaluation_attempts",999),
    ("successful_evaluations",999),
    ("nominal_kernel_solves",999),
    ("confirmed_numerical_solves",999),
    ("cache_hits",999),
])
def test_tampered_counters_rejected(tmp_path,field,bad):
    path=tmp_path/"ledger.json"
    run_search(path,seed=7,budget=1,elements=256)
    raw=json.loads(path.read_text())
    raw[field]=bad
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="accounting mismatch"):
        open_search(path)


@pytest.mark.parametrize("name,bad",[
    ("objectives",{"areal_mass":-999}),
    ("constraints",{"mass_cap":"violated"}),
    ("manufacturing_feasibility","conditional"),
    ("numerical_quality","unresolved"),
    ("hard_constraint_feasibility","infeasible"),
    ("evidence_maturity","measured"),
    ("qualified",False),
])
def test_tampered_evaluation_derived_summary_rejected(tmp_path,name,bad):
    path=tmp_path/"ledger.json"
    run_search(path,seed=7,budget=1,elements=256)
    raw=json.loads(path.read_text())
    raw["proposals"][0][name]=bad
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="Persisted evaluation summary mismatch"):
        open_search(path)


def test_cancellation_before_evaluation_charges_zero(tmp_path):
    path=tmp_path/"cancel.json"
    out=run_search(path,seed=5,budget=2,elements=256,
        cancel_requested=lambda:True)
    assert out["evaluation_attempts"]==0
    assert out["confirmed_numerical_solves"]==0
    assert not out["kernel_solve_count_uncertain"]


def test_budget_is_total_proposal_slots_after_restart(tmp_path):
    path=tmp_path/"budget.json"
    with pytest.raises(KeyboardInterrupt):
        run_search(path,seed=7,budget=2,elements=256,
            evaluation_adapter=_fault,evaluator_identity="budget-wrapper-v1")
    done=run_search(path,seed=7,budget=2,elements=256,resume=True,
        evaluation_adapter=evaluate,evaluator_identity="budget-wrapper-v1")
    assert len(done["proposals"])==2
    assert done["stop_reason"]=="evaluation_budget_exhausted"
    with pytest.raises(ValueError,match="different campaign"):
        run_search(path,seed=7,budget=3,elements=256,resume=True,
            evaluation_adapter=evaluate,evaluator_identity="budget-wrapper-v1")


def test_after_result_persistence_before_ledger_update_recovers_success(tmp_path,monkeypatch):
    from material_core.store import RunStore
    path=tmp_path/"after-store.json"
    original=RunStore.finish
    once={"pending":True}
    def interrupt_after_commit(self,run_id,evaluation):
        original(self,run_id,evaluation)
        if once["pending"]:
            once["pending"]=False
            raise KeyboardInterrupt("after immutable commit")
    monkeypatch.setattr(RunStore,"finish",interrupt_after_commit)
    with pytest.raises(KeyboardInterrupt):
        run_search(path,seed=4,budget=2,elements=256)
    monkeypatch.setattr(RunStore,"finish",original)
    ledger=open_search(path)
    assert ledger["proposals"][0]["status"]=="created"
    assert ledger["evaluation_attempts"]==1
    resumed=run_search(path,seed=4,budget=2,elements=256,resume=True)
    assert [p["status"] for p in resumed["proposals"]]==["complete","complete"]
    assert resumed["evaluation_attempts"]==2
    assert resumed["confirmed_numerical_solves"]==4
    assert resumed["failed_attempts"]==0
    assert not resumed["kernel_solve_count_uncertain"]


def test_ledger_write_interrupted_after_wp2_commit(tmp_path,monkeypatch):
    from material_core import wp3_search as search
    path=tmp_path/"write.json"
    real=search._write_ledger
    triggered={"flag":False}
    def write_fault(path,ledger):
        if (not triggered["flag"] and ledger["proposals"]
                and ledger["proposals"][0]["status"]=="complete"):
            triggered["flag"]=True
            raise KeyboardInterrupt("ledger write before atomic replacement")
        return real(path,ledger)
    monkeypatch.setattr(search,"_write_ledger",write_fault)
    with pytest.raises(KeyboardInterrupt):
        run_search(path,seed=4,budget=2,elements=256)
    monkeypatch.setattr(search,"_write_ledger",real)
    assert open_search(path)["evaluation_attempts"]==1
    restored=run_search(path,seed=4,budget=2,elements=256,resume=True)
    assert [p["status"] for p in restored["proposals"]]==["complete","complete"]
    assert restored["successful_evaluations"]==2


@pytest.mark.parametrize("field,bad",[
    ("architecture","homogeneous-not-real"),
    ("fraction",0.111),
    ("pair",["scenario_A","scenario_C"]),
])
def test_tampered_proposal_parameters_rejected(tmp_path,field,bad):
    path=tmp_path/"proposal.json"
    run_search(path,seed=4,budget=2,elements=256)
    record=json.loads(path.read_text())
    record["proposals"][1]["proposal"][field]=bad
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError,match="Proposal"):
        open_search(path)


def test_paired_export_rechecked_against_underlying_campaigns(tmp_path):
    from material_core.wp3_search import compare_paired,reopen_paired
    base=tmp_path/"paired"
    original=compare_paired(base,seeds=(11,),budget=2,elements=256)
    assert reopen_paired(base)==original
    path=base/"comparison.json"
    raw=json.loads(path.read_text())
    raw["pairs"][0]["explore"]["qualified_count"]=999
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="Paired summary"):
        reopen_paired(base)


def test_missing_required_attempt_accounting_rejected(tmp_path):
    path=tmp_path/"missing.json"
    run_search(path,seed=7,budget=1,elements=256)
    record=json.loads(path.read_text())
    del record["evaluation_attempts"]
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError,match="Campaign accounting mismatch"):
        open_search(path)
