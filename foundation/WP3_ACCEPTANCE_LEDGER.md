# WP3 requirement-to-evidence ledger — candidate freeze

**Authority:** WP3 New Chat Takeover and GitHub Brief v1.0, Vision v3 and Product Definition v1; corrected WP2 ancestor `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`.
**Scientific boundary:** synthetic planar thermal–mechanical demonstration. Manufacturing feasibility remains **unknown** for intended-only designs; an eligible numerical ranking is not manufacture validation.
**Evidence rule:** these mappings specify executable checks, not claims of independent acceptance. Record final commit and completed CI run in the frozen review section below, and do not accept an unchecked HEAD.

## Functional gate

| ID | Executable evidence | Acceptance status |
| --- | --- | --- |
| F01 | `foundation/setup.sh`, `pip check`, `verify_wp2.py`, foundation/recovery CI jobs | Passed at 40127435140 (185 foundation/recovery and corrected WP2 checks); direct-head focused job also passed |
| F02 | `test_wp3_provider.py`, `test_wp3_search.py`: homogeneous/layered/gradient, A/B/C synthetic catalogue and new gradients | Passed in corrected foundation/PR integration CI 40127435140; independent review pending |
| F03 | `test_wp3_evaluation_integration.py`, `test_wp3_search.py`, `wp3_qualified.py`: WP2 eligibility, common context, Pareto | Implementation + tests; independent ranking review pending |
| F04 | `test_changed_hard_constraint_and_no_solution`: 31 vs 1 kg/m² cap; separate immutable scenarios | Implemented; note this is a changed constraint, not a changed duty |
| F05 | Impossible 1 kg/m² bound; no numerically eligible Pareto members | Implemented |
| F06 | `compare_paired` with seeds 11, 23, 37 and equal caps; two isolated stores per paired seed | Implemented; actual three-seed outcomes in results below; no superiority claim |
| F07 | `open_search` and `recompute_search`, subprocess CLI and immutable `RunStore` | CI 40127435140 passed tamper, replay and hash/checksum checks; independent review pending |
| F08 | Cancellation before/after a completed evaluation, `stop_history`, resumable append-only ledger | CI 40127435140 passed interruption, failed attempt uncertainty, crash-after-store and atomic-write fault injection; independent review pending |
| F09 | Current foundation + recovery + legacy jobs, WP2 verifier, old run-store contracts | CI 40127435140: 185 foundation/recovery and 1,148 legacy/recovery passed; direct-head correction job 24 passed |
| F10 | registered `wp3_adapters.py` default/alternate provider contracts, actual changed-duty three-layer construction and generic `wp3_pareto.py` objective ordering | Software modularity tests, not additional scientific capability |

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
| C10 | Fixed seeds, persisted configuration digest, tampering tests, cancellation and replay tests | Fault injection and hard-exit subprocess tests added; no arbitrary network/power failure guarantee |


## Paired sampling observations — 24 October 2026

