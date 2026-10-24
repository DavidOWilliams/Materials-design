# WP3 frozen-review package and independent-review assignment

This package exists for an independently tasked reviewer; authorship and GitHub Actions execution do not constitute independent approval.

## Review subject
- Dedicated branch: `wp3-inverse-search-2026-10-24`, draft pull request #3, unmerged.
- Corrected WP2 reference: `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`; solver identity `wp2-bounded-2`.
- Sources: `material_core/wp3_adapters.py`, `wp3_provider.py`, `wp3_search.py`, `wp3_campaign.py`, `wp3_vertical.py`, `wp3_qualified.py`, `wp3_pareto.py`; immutable `store.py`, WP2 evaluator and tests.
- Review separately: numerical references, Pareto ranking, search/sampling fairness, reproducibility and recovery, evidence maturity, and whether software contracts preserve the full Vision v3.
- Evidence: matching final-head GitHub Actions workflow logs and complete uploaded run-store artifacts; `WP3_ACCEPTANCE_LEDGER.md` and `WP3_VISION_TRACEABILITY.md`.

## Predeclared scientific and ranking references

1. Independent homogeneous conduction check: steady 1D planar flux magnitude = temperature difference divided by thickness-over-conductivity (60,000 W/m² at k=6 W/(m K), ΔT=100 K, 0.01 m). A uniform stress-free plate under linear through-thickness temperature change must show near-zero artificial thermal stress under the free-bending model.
2. Areal mass of a mixture = thickness times the volume-weighted density; a bound is satisfied or violated independently of quality/evidence. The historical 0.35 example violates the 31 kg/m² mass cap, while 0.65 meets the declared constraint. Neither implies manufacturing feasibility.
3. WP2 numerical gate includes separately doubled mesh and thresholds for sampled tensile mismatch, curvature, heat flux and mass. Verify exactly implemented denominators and near-zero rules; do not infer global error bounds from mesh agreement.
4. Under a common compatible context, compare only complete, constraint-satisfying, numerically qualified objective vectors. Pareto comparison must not silently include unknown, missing, nonfinite or ineligible options. Ties are deterministic, and preference is not dominance.
5. Sampling baseline: identical fixed start, catalogue, objective definitions, constraints, mesh policy and evaluation caps, with isolated caches and published paired seeds (11,23,37). Report coverage, qualified and constraint-satisfying counts, effective solve counts and whether search improves, ties or loses. No superiority is assumed.
6. Verify changed mass-bound scenario does not secretly relax or reweight constraints; when no candidate qualifies the output must say so.
7. Check intended/estimated/measured target identities and that no process transform or empirical material claim is inferred from this software demonstration.

## Reviewer questions and possible blockers

- Are the *additional synthetic constituent* and its complete property/provenance domain a valid software test only, with no implied ceramic material evidence?
- Does the generic campaign service contain avoidable fixture names or scientific hard-coding? Can a provider test double and evaluator double be substituted without changing Pareto logic?
- Does every candidate reach final ranking through WP2-derived numerical eligibility and compatible context?
- Do the persistent decision and separate-process numerical recomputation detect altered or missing run artifacts?
- Are actual kernel solve counts defensible in failure cases? Any unknown number of partial attempted solves must remain flagged uncertain.
- Does cache isolation make the paired baseline fair, and do the specific seeds expose outcomes rather than cherry-pick?
- Do edge and failure tests cover scenarios materially different from implementation-owned nominal examples?
- Are the exact F01–F10 and C01–C10 results sufficient, including legacy regression, historical compatibility and user-facing CLI examples?
- Are new scientific models, global optimality, real ceramic manufacturability, measured validation or WP4/5 outcomes improperly claimed anywhere?

## Independent-review record

**Status: PENDING.** No independently commissioned human or separate-task review agent has checked or approved these findings. Record reviewer identity, exact reviewed SHA, independent method/references, blocking findings, resolution commit, rerun links and final outcome when available. Do not mark Gate 3 accepted before that occurs.

## Independent inspection corrective package — 24 October 2026

The inspection reviewed `3e46821daad059e2538a73ef521315ecde4a70a2` and identified:
1. Lost attempted evaluation accounting after a real WP2 solve raises `KeyboardInterrupt` before result persistence.
2. Forged derived counters/objective summaries accepted during ledger reopen.
3. Ambiguous "final-head" evidence from a pull-request temporary merge checkout.

