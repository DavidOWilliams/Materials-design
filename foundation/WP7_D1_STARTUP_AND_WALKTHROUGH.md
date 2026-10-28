# WP7 D1 — clean installation, demonstration, dossier restoration

**Synthetic computational demonstration only.** All materials are neutral hypothetical scenario records; physical ceramic properties, measured achieved state, process accuracy and engineering readiness remain unvalidated.

## Source and environment

Tested upstream acceptance baseline: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`. WP7 implementation changes live on branch `wp7-d1-app-implementation-2026-10-28` and draft PR #16. Use exact release-candidate implementation source SHA recorded in WP7 completion/qualification evidence, not the later governance PR #12 HEAD or CI merge checkout. Python **3.12** required. In a fresh checkout from repository root:

```sh
bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py
```

The foundation numerical dependencies are hash locked; Streamlit and Playwright test-only dependencies are separately pinned but their entire transitive dependency set is captured by the workflow freeze rather than hash locked. Run `pip check`.

## Journey A — mixed architecture inverse search and numerical Pareto

Open **2. Explore three architectures**. Select 4096 elements for the full-resolution demonstration, nine candidate slots, deterministic seed 17 and a 31 kg/m² synthetic mass ceiling. Click **Generate three architecture classes and persist WP3 campaign**. The existing accepted WP3 bounded generator evaluates a starting homogeneous reference, further homogeneous/layered/gradient alternatives, and variations in the neutral A/B/C scenario-material catalogue. It logs each proposal, constraint, numerical quality, and qualified numerical Pareto decision. Results and `run-store` are immutable/durable within the selected workspace. 128/256/512 element modes are previews, not automatically scientifically qualified.

Click **Inspect WP3 search and numerical Pareto**, inspect all proposals, separate feasibility/quality/evidence flags, and select a candidate for original intended design, brief, objective measurements and hashes. **Intended-state WP3 results have unknown manufacturing feasibility**: do not compare their Pareto outcomes to WP4 estimated-state manufacturing-feedback results as if they share an achieved-state context.

Download **full verified WP3 dossier ZIP** (the ledger, SQLite store, hash-addressed source/evaluations, and SHA256 manifest). Use **WP3 portable ZIP to restore** with an unused destination directory and click **Verify and restore WP3 ZIP**. The import verifies membership, file hashes, persisted WP3 accounting/identities and all completed numerical evaluations. Restart Streamlit and reopen the restored ledger.

For separate-process confirmation from the repo root:

```sh
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger d1-workspace/mixed-restored/campaign.json --recompute
```

## Journey B — manufacturing resolution and feedback on a gradient

In **1. Run demonstration**, select representative 31 kg/m² mass ceiling, 0.005 m layer resolution, 0.25 feed step and feedback enabled. Keep or adjust the bounded supported brief/mesh/budget. The same accepted WP4 code maps intended gradient to estimated achieved fields, checks mass constraints and numerical qualification, revises a constituent fraction when the supported binding mass feedback is present, and stops with a documented reason. Use a *new plain JSON filename* for every run.

Choose **3. Inspect feedback and trade-offs**, reopen the verified dossier and inspect candidate rows, exclusions, numerical-quality status, objective directions/units and strictly computed intra-WP4 Pareto. Choose a candidate for its intended/estimated inputs, evaluation, balances, constraint feedback and hashes. No candidate is declared physically feasible; scenario feasible means conditional on the synthetic inputs and process model.

Choose **4. Restore and replay** to verify/recompute, download the full immutable original JSON, import to a distinct filename and replay. Shutdown Streamlit and restart; re-enter the original/recovered path. For actual separate Python process:

```sh
PYTHONPATH=foundation .venv-foundation/bin/python -c "import json,sys;from material_core.wp5_service import replay;print(json.dumps(replay(sys.argv[1])))" d1-workspace/d1-example.json
```

Try the **Infeasible mass limit** preset (1 kg/m²), and the resolution sensitivity preset. Ineligible or unresolved candidates remain excluded even if some numerical objective appears favourable. Existing WP5 journal cancellation/recovery remains available through the original `foundation/wp5_app.py`, not the simplified D1 UI. For ZIP/JSON integrity challenges, never overwrite original evidence.

## Fully reproducible example-evidence build

```sh
PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py wp7-evidence --elements 4096 --budget 9
```

Produces gradient feedback and no-feasible WP4 dossiers, a nine-slot mixed-architecture WP3 ledger/run-store, portable WP3 ZIP, extracted/restored copy and `example-manifest.json` summarising objectives, candidate counts, source hashes and **real separate-process replays**. New directory required; do not rerun over old evidence. The GitHub Actions workflow archives generated files and per-file SHA256SUMS when its step actually succeeds.

## Scientific status

The accepted numerical model is bounded thermal transmission, areal mass and *tensile thermal mismatch*, not complete thermo-mechanical residual stress. WP4 layer/feed mapping is assumed rather than measured. There is no validated mixing lag, porosity, shrinkage, sintering, CFD, process-history residual stress or achieved-state uncertainty model. WP3 search is not proof of global optimality or algorithmic superiority. WP7 Gate 3 needs an independent reviewer; no production recommendation or V1 statement is authorised.
