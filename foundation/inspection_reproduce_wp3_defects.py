"""Independent inspection defect reproductions against unmodified WP3 search implementation.

This file is a *pre-correction reproduction*; after correction, these assertions
must fail and the replacement acceptance tests must pass. Run separately.
"""
import json
from material_core.wp2_numerical import evaluate
from material_core.wp3_search import run_search, open_search


def test_pre_correction_interrupted_accounting(tmp_path):
    path=tmp_path/"interrupt.json"
    def interrupted(inputs):
        evaluate(inputs)
        raise KeyboardInterrupt("after genuine WP2 solve")
    try:
        run_search(path,seed=7,budget=2,elements=256,
                   evaluation_adapter=interrupted,
                   evaluator_identity="wp2-wrapper-interruption-v1")
    except KeyboardInterrupt:
        pass
    else:
        raise AssertionError("Fault injection did not interrupt")
    outcome=run_search(path,seed=7,budget=2,elements=256,resume=True,
                       evaluation_adapter=evaluate,
                       evaluator_identity="wp2-wrapper-interruption-v1")
    assert [p["status"] for p in outcome["proposals"]]==["failed","complete"]
    assert outcome["unique_evaluations"]==1
    assert not outcome.get("kernel_solve_count_uncertain",False)


def test_pre_correction_accepts_tampered_derived_fields(tmp_path):
    path=tmp_path/"evidence.json"
    run_search(path,seed=11,budget=1,elements=256)
    raw=json.loads(path.read_text())
    raw["unique_evaluations"]=999
    raw["proposals"][0]["objectives"]={"areal_mass":-999}
    path.write_text(json.dumps(raw))
    reopened=open_search(path)
    assert reopened["unique_evaluations"]==999
    assert reopened["proposals"][0]["objectives"]["areal_mass"]==-999
