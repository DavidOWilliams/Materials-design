# P1 preregistration — provisional protocol, NOT FROZEN FOR CONFIRMATORY RUNS
Date: 2026-10-26
Branch base: c53dee793479843cc69926dd0da3663f22483b2f (WP6 branch head; acceptance unverified).
Status: DESIGN ONLY. Do not execute confirmatory comparisons until WP6 acceptance, supported WP4 transformation, and scoring independence are verified and this protocol is amended and explicitly frozen in a subsequent commit.

## Question and hypotheses
Does access to existing manufacturing-feedback predictions improve independently scored achieved-state feasible multiobjective outcomes under equal computational effort?
H0: no improvement. H1: improvement in at least one prespecified supported scenario. No directional superiority presumed.

## Design and fairness
Pair trials by seed and scenario. Compare random/space-filling feedback off/on (A/B); add inverse-search off/on (C/D) only if inspection establishes a genuinely distinct algorithm. Identical initial candidate domain, constraints, seed streams, numerical solver, stopping policy and common blinded final scorer. Feedback-off must not receive manufacturing information during search. Search outputs must be frozen before scoring. Do not treat identical synthetic process models for training and scoring as external validation.

## Scenarios
Identity, mild, consequential, feasibility-changing, tradeoff-changing, no-feasible, potentially detrimental, and held-out perturbation, ONLY if already expressible with supported WP4/WP6 contracts. Record model version, provenance and assumptions. Unsupported scenarios are declared non-estimable, not simulated with invented physics.

## Outcomes
Primary: paired difference in feasible achieved-state hypervolume at fixed, predeclared reference point and common independent evaluator. If valid reference bounds cannot be justified, primary endpoint must be amended and refrozen before outcomes are observed.
Secondary: feasibility probability, nondominated objective vectors, evaluations to target, failures, wasted evaluations, CPU time, cache behavior. No arbitrary weighted scalar aggregation.

## Budgets
Separate numerical calls, manufacturing calls, generation, failures, retries, cache hits/misses, final scoring, process CPU time and machine configuration. Two matched comparisons: justified measured-call-equivalent cost and actual CPU-time budget. Never equate call types without calibration. Independent scoring excluded from search budgets and identical across arms.

## Replication and analysis
Run labelled feasibility/runtime pilots first; do not pool with confirmatory trials. Before confirmatory work, freeze trial count, seed list, scenario parameters, call-cost calibration, budgets, reference points, target thresholds and exclusion criteria. Use paired bootstrap CIs where meaningful; report failures and zero-feasible runs without dropping them. Statistical and engineering significance separately assessed; no unplanned significance claims.

## Integrity and interruption
Immutable configuration hash including solver/process/scorer version, assumptions, seeds, dependencies and source SHA. Per-trial append-only records, atomic checkpoints, restart compatibility check, cache namespace isolation, independent replay, raw JSON/CSV and SHA256 manifest. No unverified success claims.

## Gates
Gate 1: infrastructure, budgets, identity and replay. Gate 2: adversarial tests, complete regression. Gate 3: separate independent reviewer; implementation lead cannot self-approve.

## Blocking prerequisites
1. Locate WP6 independent reviewer disposition and exact accepted tested-source SHA.
2. Inspect WP3 search, WP4 process, WP5 service, WP6 evaluation and Implementation Plan v2.
3. Verify genuinely independent scorer and model-supported scenarios.
4. Pilot and preregister numeric budgets, seeds, trial count and reference point BEFORE confirmatory execution.
