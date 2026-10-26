"""WP6 evaluation protocol smoke and negative boundary tests."""
import json
import pytest
from foundation.wp6.evaluate import run, CASES

def test_preregistered_cases():
    assert len(CASES)==9
    assert ("control_on",31.0,0.005,0.25,True,1) in CASES
    assert ("control_off",31.0,0.005,0.25,False,1) in CASES

@pytest.mark.parametrize("budget", [0,-1,True,False,1.5,"4",None])
def test_invalid_budget_does_not_create_files(tmp_path,budget):
    target=tmp_path/"absent"
    with pytest.raises(ValueError):
        run(target,budget=budget)
    assert not target.exists()

def test_immutable_output(tmp_path):
    target=tmp_path/"result"
    target.mkdir()
    with pytest.raises(FileExistsError):
        run(target)

def test_run_reopen_replay(tmp_path):
    result=run(tmp_path/"evaluation",elements=128,budget=2)
    assert len(result["cases"])==len(CASES)
    assert len(result['pairs'])==3
    assert all(p['causal_superiority_established'] is False for p in result['pairs'])
    assert next(x for x in result['cases'] if x['case']=='no_feasible')['feasible_candidates']==0
    heldout=next(x for x in result['cases'] if x['case']=='heldout_on')
    control=next(x for x in result['cases'] if x['case']=='control_on')
    assert heldout['brief_hash'] != control['brief_hash']
    assert all(x["status"]=="complete" for x in result["cases"]), result
    assert all(x["measured_evidence"] is None for x in result["cases"])
    assert all(x["manufacturing_validation"]=="not_established" for x in result["cases"])
    assert all(x["proposals"]<=2 for x in result["cases"])
    assert json.loads((tmp_path/"evaluation"/"report.json").read_text())["schema_version"]==1
