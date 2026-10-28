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
