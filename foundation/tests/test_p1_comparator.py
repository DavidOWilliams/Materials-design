"""P1 focused regression: control continues after the first candidate.

Executed by .github/workflows/p1-equal-effort.yml. No physical validation.
"""
import json
import pytest
from material_core.p1_comparator import execute, compare

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
