# Scientific evidence roadmap — P1 / P2 / P3

**Authority:** Implementation Plan v2 (2026-10-20), original and corrected WP6 protocols, independent WP6 Gate 3 decision (`foundation/WP6_INDEPENDENT_ACCEPTANCE.md`). **Status:** planned, NOT executed or validated. **D1** is a bounded synthetic working demonstration. **V1** is separately measured ceramic manufacturing validation. The long-term Vision is general-purpose material-system inverse design, **not aviation-only**.

## Scientific evidence hierarchy

Keep separate: (i) intended design; (ii) estimated achieved state from named process scenario; (iii) measured achieved state with specimen, instrument and uncertainty; (iv) numerical *verification* of code/replay/conservation; (v) numerical *qualification* against independent references and applicability; (vi) conditional scenario-based manufacturing feasibility; (vii) physical manufacturing validation. Neither runtime tests, third-party property tables nor synthetic process quantisation establish (iii) or (vii). Scientific uncertainty is not reduced by running the same deterministic model repeatedly without varying defensible inputs.

## P1 — Equal-effort feedback and comparative search evaluation

**Question / decision:** Does achieved-state-informed revision outperform a non-feedback alternative (and a sensible search baseline) on *identically evaluated achieved-state objectives* for a qualified bounded family, at the **same actual numerical cost**? Decide whether feedback adds real design value rather than just more candidate evaluations.

**What exists:** WP4 scenario maps intended to estimated achieved state and triggers a feasible revision; WP6 three nominal-budget pairs and sensitivity cases execute. Control-on uses 4 evaluations / 8 refinement solves and reaches one feasible candidate; control-off uses 2 evaluations / 4 refinement solves and zero feasible. WP6 correctly declares no equal-effort causal superiority. The common prefix is diagnostic only; no independent comparator performance demonstrated.

**Methods:** Preregister fixed scientific brief, compatible material catalogue, solver settings and common final achieved-state evaluator. Compare (A) full manufacturing-feedback search, (B) no-feedback search with *equal real evaluation opportunity* and common achieved-state post-evaluation, (C) random or space-filling sampling, and optionally (D) objective-aware baseline. Use identical starting set, hardware/environment and fixed maximum actual evaluator calls; separately report refinement solves/wall time/failed calls. Introduce at least 10 independent **predeclared search seeds** if stochastic search is implemented or uses a controlled sampler; do **not** relabel a deterministic single run as replicated trials. Pair runs by seed and brief, use multiple feasible fixtures and hold them fixed; report Pareto dominance or hypervolume only if reference point and objective directions are frozen, alongside per-objective raw values, constraint violations, no-feasible rate, failure/cancellation, paired differences and dispersion. Never budget 'free' common-evaluator computations selectively. Where search strategies stop early, handle unconsumed budget as data, or use a preregistered symmetric stop policy; never fabricate extra solves or force failure into success.

**Alternatives/risks:** If modifying the accepted WP5 stopping behaviour is needed, first implement comparison-specific adapters in a future authorised package, not in frozen WP6. Exploratory matched *prefix* is not a feedback superiority test. A negative/inconclusive result is a valid scientific outcome. Paired seeds are only meaningful when algorithmic randomness really varies.

**Dependencies:** WP3/WP4 numerical eligibility, stable WP5 evaluator interfaces, explicit compute-accounting model, P2-qualified comparator fixture; no new physics/model training. D1 release does not depend on P1. WP7 should make the non-claim explicit.

**First bounded deliverable:** A protocol-only candidate benchmark specification and cost-accounting worksheet for 2 qualified D1 fixtures, 3 comparator policies, 10 paired seeds **conditional on stochastic variation**, explicit evaluator-call and refinement-solve rules, and acceptance thresholds preregistered *before running*. No application feature changes yet.

**Acceptance/evidence:** protocol SHA, frozen fixtures and seed list, deterministic audit of actual numerical calls, source/env SHA, full candidate trajectories, common achieved-state evaluations, feasible/infeasible outcomes, paired objective and feasibility summaries with dispersion, manifest/replay. A 'pass' means reproducible unbiased comparison **regardless of which method wins**, not a required positive result.

**Indicative effort / uncertainty:** protocol and feasibility audit ~1–3 active days; comparator implementation/evaluation ~3–10 more days if interfaces suffice, longer if stopping/search abstractions require change. Estimates are planning assumptions, not commitments. High risk: comparator parity, meaningful stochastic variation, comparable physical constraints.

