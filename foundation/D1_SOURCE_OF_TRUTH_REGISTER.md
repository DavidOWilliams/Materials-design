# D1 source-of-truth register — reconciled 28 October 2026

**Scope:** bounded synthetic D1; no measured ceramic V1 qualification. This is a governance register, not a release decision. Accepted source is distinct from acceptance-document and workflow commits.

| Package | Exact implementation identity | Decision / evidence | Documentation-only identity | Git ancestry / status |
| --- | --- | --- | --- | --- |
| WP1 | `729a9da54cf339cc7c97526879a5ec49e03fcd4f` (published tree equal to tested local `9fc44509bf45096d52d7abb8d84f13d786e31c60`) | `foundation/COMPLETION_REPORT.md`; bounded completion and 74 focused/recovery checks | `22350b119d8a30248a9924ba375ebf4c8dabb4b7` (single report file, parent equals published WP1 source) | WP6 ancestor |
| WP2 | **Not separately labelled final accepted tested source in available approval record**. Last corrected implementation commit before the final report-only commit: `a3a4d592c0e9a3bb42868ee46295a4ba3831af31`. Published WP2 head `7009189d9be4dfd5940999c88cbb5c3c70c8ce56` is documentation-only (one `WP2_COMPLETION_REPORT.md` change). | PR #2 states five findings corrected, five green jobs on [run 40073237148](https://github.com/DavidOWilliams/Materials-design/actions/runs/40073237148), and 134 corrected tests; **this source identity is a best evidenced candidate, not independently confirmed exact tested checkout** | `7009189d9be4dfd5940999c88cbb5c3c70c8ce56` documentation-only report commit; additional earlier documentation-only `e5ca57fa0fd0e8cd693f0816860e9ce6d5f752b8` | WP2 branch/head ancestor of WP6; exact tested-source reconciliation still required |
| WP3 | `790c3521f09e3f61615702de3b149c9f315e9e74` | Bounded independent acceptance; `foundation/WP3_ACCEPTANCE_LEDGER.md` | `71933c733340d4b7c33777488a428bc56e34f57f` | WP6 ancestor |
| WP4 | `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b` | Bounded independent acceptance, PR #4 | `1805811acdafacd66ba3574e8cb45c59bebdd8e5`; archive preservation `bb67e51029c5479361c59cea0b73b6bb722826f1` | WP6 ancestor |
| WP5 | `4078a83dc11e14703ff6cc03f5b62f4e48879d14` | Independent acceptance `foundation/WP5_INDEPENDENT_ACCEPTANCE.md` | `5ade1e9650795427a8bb32de64dfce6c11cd0426` | WP6 ancestor |
| WP6 | `1f89c2d1bf64b669ca98b81f4305d20d08104e5c` | Programme owner reports 27 October final independent Gate 1–3 PASS. Exact source independently executed in [run 40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136). Later decision has not been found as a repository-original independent signed/final acceptance report; see `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`. Earlier independent review document on PR #8 held Gate 2 OPEN for older source `c53dee...`; that decision is retained unchanged. | This D1 provenance document's eventual commit is documentation-only, **not** WP6-tested implementation | D1 source starting point; not merged to default branch |
| P1 | original `6eb62daec638185f5c5dc170182e9e0454b6e061`, corrected `752752f880ed7c4b0c77d399ca7c99f9a9bb094e` | Gate 3 withheld | independent P1 PR #10 | Diverged from WP6; excluded |

## Exact D1 verification

- [Run 40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136), job `122742537320`, completed success, immutable checkout confirmed by raw log and downloaded artifact `12805993031`.
- Artifact SHA256 metadata: `62ce54d59bc9de714941d4158bfe86750fcb0340b5d03a010f67b75cc7bc5ee9`. Locally extracted ZIP internal manifest verified **12/12 entries**, including identical implementation identity, dependencies, regression and challenge logs.
- Ubuntu 24.04, Python 3.12.15, foundation packages as locked; clean `pip check`; **350 regressions passed**, **15 WP6 focused/reproduction tests passed**, Gate 2 challenge step succeeded.
- **Critical gap:** `manifests.txt` and `manifests-check.log` both zero bytes. Existing repository manifest command found none, therefore it silently succeeded without validating any repository evidence. This step is **UNVERIFIED**, not a valid manifest-integrity pass.
- Full-resolution WP6 4096-element campaign and nine-case separate-process replay, external archive checksum and application HTTP startup are NOT part of that successful run. Workflow-only PR #15 is prepared, **not executed**. No success claim for those checks.

Dependencies WP1 → WP2 → WP3 → WP4 → WP5 → WP6. No P1 integration. WP7 release acceptance and tag prohibited until complete independent review.

**Current D1 integration verification disposition: CONDITIONAL for bounded WP7 preparatory development only**. Mandatory release baseline closure remains blocked by missing exact-source replay/external evidence/app startup and incomplete WP2/WP6 documentary identities.
