"""Record recovery lineage and content hashes; no network or source modification."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).parent
SOURCE = ROOT.parents[1] / 'recovery_sources' / 'WP0_Ceramic_Evidence_Package.zip'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    with zipfile.ZipFile(SOURCE) as archive:
        for name in archive.namelist():
            assert archive.read(name) == (ROOT/'ceramic'/name).read_bytes(), name
    inventory = {
        'recovery_date': '2026-10-21',
        'base_commit': 'f3e6cfc7f7e9ed885ce681814c0927fc421163c8',
        'branch': 'wp0r-recovery-2026-10-21',
        'missing_original_commit': '51c84ac',
        'source_archive_sha256': digest(SOURCE.read_bytes()),
        'recovered_exact': ['ceramic/'+p.name for p in sorted((ROOT/'ceramic').iterdir()) if p.is_file()],
        'reconstructed': ['thermal.py','laminate.py','test_recovery.py'],
        'not_recovered': ['Original wp0_spike and wp0_comparison source and tests',
                          'Original wp0_manufacturing source and tests',
                          'Original local git commit', 'Previously inspected source PDFs'],
        'files': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(ROOT.rglob('*'))
                  if p.is_file() and '__pycache__' not in p.parts and p.name != 'inventory.json'},
    }
    (ROOT/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print('All four ceramic files match the retained ZIP byte-for-byte')


if __name__ == '__main__':
    main()