**Link:** Post-WP6 P1; may be parallel to WP7/D1; not a V1 substitute. Scientific results may inform subsequent roadmap/optimisation work, not determine D1 release approval.

## P2 — Independent numerical benchmarks and staged held-out generalisation

**Question / decision:** Which supported physical-domain predictions survive held-out inputs and **independently published** references, and where are applicability limits? Determine when a new architecture/material case is qualifiable.

**WP6 reality:** Held-out *duty description* changed brief hash, **not** thermal/mechanical inputs or objective outcomes. Mass-limit and layer/feed variations exercise supported constraint/process sensitivities. WP6 did **not** verify scientific generalisation to unseen parameter combinations, new materials/architectures, or new physical mechanisms.

**Stage 1 (within supported equations):** Register independent published **planar steady 1D conduction** homogeneous, layered and graded fixtures with full boundary conditions and analytical/refined reference outputs. Hold out parameter and layer/fraction combinations not used in earlier WP2/WP4 qualification. Record units, phase/property basis, layer widths, restraints, mesh-convergence criterion, numerical tolerance and independent reference derivation. Reproduce against WP2 only where the boundary value problem truly matches.

**Stage 2 (within qualified domain):** Seek compatible property packs and different supported architecture/material combinations (homogeneous, discrete layers, continuous gradient) under common brief. Verify provenance and constitutive assumptions; no isolated property values 'stitched' into seemingly validated material records. Preregister hold-out and applicability. Challenge stress-free reference, thermal mismatch, constrained/free expansion and any known ill-posed near-zero moments.

**Stage 3 (new physics):** Treat alternate geometry, CFD extrusion flow, mixing lag, shrinkage/sintering, total residual stress, coatings/substrate interfaces and lifecycle effects as *future qualification projects* requiring existing applicable FE/CFD method, independent references and authorization. Never extrapolate the current planar model to them because a literature article happens to present a different geometry.

**Candidate published sources to screen (not yet approved benchmark fixtures):**
- Rakocha & Popovych (2016), open-access three-layer thermosensitive hollow-cylinder analytic study: https://reference-global.com/article/10.1515/ama-2016-0027 — **different cylindrical geometry; not directly applicable to planar WP2**.
- Shypul & Myntiuk (2020), layered-cylinder transient thermoelastic solution: https://pp.bme.hu/me/article/view/14733 — **transient/cylindrical; not a direct WP2 qualification case**.
- NIST AM Bench https://www.nist.gov/ambench — public benchmark data programme mainly relevant for method illustration; **do not infer ceramic relevance or permission for a particular dataset without dataset-level inspection**.

**Alternatives/risks:** Create independent hand-calculated stratified-planar references for stage 1 if compatible published benchmark unavailable; record independence from production implementation. Mesh refinement and conservation plus signed thermal forces/moments should accompany any comparison. Fail or label unresolved when constitutive or boundary contexts are incompatible.

**First bounded deliverable:** Benchmark applicability matrix with **three** independent planar reference fixtures and **one** rejected out-of-domain candidate; record DOI/reuse rights, exact numerical reference extraction, hold-out split, tolerances and unresolved properties. This is a **benchmark selection/qualification proposal**, not a claim of executed validation.

**Acceptance/evidence:** frozen fixture/reference hashes; independent calculations; property/source conditions; at least two mesh levels plus tolerance justification; no fitted parameter tuned to hold-out outputs; signed errors and fail/inconclusive disposition; domain-of-validity matrix; separate reviewer signoff.

**Indicative effort / uncertainty:** sourcing/screening 2–5 active days, reproducible stage-1 benchmark 3–8 additional days depending on published data quality; higher stages separately scoped. High uncertainty: source transparency, property-pack consistency, model-domain mismatch.

**Link:** P2 can proceed alongside WP7; stage-1 numerical benchmarking strengthens model credibility but is not a retrospective WP6 gate; out-of-domain physics is outside D1. Stage 2/3 support the longer general-purpose inverse-design Vision and later FE/CFD integrations.

## P3 — Measured ceramic achieved-state and independent baseline/revision validation (E1/E2)

**Question / decision:** Given real ceramic process commands and input materials, how accurately does a qualified process/achieved-state model predict actual geometry, composition and relevant density/porosity, and does a frozen revised design outperform baseline under measured manufacturing constraints?

