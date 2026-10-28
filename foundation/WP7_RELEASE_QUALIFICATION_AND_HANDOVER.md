# WP7 Gate 1–3 qualification and independent reviewer handover — OPEN

Date: 28 October 2026. Accepted WP6 source: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`. WP7 implementation branch: `wp7-d1-app-implementation-2026-10-28` (separate from governance PR #12 and workflow PR #13). **These notes are not a test result or independent review.** Do not copy the WP6 PASSES to WP7.

## Required Gate 1 execution
- Python 3.12 fresh checkout and `bash foundation/setup.sh` plus Streamlit pin, environment inventory, `pip check` and startup.
- `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp7_d1_demo.py -vv` exercises actual Streamlit AppTest widgets; this is an actual application-testing harness, not a browser test.
- Launch real Streamlit, use browser to run all three presets, inspect/trade-offs/select/export, close/restart, restore/replay; screenshot/video and browser test record. Existing `foundation/tests/wp5_browser_acceptance.py` tests the *WP5* interface only and cannot count as WP7 browser PASS.
- Reproduce WP6, WP3/WP4 and WP1/WP2 retained numerical checks at **exact** WP7 implementation source.

## Required Gate 2 challenge evidence
- Valid 31 kg/m² default, 1 kg/m² infeasible; vary layer/feed/mesh and supported brief budget (do not generalise unqualified mesh).
- Reject malformed/unsupported brief, invalid budget, existing dossier path, invalid import destination and forged checksum.
- Assert no infeasible/unresolved record is Pareto eligible. Compare preserved numeric outputs to accepted WP6 reference; test clean-run repeatability, separate-process replay, cancellation and durable journal recovery using existing WP5 interfaces. Capture raw logs and working dossier.
- Reproducibility manifest must include exact checkout HEAD and source diff from WP6, OS/Python `pip freeze`, setup logs, independent-run stdout, SHA256 for every JSON, archived evidence, workflow job SHA and URL.

## Gate 3 independent review checklist
- Independently verify exact candidate SHA and diff vs WP6, assess any scientific or eligibility interpretation changes, verify the *actual* WP7 UI and challenge logs, reproduce restore and independent replay, verify archive hashes and documentation.
- Resolve the **high-severity multi-architecture application gap**: WP7 as currently implemented only provides WP4 gradient sequence; homogeneous and layered WP2 references are not selectable in the WP7 app. D1 checklist #1 remains open.
- Resolve whether intended representative scenario actually produced more than one candidate; if not, do not claim a multi-candidate Pareto comparison. Assess saved example dossier availability, full numerical environment and physical limitations.
- Do not mark independent acceptance before the independent reviewer signs finding dispositions. No release tag or merge is authorised.

## Evidence manifest skeleton — fill from executed runs only
- Proposed tested source SHA: **NOT YET QUALIFIED**
- Gate 1 Streamlit AppTest result: **NOT YET EXECUTED**
- Gate 1 real browser result: **NOT YET EXECUTED**
- Gate 2 numerical/regression result: **NOT YET EXECUTED**
- Gate 2 separate-process replay: **NOT YET EXECUTED**
- D1 saved example dossier and SHA256: **NOT YET EXECUTED/ARCHIVED**
- Exact-source Actions run and artifact ID: **NOT YET AVAILABLE**
- Independent release disposition: **NOT ACCEPTED**

Historical verified WP6 evidence remains unaltered: runs 40666591136, 40668433992; artifact 12807606181.

**Disposition:** WP7 implementation started, incomplete candidate and evidence package. **NOT READY for independent WP7 release review.** Do not self-declare Gates 1–3.
