# WP4 acceptance ledger — ACCEPTED within bounded synthetic scope

## Authoritative acceptance decision — 25 October 2026

**Accepted implementation:** `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b`.

The separately tasked ChatGPT review session completed independent closure review and found no remaining blocker in the agreed bounded WP4 scope. The user authorised recording this decision in GitHub. **R1–R5, including the final R2 checkpoint-write recovery finding, are closed for this exact implementation.**

| Completion gate | Decision |
|---|---|
| Gate 1 — Functional execution, persistence and replay | Closed / accepted for the bounded scope |
| Gate 2 — Valid variations, invalid-input challenges and unknown-state preservation | Closed / accepted for the bounded scope |
| Gate 3 — Separately tasked scientific, architecture and corrective review | Closed / accepted for the bounded scope |

This decision supersedes all earlier “awaiting independent closure”, “changes required” and pending gate statements preserved in the historical section below. Earlier test results remain historical; they are not relabelled as tests of the accepted revision.

## Final revision and verification evidence

- Accepted source: [beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b](https://github.com/DavidOWilliams/Materials-design/commit/beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b).
- Actual WP4 CI checkout: `57c7d6134a6e9f4a1d30077d5d8575dd1a4c899c`, a temporary PR merge commit. Reviewer independently confirmed identical tree hash for source and checkout: `a067510fe9ace3ef791cf6f7871302c654cc0349`.
- [WP4 qualification 40231063605](https://github.com/DavidOWilliams/Materials-design/actions/runs/40231063605): 85 focused WP4 tests and 291 foundation/recovery tests passed.
- [WP3 integration 40231063596](https://github.com/DavidOWilliams/Materials-design/actions/runs/40231063596): all four jobs passed; CI logs confirm 1,148 legacy tests passed with 10 warnings. Legacy tests were checked from CI, not independently rerun locally.
- Independent reviewer local execution on the accepted source: **291 passed in 60.38 seconds**, using the existing review environment.
- Supporting submission archive: `wp4-qualification-dossiers`, artifact ID `12612821575`, reported SHA-256 `36eb05e5e69bc0af8a86c08fbada5b97fa6c9a5f6b8b64b3478020df588b831d`. Archive references identify the implementation evidence; the reviewer additionally executed source-level probes and inspected CI logs, without claiming inspection of every archive byte.

## Independent closure findings

The reviewer reran the original invalid-record probes: false feedback-disabled histories, mismatched process resolution, incorrect baseline evaluation identity, unsupported schema and false no-improvement termination were rejected by reopening and numerical replay.

Independent instrumented failed-write recovery checks produced:

| Scenario | Calls before interruption | Additional continuation calls | Actual / recorded total | Durable candidates reused |
|---|---:|---:|---:|---:|
| Default: first checkpoint write fails | 2 | 3 | 5 / 5 | 0 |
| Default: final feasible checkpoint write fails | 4 | 1 | 5 / 5 | 2 |
| Alternate: later checkpoint write fails | 3 | 1 | 4 / 4 | 1 |

Each recovered dossier reopened and numerically replayed successfully. Repeating resume caused zero additional numerical evaluations. Necessary reevaluation after a failed write is counted as work, not mislabelled as reuse.

The earlier successful-checkpoint cases remained correct: default 4 actual/recorded evaluations and alternate 3; final feasible checkpoint recovery required zero new evaluations. Negative reuse and changed event candidate identity remained rejected. Optional verification returned and persisted identical records, and the returned record could be saved and reopened.

The prior independent analytical checks of commands, signed constituent balances, conduction and free-plate stress remain applicable: the numerical kernel and relevant transformation calculations were unchanged by the closure corrections. Estimated areal mass is 37.5, 32.5 and 27.5 kg/m² across the primary feedback sequence, satisfying the 31 kg/m² cap at the last candidate. Heat transmission improves while tensile thermal mismatch stress rises slightly; no across-objective improvement is claimed.

## Acceptance boundaries and handover

Acceptance is for the agreed **bounded synthetic software/numerical demonstration**. Intended design, estimated achieved state and measured evidence remain distinct. There is no experimental ceramic manufacturing validation, new physical model, V1 completion or full D1 release claim.

Retained limits include synthetic properties and ideal-deposition assumptions; bounded routes and revision policy; conditional scenario feasibility; single-writer recovery; no mid-solver restart; and no externally authenticated audit evidence. Independent review was AI-assisted and separately tasked, not human expert certification or an exhaustive correctness proof.

The accepted commit may be used as the WP5 briefing baseline with these limits carried forward. This acceptance-record change is **documentation only**: it does not change the accepted implementation SHA, and earlier test results are not presented as execution of the later documentation commit. PR #4 remains draft and unmerged; this action neither merges it nor starts WP5.

## Historical implementation ledger and correction history — superseded status

The text below is retained unchanged as historical evidence. Its provisional gate statuses and pending-review statements are superseded by the authoritative decision above.

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
