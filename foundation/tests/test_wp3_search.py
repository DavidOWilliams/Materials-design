"""WP3 mixed search functional and challenge tests over genuine WP2 evaluations."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from material_core.wp3_search import run_search,open_search,compare_paired


def test_mixed_architectures_candidates_reopen_and_replay(tmp_path):
    path=tmp_path/"run.json"
    result=run_search(path,seed=11,budget=9,elements=256)
    assert result["stop_reason"]=="evaluation_budget_exhausted"
    assert len(result["proposals"])==9
    assert {p["proposal"]["architecture"] for p in result["proposals"]}=={
        "homogeneous","layered","gradient"}
    assert len({tuple(p["proposal"]["pair"]) for p in result["proposals"]})>=3
    assert result["unique_evaluations"]==9
    assert result["nominal_kernel_solves"]==9
    assert result["refinement_kernel_solves"]==9
    assert all(p["manufacturing_feasibility"]=="unknown" for p in result["proposals"])
    assert all(p["evidence_maturity"]=="synthetic" for p in result["proposals"])
    assert open_search(path)==result
    env=dict(os.environ)
    env["PYTHONPATH"]=str(Path(__file__).resolve().parents[1])+os.pathsep+env.get("PYTHONPATH","")
    process=subprocess.run([sys.executable,"-m","material_core.wp3_search",
             "--ledger",str(path),"--reopen"],check=True,text=True,
             capture_output=True,env=env)
    assert json.loads(process.stdout)==result


def test_cancel_resume_and_incompatible_config(tmp_path):
    path=tmp_path/"cancel.json"
    result=run_search(path,seed=7,budget=3,elements=256,cancel_requested=lambda:True)
    assert result["stop_reason"]=="cancelled"
    assert result["proposals"]==[]
    restored=run_search(path,seed=7,budget=3,elements=256,resume=True)
    assert len(restored["proposals"])==3
    assert restored["stop_reason"]=="evaluation_budget_exhausted"
    with pytest.raises(ValueError,match="different campaign"):
        run_search(path,seed=8,budget=3,elements=256,resume=True)


def test_changed_hard_constraint_and_no_solution(tmp_path):
    standard=run_search(tmp_path/"normal.json",seed=5,budget=3,elements=256,mass_limit=31.)
    impossible=run_search(tmp_path/"impossible.json",seed=5,budget=3,elements=256,mass_limit=1.)
    assert any(p["qualified"] for p in standard["proposals"])
    assert not any(p["qualified"] for p in impossible["proposals"])
    assert impossible["qualified_comparison"]["pareto_ids"]==[]
    assert all(p["hard_constraint_feasibility"]=="infeasible" for p in impossible["proposals"])


def test_equal_budget_paired_sampling(tmp_path):
    result=compare_paired(tmp_path/"paired",seeds=(11,23),budget=3,elements=256)
    assert len(result["pairs"])==2
    for row in result["pairs"]:
        assert row["explore"]["kernel_solves"]<=6
        assert row["sampling"]["kernel_solves"]<=6
        assert row["explore"]["unique_evaluations"]<=3
        assert row["sampling"]["unique_evaluations"]<=3
    assert (tmp_path/"paired"/"comparison.json").exists()


def test_search_rejects_invalid_inputs_and_corruption(tmp_path):
    for kwargs in ({"seed":True},{"budget":0},{"elements":True},
                   {"mass_limit":-1},{"method":"unknown"}):
        with pytest.raises(ValueError):
            run_search(tmp_path/"invalid.json",**kwargs)
    path=tmp_path/"good.json"
    run_search(path,seed=2,budget=1,elements=256)
    raw=json.loads(path.read_text())
    raw["config"]["mass_limit"]=200.
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="configuration changed"):
        open_search(path)
