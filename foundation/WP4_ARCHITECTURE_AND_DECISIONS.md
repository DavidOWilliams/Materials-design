# WP4 architecture and decisions — bounded synthetic capability

## Design/state separation
The authoritative `IntendedDesign` is immutable. `ProcessScenario` declares layer and feed resolution. `ManufacturingCommands` records discrete per-layer composition. `EstimatedAchievedState` encloses a geometry container whose type happens to be `IntendedDesign`; it is **not** a second original intention. `MeasuredAchievedState` is never populated by this synthetic implementation. `RunInputs.evaluation_target='estimated'` routes WP2 to estimated geometry, without fallback.

## Mapping
Coordinates run hot face to cold face over normalized thickness [0,1]. The physical coupon thickness is unchanged. The number of layers must be a positive integer <=10,000; non-divisible thickness is rejected. Each layer command uses analytically integrated intended fractions across its interval, respecting layered discontinuities and gradient knots. A two-constituent feed is rounded to the nearest step, with ties to the lower first-sorted constituent level. Endpoints are included. Unsupported non-volume composition bases and unsupported routes are rejected. Commands declare a **unit projected area** rather than inventing an absolute coupon volume.

Estimated geometry assumes perfect deposition and perfect interfaces only. No mixing delay, shrinkage, porosity, sintering, CFD, geometry defects or total manufacturing residual stress is calculated. The WP2 `tensile_thermal_mismatch` is not manufacturing residual stress.

## Material accounting
`wp4_balances.balances` independently integrates intended layer fractions and sums commanded/estimated fractions on the unit-area basis (m3/m2). It reports signed per-constituent differences, integrated absolute layer-average fraction error and maximum layer-average fraction error. Feed rounding can change constituent budgets. No post-quantisation renormalisation to restore a target is allowed.

## Closed-loop demonstration
`wp4_feedback.run` holds the duty, property pack, resolution and numerical settings fixed. A binding achieved areal-mass cap produces feedback with metric, limit, actual value, units and admissible revision variable. The bounded two-phase density-guided policy increases the lighter phase's intended fraction by 0.25, preserving parent hashes. The new design is transformed and re-evaluated. The first numerically qualified, conditionally feasible result terminates; otherwise budget or an explicit stopping reason applies. This is a demonstration policy, not a generic optimiser.

`wp4_comparisons` freezes an on/off maximum budget and a five-point layer/feed sensitivity grid. Early stops may consume fewer evaluations; no equal-expenditure improvement is claimed.

## Persistence and qualification
`wp4_feedback.save` writes a single immutable JSON dossier and refuses overwrite. `reopen` checks content hash, input/evaluation identity, process, design lineage, summary metrics, feasibility, feedback, balances and revision causality. `recompute` regenerates transformed inputs and WP2 results. Hash checks prevent accidental corruption; reconstructing key derived fields detects selected resealed forgeries. This is not an adversarially authenticated evidence store, multi-writer journal or crash-safe resumable campaign.

WP3's search engine and WP2's numerical solver are unchanged. No new scientific physics is introduced. Independent Gate 3 review remains separate.

## Outstanding work and deferred requirements
- No full process/evaluator registry; current transform route is a hard-coded bounded capability.
- No alternative-duty campaign, resumable crash recovery, or failed-attempt durable journal.
- No separate measured validation, evidence-based ceramic calibration or process prediction.
- No independently signed evidence manifest or formal Gate 1/2/3 acceptance ledger.
- No WP5 interface or full D1 product completion.

Do not treat a passing regression suite as acceptance of these missing capabilities.
