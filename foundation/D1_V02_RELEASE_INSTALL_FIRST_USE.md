# D1 v0.2 — clean install, first use and evidence retention

**Internal bounded synthetic demonstration; not validated ceramic production design.** First confirm that your checkout is the approved candidate and you have Python 3.12. Do not use the old `d1-v0.2-guided-ui` development branch once a controlled release has been approved.

## Setup (Linux/Codespaces with Python 3.12)

```bash
git rev-parse HEAD
python3.12 --version
PYTHON=python3.12 bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2
.venv-foundation/bin/python -m pip check
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py --server.address 0.0.0.0 --server.port 8501
```

In Codespaces use the forwarded port 8501 from Ports → Open in Browser. Existing `.venv-foundation` created by an earlier source must be inspected before reuse; do not overwrite evidence. These instructions are based on source + Ubuntu CI; **a user-led Windows/Edge/Codespaces trial is not independently passed**. For details consult `foundation/D1_V02_CODESPACES_FIRST_USER_GUIDE.md`.

## Walkthrough

1. **Run demonstration:** inspect hypothetical scenario, mass ceiling and objectives. If `d1-example.json` exists, inspect the saved dossier or choose **Use suggested unused filename**. Do not overwrite immutable records.
2. **Explore architectures:** create a WP3 search campaign at a **new directory**; use 4096 elements and reproducible seed/budget for qualified full-resolution examples. Compare homogeneous, layered and gradient schematic composition with source knots/interfaces, exact tables and **WP3 intended-state** mass/thermal mismatch/transmission results. Green numerical status does not imply manufactured feasibility.
3. Choose a **completed supported A/B gradient** and verify source lineage to WP4. Unsupported materials, homogeneous/layered candidates or incompatible duty/mesh must reject explicitly. Source WP3 Pareto eligibility does not transfer to WP4.
4. **Manufacturing and trade-offs:** run WP4 into a *new* dossier filename. View conditional synthetic estimated-achieved profile/deviations where coordinate, material and source basis match; preserve unknown results and separate WP4 Pareto.
5. Exercise checkpoint/candidate-boundary cancellation in a new binding scenario and recover into a different immutable dossier. No mid-solver interruption. Verify the saved companion `<wp4-dossier>.handoff.json`.
6. **Restore and replay:** reopen source WP3 ledger and WP4 dossier, verify immutable hashes, generate WP3 portable ZIP, restore into unused directory, replay numerical results in separate process and restart browser.

## Reproducible evidence

```bash
PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py d1-v02-examples --elements 4096 --budget 9
```

Preserve the generated manifest, WP3 complete ledger/SQLite/run-store/hash-addressed files or verified WP3 ZIP, WP4 JSON, `*.handoff.json`, journal and evidence hashes. The WP4 JSON+companion alone **cannot be relocated as a standalone combined bundle**. Existing dossiers must never be overwritten.

Scientific interpretation: intended vs estimated achieved are different contexts; no measurements, process accuracy or physical validation. Unsupported overlays are withheld and nonfinite fields not treated as qualified. User-accessibility and Windows/Edge experience remain an outstanding distribution gate.
