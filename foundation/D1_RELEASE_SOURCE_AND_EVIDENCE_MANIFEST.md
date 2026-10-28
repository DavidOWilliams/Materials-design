# D1 v0.1.0 proposed source and evidence manifest

## Immutable identities
- WP6 accepted integration source: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- WP7 independently accepted **application/source**: `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, Git tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`.
- WP7 PR #18 documentation-only HEAD: `b17ed112082bc21ab3833d57062be6d56d0d5918`, tree `273fd0c766dd72dd38a6e9bffcfbfdf98dc003f5`; compare accepted→PR head: **one Markdown file** `foundation/WP7_IR01_IR06_CORRECTIVE_DISPOSITION_2026-10-28.md`, no application/workflow/dependency change.
- Final independent PR #19 review HEAD: `3cff37663e79e05b62e88b738450788629c3bab8`; review-only tests, workflow and documentation are not the accepted application.
- D1 release candidate branch `d1-release-candidate-2026-10-28` started **exactly** at `c8f0292351553129fbcbdac3bd4f7a84a39365f9`; subsequent candidate commits are documentation-only, not retested application. Record final candidate HEAD and tree after all packaging. Main has only prior CI enablement (PRs #14/#15) and not accepted WP7 app source; avoid wholesale historical PR merges and do not call the current main a D1 release.
- Evidence ZIP archive IDs/hashes: author `12815911040` / `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`; independent `12818005576` / `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`; source-specific original reviewer verification 99/99 and 41/41 entries, respectively.
- Implementation [run 40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663) and reviewer [run 40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535). Prior WP6 exact-source qualification [40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136), full replay [40668433992](https://github.com/DavidOWilliams/Materials-design/actions/runs/40668433992).

## Approval and limitations
Reviewer final report source: `review/WP7_FINAL_INDEPENDENT_CORRECTIVE_ACCEPTANCE_2026-10-28.md` on PR #19 branch. Earlier PR #17 Gate 1 BLOCKED record retained. Original earlier independent WP6 Gate 2 OPEN report on PR #8 is `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` at docs-only `5c6c2e368664ee91a038f2677d4304eed7db7a4e`, **not** the later reported final WP6 three-gate PASS original. Later WP6 final acceptance is programme-owner-supplied and documented in `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`; original final reviewer report remains unlocated; **IR05 nonblocking but open**.

Full release-candidate exact-tree equivalence and packaging verification must be documented at final HEAD. This manifest is a release packaging document, not an independent release review or final tag record. P1/P2/P3/E1/E2 remain excluded.


---

## IR05 documentary-source correction — 28 October 2026 (authoritative supersession of outdated gap statements above)

**IR05 CLOSED — original final independent WP6 acceptance recovered:** [`foundation/WP6_INDEPENDENT_ACCEPTANCE.md` at documentation-only commit `5c6c2e368664ee91a038f2677d4304eed7db7a4e`](https://github.com/DavidOWilliams/Materials-design/blob/5c6c2e368664ee91a038f2677d4304eed7db7a4e/foundation/WP6_INDEPENDENT_ACCEPTANCE.md). Its final dated section, **“FINAL independent WP6 Gate 3 acceptance — 27 October 2026”**, explicitly accepts bounded WP6 at tested `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`, Gates 1, 2 and 3 PASS. Independent WP6 workflow [40538857738](https://github.com/DavidOWilliams/Materials-design/actions/runs/40538857738), artifact `12748729866`, ZIP SHA256 `ff8c4ecad1be50f5a5b6d5c5496ade2bb906cd615cb9819bf8d585a3e7f459b2`, archived manifest 28/28; independent WP3 run `40538857597` and WP4 run `40538857615` succeeded. The same original report retains earlier Gate 2 OPEN and withheld findings as historical, source-specific snapshots; those are **superseded by the final acceptance section, not overwritten**. The final report commit is documentation-only, distinct from tested WP6 application source.
