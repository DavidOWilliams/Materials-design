# D1 v0.2 — Independent Re-Review of Recovery Confirmation Integrity Correction

**Date:** 30 October 2026  
**Independent verdict:** **ACCEPTED — TARGETED CORRECTION.**  
**Finding:** **D1-V02-IR25-01 — CLOSED BY INDEPENDENT REVIEW.**  
**Authority:** This is independent source-pinned testing; it does NOT authorise a merge, release, tag, deployment, or amendment to integration PR #24.

## A. Immutable source and evidence identities

| Role | Exact identity |
|---|---|
| Original independently accepted v0.2 SHA | `d9e63ea468294eba4fc25493395ad68d60edf9a5` |
| First correction / historical failing reviewer source | `ef06a529bdbdda7d4a2bd43d532ad54e4c266696` |
| **New corrected source accepted** | **`8ba23e859e920bcd7dbf19b87f2f07ddeeb4c62a`** |
| Actual implementation D1 CI merge checkout | `0e30910adfa5919abaf9e847f44c22ffc76c9442` |
| Later documentation-only PR #26 commit | `1f9c4dc6a0f177a2ded486e8598cc45fb0a0313b` |
| Correction PR (draft/unmerged) | https://github.com/DavidOWilliams/Materials-design/pull/26 |
| Original independent negative review | https://github.com/DavidOWilliams/Materials-design/pull/27 |
| Current independent review branch | `independent/d1-v02-ir25-rereview-2026-10-30` |
| **Actual independent execution** | https://github.com/DavidOWilliams/Materials-design/actions/runs/41089182257 (job `124178222628`; **SUCCESS**) |
| Actual reviewer source checkout | `8f047567cfc787bb0de3dc0dd90124c033cbcec2` |
| Independent reviewer artifact | `12993441777` ZIP SHA256 `3edfd431602a3bb8aecd130cbba541d095ce02a572000577f5e4f9c5aeb4b635`; **39/39** SHA256SUMS verified |
| Implementation D1 v0.2 artifact | `12991415168` ZIP SHA256 `460b147a560e1491d3501a18a3e2b23eedc17d2b931e5f666282ab2747cde48c`; **161/161** SHA256SUMS verified |

The diff between first correction and the new tested correction modifies only `foundation/wp7_app.py`, `foundation/tests/wp7_ir_browser_acceptance.py`, `.github/workflows/d1-v02-ui-verification.yml`, adds `foundation/ui_tests/test_d1_v02_recovery_status_integrity.py` and the implementation handover. The exact new tested source to documentation HEAD diff adds only `foundation/D1_V02_RECOVERY_CONFIRMATION_INTEGRITY_CORRECTION_REPORT.md`. No `foundation/material_core`, accepted scientific/evidence contracts, Pareto, solver code or dependencies were modified. Reviewer branch adds only reviewer scripts, notes and workflows; source-diff file `reviewer-only-diff.txt` included in artifact.

## B. Root-cause verification and corrected behaviour

