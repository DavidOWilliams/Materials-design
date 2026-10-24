# WP3 bounded search: execution and evidence

WP3 is an assumption-based **synthetic planar thermal–mechanical** demonstration, not a validated ceramics predictor. All distances, flux, mass, thermal mismatch and property conditions must be interpreted using the recorded scenario and corrected WP2 contracts.

## Locked environment

From repository root:

```bash
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pip check
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python foundation/verify_wp2.py --output /tmp/wp3-wp2-reference
```

## Mixed-space exploration and replay

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-review/search.json --seed 17 --budget 9
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-review/search.json --reopen
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-review/search.json --recompute
```

The first command creates an immutable run store and an atomic campaign journal. `--reopen` verifies immutable input/result checksums, proposal/parent links, all declared objective, constraint, qualification, evidence and manufacturing summaries, derived accounting and reconstructed Pareto decisions **without solving**. Tampered summaries are rejected, not silently repaired. `--recompute` also recomputes WP2 evaluations and compares canonical hashes in a separate invocation. Neither rewrites completed runs. The default campaign includes three architecture classes and three synthetic material pairs, bounded composition and gradient-knot variables.

## Paired equal-budget comparison

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --paired /tmp/wp3-paired --budget 9
```

Seeds 11, 23 and 37 are prespecified in the service. Search uses structured coverage plus bounded seeded changes; sampling draws uniformly from the same discrete/continuous domain. Both include the same homogeneous start and isolated store. Counts are evaluations and known paired kernel solves; a failed computation may leave its actual solve count uncertain. The output is *not* a pre-registered hypervolume benchmark and must not be interpreted as statistical superiority.

## Resource and interruption semantics

- **Evaluation budget is a whole-campaign limit on proposal slots**, including invalid proposals, completed evaluations, interrupted/failed attempts and cache hits. On resume, previously consumed slots are not reset and neither the budget nor method, seed, catalogue, adapter identity, mesh, duty or hard constraints may change.
- **Wall-time limit is per invocation**, not cumulative across resumes. The numeric value is stored in the immutable configuration and must match on resume; any additional invocation can consume a fresh allocation of the same duration. Wall-clock time is not a guaranteed hard kill during a numerical solve. Cancellation is polled between proposals, not mid-solver.
- Every non-cached, created run is journaled **before** calling the evaluator. `evaluation_attempts` counts attempted non-cached evaluations, `unique_evaluations` counts distinct attempted input hashes, `successful_evaluations` counts completed non-cached evaluations, and `failed_attempts` counts failed records. A restored interrupted run uses its original run ID and slot and becomes a retained failed run unless its result was durably completed; it is never re-executed silently.
- `nominal_kernel_solves`, `refinement_kernel_solves` and `confirmed_numerical_solves` count only **confirmed** paired solves supporting a complete persisted WP2 evaluation. An interrupted/failed attempt may have executed zero, one or two kernels, so `uncertain_evaluation_attempts` and `kernel_solve_count_uncertain=true` explicitly prevent treating the confirmed count as an exact total. In an interrupted campaign, confirmed totals are lower bounds, not bounds on actual CPU work.
- Resume via Python API `run_search(path,seed=...,budget=...,resume=True)` requires exactly the original configuration. This cannot be used to silently change the search space or bounds.
- The immutable store and ledger must travel together for portable replay; retaining only exported summaries is insufficient.
- Each intended design retains `manufacturing_feasibility=unknown`. Actual manufacturing and achieved-state prediction are deferred to WP4 and measured validation to V1.

## Inspection reproductions, diagnostics and integrity limits

The original defects are preserved as reproducible tests in `foundation/inspection_reproduce_wp3_defects.py`. CI run [40126364720](https://github.com/DavidOWilliams/Materials-design/actions/runs/40126364720) executed and passed both **old-defect reproductions** before correction. Run the corrected positive tests with:

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp3_inspection_corrections.py -q
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
```

The correction tests include a real WP2 solve followed by `KeyboardInterrupt`, `os._exit(57)` in a separate process, an interrupt after the evaluation has already been committed, and a simulated interrupted ledger write. Resume is explicitly tested. Ledger counter changes, fabricated objective/constraint summaries, modified qualification/manufacturing/evidence statuses, proposal parameters and parent links are rejected against the immutable inputs/evaluations. Derived fields are checked at read time; corruption is **not** fixed by recomputing an attacker-supplied digest.

**Integrity boundary:** cryptographic hashes validate the immutable run artifacts against their stored references and objective/decision reports against those artifacts. They do not supply external signatures or protect against an attacker capable of coordinated replacement of the SQLite database, all artifacts, the ledger and its provenance. This is accidental or uncoordinated tampering detection, not tamper-proof audit storage. A hard kill after SQLite insertion but before the campaign journal records the newly created run can leave an orphan run record; the campaign cannot yet reconstruct a wholly missing journal link automatically. Concurrent writers to the same campaign ledger are unsupported.

On pull-request Actions, the standard checkout normally uses a temporary merge SHA. The workflow prints `github.event_name`, `GITHUB_SHA` and `git rev-parse HEAD`; the separate `wp3-exact-branch-head` job explicitly checks out `github.event.pull_request.head.sha || github.sha` and prints that identity. Check the job logs and artifact metadata rather than assuming the tested checkout equals the PR branch head.
