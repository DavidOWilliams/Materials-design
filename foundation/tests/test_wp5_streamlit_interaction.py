"""Actual Streamlit widget interaction: no mocks of numerical or WP4 services."""
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from material_core.wp5_service import inspect, replay


def control(group, label):
    matches = [widget for widget in group if widget.label == label]
    assert len(matches) == 1, (label, [w.label for w in group])
    return matches[0]


def assert_no_ui_errors(app):
    assert not list(app.exception), [str(x.message) for x in app.exception]
    assert not list(app.error), [str(x.proto) for x in app.error]


def test_streamlit_full_interactive_vertical(tmp_path):
    app = AppTest.from_file("foundation/wp5_app.py", default_timeout=120).run()
    assert_no_ui_errors(app)
    control(app.text_input, "Workspace directory").set_value(str(tmp_path)).run()
    control(app.button, "Save new immutable brief").click().run()
    assert (tmp_path / "brief.json").exists()
    control(app.text_input, "Saved brief to use (optional; must match supported WP4 fixture)").set_value(
        str(tmp_path / "brief.json")
    ).run()
    control(app.button, "Execute and persist campaign").click().run()
    assert_no_ui_errors(app)
    dossier = tmp_path / "campaign.json"
    assert dossier.exists()
    assert inspect(dossier)["records"]
    assert inspect(dossier)["measured_evidence"] is None
    control(app.button, "Inspect verified dossier").click().run()
    assert_no_ui_errors(app)
    control(app.button, "Recompute numerical evidence").click().run()
    assert_no_ui_errors(app)
    assert replay(dossier)["status"] == "passed"
    control(app.text_input, "Source dossier to import").set_value(str(dossier)).run()
    control(app.text_input, "New immutable destination").set_value(str(tmp_path / "imported.json")).run()
    control(app.button, "Import verified dossier").click().run()
    assert_no_ui_errors(app)
    assert (tmp_path / "imported.json").exists()
    control(app.button, "Replay imported dossier").click().run()
    assert_no_ui_errors(app)
    assert replay(tmp_path / "imported.json")["status"] == "passed"


def test_streamlit_invalid_brief_is_rejected(tmp_path):
    app = AppTest.from_file("foundation/wp5_app.py", default_timeout=120).run()
    control(app.text_input, "Workspace directory").set_value(str(tmp_path)).run()
    control(app.text_area, "Typed brief JSON (complete contract)").set_value('{"invalid": true}').run()
    assert list(app.error)
    assert not (tmp_path / "brief.json").exists()


def test_streamlit_process_version_binds_to_persisted_campaign(tmp_path):
    app = AppTest.from_file("foundation/wp5_app.py", default_timeout=120).run()
    control(app.text_input, "Workspace directory").set_value(str(tmp_path)).run()
    control(app.number_input, "Process scenario version").set_value(2).run()
    control(app.number_input, "Maximum evaluations").set_value(1).run()
    control(app.button, "Execute and persist campaign").click().run()
    assert_no_ui_errors(app)
    from material_core.wp4_feedback import reopen
    dossier = tmp_path / "campaign.json"
    assert dossier.exists()
    assert reopen(dossier)["process"]["version"] == 2
    assert replay(dossier)["status"] == "passed"


def test_streamlit_cancel_recover_and_corrupt_import(tmp_path):
    app = AppTest.from_file("foundation/wp5_app.py", default_timeout=120).run()
    control(app.text_input, "Workspace directory").set_value(str(tmp_path)).run()
    journal = tmp_path / "campaign-journal.jsonl"
    recovered = tmp_path / "recovered.json"
    control(app.text_input, "Journal path").set_value(str(journal)).run()
    control(app.text_input, "Recovered dossier path").set_value(str(recovered)).run()
    control(app.button, "Start checkpointed campaign with cancellation").click().run()
    assert_no_ui_errors(app)
    assert journal.exists()
    control(app.button, "Inspect journal and attempt history").click().run()
    assert_no_ui_errors(app)
    control(app.button, "Resume from durable journal").click().run()
    assert_no_ui_errors(app)
    assert recovered.exists()
    assert replay(recovered)["status"] == "passed"
    corrupt = tmp_path / "forged.json"
    corrupt.write_text('{"record": {}, "record_sha256": "forged"}')
    control(app.text_input, "Source dossier to import").set_value(str(corrupt)).run()
    control(app.text_input, "New immutable destination").set_value(str(tmp_path / "rejected.json")).run()
    control(app.button, "Import verified dossier").click().run()
    assert list(app.error)
    assert not (tmp_path / "rejected.json").exists()
