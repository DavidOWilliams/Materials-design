# D1 integration manifest — evidence update 28 October 2026

## Immutable implementation and branches
- Accepted implementation: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- WP7 governance branch `wp7-d1-reproducible-release-2026-10-27`; draft PR #12. Later D1 register changes are **documentation only**, not retested implementation.
- Separate verification PR #13 `d1-governance-verification-2026-10-27`, not integrated.
- Default `main` contains only the CI-enablement workflow from PR #14 and its pre-existing code; accepted WP6 application source is not represented as merged to `main`.
- New workflow-only PR #15 against `main` adds separate exact-source complete replay and smoke verification. Not merged or executed.
- No cherry-picks, PR merges into application source, force pushes, P1 or experimental implementation incorporations.

## Actually verified
- [GitHub Actions run 40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136) `workflow_dispatch` on `main` event SHA `1b8fd2724cbea94d5fe995c750188b80e54d12fe`; actual detached implementation checkout `1f89c2d1bf64b669ca98b81f4305d20d08104e5c` (the identities are deliberately different).
- Job `122742537320` success; evidence artifact `12805993031`, GitHub metadata digest `sha256:62ce54d59bc9de714941d4158bfe86750fcb0340b5d03a010f67b75cc7bc5ee9`.
- Archive's 12 recorded SHA256 entries independently verified against downloaded file bytes, clean Linux/Python 3.12.15 environment, `pip check` good, 350 foundation/recovery regressions and 15 WP6 focused tests, successful Gate 2 challenge step.
- Repository evidence SHA256 verification: **NOT RUN EFFECTIVELY**. Both saved manifest file list and check output empty; workflow erroneously regarded zero discovered manifests as success.

## Required before verified D1
1. Execute PR #15's full replay CI workflow after user-authorised workflow-only merge to default branch. Inspect run checkout, logs, WP1/2 numerical restored replay, WP3/4 integration tests, WP4 dossier, nine WP6 full-resolution campaigns and separate-process replay, verified external ZIP+manifest, Streamlit startup and preserved source-specific evidence. No arbitrary existing test results transferred from other source SHAs.
2. Resolve WP2 accepted tested SHA from actual final-head Actions logs (last WP2 implementation `a3a4d592...`, later documentation-only head `7009189...`). Do not call guessed identity independently accepted.
3. Retain separate 27 October owner-reported WP6 final Gate 1–3 acceptance and prior historical review OPEN decision; obtain original final independent-review text if available.
4. Update programme ledger only with evidence status and obtain independent WP7 D1 release review. No tag before acceptance.

**Disposition:** CONDITIONAL for bounded WP7 preparation, not a verified release baseline or WP7 release acceptance. No experimental P1 / measured V1 claims.
