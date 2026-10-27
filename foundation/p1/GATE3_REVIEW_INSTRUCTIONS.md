# P1 — independent Gate 3 review instructions (reviewer-facing)

**Status:** ready for independent scrutiny, **not independently accepted**. This document is a review handover, not a self-issued Gate 3 disposition.

## Exact source and evidence
- Accepted base: WP5 tested source `4078a83dc11e14703ff6cc03f5b62f4e48879d14`; WP5 acceptance documentation `5ade1e9650795427a8bb32de64dfce6c11cd0426` is evidence-only.
- **Exact tested P1 source:** `6eb62daec638185f5c5dc170182e9e0454b6e061`.
- Confirmatory GitHub Actions run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40483551395
- Confirmatory artifact: https://github.com/DavidOWilliams/Materials-design/actions/runs/40483551395/artifacts/12724002391
- Prespecified scientific protocol: `foundation/p1/CONFIRMATORY_PROTOCOL_FROZEN.md` and `CONFIRMATORY_CONFIG_FROZEN.json` (committed before confirmatory experiment).
- Permanent evidence: `foundation/p1/evidence/confirmed-source-6eb62da/`. Confirmatory original SHA256 manifest is preserved unchanged and expanded `sha256_manifest_plus_report.txt` covers added report and logs. Evidence-only commits are not retested source identities.
- Provisional protocol and pilot seed data are NOT confirmatory.

## Verification requested
1. Independently establish that protocol SHA256 `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0` is the pre-outcome frozen version, with seeds 2001–2020, 20 paired trials for each (sampling/explore) × (0.25/0.50) combination.
2. Checkout the exact P1 tested SHA and execute focused test suite, all foundation and recovered_wp0 tests, comparing with CI's **9 focused and 348 regression passing**. Confirm test coverage for blind continuation beyond the first candidate, paired budgets, actual feedback revision, replay, held-out scoring, and statistics.
3. Recompute SHA256 hashes for all original confirmatory files and separately inspect 80 paired-trial rows and 160 full arm records, especially failures and omitted candidates.
4. Verify arm parity and leakage isolation. Both arms use a shared seeded WP3 proposal sequence, equal WP4 transforms and WP2 evaluations; only intervention uses the preceding achieved mass violation to revise its own future candidate. Verify blind arm never sees manufacturing feedback when generating candidates.
5. Independently recompute each selected arm from WP3 proposal generation through WP4 estimated inputs and WP2 evaluation, checking typed identities and expected objectives. A common synthetic scorer is **not an independent empirical process model**.
6. Reimplement 3D feasible hypervolume independently with fixed reference (120000 W/m², 45 kg/m², 1e9 Pa). Verify paired mean +0.014069733796296294 and percentile-bootstrap interval [0.0037037037037037043,0.025925925925925925], checking stratified paired resampling and no post-selection.
7. Independently audit 80-ms CPU cutoff (measured process CPU ns): paired mean -0.0017288773148148146 and interval [-0.005186631944444444,0.0]. Distinguish proposal generation, numerical, transformation and feedback overhead; prohibit counting final rescoring in search budgets.
8. Verify no effect on paired feasibility-rate difference (observed zero), and evaluate whether 0.02 is an appropriate practical significance threshold.
9. Inspect negative controls and scenarios: structured exploration shows zero HV difference; test no feasible at deliberately impossible mass cap; challenge cache poisoning, incompatible config, truncated trial, missing objectives, interrupted evidence, invalid CPU timestamps and process-model leakage.
10. Scrutinise whether mesh=32 achieves a sufficiently qualified numerical comparison. Recheck the WP2 numerical quality eligibility semantics in the raw records; assess whether results have genuine three-objective Pareto information or degeneracy.
11. Evaluate the held-out feed-resolution swap as *assumption sensitivity only*. There is no measured process validation and no demonstration of external generalisation.
12. Verify reproducibility of analysis under fresh Python 3.12 environment. Identify any evidence gaps blocking Gate 2 or Gate 3 independently rather than silently accepting claims.

## Questions requiring explicit independent disposition
- Are numerical-evaluation and manufacturing-transformation parity independently reproducible for all 80 pairs?
- Are per-candidate and per-run CPU totals reliable and is the CPU comparison operationally meaningful?
- Does the feasible 3D hypervolume estimator and its reference meet scientific validity?
- Are the stated 95% bootstrap intervals reproducible and appropriately interpreted?
- Does the 80-pair data support an engineering-useful advantage, given the smaller-than-threshold mean and CPU-time reversal?
- Are additional identity-feedback, infeasibility, failure and interruption challenges required before Gate 2 closure?
- Is Gate 3 ACCEPT, ACCEPT WITH LIMITATIONS, or CHANGES REQUIRED? **Only the separate reviewer makes this decision.**

## Boundaries
WP4 accepted implementation remains unchanged. WP6 independent review PR #8 reports Gate 1 PASS, Gate 2 OPEN and withheld formal WP6 acceptance; P1 does not close those requirements. There is no physical ceramic validation, CFD/sintering/porosity modelling, or new independently calibrated manufacturing model.
