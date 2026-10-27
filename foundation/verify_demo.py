"""Run all WP1 fixtures, persist and reopen them in separate processes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from material_core.store import RunStore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    store_path = args.output / 'store'
    records = []
    for architecture in ('homogeneous', 'layered', 'gradient'):
        started = time.perf_counter()
        command = [sys.executable, '-m', 'material_core.demo', '--store',
                   str(store_path), '--architecture', architecture]
        created = json.loads(subprocess.run(command, check=True, text=True,
                                            capture_output=True).stdout)
        replay_command = [sys.executable, '-m', 'material_core.demo', '--store',
                          str(store_path), '--replay', created['run_id']]
        replay = json.loads(subprocess.run(replay_command, check=True, text=True,
                                          capture_output=True).stdout)
        run = RunStore(store_path).load(created['run_id'])
        (args.output / (architecture + '-inputs.json')).write_text(
            run.inputs.canonical_json() + '\n')
        (args.output / (architecture + '-evaluation.json')).write_text(
            run.evaluation.canonical_json() + '\n')
        records.append({'architecture': architecture, 'create': created,
                        'replay': replay, 'commands': [command, replay_command],
                        'elapsed_seconds': time.perf_counter() - started})
    summary = {'claim': 'Same-host separate-process numerical replay, not physical validation',
               'fixtures': records}
    (args.output / 'demo-verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
