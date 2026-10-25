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
