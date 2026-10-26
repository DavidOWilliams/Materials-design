# WP6 preregistered evaluation protocol — v0.1 (NOT YET EXECUTED)

Frozen before WP6 campaigns. Base: WP5 accepted implementation 4078a83dc11e14703ff6cc03f5b62f4e48879d14; acceptance/evidence 5ade1e9650795427a8bb32de64dfce6c11cd0426. This document is a protocol, not evaluation results.

## Scientific boundary
D1 synthetic computational demonstration only. Intended geometry, estimated achieved geometry and measured evidence are separate; measured evidence is unavailable. Numerical completion is not physical validation. Unknown is not pass. No new scientific models or trained predictors.

## Cohorts and preregistered contrasts
1. Original supported WP4 brief: control, fixed seed/search policy and budget.
2. Held-out duty-description brief: distinct immutable brief ID/version/duty text, created before campaign execution; never use its outcome to adjust algorithm parameters. WP5 accepts duty-description changes, not new physical thermal boundaries.
3. Constraint contrast: supported mass_limit 31.0 versus 30.0 kg/m² using separately generated compatible fixtures; document any incompatibility rather than imply unsupported WP5 brief constraint edits.
4. Process assumptions: layer 0.005 versus 0.010 m; feed 0.25 versus 0.50; explicitly version each scenario. Evaluate one variable at a time.
5. Feedback enabled/disabled: matched brief, numerical settings, material set, candidate budget and search policy. Count attempted, completed, rejected, failed and cancelled evaluations; no claim of causal physical superiority.
6. Negative cases: no improvement, no feasible candidate, invalid budget/input, unresolved numerical quality or missing measured evidence, corrupted persisted dossier and replay mismatch.

## Measures
Per run: exact source SHA, fixture hashes, brief identity, process version, settings, seed if supported, evaluation budget, attempted/completed counts, stopping reason, qualified/eligible candidate count, feasibility and constraint outcomes, objective values and units (thermal transmission W/m², areal mass kg/m², tensile thermal mismatch Pa), intended/estimated-achieved comparison, numerical quality and replay result. Missing values remain null. Preserve all candidate outcomes, not only winners.

## Decision rules
Report observed deltas without declaring superiority. Compare objective values only for eligible candidates in compatible numerical contexts. Distinct process assumptions are unpaired scenario comparisons. No feasible eligible solution is a reported result, not a harness failure. Integrity corruption must fail closed. Inconclusive is separate from pass and fail. No post-hoc replacement of the held-out fixture or budget.

## Evidence requirements
Before execution capture implementation commit, environment lock and SHA-256 fixture manifest. After execution archive raw dossiers/journals, commands, stdout/stderr, return codes, machine-readable results, separate-process reopen/recompute, hashes and failure ledger. The tested implementation SHA must be distinguished from any subsequent documentation/evidence commit.

## Gates
Gate 1: reproducible execution and persisted results. Gate 2: challenge/sensitivity/integrity verification with honest failure disposition. Gate 3: separately tasked independent reviewer only. Neither Gate 1 nor Gate 2 is claimed here.
