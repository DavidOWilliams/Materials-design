"""WP2 R1 regression: constraint metrics are distinct from optimisation objectives."""
import json
import subprocess
import sys

import pytest
from material_core.contracts import (
    Brief, Constraint, ConstraintMetric, Evaluation, Metric, RunInputs, quantity,
)
from material_core.demo import make_fixture
from material_core.store import RunStore
from material_core.thermal import evaluate


def case(value=20., status="computed", shared=False):
    source=make_fixture()
    raw=source.model_dump(mode="json")
    raw["brief"]["constraints"]=[Constraint(id="mass_cap",metric_id="mass",
        limit=quantity("areal_mass",30.),relation="le",
        applicability="synthetic software fixture").model_dump(mode="json")]
    if shared:
        raw["brief"]["objectives"].append({"schema_version":"1.0","id":"mass",
            "dimension":"areal_mass","unit":"kg/m2","direction":"min",
            "applicability":"synthetic software fixture"})
    inputs=RunInputs.model_validate(raw)
    computed=status=="computed"
    m=ConstraintMetric(metric_id="mass",value=quantity("areal_mass",value) if computed else None,
        status=status,explanation="Software fixture; not a physical mass calculation")
    original=evaluate(inputs)
    objectives=list(original.metrics)
    if shared:
        objectives[-1]=Metric(objective_id="mass",value=m.value,status=m.status,
            explanation="Software fixture; not a physical mass calculation")
    result=Evaluation(input_hash=inputs.content_hash,brief_hash=inputs.brief.content_hash,
        solver=inputs.solver,status="complete" if all(x.status=="computed" for x in objectives) else "incomplete",
        metrics=tuple(objectives),constraint_metrics=(m,),feasibility="conditional",
        limitations=("Synthetic constraint fixture; no ceramic material validation.",))
    return inputs,result


@pytest.mark.parametrize("value,eligible",[(20.,True),(30.,True),(31.,False)])
def test_constraint_only_satisfied_and_violated(value,eligible,tmp_path):
    inputs,result=case(value)
    store=RunStore(tmp_path)
    run_id=store.create(inputs)
    store.finish(run_id,result)
    loaded=RunStore(tmp_path).load(run_id)
    assert loaded.evaluation.constraint_metrics[0].value.value==value
    assert loaded.evaluation.comparison_eligible(inputs.brief) is eligible


@pytest.mark.parametrize("status",["missing","unsupported","failed"])
def test_unknown_constraints_cannot_pass(status,tmp_path):
    inputs,result=case(status=status)
    store=RunStore(tmp_path);run_id=store.create(inputs);store.finish(run_id,result)
    assert not RunStore(tmp_path).load(run_id).evaluation.comparison_eligible(inputs.brief)


def test_constraint_absent_remains_unknown(tmp_path):
    inputs,result=case()
    result=result.model_copy(update={"constraint_metrics":()})
    s=RunStore(tmp_path);run_id=s.create(inputs);s.finish(run_id,result)
    assert not s.load(run_id).evaluation.comparison_eligible(inputs.brief)


def test_shared_objective_constraint_agreement_and_conflict(tmp_path):
    inputs,result=case(shared=True)
    s=RunStore(tmp_path);run_id=s.create(inputs);s.finish(run_id,result)
    assert s.load(run_id).evaluation.comparison_eligible(inputs.brief)
    wrong=ConstraintMetric(metric_id="mass",value=quantity("areal_mass",21.),
        status="computed",explanation="Intentional conflict")
    other=s.create(inputs)
    with pytest.raises(ValueError,match="disagree"):
        s.finish(other,result.model_copy(update={"constraint_metrics":(wrong,)}))


def test_unit_mismatch_and_nonfinite_rejected(tmp_path):
    inputs,result=case()
    s=RunStore(tmp_path);run_id=s.create(inputs)
    wrong=ConstraintMetric(metric_id="mass",value=quantity("stress",20.),
        status="computed",explanation="Wrong unit")
    with pytest.raises(ValueError,match="Constraint result units"):
        s.finish(run_id,result.model_copy(update={"constraint_metrics":(wrong,)}))
    raw=result.model_dump(mode="json")
    raw["constraint_metrics"][0]["value"]["value"]=float("nan")
    with pytest.raises(ValueError):
        Evaluation.model_validate_json(json.dumps(raw))


def test_replay_separate_process_and_original_wp1_bytes(tmp_path):
    legacy=evaluate(make_fixture())
    assert "constraint_metrics" not in json.loads(legacy.canonical_json())
    inputs,result=case()
    s=RunStore(tmp_path);run_id=s.create(inputs);s.finish(run_id,result)
    program="""import sys
from material_core.store import RunStore
s=RunStore(sys.argv[1]).load(sys.argv[2])
assert s.evaluation.comparison_eligible(s.inputs.brief)
print(s.evaluation.constraint_metrics[0].value.value)
"""
    run=subprocess.run([sys.executable,"-c",program,str(tmp_path),run_id],
        text=True,capture_output=True,check=True)
    assert float(run.stdout)==20.
