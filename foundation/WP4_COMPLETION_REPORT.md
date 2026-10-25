# WP4 corrective implementation completion and evidence status

## Scope
The WP4 branch retains the accepted WP2/WP3 baseline and bounded synthetic manufacturing-feedback demonstration. R1 adds strict campaign schema, identity, baseline and causal-stop validation. R2 freezes original configuration and typed baseline before work, separates transform/evaluation events, reuses durably completed numerical evaluations, validates cumulative accounting and rejects insufficient legacy history. R3 preserves the canonical design content hash. R4 routes alternate-duty execution and continuation through the same lifecycle without default-duty substitution. R5 provides the F01–F12/C01–C12 acceptance matrix with exact test and artifact references.

## Scientific result and trade-off
The 4096-element qualified feedback demonstration begins with an estimated achieved-state mass of 37.5 kg/m², then 32.5 kg/m², then a conditionally scenario-feasible design under the 31 kg/m² cap. Mass and thermal transmission improve while thermal stress increases slightly; **not every objective improves**. The result is a synthetic software test and does not validate ceramic manufacturability.

## Historical versus corrected evidence
The earlier 46/252 passing tests and independent 257-test report concern earlier commits, not this correction. Only the final corrected-revision GitHub Actions logs, actual checkout SHA, and uploaded raw dossiers qualify the corrected source. The independent reviewer must inspect these artifacts and decide whether findings close.

## Remaining limits
No experimental measurements, calibrated process uncertainty, CFD, sintering, porosity, manufacturing residual-stress prediction, signed external provenance or mid-kernel restart. No WP5 or merge. Independent Gate 3 **performed, changes required, pending closure**, not passed.


## Three-defect independent follow-up

Following review of `54c8674`, terminal feasible checkpoint recovery, embedded attempt-event validation and optional verification persistence were corrected. Final feasible recovery must not rerun any completed numerical evaluations. Reuse is proven by a durable continuation marker and validated against hash-chained stage events. Optional numerical verification is recorded only after successful recomputation, and its result is saved consistently with the returned dossier.

The exact independent reproductions and terminal default/alternate call-count audits are in `foundation/tests/test_wp4_final_review_defects.py` and `foundation/wp4_review_evidence.py`. The final source revision and CI checkout must be recorded from the subsequent workflow; previous passing runs do not qualify these edits. Gate 3 remains awaiting independent closure.


## Final R2 checkpoint-write recovery correction

Independent review of `ed84a8f0` confirmed a checkpoint callback failure *after numerical evaluation but before candidate persistence* caused an unreopenable resumed dossier. The correction retains both evaluation attempts in the durable event ledger, distinguishes a completed numerical evaluation from a committed reusable checkpoint, and permits a new attempt after a failed write. Reused-candidate accounting is based on persisted checkpoints rather than event completions. The complete dossier is validated and reopened before `resume()` succeeds.

Tests include interruption before the first checkpoint, after earlier checkpoints, final feasible checkpoint, alternate duty, repeated recovery and independent numerical-call counts. The `wp4_review_evidence.py` evidence archive includes each raw manifest, journal, event sidecar, resumed dossier and JSON call audit. Existing terminal checkpoint and optional verification behavior remains required. No new physics or experimental validation. Independent Gate 3 closure is pending.
