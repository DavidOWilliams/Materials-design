# WP1 CPU environment

WP1 uses an isolated Python 3.12 environment with 13 locked runtime/test
packages. The reusable contracts use Pydantic; the foundation example calls the
recovered NumPy/SciPy/scikit-fem Fourier calculation. SQLite and artifact
persistence use the Python standard library. Pytest is a development/test
dependency. No UI, notebook, retrieval client, GPU or language-model service is
needed by the new core.

## Setup and verification

From the repository root on a host with Python 3.12 and venv support:

```sh
bash foundation/setup.sh
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python -m pip check
```

The optional first argument to setup.sh selects another new environment path;
`PYTHON=/path/to/python3.12` selects the interpreter. The script fails on a
non-3.12 interpreter, refuses to overwrite an existing environment, and uses
`pip install --require-hashes`. Network/package-index access is required for
first installation. It does not install operating-system packages, upgrade the
OS, or execute project setup hooks. Python's venv-supplied pip is bootstrap
infrastructure; application dependencies are fully version/hash locked.

The accepted numerical versions are NumPy 2.3.5, SciPy 1.17.0 and scikit-fem
12.0.2, retained from the recovered benchmark. Pydantic 2.12.5 supplies strict
validation/serialization. pytest 9.0.2 runs the tests. The resolved transitive
versions are in `requirements.lock.txt`; hashes permit the published artifacts
for those exact versions. `requirements.in.txt` lists the five direct packages.

To intentionally update the lock in a separate reviewed change:

```sh
uv pip compile foundation/requirements.in.txt --generate-hashes --output-file foundation/requirements.lock.txt --python-version 3.12
```

`uv` is a lock-generation tool, not a runtime or setup prerequisite. Re-exercise
fresh setup, numerical references and replay after any update. Package licences
are retained in installed distributions: Pydantic/pytest are MIT; NumPy,
SciPy and scikit-fem are BSD-family open-source packages. Third-party scientific
data reuse is a separate issue, recorded with the input evidence.

## Executed setup

On 22 October 2026 a genuinely new virtual environment was created at
`/workspace/scratch/3c56ad540c71/wp1-core-env`, using Python 3.12.14 on Linux
x86-64. The supplied setup script installed from the hash lock and `pip check`
reported no broken requirements. This is same-host fresh-environment
verification, not an independently operated machine or a Codespaces/container
build. Actual platform/version records and setup output are in
`foundation/evidence/environment-*`.

The legacy application dependencies remain separate. Its large historical
requirements file is not imported into the new core environment. Legacy
verification uses a separate virtual environment and is documented in
`foundation/evidence/legacy-*`. Live external API workflows and the full UI
are not inferred from pytest collection or passing offline tests.

Fresh regression results: the minimal environment passed all 28 recovery tests
in 0.49 seconds; the separate historical environment passed all 1,148 legacy
plus recovery tests in 33.44 seconds with no exclusions and 10 dependency
deprecation warnings. Both environments passed `pip check`. These are current
session results, distinct from the historical WP0R test report.
