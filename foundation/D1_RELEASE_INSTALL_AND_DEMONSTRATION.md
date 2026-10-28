# D1 v0.1.0 — install, user walkthrough and preservation

**Source:** `c8f0292351553129fbcbdac3bd4f7a84a39365f9`; Python 3.12. All examples are synthetic. Run from repository root.

## Clean install and launch

```bash
bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2
.venv-foundation/bin/python -m pip check
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py
```

The numerical foundation is hash-locked; Streamlit 1.40.2 pinned but transitive UI environment is captured in CI dependency freeze. Do not claim a fully hash-locked UI. Preserve `pip freeze`, OS/Python and exact source identity.

## Integrated example

1. Open **Explore three architectures**. Select the representative full 4096 elements, deterministic seed 17, nine proposal slots and 31 kg/m² synthetic ceiling. Generate and persist the WP3 campaign.
2. Inspect homogeneous, layered and gradient proposals with constraints, numerical quality, unknown manufacturing evidence and *WP3-only* qualified Pareto. Select a **completed gradient using scenario_A and scenario_B**; reject homogeneous/layered or unsupported scenario_C as WP4 handoff candidates.
3. Select **WP3 candidate for WP4 handoff**. The original selected WP3 source hashes/ledger/run identity are preserved; a **new WP4** numerical context is constructed, not a relabelled WP3 Pareto point. Choose a fresh WP4 destination file, layer/feed settings and candidate budget.
4. Evaluate selected design, save immutable WP4 dossier, and inspect the intended/estimated state, conditional manufacturing mapping and density-guided mass feedback only when applicable. Inspect **WP4-only** Pareto and the separate `<dossier>.handoff.json` provenance. Do not claim a revision happened if naturally stopped.
5. To exercise actual cooperative cancellation, use a *new* suitably binding 1 kg/m² campaign, select the compatible gradient, set **Cooperatively cancel after completed candidates = 1** and choose a new journal path. Inspect checkpoint records and recover to a new immutable dossier; do not overwrite initial evidence.
6. Restart Streamlit, reopen the WP4 dossier and source WP3 campaign and replay. Separate-process CLI:
```bash
PYTHONPATH=foundation .venv-foundation/bin/python -c 'import sys,json;from material_core.wp7_handoff import verify_handoff;from material_core.wp5_service import replay;print(json.dumps({"handoff":verify_handoff(sys.argv[1]),"numerical":replay(sys.argv[1])}))' d1-workspace/selected-wp4.json
```
7. Verify/export the **complete WP3 ZIP** containing ledger, SQLite and artifacts. Preserve the WP4 dossier and companion `*.handoff.json` alongside the WP3 workspace/verified ZIP. They are **not** a self-contained relocatable combined ZIP. When restoring, use an unused destination and verify source lineage at its resulting path.

## Generate reproducible example evidence

```bash
PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py wp7-evidence --elements 4096 --budget 9
```

Use a new directory; never overwrite historic accepted evidence. Record generated manifest, verified WP3 ZIP, WP4 JSON and handoff companion, logs and source SHA. Original detailed correction walkthrough: `foundation/WP7_IR01_IR04_CORRECTIVE_DEMONSTRATION.md`; source testing `foundation/tests/wp7_ir_browser_acceptance.py`.

**Failure and scope:** missing WP3 ledger/store means WP4 handoff provenance cannot be verified; reject as missing, do not invent data. Cancel is candidate-boundary only. Intended-state WP3 is not measured. Lower-resolution results may remain unresolved. No real ceramics certification.