**Original finding, independently reproduced earlier:** first persistent-status fix kept `d1_recovery_status` and displayed green merely while both filenames existed; after corrupting recovered `*.handoff.json`, `verify_handoff` rejected it, but the GUI still showed `Recovered original selected design and verified source lineage`. Original review [41069060796](https://github.com/DavidOWilliams/Materials-design/actions/runs/41069060796), screenshot `04-tampered-companion-rerender.png`; finding IR25-01 OPEN.

**New change:** every Streamlit rerender with a saved `d1_recovery_status` invokes the accepted authoritative `verify_handoff(recovery_status["dossier"])`. A non-True return or exception clears the saved success and displays the warning `Previously recovered dossier can no longer be verified`. Initial success still occurs only after `recover_checkpointed_handoff` and `verify_handoff` complete. A new attempted recovery clears prior status first. The optional `summary` render is caught independently, so it cannot mask a verified completed recovery. No weaker existence-only/hash substitute is used.

**Verdict:** scientifically unchanged and fail-closed. The verifier can reopen source run/ledger and dossier on every rerender, which adds integrity checking overhead for the selected recovery status, but no numerical solver rerun was observed; performance beyond the bounded demonstration was not benchmarked.

## C. R1–R5 final disposition

| Gate | Verdict | Independently established |
|---|---|---|
| **R1 — Root cause and correction integrity** | **PASS** | Code now uses authoritative `verify_handoff` on every persistent-status display. On corrupt companion, current green removed and warning shown; state is cleared, so restoring bytes does not silently resurrect success. New recovery attempts invalidate old status; optional chart failure separate. |
| **R2 — Live real Chromium adverse case** | **PASS** | Fresh real Streamlit server, Python 3.12.15, pinned Streamlit 1.40.2 and Chromium/Playwright 1.56.0. Valid WP3→WP4 recovery and immediate green, ordinary rerender green, corrupt companion => verifier failure and **green absent / warning visible**, second rerender and restored bytes => old green still absent, fresh independent browser session reopens saved dossier. |
| **R3 — Recovery, replay, immutability** | **PASS** | New immutable recovered JSON and companion verified, separate Python-process numerical replay passed, source WP3 ledger/original WP4 dossier/journal hashes remained unchanged, existing-output and missing-journal rejected, corrupt companion fails authoritative check. Disposable deliberate corruption restored after adverse challenge; good evidence preserved. |
| **R4 — Scientific and regression preservation** | **PASS (bounded)** | No science/eligibility/model/dossier-contract change. All corrected-source WP3, WP4, WP7 and D1 workflows green at job level; independent focused **16 passed**. Developer D1 workflow showed identical WP3 intended-state Pareto/proposals and WP4 feedback/numerical objectives against `d1-v0.1.0`. |
| **R5 — Provenance and evidence integrity** | **PASS** | Exact implementation vs documentation SHA distinguished; independent original artifact and new reviewer archive outer SHA256 checks and all **161/161** and **39/39** manifest entries verified; logs and four screenshots captured; historical adverse failure preserved. |

**Overall: ACCEPTED — TARGETED CORRECTION. D1-V02-IR25-01 CLOSED BY INDEPENDENT REVIEW.**

## D. Independently executed browser challenges (not merely developer CI)

**Executed command:** `PYTHONPATH=foundation .venv-foundation/bin/python review/d1_v02_ir25_independent_chromium.py` in fresh GitHub Actions runner. A new Streamlit process on localhost:8536 and real Chromium interacted with the app. Source application exact new correction `8ba23e...`; reviewer checkout `8f047...` differs only in review scripts/config.

| Test | Actual execution & result |
|---|---|
| **R2-T01** | Created WP3 campaign, selected compatible A/B gradient, executed WP4 handoff and checkpoint; recovery produced verified new dossier and visible success — **PASS real Chromium** |
| **R2-T02** | Clicked checkpoint-inspection control to trigger rerender; valid recovered evidence remained verified and green confirmation stayed visible — **PASS real Chromium** |
| **R2-T03** | Corrupted `selected-wp4-recovered.json.handoff.json` `sha256` while both files existed; `verify_handoff` raised integrity mismatch; clicked unrelated control and waited for warning and **zero green success** — **PASS real Chromium** |
| **R2-T04/T05** | After damaged state was invalidated, restored original companion bytes and retriggered Streamlit rerender; stale green success did not reappear — **PASS real Chromium** |
| **R2-T06** | New independent browser context reopened and inspected recovered WP4 evidence before the adverse mutation — **PASS real Chromium** |
| **R3 missing journal, existing target, corrupt companion** | Actual backend calls rejected missing journal `FileNotFoundError`, existing output `FileExistsError`, mutated companion `ValueError` — **PASS backend** |
| **R3 replay and source hashes** | New separate Python-process `verify_handoff` and `replay` passed; original source files hash-identical — **PASS actual subprocess/backend** |
| **R4 focused regressions** | `pytest foundation/tests/test_wp7_ir01_ir04.py foundation/tests/test_d1_visuals.py foundation/ui_tests/test_d1_v02_recovery_status_integrity.py -q` — **16 passed** on independent run |
| **AppTest new developer cases** | Six focused `foundation/ui_tests/test_d1_v02_recovery_status_integrity.py` cases exercised in implementation CI; independent focused suite also reran them, including missing dossier, missing companion, tampered companion, modified dossier, failed attempt, optional-summary failure — **PASS AppTest** |

**Independent logs:**
- `REVIEW_PASS R2 R3 normal_browser_restore_rerender_fresh_session`
- `REVIEW_REJECTED tampered_companion ValueError Handoff manifest integrity mismatch`
- `REVIEW_PASS R2_T03 corrupted_companion_green_absent_warning_visible {"success_visible":false,"warning_visible":true,"verify_handoff":"rejected"}`
- `REVIEW_PASS R2_T04_T05 stale_status_does_not_return_after_repair`
- `16 passed in 6.27s`.

**Screenshot evidence in artifact `12993441777`:**
- `browser/01-confirmed-recovery.png` — valid success.
- `browser/02-after-rerender.png` — valid persistent success.
- `browser/03-fresh-context.png` — fresh context can reopen saved WP4.
- `browser/04-tampered-companion-rerender.png` — corrupt current provenance, no green verified claim, warning.

**Original file hashes before mutation from independent run:**
- recovered JSON: `1754d2b85d2e024054a80c3cfaefc31bd8c0c7b9d128fa1766523806502323b3`
- recovered companion: `201a2781fc9a51be53b9894053f078add90194324c67c93be688b0e0e70568bd`
- checkpoint journal: `dac7f482ee2fcaa1bfd1f28fde85dcaac61f670ef52099839292f4b2fa09e526`
- original WP3 ledger: `9371c70f572654f2a2630415205da2bbd82a870fb405565cb91d32a43783dd70`.

## E. Corrected implementation qualification reviewed (not a substitute for above)

- WP3: https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638465 — **all 4 jobs passed**.
- WP4: https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638732 — **job passed**.
- WP7: https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638752 — **job passed**.
- D1 v0.2: https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638967 — **job passed**. Source merge checkout `0e30910adfa5919abaf9e847f44c22ffc76c9442`; report `PASS: identical WP3 intended-state Pareto/proposal and WP4 feedback/numerical objective outcomes`, and browser handoff screenshot `browser-handoff/wp7-ir25-tampered-companion-warning.png`.

The implementation artifact `12991415168` ZIP SHA256 `460b147a560e1491d3501a18a3e2b23eedc17d2b931e5f666282ab2747cde48c` was downloaded and all **161/161** internal SHA256SUMS entries rehashed independently. New independent ZIP `12993441777` SHA256 `3edfd431602a3bb8aecd130cbba541d095ce02a572000577f5e4f9c5aeb4b635` similarly **39/39** internal entries passed. Neither archive is solely accepted on metadata digest.

Historical first correction independent run `41069060796` remains the documented original failure. Two initial attempts of the new *reviewer's* independently authored test runner failed while the UI still showed `RUNNING` — reviewer wrongly sampled the green-status locator before the Streamlit rerender completed. The screenshot/runner evidence was preserved; after changing only the reviewer assertion to wait for zero green messages, the final run `41089182257` passed. These were reviewer synchronization mistakes, not application findings.

## F. Findings register and residual limitations

| ID | Severity | Description | Disposition |
|---|---|---|---|
| **D1-V02-IR25-01** | Previously major, release-blocking | Stale green 'verified' after corrupted `*.handoff.json`. Reproduced original failure at `ef06a...`, independently verified new corrective behaviour at `8ba23e...`. | **CLOSED BY INDEPENDENT REVIEW** |
| **D1-V02-IR25-02** | Informational | Transient success after optional summary refresh originally fixed; now green persists only with verifiable current dossier. | **CLOSED** |
| **D1-V02-IR25-03** | Informational | Source, journal and numerical replay preserved; no accepted physics/eligibility changes. | **PASS / CLOSED** |
| **D1-V02-IR25-RV01** | Reviewer test-harness history | First rerender assertion sampled live Streamlit page during RUNNING and falsely detected stale status; corrected by waiting for completed UI state. | **CLOSED — reviewer fixture**, historical failed runs retained |

Residual bounded limitations: No measured ceramic achieved state or V1 validation, no general engineering production qualification, and no full assistive-tech human accessibility test established. Live authoritative provenance verification on each recovery-status rerender can add filesystem/read overhead; bounded case passed, high-volume latency not profiled. This is not a blocker for bounded internal D1 v0.2 integration.

## G. Recommendation and controls

**ACCEPTED — TARGETED CORRECTION.** The controlled release-governance team may **reconcile exact tested corrected source `8ba23e859e920bcd7dbf19b87f2f07ddeeb4c62a` into integration PR #24**, preserving later documentation-only history and original failures. Re-run controlled integration source-equivalence, exact merge-tree qualification, browser restoration/negative verification and evidence hashes at the resulting integration SHA. Do not automatically merge PR #26 or any historical review PRs. No tag, release, deployment or owner-approval presumption. No modifications were made to `main`, PR #24 or implementation source by the reviewer.