Source run: [WP3 Actions #40123058451](https://github.com/DavidOWilliams/Materials-design/actions/runs/40123058451), code/configuration at `cfe8631b0d315fc9e6b1369f3dbf1c6022b5682c`. Each method has 3 unique evaluations, no cache hits, and 6 reported nominal/refinement kernel solves per seed.

| Seed | Explore qualified | Sampling qualified | Explore Pareto | Sampling Pareto |
| --- | ---: | ---: | ---: | ---: |
| 11 | 2 | 3 | 2 | 3 |
| 23 | 2 | 3 | 2 | 2 |
| 37 | 2 | 1 | 2 | 1 |

Coverage counts are not objective-value superiority or scientifically meaningful hypervolume. Sampling achieves higher qualifying coverage on two seeds; structured coverage on one. The study is very small and does **not** justify a general claim that inverse search improves on uniform sampling. See archived input/evaluation artifacts for actual flux, mass and stress vectors. Method choice must remain open to further evidence.

## Exact gates and limitations

- **Gate 1:** Do not close until all jobs at the frozen source SHA succeed, artifacts are inspected and one numerical replay is separately checked.
- **Gate 2:** These are bounded tests in the declared synthetic domain. Not evidence that arbitrary constitutive models, property families or manufacturing data are supported.
- **Gate 3:** **PENDING SEPARATE REVIEW.** An external scientific/architecture reviewer must check numerical references, method applicability, Pareto eligibility, budget fairness, architecture and traceability independent of implementation-owned tests. CI does not replace this approval.
- **Not WP3:** WP4 process-resolution transform; WP5 UI; full D1; measured V1; coating/CFD/residual-stress process history; lifecycle scores or unmeasured material claims.

## Frozen-revision sign-off

At publication, record the tested commit SHA, run IDs, outcomes of each job, artifact IDs, reviewer identity/findings, any fixes and final independent reviewer decision here. **No independent reviewer approval is recorded in this document.**

## Independent WP3 inspection correction: finding → reproduction → change → verification

**Inspected head:** `3e46821daad059e2538a73ef521315ecde4a70a2` (unchanged when correction work began).
**Pre-correction reproduction:** CI [run 40126364720](https://github.com/DavidOWilliams/Materials-design/actions/runs/40126364720), `foundation/inspection_reproduce_wp3_defects.py`: **2 passing reproductions of the defects**, using unchanged implementation logic from inspected revision. The reproduction was deliberately kept outside the normal acceptance suite.
**Correction regressions:** `foundation/tests/test_wp3_inspection_corrections.py`, tested against corrected branch-head separately from GitHub's PR temporary merge.

| Finding | Observed before | Correction and authoritative basis | Behavioural regression |
| --- | --- | --- | --- |
| I-01: interrupted accounting | WP2 solver ran, KeyboardInterrupt before persistence; after resume, failed+complete ledger said only 1 unique evaluation, with no uncertainty | Non-cache created run is journaled as an attempt **before** evaluation; counts reconstructed from immutable RunStore links, not incremented only on successful result. Failed/created attempt remains uncertainty-marked; confirms only complete stored WP2 nominal/refinement solve pair | `test_interrupt_after_wp2_numerical_work_then_resume`, `test_subprocess_hard_exit_after_real_wp2_before_result_store` |
| I-02: corrupted accounting accepted | `unique_evaluations=999` opened without complaint | `open_search` rebuilds proposal/attempt/cache/confirmed solve and uncertainty counts from linked immutable runs and rejects inconsistent numeric fields | `test_tampered_counters_rejected` |
| I-03: objective and status fabrication accepted | Completed candidate `{"areal_mass":-999}` opened without complaint | `open_search` cross-checks objectives, individual constraints, eligibility, mesh quality, evidence, manufacturing status and hard-constraint status against stored evaluations | `test_tampered_evaluation_derived_summary_rejected` |
| I-04: interruption boundaries | Unknown after-result or during-write effect | Resume distinguishes lost pending result from durably finished result; catches independent-process hard exits, retains same proposal slot, verifies lineage; no silent duplicate evaluator call | `test_after_result_persistence_before_ledger_update_recovers_success`, `test_ledger_write_interrupted_after_wp2_commit`, cancellation/budget tests |
| I-05: proposal identity | Ledger description could diverge from true input | Verify reported architecture, pair and fraction/knot against immutable intended design and typed parent-run links | `test_tampered_proposal_parameters_rejected` |
| I-06: misleading CI provenance | Historical CI described as "final-head" despite PR merge checkout | Print actual event and checked-out SHA for all jobs, add separate SHA-pinned branch-head job and preserve workflow/artifact commit identities | Run 40126875288: temporary PR merge `f60588f9cc87ff06644d0acbd18d1338d5014604`; explicit head `47f4cd9ce288b3bbe62c93e9642318e33923c801` |

**Corrected example after a solver interruption, two proposal slots:** 1 failed + 1 complete, 2 attempts, 2 distinct attempted input hashes, 1 confirmed completed evaluation, 2 confirmed WP2 kernel solves, 1 uncertain attempt, `kernel_solve_count_uncertain=true`. Two is **not** asserted to be the total number of actual kernel solves. Before correction the same sequence reported one unique evaluation and no uncertainty.

**Limits:** run-store SHA256 and typed contracts protect stored artifacts against unmatched changes. Derived campaign records are validated against their linked immutable input/evaluation artifacts, and Pareto output is rebuilt. This does not prove resistance to a coordinated adversary who can rewrite the database, source artifacts, ledger and their hashes together. Crashes in the narrow window after a new store row is created but before its ledger link is durably recorded may leave an orphaned run that cannot yet be automatically recovered. Concurrent writers are unsupported. Confirmation of a nominal/refinement solve pair comes from a completed persisted WP2 evaluation; an opaque injected evaluator cannot prove how much partial work it did.

**Campaign resource contract:** a proposal slot counts toward the campaign-wide evaluation budget, including failed, invalid and cached proposals; resume does not reset it. A wall-time limit is per invocation and must be retained unchanged in the immutable campaign configuration. Mid-kernel wall-time preemption is not claimed.

## CI identity and review-gate discipline

- Historical run [40123251720](https://github.com/DavidOWilliams/Materials-design/actions/runs/40123251720) was reported successful but executed the **PR temporary merge** `d5f0039b32a120db5542d68fef98af423a29e2c2`, not a direct checkout of branch head `3e46821daad059e2538a73ef521315ecde4a70a2`. The underlying branch head was an input to that integration check, not its checked-out SHA.
- Corrected run [40126875288](https://github.com/DavidOWilliams/Materials-design/actions/runs/40126875288) logged `event=pull_request`, ordinary check-out `f60588f9cc87ff06644d0acbd18d1338d5014604`, and explicit `wp3-exact-branch-head` check-out `47f4cd9ce288b3bbe62c93e9642318e33923c801`. The latter ran focused correction tests and corrected WP2 reference verification.
- Subsequent commits require a **fresh** matching run, with independent head and temporary merge job results, artifact metadata, exact test counts and completion events recorded. Do not substitute a prior green run.
- Gate 3 **remains PENDING a separately tasked numerical and architecture reviewer**. Engineering CI and this findings-to-tests ledger are not independent approval.

## Verified corrected pre-review source — CI and artifacts

At commit **`8500ce4ff87118ab693bc4a17a9fdaa0f25b2a46`**, GitHub Actions [run 40127435140](https://github.com/DavidOWilliams/Materials-design/actions/runs/40127435140) finished with **all three jobs successful**.

| Job | Actual checkout SHA | Result | Job ID |
| --- | --- | --- | --- |
| `wp3-contract-and-vertical` | PR integration merge `598a16216ebca3dc49d8bf643fa66a8e10e55ed1` | **185 passed**, corrected WP2 reference, campaign/reopen/recompute and paired-report validation passed | 120971765610 |
| `wp3-legacy-regression` | PR integration merge `598a16216ebca3dc49d8bf643fa66a8e10e55ed1` | **1,148 passed; 10 warnings** | 120971765539 |
| `wp3-exact-branch-head` | Explicit branch head `8500ce4ff87118ab693bc4a17a9fdaa0f25b2a46` | **24 focused inspection tests passed**; corrected WP2 reference verifier passed | 120971765373 |

The run's event was `pull_request`, and `GITHUB_SHA` was the temporary merge commit; workflow artifact metadata separately reports head source SHA `8500ce4...`. The checked-out SHAs above were confirmed from the respective job logs rather than assumed from artifact labels.

- Campaign and separate-process replay output: artifact **12572624132**, 2,924,264 bytes, **115 files**, 17 SQLite stores, ZIP integrity test passed.
- Explicit-head corrected WP2 reference evidence: artifact **12573134325**, 396,840 bytes, **26 files**, ZIP integrity test passed.
- These artifacts and jobs are test evidence for their precise source revisions. Any subsequent documentation-only commit must obtain a matching final-head run; do not copy prior results forward as direct proof of a newer HEAD.

**Implementation-owned Gate 1 and Gate 2:** supported for the declared synthetic WP3 domain at the tested revision above. **Gate 3 remains PENDING** independent scientific and architecture review. No independent reviewer has approved the correction.

## Independent scientific/architecture review R1–R4 closure evidence — revision after d62023d

| Finding | Inspected defect and pre-fix reproduction | Correction | Required validation |
| --- | --- | --- | --- |
| R1 unprotected schema-1 API | Old `run_campaign` + forged `unique_evaluations=999` and `pareto_ids=["invented"]`; `reopen_campaign` accepted both | Retire normal v1 API/CLI, preserve `read_legacy_unvalidated` as labelled non-reviewable reader; use only schema-2 search as executable/CI path | `test_wp3_campaign.py` refuses normal API, CLI and forged historical evidence; current WP3 CI invokes schema-2; exact-original reproduction job |
| R2 recovery bypasses completed corruption | Real WP2 completes first, second crashes, corrupt first objective/constraints/status; old `recovery=True` suppressed unrelated mismatch | Remove blanket any-pending bypass; all complete summaries/counters/Pareto checked even with pending; only valid created-run reconciliation on resume | Parameterized completed-field corruption during pending recovery; pending comparison corruption; existing interruption boundary tests |
| R3 fabricated stop status | Set full ledger `stop_reason=manufacturing_validated`; old open accepted | Closed set of four reasons, matching terminal event, proposal budget/pending consistency, explicit resume-to-running transition and stop history | Unsupported and mismatched states, impossible budget, pending termination, actual cancel/stop/resume tests |
| R4 synthetic coupling | Hardcoded A/B starting design, objective IDs, fixture `propose` and geometric representation branches in campaign code | Versioned adapters with `start/proposal/build/validate/baseline` own scenario. Brief supplies objective/constraint IDs and hashes. Alternate synthetic 380/320 K three-layer WP2-supported duty proves a materially different scenario with same orchestration. Unknown adapters fail; recorded non-WP2 evaluator cannot be silently recomputed as WP2 | Alternate scenario persistence/reopen/resume/recompute and explicit CLI, mutated-proposal rejections, unsupported adapter tests and exact-original reproduction |

**Source of truth:** reviewed head `d62023d7205d48beba11269d4c358a7380ab9ca4` is checked out *unchanged* in CI job `wp3-original-review-reproduction` and the frozen `foundation/reproduce_reviewed_wp3_r1_r4.py` reports all four defects. Implementation-owned current regression tests do not substitute for a fresh independent review. See `foundation/WP3_R1_R4_CORRECTION_RECORD.md` for root causes, incompatibilities, architecture choices, and scientific safeguards.

**Compatibility:** historical schema-1 artifacts remain readable as unvalidated historical material only. They are not upgraded by opening, and must not be cited as qualified WP3 acceptance. New work must use the schema-2 path. Previous custom evaluator test doubles require a supplied callable for execution; reopening can check stored artifacts, but independent numerical recomputation must fail unless evaluator identity is registered and scientifically supported.

**Exploration is structured seeded sampling**, not an adaptive optimiser. Earlier three-seed comparisons do not establish superiority. New paired comparisons retain exactly the same budget/count semantics and fixed start within the default provider. These scientific boundaries and the distinct numerical qualification/hard-feasibility/manufacturing/evidence statuses remain mandatory.

**Gate 3 remains pending separately commissioned independent re-review** of the corrected, exact-commit review package.
