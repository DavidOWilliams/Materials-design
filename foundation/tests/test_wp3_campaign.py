"""Seeded WP3 campaign increment: store, qualification, budgets and cancellation."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from material_core.wp3_campaign import reopen_campaign, run_campaign


def test_campaign_reopen_and_independent_process(tmp_path):
    ledger_path = tmp_path / "campaign.json"
    record = run_campaign(ledger_path, seed=17, evaluation_budget=3, elements=4096)
    assert record["stop_reason"] == "evaluation_budget_exhausted"
    assert len(record["proposals"]) == 3
    assert record["unique_evaluations"] == 3
    assert record["nominal_kernel_solves"] == 3
    assert record["refinement_kernel_solves"] == 3
    first, second = record["proposals"][:2]
    assert first["constraint_outcomes"]["mass_cap"] == "violated"
    assert not first["numerically_eligible"]
    assert second["constraint_outcomes"]["mass_cap"] == "satisfied"
    assert second["numerically_eligible"]
    assert all(item["manufacturing_feasibility"] == "unknown" for item in record["proposals"])
    assert "0" not in record["qualified_comparison"]["pareto_ids"]
    assert reopen_campaign(ledger_path) == record

    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "material_core.wp3_campaign", "--ledger",
         str(ledger_path), "--reopen"],
        capture_output=True, text=True, check=True, env=env)
    assert json.loads(result.stdout) == record


def test_campaign_cancellation_and_immutable_ledger(tmp_path):
    path = tmp_path / "cancel.json"
    record = run_campaign(path, seed=3, evaluation_budget=3,
                          cancel_requested=lambda: True)
    assert record["stop_reason"] == "cancelled"
    assert record["proposals"] == []
    assert record["unique_evaluations"] == 0
    with pytest.raises(FileExistsError):
        run_campaign(path, seed=3, evaluation_budget=3)


def test_campaign_rejects_invalid_budget_and_seed(tmp_path):
    for seed, budget in ((True, 1), (1, 0), (1, True), (1.5, 1)):
        with pytest.raises(ValueError):
            run_campaign(tmp_path / "bad.json", seed=seed, evaluation_budget=budget)
