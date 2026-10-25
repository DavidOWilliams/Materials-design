# WP4 execution, recovery and evidence

Run from repository root after `bash foundation/setup.sh`.

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback run /tmp/wp4-dossier.json --journal /tmp/wp4-journal.jsonl --elements 4096 --budget 4
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback resume /tmp/wp4-journal.jsonl --elements 4096 --budget 4
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback reopen /tmp/wp4-journal.jsonl.resumed.json
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp4_feedback recompute /tmp/wp4-journal.jsonl.resumed.json
```

The journal, `.manifest.json` and `.attempts.jsonl` sidecar must be retained together. The manifest freezes the original typed baseline, process, solver and implementation identities **before** numerical work. Resumption reuses completed baseline/candidate evaluations and appends only newly completed candidates; it does not restart an interrupted solver kernel. Missing legacy manifests or attempt histories are rejected rather than inventing exact costs. `recompute` is a separate optional verification process whose solver calls are **not** continuation cost.

For the alternate duty, run with `--adapter wp3-alternate-duty-layered-provider-v1` and a journal, then resume with the same resolution, budget and route options. The manifest preserves the original 380/320 K duty; it does not substitute the default 400/300 K fixture. A second synthetic route is `--route synthetic_ideal_uniform_batch_deposition --layer 0.01`.

The `run` service supports cooperative cancellation between candidate evaluations; no mid-solver cancellation/restart is promised. `wp4_export.export(dossier_path)` exports the canonical intended design hash and marks measured evidence unavailable.

**Scientific limits:** synthetic ideal deposition, no empirical ceramic measurements, CFD, sintering, porosity or manufacturing residual-stress prediction. Thermal stress can increase while mass and heat transmission improve.

**Review:** independent Gate 3 performed; changes required; corrected evidence awaits independent closure. The acceptance matrix and final CI checkout SHA are authoritative.
