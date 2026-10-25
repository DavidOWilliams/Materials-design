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
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --paired /tmp/wp3-paired --paired-reopen
```

Seeds 11, 23 and 37 are prespecified in the service. Search uses structured coverage plus bounded seeded changes; sampling draws uniformly from the same discrete/continuous domain. Both include the same homogeneous start and isolated store. The second command cross-checks each paired export row against its linked immutable campaign, validating the saved totals and Pareto counts. Counts are attempted evaluations and confirmed paired kernel solves; a failed computation may leave its actual solve count uncertain. The output is *not* a pre-registered hypervolume benchmark and must not be interpreted as statistical superiority.

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

## Supported and retired commands (R1)

**Only schema-2 `material_core.wp3_search` is supported for new WP3 campaigns and accepted evidence.** The historical `material_core.wp3_campaign.run_campaign`, `reopen_campaign` and ordinary CLI now raise `RuntimeError: ... retired`. The independent review demonstrated that schema-1 counters and Pareto IDs could be altered without detection. They are not valid WP3 acceptance evidence, even if the historical run-store artifacts remain intact.

To inspect old JSON without validating it:

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_campaign --ledger PATH_TO_SCHEMA1_JSON --legacy-read-unvalidated
```

The reader returns `validation_status=UNVALIDATED_LEGACY_V1`, `review_eligible=false` and the original historical contents; it makes **no replay or qualification claim**. Preserve old files unchanged; generate a new schema-2 campaign at a **new directory** for current qualification.

## Versioned providers and scenario differences (R4)

Default provider: `wp3-synthetic-catalogue-provider-v1`, preserving the A/B/C synthetic software scenarios. The second registered provider `wp3-alternate-duty-layered-provider-v1` uses the same corrected WP2 evaluator, with a 380 K/320 K thermal duty and a variable **three-layer** configuration instead of the default 400 K/300 K A/B/C domain. Both are hypothetical numerical scenarios without validated ceramics data.

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-alternate/campaign.json --provider wp3-alternate-duty-layered-provider-v1 --seed 17 --budget 3
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-alternate/campaign.json --reopen
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --ledger /tmp/wp3-alternate/campaign.json --recompute
```

The scenario adapter owns the baseline, proposal construction and typed validation. Campaign sequencing, budgets, persistent links, qualification/decision coordination and stop states are scenario-neutral. The campaign stores provider identity, actual brief hash, catalogue hash, declared objective and constraint IDs, and evaluator identity. An unknown provider fails explicitly; an unregistered evaluator cannot be silently substituted during numerical recomputation.

**Search-policy terminology:** `explore` is structured seeded sampling, not evaluation-driven adaptive optimisation. The original A/B/C and the alternate three-layer paths are bounded scientific-software demonstrations, not evidence of physical performance.

## Recovery and termination states (R2–R3)

Allowed `stop_reason` values are `running`, `cancelled`, `wall_time_budget_exhausted`, and `evaluation_budget_exhausted`. Terminal records include `termination_event` with matching reason and number of consumed proposal slots. Invalid reasons (such as `manufacturing_validated`), impossible budget exhaustion and terminal states with outstanding `created` proposals are rejected. Resume records the previous stop in `stop_history`, changes status to `running`, clears terminal declaration, and only then continues.

When another proposal is pending, previously completed proposal summaries and numerical comparison remain **fully validated**. A corrupt objective, constraint, qualification, evidence or manufacturing field is rejected without changing the historical ledger. Recovery tolerances apply to the pending operation's normal state transition, not to unrelated completed data. A process kill between evaluation commit and journal update can be resumed without re-evaluating that completed result.

Termination-event metadata documents the campaign's own cancellation or wall-time decision, not an independently authenticated external signal. The whole-campaign proposal budget persists across resumes; wall-time applies separately per invocation as previously documented.

## Re-review commands

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_wp3_review_r1_r4.py foundation/tests/test_wp3_campaign.py -q
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
```

For **R1–R4 before correction**, use `foundation/reproduce_reviewed_wp3_r1_r4.py` with `PYTHONPATH` bound to an isolated checkout of exact reviewed commit `d62023d7205d48beba11269d4c358a7380ab9ca4`. The GitHub workflow's `wp3-original-review-reproduction` job does this without modifying the historical revision.


## Evaluator identity requirement (R4 follow-up)

Every campaign binds a versioned evaluator identity **before** a run store or ledger is created. No `evaluation_adapter` argument means the registered `wp2-bounded-2` implementation unless a registered alternate identity is explicitly requested. Supplying a custom callable **without `evaluator_identity` raises ValueError before any numerical work**. The reserved standard identity can only name the exact registered `evaluate` implementation; a wrapper cannot claim it.

`wp2-delegate-test-v1` is a separately registered **software test delegate** to the same corrected WP2 evaluator, not a new scientific model. It is a supported versioned execution and numerical-replay identity. For example:

```python
from material_core.wp3_search import run_search, open_search, recompute_search
from material_core.wp3_evaluators import DELEGATE
run_search("/tmp/wp3-evaluator/campaign.json", seed=7, budget=2,
           elements=256, evaluator_identity=DELEGATE)
open_search("/tmp/wp3-evaluator/campaign.json")
recompute_search("/tmp/wp3-evaluator/campaign.json")
```

Fault-injection callables remain available using explicit, clearly labelled test identities (such as `fault-wrapper-v1`). Their records can be checked against stored immutable artifacts, but numerical recomputation fails explicitly because no registered evaluator exists for that identity. Using an explicitly labelled temporary test identity does not certify its numerical behaviour. This prevents accidental replay with a different implementation and preserves the existing interruption tests.

Regression suite: `foundation/tests/test_wp3_evaluator_identity.py`. The workflow also runs the registered delegate campaign and numerical recomputation in separate processes and uploads the complete run store. This does not broaden WP3 scientific scope or change WP2 thresholds.
