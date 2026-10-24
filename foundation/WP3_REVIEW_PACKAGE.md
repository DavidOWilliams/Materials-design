# WP3 frozen-review package and independent-review assignment

This package exists for an independently tasked reviewer; authorship and GitHub Actions execution do not constitute independent approval.

## Review subject
- Dedicated branch: `wp3-inverse-search-2026-10-24`, draft pull request #3, unmerged.
- Corrected WP2 reference: `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`; solver identity `wp2-bounded-2`.
- Sources: `material_core/wp3_provider.py`, `wp3_search.py`, `wp3_campaign.py`, `wp3_vertical.py`, `wp3_qualified.py`, `wp3_pareto.py`; immutable `store.py`, WP2 evaluator and tests.
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
