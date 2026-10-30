# D1 v0.2 — Independent targeted browser-recovery correction review
**Date:** 30 October 2026  
**Independent reviewer:** separately tasked reviewer, did not author Issue #25 correction.  
**VERDICT: BLOCKED — FURTHER TARGETED CORRECTION REQUIRED.** A fresh independent browser journey confirms the original disappearance problem is fixed for valid persisted evidence, but reveals a **new stale-green-confirmation defect** after provenance corruption. Do not reconcile PR #26 into controlled integration PR #24 yet.

## 1. Frozen source and provenance

| Identity | Exact |
|---|---|
| Original independently accepted D1 v0.2 | `d9e63ea468294eba4fc25493395ad68d60edf9a5` |
| Tested Issue #25 correction | **`ef06a529bdbdda7d4a2bd43d532ad54e4c266696`** |
| Actual developer D1 CI merge checkout | `128d9a200260969b86ed2ff3f69497b8674b3320` (implementation handover) |
| Subsequent documentation-only commit | `65c7cfa1af5bfe329b078a12b51a52bdc7bc2b2e` |
| Implementation PR | https://github.com/DavidOWilliams/Materials-design/pull/26 (draft; unmerged) |
| Unmodified integration PR | https://github.com/DavidOWilliams/Materials-design/pull/24 |
| Independent reviewer branch/PR | `independent/d1-v02-browser-recovery-review-2026-10-30`, PR #27 |
| Reviewer-authored CI | https://github.com/DavidOWilliams/Materials-design/actions/runs/41069060796, job `124108030222`, **SUCCESS** |
| Independent review evidence artifact | `12984411586`; independently verified ZIP SHA256 `e990bdece78f1516fc7de693de66b889c897be9b0acd1269e90018feb40de2c5`; **40/40** entries of SHA256SUMS verified |

Verified exact implementation diff relative to independently accepted prior source comprises **only** `foundation/wp7_app.py`, `foundation/tests/wp7_ir_browser_acceptance.py` and `.github/workflows/d1-v02-ui-verification.yml`. Diff from corrected source to later PR HEAD is **only** `foundation/D1_V02_BROWSER_RECOVERY_CORRECTION_AND_REVIEW_HANDOVER.md`. No `foundation/material_core`, numerical, WP3/WP4 Pareto, evidential-contract or dependency edits.

The reviewer created only `review/d1_v02_recovery_independent_browser.py`, `.github/workflows/d1-v02-recovery-independent.yml` and this report on its isolated branch. PR #24, `main` and all tags remain untouched.

## 2. Root-cause analysis (R1)

**Original defect:** The prior immediate `st.success(...)` was a transient element produced within the recovery button handler and positioned before a secondary `summary(recovered_file)` chart refresh. The original failure artifacts contain `browser-handoff/selected-wp4-recovered.json` plus `*.handoff.json`, which supports successful backend recovery but not a persistent user-facing confirmation. Streamlit rerender/secondary view update is a plausible cause of disappearance; original evidence does not isolate the exact rerender event conclusively.

**Corrected behaviour:** After `recover_checkpointed_handoff` and **after** authoritative `verify_handoff(recovered_file)`, the app records `d1_recovery_status` in Streamlit session state, displays success and catches optional `summary` errors separately. Later rerenders show a persistent message while `Path(dossier).is_file() and Path(companion).is_file()`. A missing file instead produces a warning. This successfully addresses normal recovery and rerender behaviour.

**Independently observed defect:** On a completed successful browser recovery, reviewer deliberately altered the SHA field inside the **recovered** `selected-wp4-recovered.json.handoff.json`, keeping the file present. `verify_handoff(recovered_file)` correctly raised `ValueError: Handoff manifest integrity mismatch`. After the user clicked **Inspect cancellation checkpoints** to force a Streamlit rerender, the previously green **“Recovered original selected design and verified source lineage”** confirmation **remained visible**. Reviewer log exact marker:
`REVIEW_OBSERVATION stale_success_after_companion_corruption {"success_visible": true, "actual_verify_handoff": "failed", "both_files_exist": true}`.
Screenshot: artifact `12984411586`, `browser/04-tampered-companion-rerender.png`.

