# D1 v0.1.0 controlled release integration report — 28 October 2026

**Disposition:** BOUNDED WP7 IMPLEMENTATION INDEPENDENTLY ACCEPTED; CONTROLLED D1 RELEASE CANDIDATE PREPARED; OWNER MERGE/TAG AUTHORISATION **NOT** YET GIVEN. Exact release-candidate source-only equivalence must remain true at final PR head; CI at the latest source is an execution gate.

## 1. Source and ancestry

1. Accepted WP6 integration implementation: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`, ancestor of accepted WP7.
2. Accepted independently reviewed WP7 implementation: `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, exact Git tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`.
3. WP7 PR #18 documentation-only head: `b17ed112082bc21ab3833d57062be6d56d0d5918`; GitHub compare: **one Markdown file** `foundation/WP7_IR01_IR06_CORRECTIVE_DISPOSITION_2026-10-28.md`. Application, numerical code, dependencies, CI and source tests unchanged between accepted WP7 SHA and this head.
4. WP7 reviewer PR #19 head `3cff37663e79e05b62e88b738450788629c3bab8`, reviewer-only code/tests/workflow and documentation; independently reviewed application code remains unchanged. Full original final independent report: `review/WP7_FINAL_INDEPENDENT_CORRECTIVE_ACCEPTANCE_2026-10-28.md` on reviewer branch. Gate 1 PASS (bounded), Gate 2 PASS, Gate 3 PASS (bounded): **READY FOR D1 RELEASE APPROVAL**, not release authorised.
5. Release branch `d1-release-candidate-2026-10-28` branched directly from accepted WP7 implementation. It adds release notes, approved-scope instructions, manifest, release checklist, copies of D1 governance register/ledger with dated updates, and a verification-only CI workflow. **No application code, numerical algorithms, accepted dependency lock or evidence bytes were modified.** Final head and tree are recorded by GitHub PR #20 and candidate workflow artifact; documentation-only later commits must not be identified as tested implementation.

## 2. Actual accepted-source CI and independent evidence

- Implementation corrective [run 40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663), job `122810313169`, success: ten focused/360 foundation+recovery passed, 4096 numerical example dossiers, three separate-process replays, two Chromium browser journeys including selected-candidate handoff and recovery. ZIP artifact `12815911040`, SHA256 `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`; independently downloaded, 99/99 SHA256SUMS entries match.
- Independent [run 40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535), job `122824717424`, success: four independent corrective challenge tests, independent Chromium end-to-end handoff, cancellation, browser restart/replay, 360 regressions. ZIP artifact `12818005576`, SHA256 `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`; independently downloaded, 41/41 SHA256SUMS entries match.
- Historical blocked finding [PR #17](https://github.com/DavidOWilliams/Materials-design/pull/17) and initial reviewer-script failure remain immutable and not falsely reinterpreted.
- WP6 baseline qualification [40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136), full replay [40668433992](https://github.com/DavidOWilliams/Materials-design/actions/runs/40668433992) preserved separately.
- Exact proposed release source equivalence: release candidate workflow `.github/workflows/d1-release-candidate-qualification.yml` checks immutable accepted WP7 tree and checks that every difference is documentation or this CI workflow. Run `40693796220` **FAILED** before application tests due to an overly narrow **verification allowlist** omitting programme ledger; no source or scientific failure. Correction at workflow-only `8fe9612ac1789843d93b732116ff10bf8ed5895f`; new CI [run 40693887420](https://github.com/DavidOWilliams/Materials-design/actions/runs/40693887420) started. **Treat as pending until job conclusion and manifest inspected**. Do not record an uninspected green result.

## 3. Release assets and user preservation boundaries

See `foundation/D1_RELEASE_NOTES_v0.1.0.md`, `foundation/D1_RELEASE_INSTALL_AND_DEMONSTRATION.md`, `foundation/D1_RELEASE_SOURCE_AND_EVIDENCE_MANIFEST.md`, `foundation/D1_RELEASE_APPROVAL_CHECKLIST.md`. Install requires Python 3.12, hash-locked foundation requirements via `bash foundation/setup.sh`, pinned `streamlit==1.40.2`, `pip check`. Representative journey: WP3 intended-only homogeneous/layered/gradient exploration, choose compatible A/B gradient, traceable WP4 estimated-achieved evaluation, feedback only if supported mass constraint binds, distinct Pareto, boundary cancellation and checkpoint recovery, preserved source ledger plus handoff integrity. Examples can be rebuilt at 4096 cells.

**Critical portability limitation:** A WP4 dossier and `*.handoff.json` **are not a self-contained, relocatable combined bundle**. Preserve the exact original WP3 ledger, store, evaluation artifacts and/or verified WP3 ZIP; otherwise handoff source lineage cannot be reproduced.

## 4. Science and decision limitations

No measured physical ceramic properties or validation, manufacturing process qualification, global algorithm superiority, externally validated residual stresses, certified airworthiness or production readiness. P1/P2/P3/E1/E2 scientific programme excluded. WP3 numerical intended-state Pareto must not be mixed into WP4 estimated-state Pareto. Gradient-only compatible A/B handoff; non-A/B/homogeneous/layered reject. Cancellation between candidates; no mid-solver interruption. Preview results may be unqualified.

**IR05:** Original later 27 October WP6 final Gate-3 PASS report has not been retrieved. The earlier review PR #8 document (docs SHA `5c6c2e368664ee91a038f2677d4304eed7db7a4e`) recorded a different source with Gate 2 OPEN and must NOT be presented as final later PASS. User-supplied final acceptance is preserved in `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`. This is nonblocking documentation provenance but must be resolved/flagged.

## 5. Governance and approval

Release PR **#20**, branch `d1-release-candidate-2026-10-28`, base `main`, is **draft/unmerged**. It is a controlled PR based on accepted WP7 tested implementation, not a merge of PRs #12, #13, #16, #17, #18, #19. Exact final release source/tree identity must be read from the branch after packaging; the accepted WP7 *implementation tree* must remain untouched and any disallowed differences must fail closed. No final release tag has been created.

Proposed first tag after final approval: `d1-v0.1.0`. After owner authorises integration, merge only authorised release PR, verify resulting `main` tree, freeze new release commit, rerun any checks invalidated by merge (including dependency/code/config changes), perform independent post-integration release verification and request distinct tag authorisation. **RELEASE MERGED AND TAGGED is FALSE until separately approved.**
