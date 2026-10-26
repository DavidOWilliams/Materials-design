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

def test_corrupt_dossier_fails_closed(tmp_path):
    from material_core.wp5_service import execute, inspect, replay
    path=tmp_path/"corrupt.json"
    execute(path,elements=128,budget=2)
    original=path.read_text()
    path.write_text(original.replace("wp4-feedback-v1","tampered-algorithm",1))
    with pytest.raises((ValueError,KeyError)):
        inspect(path)
    with pytest.raises((ValueError,KeyError)):
        replay(path)

def test_cancelled_campaign_is_explicitly_unresolved(tmp_path):
    from material_core.wp5_service import execute, inspect, replay
    path=tmp_path/"cancelled.json"
    result=execute(path,elements=128,budget=4,cancel_requested=lambda: True)
    assert result["stop_reason"]=="cancelled"
    assert result["proposals"]==0
    assert inspect(path)["measured_evidence"] is None
    assert replay(path) is not None

def test_unsupported_physics_edit_rejected_without_files(tmp_path):
    from material_core.wp5_service import execute, prepared_inputs
    base=prepared_inputs(elements=128).brief.model_dump(mode="json")
    base["geometry"]={"unsupported":"change"}
    path=tmp_path/"invalid.json"
    with pytest.raises((ValueError,TypeError)):
        execute(path,elements=128,brief=base)
    assert not path.exists()

def test_no_improvement_or_budget_exhaustion_distinguished(tmp_path):
    from material_core.wp5_service import execute
    path=tmp_path/"saturated.json"
    result=execute(path,elements=128,mass_limit=1.0,budget=8)
    assert result["stop_reason"] in ("no_improvement_possible","evaluation_budget_exhausted")
    assert not any(x["feasible"] for x in result["records"])
    assert result["proposals"]<=8
