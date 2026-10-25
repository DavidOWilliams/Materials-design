# WP4 corrective challenge test report

## Executable challenges
`test_wp4_review_reproductions_v2.py` reproduces unsupported schema 999, forged no-improvement stop, incorrect baseline evaluation input hash, numerical mesh mismatch, false content hash, missing event history, altered cumulative counters, alternate-duty interruption/continuation and content-hash sensitivity. `test_wp4_r1_r4_review_closure.py` rejects a forged feedback-disabled three-candidate campaign and tests the original recovery defect. `test_wp4_resume.py` asserts completed evaluations are reused, not recomputed.

`foundation/wp4_review_evidence.py` independently wraps the numerical evaluator to count calls before and after injected interruption, produces complete default and alternate-duty resumed dossiers, reopens and numerically recomputes them in a separate verification step, and archives the manifest, checkpoint journal, attempt events and call audit.

Other scientific and numerical challenges: `test_wp4_analytical_reference.py`, `test_wp4_thermal_reference.py`, `test_wp4_balances.py`, `test_wp4_qualified_feedback.py`, `test_wp4_comparisons.py`, `test_wp4_integrity.py`, `test_wp4_export.py`, `test_wp4_registry.py`, `test_wp4_mesh_separation.py`.

## Evidence
Dedicated WP4 qualification workflow `.github/workflows/wp4-qualification.yml` archives `wp4-qualification-dossiers`, `wp4-tested-sha.txt` and `wp4-review/*`. WP3 PR integration CI is separate. The acceptance matrix gives each F/C case's expectation, test and artifact. **A passing test is not independent Gate 3 approval.**

## Remaining limitations
The demonstration uses synthetic process assumptions and WP2 numerical physics. No measured ceramic achieved state, authenticated adversarial event ledger, calibrated uncertainty or solver-kernel restart. Independent Gate 3 performed, changes required, awaiting closure.
