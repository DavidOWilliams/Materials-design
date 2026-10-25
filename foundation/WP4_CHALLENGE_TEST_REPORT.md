# WP4 challenge test report — implementation self-review (open)

**Authority:** WP4 Manufacturing Feedback Implementation Brief v1.0. This is not independent Gate 3 review.

## Tested challenge paths in code

- Analytical homogeneous, two-layer, linear gradient, interface discontinuity and feed-rounding tie references: `test_wp4_analytical_reference.py`.
- Thickness non-divisibility, unsupported process and strict registry route identity: `test_wp4_resolution.py`, `test_wp4_registry.py`.
- Signed constituent budgets and quantisation difference: `test_wp4_balances.py`.
- Binding mass constraint, feedback-generated revision and impossible budget: `test_wp4_feedback.py`.
- Feedback-on/off fixed maximum budget and predeclared five-point sensitivity grid: `test_wp4_comparisons.py`.
- Cancel before and after evaluation, append-only checkpoint, simulated failure after fsync, truncated tail and tampered journal: `test_wp4_cancellation.py`, `test_wp4_journal.py`.
- Dossier checksum, resealed forged metrics/feasibility/feedback/counters/lineage, numerical recomputation: `test_wp4_integrity.py`, `test_wp4_feedback.py`.
- Synthetic/measurement boundary and fabricated measurement export: `test_wp4_export.py`.
- Alternate-duty adapter through the common WP4 transformer: `test_wp4_alternate.py`.

## Limitations preventing Gate 2 closure

This list is not a substitute for F/C expected/actual tables tied to a pinned direct-branch run. Outstanding cases include coordinated mutation of nested process/transform inputs, interrupted journal **resume** (rather than inspection), missing-property challenges through all persistence paths, second distinct transform delegate, numerical near-zero/moment references on transformed profiles, explicit process-resolution mesh-independence, full cost accounting and robust Pareto checks.

No ceramic processing measurements are used. No claim of material manufacturing feasibility or scientific-model validation follows from these tests.

## Execution

Dedicated WP4 workflow: `.github/workflows/wp4-qualification.yml`. Review its actual run ID, checked-out SHA, job logs and uploaded dossiers. Earlier WP3 CI is inherited regression evidence only. **Gate 1 and Gate 2 remain open until individually audited against the final revision.**
