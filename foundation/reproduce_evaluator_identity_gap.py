"""Reproduction for R4 evaluator identity mismatch on inspected revision."""
from pathlib import Path
from tempfile import TemporaryDirectory
from material_core.wp2_numerical import evaluate
from material_core.wp3_search import run_search,recompute_search

def wrapper(inputs):
    return evaluate(inputs)

with TemporaryDirectory() as folder:
    path=Path(folder)/"campaign.json"
    result=run_search(path,seed=1,budget=1,elements=256,evaluation_adapter=wrapper)
    assert result["config"]["evaluation_adapter"]=="wp2-bounded-2"
    assert recompute_search(path)["recomputed"]==1
    print("R4 original behaviour reproduced: unnamed wrapper recorded under default identity")
