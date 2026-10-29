# D1 v0.2 — Functional, scientific and browser verification report

**Implementation verification:** PASSED at the exact tested checkout SHA below. **Independent scientific acceptance:** PENDING. Draft PR #22 remains unmerged.

## Source identity

- Scientific baseline: release tag `d1-v0.1.0`, accepted WP7 commit `c8f0292351553129fbcbdac3bd4f7a84a39365f9`.
- UI code-change checkpoint: `45445d85a9b42ab4d3b5d53fb6126505b180cc10`.
- CI baseline-fetch fix: `83e015779bce6f44db7c5beed53913a5def890aa`.
- **Exact tested checkout SHA:** `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c` (implementation + test correction). Later documentation-only changes are distinct and must not be reported as the tested implementation.
- **Green CI run:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174
- **Preserved evidence artifact:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174/artifacts/12934327177
- **Uploaded artifact ZIP SHA256:** `f6f891aa72c458cfc59596968bfc0c6f6980185445498f9e64d2b5487d75feb9`.

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
| Final source `2bc11618ed56` display unit tests | PASS — 7 tests, exit code 0 | [Green CI 40957223174](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174) |
| Final source complete foundation test suite | PASS — 342 tests, one warning, exit code 0 | Same green CI run |
| Final source exact WP3/WP4 comparison to tagged release | PASS — identical intended Pareto/proposals and WP4 feedback/objectives, exit code 0 | Same run; baseline-compare JSON and log |
| Final source full-resolution example generation | PASS — 4096 elements, nine-proposal example, exit code 0 | Same run; archived dossiers |
| Final source Chromium four-tab first-user journey | PASS — real browser interaction, evidence collision, screenshots, restored replay and narrow viewport, exit code 0 | Same run; `browser/` screenshot folder and browser log |
| Final source Chromium selected-gradient handoff / checkpoint / recovery | PASS — real WP3-to-WP4 handoff, verified companion and replay, checkpoint journal and recovery, exit code 0 | Same run; `browser-handoff/` screenshots and browser-handoff log |
| SHA256 manifest and artifact upload | PASS — artifact 12934327177, zip digest above | Same run; `SHA256SUMS` manifest |

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

**Implementation team verification PASSED at `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c`.** This includes the required scientific, baseline-comparison and major browser journeys. **Independent acceptance remains PENDING**: the external reviewer must separately inspect chart/source accuracy, scenario challenges, accessibility, exact evidence hashes and known medium/low limitations. No source was merged or released.
