"""Frozen demonstrations of independently inspected R1–R4 defects.

Run with PYTHONPATH pointing at the EXACT reviewed historical commit,
not current corrected code. Each check asserts the old defective behavior.
"""
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from material_core.wp2_numerical import evaluate
from material_core.wp3_campaign import run_campaign,reopen_campaign
from material_core.wp3_search import run_search,open_search
import material_core.wp3_search as search


def reproduce_r1(root):
    path=root/"r1.json"
    run_campaign(path,seed=2,evaluation_budget=1,elements=256)
    record=json.loads(path.read_text())
    record["unique_evaluations"]=999
    record["qualified_comparison"]["pareto_ids"]=["invented"]
    path.write_text(json.dumps(record))
    reopened=reopen_campaign(path)
    assert reopened["unique_evaluations"]==999
    assert reopened["qualified_comparison"]["pareto_ids"]==["invented"]
    print("R1 reproduced: retired older v1 reader accepted fabricated evidence")


def _start_pending(path):
    calls=[0]
    def evaluator(inputs):
        calls[0]+=1
        if calls[0]==2:
            evaluate(inputs)
            raise KeyboardInterrupt("after real WP2 solve")
        return evaluate(inputs)
    try:
        run_search(path,seed=11,budget=3,elements=256,evaluation_adapter=evaluator,
                   evaluator_identity="review-r2-wrapper-v1")
    except KeyboardInterrupt:
        pass
    else:
        raise AssertionError("Expected interrupted second attempt")


def reproduce_r2(root):
    path=root/"r2.json"
    _start_pending(path)
    original=json.loads(path.read_text())
    assert [x["status"] for x in original["proposals"]]==["complete","created"]
    original["proposals"][0]["objectives"]={"areal_mass":-999}
    path.write_text(json.dumps(original))
    resumed=run_search(path,seed=11,budget=3,elements=256,
                       evaluator_identity="review-r2-wrapper-v1",
                       evaluation_adapter=evaluate,resume=True)
    assert resumed["proposals"][0]["objectives"]!={"areal_mass":-999}
    print("R2 reproduced: completed corruption silently replaced during pending recovery")


def reproduce_r3(root):
    path=root/"r3.json"
    run_search(path,seed=2,budget=1,elements=256)
    original=json.loads(path.read_text())
    original["stop_reason"]="manufacturing_validated"
    path.write_text(json.dumps(original))
    assert open_search(path)["stop_reason"]=="manufacturing_validated"
    print("R3 reproduced: fabricated manufacturing termination accepted")


def reproduce_r4():
    source=inspect.getsource(search)
    assert 'starting_design="shared homogeneous A/B 0.5"' in source
    assert 'objectives=("thermal_transmission","areal_mass","tensile_thermal_mismatch")' in source
    assert "inputs=propose(**proposal" in source
    assert 'architecture.kind=="homogeneous"' in source
    print("R4 reproduced: orchestration owns scenario construction and geometric validation")


if __name__=="__main__":
    with TemporaryDirectory() as tmp:
        base=Path(tmp)
        for name,fn in (("r1",reproduce_r1),("r2",reproduce_r2),("r3",reproduce_r3)):
            p=base/name;p.mkdir()
            fn(p)
        reproduce_r4()
        def wrapper(inputs):
            return evaluate(inputs)
        from material_core.wp3_search import recompute_search
        older=base/"evaluator.json"
        old_result=run_search(older,seed=4,budget=1,elements=256,evaluation_adapter=wrapper)
        assert old_result["config"]["evaluation_adapter"]=="wp2-bounded-2"
        assert recompute_search(older)["recomputed"]==1
        print("Original evaluator identity gap reproduced")
    print("Four original independent-review findings reproduced on inspected source")
