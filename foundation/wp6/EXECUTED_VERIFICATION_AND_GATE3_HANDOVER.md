# WP6 executed verification and Gate 3 handover (2026-10-26)

## Immutable tested source and evidence
- Tested implementation SHA: `1e9a3ea4f9beb202b46fa85abd8b7d9930277381`.
- GitHub Actions run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40336776440
- Artifact ID: `12658165098`; artifact ZIP SHA-256: `172fa6825e403944d4e966da0c9ace870513f63fa5e2df7332e5f74219994319` (GitHub metadata).
- Archive contains source-sha.txt, python.txt, dependencies.txt, pip-check.txt, WP6 and regression logs, nine immutable case dossiers, report.json, SHA256SUMS.
- Independent download and manifest inspection: all 17 SHA256SUMS entries match archived file bytes; source-sha.txt records the tested SHA.
- Focused tests: **10 passed**; foundation/recovery regression: **345 passed**.
- All nine full-resolution campaigns completed; all nine numerical replays reported **passed**.
- This documentation commit is distinct from the tested source; it does not change the tested implementation.

## Results (synthetic D1; 4096 elements; nominal budget 4)
| Case | Stop reason | Evaluations | Candidate proposals | Refinement solves | Feasible candidates |
|---|---|---:|---:|---:|---:|
| control_on | qualified_scenario_feasible | 4 | 3 | 8 | 1 |
| control_off | feedback_disabled | 2 | 1 | 4 | 0 |
| tight_mass_on | qualified_scenario_feasible | 4 | 3 | 8 | 1 |
| tight_mass_off | feedback_disabled | 2 | 1 | 4 | 0 |
| layer_sensitivity | qualified_scenario_feasible | 3 | 2 | 6 | 1 |
| feed_sensitivity | qualified_scenario_feasible | 3 | 2 | 6 | 1 |
| heldout_on | qualified_scenario_feasible | 4 | 3 | 8 | 1 |
| heldout_off | feedback_disabled | 2 | 1 | 4 | 0 |
| no_feasible | evaluation_budget_exhausted | 5 | 4 | 10 | 0 |

Units: thermal transmission W/m²; areal mass kg/m²; tensile thermal mismatch Pa. The full candidate objective vectors, qualification and feedback records are in archived `campaigns/report.json` and dossiers. Each scenario's `measured_evidence` is null.

## Scientific and comparison limits
- On/off pairs share a nominal maximum of four candidate proposal slots, **not equal actual computational effort** (4 versus 2 evaluations; 8 versus 4 refinement solves). This is **not** a fair equal-effort causal comparison.
- The 'heldout' cases have a revised **duty description and brief hash**, but unchanged numerical model inputs and the same output as control. Thus they are **not a genuinely held-out scientific challenge**. A new supported scientific duty/geometry/constraint with separate preregistration and qualification is still required.
- No measured achieved-state evidence; no V1 validation. Estimated achieved state must not be described as measured.
- No dedicated executed no-improvement or unresolved-outcome challenge was verified by this run. Invalid budget rejection and no-files behavior were covered by focused tests; the no-feasible case completed with zero feasible candidates.
- The run does not demonstrate equal-effort advantage, generalization to a held-out physics problem, or scientific validation.

## Gate dispositions
- Gate 1: **partial**. Harness execution, nine cases, dossier reopen/replay, negative budget validation and regression pass. Missing required genuine held-out challenge and explicit no-improvement/unresolved challenge.
- Gate 2: **open**. Evidence integrity and no-feasible challenge pass; fair effort comparison, genuinely held-out scientific case and other preregistered challenge boundaries incomplete.
- Gate 3: **not assessed**; independent reviewer must use tested SHA and raw artifact, not this later documentation commit.

## Reviewer instructions
Retrieve GitHub Actions artifact 12658165098 and independently check SHA256SUMS, source-sha.txt, case dossiers, report.json, focused/regression logs, replay status, early stops, measured_evidence=null, and original WP5 accepted tested SHA `4078a83dc11e14703ff6cc03f5b62f4e48879d14` versus acceptance/evidence SHA `5ade1e9650795427a8bb32de64dfce6c11cd0426`. Treat unknown as not pass. Do not merge or promote WP6 to V1.
