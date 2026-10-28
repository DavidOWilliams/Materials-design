import json
from pathlib import Path
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
    brief["thickness"]["value"] *= 2
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
    import json
    envelope = json.loads(manifest.read_text())
    envelope["manifest"]["config"]["budget"] = 99
    manifest.write_text(json.dumps(envelope))
    with pytest.raises(ValueError, match="Corrupt"):
        recover_journal(journal, tmp_path / "output.json")


def test_portable_import_and_replay(tmp_path):
    from material_core.wp5_service import portable_import
    source, target = tmp_path / "source.json", tmp_path / "copy.json"
    execute(source, elements=128, budget=1)
    imported = portable_import(source, target)
    assert imported == __import__("material_core.wp4_feedback", fromlist=["reopen"]).reopen(source)
    assert replay(target)["status"] == "passed"
    with pytest.raises(FileExistsError):
        portable_import(source, target)


def test_corrupt_portable_import_rejected(tmp_path):
    from material_core.wp5_service import portable_import
    source = tmp_path / "forged.json"
    source.write_text('{"record": {}, "record_sha256": "forged"}')
    with pytest.raises((ValueError, KeyError)):
        portable_import(source, tmp_path / "target.json")
    assert not (tmp_path / "target.json").exists()


def test_process_scenario_versioning():
    from material_core.wp5_service import versioned_scenario
    a = versioned_scenario(version=1)
    b = versioned_scenario(version=2)
    assert a.version == 1 and b.version == 2
    assert a.id == b.id
    with pytest.raises(ValueError):
        versioned_scenario(version=0)


def test_distinct_process_scenario_comparison(tmp_path):
    from material_core.wp5_service import compare_scenarios
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    execute(a, elements=128, budget=1, layer=0.005)
    execute(b, elements=128, budget=1, layer=0.01)
    comparison = compare_scenarios(a, b)
    assert comparison["causal_effect_established"] is False
    assert comparison["measured_evidence"] is None
    with pytest.raises(ValueError, match="Identical"):
        compare_scenarios(a, a)


def test_saved_brief_full_vertical_workflow(tmp_path):
    from material_core.wp5_brief_editor import revise_brief, save_brief, open_brief
    from material_core.wp5_service import portable_import
    fixture = prepared_inputs(elements=128).brief
    changed = revise_brief(fixture, {"duty": fixture.duty + " — WP5 bounded edited duty"})
    saved = tmp_path / "edited-brief.json"
    save_brief(saved, changed)
    loaded = open_brief(saved)
    dossier = tmp_path / "campaign.json"
    execute(dossier, elements=128, budget=loaded.evaluation_budget,
            brief=loaded.model_dump(mode="json"))
    observed = inspect(dossier)
    assert observed["brief_hash"] == loaded.content_hash
    assert observed["records"]
    assert observed["measured_evidence"] is None
    imported = tmp_path / "reopened.json"
    portable_import(dossier, imported)
    assert inspect(imported)["brief_hash"] == loaded.content_hash
    assert replay(imported)["status"] == "passed"


def test_versioned_process_identity_persists_and_replays(tmp_path):
    from material_core.wp5_service import compare_scenarios, execute_journal, recover_journal
    original, revised = tmp_path / "v1.json", tmp_path / "v2.json"
    execute(original, elements=128, budget=1, process_version=1)
    execute(revised, elements=128, budget=1, process_version=2)
    from material_core.wp4_feedback import reopen
    assert reopen(original)["process"]["version"] == 1
    assert reopen(revised)["process"]["version"] == 2
    from material_core.contracts import ProcessScenario
    assert (ProcessScenario.model_validate_json(json.dumps(reopen(original)["process"])).content_hash !=
            ProcessScenario.model_validate_json(json.dumps(reopen(revised)["process"])).content_hash)
    assert replay(revised)["status"] == "passed"
    comparison = compare_scenarios(original, revised)
    assert comparison["causal_effect_established"] is False
    journal = tmp_path / "versioned.jsonl"
    execute_journal(journal, elements=128, budget=1, process_version=2, cancel_requested=lambda: True)
    resumed = recover_journal(journal, tmp_path / "versioned-recovered.json")
    assert resumed["process"]["version"] == 2
    assert replay(tmp_path / "versioned-recovered.json")["status"] == "passed"


def test_invalid_process_version_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="version"):
        execute(tmp_path / "bad.json", elements=128, budget=1, process_version=0)
    assert not (tmp_path / "bad.json").exists()


