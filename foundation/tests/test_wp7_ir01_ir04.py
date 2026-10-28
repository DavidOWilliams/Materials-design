"""WP7 independent finding IR01/IR04 focused full service challenges."""
import json
import subprocess
import sys
from pathlib import Path

import pytest
from material_core.wp3_search import run_search
from material_core.wp7_handoff import (
    qualified_handoff_source, execute_handoff, verify_handoff,
    start_checkpointed_handoff, recover_checkpointed_handoff,
)
from material_core.wp5_service import replay
from material_core.wp4_feedback import reopen


def source(tmp_path, mass=31.):
    ledger = tmp_path / "wp3" / "campaign.json"
    run_search(ledger, seed=17, budget=4, elements=128, mass_limit=mass)
    return ledger


def test_selected_gradient_handoff_and_separate_process_replay(tmp_path):
    ledger = source(tmp_path)
    with pytest.raises(ValueError, match="gradient only"):
        qualified_handoff_source(ledger, 0, elements=128, mass_limit=31.)
    with pytest.raises(ValueError, match="gradient only"):
        qualified_handoff_source(ledger, 2, elements=128, mass_limit=31.)
    with pytest.raises(ValueError, match="mesh/mass"):
        qualified_handoff_source(ledger, 3, elements=256, mass_limit=31.)
    baseline, evidence = qualified_handoff_source(ledger, 3, elements=128, mass_limit=31.)
    assert evidence["source_design_hash"] == baseline.design.content_hash
    assert evidence["measured_evidence"] is None
    target = tmp_path / "selected.json"
    result = execute_handoff(ledger, 3, target, elements=128, mass_limit=31.,
                             budget=4)
    assert result["records"]
    assert verify_handoff(target)["verified"] is True
    assert result["baseline_intended_inputs"]["design"]["architecture"]["kind"] == "gradient"
    assert replay(target)["status"] == "passed"
    script = ("import sys,json;from material_core.wp7_handoff import verify_handoff;"
              "from material_core.wp5_service import replay;"
              "print(json.dumps([verify_handoff(sys.argv[1]),replay(sys.argv[1])]))")
    p = subprocess.run([sys.executable,"-c",script,str(target)],
        capture_output=True,text=True,check=True)
    data = json.loads(p.stdout)
    assert data[0]["verified"] is True and data[1]["status"] == "passed"
    raw = json.loads((tmp_path / "selected.json.handoff.json").read_text())
    raw["provenance"]["source_design_hash"]="0"*64
    (tmp_path / "selected.json.handoff.json").write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="integrity"):
        verify_handoff(target)


def test_checkpoint_cancel_recover_preserves_selected_lineage(tmp_path):
    ledger = source(tmp_path, mass=1.)
    journal = tmp_path / "selected.journal.jsonl"
    result = start_checkpointed_handoff(ledger, 3, journal,
        elements=128,mass_limit=1., budget=4, cancel_after=1)
    assert result["completed"] == 1
    assert result["stop_reason"] == "cancelled"
    restored = tmp_path / "recovered.json"
    done = recover_checkpointed_handoff(journal, restored)
    assert done["records"]
    assert verify_handoff(restored)["verified"] is True
    assert replay(restored)["status"] == "passed"
    with pytest.raises(FileExistsError):
        recover_checkpointed_handoff(journal, restored)


def test_no_unsupported_catalogue_or_spoofed_wp3_source(tmp_path):
    ledger=source(tmp_path)
    with pytest.raises(ValueError,match="mesh/mass"):
        qualified_handoff_source(ledger,3,elements=128,mass_limit=30.)
    with pytest.raises(ValueError):
        qualified_handoff_source(ledger,99,elements=128,mass_limit=31.)
    data=json.loads(ledger.read_text())
    data["config"]["mass_limit"]=999.
    ledger.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        qualified_handoff_source(ledger,3,elements=128,mass_limit=31.)
