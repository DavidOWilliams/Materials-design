#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
core_python="${PYTHON:-python3.12}"
core_venv="${1:-$repo_root/.venv-foundation}"
"$core_python" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Python 3.12 required"'
if [[ -e "$core_venv" ]]; then
  printf 'Refusing to overwrite existing environment: %s\n' "$core_venv" >&2
  exit 1
fi
"$core_python" -m venv "$core_venv"
"$core_venv/bin/python" -m pip install --require-hashes -r "$repo_root/foundation/requirements.lock.txt"
"$core_venv/bin/python" -m pip check
printf 'Ready: %s/bin/python\n' "$core_venv"
