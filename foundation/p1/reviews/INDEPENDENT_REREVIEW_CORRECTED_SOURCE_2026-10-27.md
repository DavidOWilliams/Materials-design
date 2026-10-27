# P1 independent re-review of corrected source — 27 October 2026

**Independent disposition: CONDITIONAL / NOT YET FORMALLY ACCEPTED.** Reviewed checkpoint-corrected tested SHA `03cf5718da6b88c05c75ce492ea963507899f66b`; original tested SHA `6eb62daec638185f5c5dc170182e9e0454b6e061` remains separate. No original evidence or implementation modified.

## Independently executed checks
Downloaded the exact GitHub Actions run `40486605412` artifact `12725751556`. Independently SHA256 verified **564/564** original confirmatory manifest entries and **67/67** pilot manifest entries, zero mismatches. Read all **80 pairs, 160 arm records, 640 candidate records and 160 checkpoint records**. Independently calculated normalized feasible 3D hypervolume by inclusion/exclusion of dominated cuboids, rather than importing P1 analysis. Recomputed every 80 paired HV difference, scenario mean, and a 2000-repetition, seed-8846 stratified paired bootstrap. All 160 arm counters, four proposal/transform/evaluation slots, component CPU sums, checkpoint payload digests, and checkpoint row identities reconciled: **zero discrepancies**.

## Results
- Mean equal-work HV difference +0.014069733796296297; bootstrap 95% percentile CI [+0.0037037037037037047,+0.025925925925925932].
- Positive/zero/negative pairs 6/74/0; sampling feed 0.25 +0.01727430556, sampling feed 0.5 +0.03900462963, both explore strata 0.
- CPU 80ms prefix mean 0.0 for corrected source; original source's -0.0017288773 result is not transferable. The same seeds and frozen protocol were reused; these are NOT 160 independent pairs.
- Qualified candidate records: blind 125, feedback 126. Revision flags: blind 0, feedback 45. No archived failed evaluations, failed transforms or cache hits.
- Frozen practical threshold 0.02 is above observed pooled mean; confidence interval crosses it.
- Feasible tensile thermal-mismatch values remain negligible relative to 1e9 Pa HV reference; nominal 3D HV effectively measures transmission and mass.

## CI evidence and source
GitHub Actions job `122129838493` at run `40486605412` logs **11 focused tests and 350 regression tests passed**, including interruption/resume without repeating and corrupt/incompatible checkpoint rejection. These are verified *CI logs*, **not independently executed implementation tests**. Independently inspected corrected source's `_save_checkpoint`, `_load_checkpoint`, `execute`, `score_saved`, `compare` and existing challenge workflow. Source stores a durable checkpoint after each completed candidate; recovery checks config digest, proposal stream and row CPU totals. No physical measurements or external process model.

## Scientific and robustness findings
1. **R1 HIGH (open):** Fresh independent source checkout and execution of corrected-source focused tests, numerical failures, no-feasible scenario, invalid objective, cache, replay, mid-trial interruption, corrupted checkpoint and blind leakage still required. The existing challenge workflow is pinned to **original** SHA `6eb62da...`, not corrected SHA; it cannot prove corrected-source challenge closure. Existing CI has some, but not all, challenge coverage.
2. **R2 HIGH (scientific qualification):** Thermal-mismatch objective is effectively degenerate in feasible points. Report the synthetic result as nominal 3D HV with effectively 2D discrimination; do not assert general three-objective optimisation.
3. **R3 MEDIUM:** CPU-prefix difference changes from negative to zero between software versions with the same seeds. No robust equal-CPU efficiency claim; benchmark stability remains unverified.
4. **R4 MEDIUM:** Corrected-source `score_saved` uses native achieved.brief for held-out evaluation qualification; assess possible context discrepancy. Held-out feed is in-model assumption sensitivity, not independent validation.
5. **R5 MEDIUM:** Full byte comparison of later Git repository preserved copy with downloaded CI artifact not independently performed; original artifact manifest is independently verified.
6. **R6 SCIENTIFIC LIMITATION:** Both arms achieve at least one feasible design in every pair; no feasibility-rate improvement can be established under these constraints. No real ceramic performance claim.

## Claims
A archived reproducibility **SUPPORTED**, fresh independent execution **INCONCLUSIVE**.
B equal recorded numerical work **SUPPORTED**.
C narrow in-model feedback HV benefit under equal work **SUPPORTED** for the frozen 80 pairs, with method-specific and synthetic limits.
D practical benefit **INCONCLUSIVE / not demonstrated** relative to 0.02.
E equal CPU efficiency improvement **UNSUPPORTED**.
F general inverse-design feedback superiority **UNSUPPORTED**.
G manufactured ceramic improvement **UNSUPPORTED**.

## Gates
- **Gate 1 CONDITIONAL PASS:** CI recovery tests and independently audited checkpoint archive, but no independent runtime challenge execution.
- **Gate 2 OPEN / FAIL TO CLOSE:** broader adversarial challenge and third-objective scientific limitation.
- **Gate 3 OPEN / FAIL TO CLOSE:** no independent implementation execution at corrected SHA; evidence arithmetic and original CI artifact integrity pass.

**Acceptance recommendation:** withhold formal Gate 3 sign-off pending bounded independent runtime challenges and corrected scientific wording. No need to rerun the 80-pair study to seek a favourable result. Preserve tested SHAs, raw evidence, and frozen protocol unchanged. This review is documentation only and should not be merged without explicit authorization.
