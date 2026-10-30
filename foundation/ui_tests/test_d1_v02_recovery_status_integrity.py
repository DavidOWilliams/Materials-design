"""Focused Streamlit recovery-status fail-closed tests.

These complement the REAL Chromium source-backed corruption test. They exercise
rerender status invalidation with missing and deliberately invalid evidence.
"""
from pathlib import Path
import pytest

@pytest.mark.parametrize("mode", ["missing_dossier", "missing_companion", "tampered_companion", "modified_dossier"])
def test_persisted_verified_status_fails_closed_on_rerender(tmp_path, mode):
    from streamlit.testing.v1 import AppTest
    dossier = tmp_path / "selected-wp4-recovered.json"
    companion = Path(str(dossier) + ".handoff.json")
    if mode != "missing_dossier":
        dossier.write_text("{}" if mode == "modified_dossier" else "unverifiable dossier", encoding="utf-8")
    if mode in ("tampered_companion", "modified_dossier"):
        companion.write_text('{"sha256":"'+("0"*64)+'","provenance":{}}', encoding="utf-8")
    app = AppTest.from_file("foundation/wp7_app.py", default_timeout=120)
    app.session_state["d1_recovery_status"] = {
        "dossier": str(dossier),
        "companion": str(companion)
    }
    app.run()
    assert not list(app.exception)
    warnings = [str(x.value) for x in app.warning]
    successes = [str(x.value) for x in app.success]
    assert any("can no longer be verified" in x for x in warnings), warnings
    assert all("Recovered original selected design" not in x for x in successes)
    assert "d1_recovery_status" not in app.session_state
    # Warning/success must not return automatically on another rerender.
    app.run()
    assert all("Recovered original selected design" not in str(x.value) for x in app.success)
