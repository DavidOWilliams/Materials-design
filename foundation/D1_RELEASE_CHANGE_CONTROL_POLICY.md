# D1 release and change-control policy

1. Promote only independently accepted tested source identities. Record tested SHA, acceptance decision/scope, evidence location and hashes, and separate documentation-only commits.
2. Before integration, prove ancestry with git merge-base --is-ancestor and compare trees/files for any non-ancestor accepted changes; do not merge all PRs by default.
3. Create candidate from exact accepted source; use separate commits for governance. Any executable/dependency/workflow modification requires new candidate SHA and retesting.
4. In clean GitHub Actions checkout at pinned SHA, install locked dependencies, run WP1–WP6 regressions, WP3/WP4 integration, WP6 workflow, numerical/dossier replay and SHA256 archive verification; retain raw logs, artifact links, environment and exact checkout SHA. A configured but unexecuted workflow is NOT verification.
5. Freeze reviewed candidate by immutable full SHA and archived evidence manifest. No moving acceptance references, overwriting evidence or force pushes.
6. WP7 independent reviewer checks provenance, scientific boundaries, tests, evidence replay, excluded P1 and candidate SHA; reviewer records findings and decision separately. Self-approval prohibited.
7. Retest after any source, dependency, configuration, workflow, test or evidence-affecting change; docs-only changes require provenance/diff check and cannot inherit a new tested identity.
8. After independent WP7 acceptance, authorised maintainer establishes final release SHA and annotated signed or documented Git tag; never tag in advance.
9. Rejected/unaccepted/experimental changes remain on isolated branches and outside D1.
