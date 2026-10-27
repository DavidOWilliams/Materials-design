# P1 scientific evaluation — confirmatory synthetic in-model study

**Status:** executed and software-verified; **independent Gate 3 review pending**.
**Exact tested checkout SHA:** `6eb62daec638185f5c5dc170182e9e0454b6e061`.
**Frozen protocol SHA256:** `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0`.

## Executive summary

Primary question: Does WP4's bounded density-guided areal-mass correction improve numerically qualified synthetic estimated achieved-state performance when WP3 proposal opportunities and numerical work are matched?

Across 80 paired trials, normalized feasible three-objective HV difference (feedback minus blind) was +0.014070 (95% paired CI +0.003704 to +0.025926; n=80).
At the preregistered 80 ms search CPU threshold, paired HV difference was -0.001729 (95% paired CI -0.005187 to +0.000000; n=80).
Trial-level feasibility difference was +0.000000 (95% paired CI +0.000000 to +0.000000; n=80).
The prespecified practical HV threshold was 0.02; assess statistical uncertainty and engineering materiality separately.
These are entirely synthetic results. No improved real manufactured ceramic performance is established.

## Frozen design and fairness

WP3 seeded sampling or structured exploration, two supported WP4 feed resolutions (0.25, 0.50), four proposal slots per arm, 20 paired seeds (2001–2020) per stratum, 80 pairs total. Each arm applies the same WP4 ideal process transform and WP2 numerical evaluator. Feedback-on additionally permits WP4's previous-violation density-guided revision; blind does not use achieved-state information to select future designs.
No additional optimisers were introduced. The exploration policy is a different proposal schedule, not a distinct inverse-optimisation algorithm. Cache hits are disabled for both arms. Separate final scoring costs are excluded from optimisation budgets.

## Computational budget and metric definitions

Matched numerical work means equal attempted proposal slots, WP4 transformations and WP2 evaluations. CPU-prefix results use measured generation, transformation, numerical and feedback calculation CPU time. Revision cost is included in proposal generation. The 80 ms threshold and all trial seeds were frozen before confirmation.
Three minimized objectives: thermal transmission W/m², areal mass kg/m², tensile thermal mismatch Pa. Fixed normalized hypervolume reference: 120000 W/m², 45 kg/m², 1e9 Pa. No-feasible designs contribute zero HV; infeasible attempts remain in the denominator.

## Full stratum-level paired results

| Scenario (proposal / feed) | Equal-work HV effect (95% CI) | CPU-budget HV effect (95% CI) | Feasible-rate difference (95% CI) | Held-out feed HV effect (95% CI) |
|---|---|---|---|---|
| explore / 0.25 | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) |
| explore / 0.5 | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) |
| sampling / 0.25 | +0.017274 (95% paired CI +0.000000 to +0.040422; n=20) | -0.006916 (95% paired CI -0.020747 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.048380 (95% paired CI +0.009375 to +0.096759; n=20) |
| sampling / 0.5 | +0.039005 (95% paired CI +0.000000 to +0.083449; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.000000 (95% paired CI +0.000000 to +0.000000; n=20) | +0.014815 (95% paired CI +0.000000 to +0.037963; n=20) |

## Raw outcomes and sensitivity

The attached all_paired_trials.json provides every paired objective vector, feasibility outcome, budget audit, seed, method and process scenario without outcome selection. Raw arm records, complete common-scorer output, per-candidate CPU ledgers, dependencies, source identity, curves and SHA256 manifest are retained in the same evidence directory.
Held-out rescoring switches 0.25 and 0.50 feed resolutions only after design selection. It checks sensitivity to another assumption within the SAME synthetic WP4 process family; it is not an independent empirical validation model.

## Interpretation and threats to validity

1. Software correctness is supported by focused tests, replay and full regression; this does not qualify physical ceramics.
2. Numerical eligibility is established only where WP2 reports qualified mesh/constraints; mesh 32 can leave objectives unresolved.
3. The correction targets an achieved areal-mass violation specifically and is not a multiobjective adaptive optimiser.
4. CPU comparisons are runner- and execution-condition-dependent and are not matched wall-clock, distributed or GPU budgets.
5. Synthetic achieved-state and holdout feeds share idealized physics, so superiority in this environment cannot establish physical or generalised superiority.
6. Only two supported feed resolutions and four-proposal budgets were studied; a true identity-process negative control is unavailable for arbitrary WP3 architectures.
7. These confidence intervals are descriptive and have not undergone separate independent statistical review; no unadjusted scenario-level multiplicity claims are made.

## Roadmap implications

P2 should challenge numerical quality and independent objective modelling using external published benchmarks without introducing unqualified physics. P3 should obtain independently measured ceramic command-to-achieved-state data and validate the process model out of sample. Only after those checks could feedback benefits be evaluated as manufactured performance rather than synthetic consistency.

## Independent Gate 3 reviewer tasks

Check frozen protocol precedes confirmation; inspect exact tested SHA and full CI raw log; rerun focused and foundation regression; independently recompute saved arms and objective metrics; verify paired seeds/candidate opportunities/cache policy/CPU accounting; recompute the 3D hypervolume and bootstrap estimates; test failure/no-feasible/identity-limit controls; assess scientific interpretation and heldout dependence; verify every SHA256 manifest entry.
**Gate 3 is NOT self-approved. WP6 Gate 2 remains OPEN and formal acceptance withheld.**
