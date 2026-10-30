# D1 integration manifest — evidence update 28 October 2026

## Immutable implementation and branches
- Accepted implementation: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- WP7 governance branch `wp7-d1-reproducible-release-2026-10-27`; draft PR #12. Later D1 register changes are **documentation only**, not retested implementation.
- Separate verification PR #13 `d1-governance-verification-2026-10-27`, not integrated.
- Default `main` contains only the CI-enablement workflow from PR #14 and its pre-existing code; accepted WP6 application source is not represented as merged to `main`.
- New workflow-only PR #15 against `main` adds separate exact-source complete replay and smoke verification. Not merged or executed.
- No cherry-picks, PR merges into application source, force pushes, P1 or experimental implementation incorporations.

## Actually verified
- [GitHub Actions run 40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136) `workflow_dispatch` on `main` event SHA `1b8fd2724cbea94d5fe995c750188b80e54d12fe`; actual detached implementation checkout `1f89c2d1bf64b669ca98b81f4305d20d08104e5c` (the identities are deliberately different).
- Job `122742537320` success; evidence artifact `12805993031`, GitHub metadata digest `sha256:62ce54d59bc9de714941d4158bfe86750fcb0340b5d03a010f67b75cc7bc5ee9`.
- Archive's 12 recorded SHA256 entries independently verified against downloaded file bytes, clean Linux/Python 3.12.15 environment, `pip check` good, 350 foundation/recovery regressions and 15 WP6 focused tests, successful Gate 2 challenge step.
- Repository evidence SHA256 verification: **NOT RUN EFFECTIVELY**. Both saved manifest file list and check output empty; workflow erroneously regarded zero discovered manifests as success.

## Required before verified D1
1. Execute PR #15's full replay CI workflow after user-authorised workflow-only merge to default branch. Inspect run checkout, logs, WP1/2 numerical restored replay, WP3/4 integration tests, WP4 dossier, nine WP6 full-resolution campaigns and separate-process replay, verified external ZIP+manifest, Streamlit startup and preserved source-specific evidence. No arbitrary existing test results transferred from other source SHAs.
2. Resolve WP2 accepted tested SHA from actual final-head Actions logs (last WP2 implementation `a3a4d592...`, later documentation-only head `7009189...`). Do not call guessed identity independently accepted.
3. Retain separate 27 October owner-reported WP6 final Gate 1–3 acceptance and prior historical review OPEN decision; obtain original final independent-review text if available.
4. Update programme ledger only with evidence status and obtain independent WP7 D1 release review. No tag before acceptance.

**Disposition:** CONDITIONAL for bounded WP7 preparation, not a verified release baseline or WP7 release acceptance. No experimental P1 / measured V1 claims.


---

## Final verified integration-source manifest — 28 October 2026 (supersedes conditional status above)

**VERIFIED for bounded D1 integration baseline only.** Immutable application source `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`; WP7 branch `wp7-d1-reproducible-release-2026-10-27` / draft PR #12 remains documentation-ahead and unmerged. Verification-only workflow file `.github/workflows/d1-full-replay.yml` was enabled via CI-only PR #15, merged to main at `8ccf11aa7b93ad9baca57b8c3640664e1de7427c` — NOT an application implementation commit and NOT the tested checkout.

