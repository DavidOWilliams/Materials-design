# D1 v0.2 — Targeted Browser Recovery Correction and Verification

**Date:** 30 October 2026  
**Issue:** [#25](https://github.com/DavidOWilliams/Materials-design/issues/25)  
**Correction PR:** [#26](https://github.com/DavidOWilliams/Materials-design/pull/26) — draft; not merged  
**Disposition:** **READY FOR INDEPENDENT CORRECTION REVIEW**; no independent acceptance asserted.

## A. Root-cause diagnosis

Independently accepted base: `d9e63ea468294eba4fc25493395ad68d60edf9a5`. Original pre-merge failure at integration candidate `ef62b682910fb0ef438377d46e118e072b0f00d7`:

- [Release 41050841938](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050841938), archived failed evidence **12974463829**.
- [D1 UI 41050842001](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050842001), archived failed evidence **12974174453**.
- [WP7 41050841935](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050841935), archived failed evidence **12974059614**.

All three failed real Chromium `wp7_ir_browser_acceptance.py` at browser-visible text `Recovered original selected design`; original errors were `AssertionError: element(s) not found`. The failed archived workspaces contain `selected-wp4-recovered.json`, `selected-wp4-recovered.json.handoff.json`, original journal, immutable manifest and source ledger. They do **not** alone prove a successful UI confirmation. The downloaded artifacts' SHA256SUMS verified **165/165**, **158/158** and **98/98** file entries respectively. The ZIP checksums independently matched GitHub:

- `12974463829` — `7d5332d6c183349101ba9c598428d50f48ac3beb6bbe2ca9e6a8ce6fe504618f`.
- `12974174453` — `e58a63f6a232e4d513e206be84598a54ce92900561fd833a0cdddfae896f23b0`.
- `12974059614` — `18dfcb84aa71da3fa88e83e509738a9b662d746c0b525efd9be6d22c27303399`.

**Supported diagnosis:** recovery writes and provenance creation can complete while the original user-facing `st.success` is transient: it lived only inside the button execution branch and could disappear on rerender. The success message was also placed after the optional dossier-summary refresh, so downstream display work could suppress/delay it. The evidence supports a browser/session-state observation issue, *not* a defect in WP7 recovery physics. A single exclusive cause for every historical timeout cannot be proven from the original screenshots/logs; CI runtime/timing variation remains possible. The prior accepted v0.2 workflow passed, while controlled integration and an intermediate WP7 correction run failed on this UI assertion; a subsequent diagnostic correction run succeeded.

## B. Minimal correction

Dedicated branch `fix/d1-v02-browser-recovery-confirmation-2026-10-30`, created directly from independently accepted commit `d9e63ea468294eba4fc25493395ad68d60edf9a5`.

**Exact tested correction head:** `ef06a529bdbdda7d4a2bd43d532ad54e4c266696`.

Changed only these three paths:

1. `foundation/wp7_app.py` — persist a path-identified recovery success status in Streamlit session state after `recover_checkpointed_handoff` and `verify_handoff` complete. Display durable confirmation on subsequent rerenders; clear status when a new recovery attempt starts. Confirm successful recovery independently of optional follow-on `summary` panel refresh; if that refresh fails, show an actionable warning rather than withdrawing the verified recovery success. A missing dossier or sidecar produces a warning, not a false confirmation.
2. `foundation/tests/wp7_ir_browser_acceptance.py` — retain the browser-visible success assertion, force a second Streamlit rerender and assert the message is still visible, hash-check original WP4 dossier/journal/WP3 ledger, assert recovered `.handoff.json`, verify `verify_handoff`, replay in a **separate Python process**, and reopen the recovered dossier from a fresh Chromium browser context. On a browser assertion failure, preserve a screenshot and DOM text for diagnosis.
3. `.github/workflows/d1-v02-ui-verification.yml` — narrow trigger extension for this isolated correction branch / its PR against the D1 development branch to ensure the existing full Chromium and regression workflow actually executes; no dependency or test semantics changes.

No `foundation/material_core` module, accepted numeric formulation, scientific status, chart or objective/Pareto calculation, saved baseline, release tag or PR #24 governance document was modified.

## C. Final execution and provenance

The full corrected-source CI suite passed:

| Workflow | Run / actual outcome | Preserved evidence |
|---|---|---|
| [WP3 qualification 41059744665](https://github.com/DavidOWilliams/Materials-design/actions/runs/41059744665) | **All four jobs SUCCESS**, contract/vertical science **359 passed / 2 skipped**; additional qualification tests executed | artifact **12978950786**, SHA256 `6a26bc236516d835a1edf818d19038a3798b14b537a647d5868e3e0bdf3f7c36`; branch-head artifact **12978940918** |
| [WP4 integration 41059744717](https://github.com/DavidOWilliams/Materials-design/actions/runs/41059744717) | **wp4-direct-branch SUCCESS**, scientific, browser and recovery stages | artifact **12978468692**, SHA256 `063b949e1445ed56a22a8bf23ee419e21294b53f7bd9a2f7354921695b541786` |
| [WP7 exact-source 41059744932](https://github.com/DavidOWilliams/Materials-design/actions/runs/41059744932) | **qualify SUCCESS**; included **367 passed, one warning** full regression and accepted browser recovery/lineage | artifact **12978786901**, SHA256 `e9a7636381232db30a76685851e28265c7d656852d51da1a5baa6d94747bd752` |
| [Dedicated D1 41059745106](https://github.com/DavidOWilliams/Materials-design/actions/runs/41059745106) | **verify SUCCESS**; visual unit tests **7 passed**, foundation **339 passed/1 warning**, Streamlit UI collision **3 passed/1 warning**, exact v0.1.0 WP3/WP4 comparison **identical**, full-resolution example generation, first-user Chromium, strengthened recovery and new-context reopened screenshot | artifact **12978831877**, SHA256 `c6374d87d4b56cc3b7b2045a020b93671a1fea831c6d898b243c5435e2949130` |

**Source identities:** The correction-branch source head is `ef06a529bdbdda7d4a2bd43d532ad54e4c266696`. Dedicated D1 run `41059745106` recorded ephemeral PR-merge checkout `128d9a200260969b86ed2ff3f69497b8674b3320` in `tested-source-sha.txt`. GitHub blob comparison confirmed the exact same `foundation/wp7_app.py`, `foundation/tests/wp7_ir_browser_acceptance.py`, dedicated D1 workflow and unchanged WP7 handoff scientific module at the branch head and CI merge checkout. The WP7 qualification log references the branch head SHA. Do not substitute the merge checkout SHA for the branch SHA.

**Independent evidence integrity check:** The downloaded final D1 artifact `12978831877` ZIP SHA256 matched GitHub and all **160/160** SHA256SUMS entries matched bytes. It contains `wp7-ir04-browser.png` and `wp7-ir04-reopened-new-session.png`, browser logs, source identity, environment versions, exact baseline JSON and immutable generated dossiers. Previous failed CI runs and evidence remain archived without alteration. An intermediate correction run [41058437737](https://github.com/DavidOWilliams/Materials-design/actions/runs/41058437737) still failed the confirmation assertion and is retained; later [41059447906](https://github.com/DavidOWilliams/Materials-design/actions/runs/41059447906) passed after the persistent status test change, and the final exact-source runs above passed after decoupling from the summary refresh.

**Environment:** GitHub Actions Ubuntu runner, Python 3.12, pinned foundation dependencies, Streamlit `1.40.2`, Playwright Chromium with installed browser dependencies. Actual dependency freeze is inside the evidence archive; no dependency versions changed by this correction.

## D. Preservation and limitations

- WP2–WP7 numerical/eligible/Pareto/provenance/replay algorithms remain byte-identical at tested branch relative to accepted source.
- WP3 intended-state and WP4 synthetic estimated-achieved-state status remain separate; no experimental claim is introduced.
- Final exact-source rerun confirms accepted WP3/WP4 baseline numerical comparison remained identical.
- The recovered dossier and source companion verify independently, with separate-process replay; existing dossier, checkpoint journal and source ledger unchanged according to browser test SHA256 hashes.
- Corrupt/missing source manifest and invalid inputs retain the accepted backend fail-closed behaviour; the present narrow correction does not change these validations. The complete recovery/foundation suites executed, but this report does not claim that every possible corrupted browser input was separately exercised in Chromium.
- Transient message timing cannot be retrospectively reconstructed definitively from original failed runs; preserving a verified recovery status and decoupling it from an optional UI refresh is the bounded remedy supported by source inspection, archived failures, successful real-browser tests and independent process replay.

## E. Independent-review handover

**Implementation engineer finding:** corrected and verified; **formal acceptance pending**.

The independent reviewer should check: the three-path diff relative to accepted `d9e63ea...`, the prior failed artifacts and actual browser DOM/screenshot evidence; tested branch and PR-merge SHA distinction; successful D1 and WP7 browser visible recovery including rerender and fresh browser session; original immutable source hashes; recovered handoff source lineage and separate-process replay; unchanged numerical baselines; and all final workflow job conclusions. Record if any prior Gate 1–3 finding needs renewed qualification. Do not merge PR #26, PR #24 or publish a release without programme-owner authorisation.

**Final disposition: READY FOR INDEPENDENT CORRECTION REVIEW.**
