# P1 independent review correction report — IR-01 through IR-06

**Date:** 27 October 2026. **Implementation-team document; NOT an independent Gate 3 disposition.**
**Branch:** `p1-ir1-ir6-corrections-2026-10-27`; draft correction PR #11 targeting P1 draft PR #9, not merged.

## Historical evidence boundary

- Accepted WP5 tested implementation: `4078a83dc11e14703ff6cc03f5b62f4e48879d14`.
- Original P1 confirmatory tested implementation: `6eb62daec638185f5c5dc170182e9e0454b6e061`; original complete Actions run `40483551395`.
- Protocol `foundation/p1/CONFIRMATORY_CONFIG_FROZEN.json`, immutable SHA256 `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0`.
- Later recovery/checkpoint-corrected implementation: `03cf5718da6b88c05c75ce492ea963507899f66b`; Actions `40486605412`. This is a distinct previously tested source; its separate same-seed evidence is not independent new confirmatory data.
- Current IR-01–06 correction implementation **candidate**, awaiting exact-source complete rerun: `752752f880ed7c4b0c77d399ca7c99f9a9bb094e`. All subsequent report/documentation commits must be distinguished from this implementation identity.
- Both historical evidence repositories remain retained at `foundation/p1/evidence/confirmed-source-6eb62da/` and `confirmed-source-03cf571/`. The original 80-pair evidence and protocol have not been changed or reselected.
- PR #9 remains draft/unmerged. WP6 Gate 2 remains open and WP6 formal acceptance withheld.

## Finding disposition (implementation team; independent review must decide acceptance)

| Finding | Current disposition | Evidence and caveat |
|---|---|---|
| P1-IR-01 exact clean executable rerun | **PARTIALLY RESOLVED** | Clean original SHA `6eb62da...` rechecked: **13 focused and 348 foundation/recovery passing**, CI run `40539051957` job `ir-original-clean-checkout`. Fresh corrected-code final result must also pass. This rerun is performed by the implementation team, not the independent reviewer. |
| P1-IR-02 adversarial runtime challenges | **PARTIALLY RESOLVED** | Twelve challenge categories implemented at `foundation/tests/test_p1_ir_challenges.py`: no feasible, WP4 failure, WP2 failure, invalid objectives, truncated record, config mismatch, cache poisoning, checkpoint resume, CPU/timestamp tamper, blind leakage, no-revision negative control and stop reason. Earlier 32 focused tests and 367 foundation/recovery tests passed before last timestamp/benchmark corrections. Final exact SHA suite must be audited before classifying RESOLVED. No general identity manufacturing transform is claimed. |
| P1-IR-03 hypervolume objective degeneracy | **RESOLVED — INTERPRETATION ONLY** | `P1_IR03_NUMERICAL_INTERPRETATION.md` and `test_p1_ir_numerical.py` document synthetic tensile-stress range 5.759824041329242e−9 through 2.0328790734103208e−8 Pa (125 blind, 126 feedback feasible vectors), versus 1e9 Pa frozen reference. Nominal 3D HV effectively behaves as **2D thermal/mass**. No historical HV or CI is altered; physical scientific and stress validation remain outside P1. |
| P1-IR-04 held-out eligibility and revision state | **PARTIALLY RESOLVED** | Held-out eligibility now references actual held-out scored inputs, not the native inputs. In the current supported WP4 model the brief fields remain identical, so this is an integrity/semantic correction without demonstrated changed historical objective values. Revised records distinguish `revision_attempted` from `revision_applied` (actual architecture change); original `revision_applied` had represented an attempt. New supplementary tests must pass at final SHA. Original scores are retained. |
| P1-IR-05 CPU instrumentation | **OPEN / INCONCLUSIVE SCIENTIFIC EFFICIENCY** | Process CPU is distinct from wall time, file persistence and startup. Added per-candidate validation of nonnegative integral CPU counters, aggregate reconciliation, UTC diagnostics and exploratory repeated-run benchmark, including warm-up/60,80,100ms sensitivity. The 80ms CPU effect varied historically from −0.0017289 (original) to 0 (checkpoint-corrected same-seed run), thus **no robust CPU-efficiency advantage is established**. New benchmark previously failed due script import and shell-pipe masking; both corrected; final strict rerun pending. |
| P1-IR-06 evidence integrity | **RESOLVED — IMPLEMENTATION AUDIT** | CI `40539051957`, `ir-archive-integrity` job, independently re-read exact original Actions archive, checked original and expanded SHA256 manifests; **405 original files, 412 saved files, 0 missing, 0 modified, 7 supplementary report/log/figure/manifest files**. Original report/statistical data preserved. Reviewer must separately reproduce this audit. |

## Adversarial expected outcomes
The tests define expected outcomes through assertions and exercise the **actual** WP3/WP4/WP2-backed P1 comparator. Invalids are refused, failed proposals consume budget slots and are retained, checkpoint resumes reuse previously persisted candidate evidence, cached results are deliberately prohibited, blind proposal generation has no achieved feedback state, and budget exhaustion is classified explicitly. Supplementary no-violation control is **not** a physics-equivalent identity transformation.

## Confirmatory scientific interpretation (never revised retrospectively)
Frozen n=80 pairs, equal numerical-work 3D normalized HV feedback minus control mean **+0.0140697338**, 95% percentile bootstrap CI **[+0.00370370,+0.02592593]**. Only **6 positive**, **74 exactly zero**, **0 negative** matched numerical-work pair effects. The mean is below preregistered practical threshold 0.02 and the apparent third objective is degenerate. Trial-level feasibility difference is zero. The original 80ms CPU-prefix result was **−0.00172888** (CI −0.00518663 to 0); the distinct checkpoint corrected same-seed replication yielded zero. CPU-based benefit is not established. This is synthetic in-model software evidence, neither independently calibrated manufacturing prediction nor physical ceramic validation.

## Outstanding verification and acceptance
- Final exact IR correction implementation must pass all adversarial, focused and full regression checks in GitHub Actions with unmasked process failure codes, record exact head SHA and dependency freeze.
- Strict repeated-run CPU benchmark must generate retained JSON and log; assess clock variability and 80ms cutoff sensitivity without upgrading the historical CPU claim.
- SHA256 manifest for the correction evidence package and clean final reviewer handover must be generated separately from the frozen original evidence.
- Separately tasked reviewer must reproduce selected corrections, validate scientific interpretation and decide Gate 1/2/3. **Gate 3 NOT self-approved.**

## Independent reviewer reproduction
Start with original-source CI run `40483551395`, exact correction-branch run(s) referenced above, both retained SHA256 manifests, new `foundation/tests/test_p1_ir_challenges.py`, `test_p1_ir_numerical.py`, changed `material_core/p1_comparator.py`, CPU benchmark JSON, and this report. Challenge negative controls, recovery, numerical qualification, metrology, and holdout process assumptions without treating any supplementary tests as replacement confirmatory trials.
