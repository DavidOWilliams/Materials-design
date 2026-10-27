"""P1-IR-03 archive-based numerical degeneracy audit, supplemental only."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/"p1"/"evidence"/"confirmed-source-6eb62da"

def test_frozen_protocol_identity_and_original_outcomes():
    config=Path(__file__).resolve().parents[1]/"p1"/"CONFIRMATORY_CONFIG_FROZEN.json"
    assert hashlib.sha256(config.read_bytes()).hexdigest()=="f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0"
    summary=json.loads((ROOT/"confirmatory_summary.json").read_text())
    assert summary["confirmatory_n_pairs"]==80
    assert abs(summary["primary"]["mean"]-0.014069733796296294)<1e-15

def test_qualifying_stress_degenerate_vs_frozen_gigapascal_reference():
    rows=json.loads((ROOT/"all_paired_trials.json").read_text())
    assert len(rows)==80
    for arm,expected in (("control",125),("feedback",126)):
        stress=[obj["tensile_thermal_mismatch"] for row in rows
                for obj in row["summary"]["objective_vectors"][arm]]
        assert len(stress)==expected
        assert len(set(stress))==8
        assert min(stress)>0
        assert max(stress)<2.1e-8
        assert max(stress)/1e9<3e-17