- Core clean environment/regression: [run 40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136), artifact 12805993031, 350 regressions + 15 WP6 focused/reproduction tests, passed.
- Complete selected integration/replay: [run 40668433992](https://github.com/DavidOWilliams/Materials-design/actions/runs/40668433992), job 122748812186, artifact 12807606181, checkout `1f89c2d...`, 157 WP3/WP4 integration tests, WP1/WP2 (8 scenarios) replay, WP4 4096-cell 3 recomputations, WP6 nine 4096-cell campaigns/nine independent-process replays, historical unresolved-case reproduction and external SHA256 archive checks, Streamlit startup/health check, complete success.
- SHA256: complete artifact metadata and independently computed ZIP SHA256 `d8367e5c25699609e14f8038b8b5932bbe6c819fc3fc36086e737fd0d73fcdfb`; all 99/99 entries in archived `SHA256SUMS` match. Prior core artifact `62ce54d59bc9de714941d4158bfe86750fcb0340b5d03a010f67b75cc7bc5ee9` and 12/12 internal hashes match. Historical archived ZIP verified using preregistered `39e01e06110ef612f6ff561dea6a2568b0fc8b539dde9c466e2cab4a6033d3da` with internal manifest; no false nonempty checks.
- WP2 corrected final-head CI `40073237148`: actual tested checkout `7009189d9be4dfd5940999c88cbb5c3c70c8ce56` is one report-only commit after last implementation-changing `a3a4d592c0e9a3bb42868ee46295a4ba3831af31`, thus tested application tree identical. See source register.
- WP6 final bounded acceptance is recorded as programme-owner supplied 27 October decision in `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`; the original independent final review text still requires retention/linkage. Historical earlier PR #8 OPEN decision retained and distinct.
- No P1, no changed accepted implementation, no release tag and no application PR merged. Existing documentation-only revisions of PR #12 are NOT separate tested source identities.

**Release controls remain:** WP7 implementation/package/user handover and independent release acceptance are separate from this verified integration baseline. No D1 release tag until explicit authorised gate closure.


## D1 v0.1.0 controlled release candidate appendix — 28 October 2026

- Accepted WP7 application `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, tested tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`; accepted WP6 integration ancestor `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- Later PR #18 `b17ed112082bc21ab3833d57062be6d56d0d5918` is **one Markdown-only commit**, and not a newly tested implementation.
- Final independent WP7 approval recommendation [PR #19](https://github.com/DavidOWilliams/Materials-design/pull/19), dated 28 October, Gates 1–3 PASS bounded, not owner publication approval. Final reviewed report: `review/WP7_FINAL_INDEPENDENT_CORRECTIVE_ACCEPTANCE_2026-10-28.md` on independent review branch, not yet in accepted implementation tree.
- Author source CI [40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663) artifact `12815911040`, ZIP SHA256 `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`. Independent review CI [40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535) artifact `12818005576`, ZIP SHA256 `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`. Reviewer independently checked 99/99 and 41/41 source-specific manifest entries.
- Release integration branch `d1-release-candidate-2026-10-28` starts directly at accepted WP7 implementation, **without importing extra unreviewed code**, and holds D1 release documents. Final release commit/tree must be recorded after documentation completion. Release branch differs from accepted application only by documentation; see `foundation/D1_RELEASE_SOURCE_AND_EVIDENCE_MANIFEST.md` and `foundation/D1_RELEASE_INTEGRATION_REPORT.md`.
- WP3 intended-state Pareto and WP4 estimated-achieved-state Pareto separate. WP4 can consume **compatible A/B gradient** WP3 selection only. Cooperatively cancel at candidate boundaries. WP4 `*.handoff.json` is not independently relocatable with WP4 dossier: preserve WP3 workspace/ledger/run store or verified WP3 ZIP.
- Scientific limits D1 synthetic demonstration; no P1/P2/P3/E1/E2 scientific claims or measured ceramics / V1. IR05 historical WP6 original *final* Gate 3 PASS report remains unlocated. Earlier WP6 PR #8 review with Gate 2 OPEN at older SHA remains preserved; do not cite it as the final later PASS record.
- **READY FOR OWNER APPROVAL only if exact release packaging/code tree and checks are evidenced.** No application merge, tag or published release authorised by this appendix.


---

## IR05 documentary-source correction — 28 October 2026 (authoritative supersession of outdated gap statements above)

**IR05 CLOSED — original final independent WP6 acceptance recovered:** [`foundation/WP6_INDEPENDENT_ACCEPTANCE.md` at documentation-only commit `5c6c2e368664ee91a038f2677d4304eed7db7a4e`](https://github.com/DavidOWilliams/Materials-design/blob/5c6c2e368664ee91a038f2677d4304eed7db7a4e/foundation/WP6_INDEPENDENT_ACCEPTANCE.md). Its final dated section, **“FINAL independent WP6 Gate 3 acceptance — 27 October 2026”**, explicitly accepts bounded WP6 at tested `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`, Gates 1, 2 and 3 PASS. Independent WP6 workflow [40538857738](https://github.com/DavidOWilliams/Materials-design/actions/runs/40538857738), artifact `12748729866`, ZIP SHA256 `ff8c4ecad1be50f5a5b6d5c5496ade2bb906cd615cb9819bf8d585a3e7f459b2`, archived manifest 28/28; independent WP3 run `40538857597` and WP4 run `40538857615` succeeded. The same original report retains earlier Gate 2 OPEN and withheld findings as historical, source-specific snapshots; those are **superseded by the final acceptance section, not overwritten**. The final report commit is documentation-only, distinct from tested WP6 application source.


---

## D1 v0.2 source-controlled integration — 30 October 2026 (newer dated position supersedes historical v0.1 release-state text above)

- Previous v0.1.0 release tag `d1-v0.1.0` is unchanged, annotated tag object `8ba4331bab178bbdbef9e27cde77e1923cd7ee8e`, target `ec4bea044858bc275a1be80c3df24be438085279`. Pre-v0.2 `main` matches this commit.
- Accepted corrected v0.2 application `d9e63ea468294eba4fc25493395ad68d60edf9a5`, **tree `f63327ed03e7b22bb8c655c2d7ec608f0b0d7bb2`**, independently accepted via review PR #23 original final 30 October addendum. Gate 1 PASS bounded, Gate 2 PASS, Gate 3 PASS bounded. Later PR #22 report-only head `f8b97b91889d61848bee7afbed80c5b3853edc23` differs by exactly one Markdown report and is not a second tested implementation.
- Reviewer PR #23 head `6d689eab52329b57a821ca7eeac7f1cfcac3e483` is **independent review assets**, not accepted scientific application. Original final report `review/D1_V02_INDEPENDENT_SCIENTIFIC_PRESENTATION_VERIFICATION_2026-10-30.md` on `independent/d1-v02-scientific-display-review-2026-10-30`. Earlier Gate 3 BLOCKED and failed tests remain historical, superseded by final addendum and NOT deleted.
- Implementation [D1 v0.2 run 41047548183](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548183), artifact `12972374769`, ZIP digest `bc6fc216e5d6bea985d5f7017f4635b85a08bc4f98f8fad15f366d0d500053a7` (159/159 independently checked). WP3 full integration [41047548251](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548251) four green jobs, WP3 scientific 359 PASS/2 SKIP. WP4 [41047548198](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548198) and WP7 [41047548148](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548148) green. Separate independent scientific display review [41046147946](https://github.com/DavidOWilliams/Materials-design/actions/runs/41046147946), artifact `12972198847`, four independent source-data/integrity challenges and 370 regressions.
- Controlled release candidate branch `d1-v0.2-controlled-integration-2026-10-30` is based on accepted v0.2 source history and adds only explanatory v0.2 release documentation, these updated authoritative governance records, and independent qualification workflow `.github/workflows/d1-v02-release-integration.yml`. Candidate exact HEAD, full tree and source-vs-accepted diff are recorded in GitHub CI and PR after documentation finalisation. **No source/code/locked dependency delta beyond the independently accepted v0.2 application may be silently accepted.**
- **F01 CLOSED** (isolated three Streamlit UI tests explicitly executed), **F02 OPEN informational**, not tested for real first-time user, accessibility/assistive tech, Windows Edge or Codespaces, **F03 ACCEPTED BOUNDED** scientific limitation, **F04 CLOSED** with historical failing reviewer CI preserved.
- WP3 intended-state homogeneous/layered/gradient synthetic assessment remains distinct from WP4 estimated-achieved compatible A/B gradient feedback; do not pool Pareto, mislabel unknowns or imply physical manufacture. WP4 `*.handoff.json` requires preserved source WP3 ledger/store or verified complete ZIP. P1/P2/P3/E1/E2 and V1 excluded.
- New release target only **candidate** `d1-v0.2.0`, no tag, release publication, deployment or main merge authorised. Separate owner decision required after candidate actual CI and archive qualification. The successful v0.1.0 release scope and historical records remain unchanged.


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
