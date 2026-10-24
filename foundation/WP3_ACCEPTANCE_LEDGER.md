# WP3 requirement-to-evidence ledger — candidate freeze

**Authority:** WP3 New Chat Takeover and GitHub Brief v1.0, Vision v3 and Product Definition v1; corrected WP2 ancestor `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`.
**Scientific boundary:** synthetic planar thermal–mechanical demonstration. Manufacturing feasibility remains **unknown** for intended-only designs; an eligible numerical ranking is not manufacture validation.
**Evidence rule:** these mappings specify executable checks, not claims of independent acceptance. Record final commit and completed CI run in the frozen review section below, and do not accept an unchecked HEAD.

## Functional gate

| ID | Executable evidence | Acceptance status |
| --- | --- | --- |
| F01 | `foundation/setup.sh`, `pip check`, `verify_wp2.py`, foundation/recovery CI jobs | CI to check on frozen commit |
| F02 | `test_wp3_provider.py`, `test_wp3_search.py`: homogeneous/layered/gradient, A/B/C synthetic catalogue and new gradients | Implementation + tests; final-head verification required |
| F03 | `test_wp3_evaluation_integration.py`, `test_wp3_search.py`, `wp3_qualified.py`: WP2 eligibility, common context, Pareto | Implementation + tests; independent ranking review pending |
| F04 | `test_changed_hard_constraint_and_no_solution`: 31 vs 1 kg/m² cap; separate immutable scenarios | Implemented; note this is a changed constraint, not a changed duty |
| F05 | Impossible 1 kg/m² bound; no numerically eligible Pareto members | Implemented |
| F06 | `compare_paired` with seeds 11, 23, 37 and equal caps; two isolated stores per paired seed | Implemented; interpretation requires inspection of actual outcomes |
| F07 | `open_search` and `recompute_search`, subprocess CLI and immutable `RunStore` | Implemented; artifact reopening and recompute are separate claims |
| F08 | Cancellation before/after a completed evaluation, `stop_history`, resumable append-only ledger | Implemented; hard termination mid-kernel is not resumable mid-solve |
| F09 | Current foundation + recovery + legacy jobs, WP2 verifier, old run-store contracts | Await final-head CI for all jobs |
| F10 | `test_replaceable_provider_and_evaluator_contract` and generic `wp3_pareto.py` objective ordering | Software modularity tests, not additional scientific capability |

## Challenge gate

| ID | Evidence | Interpretation |
| --- | --- | --- |
| C01 | `test_wp3_provider.py`: varying constituents, architectures, layer boundary/fraction, gradient middle fraction and knot position; rejected unsupported pairs/bounds | Search currently declares volume fraction only; other bases are not silently converted |
| C02 | `test_wp3_pareto.py` tests mixed min/max, permutation, ties, duplicates and missing objectives | Contract tests |
| C03 | WP2 corrected constraint tests, including two-sided and contradictory limits | Inherited WP2 with unchanged scientific contract |
| C04 | Missing objective exclusions in Pareto and WP2 unknown-manufacturing regression | No unknown-to-feasible promotion |
| C05 | `test_wp2_corrections.py` / `test_wp2_property_mapping.py` property applicability | Inherited WP2 |
| C06 | `compatible_comparison`, context/hash/method regression tests and distinct catalogue pack | Inherited WP2 and WP3 tests |
| C07 | 128-mesh under-resolved WP2 cases excluded from final qualified comparisons | Inherited WP2 |
| C08 | Pydantic contracts, provider bound tests and invalid search configuration tests | Unsupported input rejected |
| C09 | WP2 achieved-target guards and evidence-status contract tests | WP4 transformer intentionally not implemented |
| C10 | Fixed seeds, persisted configuration digest, tampering tests, cancellation and replay tests | Ledger-level checks; no arbitrary host crash simulation |

## Exact gates and limitations

- **Gate 1:** Do not close until all jobs at the frozen source SHA succeed, artifacts are inspected and one numerical replay is separately checked.
- **Gate 2:** These are bounded tests in the declared synthetic domain. Not evidence that arbitrary constitutive models, property families or manufacturing data are supported.
- **Gate 3:** **PENDING SEPARATE REVIEW.** An external scientific/architecture reviewer must check numerical references, method applicability, Pareto eligibility, budget fairness, architecture and traceability independent of implementation-owned tests. CI does not replace this approval.
- **Not WP3:** WP4 process-resolution transform; WP5 UI; full D1; measured V1; coating/CFD/residual-stress process history; lifecycle scores or unmeasured material claims.

## Frozen-revision sign-off

At publication, record the tested commit SHA, run IDs, outcomes of each job, artifact IDs, reviewer identity/findings, any fixes and final independent reviewer decision here. **No independent reviewer approval is recorded in this document.**
