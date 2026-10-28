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
- [ ] Retrieve/attach original final WP6 27 October independent acceptance report if it exists; otherwise retain explicit owner-provenance-only IR05 gap.
- [ ] Owner approves exact bounded scope, integration strategy and final main release merge.
- [ ] After merge, inspect main and repeat source-tree/CI equivalence check; freeze actual release SHA, gain approval to create annotated tag `d1-v0.1.0` (or selected version). Do not tag before approval.
- [ ] Independent post-integration WP7 release check and published user guide/package verification at eventual tagged SHA.

**Scientific claims prohibited:** WP3 and WP4 Pareto pooling; manufactured/physical validation; broad process physics; mid-solver cancellation; equal-effort algorithm superiority; portable WP4+handoff standalone bundle; P1/P2/P3/E1/E2/V1 completion.
