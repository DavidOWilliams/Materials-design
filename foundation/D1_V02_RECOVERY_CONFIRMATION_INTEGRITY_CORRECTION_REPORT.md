# D1 v0.2 — Recovery Confirmation Integrity Correction and Verification Report

**Date:** 30 October 2026  
**Finding:** D1-V02-IR25-01, independently raised in [PR #27](https://github.com/DavidOWilliams/Materials-design/pull/27)  
**Implementation disposition:** **CORRECTED AND VERIFIED BY IMPLEMENTATION TEAM; TARGETED INDEPENDENT RE-REVIEW REQUIRED**  
**Correction PR:** [#26](https://github.com/DavidOWilliams/Materials-design/pull/26) — draft, unmerged  
**Exact tested implementation SHA:** `8ba23e859e920bcd7dbf19b87f2f07ddeeb4c62a`  
**Actual dedicated D1 CI merge checkout:** `0e30910adfa5919abaf9e847f44c22ffc76c9442`  
**Acceptance source predecessor:** `d9e63ea468294eba4fc25493395ad68d60edf9a5`  
**Original Issue #25 correction:** `ef06a529bdbdda7d4a2bd43d532ad54e4c266696`  
**Later original handover commit:** `65c7cfa1af5bfe329b078a12b51a52bdc7bc2b2e`.

## A. Root cause and evidence

The independent reviewer reproduced: initial valid recovery and `verify_handoff` succeeded; after a rerender the green confirmation correctly persisted; when the saved `selected-wp4-recovered.json.handoff.json` SHA-256 field was deliberately altered, the authoritative verifier rejected it (`ValueError: Handoff manifest integrity mismatch`), but the application still displayed green on the next rerender. The previous UI `d1_recovery_status` held only output filenames and checked `is_file()` for both. Existence of a dossier and companion is not continued evidence integrity. This was a UI truthfulness/integrity-status defect, not an accepted WP7 scientific or provenance-verifier defect.

Independent reproduction: [reviewer run 41069060796](https://github.com/DavidOWilliams/Materials-design/actions/runs/41069060796), artifact **12984411586**, ZIP SHA256 `e990bdece78f1516fc7de693de66b889c897be9b0acd1269e90018feb40de2c5`, negative screenshot `browser/04-tampered-companion-rerender.png`. Reviewer R1 BLOCKED. The independent review report `review/D1_V02_ISSUE25_INDEPENDENT_BROWSER_RECOVERY_REVIEW_2026-10-30.md` is preserved unchanged.

## B. Exact correction

Only these application/test/verification paths were changed since the first correction:

1. `foundation/wp7_app.py`: on each Streamlit rerender, before displaying the stored verified-status claim, invoke the unchanged authoritative `verify_handoff(recovery_status["dossier"])`. Show green only for `verified is True`. On exception, missing evidence, source mismatch or unverified status: clear `d1_recovery_status`, show a visible warning, and leave all source/destination files unchanged. This uses the existing source-ledger, source-selection, manifest and dossier checks; no second weaker integrity contract or numerical/physics changes were added.
2. `foundation/tests/wp7_ir_browser_acceptance.py`: extend the actual Chromium selected-design/cancellation/recovery test to tamper the already verified companion, independently assert backend rejection, trigger a keyboard-accessible Streamlit rerender, assert the warning appears and the green confirmation disappears, screenshot the adverse state, restore original bytes and assert success does **not** silently return. Existing checks retain new-browser reopening, original source/journal hash immutability, `verify_handoff` and separate-process `replay`. Keyboard activation is needed because a Streamlit overlay intercepted mouse clicks in one intermediate run; genuine real-browser interaction is preserved.
3. `foundation/ui_tests/test_d1_v02_recovery_status_integrity.py`: add focused Streamlit AppTest negative cases for missing dossier, missing companion, invalid companion and modified/invalid recovered JSON, and UI-presentational tests for a failed subsequent recovery clearing stale status and optional summary refresh failure preserving a valid recovery status (the latter two use explicit presentation-only backend stubs).
4. `.github/workflows/d1-v02-ui-verification.yml`: ensure the dedicated pinned Streamlit UI test step executes the additional six adverse cases, rather than leaving them in the numerical science-only test-discovery scope.

No `foundation/material_core` module, WP2–WP7 physics/numerical/eligibility, chart data, replay or handoff contract, immutable dossier, baseline tag or dependency version was modified. `verify_handoff` performs the authoritative integrity validation, including provenance source lineage; it is more costly than file existence but intentionally fail-closed, with no new scientific recomputation rule introduced by this UI.

## C. Executed adverse challenge matrix

| Challenge | Test mode and result | Limitation |
|---|---|---|
| IR25-T01 valid recovery | **PASS real Chromium**: recovery + authoritative handoff verification before success | Synthetic D1 only |
| T02 ordinary rerender | **PASS real Chromium**: green remains for unchanged valid dossier | Session-local confirmation |
| T03 corrupt `.handoff.json` after success | **PASS real Chromium**, source-backed: verifier rejects, rerender displays warning and no green; screenshot `browser-handoff/wp7-ir25-tampered-companion-warning.png` | Original companion bytes restored afterward |
| T04 modified recovered JSON | **PASS focused Streamlit AppTest**, invalid/malformed dossier rejected from persisted status | Not an additional browser challenge on a once-valid source-backed dossier |
| T05 missing companion | **PASS focused AppTest**, warning and invalidation | Presentation negative |
| T06 missing recovered dossier | **PASS focused AppTest**, warning and invalidation | Presentation negative |
| T07 invalid/missing source lineage | Authoritative `verify_handoff` exercised by WP7/recovery regressions and source-backed browser T03; corrupted/invalid source failure behaviour unchanged | No new standalone missing-source browser manipulation executed |
| T08 failed new recovery | **PASS focused AppTest**, earlier status cleared; actual backend rejects missing journal | Existing successful status simulated via explicit UI stub |
| T09 existing destination | **PASS retained collision AppTest and first-user Chromium**; no overwrite | Accepted immutable backend rule unchanged |
| T10 new browser context | **PASS real Chromium**, recovered dossier reopened and inspected | Valid recovered evidence |
| T11 separate-process replay | **PASS real-browser test plus fresh Python subprocess**, `verify_handoff` and numerical `replay` | Synthetic D1 |
| T12 optional summary refresh error | **PASS focused AppTest**, independent UI stub makes summary raise; verified recovery success remains with separate warning | Mocked UI-only exception, not a production graphical fault |

All four invalid persisted-status AppTest parametrizations cleared the stored status and showed no green message on another rerender. The real Chromium T03 specifically reproduces the independent reviewer's exact failure sequence and does **not** merely assert files exist.

## D. Exact-source CI and numerical preservation

Final corrected-source workflows, all concluded **SUCCESS**:

| Workflow | Run | Job outcomes |
|---|---|---|
| [WP3](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638465) | `41082638465` | All four WP3 jobs SUCCESS; original, contract/vertical, branch-head and legacy |
| [WP4](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638732) | `41082638732` | `wp4-direct-branch` SUCCESS |
| [WP7](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638752) | `41082638752` | `qualify` SUCCESS, real handoff/browser recovery including T03 |
| [Dedicated D1](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638967) | `41082638967` | `verify` SUCCESS, 7 visual unit tests, 339 foundation tests (one warning), **9 explicitly run Streamlit UI tests** (one warning), deterministic v0.1.0 WP3/WP4 numerical comparison **identical**, 4096-element example, real Chromium first-user and T03/recovery/lineage |

Python **3.12.15** in the dedicated D1 run; pinned Streamlit **1.40.2**, Playwright Chromium. Exact installed dependency freeze is archived. The later documentation-only commit below is *not* the tested implementation. The D1 job recorded PR-merge SHA `0e30910adfa5919abaf9e847f44c22ffc76c9442`; GitHub blob comparison confirmed byte-identical application, browser test, Streamlit integrity test and dedicated CI workflow files at branch source `8ba23e859e920bcd7dbf19b87f2f07ddeeb4c62a`.

## E. Evidence archive and integrity

- **Final D1 artifact [12991415168](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638967/artifacts/12991415168)**, ZIP SHA256 `460b147a560e1491d3501a18a3e2b23eedc17d2b931e5f666282ab2747cde48c`. Independently rehashed the actual ZIP; **161/161** `SHA256SUMS` entries matched, zero missing/mismatches. It contains screenshots `browser-handoff/wp7-ir04-browser.png`, `wp7-ir04-reopened-new-session.png`, **`wp7-ir25-tampered-companion-warning.png`**, numerical comparisons, dossiers, logs, source SHA and Python/dependency versions.
- WP7 artifact **12991160302** from successful final correction source? **NO** — historical prior-source artifact. The correct final WP7 artifact is **12991160302?** Reviewer must rely on current final WP7 run `41082638752` and its artifact list rather than any stale ID.
- Final WP3 artifact **12989533533**, ZIP SHA256 `f837d7866939ebdc8702ff5d35d8df08fa8c4488617faab084a774e7221ed214`.
- Final WP4 artifact **12990352857**, ZIP SHA256 `51f406a526db665f125e96e25107f3241692a0af3349d7994bc553d9469c72d1`.
- Final WP7 artifact **12991160302**, ZIP SHA256 `722e2658ee64f9fd3cb6222404cbab9edbdc7528bb9804fdd5f41ca78ed567ab`.

**Historical failed attempts remain preserved without relabelling:** original Issue #25 failure workflows `41050841938`, `41050842001`, `41050841935`; reviewer negative `41069060796`; first new UI-test harness mistake `41079200534` (unsupported `.message` alert property, corrected to `.value`); first added browser adverse run `41080784436` (pointer interception on existing checkpoint button, corrected to native keyboard focus/Enter). Earlier green source `a65fdd323bd8b165e6ef65ad9f87f0749cac60eb` passed source-backed Chromium after correction but predates the final browser keyboard-coverage amendment. None is substituted for the exact final green run.

## F. Independent-review decision request

**Implementation team disposition: D1-V02-IR25-01 CORRECTED and source-pinned VERIFIED. Independent R1 closure remains PENDING.**

Request the independent reviewer independently repeat the two central browser paths at the **exact tested source**: (i) valid recovery, ordinary rerender and retained green confirmation; (ii) after successful recovery, corrupt the already stored companion and trigger a rerender, verifying explicit warning and no positive verified-lineage label. Independently check source and journal immutability, authoritative `verify_handoff`, fresh-process replay, screenshot provenance and the four workflow job conclusions. If those pass, reviewer may close finding and advise the controlled integration team; no automatic merge or release authority is implied.

**No PR #24, PR #27, main, tag or release was changed.**
