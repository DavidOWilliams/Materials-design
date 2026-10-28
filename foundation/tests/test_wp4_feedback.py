from material_core.wp4_feedback import run,save,reopen,recompute
import pytest

def test_binding_feedback_revision():
    dossier=run(elements=256,mass_limit=31.,budget=5)
    assert dossier["records"][0]["feedback"] is not None
    assert len(dossier["records"])>1
    assert dossier["records"][1]["intended_hash"]!=dossier["records"][0]["intended_hash"]
    assert dossier["records"][1]["intended_design"]["parent_hashes"]==[dossier["records"][0]["intended_hash"]]
    assert dossier["process"]["route"]=="synthetic_ideal_planar_deposition"
    assert dossier["measured_evidence"] is None

def test_no_feedback_same_start():
    on=run(elements=256,budget=3,feedback=True)
    off=run(elements=256,budget=3,feedback=False)
    assert on["records"][0]["intended_hash"]==off["records"][0]["intended_hash"]
    assert off["stop_reason"]=="feedback_disabled"

def test_impossible_budget_not_relaxed():
    x=run(elements=256,mass_limit=1.,budget=4)
    assert not any(r["feasible"] for r in x["records"])
    assert x["config"]["mass_limit"]==1.

def test_portable_reopen_recompute(tmp_path):
    path=tmp_path/"dossier.json"
    save(path,run(elements=256,budget=3))
    assert reopen(path)["algorithm"]=="wp4-feedback-v1"
    assert recompute(path)["status"]=="passed"
    with pytest.raises(FileExistsError):
        save(path,run(elements=256,budget=1))
