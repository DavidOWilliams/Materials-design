"""WP3 evaluator identity checks."""
import pytest
from material_core.wp2_numerical import evaluate
from material_core.wp3_evaluators import STANDARD, DELEGATE, delegate
from material_core.wp3_search import run_search, open_search, recompute_search

def wrapper(inputs):
    return evaluate(inputs)

def test_unnamed_adapter_fails_before_creating_campaign(tmp_path):
    path=tmp_path/"a.json"
    with pytest.raises(ValueError,match="explicit evaluator_identity"):
        run_search(path,seed=3,budget=1,elements=256,evaluation_adapter=wrapper)
    assert not path.exists()
    assert not (tmp_path/"run-store").exists()

@pytest.mark.parametrize("identity",[STANDARD,DELEGATE])
def test_reserved_identity_rejects_different_callable(tmp_path,identity):
    path=tmp_path/"b.json"
    with pytest.raises(ValueError,match="reserved"):
        run_search(path,seed=3,budget=1,elements=256,
                   evaluator_identity=identity,evaluation_adapter=wrapper)
    assert not path.exists()

def test_registered_alternate_executes_and_recomputes(tmp_path):
    path=tmp_path/"c.json"
    record=run_search(path,seed=3,budget=2,elements=256,evaluator_identity=DELEGATE)
    assert record["config"]["evaluation_adapter"]==DELEGATE
    assert open_search(path)==record
    assert recompute_search(path)["recomputed"]==2

def test_explicit_registered_callable_and_replay(tmp_path):
    path=tmp_path/"d.json"
    run_search(path,seed=3,budget=1,elements=256,
               evaluation_adapter=delegate,evaluator_identity=DELEGATE)
    assert recompute_search(path)["recomputed"]==1

def test_named_test_wrapper_reopens_but_recompute_refuses(tmp_path):
    path=tmp_path/"e.json"
    result=run_search(path,seed=3,budget=1,elements=256,
                      evaluation_adapter=wrapper,evaluator_identity="test-wrapper-v1")
    assert open_search(path)==result
    with pytest.raises(ValueError,match="Unavailable evaluator"):
        recompute_search(path)
