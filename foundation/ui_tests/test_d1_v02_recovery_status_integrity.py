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

def _selected_source():
    """Only a UI fixture: backend scientific eligibility remains tested elsewhere."""
    return {"ledger":"/nonexistent/source-ledger.json","index":3,"elements":128,"mass_limit":31.0}

def test_failed_new_recovery_attempt_clears_previous_status(monkeypatch, tmp_path):
    from streamlit.testing.v1 import AppTest
    # Presentation-only stub of an earlier successful authoritative verification.
    import material_core.wp7_handoff as handoff
    monkeypatch.setattr(handoff,"verify_handoff",lambda path: {"verified":True})
    app=AppTest.from_file("foundation/wp7_app.py",default_timeout=120)
    app.session_state["wp7_handoff"]=_selected_source()
    app.session_state["d1_recovery_status"]={"dossier":str(tmp_path/"old.json"),
                                            "companion":str(tmp_path/"old.json.handoff.json")}
    app.run()
    assert any("Recovered original selected design" in str(x.value) for x in app.success)
    # Journal doesn't exist, so the actual backend recovery must reject it.
    btn=next(x for x in app.button if x.label=="Recover selected-design journal into immutable dossier")
    btn.click().run()
    assert any("Recovery rejected:" in str(x.value) for x in app.error)
    assert "d1_recovery_status" not in app.session_state
    app.run()
    assert all("Recovered original selected design" not in str(x.value) for x in app.success)

def test_optional_summary_failure_preserves_verified_recovery(monkeypatch,tmp_path):
    from streamlit.testing.v1 import AppTest
    import material_core.wp7_handoff as handoff
    import material_core.wp7_view as view
    def recovered(journal,output):
        Path(output).parent.mkdir(parents=True,exist_ok=True)
        Path(output).write_text("persisted synthetic source",encoding="utf-8")
        Path(str(output)+".handoff.json").write_text("persisted companion",encoding="utf-8")
        return {"stop_reason":"cancelled","records":[{"index":0}]}
    def verified(output):
        assert Path(output).exists() and Path(str(output)+".handoff.json").exists()
        return {"verified":True}
    monkeypatch.setattr(handoff,"recover_checkpointed_handoff",recovered)
    monkeypatch.setattr(handoff,"verify_handoff",verified)
    monkeypatch.setattr(view,"summary",lambda path: (_ for _ in ()).throw(ValueError("optional view unavailable")))
    app=AppTest.from_file("foundation/wp7_app.py",default_timeout=120)
    app.session_state["wp7_handoff"]=_selected_source()
    app.run()
    next(x for x in app.text_input if x.label=="D1 workspace").set_value(str(tmp_path)).run()
    next(x for x in app.button if x.label=="Recover selected-design journal into immutable dossier").click().run()
    assert any("Recovered original selected design" in str(x.value) for x in app.success)
    assert any("optional comparison view" in str(x.value) for x in app.warning)
    assert "d1_recovery_status" in app.session_state
    app.run()
    assert any("Recovered original selected design" in str(x.value) for x in app.success)
