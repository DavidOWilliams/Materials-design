"""Restore the exact accepted WP4 evidence/source archives using Python stdlib."""
from pathlib import Path
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text())
for name, record in manifest['files'].items():
    data = bytearray()
    for part in record['parts']:
        content = (root / part['path']).read_bytes()
        if len(content) != part['bytes'] or hashlib.sha256(content).hexdigest() != part['sha256']:
            raise ValueError('Part verification failed: ' + part['path'])
        data.extend(content)
    if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
        raise ValueError('Archive verification failed: ' + name)
    target = root / name
    if target.exists() and target.read_bytes() != data:
        raise ValueError('Refusing to overwrite different file: ' + name)
    target.write_bytes(data)
    print('Verified:', name, record['sha256'])
with zipfile.ZipFile(root / 'WP4_tested_evidence_beaf8a5.zip') as archive:
    bad = archive.testzip()
    if bad is not None:
        raise ValueError('ZIP integrity failure: ' + bad)
    print('Evidence ZIP integrity passed:', len(archive.infolist()), 'entries')
