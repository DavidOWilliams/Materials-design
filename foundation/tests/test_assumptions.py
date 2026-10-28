"""Behavioural tests for source fidelity and assumption history integrity."""
from dataclasses import FrozenInstanceError
from hashlib import sha256
import json
from pathlib import Path
import re

import pytest

from material_core.assumptions import AssumptionRecord, AssumptionRegistry, validate_snapshot

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'recovered_wp0/evidence/WP0_Decision_Pack_and_Assumptions.md'


def test_builtin_preserves_complete_original_register():
    registry = AssumptionRegistry.from_builtin()
    source_rows = [line for line in SOURCE.read_text().splitlines()
                   if re.match(r'\| A\d\d \|', line)]
    assert len(registry.snapshot()) == len(source_rows) == 15
    for line in source_rows:
        ident, question, answer, basis, consequence, priority = [s.strip() for s in line.split('|')[1:-1]]
        item = registry.get(ident, 1)
        assert (item.exact_question, item.provisional_answer, item.evidence_basis,
                item.sensitivity_consequence, item.sensitivity_priority) == (question, answer, basis, consequence, priority)
        assert item.source_sha256 == sha256(SOURCE.read_bytes()).hexdigest()
        assert item.value_status == 'unresolved'
        assert item.value is item.value_range is item.unit is None
        assert item.status == 'open'
        assert item.affected_calculations and item.owner and item.resolution_criterion


def test_update_retains_historic_run_and_changes_identity():
    registry = AssumptionRegistry.from_builtin()
    original = registry.get('A09', 1)
    saved = registry.snapshot({'A09': 1})
    changed = registry.update('A09', expected_version=1, provisional_answer='Explicit software scenario, still awaiting physical evidence.', value_status='specified', value=0.001, unit='m')
    assert changed.version == 2 and changed.content_hash != original.content_hash
    assert registry.get('A09') == changed
    assert registry.get('A09', 1) == original
    assert validate_snapshot(json.loads(json.dumps(saved))) == (original,)
    assert registry.snapshot({'A09': 1}) == saved
    with pytest.raises(ValueError, match='Stale'):
        registry.update('A09', expected_version=1, provisional_answer='overwrite attempt')
    with pytest.raises(ValueError, match='overwrite'):
        registry.add(AssumptionRecord.from_dict({**saved[0], 'content_hash': None, 'provisional_answer': 'overwrite attempt'}))


def test_snapshots_are_detached_and_detect_tampering():
    registry = AssumptionRegistry.from_builtin()
    record = registry.get('A01')
    with pytest.raises(FrozenInstanceError):
        record.owner = 'different owner'
    snapshot = registry.snapshot({'A01': 1})
    snapshot[0]['affected_calculations'].append('injected')
    assert 'injected' not in record.affected_calculations
    with pytest.raises(ValueError, match='hash mismatch'):
        validate_snapshot(snapshot)
    with pytest.raises(ValueError, match='one version'):
        validate_snapshot(registry.snapshot({'A01': 1}) * 2)
    with pytest.raises(KeyError):
        registry.snapshot({'A01': 17})


@pytest.mark.parametrize('change', [
    {'value': 0.0},
    {'value_status': 'specified', 'value': float('nan'), 'unit': 'm'},
    {'value_status': 'specified', 'value': float('inf'), 'unit': 'm'},
    {'value_status': 'specified', 'value': True, 'unit': '1'},
    {'value_status': 'specified', 'value': 1, 'unit': None},
    {'value_status': 'specified', 'value': 1, 'unit': 'banana'},
    {'value_status': 'specified', 'value_range': [2, 1], 'unit': 'm'},
    {'value_status': 'specified', 'value_range': [1, 2, 3], 'unit': 'm'},
    {'value_status': 'specified', 'value': 1, 'value_range': [1, 2], 'unit': 'm'},
    {'affected_calculations': []},
    {'status': 'validated_by_successful_software'},
])
def test_unresolved_and_invalid_values_cannot_be_favourable_defaults(change):
    registry = AssumptionRegistry.from_builtin()
    with pytest.raises(ValueError):
        registry.update('A13', expected_version=1, **change)
    assert registry.get('A13').version == 1


def test_hash_is_independent_of_mapping_key_order_and_unknown_fields_rejected():
    data = AssumptionRegistry.from_builtin().snapshot({'A05': 1})[0]
    reversed_data = dict(reversed(list(data.items())))
    assert AssumptionRecord.from_dict(data).content_hash == AssumptionRecord.from_dict(reversed_data).content_hash
    with pytest.raises(TypeError):
        AssumptionRecord.from_dict({**data, 'hidden_assumption': 'yes'})
