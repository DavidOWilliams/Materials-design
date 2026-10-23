"""Actual WP1 immutable byte/hash artifact compatibility checks."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from material_core.contracts import Evaluation, RunInputs


EVIDENCE=Path(__file__).resolve().parents[1]/'evidence'


@pytest.mark.parametrize('arch',['homogeneous','layered','gradient'])
def test_wp1_raw_bytes_and_hashes_unchanged(arch):
    a=(EVIDENCE/f'{arch}-inputs.json').read_bytes()
    b=(EVIDENCE/f'{arch}-evaluation.json').read_bytes()
    i=RunInputs.model_validate_json(a)
    e=Evaluation.model_validate_json(b)
    assert i.canonical_json().encode()==a.rstrip(b'\\n')
    assert e.canonical_json().encode()==b.rstrip(b'\\n')
    assert i.content_hash==hashlib.sha256(a.rstrip(b'\\n')).hexdigest()
    assert e.content_hash==hashlib.sha256(b.rstrip(b'\\n')).hexdigest()
    assert e.input_hash==i.content_hash
    assert e.brief_hash==i.brief.content_hash
    assert e.solver==i.solver
    assert 'constraint_metrics' not in json.loads(b)
    assert e.constraint_metrics==()


def test_wp1_saved_artifacts_load_in_independent_interpreter():
    program="""import hashlib,sys
from pathlib import Path
from material_core.contracts import RunInputs,Evaluation
p=Path(sys.argv[1])
for arch in ('homogeneous','layered','gradient'):
 a=(p/(arch+'-inputs.json')).read_bytes()
 b=(p/(arch+'-evaluation.json')).read_bytes()
 i=RunInputs.model_validate_json(a);e=Evaluation.model_validate_json(b)
 assert i.canonical_json().encode()==a.rstrip(b'\\n')
 assert e.canonical_json().encode()==b.rstrip(b'\\n')
 assert e.input_hash==i.content_hash
print('three immutable WP1 architectures preserved')
"""
    completed=subprocess.run([sys.executable,'-c',program,str(EVIDENCE)],
        capture_output=True,text=True,check=True)
    assert 'preserved' in completed.stdout
