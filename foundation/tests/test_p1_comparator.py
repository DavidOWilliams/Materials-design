"""P1 focused regression: control continues after the first candidate.

Executed by .github/workflows/p1-equal-effort.yml. No physical validation.
"""
import json
import pytest
from material_core.p1_comparator import execute, compare, score_saved

def test_blind_comparator_continues_and_respects_budget(tmp_path):
    record = execute(seed=17, budget=3, feedback=False,
                     output=tmp_path/"control.json", elements=32)
    assert len(record["rows"]) == 3
    assert record["accounting"]["proposals"] == 3
    assert len({r["intended_hash"] for r in record["rows"]}) == 3
    assert all(r["revision_applied"] is False for r in record["rows"])
    assert all(r["status"] != "pending" for r in record["rows"])

def test_both_arms_are_budget_auditable_and_immutable(tmp_path):
    a=tmp_path/"a.json"
    b=tmp_path/"b.json"
    x=execute(seed=19,budget=3,feedback=False,output=a,elements=32)
    y=execute(seed=19,budget=3,feedback=True,output=b,elements=32)
    audit=compare(a,b)
    assert x["accounting"]["proposals"]==y["accounting"]["proposals"]==3
    assert audit["matched_numerical_work"] is True
    assert audit["matched_cpu_time"] is False
    assert audit["independent_scoring"] is False
    assert [r["proposal"] for r in x["rows"]]==[r["proposal"] for r in y["rows"]]
    with pytest.raises(FileExistsError):
        execute(seed=19,budget=3,feedback=False,output=a,elements=32)

def test_invalid_configuration_creates_nothing(tmp_path):
    output=tmp_path/"nested"/"bad.json"
    with pytest.raises(ValueError):
        execute(seed=1,budget=0,feedback=False,output=output)
    assert not output.parent.exists()

def test_mismatched_seed_rejected(tmp_path):
    a=tmp_path/"a.json"
    b=tmp_path/"b.json"
    execute(seed=1,budget=2,feedback=False,output=a,elements=32)
    execute(seed=2,budget=2,feedback=True,output=b,elements=32)
    with pytest.raises(ValueError,match="Incompatible"):
        compare(a,b)

def test_tampered_config_rejected(tmp_path):
    a=tmp_path/"a.json"
    b=tmp_path/"b.json"
    execute(seed=1,budget=2,feedback=False,output=a,elements=32)
    execute(seed=1,budget=2,feedback=True,output=b,elements=32)
    item=json.loads(a.read_text())
    item["config"]["budget"]=500
    a.write_text(json.dumps(item))
    with pytest.raises(ValueError,match="digest"):
        compare(a,b)

def test_density_feedback_triggers_with_wp3_three_material_catalogue(tmp_path):
    a=execute(seed=1,budget=3,feedback=False,output=tmp_path/"blind.json",
              elements=32,mass_limit=10.0)
    b=execute(seed=1,budget=3,feedback=True,output=tmp_path/"feedback.json",
              elements=32,mass_limit=10.0)
    assert len(a["rows"]) == len(b["rows"]) == 3
    assert all(r["status"] == "complete" for r in b["rows"])
    assert any(r["revision_applied"] for r in b["rows"][1:])
    assert all(not r["revision_applied"] for r in a["rows"])
    assert compare(tmp_path/"blind.json",tmp_path/"feedback.json")["matched_numerical_work"]

def test_common_scorer_recomputes_and_rejects_tampering(tmp_path):
    output=tmp_path/"trial.json"
    execute(seed=18,budget=3,feedback=True,output=output,elements=32,
            mass_limit=10.0)
    saved=score_saved(output)
    assert saved["scoring_evaluations"]==3
    assert saved["external_process_validation"] is False
    data=json.loads(output.read_text())
    data["rows"][0]["objectives"]["areal_mass"]=-100.0
    output.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="Stored objective"):
        score_saved(output)

def test_per_candidate_cpu_accounting_reconciles(tmp_path):
    record=execute(seed=44,budget=3,feedback=False,
                   output=tmp_path/"cpu.json",elements=32)
    for category in ("proposal_cpu_ns","manufacturing_cpu_ns","numerical_cpu_ns"):
        assert sum(row[category] for row in record["rows"])==record["accounting"][category]

def test_heldout_process_sensitivity_preserves_search_evidence(tmp_path):
    trial=tmp_path/"trial.json"
    execute(seed=5,budget=3,feedback=True,output=trial,
            elements=32,feed=.25,mass_limit=10.0)
    prior=trial.read_bytes()
    native=score_saved(trial)
    sensitivity=score_saved(trial,heldout_feed=.5)
    assert native["scoring_evaluations"]==3
    assert sensitivity["scoring_evaluations"]==6
    assert sensitivity["heldout_feed"]==.5
    assert trial.read_bytes()==prior

def test_mid_trial_interruption_checkpoints_and_resumes_without_repeating(tmp_path):
    from unittest.mock import patch
    import material_core.p1_comparator as cmp
    path=tmp_path/"interrupted.json"
    original=cmp._candidate
    def stop_after_two(provider,index):
        if index==2:
            raise KeyboardInterrupt("simulated process interruption")
        return original(provider,index)
    with patch.object(cmp,"_candidate",side_effect=stop_after_two):
        with pytest.raises(KeyboardInterrupt):
            execute(seed=5,budget=4,feedback=True,output=path,elements=32,
                    mass_limit=10.0)
    checkpoint=tmp_path/"interrupted.json.checkpoint.json"
    assert checkpoint.exists() and not path.exists()
    pre=json.loads(checkpoint.read_text())["record"]
    assert len(pre["rows"])==2
    recovered=execute(seed=5,budget=4,feedback=True,output=path,elements=32,
                      mass_limit=10.0)
    assert recovered["accounting"]["proposals"]==4
    assert recovered["rows"][:2]==pre["rows"]
    assert len(recovered["rows"])==4
    assert score_saved(path)["scoring_evaluations"]==4

def test_incompatible_or_corrupt_checkpoint_rejected_without_mutation(tmp_path):
    from unittest.mock import patch
    import material_core.p1_comparator as cmp
    path=tmp_path/"interrupted.json"
    original=cmp._candidate
    def stop_after_one(provider,index):
        if index==1:raise KeyboardInterrupt()
        return original(provider,index)
    with patch.object(cmp,"_candidate",side_effect=stop_after_one):
        with pytest.raises(KeyboardInterrupt):
            execute(seed=7,budget=3,feedback=False,output=path,elements=32)
    journal=tmp_path/"interrupted.json.checkpoint.json"
    pristine=journal.read_bytes()
    with pytest.raises(ValueError,match="Incompatible"):
        execute(seed=8,budget=3,feedback=False,output=path,elements=32)
    assert journal.read_bytes()==pristine
    data=json.loads(journal.read_text())
    data["record"]["rows"][0]["intended_hash"]="f"*64
    journal.write_text(json.dumps(data))
    corrupted=journal.read_bytes()
    with pytest.raises(ValueError,match="corrupt"):
        execute(seed=7,budget=3,feedback=False,output=path,elements=32)
    assert journal.read_bytes()==corrupted and not path.exists()
