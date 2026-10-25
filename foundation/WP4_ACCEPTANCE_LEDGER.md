# WP4 independent corrective acceptance matrix — awaiting reviewer closure

**Authority:** WP4 Implementation Brief v1.0; independent Gate 3 review **performed, changes required**, not approved. No WP5, no merge. Source revision for this table is the branch revision at the final WP4 Actions run; the workflow artifact `wp4-tested-sha.txt` is the authoritative actual checkout, not an assumed PR merge SHA. Earlier 46/252 and 257-test reports refer to earlier revisions and do not qualify this revision.

**Observed status:** Rows describe acceptance criteria and expected executable outcomes. A passing workflow must supply the actual observed result; do not treat a test name as an observed pass. Each row remains *pending final run and independent inspection* until the final logs and artifacts are pinned.

| ID | Requirement | Precise expected result | Executable verification | Supporting artifact / log | Observed result / remaining limitation |
|---|---|---|---|---|---|
| F01 | WP2/WP3 baseline unchanged | Foundation and recovery suite passes | `Full foundation/recovery pytest` | `CI job log` | **Pending final run**; Pending final checkout |
| F02 | Homogeneous, layered and gradient transform bounded | Analytical references and interfaces match | `test_wp4_analytical_reference.py; test_wp4_resolution.py` | `WP4 focused log` | **Pending final run**; Synthetic only |
| F03 | Signed volume balances conserved | Expected and actual constituent totals agree | `test_wp4_balances.py` | `WP4 focused log` | **Pending final run**; Unit-area ideal deposition |
| F04 | Achieved-state evaluation changes with process resolution | WP2 evaluates estimated geometry and retains identity | `test_wp4_bridge.py; test_wp4_mesh_separation.py` | `WP4 focused log` | **Pending final run**; No measured physics |
| F05 | Binding violation causes intended redesign | 4096-element case reaches conditional feasibility after two revisions | `test_wp4_qualified_feedback.py; higher-resolution CI step` | `wp4-higher-resolution.json` | **Pending final run**; Stress trade-off remains |
| F06 | Impossible budget never falsely succeeds | Exhaustion recorded and no feasible result invented | `test_wp4_feedback.py; wp4-impossible CLI` | `wp4-impossible.json` | **Pending final run**; No physical feasibility |
| F07 | Feedback on/off comparable | Same declared budget; unused evaluations explicit | `test_wp4_comparisons.py; paired()` | `wp4-paired.json` | **Pending final run**; Not equal consumed work |
| F08 | Sensitivity preregistered | Five-point fixed grid recorded without selection bias | `test_wp4_comparisons.py; sensitivity()` | `wp4-sensitivity.json` | **Pending final run**; Bounded grid |
| F09 | Dossiers portable and numerically replayable | Separate-process reopen/recompute passes | `test_wp4_feedback.py; WP4 CI replay` | `wp4-dossier.json` | **Pending final run**; No external signature |
| F10 | Cancellation and interruption preserve work | Verified checkpoint reuse, durable event accounting and resumable dossier | `test_wp4_resume.py; test_wp4_review_reproductions_v2.py` | `wp4-review/*` | **Pending final run**; Mid-solver recovery unsupported |
| F11 | Alternate duty and second transform | Alternate runs, resumes and replays unchanged duty; uniform route evaluated | `test_wp4_uniform.py; test_wp4_review_reproductions_v2.py` | `wp4-review/alternate-*` | **Pending final run**; Two synthetic routes |
| F12 | Estimated is not measured | Export excludes measurements and rejects forged evidence | `test_wp4_export.py; test_wp4_review_reproductions_v2.py` | `wp4-export.json` | **Pending final run**; No experimental validation |
| C01 | Invalid resolution rejected | Nondivisible thickness and invalid steps fail closed | `test_wp4_resolution.py; test_wp4_boundaries.py` | `WP4 focused log` | **Pending final run**; Extreme grids limited |
| C02 | Quantization deterministic | Ties and endpoints preserve fractions | `test_wp4_analytical_reference.py; test_wp4_boundaries.py` | `WP4 focused log` | **Pending final run**; Two constituents |
| C03 | Material balance invariant | Signed volume and density checks consistent | `test_wp4_balances.py` | `WP4 focused log` | **Pending final run**; No shrinkage |
| C04 | Unsupported properties/geometry rejected | Missing inputs fail qualification | `test_wp4_bridge.py; inherited WP2 tests` | `Foundation log` | **Pending final run**; Synthetic property pack |
| C05 | Invented measured record rejected | Resealed measurement forgery rejected | `test_wp4_export.py` | `WP4 focused log` | **Pending final run**; External forgery beyond checksum |
| C06 | Versioned process and evaluator identity | Unknown route/evaluator/revision rejected | `test_wp4_registry.py; review reproductions` | `WP4 focused log` | **Pending final run**; No independent evaluator registry |
| C07 | Numerical eligibility respected | Unqualified output cannot claim feasible | `test_wp4_feedback.py; test_wp4_qualified_feedback.py` | `wp4-higher-resolution.json` | **Pending final run**; Mesh-specific |
| C08 | Adversarial campaign mutations fail | False stop/schema/baseline/counters rejected | `test_wp4_review_reproductions_v2.py` | `WP4 focused log` | **Pending final run**; Checksum not authentication |
| C09 | Interrupted recovery truthful | Completed evaluations reused; missing history rejected | `test_wp4_resume.py; wp4_review_evidence.py` | `wp4-review/*` | **Pending final run**; No mid-kernel restart |
| C10 | Registry and alternate lifecycle | Unknown transforms fail; alternate context preserved on resume | `test_wp4_registry.py; review reproductions` | `wp4-review/alternate-*` | **Pending final run**; Bounded routes |
| C11 | Revision deterministic | Lineage, feedback causality and stopping validated | `test_wp4_integrity.py; review reproductions` | `WP4 focused log` | **Pending final run**; Not general Pareto |
| C12 | Cancellation and budgets fail closed | Impossible/zero budget, interrupted checkpoint and corrupt tail tested | `test_wp4_cancellation.py; test_wp4_boundaries.py; test_wp4_journal.py` | `WP4 focused log` | **Pending final run**; No physical validation |

## Corrective reviewer reproductions

R1: unsupported schema 999, forged no-improvement, wrong baseline input hash, false feedback-disabled multi-candidate history, and process/mesh mismatch must all be rejected by `reopen` before numerical replay. R2: interruption reuses completed baseline and candidates; numerical evaluator-call audit is independently counted in `foundation/wp4_review_evidence.py`. Missing legacy manifests/events are rejected, transform failures are not counted as numerical evaluations, and forged cumulative counters fail. R3: baseline export uses `IntendedDesign.content_hash`; a design-content change with the same ID changes the digest. R4: alternate-duty manifest preserves full WP3 typed baseline, duty and process across continuation and replay. R5: reconcile this matrix with the final CI logs, architecture, usage, completion and challenge reports.

**Gate 1:** implementation evidence under final verification. **Gate 2:** corrective challenges under final verification. **Gate 3:** independently reviewed, changes required, awaiting independent closure. No physical ceramic validation claimed.
