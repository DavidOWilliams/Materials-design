# D1 v0.2 — controlled integration and programme-owner approval dossier

**30 October 2026; PRE-MERGE candidate, not owner-approved, not tagged.** Final disposition requires *actual current candidate* CI conclusion and artifact inspection, not earlier accepted-source runs alone.

## Acceptance authority and exact identities
- Current v0.1.0 tag is an annotated tag object `8ba4331bab178bbdbef9e27cde77e1923cd7ee8e` targeting `ec4bea044858bc275a1be80c3df24be438085279`, same as current main before v0.2.
- Independently accepted corrected v0.2 implementation `d9e63ea468294eba4fc25493395ad68d60edf9a5`, source tree `f63327ed03e7b22bb8c655c2d7ec608f0b0d7bb2`.
- PR #22 later Markdown-only HEAD `f8b97b91889d61848bee7afbed80c5b3853edc23`. Reviewer branch PR #23 HEAD `6d689eab52329b57a821ca7eeac7f1cfcac3e483` is reviewer tests/CI/docs, not accepted implementation.
- Dedicated release-integration branch `d1-v0.2-controlled-integration-2026-10-30` begins directly from PR #22 documentation HEAD and accepted code; it must contain only original accepted scientific/application tree, additional release docs/governance records and the release qualification workflow. Git ancestry is directly from prior main, without merging history from PR #23 or research projects. Exact candidate HEAD/tree in PR and qualification artifact.
- GitHub compare main→accepted v0.2 enumerates 16 changed paths: v0.2 workflow, 7 implementation docs, 3 production visual/UI modules and source replacement, presentation/browser/unit/UI tests. No third-party scientific model or underlying WP2/3/4 numerical/feedback kernel modification.
- Independence: original final [review report](https://github.com/DavidOWilliams/Materials-design/blob/independent/d1-v02-scientific-display-review-2026-10-30/review/D1_V02_INDEPENDENT_SCIENTIFIC_PRESENTATION_VERIFICATION_2026-10-30.md) latest addendum; Gate 1 PASS bounded, Gate 2 PASS, Gate 3 PASS bounded, but not an approval to merge. F01 CLOSED, F02 OPEN nonblocking for bounded internal demonstration, F03 accepted synthetic limitation, F04 CLOSED and past failing evidence retained.

## Source-pinned evidence
- Independent science presentation [41046147946](https://github.com/DavidOWilliams/Materials-design/actions/runs/41046147946), artifact `12972198847`.
- Implementation [41047548183](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548183), artifact `12972374769`, external ZIP SHA256 `bc6fc216e5d6bea985d5f7017f4635b85a08bc4f98f8fad15f366d0d500053a7`, 159/159 entries rechecked independently.
- WP3 [41047548251](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548251), 359 scientific passed/2 skipped and all four jobs green; WP4 `41047548198`, WP7 `41047548148` green.
- Proposed candidate dedicated CI workflow `.github/workflows/d1-v02-release-integration.yml` asserts accepted implementation tree unchanged, source-only documentation/CI diff, exact checkout SHA, clean Python 3.12, foundation and isolated graphical tests, v0.1.0 numerical equivalence, 4096 full-resolution examples, distinct-process replay, real Chromium first-user/handoff recovery and checksummed archive.

## Scientific boundary and residual risks
WP3 intended-state architecture search and WP4 *estimated achieved-state* A/B-gradient manufacturing-feedback simulations are different evaluation contexts and their Pareto results never pool. Unknown/nonfinite and unsupported achieved-state overlays must not be promoted. No experimental ceramics validation, industrial production fitness, airworthiness certification, new scientific physics or P1/P2/P3/E1/E2/V1 claims. Four tabs retained; accessibility, assistive technology, real Codespaces/Windows/Edge and owner first-use testing remain OPEN (F02), nonblocking only for bounded **internal** integration; separate decision before wider distribution.

## Approval controls
- [x] Final original independent record and superseding 30 October Gate 3 PASS retrieved.
- [x] Accepted application SHA/tree and documentation-only later PR #22 delta confirmed.
- [x] Historical v0.1.0 tag target verified unchanged.
- [x] Controlled release branch from accepted v0.2 lineage created without P1.
- [ ] Verify exact final candidate workflow PASS and preserve artifact SHA256.
- [ ] Verify current HEAD/tree/source equivalence after final documentation commits.
- [ ] Owner separately authorises merging ONLY controlled integration PR into main.
- [ ] After merge, verify actual main checkout/tree, clean runtime, regression, exact baseline comparison, browser and archive; prepare separate post-merge decision.
- [ ] Owner separately authorises eventual `d1-v0.2.0` tag and publication/deployment. **None authorised.**

**Intended decision:** READY FOR OWNER APPROVAL only after live integration PR verification passes. Do not merge PR #22/#23 or controlled PR automatically.


---

## 30 October 2026 release qualification finding — BLOCKED for integration approval (supersedes the provisional candidate-readiness above)

**Exact candidate tested:** `ef62b682910fb0ef438377d46e118e072b0f00d7`, tree `0f68efdaf430297b3a024fb034464f97f17c7b3b`. Source-diff gate confirmed **only ten Markdown files and one CI workflow differ from independently accepted v0.2 application** `d9e63ea468294eba4fc25493395ad68d60edf9a5`; no scientific or application modification beyond accepted code.

- **PASS:** [WP3 41050841936](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050841936) and [WP4 41050841919](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050841919) all jobs green.
- **PASS within failed jobs:** exact application-tree assertion, clean Python 3.12 install, source-encoded scientific visual tests, complete foundation/UI tests, direct tagged v0.1.0 versus v0.2 WP3/WP4 numerical outcome comparison, new 4096-element dossiers and 3 separate-process replays, first-user Chromium visual/immutability journey.
- **FAIL, reproducible twice at identical source:** [dedicated integration 41050841938](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050841938), [v0.2 CI 41050842001](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050842001), [WP7 CI 41050841935](https://github.com/DavidOWilliams/Materials-design/actions/runs/41050841935). All three fail at `foundation/tests/wp7_ir_browser_acceptance.py:60`, awaiting transient visible text `Recovered original selected design` for 120s. Attempt 2 reruns at the same source failed identically. Do **not** count these full workflow executions or skipped subsequent checks as PASS.
- **What persisted:** failed run artifact `12974463829`, ZIP SHA256 `7d5332d6c183349101ba9c598428d50f48ac3beb6bbe2ca9e6a8ce6fe504618f`, internal archived manifest 165 entries valid; includes a newly saved recovered WP4 JSON, `*.handoff.json`, journal and source WP3 store. The recovered files' existence narrows but does not close the missing UI/reopen observation. Dedicated v0.2 failure artifact `12974174453`, ZIP SHA256 `e58a63f6a232e4d513e206be84598a54ce92900561fd833a0cdddfae896f23b0`, 158 entries valid. Attempt 2 archives retained separately in GitHub Actions; never erase initial failures.
- **Finding:** [issue #25](https://github.com/DavidOWilliams/Materials-design/issues/25) requests a narrowly scoped implementation/test correction and independent re-verification. The source code itself is unchanged from independent v0.2 acceptance; the failure is an observed **candidate browser verification defect**, not proof of model regression or full recovery failure. Test selector/transient Streamlit state synchronisation versus durable user confirmation must be examined and independently dispositioned; after any test/app correction the exact corrected source and full affected browser/integration workflows must be rerun.
- **Disposition:** **NOT READY FOR OWNER INTEGRATION APPROVAL** while the repeated browser gate is open. Existing independent Gate 1–3 PASS at earlier accepted source remains a historical scoped decision but cannot be automatically extended to failing exact PR #24 run. Owner approval is **not requested yet**. Preserve `d1-v0.1.0`, `main`, P1/P2/P3/E1/E2/V1 scope; **no merge, tag, publication or deployment**. V02-IR-F02 human accessibility/Edge/Codespaces remains separate OPEN/nonblocking for later distribution.

This is a documentation-only release-governance update. Subsequent docs-only branch HEAD must not be misidentified as the executable checkout `ef62b682...` used in the failing tests.


---

## D1 v0.2 Issue #25 final accepted correction — governance supersession (30 October 2026)

**Authoritative final scientific/application implementation:** `8ba23e859e920bcd7dbf19b87f2f07ddeeb4c62a`, Git tree `84513ca9aaa2d923bb3e3ff7a333eb8c131f9a93`. This supersedes the earlier original accepted v0.2 implementation `d9e63ea468294eba4fc25493395ad68d60edf9a5` **for release integration**; it does not overwrite that original acceptance. First failed recovery correction `ef06a529bdbdda7d4a2bd43d532ad54e4c266696` remains a separately recorded historical failed source. PR #26's `1f9c4dc6a0f177a2ded486e8598cc45fb0a0313b` is later documentation-only, not a tested implementation. Original independent review PR #27 BLOCKED remains preserved.

**Final independent acceptance:** [PR #28](https://github.com/DavidOWilliams/Materials-design/pull/28), `review/D1_V02_ISSUE25_FINAL_INDEPENDENT_INTEGRITY_REREVIEW_2026-10-30.md` on `independent/d1-v02-ir25-rereview-2026-10-30`. R1 root-cause/integrity PASS, R2 real Chromium adverse testing PASS, R3 recovery/replay/immutability PASS, R4 science/regression preservation PASS, R5 provenance/evidence integrity PASS. **D1-V02-IR25-01 CLOSED BY INDEPENDENT REVIEW.** First unsuccessful reviewer test `41069060796` and earlier pre-merge PR #24 failures `41050841938`, `41050842001`, `41050841935` remain historical failures, not relabelled green.

**Corrected-source author evidence:** [D1 41082638967](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638967), artifact `12991415168`, ZIP SHA256 `460b147a560e1491d3501a18a3e2b23eedc17d2b931e5f666282ab2747cde48c`, internal manifest 161/161 independently checked. [WP3 41082638465](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638465) (all four jobs), [WP4 41082638732](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638732) and [WP7 41082638752](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638752) all green. **Independent evidence:** [41089182257](https://github.com/DavidOWilliams/Materials-design/actions/runs/41089182257), artifact `12993441777`, ZIP SHA256 `3edfd431602a3bb8aecd130cbba541d095ce02a572000577f5e4f9c5aeb4b635`, manifest 39/39 independently checked; 16 focused tests pass.

**Accepted correction scope:** only browser recovery UI state verification and its integrity-focused UI/browser tests, one UI verification workflow and documentation. On rerender the existing authoritative `verify_handoff` checks current dossier+companion; invalid/corrupted evidence clears stale green success and shows a warning. Restoring previously corrupted bytes does not resurrect stale success. Fresh browser reopening, separate-process replay, immutable original WP3/WP4/journal evidence and v0.1 numerical outcome equivalence remain verified. No WP2/3/4 scientific algorithms, visual source coordinates, WP7 eligibility/provenance contracts or dependency changes.

**Controlled integration PR #24** copies the independently accepted implementation files byte-for-byte and preserves the later docs-only correction report distinctly. Its source-equivalence CI explicitly pins `8ba23e...` and checks Git blob identity for `foundation/wp7_app.py`, `foundation/tests/wp7_ir_browser_acceptance.py`, `foundation/ui_tests/test_d1_v02_recovery_status_integrity.py` and `.github/workflows/d1-v02-ui-verification.yml`; all remaining differences must be governance Markdown or the release-only workflow. **Integration checkout HEAD and full tree are determined by the final actual Actions run/PR after this appendix, NOT by an earlier failed/source checkout.**

**Pre-merge gate:** independently accepted correction is CLOSED; PR #24 integration qualification is **pending actual current-HEAD execution**. No owner approval to merge, tag, release, publish or deploy. F02 remains OPEN informational: real novice users, Windows/Edge, Codespaces and assistive-tech/accessibility require assessment before broader distribution; bounded synthetic D1 is not measured ceramics/V1 and excludes P1/P2/P3/E1/E2. WP3 intended and WP4 estimated-achieved Pareto comparisons remain separate. WP4 dossier and handoff companion require retained WP3 ledger/store or verified ZIP.
