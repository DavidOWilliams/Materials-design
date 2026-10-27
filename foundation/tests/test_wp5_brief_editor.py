import json
import pytest
from material_core.wp4_feedback import starting_inputs
from material_core.wp5_brief_editor import validate_brief, revise_brief, save_brief, open_brief


def fixture_brief():
    return starting_inputs(elements=128).brief


def test_round_trip(tmp_path):
    brief = fixture_brief()
    path = tmp_path / "brief.json"
    save_brief(path, brief)
    assert open_brief(path).content_hash == brief.content_hash
    with pytest.raises(FileExistsError):
        save_brief(path, brief)


def test_versioned_edit():
    brief = fixture_brief()
    updated = revise_brief(brief, {"duty": brief.duty + " (revised)"})
    assert updated.version == brief.version + 1
    assert updated.content_hash != brief.content_hash
    assert updated.thickness == brief.thickness


@pytest.mark.parametrize("change", [
    {"evaluation_budget": 0},
    {"evaluation_budget": -1},
    {"thickness": {"dimension": "temperature", "value": 1, "unit": "K"}},
    {"unsupported_property": 12},
    {"kind": "brief"},
])
def test_invalid_edits_fail_closed(change):
    with pytest.raises((ValueError, TypeError)):
        revise_brief(fixture_brief(), change)


def test_tamper_rejected(tmp_path):
    path = tmp_path / "brief.json"
    save_brief(path, fixture_brief())
    raw = json.loads(path.read_text())
    raw["brief"]["duty"] = "forged"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="integrity"):
        open_brief(path)


def test_missing_fields_rejected():
    with pytest.raises(ValueError):
        validate_brief({"id": "incomplete", "evaluation_budget": 2})
