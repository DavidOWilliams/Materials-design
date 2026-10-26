# P1 recovery checkpoint — 2026-10-26

## Authoritative history
Accepted tested WP5 source: 4078a83dc11e14703ff6cc03f5b62f4e48879d14.
Acceptance/evidence documentation: 5ade1e9650795427a8bb32de64dfce6c11cd0426 (not the tested source).
WP6 tested source c53dee793479843cc69926dd0da3663f22483b2f; reviewer PR #8: Gate 1 PASS, Gate 2 OPEN, formal Gate 3 acceptance withheld. WP6 must NOT silently replace accepted WP5 as P1 source.
Current P1 correct branch: p1-equal-effort-from-accepted-wp5-2026-10-26.
Previous WP6-based exploratory branch p1-equal-effort-feedback-2026-10-26 is NOT authoritative; do not merge it.

## Confirmed design blocker
Accepted WP4 module foundation/material_core/wp4_feedback.py: run() stops feedback=False immediately after first candidate with stop_reason=feedback_disabled. feedback=True can make repeated proposals using _revise() on the areal_mass constraint. Merely setting identical budget arguments does NOT give equal actual effort; WP4's comparison API explicitly does not assert a paired scientific comparison. Its feedback policy is density-guided, not a general multiobjective inverse optimiser.

## Assessment
Do NOT execute confirmatory P1 comparisons using WP4 run(feedback=False) vs run(feedback=True): structurally invalid. Manufacturing transform currently excludes mixing lag, shrinkage, porosity, sintering, CFD, and manufacturing residual stress. Cannot claim those scenarios or physically grounded distortion severity.

## Bounded correction
1. Reuse existing WP3 proposal generation or WP4 gradient candidate construction, WP4 estimated_inputs and WP2 evaluate; do not copy physics.
2. Build search orchestration which gives control arm independently generated proposals after its first result, without revealing manufacturing scores until independent final scoring. Give treatment arm appropriately separated feedback state.
3. Verify identical proposal eligibility, seed allocation, inputs, constraints and stopping policy; preserve failures and call counters for both arms. If group C/D algorithm is not genuinely distinct, omit it.
4. Audit independent evaluator/model assumptions. A common scorer using identical synthetic transform establishes only in-model performance, not physically independent validation.
5. Calibrate measured CPU cost, then freeze complete primary metric/reference bounds, scenarios, seeds, trial count, budgets and exclusions in a new versioned preregistration commit BEFORE confirmatory runs.
6. Run labelled pilots, full tests and scientific challenges; retain exact source SHA, CI run ids and SHA256 artifacts. Separate reviewer alone closes Gate 3.

## Work performed this session
Repository branches and WP6 PR #8 reviewed; WP5 acceptance evidence checked; WP3 and WP4 source and WP5 service inspected; provisional protocol committed, and draft PR #9 opened. No P1 harness, pilot, confirmatory trial, test run or CI execution has been performed; no results can be inferred. The preregistration draft is not frozen and cannot be treated as preregistered evidence for outcome analysis.

## Exact next executable action
Implement a minimal audited two-arm runner on this branch reusing existing WP3/WP4/WP2 components, with a fail-closed budget ledger and explicit final-scoring boundary; first write tests proving that the control arm can consume the full matched budget rather than stopping at one proposal, and that same-config candidate/scorer replay is reproducible. Do not run confirmatory experiments before protocol freeze.
