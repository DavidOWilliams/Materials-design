# WP4 usage — bounded synthetic feedback prototype

WP4 remains an **assumption-based software demonstration**, not measured ceramic validation.

Run in the locked foundation environment described in `foundation/ENVIRONMENT.md`, with `PYTHONPATH=foundation` and the locked Python interpreter:

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback run /tmp/wp4-dossier.json --elements 4096 --mass-limit 31 --layer 0.005 --feed 0.25 --budget 4
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback reopen /tmp/wp4-dossier.json
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback recompute /tmp/wp4-dossier.json
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback run /tmp/wp4-no-feedback.json --no-feedback --budget 4
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback run /tmp/wp4-impossible.json --mass-limit 1 --budget 4
```

Each run path must not exist already; this prevents overwriting historical dossiers. `reopen` validates recorded identities and decisions without running the numerical model; `recompute` regenerates the deterministic transformer output and WP2 numerical evaluations.

The reference coupon is 10 mm thick. Default layers are 5 mm. Feed fraction step is 0.25. Constituent volume fractions are discretised; the resulting estimated geometry is **not** a measurement. Commands are an ideal-deposition recipe on a unit-area basis, not machine G-code. Missing shrinkage, porosity, mixing lag, CFD and sintering remain unknown.

The initial campaign uses a synthetic A/B gradient, then attempts bounded density-guided revisions when estimated achieved areal mass violates the common mass cap. A numerical qualification or conditional scenario result is **not** global manufacturing feasibility.

The present campaign API does not support interruption recovery or independent Gate 3 approval; these are open requirements and must not be inferred from WP3's accepted functionality.

## Append-only checkpoint mode

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback run /tmp/wp4-checkpointed-dossier.json --journal /tmp/wp4-checkpoints.jsonl --elements 256 --budget 4
PYTHONPATH=foundation .venv-foundation/bin/python -c 'from material_core.wp4_journal import recover; print(len(recover("/tmp/wp4-checkpoints.jsonl")))'
```

The checkpoint journal flushes each complete candidate and rejects partial trailing writes. It is single-writer and **not** a resumable execution engine; after interruption, previously committed records can be inspected, but automated continuation is not supported. This is deliberately different from WP3's campaign store.

The explicit transform registry (`wp4_registry.py`) rejects unknown process routes. `wp4_alternate.py` runs the accepted WP3 alternate-duty adapter through the same transform/evaluator bridge. Both are synthetic software scenarios, not distinct empirically calibrated manufacturing processes.

## Resume and second manufacturing capability

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback resume /tmp/wp4-checkpoints.jsonl --elements 256 --budget 4
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback run /tmp/wp4-uniform-dossier.json --route synthetic_ideal_uniform_batch_deposition --layer 0.01 --elements 256 --budget 4
```

## Explicit cancellation and evidence export

The CLI is synchronous. Cooperative cancellation is exposed at the service boundary between candidate evaluations, not as an operating-system signal handler:

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -c 'from material_core.wp4_feedback import run,save; save("/tmp/wp4-cancelled.json",run(elements=256,cancel_requested=lambda: True))'
PYTHONPATH=foundation .venv-foundation/bin/python -c 'import json; from material_core.wp4_export import export; json.dump(export("/tmp/wp4-dossier.json"),open("/tmp/wp4-evidence-export.json","w"),indent=2)'
```

The export is derived from the validated complete dossier and explicitly labels measured evidence unavailable. Do not substitute it for the full source record or claim experimentally established manufacture feasibility.
