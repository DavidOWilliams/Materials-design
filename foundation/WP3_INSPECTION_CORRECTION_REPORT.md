# WP3 Independent Inspection Corrections — implementation and handover

**24 October 2026 | Engineering correction report | Draft PR #3 remains unmerged**

## Purpose and authority

This is the finding-to-reproduction-to-fix-to-test record for independent inspection of WP3 at **`3e46821daad059e2538a73ef521315ecde4a70a2`**, on branch `wp3-inverse-search-2026-10-24`. Current Vision v3, Product Definition v1, Implementation Plan v2 and WP3 takeover brief remain authoritative. The corrected WP2 numerical baseline is `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`. No rewrite of the WP2 solver, merge, force-push, branch deletion or WP4 work was undertaken.

## Inspect-before-correction reproduction

Before modifying `wp3_search.py`, two tests were added in `foundation/inspection_reproduce_wp3_defects.py` to exercise the source as inspected. [Actions run 40126364720](https://github.com/DavidOWilliams/Materials-design/actions/runs/40126364720) reported **2 passed**. The tests assert the actual *defective* behaviour and are retained outside the standard regression suite as frozen provenance.

- **Interrupted attempt:** evaluator first executes real corrected WP2, then raises `KeyboardInterrupt`. After restarting the same configuration, the store has a failed proposal and a complete proposal, but old ledger counted **1** `unique_evaluations` and did **not** expose uncertain partial numerical work.
- **Misleading derived report:** editing the saved campaign ledger to `unique_evaluations=999` and `objectives={"areal_mass":-999}` allowed `open_search` to return altered values.

These pre-correction results are deliberately not success criteria for the new implementation.

## Corrections and independently observable behaviour

| ID | Reproduced failure / risk | Correction in `wp3_search.py` | Test / evidence |
| --- | --- | --- | --- |
| R1 | Interrupted numerical work disappeared from attempted evaluation count | Journal each noncached created run before invoking solver; reconstruct counts from linked durable run rows; mark created/failed work as numerically uncertain | Real-WP2 post-evaluation `KeyboardInterrupt`; separate process `os._exit(57)`; attempted vs confirmed counters |
| R2 | Interrupted recovery double-count/loss risk | Reconcile created run as complete if result already durably finished; otherwise terminate that same run as failed, use the same slot and preserve parent lineage; do not re-evaluate it automatically | Post-store persistence and interrupted ledger-write fault injection; resume without rewriting completed results |
| R3 | Numerical attempt count misrepresented as exact solve total | Separate `evaluation_attempts`, `unique_evaluations`, `successful_evaluations`, `failed_attempts`, `cache_hits`, confirmed WP2 nominal/refinement solves and `uncertain_evaluation_attempts`; explicit uncertainty flag | Normal, cancelled and fault-interrupted regression tests |
| R4 | `unique_evaluations=999` accepted | `open_search` reconstructs and compares required counter fields against all linked store records; missing fields are rejected except explicit recovery of a pending legacy run | Parameterized invalid counter values; missing required accounting field |
| R5 | `areal_mass=-999` and status fabrications accepted | Reconstruct and validate each completed proposal's numerical objectives, constraints, mesh quality, hard feasibility, evidence maturity, manufacturing feasibility and qualified eligibility from immutable evaluation | Parameterized object/constraint and status corruption regressions |
| R6 | Tampered proposal description or run references potentially misleading | Check run/input identity, immutable parent hashes and predecessor links; also compare architecture, constituent pair, fraction and gradient knot/position to typed stored design | Altered pair, architecture and fraction; existing hash/lineage regressions |
| R7 | Saved paired summary could be altered separately | New `reopen_paired` validates each paired-row count/decision against its own intact campaign and isolated run store, without mutating stored data | Paired summary tamper test; separate-process CLI `--paired-reopen` |
| R8 | Ambiguous CI "final branch-head" claims | Print `GITHUB_EVENT_NAME`, `GITHUB_SHA` and actual `git rev-parse HEAD`; separate SHA-pinned branch-head job from PR-merge integration job | Workflow logs list event, PR merge SHA and exact branch-head SHA |

### Before / after — interrupted two-slot campaign

| Field | Pre-correction reported | Corrected intended report |
| --- | --- | --- |
| Proposed slots | 2 (1 failed, 1 complete) | 2 (1 failed, 1 complete) |
| Evaluation attempts | Missing / not authoritative | 2 |
| Distinct attempted input hashes | 1 (incorrect) | 2 |
| Confirmed successful evaluations | 1 | 1 |
| Confirmed nominal + refinement WP2 solve pairs | Misleading / incomplete | 1 confirmed pair = 2 confirmed solves |
| Actual total kernel work during interrupted attempt | Not represented | **Unknown**; no fabricated exact total |
| Uncertain evaluation attempts | Not represented | 1 |
| `kernel_solve_count_uncertain` | False/absent | True |
| Manufacturing feasibility | Unknown for intended-only | Still unknown |

The confirmed solve count is a **lower bound** when interruption occurred. A real WP2 call may have performed partial or complete numerical work before the process died, but without a durably completed result the ledger cannot prove its exact kernel count.

### Resource semantics, persistence and recovery

- **Evaluation budget applies to the entire campaign**: a finite number of proposal slots including invalid proposals, failures, cache hits and completed evaluations. Resume never refills slots already consumed.
- **Wall-time limit applies per invocation**. The same numerical limit is part of the persisted configuration identity, while each invocation starts its own monotonic timer. It is a between-proposal guard, not a hard timeout for an individual solve.
- On new work, a `RunStore.create` operation creates a durable run, followed by the journaled `created` attempt. After completion, `RunStore.finish` saves immutable evaluation bytes. Reopening reconciles a journaled `created` with the run-store's actual terminal status, so a result committed just before crash is not automatically rerun.
- Journal writes are atomic-file replacement within the current platform assumptions. RunStore's SQLite and content-addressed JSON artifacts are authoritative for stored inputs, evaluations and terminal failed reasons. The journal is authoritative for declared campaign config, proposal intent/order and stop history, but its derived views are rechecked.
- The implementation-owned tests separately exercise cancellation before evaluations, interruption inside the wrapper, hard process exit, successful-result persistence before journal update, ledger-write failure, counter corruption, summary corruption and paired-report corruption.

## CI checked-out identities: interpret precisely

Previous [Actions 40123251720](https://github.com/DavidOWilliams/Materials-design/actions/runs/40123251720) was successful, but a **pull_request temporary merge** commit `d5f0039b32a120db5542d68fef98af423a29e2c2` was checked out. The source branch head `3e46821daad059e2538a73ef521315ecde4a70a2` was a constituent of that merge, not necessarily the checkout tested. This is not direct branch-head verification.

The correction workflow provides a separate `wp3-exact-branch-head` job whose checkout is pinned to the PR head, and prints its identity; the main `wp3-contract-and-vertical` PR job prints the temporary merge checkout identity. Tests from these different source trees must **not** be presented as the same exact binary/checkout. On a push event the ordinary checkout resolves the branch commit. For final qualification verify the job *event, checked-out SHA, source PR head, run ID, job ID, completion, and artifact head SHA* in the actual logs.

## Reproduction commands

```bash
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pip check
.venv-foundation/bin/python -m pytest foundation/tests/test_wp3_inspection_corrections.py -q
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python foundation/verify_wp2.py --output /tmp/wp3-corrected-wp2
.venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-fixed/search.json --seed 17 --budget 9
.venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-fixed/search.json --reopen
.venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-fixed/search.json --recompute
.venv-foundation/bin/python -m material_core.wp3_search --paired /tmp/wp3-paired-fixed --budget 3 --elements 4096
.venv-foundation/bin/python -m material_core.wp3_search --paired /tmp/wp3-paired-fixed --paired-reopen
```

For the old-defect reproducer, execute the supplied `inspection_reproduce_wp3_defects.py` using an **isolated checkout of the inspected original source**. Do not run its deliberately failing-behaviour assertions against corrected code as a passing acceptance suite. The CI run linked above is the frozen historic reproduction.

## Integrity boundary and remaining limitations

Internal consistency is checked against immutable stored input/result hashes and SQLite run metadata; no existing artifacts are rewritten by `open_search`. This is **not** protection against a coordinated attacker who can rewrite the journal, all SQLite records, property/evaluation artifacts and corresponding hashes. There are no trusted external signatures or independent public log anchor. A hard crash after `RunStore.create` and before the first campaign journal link can leave an orphan store row not automatically reconciled. Concurrent writers to the same campaign path are not supported; interrupted filesystem directory-sync failures and actual partial numerical work cannot be reconstructed beyond available evidence.

The model remains a **synthetic, bounded planar thermomechanical** example. Numerical qualification is separate from hard-constraint satisfaction, manufacturing feasibility and evidence maturity. Intended-only manufacturing feasibility remains **unknown**. The infeasible `mid_fraction=.35` reference remains infeasible, while `.65` is constraint-satisfying and numerically qualified only under declared assumptions. The small three-seed equal-budget comparison does not establish optimisation superiority. No D1, V1, real ceramic prediction, WP4 or WP5 is claimed.

## Acceptance

Gate 1 functional and Gate 2 implementation-owned challenge results must be linked to one final tested commit, including separate head/PR checkout identities and artifact validation. Gate 3 is **PENDING** a separately tasked independent scientific and architecture reviewer. The review package and `WP3_ACCEPTANCE_LEDGER.md` identify required checks and open questions. Keep PR #3 draft; do not merge before the required approval.
