# WP1 legacy and recovery verification

Executed 22 October 2026 from the repository root, based on recovery commit
2655d64f2d5a02dfeaf2a3c4c1e553cda218a89f. The new foundation lives separately;
legacy production source and recovery reference source were not edited.

A separate fresh Python 3.12.14 virtual environment was created at
`/workspace/scratch/3c56ad540c71/wp1-legacy-env`. Installing the observed recovery
freeze succeeded; this exercises the previously verified dependency combination
and does not assert reproduction of every pin in root requirements.txt.

Commands executed:

```sh
python3.12 -m venv /workspace/scratch/3c56ad540c71/wp1-legacy-env
/workspace/scratch/3c56ad540c71/wp1-legacy-env/bin/python -m pip install -r recovered_wp0/environment-freeze.txt
/workspace/scratch/3c56ad540c71/wp1-legacy-env/bin/python -m pip check
/workspace/scratch/3c56ad540c71/wp1-legacy-env/bin/python -m pip freeze
/workspace/scratch/3c56ad540c71/wp1-legacy-env/bin/python -m pytest tests recovered_wp0 -q
```

Result: **1,148 passed, 10 warnings, 33.44 seconds; no exclusions**.
`pip check` reported no broken requirements. Full output is retained in
`legacy-regression-tests.txt`; installation, package freeze and consistency
output are retained alongside it. The 10 warnings concern external dependency
deprecations and did not fail collection or execution.

This verifies the 1,120 legacy tests and 28 recovery checks freshly in this
session. It is not the historical WP0R result. Live Materials Project API
workflows, standalone external-service harness workflows, and the full
Streamlit application UI were not executed. Their modules collecting does not
establish live-service functionality.

The separate minimal foundation environment also executed the 28 recovery
checks: **28 passed in 0.49 seconds**. This confirms that the recovered numerical
fixture works without legacy UI/retrieval dependencies. Foundation integration
and replay results are documented separately by the lead.
