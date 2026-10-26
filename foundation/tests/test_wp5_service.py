import pytest
from material_core.wp5_service import execute, inspect, replay, compare_compatible, prepared_inputs


def test_end_to_end(tmp_path):
    p = tmp_path / "run.json"
    record = execute(p, elements=128, budget=1)
    assert p.exists()
    assert inspect(p)["measured_evidence"] is None
    assert inspect(p)["export"]["measured_evidence"] is None
    assert replay(p)["status"] == "passed"
    assert compare_compatible(p, p)["measured_evidence"] is None
    with pytest.raises(FileExistsError):
        execute(p, elements=128, budget=1)


def test_invalid_budget(tmp_path):
    with pytest.raises(ValueError, match="budget"):
        execute(tmp_path / "invalid.json", budget=0)


def test_incompatible_comparison(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    execute(a, elements=128, budget=1, mass_limit=31.0)
    execute(b, elements=128, budget=1, mass_limit=29.0)
    with pytest.raises(ValueError, match="Incompatible"):
        compare_compatible(a, b)


def test_unsupported_geometry_edit():
    base = prepared_inputs(elements=128)
    brief = base.brief.model_dump(mode="json")
    brief["thickness"]["value"] *= 2
    with pytest.raises(ValueError, match="Unsupported"):
        prepared_inputs(elements=128, brief=brief)
