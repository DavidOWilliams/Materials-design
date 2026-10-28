# WP6-R1–R4 protocol amendment v1.0 — frozen before correction execution

Date: 2026-10-26. Original protocol: PREREGISTERED_PROTOCOL.md. Original nine-case tested run 40336776440 and artifact 12658165098 are retained without modification. This amendment is prospective, not a retrospective change to those outcomes.

## Confirmatory cases and expected outcomes
- Existing nine full-resolution cases: repeat at 4096 elements, nominal budget 4, preserve every candidate; compare to original results by dossier content and objective values, without assuming byte-identical metadata.
- R1 paired feedback on/off: same fixture, process, settings, and maximum four candidate proposals. Record baseline plus candidate numerical evaluations, refinement solves, proposals, unused slots, early stopping and qualified candidates. **Hypothesis**: feedback-off stops after one candidate; actual effort differs. A nominal-budget comparison is descriptive, not equal-effort causal evidence. No algorithm modification or padding of extra solver evaluations is permitted. Exploratory equal-effort policy: compare the common initial candidate and baseline only, as a *shared-prefix* comparison; this has equal actual effort but cannot establish a feedback improvement effect.
- R2 held-out duty description: distinguish identity-only test from scientific held-out test. Existing WP5 prepared_inputs permits only duty, id, version and budget changes. Mass-limit and process sensitivities are separate supported scenarios, not independent held-out physics. **Expected**: no claim of scientific generalisation. No new physics is authorized.
- R3 adversarial cases: reject invalid budget without files; reject unsupported brief physics edits without files; corrupted dossier must fail closed; cancellation must be explicit; no-feasible limit 1 kg/m² with budget 4 must return zero feasible; exploratory saturated limit 1 kg/m² budget 8 may yield no-improvement or exhaustion, report actual stop rather than substitute result; missing measured evidence must remain null.
- R4 numerical reproduction: in a fresh Python process reopen all nine saved dossiers and call WP5 replay; capture replay status, numerical reference differences if available, provenance and objective units. Deliberately tampered dossier must be rejected. Use unchanged WP2 numerical qualification logic, never re-label conditional feasibility as measured validation.

## Frozen settings
Python 3.12, foundation/requirements.lock.txt plus Streamlit 1.40.2 for existing WP5 UI regressions. Synthetic WP4 route, 4096 elements, mass limits 31/30/1 kg/m², layer 0.005/0.010 m, feed fraction 0.25/0.50, nominal proposal budget 4, deterministic existing WP4 revision policy. Extra saturated negative case: 128 elements, budget 8. No stochastic seed is applicable to the deterministic WP4 algorithm.

## Acceptance and interpretation
Gate 1 requires full green functional and regression run, archived raw results, separate-process replay, and verified SHA256SUMS. Gate 2 may pass only for demonstrated bounded challenges; the scientific held-out generalisation requirement remains open unless a separately qualified fixture is introduced. R1 closes only as a **narrowed claim** (descriptive unequal-effort comparison plus equal-effort shared prefix), not as superiority of feedback. Unknown/inconclusive is never pass. Gate 3 is independent.

## Evidence
Archive source-sha.txt, dependencies, commands/logs, original and corrected run references, raw dossiers, report.json, separate-process replay results, adversarial test outputs and SHA256SUMS. Preserve CI merge checkout SHA separately from tested branch implementation SHA. This amendment is frozen before the correction run; any later amendments must be separately versioned and explained.
