"""D1 v0.2 Streamlit UI collision checks against live widget semantics."""
from pathlib import Path
import pytest
from d1_visual_data import unused_output, output_conflicts

def button(app,label):
    matches=[x for x in app.button if x.label==label]
    assert len(matches)==1, (label, [x.label for x in app.button])
    return matches[0]

def test_tab1_existing_dossier_preserved_and_suggested_name(tmp_path):
    from streamlit.testing.v1 import AppTest
    original=tmp_path/"d1-example.json"
    original.write_bytes(b"existing immutable dossier")
    app=AppTest.from_file("foundation/wp7_app.py",default_timeout=120).run()
    workspace=next(x for x in app.text_input if x.label=="D1 workspace")
    workspace.set_value(str(tmp_path)).run()
    assert not list(app.exception)
    assert button(app,"Generate, evaluate and save dossier").disabled
    button(app,"Use suggested unused filename").click().run()
    assert not list(app.exception), [str(x.message) for x in app.exception]
    assert next(x for x in app.text_input if x.label=="New D1 dossier filename").value=="d1-example-run-001.json"
    assert not button(app,"Generate, evaluate and save dossier").disabled
    assert original.read_bytes()==b"existing immutable dossier"
    button(app,"Generate, evaluate and save dossier").click().run()
    assert not list(app.exception)
    assert not list(app.error)
    assert (tmp_path/"d1-example-run-001.json").exists()
    assert original.read_bytes()==b"existing immutable dossier"

def test_tab2_campaign_directory_collision_guidance(tmp_path):
    from streamlit.testing.v1 import AppTest
    old=tmp_path/"mixed-architecture"
    old.mkdir()
    (old/"campaign.json").write_text("untouched")
    app=AppTest.from_file("foundation/wp7_app.py",default_timeout=120).run()
    next(x for x in app.text_input if x.label=="D1 workspace").set_value(str(tmp_path)).run()
    assert not list(app.exception)
    assert button(app,"Generate three architecture classes and persist WP3 campaign").disabled
    button(app,"Suggest unused WP3 campaign directory").click().run()
    assert not list(app.exception)
    assert not button(app,"Generate three architecture classes and persist WP3 campaign").disabled
    assert (old/"campaign.json").read_text()=="untouched"

def test_path_companion_collision_preserved(tmp_path):
    output=tmp_path/"selected-wp4.json"
    companion=Path(str(output)+".handoff.json")
    companion.write_bytes(b"sidecar")
    assert output_conflicts(output,(".handoff.json",))==[str(companion)]
    assert unused_output(output,(".handoff.json",))!=output
    journal=tmp_path/"journal.jsonl"
    Path(str(journal)+".manifest.json").write_bytes(b"journal companion")
    assert output_conflicts(journal,(".manifest.json",".attempts.jsonl"))
