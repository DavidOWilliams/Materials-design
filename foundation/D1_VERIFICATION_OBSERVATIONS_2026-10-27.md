# D1 verification observation — 27 October 2026

## Disposition: BLOCKED (exact-source execution not established)

Immutable authorised application source: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
Separate verification-workflow commit: `69e957fdd77b246b9ed0020f9d324a92652e343c`; draft PR #13. WP7 integration PR #12 remains separate.

## Actually observed GitHub Actions runs on PR #13 workflow commit

- WP6 demonstration evaluation: [40561289028](https://github.com/DavidOWilliams/Materials-design/actions/runs/40561289028), success; job 122390694333, all steps successful; **actual checkout `f8c8ea8`**, PR merge of verification commit into main, NOT immutable accepted WP6. 14 focused WP6 tests passed, portable reproduction 1 passed, archived reproduction 1 passed, foundation 350 passed, nine campaigns complete, zero failed; archived ZIP checksum and internal SHA256 checks passed. Evidence is informative only, not D1 exact-source verification.
- WP4 qualification: [40561289031](https://github.com/DavidOWilliams/Materials-design/actions/runs/40561289031), success; job 122390693940; WP4 tests, WP5 UI/browser, foundation regression, campaign replay and archival steps successful. Exact checkout not independently reconciled; PR merge workflow.
- WP3 integration: [40561289000](https://github.com/DavidOWilliams/Materials-design/actions/runs/40561289000), success; four jobs 122390693768, 122390694341, 122390694481, 122390694495. PR merge workflow; no exact accepted-WP6 SHA claim.
- The newly added `d1-exact-source-verification.yml` job has **not** been observed running. The connector has no dispatch operation; the workflow was created on a non-default branch, and GitHub does not necessarily register a new workflow_dispatch workflow until present on the default branch. Git clone from the local container failed: `Could not resolve host: github.com`.

## Reconciled ancestry

GitHub compare: WP1 published tested `729a9da54cf339cc7c97526879a5ec49e03fcd4f` ancestor (441 commits before WP6); WP3 accepted `790c3521f09e3f61615702de3b149c9f315e9e74` ancestor (253 commits before WP6); WP4 `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b` and WP5 `4078a83dc11e14703ff6cc03f5b62f4e48879d14` ancestors. P1 original `6eb62daec638185f5c5dc170182e9e0454b6e061` and corrected `752752f880ed7c4b0c77d399ca7c99f9a9bb094e` **diverge** from WP6 (not ancestors); no P1 merge performed.

WP1 tested source and tree equivalence: foundation/COMPLETION_REPORT.md; documentation-only commit pending. WP2 corrected accepted source and documentation-only identity pending exact evidence audit. WP3 documentation acceptance `71933c733340d4b7c33777488a428bc56e34f57f`; WP4 `1805811acdafacd66ba3574e8cb45c59bebdd8e5`; WP5 `5ade1e9650795427a8bb32de64dfce6c11cd0426`. WP6 final acceptance of 27 October supplied by programme owner, accepted source `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`; `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` absent on accepted WP6 and PR #12 branch at inspection. Historical PR #8 withheld acceptance at earlier Gate 2 stage; not superseded without durable later record.

## Remaining mandatory actions

1. Run a workflow that checks out the immutable WP6 SHA and inspect job logs/artifacts. Minimum user action: make the verification workflow dispatchable in Actions (e.g. authorised default-branch workflow addition, separately reviewed), then select **Run workflow**; do not merge PR #13 or #12 merely to trigger it. Alternatively an authorised CI operator may run the exact-source commands in a clean GitHub runner and upload evidence.
2. Complete WP2 source/acceptance reconciliation and preserve the WP6 final acceptance decision in a separate documentation-only record.
3. Extend exact-source checks to WP3/WP4 integration, numerical dossier restore, separate-process replay, evidence archives, application startup; generate source-specific SHA256 manifest.
4. Update PR #12 ledger and register only after actual evidence, preserving separation of tested source and documentation commits.

No final release tag, PR merge, force push, accepted source modification or independent WP7 acceptance.
