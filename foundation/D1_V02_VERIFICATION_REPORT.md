# D1 v0.2 — Functional, scientific and browser verification report

**Status at draft creation:** NOT VERIFIED for independent acceptance. This report records real observed CI output; later results must be added explicitly. Draft PR #22 is not merged.

## Source identity

- Scientific baseline: release tag `d1-v0.1.0`, accepted WP7 commit `c8f0292351553129fbcbdac3bd4f7a84a39365f9`.
- UI code-change checkpoint: `45445d85a9b42ab4d3b5d53fb6126505b180cc10`.
- CI baseline-fetch fix: `83e015779bce6f44db7c5beed53913a5def890aa`.
- Subsequent documentation commits change no physics; **only a completed green CI checkout SHA may be called tested**.

## Verified partial evidence

| Gate / source | Actual observed outcome | Evidence |
|---|---|---|
| Foundation UI display transforms at `945bf625` | PASS (executed) | [GitHub Actions 40953991312](https://github.com/DavidOWilliams/Materials-design/actions/runs/40953991312) |
| Foundation full scientific pytest at `945bf625` | PASS (executed) | Same run, `scientific-regression.log` in archived evidence |
| Full 4096-element, nine-proposal examples at `945bf625` | PASS (executed) | Same run, `example-generation.log` and dossiers |
| Actual Chromium initial challenge/collision at `945bf625` | PARTIAL, then failed due outdated *test selector*, not evidence overwrite | Same run, screenshots `01-challenge.png`, `02-collision.png`, browser logs |
| WP7 Streamlit interaction, numerical/application regression, separate-process replay at `945bf625` | PASS (executed) | [WP7 40953991247](https://github.com/DavidOWilliams/Materials-design/actions/runs/40953991247) |
| Existing WP7 real-browser test at `945bf625` | FAIL due outdated page-title selector. No acceptance claim | Same WP7 run |
| Deterministic v0.1/v0.2 numeric comparison at `dbbac04c` | NOT EXECUTED: shallow checkout lacked release tag and failed before comparison. Workflow corrected at `83e01577` | [CI 40954823890](https://github.com/DavidOWilliams/Materials-design/actions/runs/40954823890) |
| Final source `83e01577` full test and browser gates | PENDING as of initial drafting; check [CI 40955414384](https://github.com/DavidOWilliams/Materials-design/actions/runs/40955414384) | Must obtain final job conclusion and logs |

## Immutability challenge evidence

The reported pre-existing `d1-example.json` causes expected backend `FileExistsError` under the accepted immutable evidence rules. UI correction now checks before execution, shows a user-readable conflict and allows existing dossier inspection or a fresh unused filename. The suggested-name callback uses Streamlit's supported `on_click` state-update timing. The backend remains the final atomic protection against collision races.

The same preflight pattern covers the WP3 campaign directory, WP4 handoff dossier plus companion, checkpoint journal with manifest and attempts sidecars, recovered dossier, new ZIP destination and copied dossier. A new run never reassigns the ID of previous saved evidence.

## Tests and limitations

The `foundation/tests/test_d1_visuals.py` suite tests objective schema separation, source knots, layered interface positions, missing achieved geometry, stop messages and output conflicts. `foundation/tests/test_d1_v02_ui_collision.py` uses actual Streamlit AppTest widgets to test the reused default, suggested unused filename and WP3 campaign conflict. Existing WP1–WP7 suites are retained.

The dedicated Playwright browser script tests desktop/narrow Chromium, immutable collision, new WP4 run, WP3 creation, separate Pareto charts, Tab4 import/replay and screenshot output. The WP7 IR browser script separately tests compatible A/B handoff, cancellation journal and recovery. These are **test definitions**; their completed final-source execution must be confirmed from Actions logs.

No measured process state, real manufacturing feasibility, ceramic certification, full 3D material physics or combined WP3/WP4 Pareto is established. The four inherited tabs are retained, not a complete seven-stage navigation replacement. Direct chart-click selection and broader formal accessibility audit remain outstanding.

## Evidence archive and integrity

The dedicated CI workflow creates `/tmp/d1-v02-verification` with source SHA, Python version, `pip freeze`, exact stdout logs, source-comparison JSON, examples, actual Chromium screenshots and a sorted SHA256SUMS manifest. It uploads a `d1-v02-ui-verification` GitHub Actions artifact even if a test fails. Each report must cite its exact run rather than borrowing success from earlier commits.

## Acceptance decision

**NOT VERIFIED pending successful browser and exact-baseline outcome comparison on one final SHA.** No unresolved critical/high defects may be waived by a visual demonstration alone. Independent reviewer must separately evaluate evidence and record an explicit disposition.
