"""WP7 accepted WP3 architecture integration and portable evidence tests."""
import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from material_core.wp3_search import run_search, recompute_search
from material_core.wp7_search_dossier import (
    export_mixed_zip, import_mixed_zip, mixed_candidate, mixed_summary
)


def test_three_architectures_durable_zip_independent_process(tmp_path):
    ledger_path = tmp_path / "original" / "campaign.json"
    record = run_search(ledger_path, seed=17, budget=4, elements=128, mass_limit=31.)
    assert len(record["proposals"]) == 4
    view = mixed_summary(ledger_path)
    assert {"homogeneous", "layered", "gradient"} <= {
        row["architecture"] for row in view["rows"]
    }
    assert view["measured_evidence"] is None
    assert all(row["manufacturing_feasibility"] == "unknown"
               for row in view["rows"] if row["status"] == "complete")
    assert mixed_candidate(ledger_path, 0)["evaluation"]["status"]
    assert view["pareto"] is not None
    blob = export_mixed_zip(ledger_path)
    assert blob.startswith(b"PK")
    restored = tmp_path / "restored"
    result = import_mixed_zip(blob, restored)
    assert result["replay"] == "passed"
    assert mixed_summary(restored / "campaign.json")["rows"] == view["rows"]
    with pytest.raises(FileExistsError):
        import_mixed_zip(blob, restored)
    env = dict(os.environ, PYTHONPATH=str(Path("foundation").resolve()))
    cmd = ("import sys,json; from material_core.wp3_search import recompute_search; "
           "print(json.dumps(recompute_search(sys.argv[1])))")
    executed = subprocess.run([sys.executable, "-c", cmd,
                               str(restored / "campaign.json")],
                              capture_output=True, text=True, env=env, check=True)
    assert json.loads(executed.stdout)["replay"] == "passed"


def test_wp3_archive_tamper_and_path_traversal_closed(tmp_path):
    original = tmp_path / "original" / "campaign.json"
    run_search(original, seed=17, budget=4, elements=128)
    valid = export_mixed_zip(original)
    modified = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(valid)) as source, zipfile.ZipFile(modified, "w") as target:
        for item in source.infolist():
            raw = source.read(item.filename)
            if item.filename == "campaign.json":
                raw = raw + b" "
            target.writestr(item.filename, raw)
    with pytest.raises(ValueError, match="checksum"):
        import_mixed_zip(modified.getvalue(), tmp_path / "tampered")
    assert not (tmp_path / "tampered").exists()
    malicious = io.BytesIO()
    with zipfile.ZipFile(malicious, "w") as target:
        manifest = {"schema": "wp7-wp3-portable-v1",
                    "files": {
                        "campaign.json": hashlib.sha256(b"{}").hexdigest(),
                        "run-store/runs.sqlite3": hashlib.sha256(b"bad").hexdigest(),
                        "../unsafe.txt": hashlib.sha256(b"evil").hexdigest()}}
        target.writestr("SHA256SUMS.json", json.dumps(manifest))
        target.writestr("campaign.json", b"{}")
        target.writestr("run-store/runs.sqlite3", b"bad")
        target.writestr("../unsafe.txt", b"evil")
    with pytest.raises(ValueError, match="Unsafe archive"):
        import_mixed_zip(malicious.getvalue(), tmp_path / "unsafe-import")
    assert not (tmp_path / "unsafe-import").exists()
    assert not (tmp_path / "unsafe.txt").exists()


def test_wp3_real_streamlit_app_widgets(tmp_path):
    """WP3 full architecture journey through actual Streamlit widgets, not mocks."""
    pytest.importorskip("streamlit")
    from streamlit.testing.v1 import AppTest

    def widget(group, label):
        matches = [w for w in group if w.label == label]
        assert len(matches) == 1, (label, [w.label for w in group])
        return matches[0]

    app = AppTest.from_file("foundation/wp7_app.py", default_timeout=120).run()
    assert not list(app.exception)
    widget(app.text_input, "D1 workspace").set_value(str(tmp_path)).run()
    widget(app.selectbox, "WP3 mesh elements").set_value(128).run()
    widget(app.number_input, "WP3 candidate budget").set_value(4).run()
    widget(app.button, "Generate three architecture classes and persist WP3 campaign").click().run()
    assert not list(app.exception)
    assert not list(app.error)
    dossier = tmp_path / "mixed-architecture" / "campaign.json"
    assert dossier.exists()
    widget(app.button, "Inspect WP3 search and numerical Pareto").click().run()
    assert not list(app.exception)
    assert not list(app.error)
    assert mixed_summary(dossier)["pareto"] is not None
    widget(app.button, "Recompute WP3 numerical evidence").click().run()
    assert not list(app.exception)
    assert not list(app.error)
