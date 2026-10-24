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

The first command creates a full immutable run store and journal. `--reopen` checks stored checksums and reconstructs the qualified Pareto decisions without solving. `--recompute` also recomputes WP2 evaluations and compares canonical hashes in a separate invocation. Neither rewrites completed runs. The default campaign includes three architecture classes and three synthetic material pairs, bounded composition and gradient-knot variables.

## Paired equal-budget comparison

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp3_search --paired /tmp/wp3-paired --budget 9
```

Seeds 11, 23 and 37 are prespecified in the service. Search uses structured coverage plus bounded seeded changes; sampling draws uniformly from the same discrete/continuous domain. Both include the same homogeneous start and isolated store. Counts are evaluations and known paired kernel solves; a failed computation may leave its actual solve count uncertain. The output is *not* a pre-registered hypervolume benchmark and must not be interpreted as statistical superiority.

## Resource and interruption semantics

- Evaluation budget bounds the number of proposed runs; completed nominal and doubled-mesh WP2 solves count separately.
- Cancellation is polled between jobs, not mid-solver. Interrupted work is retained in a terminal failure record when reopening and resuming.
- Resume via Python API `run_search(path,seed=...,budget=...,resume=True)` requires exactly the original configuration. This cannot be used to silently change the search space or bounds.
- The immutable store and ledger must travel together for portable replay; retaining only exported summaries is insufficient.
- Each intended design retains `manufacturing_feasibility=unknown`. Actual manufacturing and achieved-state prediction are deferred to WP4 and measured validation to V1.
