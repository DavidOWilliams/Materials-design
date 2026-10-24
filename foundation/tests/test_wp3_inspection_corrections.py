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
    assert recompute_search(path)["recomputed"]==1
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
