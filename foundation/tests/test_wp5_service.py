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


def test_saved_brief_campaign_budget_mismatch(tmp_path):
    base = prepared_inputs(elements=128)
    brief = base.brief.model_dump(mode="json")
    brief["evaluation_budget"] = base.brief.evaluation_budget + 1
    with pytest.raises(ValueError, match="budget"):
        execute(tmp_path / "mismatch.json", elements=128, budget=1, brief=brief)


def test_saved_brief_rejects_unverified_process_assumptions(tmp_path):
    base = prepared_inputs(elements=128)
    brief = base.brief.model_dump(mode="json")
    brief["assumptions"] = []
    with pytest.raises((ValueError, TypeError)):
        execute(tmp_path / "unsupported.json", elements=128, budget=1, brief=brief)


def test_durable_cancel_and_recover(tmp_path):
    from material_core.wp5_service import execute_journal, recover_journal, journal_status
    journal = tmp_path / "cancel.jsonl"
    result = execute_journal(journal, elements=128, budget=2, cancel_requested=lambda: True)
    assert result["stop_reason"] == "cancelled"
    status = journal_status(journal)
    assert status["completed_candidates"] == 0
    assert status["mid_solver_restart_supported"] is False
    output = tmp_path / "resumed.json"
    recovered = recover_journal(journal, output)
    assert output.exists()
    assert recovered["accounting"]["reused_candidates"] == 0
    assert replay(output)["status"] == "passed"
    with pytest.raises(FileExistsError):
        recover_journal(journal, output)


def test_reject_corrupt_journal_manifest(tmp_path):
    from material_core.wp5_service import execute_journal, recover_journal
    journal = tmp_path / "corrupt.jsonl"
    execute_journal(journal, elements=128, budget=1, cancel_requested=lambda: True)
    manifest = tmp_path / "corrupt.jsonl.manifest.json"
    manifest.write_text(manifest.read_text().replace('"budget": 1', '"budget": 99'))
    with pytest.raises(ValueError, match="Corrupt"):
        recover_journal(journal, tmp_path / "output.json")
