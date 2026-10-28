"""Independent-review R1–R4 reproduction and corrected acceptance boundaries."""
import json
from pathlib import Path
import pytest
from material_core.wp2_numerical import evaluate
from material_core.wp3_search import run_search,open_search,recompute_search
from material_core.wp3_adapters import ALTERNATE
from material_core.wp3_campaign import run_campaign,reopen_campaign,read_legacy_unvalidated


def interrupt(inputs):
    evaluate(inputs)
    raise KeyboardInterrupt("real WP2 was run")


def _pending_campaign(path):
    calls={"n":0}
    def middle(inputs):
        calls["n"]+=1
        if calls["n"]==2:
            evaluate(inputs)
            raise KeyboardInterrupt("second WP2 result not saved")
        return evaluate(inputs)
    with pytest.raises(KeyboardInterrupt):
        run_search(path,seed=13,budget=3,elements=256,
                   evaluation_adapter=middle,evaluator_identity="review-pending-v1")
    result=open_search(path)
    assert [p["status"] for p in result["proposals"]]==["complete","created"]
    return result


def test_r1_legacy_api_and_historical_unvalidated(tmp_path):
    historical=tmp_path/"v1.json"
    historical.write_text(json.dumps({"schema_version":1,
        "unique_evaluations":999,
        "qualified_comparison":{"pareto_ids":["invented"]}}))
    with pytest.raises(RuntimeError,match="retired"):
        reopen_campaign(historical)
    with pytest.raises(RuntimeError,match="retired"):
        run_campaign(historical,seed=1,evaluation_budget=1)
    read=read_legacy_unvalidated(historical)
    assert read["review_eligible"] is False


@pytest.mark.parametrize("field,bad",[
    ("objectives",{"areal_mass":-999}),
    ("constraints",{"mass_cap":"violated"}),
    ("qualified",False),
    ("manufacturing_feasibility","conditional"),
    ("evidence_maturity","measured"),
    ("numerical_quality","unresolved"),
])
def test_r2_completed_corruption_rejected_even_with_pending(tmp_path,field,bad):
    path=tmp_path/"ledger.json"
    _pending_campaign(path)
    raw=json.loads(path.read_text())
    raw["proposals"][0][field]=bad
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="Persisted evaluation summary mismatch"):
        run_search(path,seed=13,budget=3,elements=256,resume=True,
                   evaluation_adapter=evaluate,evaluator_identity="review-pending-v1")
    assert json.loads(path.read_text())["proposals"][0][field]==bad


def test_r2_comparison_rejected_with_pending(tmp_path):
    path=tmp_path/"ledger.json"
    _pending_campaign(path)
    raw=json.loads(path.read_text())
    raw["qualified_comparison"]={"pareto_ids":["invented"]}
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="qualified comparison"):
        run_search(path,seed=13,budget=3,elements=256,resume=True,
                   evaluation_adapter=evaluate,evaluator_identity="review-pending-v1")


@pytest.mark.parametrize("reason",["manufacturing_validated","cancelled","wall_time_budget_exhausted"])
def test_r3_invalid_stop_reason_or_mismatched_terminal_event(tmp_path,reason):
    path=tmp_path/"finished.json"
    run_search(path,seed=4,budget=2,elements=256)
    raw=json.loads(path.read_text())
    raw["stop_reason"]=reason
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="stop_reason|termination|Budget|Early"):
        open_search(path)


def test_r3_pending_may_not_claim_termination(tmp_path):
    path=tmp_path/"pending.json"
    _pending_campaign(path)
    raw=json.loads(path.read_text())
    raw["stop_reason"]="cancelled"
    raw["termination_event"]={"reason":"cancelled","proposal_slots":2}
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="pending"):
        open_search(path)


def test_r3_ordinary_cancel_and_resume(tmp_path):
    path=tmp_path/"cancel.json"
    calls=iter((False,True))
    first=run_search(path,seed=4,budget=3,elements=256,
                     cancel_requested=lambda:next(calls))
    assert first["stop_reason"]=="cancelled"
    assert first["termination_event"]=={"reason":"cancelled","proposal_slots":1}
    final=run_search(path,seed=4,budget=3,elements=256,resume=True)
    assert final["stop_reason"]=="evaluation_budget_exhausted"
    assert final["termination_event"]=={"reason":"evaluation_budget_exhausted","proposal_slots":3}
    assert final["stop_history"]==["cancelled"]
    assert len(final["proposals"])==3


def test_r4_alternate_brief_persistence_and_resume(tmp_path):
    path=tmp_path/"alternate.json"
    first=run_search(path,seed=4,budget=3,elements=256,
                     provider_identity=ALTERNATE,cancel_requested=lambda:True)
    assert first["stop_reason"]=="cancelled"
    final=run_search(path,seed=4,budget=3,elements=256,
                     provider_identity=ALTERNATE,resume=True)
    assert final["config"]["provider"]==ALTERNATE
    assert len(final["proposals"])==3
    assert final["config"]["objectives"] and final["config"]["constraints"]
    assert open_search(path)==final
    assert recompute_search(path)["recomputed"]==3
    from material_core.store import RunStore
    saved=RunStore(tmp_path/"run-store").load(final["proposals"][0]["run_id"])
    assert saved.inputs.brief.hot_boundary.value==380
    assert saved.inputs.brief.cold_boundary.value==320
    assert len(saved.inputs.design.architecture.layers)==3
    assert saved.evaluation.manufacturing_feasibility=="unknown"


def test_r3_impossible_budget_exhaustion_rejected(tmp_path):
    path=tmp_path/"half.json"
    first=run_search(path,seed=4,budget=3,elements=256,
                     cancel_requested=lambda:True)
    raw=json.loads(path.read_text())
    raw["stop_reason"]="evaluation_budget_exhausted"
    raw["termination_event"]={"reason":"evaluation_budget_exhausted","proposal_slots":0}
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError,match="Budget"):
        open_search(path)
