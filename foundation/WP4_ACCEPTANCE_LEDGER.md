# WP4 internal acceptance ledger — OPEN

This ledger is implementation-owned and **not** independent Gate 3 acceptance. Source authority: WP4 Manufacturing Feedback Implementation Brief v1.0, 25 October 2026. Actual test execution is tracked in GitHub Actions on the PR branch; the WP3 workflow includes WP4 tests through foundation pytest discovery.

| ID | Current disposition | Evidence / remaining gap |
|---|---|---|
| F01 | Partial | Inherited WP2/WP3 regressions run on PR; full dedicated WP4 environment evidence not packaged |
| F02 | Partial | Transformer and analytical tests; wider architecture/gradient coverage incomplete |
| F03 | Partial | Unit-area balance service and signed-difference test; independent comprehensive references incomplete |
| F04 | Partial | WP2 estimated-target bridge; process-resolution objective-difference evidence not frozen |
| F05 | Partial | Executable mass-cap feedback revision and tests; final numerical qualification dossier not independently audited |
| F06 | Partial | Impossible mass cap test; explicit unresolved candidate and termination reporting incomplete |
| F07 | Partial | Paired on/off service, same maximum budget; cost comparability and raw constraint export incomplete |
| F08 | Partial | Preregistered five-point grid; raw evidence archive and independent assessment outstanding |
| F09 | Partial | Save/reopen/recompute tests; separate-process portable full-store evidence outstanding |
| F10 | Partial | Cooperative cancellation, fsynced append-only candidate journal and deterministic recompute-and-append resume with prefix checks; mid-kernel recovery unsupported |
| F11 | Partial | Distinct synthetic uniform-batch transform registered and tested through WP2; existing WP3 alternate-duty adapter uses common WP4 bridge; raw final-run evidence pending |
| F12 | Partial | Export marks measured evidence absent; resealed fabricated measured-evidence challenge added; broader provenance challenges incomplete |
| C01 | Partial | Non-divisible thickness and basic validity tests; coarse/fine extremes incomplete |
| C02 | Partial | Two-phase feed quantisation; multi-constituent and tie challenge incomplete |
| C03 | Partial | Binding budget and signed balances; full fidelity-limit policy missing |
| C04 | Partial | WP2 missing geometry rejection inherited; missing data challenge incomplete |
| C05 | Partial | Resealed fabricated measured-evidence field rejected; coordinated nested-state forgery not yet covered |
| C06 | Partial | Context identity and process hashes; registry/version/cache challenge incomplete |
| C07 | Partial | Numerical eligibility enforced; failed transform evidence journal missing |
| C08 | Partial | Resealed summary, feasibility, feedback, counters and lineage mutation tests; adversarial coordinated rewrite not covered |
| C09 | Partial | Fsynced checkpoint journal, truncated-tail rejection and deterministic recompute-and-append resume; independent crash/restart qualification outstanding |
| C10 | Partial | Two registered synthetic transforms, fail-closed route and replay identity checks; independent evaluator registry and coordinated identity mutations incomplete |
| C11 | Partial | Deterministic bounded policy; Pareto tie and ordering challenge incomplete |
| C12 | Partial | Impossible budget and cancellation; zero/tiny budget and reversal challenges incomplete |

**Gate 1:** OPEN. **Gate 2:** OPEN. **Gate 3:** NOT STARTED (must be independent).

Historical accepted WP3 implementation: `790c3521f09e3f61615702de3b149c9f315e9e74`. WP4 stacked PR #4 is not merged. No physical ceramic validation is claimed.

## Added qualification path

Dedicated workflow `.github/workflows/wp4-qualification.yml` runs locked WP4 focused and full foundation/recovery tests, executes a direct-branch feedback campaign, separately reopens/recomputes its dossier, exercises an impossible budget and alternate duty, and uploads raw dossiers plus tested SHA. Its passing outcome is not presumed until the run completes. Existing WP3 PR CI remains a separate integration regression.

## Independent reviewer R1–R5 corrective work (25 October 2026)

- **R1:** `reopen` rejects multi-candidate records marked feedback-disabled, impossible continuations, mismatched process resolution, and terminal states inconsistent with candidate feasibility. Challenge: `test_wp4_r1_r4_review_closure.py`.
- **R2:** Each evaluation attempt and checkpoint failure is durably recorded in a sidecar event log; resumed runs disclose per-invocation `evaluations` separately from `cumulative_evaluations` and `replayed_evaluations`. For old journals without event sidecars, a lower bound is inferred and explicitly labelled. The journal is still not an independently authenticated ledger.
- **R3:** Exported baseline intended hash is the canonical `IntendedDesign.content_hash`, not the readable design ID.
- **R4:** Alternate-duty adapter now passes its typed baseline to the same `run` feedback campaign and exposes the complete campaign record, rather than invoking a one-shot transform.
- **R5:** This ledger is reconciled with `WP4_COMPLETION_REPORT.md`, `WP4_ARCHITECTURE_AND_DECISIONS.md` and `WP4_CHALLENGE_TEST_REPORT.md` at the final verified commit. Independent Gate 3 closure remains **OPEN** until that review.

**Do not interpret R1–R5 code changes as independently closed without a pinned passing CI run.**