def test_user_selected_cancel_after_one_durable_candidate(tmp_path):
    from material_core.wp5_service import execute_journal, journal_status, recover_journal
    from material_core.wp4_journal import recover
    journal = tmp_path / "stop-after-one.jsonl"
    result = execute_journal(journal, elements=128, budget=4,
                             cancel_requested=lambda: len(recover(journal)) >= 1)
    assert result["stop_reason"] == "cancelled"
    assert journal_status(journal)["completed_candidates"] == 1
    resumed = recover_journal(journal, tmp_path / "completed.json")
    assert resumed["accounting"]["reused_candidates"] == 1
    assert replay(tmp_path / "completed.json")["status"] == "passed"


def test_no_feasible_candidate_and_unknown_measured_evidence(tmp_path):
    path = tmp_path / "impossible.json"
    record = execute(path, elements=128, budget=2, mass_limit=1.0)
    assert record["records"]
    assert not any(row["feasible"] for row in record["records"])
    observed = inspect(path)
    assert observed["measured_evidence"] is None
    assert observed["manufacturing_validation"] == "not_established"
    assert replay(path)["status"] == "passed"


def test_process_version_change_rejects_compatible_comparison(tmp_path):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    execute(first, elements=128, budget=1, process_version=1)
    execute(second, elements=128, budget=1, process_version=2)
    with pytest.raises(ValueError, match="Incompatible process"):
        compare_compatible(first, second)


def test_stale_process_identity_tamper_is_rejected(tmp_path):
    path = tmp_path / "stale.json"
    execute(path, elements=128, budget=1, process_version=2)
    envelope = json.loads(path.read_text())
    envelope["record"]["process"]["version"] = 1
    path.write_text(json.dumps(envelope))
    with pytest.raises(ValueError):
        inspect(path)
    with pytest.raises(ValueError):
        replay(path)


@pytest.mark.parametrize("invalid_budget", [0, -1, True, False, 1.0, 1.5, "1", None],
                         ids=["zero", "negative", "true", "false", "integral-float",
                              "fractional-float", "numeric-string", "none"])
def test_wp5_ir2_invalid_budget_never_creates_journal_or_parent(tmp_path, invalid_budget):
    """IR2: validate strict positive int before even creating a parent directory."""
    from material_core.wp5_service import execute_journal
    parent = tmp_path / "not-created" / "nested"
    journal = parent / "invalid.jsonl"
    with pytest.raises(ValueError, match="[Bb]udget"):
        execute_journal(journal, elements=128, budget=invalid_budget)
    assert not parent.exists()
    assert not journal.exists()
    assert not Path(str(journal) + ".manifest.json").exists()
    assert not Path(str(journal) + ".attempts.jsonl").exists()


def test_wp5_ir2_retry_same_path_after_invalid_and_real_recovery(tmp_path):
    from material_core.wp5_service import execute_journal, recover_journal, journal_status
    from material_core.wp4_journal import recover
    journal = tmp_path / "fresh" / "campaign.jsonl"
    with pytest.raises(ValueError, match="[Bb]udget"):
        execute_journal(journal, elements=128, budget=0)
    assert not journal.parent.exists()
    result = execute_journal(journal, elements=128, budget=2,
                             cancel_requested=lambda: len(recover(journal)) >= 1)
    assert result["stop_reason"] == "cancelled"
    assert journal_status(journal)["completed_candidates"] == 1
    output = tmp_path / "recovered.json"
    resumed = recover_journal(journal, output)
    assert resumed["accounting"]["reused_candidates"] == 1
    assert replay(output)["status"] == "passed"
    original = {p: p.read_bytes() for p in
                (journal, Path(str(journal) + ".manifest.json"),
                 Path(str(journal) + ".attempts.jsonl"))}
    with pytest.raises(FileExistsError):
        execute_journal(journal, elements=128, budget=2)
    assert all(p.read_bytes() == contents for p, contents in original.items())


def test_wp5_ir2_saved_brief_mismatch_no_journal_or_parent(tmp_path):
    from material_core.wp5_service import execute_journal
    base = prepared_inputs(elements=128)
    brief = base.brief.model_dump(mode="json")
    brief["evaluation_budget"] = 2
    journal = tmp_path / "not-created" / "mismatch.jsonl"
    with pytest.raises(ValueError, match="budget"):
        execute_journal(journal, elements=128, budget=1, brief=brief)
    assert not journal.parent.exists()
    assert not journal.exists()
    assert not Path(str(journal) + ".manifest.json").exists()
    assert not Path(str(journal) + ".attempts.jsonl").exists()
