# P1 independent Gate 3 — full CI archive audit, 27 October 2026

**Disposition: CHANGES REQUIRED; formal Gate 3 NOT CLOSED.** This is a documentation-only independent review of tested P1 source `6eb62daec638185f5c5dc170182e9e0454b6e061`, accepted WP5 base `4078a83dc11e14703ff6cc03f5b62f4e48879d14`. It supersedes the prior summary-only review where more extensive verification is described.

## Provenance and verified evidence
- Frozen config committed at `4a4035459155d8f4af057477b667e6f168b26eb9`, six commits before tested source. Independently computed SHA256 of its exact retrieved bytes: `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0`.
- Original CI run https://github.com/DavidOWilliams/Materials-design/actions/runs/40483551395, job 122119578414. Retrieved job log shows 9 focused and 348 regression tests passed on the tested source. **CI execution is not an independent fresh test run.**
- Downloaded original CI artifact 12724002391 and independently SHA256-checked **404/404** original confirmatory manifest files and **35/35** pilot manifest files; zero mismatches. The later repository evidence copy has not been independently compared byte-for-byte.
- An independently authored Python standard-library auditor (no imports from P1 scorer) processed **80 paired trials, 160 complete arms, 640 candidates**, 160 native scoring records and 160 held-out scoring records. Zero inconsistencies in trial uniqueness, configuration digests, raw objective/score identities, feasibility, saved proposal equality, 4 transforms/4 evaluations per arm, no cache hits/failures, per-candidate CPU accounting, 80 native HV pairs, 80 CPU-prefix comparisons, held-out HV and all performance curves.
- Independent hypervolume uses inclusion-exclusion of 3D dominated cuboids, not the implementation's sweep algorithm.

## Reproduced findings
| Measure | Independent result |
|---|---:|
| Mean paired normalized feasible HV | +0.014069733796296297 |
| 95% CI, stratified 2,000-resample bootstrap seed 8846 | [+0.0037037037037037047, +0.02592592592592593] |
| Positive / unchanged / negative pairs | 6 / 74 / 0 |
| Sampling/feed 0.25 | +0.01727430556 |
| Sampling/feed 0.50 | +0.03900462963 |
| Both structured-exploration strata | 0 |
| Trial-level feasibility difference | 0 |
| Feasible candidate records, blind / feedback | 125 / 126 |
| Feedback revision flags / blind revision flags | 45 / 0 |
| 80ms CPU-prefix mean HV delta | -0.0017288773148148146 |
| CPU-prefix bootstrap CI | [-0.005186631944444444, 0] |
| Archived total process CPU, blind / feedback | 8.755535942 s / 8.930690905 s |

The CPU-prefix difference comes from **one nonzero pair** and is not a reliable basis for a general CPU efficiency claim. Timing is archived, not freshly benchmarked.

**Material scientific limitation:** All **251 feasible candidate records** have tensile thermal mismatch between ~5.76e-9 and ~2.03e-8 Pa, normalized against a 1e9 Pa HV reference. The third normalized objective is effectively zero, making the claimed 3D HV **effectively a 2D thermal-transmission/mass measure** over feasible candidates. This is an interpretation issue, not an arithmetic or manifest-integrity defect.

## Source-level fairness and caveats
The exact tested comparator constructs a separate identically seeded WP3 provider for each arm; blind and feedback use identical stored proposals and four charged WP4 transformations/WP2 evaluations. Feedback alone applies a previous-own-arm achieved mass-violation revision. No blind-arm achieved-state selection is visible in the inspected source. `compare` trusts reported counters; independent archive audit reconciled those counters. Both arms are scored with the **same synthetic WP4/WP2 model**, not independent measured process data. Sampling and exploration are proposal policies, not two distinct full inverse optimizers.

Potential future fixes: held-out `score_saved` eligibility uses the native `achieved.brief` with the held-out result; assess if the brief changes. `revision_applied` indicates a triggered attempt, not necessarily a changed architecture. `score_saved` does not support successful scoring of failure rows. Mesh=32 is exploratory qualification only.

## Claims and gates
- A archived reproducibility **SUPPORTED**; fresh implementation execution **INCONCLUSIVE**.
- B equal recorded numerical work **SUPPORTED**; not equal CPU time.
- C narrowly specified synthetic in-model HV benefit **SUPPORTED** for the frozen data, subject to limited source-level fairness and absence of independent physical model.
- D practical benefit **NOT DEMONSTRATED**: pooled mean below prespecified 0.02; CI crosses 0.02.
- E equal-CPU benefit **UNSUPPORTED**; observed mean negative, noisy.
- F general inverse-optimisation benefit **UNSUPPORTED**.
- G real ceramic manufacturing benefit **UNSUPPORTED**.

**Gate 1 CONDITIONAL PASS:** frozen config identity, full original archive integrity, CI log, and independent numerical/statistical reconstruction verified; no independent checkout/tests.

**Gate 2 FAIL TO CLOSE:** runtime adversarial challenges not independently executed; 3D objective degeneracy requires scientific qualification.

**Gate 3 FAIL TO CLOSE / CHANGES REQUIRED:** original CI archive and analysis fully audited, but no independent execution of exact tested source, adversarial runtime tests or later repository-byte integrity comparison.

## Findings and smallest closure actions
1. **IR-01 HIGH:** Independently execute focused/regression suite at tested SHA and retain commands, environment and logs. No new confirmatory trial needed solely for this.
2. **IR-02 HIGH:** Independently execute no-feasible, missing objective, failure, interrupted run, corrupted evidence, cache poisoning, invalid CPU, config mismatch, blind leakage and identity-feedback challenges. Keep outside original sample; correct code only if defects confirmed.
3. **IR-03 HIGH scientific:** Explicitly qualify the 3D HV as effectively 2D; avoid overstating third-objective discrimination or physical inference. No retrospective reference change.
4. **IR-04 MEDIUM:** Check held-out eligibility brief and revision flag semantics; fix prospectively if necessary.
5. **IR-05 MEDIUM:** Controlled CPU repeatability audit; no present efficiency claim.
6. **IR-06 MEDIUM:** Verify later repository evidence and expanded manifest byte-for-byte against the original CI artifact.

**Recommendation:** Withhold formal acceptance. Preserve the existing 80-pair result unchanged; do not rerun simply to seek a stronger effect. This independent review does not change the tested implementation, baseline, or evidence and must not be merged without authorization.
