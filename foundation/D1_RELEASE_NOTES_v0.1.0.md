# Materials Design D1 — proposed bounded release v0.1.0

**Status: release candidate for programme-owner approval; NOT RELEASED / NOT TAGGED.** Tested accepted implementation `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`. Later packaging commits are documentation only.

## Supported

- WP3 seeded synthetic intended-state comparison of homogeneous, layered and gradient designs, separate numerical-quality and eligibility flags and WP3-only Pareto.
- Selected completed compatible two-constituent A/B WP3 gradient can be passed to a newly re-evaluated WP4 intended / *estimated achieved* state context, with source ledger/run/evaluation/design hashes retained. Incompatible architectures, materials, mesh, mass/solver/brief constraints are rejected.
- WP4 synthetic assumed layer/feed resolution, conditional density/areal-mass feedback revision and *WP4-only* Pareto. WP3 and WP4 Pareto sets are not pooled.
- Candidate-boundary cooperative cancellation, durable checkpoint, recovery into a new immutable dossier, verification, replay, and separate-process recomputation.
- Streamlit demonstrations, saved WP3 workspace/verified ZIP and WP4 dossier with provenance companion.

## Non-negotiable packaging rule

**A WP4 `*.json` dossier plus its `*.handoff.json` companion is not a standalone portable combined bundle.** The original WP3 campaign ledger, SQLite/run-store, hash-addressed artifacts and/or complete verified WP3 ZIP must also be retained and restored to a compatible location for independent source-lineage verification. Do not delete the source WP3 workspace after handing off to WP4.

## Scientific limits

Synthetic models and hypothetical material catalogues; thermal transmission, areal mass, tensile thermal mismatch (not full process-history residual stress); no validated ceramic process physics or achieved-state measurements. No manufacturing feasibility proof, shrinkage/sintering/porosity/CFD/uncertainty validation, production readiness, aviation qualification or engineering certification. Cancellation occurs between candidates, not mid-solver. Low-resolution preview results may be numerically unqualified. P1 algorithm superiority, P2 external benchmark, P3 measured validation and E1/E2 are excluded. D1 is not V1.

## Prior independent review and qualification

- Final Gate 1 PASS (bounded), Gate 2 PASS, Gate 3 PASS (bounded): [WP7 independent PR #19](https://github.com/DavidOWilliams/Materials-design/pull/19), report `review/WP7_FINAL_INDEPENDENT_CORRECTIVE_ACCEPTANCE_2026-10-28.md` on its review branch.
- Implementer exact-source [run 40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663), artifact `12815911040`, SHA256 `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`, 99/99 archived entries verified by reviewer.
- Independent [run 40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535), artifact `12818005576`, SHA256 `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`, 41/41 checked.
- Superseded Gate 1 BLOCKED original independent [PR #17](https://github.com/DavidOWilliams/Materials-design/pull/17) retained as historical negative finding. PR #18 corrects IR01/IR04. No retrospective renaming of failures.

**Proposed eventual tag:** `d1-v0.1.0` (do not create until owner authorises final merge/tag and release SHA fixed).