**Existing:** WP0 evidence contains partial alumina/zirconia CODE reproduction and a separate B4C–SiC benchmark fragment (see WP0 reproduction/evidence records). They are NOT joined specimen-level command→achieved-state evidence, and budgets/experimental contexts differ. WP6 archives all have measured evidence null. No physical validation established.

**E1 staged acquisition:** (1) inventory existing CODE/alumina–zirconia records and corresponding published sources; (2) screen appropriately licensed public datasets for exact process commands, actual deposited volume, composition maps or elemental analysis, layer geometry, shrinkage state, porosity/density, specimen/run IDs and calibration/uncertainty. NIST ceramic AM metrology programme (https://www.nist.gov/programs-projects/additive-manufacturing-ceramics) is a discovery lead, **not proof of a downloadable reusable linked ceramic dataset**. NIST AM Bench datasets are method references, not assumed ceramic datasets. Verify per-dataset licence, raw access, units, measurement provenance and missing fields; publications alone do not grant broad machine-use rights. (3) Decide reuse, data request (user authorization required), or narrowly scoped new measurements (user authorization/cost required). No third-party contact here.

**Proposed minimum data contract:** run_id/specimen_id, machine/process/method, material feed identities and composition basis, timestamp and versioned commanded settings (mixing ratios, flow/extruded volume or masses, speed, layer height, feed-switch timing); deposition accounting; intended profile; achieved geometry and composition at registered coordinates; density/porosity and shrinkage state *if measurable/relevant*; sampling/measurement instrument, calibration and uncertainty, specimen history and provenance/reuse terms. Missing measured fields stay null. Separate as-printed/dried/sintered stages.

**E2 staged validation:** Choose one genuinely supported ceramic case and scientific reviewer. Preregister baseline and revised recipe, material balance, allowable porosity/geometry deviations, success criteria, sample sizes and hold-out specimen allocation **before** observing comparison outcomes. Use existing applicable physics/process model; do not invent surrogate or train a predictor in this work. Compare intended→estimated→measured fields with errors and documented systematic/measurement uncertainty. Recompute both designs under **measured** achieved state and eligible physical constraints. Track negative outcomes, uncertainty, manufacturing failure, outliers and domain applicability. If key measurements unavailable, classify result as narrower feasibility/geometry evidence, not V1 validation. Require separate scientific and data-rights review.

**First bounded deliverable:** A one-page data-readiness matrix (E1), specimen-linked command→achieved-state schema, rights register, and a single baseline-versus-revision preregistration outline for E2. Include 'unavailable' columns rather than fabricating records. Choose whether literature reuse is plausible before proposing experiments.

**Acceptance/evidence:** E1 = source-level rights and missing-fields ledger, raw/publication IDs, realistic acquisition route and go/no-go readiness decision. E2/V1 = preserved raw datasets, specimen/command keys, metrology/calibration and uncertainty record, frozen baseline/revised criteria, independently reproducible outcome comparison, numerical/physical applicability and signed scientific-review disposition. **V1 remains blocked until these exist**.

**Indicative effort / uncertainty:** desk screening and schema 2–5 active days; suitable public dataset search 3–10 further active days; experiments, metrology and independent review **unestimated** until laboratory access, specimen numbers and rights/costs are known. High risk: sparse composition data, porosity measurement comparability, mismatch between recipe and achieved state, restrictive rights.

**Link:** P3 operationally implements E1 then E2. E1 can proceed in parallel with WP7; E2 depends on actual suitable data and scientific reviewer. **Not a WP7/D1 blocker; V1 blocker.**

## Cross-workstream review controls

1. Single ledger: `foundation/PROGRAMME_DELIVERY_LEDGER.md`. Existing WP3/WP4 ledgers remain historical authoritative *for those packages*; do not duplicate them.
2. Each protocol gets frozen source/fixture/decision version **before** executing. Record failures, incompatible comparisons and negative results. No post-hoc source substitution without explicit ledger amendment.
3. Neither P1/P2 nor P3 justifies claiming the wider Vision already operates: specialist material discovery, constituent changes beyond supported catalogue, coating architecture, CFD extrusion physics, high-fidelity residual stress, lifecycle trade-offs, and general inverse FE optimisation remain future candidates, not accepted present scope.
4. WP7 must prove D1 release independently. P1/P2/E1 may run parallel without altering frozen WP5/WP6. E2/V1 is a separate scientific milestone.