Both implementation defects were reproduced before change at [Actions run 40126364720](https://github.com/DavidOWilliams/Materials-design/actions/runs/40126364720). Corrections are in `wp3_search.py` and the focused `test_wp3_inspection_corrections.py` tests. The latest finding-to-fix-to-test matrix and the exact heads / CI event identities are in `WP3_ACCEPTANCE_LEDGER.md`.

### Reviewer sequence and required independent tests

- Fetch PR #3 and record *separately* the reviewed branch-head SHA, any GitHub-generated PR merge SHA, event name, CI run, job IDs and artifact hashes. Do not say a merge-commit test was a direct branch-head check.
- Independently calculate 1D Fourier conduction, free-bending homogeneous zero-stress reference, areal mixture mass and the `mid_fraction=.35` (constraint-violating) vs `.65` (conditionally constraint-satisfying) scenarios. Inspect physical units, evidence maturity and mesh-doubling thresholds without copying implementation-owned expected values.
- Run original defect reproductions using an **isolated checkout of the exact inspected commit** (the reproducer was added later) and contrast with corrected tests for `KeyboardInterrupt`, `os._exit(57)`, post-commit interruption, ledger write interruption, counter and objective/constraint tampering, and seeded resume.
- Independently audit the semantics of `evaluation_attempts`, `unique_evaluations`, `successful_evaluations`, `failed_attempts`, `cache_hits`, `confirmed_numerical_solves`, `uncertain_evaluation_attempts`, and the flag `kernel_solve_count_uncertain`. An interrupted opaque adapter cannot establish actual partial kernel count.
- Inspect the exact durable `RunStore` evaluation artifact and compare all reported objectives, constraints, numerical qualification and manufacturing/evidence statuses; verify the ledger never silently repairs corruption.
- Review proposal integrity across constituent and architecture changes, parent links and comparison-context boundaries, with and without feasible Pareto options.
- Verify paired methods have the same total campaign proposal budget and separate caches, read the actual objective vectors and acknowledge that observed small-seed results show no clear optimisation superiority.
- Examine the exact crash/persistence intervals: pre-proposal cancellation; between SQLite `create` and first journal record; interrupted evaluator; persisted evaluation before journal update; journal temporary write / replacement. Confirm documented orphan-run limitation and whether it is acceptable for this bounded release.
- Check all F01–F10 and C01–C10 acceptance mappings on a single final code revision and review package. Only an independently tasked review that closes blocking findings can approve Gate 3.

### Remaining threats and limitations

The check is for *internal evidence coherence*, not tamper-proof external attestation. There is no signed append-only journal and no defence against coordinated malicious rewriting of all SQLite and JSON evidence with recalculated identifiers. There is no demonstrated multi-writer concurrency. A crash between the store's new-run insertion and the ledger's first link can create an orphan run; it cannot be inferred from a journal alone. An external evaluator's reported identity does not guarantee scientific equivalence to the corrected WP2 method. This still uses synthetic constituent properties and simple planar thermomechanics, never actual ceramic manufacturing qualification, total residual-stress history, D1 or V1.

### Review record

**Separate independent reviewer: not yet assigned. Gate 3: PENDING.** The corrections and implementation-owned CI are inputs to independent scientific/architecture assessment, not its conclusion. A reviewer must record name/agent identity, exact inspected checkout SHA, original independent reference computations, each finding, blocking severity, correction verification and explicit acceptance/rejection on the reviewed source revision.

## Re-review challenge R1–R4, frozen reviewed original and corrected code

Run `foundation/reproduce_reviewed_wp3_r1_r4.py` using **only** the exact original source revision `d62023d7205d48beba11269d4c358a7380ab9ca4`; `.github/workflows/wp3-verification.yml` has an immutable `wp3-original-review-reproduction` job to demonstrate the four original defects. Record the checked-out SHA from the log and distinguish it from the temporary pull-request merge SHA.

Then review the corrected independent acceptance suite `foundation/tests/test_wp3_review_r1_r4.py`, plus the R1 retired-API tests, R2 older fault-injection recovery tests, R3 state/termination tests and R4 materially different scenario tests. Review the complete immutable stores rather than only author-side assertions.

**R1:** Test `run_campaign` and `reopen_campaign` now reject schema-1 execution/replay, including fictitious counters and Pareto IDs; old artifacts are retrievable only as `UNVALIDATED_LEGACY_V1` with `review_eligible=false`. This is deliberate API retirement, not transparent migration. CI must execute schema-2 `wp3_search` exclusively for WP3 acceptance.

**R2:** Under a pending later evaluation, modify the first completed candidate's objective, constraints, qualification, manufacturing/evidence maturity or decision summary and attempt ordinary resume. Check that errors occur *without rewriting the ledger*. Verify valid pending recovery after a crash before, during and after solver result persistence. Check uncertainty of actual kernel solve counts remains explicit.

**R3:** Check closed stop reasons and terminal events are consistent with budget, proposal count and pending work; reject `manufacturing_validated` as a terminal campaign claim. Verify cancellation, wall-time cutoff, full-budget exhaustion, mid-run interruption and stop-history transition to running on resume. Distinguish internal journal of external decision from cryptographically verifiable event.

**R4:** Confirm campaign orchestration no longer inspects the three geometry variants or constructs from a fixed A/B fixture. A versioned provider owns start, proposal, build, validate and baseline, while objective/constraint and brief/property-pack identities come from typed contracts. Check the **380/320 K, three-layer, two-phase** alternate scenario with its own provider identity versus the default **400/300 K** catalogue. Independently inspect its persisted evaluated WP2 inputs, qualified comparison, cancellation/resume and separate-process replay. Try unknown/unavailable providers and numerical evaluator identities. The current exploration methods are structured seeded sampling and randomized sampling—not a feedback-adaptive optimiser.

The re-review acceptance decision must be made on the precise tested branch SHA and recorded PR-merge SHA. A successful four-defect historical reproduction, an implementation-owned regression run or a CI success does **not** supply independent scientific or architecture approval. Maintain the explicit synthetic-data and manufacturing-unknown boundary, and do not infer D1/V1/WP4 progress from WP3 tests.

**Independent re-review status: PENDING.**