This is an **integrity-status display failure**, not a failure of `verify_handoff` or the scientific computation. It is **introduced by the new persistent-status logic**: mere continued existence of both files is not evidence that their hashes, original source context or entire dossier remain verified. A user could read a green claim of current verified lineage even when the current evidence is corrupt. The correction must not persist a misleading success assertion.

## 3. Independent review gates

| Gate | Decision | Evidence |
|---|---|---|
| **R1 — Root cause/correction integrity** | **FAIL** | Normal transient confirmation fixed, and initial success is gated after actual recovery + handoff verification, but a subsequent rerender shows false current green verified-lineage status after companion SHA corruption; file-existence-only check insufficient. |
| **R2 — Actual Chromium recovery** | **PASS** for valid evidence | Independent Python 3.12 + pinned Streamlit 1.40.2/Playwright 1.56.0 live Chromium generated WP3, selected original A/B gradient, created and verified WP4 dossier, checkpointed, recovered, verified success on screen, rerendered, fresh browser context reopened and inspected, screenshots in artifact. |
| **R3 — Recovery/provenance and immutability** | **PASS for backend; user-facing exception tracked in R1** | Recovered JSON/companion existed; `verify_handoff` and fresh Python-process `replay` passed; original WP4 dossier, journal and original WP3 ledger unchanged (SHA checked); missing journal, existing recovered destination and tampered companion rejected. The visual stale-status defect remains blocking. |
| **R4 — Scientific/regression preservation** | **PASS (bounded)** | No scientific module/eligibility/physics source changes. Developer WP3 run `41059744665` **4/4 jobs SUCCESS**; WP4 `41059744717`, WP7 `41059744932`, D1 v0.2 `41059745106` **SUCCESS**, job-level outcomes inspected. Fresh reviewer targeted suite **13 passed, 1 pre-existing Altair warning**. Developer D1 archive contains direct baseline comparison and full browser runs. |
| **R5 — Evidence/provenance integrity** | **PASS** | Downloaded and independently SHA256 verified implementation evidence archives: D1 `12978831877` `c6374d87d4b56cc3b7b2045a020b93671a1fea831c6d898b243c5435e2949130` with **160/160** internal hashes; WP7 `12978786901` `e9a7636381232db30a76685851e28265c7d656852d51da1a5baa6d94747bd752` with **100/100**; WP3 `12978950786` `6a26bc236516d835a1edf818d19038a3798b14b537a647d5868e3e0bdf3f7c36`; WP4 `12978468692` `063b949e1445ed56a22a8bf23ee419e21294b53f7bd9a2f7354921695b541786` (last two outer digest verified; no SHA256SUMS file in these ZIPs). Reviewer new archive `12984411586` digest above and **40/40** verified. Original failed run evidence artifact `12974463829` inspected, including recovered original dossier and companion, preserved separately. No failed history rewritten. |

## 4. Executed independent challenges and exact evidence

**Command:** `PYTHONPATH=foundation .venv-foundation/bin/python review/d1_v02_recovery_independent_browser.py` in isolated reviewer CI PR checkout (review-only additions to frozen corrected source). This runs a real Streamlit server and real Chromium, not AppTest or HTTP-only checks. Focused regressions: `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp7_ir01_ir04.py foundation/tests/test_d1_visuals.py foundation/ui_tests/test_d1_v02_ui_collision.py -q`, **13 PASSED**.

- Live-browser WP3 campaign generation and saved ledger, original A/B gradient candidate selection, WP4 handoff and `verify_handoff`: PASS.
- WP4 checkpoint journal and source evidence preserved; recovery into new immutable JSON and source-hash companion: PASS.
- Browser success immediately following recovery; success remains after unrelated Streamlit rerender with **valid files**: PASS.
- Separate-process `verify_handoff` and numerical `replay`: PASS.
- New isolated browser context reopens recovered dossier and displays WP4 results: PASS.
- Missing journal rejected with FileNotFoundError; pre-existing output rejected with FileExistsError; corrupted companion rejected with ValueError: PASS.
- **Post-verification corrupt companion, rerender, current green success label**: **FAIL** (stale positive status).
- Browser screenshot evidence `browser/01-confirmed-recovery.png`, `02-after-rerender.png`, `03-fresh-context.png`, `04-tampered-companion-rerender.png`; source ledger/other immutable artifacts in original evidence archive.

