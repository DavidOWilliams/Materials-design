# D1 v0.1.0 — release approval checklist

**State:** NOT MERGED; NOT TAGGED; OWNER APPROVAL NOT YET GIVEN. WP7 independent Gate 1 PASS bounded, Gate 2 PASS, Gate 3 PASS bounded on source `c8f0292351553129fbcbdac3bd4f7a84a39365f9`.

- [x] Retrieve final original WP7 independent corrective acceptance report on PR #19 (rather than superseded PR #17).
- [x] Verify WP6 accepted ancestor and WP7 accepted application SHA.
- [x] Verify accepted WP7 to documentation PR #18 difference consists of one Markdown file.
- [x] Preserve distinct review/implementation/CI/documentation SHAs, numeric/physical limits, P1 exclusion and historical failures.
- [x] Propose release candidate from exact accepted WP7 source; no reconstruction from main.
- [x] Prepare release notes, installation, complete bounded handoff walkthrough, evidence preservation warning and hash references.
- [ ] Verify final release candidate Git tree differs from accepted implementation **only** by docs. Record exact candidate HEAD and tree, list each difference; rerun affected checks and seek new review if code/config/runtime differs.
- [ ] Verify release packaging artifacts generated at the actual candidate source in clean environment. Historical accepted SHA run cannot alone prove changed candidate code. Existing author and independent exact-source CI remains applicable **only when tree difference is documents-only**.
- [x] Retrieve and cite original final WP6 independent acceptance: docs-only commit `5c6c2e368664ee91a038f2677d4304eed7db7a4e`, final 27 October PASS section; preserve earlier historical OPEN sections unchanged.
- [ ] Owner approves exact bounded scope, integration strategy and final main release merge.
- [ ] After merge, inspect main and repeat source-tree/CI equivalence check; freeze actual release SHA, gain approval to create annotated tag `d1-v0.1.0` (or selected version). Do not tag before approval.
- [ ] Independent post-integration WP7 release check and published user guide/package verification at eventual tagged SHA.

**Scientific claims prohibited:** WP3 and WP4 Pareto pooling; manufactured/physical validation; broad process physics; mid-solver cancellation; equal-effort algorithm superiority; portable WP4+handoff standalone bundle; P1/P2/P3/E1/E2/V1 completion.


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
