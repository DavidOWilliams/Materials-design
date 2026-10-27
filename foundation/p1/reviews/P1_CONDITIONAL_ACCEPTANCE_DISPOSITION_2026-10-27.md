# P1 — Independent Gate 3 conditional disposition (recorded 27 October 2026)

**Status: CONDITIONALLY ACCEPTED FOR BOUNDED SYNTHETIC RESEARCH PROGRESSION; FORMAL GATE 3 SIGN-OFF REMAINS OPEN.**

This is an **independent-review recommendation and programme-ledger proposal**, not a claim of an unqualified Gate 3 PASS, a merger, or retrospective change to frozen experimental evidence. It is recorded on the independent documentation-only review branch, separately from the P1 implementation branch.

## Source identities and supporting evidence

- Accepted WP5 starting source: `4078a83dc11e14703ff6cc03f5b62f4e48879d14`.
- Original P1 tested source: `6eb62daec638185f5c5dc170182e9e0454b6e061`.
- Checkpoint-corrected tested source: `03cf5718da6b88c05c75ce492ea963507899f66b`.
- Latest P1 IR correction tested/workflow source: `752752f880ed7c4b0c77d399ca7c99f9a9bb094e`.
- Frozen protocol SHA256: `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0`.
- Original confirmatory CI: https://github.com/DavidOWilliams/Materials-design/actions/runs/40483551395
- Checkpoint-corrected confirmatory CI: https://github.com/DavidOWilliams/Materials-design/actions/runs/40486605412
- IR correction CI: https://github.com/DavidOWilliams/Materials-design/actions/runs/40539883955
- Implementation PR: https://github.com/DavidOWilliams/Materials-design/pull/9
- Independent review PR: https://github.com/DavidOWilliams/Materials-design/pull/10
- User-supplied evidence archive: `P1_IR_Correction_Evidence_27Oct2026(1).zip`; companion independent-review report: `P1_IR_Correction_Independent_Review_2026-10-27.docx`.

## Gate decisions

| Gate | Disposition | Basis / restriction |
|---|---|---|
| Gate 1 — Infrastructure and reproducibility | **CONDITIONAL PASS** | CI evidence at corrected source; 35 focused and 370 regression tests passed; 13 original-source focused and 348 regression tests passed; recovery and checkpoint tests included. |
| Gate 2 — Scientific fairness and challenge testing | **CONDITIONAL PASS** | Correction evidence covers no-feasible, numerical failures, invalid objectives, cache, corruption, restart and feedback isolation; study remains a bounded synthetic model with scientific qualifications. |
| Gate 3 — Independent scientific acceptance | **CONDITIONAL / FORMALLY OPEN** | Independent evidence audit and scientific review support bounded progression, but separate fresh independent implementation execution has not been completed. |

The IR correction CI job `122315095711` checked out exact SHA `752752f...` and reported 35 focused and 370 regression tests passing. The user-supplied ZIP top-level SHA256 manifest had 4/4 matches; evidence comparison reported 405 files unchanged. These are **verified retained CI records**, not an independent fresh runtime execution.

## Scientific interpretation to carry forward

1. At matched numerical work, 80 paired trials yield mean normalized feasible HV gain **+0.014069733796296294**, bootstrap 95% CI **[+0.0037037037037037043, +0.025925925925925925]**. Only **6/80** pairs improved; **74/80** unchanged; **0/80** worsened. All observed gains were in sampling; structured exploration had no gain.
2. Mean gain **0.01407 is below the preregistered practical threshold 0.02**; practical engineering importance is **not demonstrated**.
3. The corrected-source 80ms CPU-prefix effect is **0**, not evidence of CPU efficiency superiority. The original-source CPU result was negative; implementation/runtime sensitivity precludes an efficiency claim.
4. All trials achieved a feasible candidate in each arm, so feasibility-rate improvement is not established.
5. Feasible thermal-mismatch objective is nearly degenerate relative to its 1e9 Pa reference; nominal 3D HV has effectively 2D discrimination (thermal transmission and areal mass).
6. Held-out feed-resolution checks remain within the same synthetic process-model family; no independent process-model validation, measured ceramic performance, or general feedback superiority has been demonstrated.
7. The original and corrected studies reuse seeds and must not be pooled as independent trials.

## Conditions, retained findings and permitted progression

- **Allowed:** progress to the next research work package, with P1 explicitly labelled a **conditionally accepted synthetic research prototype**; preserve frozen protocol, original and corrected raw evidence, exact tested source identities and independent review evidence.
- **Not allowed:** claim formal unqualified Gate 3 PASS, general manufacturing-feedback superiority, practical significance, CPU efficiency advantage, real manufactured ceramic improvement, or independent physical validation.
- **Outstanding before unqualified closure:** independently execute the corrected implementation/challenge suite at the exact tested source; retain environment, commands and logs; reconcile any remaining source/evidence provenance differences. Scientific model limitations should be carried into future external benchmarking and physical validation, not concealed or 'corrected' by rerunning the frozen study.
- **Governance:** no implementation changes, evidence rewriting, baseline movement or PR merging are authorised by this record. This is a proposed ledger update on the separate review branch; it becomes the authoritative programme ledger only if reviewed and incorporated through the repository's normal approval process.

**Decision:** Record P1 as **CONDITIONALLY ACCEPTED FOR BOUNDED SYNTHETIC RESEARCH PROGRESSION — FORMAL GATE 3 OPEN**.