New reviewer original-hash values before intentional corruption:
`selected-wp4-recovered.json` SHA256 `1754d2b85d2e024054a80c3cfaefc31bd8c0c7b9d128fa1766523806502323b3`;
`selected-wp4-recovered.json.handoff.json` SHA256 `61a0bc1cd6686dde09b7d11a0bafb28ec1f0f8630c2dd94f9ee9dc7398753efd`;
`selected-wp4-journal.jsonl` SHA256 `dac7f482ee2fcaa1bfd1f28fde85dcaac61f670ef52099839292f4b2fa09e526`;
original `mixed-architecture/campaign.json` SHA256 `d0a29b16d9340be25c6b76782c177db4eadc8458fd17ace9aa948303e7db881c`.
The reviewer restored original companion bytes after adverse test and rechecked `verify_handoff` before archive finalisation, preserving runnable good evidence plus screenshot of failing condition.

## 5. Numbered findings / correction brief

### D1-V02-IR25-01 — MAJOR / RELEASE-BLOCKING / OPEN

- **Affected identity:** tested corrected D1 source `ef06a529...`, `foundation/wp7_app.py` `with tab_review` block; session status `d1_recovery_status`.
- **Expected:** Green verified-source-lineage confirmation after later rerenders only while the **same recovered artifact and provenance actually remain verified**; corruption must yield explicit warning or demand re-verification.
- **Actual:** With corrupted but present `*.handoff.json`, `verify_handoff` fails, yet green verified-success persists.
- **Reproduction:** Run reviewer Chromium challenge above (or reproduce via valid recovery, mutate companion `sha256` field, trigger unrelated rerender). Inspect screenshot `browser/04-tampered-companion-rerender.png` and log `REVIEW_OBSERVATION stale_success_after_companion_corruption`.
- **Impact:** Misleading state-integrity assurance to user. No observed change to numerical outputs or backend rejection.
- **Cause introduced by correction:** Yes — persistent success message is conditioned only on file existence, not on retained/reevaluated verification identity.
- **Required fix:** Narrowly alter persistent status display to fail closed. On each rerender, re-verify the stored *specific* dossier/provenance against the authority used by `verify_handoff`, or retain immutable authenticated verification identity and compare current bytes (including original source context), not mere existence. On failure clear or replace prior green status and display a clear warning. Never show green before recovery+provenance verification. Keep optional `summary` separate. Preserve source/journal immutability and avoid expensive numerical recomputation for every rerender if a verified hash/equivalence check is sufficient; if verification cannot execute, do not assert current verified lineage.
- **Challenge checks after fix:** valid confirmation survives rerenders; missing dossier and companion warn; changed/malformed companion warns; modified recovered JSON/source ledger warns; failed attempted recovery does not leave stale success; normal new browser reopening and separate-process replay pass. Repeat focused tests plus WP3/WP4/WP7 and dedicated D1 workflows at the **new exact source SHA**. Submit new evidence/archive hashes for independent re-review.
- **Disposition:** OPEN; correction by implementation team, not independent reviewer.

### D1-V02-IR25-02 — INFORMATIONAL / RESOLVED

Transient initial recovery confirmation after secondary summary rerender was addressed by persistence and separation of optional summary update; valid browser recovery/rerender and fresh context verified independently. But this must be implemented without F01's stale-integrity regression.

### D1-V02-IR25-03 — INFORMATIONAL / REPLAY AND SCIENTIFIC PRESERVATION PASS

No scientific modules changed; recovered original source and numerical replay remained verifiable, developer and reviewer regression suites passed. Historical failed browser CI and independent negative result retained.

## 6. Required next action / decision

**BLOCKED — FURTHER CORRECTION REQUIRED.** Do **not** reconcile PR #26 into PR #24 or merge/tag/release. Ask existing Issue #25 implementation chat to address only `D1-V02-IR25-01` and execute the specified adverse tests, preserving initial fix and scientific integrity. Return exact new tested SHA and CI artifacts; independent reviewer must re-execute source-pinned normal rerender plus corruption-after-success before closing R1. R2/R3/R4/R5 positive evidence remains applicable insofar as unchanged code allows, but gate R1 must be reverified. No PR approval or owner authorisation implied.
