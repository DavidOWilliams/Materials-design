"""WP7 Gate 1/2 checks. Actual services (no mocked physics)."""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from material_core.wp5_service import execute, portable_import, replay
from material_core.wp7_view import summary, selected_candidate
from streamlit.testing.v1 import AppTest


def test_d1_saved_campaign_pareto_and_independent_process(tmp_path):
    path = tmp_path / "campaign.json"
    execute(path, elements=128, mass_limit=31., budget=4, feedback=True)
    view = summary(path)
    assert view["rows"]
    assert view["measured_evidence"] is None
    assert view["manufacturing_validation"] == "not_established"
    assert all(row["pareto"] is False for row in view["rows"] if not row["eligible"])
    assert all(row["reason"] for row in view["rows"])
    assert selected_candidate(path, 0)["evaluation_hash"]
    with pytest.raises(ValueError):
        selected_candidate(path, 999)
    copied = tmp_path / "copy.json"
    portable_import(path, copied)
    assert path.read_bytes() == copied.read_bytes()
    env = dict(os.environ, PYTHONPATH=str(Path("foundation").resolve()))
    program = "import sys,json;from material_core.wp5_service import replay;print(json.dumps(replay(sys.argv[1])))"
    result = subprocess.run([sys.executable, "-c", program, str(copied)],
                            check=True, capture_output=True, text=True, env=env)
    assert json.loads(result.stdout)["status"] == "passed"


def test_d1_infeasible_and_integrity_failure(tmp_path):
    path = tmp_path / "no-feasible.json"
    execute(path, elements=128, mass_limit=1.0, budget=4)
    view = summary(path)
    assert view["rows"]
    assert not view["pareto"]["pareto_ids"]
    assert not any(row["eligible"] for row in view["rows"])
    forged = tmp_path / "forged.json"
    data = json.loads(path.read_text())
    data["record"]["config"]["mass_limit"] = 999.
    forged.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        summary(forged)
    with pytest.raises(ValueError):
        portable_import(forged, tmp_path / "invalid-copy.json")
    assert not (tmp_path / "invalid-copy.json").exists()


def test_d1_actual_streamlit_widgets(tmp_path):
    app = AppTest.from_file("foundation/wp7_app.py", default_timeout=120).run()
    assert not list(app.exception)
    assert not list(app.error)
    matches = [w for w in app.text_input if w.label == "D1 workspace"]
    assert len(matches) == 1
    matches[0].set_value(str(tmp_path)).run()
    buttons = [w for w in app.button if w.label == "Generate, evaluate and save dossier"]
    assert len(buttons) == 1
    buttons[0].click().run()
    assert not list(app.exception)
    assert not list(app.error)
    path = tmp_path / "d1-example.json"
    assert path.exists()
    [w for w in app.button if w.label == "Inspect dossier and Pareto"][0].click().run()
    assert not list(app.exception)
    assert not list(app.error)
    [w for w in app.button if w.label == "Verify integrity and recompute"][0].click().run()
    assert not list(app.exception)
    assert not list(app.error)
    assert replay(path)["status"] == "passed"
