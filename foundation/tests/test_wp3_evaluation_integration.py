"""Real WP2 evaluations across WP3 qualification and immutable process replay.

The property scenario is synthetic. Numerical eligibility is not manufacture approval.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

from material_core.store import RunStore
from material_core.wp2_numerical import (
    compatible_comparison, evaluate, numerical_comparison_eligible,
)
from material_core.wp3_qualified import qualified_pareto
from material_core.wp3_vertical import propose_gradient


def test_real_wp2_feasible_infeasible_and_qualified_comparison(tmp_path):
    records = []
    for fraction, expected_outcome in ((0.35, "violated"), (0.65, "satisfied")):
        inputs = propose_gradient(mid_fraction=fraction, elements=4096)
        result = evaluate(inputs)
        mass = next(m.value.value for m in result.metrics if m.objective_id == "areal_mass")
        assert result.status == "complete"
        assert result.numerical_quality == "qualified"
        assert result.manufacturing_feasibility == "unknown"
        assert result.evidence_status == "synthetic"
        assert len(result.constraint_outcomes) == 1
        assert result.constraint_outcomes[0].outcome == expected_outcome
        assert (mass > 31.0) == (fraction == 0.35)
        assert numerical_comparison_eligible(result, inputs.brief) == (fraction == 0.65)
        store = RunStore(tmp_path)
        run_id = store.create(inputs)
        store.finish(run_id, result)
        assert store.load(run_id).evaluation.content_hash == result.content_hash
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
        replay = subprocess.run(
            [sys.executable, "-m", "material_core.wp3_vertical", "--store",
             str(tmp_path), "--replay", run_id],
            check=True, capture_output=True, text=True, env=env,
        )
        assert json.loads(replay.stdout)["evaluation_hash"] == result.content_hash
        records.append((str(fraction), result))
    assert compatible_comparison(records[0][1], records[1][1])
    decision = qualified_pareto(records, inputs.brief)
    assert decision["pareto_ids"] == ["0.65"]
    assert "0.35" in decision["excluded"]
    assert records[0][1].feasibility == "infeasible"
    assert records[1][1].feasibility == "conditional"
