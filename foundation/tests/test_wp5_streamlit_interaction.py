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
    control(app.number_input, "Maximum evaluations").set_value(20).run()
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


def test_wp5_r1_revised_saved_brief_checkpoint_cancel_recover_import_replay(tmp_path):
    """WP5-R1: exercise the *UI*, not merely the service, with a revised duty."""
    from material_core.wp5_brief_editor import revise_brief, save_brief, open_brief
    from material_core.wp4_feedback import starting_inputs, reopen
    from material_core.wp4_journal import read_manifest
    from material_core.wp5_service import portable_import
    original = starting_inputs(elements=128).brief
    revised = revise_brief(original, {
        "duty": original.duty + " | WP5-R1 independently distinguishable revised duty",
        "evaluation_budget": 2,
    })
    assert revised.content_hash != original.content_hash
    saved = tmp_path / "revised-brief.json"
    save_brief(saved, revised)
    assert open_brief(saved).content_hash == revised.content_hash

    app = AppTest.from_file("foundation/wp5_app.py", default_timeout=120).run()
    assert_no_ui_errors(app)
    control(app.text_input, "Workspace directory").set_value(str(tmp_path)).run()
    control(app.text_input, "Saved brief to use (optional; must match supported WP4 fixture)").set_value(str(saved)).run()
    control(app.number_input, "Maximum evaluations").set_value(2).run()
    control(app.number_input, "Cancel after completed candidates (0 = immediately)").set_value(1).run()
    journal = tmp_path / "campaign-journal.jsonl"
    recovered = tmp_path / "recovered.json"
    control(app.text_input, "Journal path").set_value(str(journal)).run()
    control(app.text_input, "Recovered dossier path").set_value(str(recovered)).run()
    control(app.button, "Start checkpointed campaign with cancellation").click().run()
    assert_no_ui_errors(app)
    assert journal.exists()
    manifest = read_manifest(journal)
    assert manifest["baseline_intended_inputs"]["brief"]["duty"] == revised.duty
    from material_core.contracts import RunInputs
    saved_in_manifest = RunInputs.model_validate_json(
        json.dumps(manifest["baseline_intended_inputs"])).brief
    assert saved_in_manifest.content_hash == revised.content_hash
    control(app.button, "Inspect journal and attempt history").click().run()
    assert_no_ui_errors(app)
    from material_core.wp5_service import journal_status
    assert journal_status(journal)["completed_candidates"] == 1
    control(app.button, "Resume from durable journal").click().run()
    assert_no_ui_errors(app)
    assert recovered.exists()
    assert reopen(recovered)["accounting"]["reused_candidates"] == 1
    assert inspect(recovered)["brief_hash"] == revised.content_hash
    exported = inspect(recovered)["export"]
    assert exported["intended_baseline_hash"] == reopen(recovered)["baseline_intended_inputs"]["design"]["content_hash"]
    assert replay(recovered)["status"] == "passed"
    imported = tmp_path / "r1-imported.json"
    portable_import(recovered, imported)
    assert inspect(imported)["brief_hash"] == revised.content_hash
    assert inspect(imported)["export"] == exported
    assert replay(imported)["status"] == "passed"
    assert imported.read_bytes() == recovered.read_bytes()


def test_wp5_r1_incompatible_saved_budget_creates_no_journal(tmp_path):
    """The selected immutable brief must be checked before opening the journal."""
    from material_core.wp5_brief_editor import revise_brief, save_brief
    from material_core.wp4_feedback import starting_inputs
    original = starting_inputs(elements=128).brief
    revised = revise_brief(original, {
        "duty": original.duty + " | WP5-R1 rejected budget",
        "evaluation_budget": 2,
    })
    saved = tmp_path / "revised-brief.json"
    save_brief(saved, revised)
    app = AppTest.from_file("foundation/wp5_app.py", default_timeout=120).run()
    control(app.text_input, "Workspace directory").set_value(str(tmp_path)).run()
    control(app.text_input, "Saved brief to use (optional; must match supported WP4 fixture)").set_value(str(saved)).run()
    control(app.number_input, "Maximum evaluations").set_value(1).run()
    journal = tmp_path / "rejected-journal.jsonl"
    control(app.text_input, "Journal path").set_value(str(journal)).run()
    control(app.button, "Start checkpointed campaign with cancellation").click().run()
    assert list(app.error)
    assert any("budget" in str(x.proto).lower() for x in app.error)
    assert not journal.exists()
    assert not (tmp_path / "rejected-journal.jsonl.manifest.json").exists()
    assert not (tmp_path / "rejected-journal.jsonl.attempts.jsonl").exists()
