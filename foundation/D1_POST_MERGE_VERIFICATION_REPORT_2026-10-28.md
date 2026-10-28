# Materials Design D1 — final controlled integration and post-merge independent verification

**Decision date:** 28 October 2026. **Disposition: POST-MERGE D1 INTEGRATION VERIFIED within the accepted bounded synthetic scope.** `d1-v0.1.0` **NOT TAGGED; no GitHub release published; no deployment.** Programme-owner release-tag/publication approval remains pending. This is a documented evidence review, not a claim of an additional independently authored materials-science acceptance.

## 1. Authority, merge and immutable identities

- Owner authorised PR #20 *only* for controlled integration, after correcting IR05 and rerunning exact release-candidate checks. No authorisation for tag, publication or deployment.
- [PR #20](https://github.com/DavidOWilliams/Materials-design/pull/20) was marked ready and merged by `merge` method only after pre-merge success. **Actual main merge commit: `ec4bea044858bc275a1be80c3df24be438085279`**.
- **Actual main Git tree: `80253be4d68b27d75a9e893c92e8a6304f400674`.** Merge parents: prior main `8ccf11aa7b93ad9baca57b8c3640664e1de7427c`, exact authorised PR #20 HEAD `1be9eb3015a2bc50cc8485fa9518a54b7b2111ca`.
- Independently accepted WP7 application commit `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, application/source Git tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`. Accepted WP6 integration implementation ancestor `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- GitHub compare accepted WP7 → actual merged main: only **12 added files** — nine D1 release/governance Markdown documents and **three** D1-only CI verification workflows (`d1-immutable-source.yml`, `d1-full-replay.yml`, `d1-release-candidate-qualification.yml`). **No application source, scientific numerical algorithms, dependency locks, accepted tests or evidence files differ.** The three CI workflows include two previously enabled on main before PR #20; do not misattribute their additions to PR #20.
- WP7 documentation-only PR #18 head `b17ed112082bc21ab3833d57062be6d56d0d5918`, a one-Markdown-file change after accepted source, remains separate. Independent WP7 reviewer PR #19 and earlier Gate 1 BLOCKED PR #17 remain unmerged and historically preserved.

## 2. Exact pre-merge qualification of final PR #20

- Accepted source/tree equivalence verified and all five PR-head workflows completed **success** at exact candidate `1be9eb3015a2bc50cc8485fa9518a54b7b2111ca`: WP3 [40701597984](https://github.com/DavidOWilliams/Materials-design/actions/runs/40701597984), WP4 [40701598082](https://github.com/DavidOWilliams/Materials-design/actions/runs/40701598082), WP6 [40701598236](https://github.com/DavidOWilliams/Materials-design/actions/runs/40701598236), WP7 [40701598080](https://github.com/DavidOWilliams/Materials-design/actions/runs/40701598080), D1 candidate [40701598248](https://github.com/DavidOWilliams/Materials-design/actions/runs/40701598248).
- Pre-merge full release-candidate evidence artifact `12822685684`, external ZIP SHA256 `2f52b9226fedf189935e716c386fadd187ab77bd66d631a2857c131f8584fca9` matched, internal SHA256SUMS **89/89** verified. Its source identity is PR #20 head, **not** the subsequent merge SHA.
- A previous CI-only allowlist failed [40693796220](https://github.com/DavidOWilliams/Materials-design/actions/runs/40693796220) before functional tests; corrected without scientific/application changes. Earlier Gate 1 BLOCKED and failed reviewer CI evidence remains in repository history; not relabelled PASS.

## 3. Actual post-merge verification at main source

- Automatic `push` GitHub Actions [**40702856051**](https://github.com/DavidOWilliams/Materials-design/actions/runs/40702856051), job `122867027751`, **SUCCESS**, checked out actual main `ec4bea044858bc275a1be80c3df24be438085279`, Git tree `80253be4d68b27d75a9e893c92e8a6304f400674`. Accepted source tree verified exact.
- Clean Python **3.12.15** installation via `bash foundation/setup.sh`, pinned `streamlit==1.40.2`, `pip check` and frozen dependency evidence passed. Runtime Ubuntu Linux; precise package versions in evidence artifact.
- **360 foundation/recovered-WP0 regressions passed**; **6 focused WP7 correction and mixed-architecture tests passed**. GitHub job logs independently inspected; all workflow steps concluded success with no skipped required step.
- 4096-element example generation and numerical restoration produced WP3 gradient/homogeneous/layered, two WP4 cases, **three separate-process numerical replays**: `{"status":"passed", ...}`.
- Streamlit startup health responded `ok`, and actual Playwright/Chromium WP7 integrated browser script step completed successfully. The browser log text file in archive is empty; the job success and persisted browser workspace are evidence, not proof of every possible user interaction.
- Downloaded post-merge artifact `12822416835`, GitHub ZIP SHA256 `eb48d0d3b6da62fe13f12f9dc5983a71cb6611983a8a42d512f129deab96623e`. Independent local hash equals GitHub; **all 89/89 entries of `SHA256SUMS` match actual archived bytes**, zero mismatch. `release-head.txt`, `release-tree.txt`, `accepted-implementation-tree.txt`, `accepted-source-diff.txt`, `health.txt` and `examples.log` independently inspected. GitHub artifact retention is time-limited; archive should be retained in approved programme evidence storage before its expiry.
- Source/evidence controls are thus verified for the actual integrated tree; no historical run at another source identity was substituted for this run.

## 4. IR05 resolved — original WP6 independent acceptance

At documentation-only commit [`5c6c2e368664ee91a038f2677d4304eed7db7a4e`](https://github.com/DavidOWilliams/Materials-design/blob/5c6c2e368664ee91a038f2677d4304eed7db7a4e/foundation/WP6_INDEPENDENT_ACCEPTANCE.md) the genuine `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` record contains a **final 27 October 2026** section expressly stating **Gate 1 PASS, Gate 2 PASS, Gate 3 PASS (bounded)** at tested WP6 `1f89c2d...`. That original report retains earlier OPEN/withheld decisions, which remain historically valid for older reviewed sources but are superseded by the final section.

The final WP6 independent CI evidence is [40538857738](https://github.com/DavidOWilliams/Materials-design/actions/runs/40538857738), job `122311429939`, artifact `12748729866`, ZIP hash `ff8c4ecad1be50f5a5b6d5c5496ade2bb906cd615cb9819bf8d585a3e7f459b2`, 28/28 manifest entries verified by original reviewer; WP3 and WP4 integration follow-up runs `40538857597`, `40538857615` successful. This **documentation-only WP6 report commit is NOT the WP6 implementation SHA**.

All PR #20 governance documents were corrected to cite the original **final PASS** section and mark IR05 CLOSED; no earlier review/history was deleted.

## 5. WP7 original final acceptance

- [Independent WP7 final report](https://github.com/DavidOWilliams/Materials-design/blob/independent/wp7-correction-rereview-2026-10-28/review/WP7_FINAL_INDEPENDENT_CORRECTIVE_ACCEPTANCE_2026-10-28.md) in [PR #19](https://github.com/DavidOWilliams/Materials-design/pull/19): Gate 1 PASS bounded, Gate 2 PASS, Gate 3 PASS bounded. Accepted WP7 implementation `c8f029...`.
- Accepted implementation CI [40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663), evidence `12815911040`, ZIP hash `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`, 99/99. Independent reviewer CI [40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535), evidence `12818005576`, ZIP hash `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`, 41/41. These accept a bounded synthetic software demonstration, not experimental materials science.

## 6. Bounded functionality, evidence dependencies and remaining limitations

- WP3 compares intended-state synthetic homogeneous, layered and gradient architectures. WP4 feedback applies only to strictly compatible **two-constituent A/B gradients**, re-evaluated in separate estimated-achieved-state numerical context. WP3 and WP4 Pareto fronts must **never be pooled** across incompatible contexts.
- Cooperative cancellation **between evaluated candidates**, not mid-solver interruption; checkpoint/recovery and immutable dossier replay are verified in bounded workflows.
- WP4 dossier JSON + corresponding `*.handoff.json` are **not a portable, standalone combined bundle**. Retain the original WP3 ledger, run-store and artifacts or verified complete WP3 ZIP, with reconstructable source paths and checked lineage.
- Physically measured ceramics, process accuracy/uncertainty, true general algorithmic superiority, externally benchmarked generalisation, residual-stress history, engineering certification/airworthiness and production readiness remain outside D1. P1/P2/P3, E1/E2, V1 are separate. No measured achieved-state claim is made.
- Post-merge browser automation and synthetic cases are not universal user acceptance or physical certification; package UI dependencies pinned with transitive freeze rather than universal supply-chain hash locks. Maintain archive retention as part of long-term evidence control.

## 7. Final decision and actions pending owner approval

**CONTROLLED D1 APPLICATION INTEGRATION: MERGED AND POST-MERGE VERIFIED.** PR #20 only was merged into `main` under owner authorisation. Other historic PRs not merged in this action; P1 excluded.

**NOT TAGGED; NOT PUBLISHED; NOT DEPLOYED.** Proposed tag `d1-v0.1.0`; programme owner must separately authorise creating tag, publishing a GitHub release and any deployment. Do not infer permission to tag from permission to merge. Prior to tag, reconfirm main SHA/tree, evidence archive availability, and final tag target. The Git tree `80253be...` is verified; proposed tag target is the exact main commit `ec4bea0...` only if owner approves and main has not moved.

**This report is committed on a separate documentation-only audit branch starting from the verified main merge commit** so it does not change the verified main SHA/tree or trigger a new release-candidate qualification without explicit need. The report commit itself is **not** a retested application source or a released/tagged artifact.
