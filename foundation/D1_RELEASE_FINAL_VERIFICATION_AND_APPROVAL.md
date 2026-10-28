# D1 v0.1.0 — final release candidate exact-tree qualification and approval dossier

**28 October 2026.** This annex supersedes the provisional CI-in-progress status in `D1_RELEASE_INTEGRATION_REPORT.md`. **READY FOR OWNER APPROVAL OF BOUNDED INTEGRATION**, subject to reviewing the explicitly delimited scope and the final documentation-only HEAD identity. **NOT MERGED, NOT TAGGED, NOT RELEASED.**

## Accepted implementation and candidate

- Independently accepted WP7 implementation: `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, Git tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`.
- Verified release candidate before this annex: commit `43b5c569636c7a658a0905cdedf5fb4a91b780d2`, complete Git tree `50971d627d471061507ff23135c5dd6f3318d918`. GitHub compare: nine additional files; eight release/governance Markdown and one CI-only workflow, **zero application/source/dependency changes**. This annex is a subsequent documentation-only commit and therefore NOT an additional tested application implementation. The exact final candidate HEAD and tree must be read from the resulting PR #20 and its own CI run before merge.
- CI-enabled `main` is not yet the accepted WP7 app. Pull request #20 is the sole proposed controlled application integration; existing PRs #12/#13/#16/#17/#18/#19 remain unmerged.

## Actual reproducibility checks

- An initial release workflow run [40693796220](https://github.com/DavidOWilliams/Materials-design/actions/runs/40693796220) **failed due to CI-only allowlist mistakenly omitting `foundation/PROGRAMME_DELIVERY_LEDGER.md`**. The workflow did not reach application tests, and no scientific defect was observed. Failure and artifact remain preserved. Fixed in CI-only `8fe9612ac1789843d93b732116ff10bf8ed5895f` without application change.
- First corrected success [40693887420](https://github.com/DavidOWilliams/Materials-design/actions/runs/40693887420), artifact `12817599637`, ZIP SHA256 `858f262ae6a40c2d8e65edbff3744e4c7c47c37fa95234608cdb9eb09d1f7b67`: successful tree-equivalence assertion, clean pinned numerical install and UI dependency, foundation tests, full-resolution WP3/WP4 example dossiers, separate-process replay and browser startup/journey. Independently downloaded artifact 89/89 SHA256SUMS entries verified.
- **Final documented candidate run** [40694166334](https://github.com/DavidOWilliams/Materials-design/actions/runs/40694166334), job `122836392936`, **SUCCESS**. Workflow checked out exact `43b5c569636c7a658a0905cdedf5fb4a91b780d2`, tree `50971d627d471061507ff23135c5dd6f3318d918` and verified accepted source tree identity `b9ab5ed7...`. `360 passed` foundation+recovery tests and `6 passed` targeted WP7 correction/mixed-architecture tests. Full 4096-element generation: WP3 gradient/homogeneous/layered, two WP4 cases and **3 independent-process replays**, successful HTTP startup health and actual Chromium end-to-end browser script. Evidence uploaded [artifact 12818218481](https://github.com/DavidOWilliams/Materials-design/actions/runs/40694166334/artifacts/12818218481), GitHub ZIP SHA256 `29bca3af2ca64f58c5ef8a208a2b790e0d5b13987157801950c3a668c7d058d6`. Independently downloaded ZIP and verified **89/89 internal SHA256SUMS entries**, zero mismatch. `health.txt` contains `ok`; examples log reports passed; original browser script is success by step conclusion, its browser log has no text but screenshot/workspace evidence remains within artifact.
- Accepted source independent [40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535), artifact `12818005576`, 41/41 verified; author [40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663), artifact `12815911040`, 99/99 verified. Independent Gate 1 PASS bounded, Gate 2 PASS, Gate 3 PASS bounded on `c8f029...`.

## Final approval checklist and explicit limitations

- [x] Original final WP7 reviewer report retrieved on PR #19; superseded BLOCKED PR #17 preserved, including earlier failed reviewer test runs.
- [x] Exact WP7 accepted application source and tree verified, baseline WP6 preserved.
- [x] Proposed candidate contains no changed application source, numerical algorithm, runtime dependencies or accepted evidence; release docs and verification-only workflow added.
- [x] Clean installation, numerical and WP7 regressions, new full-resolution dossiers, independent-process replay, browser check, SHA256 archive integrity all executed and independently reviewed at documented candidate SHA.
- [x] Mandatory separate WP3 ledger/store/verified ZIP retention explicitly documented alongside WP4 JSON + `*.handoff.json`; this pair is **not** a standalone relocatable bundle.
- [x] Scientific exclusions and distinct Pareto contexts explicitly stated.
- [ ] Preserve/link original later WP6 final independent Gate-3 PASS reviewer report (IR05 still nonblocking source gap, not to be confused with earlier OPEN review at PR #8).
- [ ] Owner explicitly approves bounded release scope and controlled integration PR #20.
- [ ] Following authorised merge: inspect new `main` commit and full tree, verify source equivalence and rerun affected qualification if any functional/dep/workflow change; record independent post-integration release review.
- [ ] Obtain separate approval for final annotated Git tag `d1-v0.1.0` and publication. Neither is done.

**Decision recommendation:** RELEASE PR #20 is technically ready to request owner authorisation to integrate the bounded D1 synthetic demonstration, **not** a published release. Exact final doc-only commit/tree and corresponding Actions status must be checked after this annex commit. Do not merge or tag without owner authorisation.
