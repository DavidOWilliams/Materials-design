# WP4 independent corrective acceptance matrix — awaiting reviewer closure

**Authority:** WP4 Implementation Brief v1.0; independent Gate 3 review **performed, changes required**, not approved. No WP5, no merge. Source revision for this table is the branch revision at the final WP4 Actions run; the workflow artifact `wp4-tested-sha.txt` is the authoritative actual checkout, not an assumed PR merge SHA. Earlier 46/252 and 257-test reports refer to earlier revisions and do not qualify this revision.

**Observed status:** WP4 qualification run [40218211505](https://github.com/DavidOWilliams/Materials-design/actions/runs/40218211505) passed **65 focused and 271 full foundation/recovery tests**, including the reviewer reproductions, and archived its raw dossiers. The actual checkout was PR merge SHA `45f0ef72aebe15a0067f2697b0c4d94aad277d61`, based on source head `3f9f9d6e794d00164c3a2ac21b1561ad13c1acbf`. GitHub compare of source head against merge checkout reports **zero changed files**, establishing source-tree equivalence. WP3 integration run [40218211523](https://github.com/DavidOWilliams/Materials-design/actions/runs/40218211523) passed all four jobs. The independent Gate 3 reviewer has not closed findings.

| ID | Requirement | Precise expected result | Executable verification | Supporting artifact / log | Observed result / remaining limitation |
|---|---|---|---|---|---|
| F01 | WP2/WP3 baseline unchanged | Foundation and recovery suite passes | `Full foundation/recovery pytest` | `CI job log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Pending final checkout |
| F02 | Homogeneous, layered and gradient transform bounded | Analytical references and interfaces match | `test_wp4_analytical_reference.py; test_wp4_resolution.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Synthetic only |
| F03 | Signed volume balances conserved | Expected and actual constituent totals agree | `test_wp4_balances.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Unit-area ideal deposition |
| F04 | Achieved-state evaluation changes with process resolution | WP2 evaluates estimated geometry and retains identity | `test_wp4_bridge.py; test_wp4_mesh_separation.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No measured physics |
| F05 | Binding violation causes intended redesign | 4096-element case reaches conditional feasibility after two revisions | `test_wp4_qualified_feedback.py; higher-resolution CI step` | `wp4-higher-resolution.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Stress trade-off remains |
| F06 | Impossible budget never falsely succeeds | Exhaustion recorded and no feasible result invented | `test_wp4_feedback.py; wp4-impossible CLI` | `wp4-impossible.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No physical feasibility |
| F07 | Feedback on/off comparable | Same declared budget; unused evaluations explicit | `test_wp4_comparisons.py; paired()` | `wp4-paired.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Not equal consumed work |
| F08 | Sensitivity preregistered | Five-point fixed grid recorded without selection bias | `test_wp4_comparisons.py; sensitivity()` | `wp4-sensitivity.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Bounded grid |
| F09 | Dossiers portable and numerically replayable | Separate-process reopen/recompute passes | `test_wp4_feedback.py; WP4 CI replay` | `wp4-dossier.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No external signature |
| F10 | Cancellation and interruption preserve work | Verified checkpoint reuse, durable event accounting and resumable dossier | `test_wp4_resume.py; test_wp4_review_reproductions_v2.py` | `wp4-review/*` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Mid-solver recovery unsupported |
| F11 | Alternate duty and second transform | Alternate runs, resumes and replays unchanged duty; uniform route evaluated | `test_wp4_uniform.py; test_wp4_review_reproductions_v2.py` | `wp4-review/alternate-*` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Two synthetic routes |
| F12 | Estimated is not measured | Export excludes measurements and rejects forged evidence | `test_wp4_export.py; test_wp4_review_reproductions_v2.py` | `wp4-export.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No experimental validation |
| C01 | Invalid resolution rejected | Nondivisible thickness and invalid steps fail closed | `test_wp4_resolution.py; test_wp4_boundaries.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Extreme grids limited |
| C02 | Quantization deterministic | Ties and endpoints preserve fractions | `test_wp4_analytical_reference.py; test_wp4_boundaries.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Two constituents |
| C03 | Material balance invariant | Signed volume and density checks consistent | `test_wp4_balances.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No shrinkage |
| C04 | Unsupported properties/geometry rejected | Missing inputs fail qualification | `test_wp4_bridge.py; inherited WP2 tests` | `Foundation log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Synthetic property pack |
| C05 | Invented measured record rejected | Resealed measurement forgery rejected | `test_wp4_export.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; External forgery beyond checksum |
| C06 | Versioned process and evaluator identity | Unknown route/evaluator/revision rejected | `test_wp4_registry.py; review reproductions` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No independent evaluator registry |
| C07 | Numerical eligibility respected | Unqualified output cannot claim feasible | `test_wp4_feedback.py; test_wp4_qualified_feedback.py` | `wp4-higher-resolution.json` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Mesh-specific |
| C08 | Adversarial campaign mutations fail | False stop/schema/baseline/counters rejected | `test_wp4_review_reproductions_v2.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Checksum not authentication |
| C09 | Interrupted recovery truthful | Completed evaluations reused; missing history rejected | `test_wp4_resume.py; wp4_review_evidence.py` | `wp4-review/*` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No mid-kernel restart |
| C10 | Registry and alternate lifecycle | Unknown transforms fail; alternate context preserved on resume | `test_wp4_registry.py; review reproductions` | `wp4-review/alternate-*` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Bounded routes |
| C11 | Revision deterministic | Lineage, feedback causality and stopping validated | `test_wp4_integrity.py; review reproductions` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; Not general Pareto |
| C12 | Cancellation and budgets fail closed | Impossible/zero budget, interrupted checkpoint and corrupt tail tested | `test_wp4_cancellation.py; test_wp4_boundaries.py; test_wp4_journal.py` | `WP4 focused log` | **PASS, run 40218211505, source `3f9f9d6`, checkout `45f0ef7`**; No physical validation |

## Corrective reviewer reproductions

R1: unsupported schema 999, forged no-improvement, wrong baseline input hash, false feedback-disabled multi-candidate history, and process/mesh mismatch must all be rejected by `reopen` before numerical replay. R2: interruption reuses completed baseline and candidates; numerical evaluator-call audit is independently counted in `foundation/wp4_review_evidence.py`. Missing legacy manifests/events are rejected, transform failures are not counted as numerical evaluations, and forged cumulative counters fail. R3: baseline export uses `IntendedDesign.content_hash`; a design-content change with the same ID changes the digest. R4: alternate-duty manifest preserves full WP3 typed baseline, duty and process across continuation and replay. R5: reconcile this matrix with the final CI logs, architecture, usage, completion and challenge reports.

**Gate 1:** implementation evidence under final verification. **Gate 2:** corrective challenges under final verification. **Gate 3:** independently reviewed, changes required, awaiting independent closure. No physical ceramic validation claimed.

## Frozen verified evidence for the correction

- Source commit tested: `3f9f9d6e794d00164c3a2ac21b1561ad13c1acbf`; actual WP4 Actions checkout: `45f0ef72aebe15a0067f2697b0c4d94aad277d61` (temporary PR merge; source-tree comparison changed files = 0).
- WP4 run: `40218211505`; **65/65 focused**, **271/271 full**; campaign qualified at 4096 elements and reopens/recomputes 3 candidates.
- WP3 integration: `40218211523`; four jobs passed.
- Evidence archive: `wp4-qualification-dossiers`, artifact ID `12607459818`, SHA-256 `ac268269364c15fe37add272b113f595d655b641b69a145f020826d916d8aa42`, includes manifests, event journals, resumed dossiers, call audit, tested checkout SHA and process sensitivity results.
- Default interrupted/resumed campaign independently instrumented: 2 original evaluator calls (intended+estimated), 2 new estimated calls, **4 actual = 4 recorded**, 1 completed candidate reused. Alternate: 2 original calls + 1 new = **3 actual = 3 recorded**, 1 reused; duty remained **380/320 K**.
- **No numerical replay during continuation**. Separate numerical dossier verification recomputed 3 default and 2 alternate candidates; these are verification work, not charged as continuation work.
- Scientific trade-off: mass and thermal transmission improve, thermal stress rises slightly; no blanket multi-objective improvement claim.

**Revision caveat:** The evidence above is for source head `3f9f9d6`. This ledger update is documentation-only; its own final source SHA must be verified by a subsequent workflow before independent submission.


## Final independent-review follow-up: terminal recovery, event evidence, verification

Three post-`54c8674` independent defects are addressed by `test_wp4_final_review_defects.py` and `wp4_review_evidence.py`:

- **Terminal checkpoint:** a durably persisted feasible final candidate is reopened with its actual `qualified_scenario_feasible` stop, without numerical reevaluation. Budget exhaustion, feedback-disabled, intermediate and alternate-duty checkpoints are covered.
- **Embedded event history:** hash-chain sequence, previous-hash linkage, supported event kinds, candidate identity, stage order and a durable continuation marker bind reused-candidate accounting to completed work. Negative reuse and changed candidate ID with unchanged event hash fail closed.
- **Optional verification:** a separate recomputation completes before a new immutable final dossier is saved. The returned and saved records agree on verified solver-call counts. Verification failure leaves no successful final dossier; prior journal/manifest remain intact.

The earlier 65/271 passing results are **historical** evidence for `54c8674`. This follow-up requires its own passing workflow, actual checkout SHA and archive before independent closure. Gate 3 has been performed and returned changes required; it is not independently closed.


## R2 checkpoint-write independent closure follow-up

The independent reviewer reproduced on `ed84a8f0f45758b9a291604c006c706719a268df`: numerical candidate evaluation completed but the checkpoint callback failed before writing; resume produced a dossier that failed reopening with `Reused candidate count unsupported by completed work`. This is historical failing evidence, not a new physics failure.

The corrective boundary distinguishes (1) evaluation starts, (2) completed evaluation attempts, (3) durable candidate checkpoints, and (4) checkpoints reused on continuation. A failed checkpoint after completed numerical work is recorded as a completed attempt and failed checkpoint; reevaluation produces a separate candidate proposal, transform and numerical attempt. `completed_evaluations` counts **all** completed attempts including repeats, while `reused_candidates` is bounded by actual persisted prefix and the durable continuation marker. The event validator permits a legitimate retry after `checkpoint_failed` but still rejects fabricated, altered or incorrectly ordered events. `resume` validates complete embedded recovery evidence and reopens the final saved dossier before reporting success.

Executable challenges: `foundation/tests/test_wp4_checkpoint_write_recovery.py` (failure before first/second/third checkpoint, final feasible, alternate duty and repeated resume); `foundation/wp4_review_evidence.py` (independent evaluator-call audit and raw journals/dossiers under `wp4-review/*write-failure*`). Previous R1/R2/R3/R4 and numerical regression tests remain in the focused and full suites. **Final CI source SHA, actual checkout SHA, test totals and archive must be taken from the final run, not inferred from this text.** Gate 3 has been performed; independent closure remains outstanding.
