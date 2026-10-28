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


---

## Final verified integration-source manifest — 28 October 2026 (supersedes conditional status above)

**VERIFIED for bounded D1 integration baseline only.** Immutable application source `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`; WP7 branch `wp7-d1-reproducible-release-2026-10-27` / draft PR #12 remains documentation-ahead and unmerged. Verification-only workflow file `.github/workflows/d1-full-replay.yml` was enabled via CI-only PR #15, merged to main at `8ccf11aa7b93ad9baca57b8c3640664e1de7427c` — NOT an application implementation commit and NOT the tested checkout.

- Core clean environment/regression: [run 40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136), artifact 12805993031, 350 regressions + 15 WP6 focused/reproduction tests, passed.
- Complete selected integration/replay: [run 40668433992](https://github.com/DavidOWilliams/Materials-design/actions/runs/40668433992), job 122748812186, artifact 12807606181, checkout `1f89c2d...`, 157 WP3/WP4 integration tests, WP1/WP2 (8 scenarios) replay, WP4 4096-cell 3 recomputations, WP6 nine 4096-cell campaigns/nine independent-process replays, historical unresolved-case reproduction and external SHA256 archive checks, Streamlit startup/health check, complete success.
- SHA256: complete artifact metadata and independently computed ZIP SHA256 `d8367e5c25699609e14f8038b8b5932bbe6c819fc3fc36086e737fd0d73fcdfb`; all 99/99 entries in archived `SHA256SUMS` match. Prior core artifact `62ce54d59bc9de714941d4158bfe86750fcb0340b5d03a010f67b75cc7bc5ee9` and 12/12 internal hashes match. Historical archived ZIP verified using preregistered `39e01e06110ef612f6ff561dea6a2568b0fc8b539dde9c466e2cab4a6033d3da` with internal manifest; no false nonempty checks.
- WP2 corrected final-head CI `40073237148`: actual tested checkout `7009189d9be4dfd5940999c88cbb5c3c70c8ce56` is one report-only commit after last implementation-changing `a3a4d592c0e9a3bb42868ee46295a4ba3831af31`, thus tested application tree identical. See source register.
- WP6 final bounded acceptance is recorded as programme-owner supplied 27 October decision in `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`; the original independent final review text still requires retention/linkage. Historical earlier PR #8 OPEN decision retained and distinct.
- No P1, no changed accepted implementation, no release tag and no application PR merged. Existing documentation-only revisions of PR #12 are NOT separate tested source identities.

**Release controls remain:** WP7 implementation/package/user handover and independent release acceptance are separate from this verified integration baseline. No D1 release tag until explicit authorised gate closure.
