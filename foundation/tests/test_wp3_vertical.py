"""WP3 vertical slice regression: persisted new proposal and subprocess replay."""
import json
import os
from pathlib import Path
import subprocess
import sys

from material_core.wp3_vertical import propose_gradient, execute_one


def test_new_design_not_fixture():
    from material_core.wp2_scenarios import make_wp2_fixture
    original = make_wp2_fixture("gradient", elements=4096)
    proposed = propose_gradient(elements=4096)
    assert proposed.design.content_hash != original.design.content_hash
    assert proposed.settings.evaluation_context_hash == original.settings.evaluation_context_hash
    assert proposed.design.parent_hashes == (original.design.content_hash,)


def test_persist_and_replay_in_separate_process(tmp_path):
    original = execute_one(tmp_path, elements=4096)
    assert original["status"] == "complete"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + env.get("PYTHONPATH", "")
    process = subprocess.run(
        [sys.executable, "-m", "material_core.wp3_vertical",
         "--store", str(tmp_path), "--replay", original["run_id"]],
        capture_output=True, text=True, env=env, check=True)
    replay = json.loads(process.stdout)
    assert replay["replay"] == "passed"
    assert replay["evaluation_hash"] == original["evaluation_hash"]
