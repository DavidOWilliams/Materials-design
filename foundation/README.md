# WP1 materials design foundation

WP1 provides strict versioned contracts, the preserved A01–A15 assumption
registry, immutable run snapshots in SQLite and JSON artifacts, and a replayable
CPU thermal verification example. It is the foundation for the planned inverse
design workflow. It is not the complete D1 demonstration or V1 measured ceramic
validation.

Start here for current implementation instructions. The recovery branch is the
base; older phase-specific restrictions describe the preserved legacy route.
See [the completion report](COMPLETION_REPORT.md),
[architecture and extension review](ARCHITECTURE.md),
[decision log](DECISIONS.md) and [environment details](ENVIRONMENT.md).

## Setup and run

From the repository root, with Python 3.12 installed:

```sh
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python -m material_core.demo --store foundation/runs/demo --architecture gradient
```

The last command prints a `run_id`. To reopen it in another process and verify
the calculation, substitute that ID:

```sh
.venv-foundation/bin/python -m material_core.demo --store foundation/runs/demo --replay RUN_ID
```

Choose `homogeneous`, `layered` or `gradient`. These are recovered synthetic
verification fixtures, with conductivity prescribed independently of
composition. They are not competing equal-material-budget ceramic designs.
The example evaluates thermal transmission only. Requested but unsupported
objectives remain explicitly incomplete, and achieved-state evaluation is
rejected by this adapter rather than replaced with the intended state.

For a repeatable evidence run covering all three fixtures and separate-process
replay:

```sh
.venv-foundation/bin/python foundation/verify_demo.py --output /tmp/wp1-verification
```

## Integration boundaries

`material_core/contracts.py` defines Brief, MaterialRecord, IntendedDesign,
ProcessScenario, manufacturing commands, estimated and measured achieved states,
Evaluation and DecisionRecord. The contracts reject unknown fields and schema
versions, invalid units, nonfinite values and inconsistent composition/geometry.
Frozen tuples and canonical JSON support detached snapshots. Public store and
adapter boundaries revalidate serialized models, including objects created
using Pydantic's unchecked `model_copy` helper.

`assumptions.py` retains exact WP0 questions and qualifications. Updates append
versions; each run stores the full selected records. The registry never assigns
a fabricated numeric value to an unresolved scientific question.

`store.py` stores input/result artifacts by SHA-256 and run metadata in SQLite.
Inputs include source hashes, assumption versions and full records, solver
source/dependency identity and settings. Identical requests share an artifact
and evaluation key but have distinct execution IDs. `find_complete` checks
integrity before returning cache candidates. Changed assumptions create a
different key; historical runs remain bound to their original snapshots.

`thermal.py` is the sole implemented evaluation adapter. Candidate generation
and manufacturing transformation have typed protocol boundaries but no working
inverse-search or process model in WP1. No core module imports the legacy UI.

## Storage and recovery

Keep the entire store directory: `runs.sqlite3` plus `artifacts/`. For this
single-operator prototype, close writers before copying both together. Never
back up only the database. Reopen using `RunStore(path).load(run_id)`; all input
and result artifact hashes and contract versions are checked.

A created run with no result is an interrupted/incomplete execution, not a
successful result. A failed run retains its reason. Terminal results cannot be
overwritten; retry by creating another execution. Missing/corrupt artifacts
raise `ArtifactIntegrityError`; restore the exact artifact from a backup, or
retain the damaged store and create a new run. Do not edit checksums to conceal
damage. A crash can leave an unreferenced artifact but does not acknowledge a
result before its artifact is durable.

The SQLite schema and payload schemas have separate versions. Unknown versions
are refused. Future domains require explicit typed variants and retained v1
readers; no automatic schema migration or distributed scheduler is claimed.

## Scientific boundaries and next work

Thermal mismatch is distinct from total residual stress. The Pelz discrepancy
and CODE missing fields, failed specimens and unequal budgets remain unchanged.
No researcher or family member was contacted. No new scientific model was
trained or invented.

WP2 should qualify property mappings and bounded thermal/mechanics adapters,
beginning with analytical free expansion, restrained expansion and a layered
reference. It should reuse the run/assumption trail, retain signed stress and
source conventions, and register tolerances before broader evaluation. Search,
manufacturing resolution feedback and the UI follow in their planned packages.


---

## WP2 bounded numerical evaluation (dedicated unmerged branch)

WP1 above remains an historical description of what WP1 delivered.
WP2 adds the mapped synthetic three-objective evaluator and an explicitly
bounded classical-laminate thermoelastic calculation. It does **not**
turn the synthetic phase catalogue into validated printed ceramic data.

From repository root using Python 3.12:

```sh
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python foundation/verify_demo.py --output /tmp/wp1-history-replay
.venv-foundation/bin/python foundation/verify_wp2.py --output /tmp/wp2-numerical
```

The setup script deliberately refuses to overwrite an existing environment.
If `.venv-foundation` already exists, use it rather than rerun setup, or
pass a new directory to `foundation/setup.sh`.

For an individual three-objective example and a separate process replay:

```sh
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp2_demo \
  --store /tmp/wp2-single --architecture gradient
# Copy the run_id shown in the printed JSON:
PYTHONPATH=foundation .venv-foundation/bin/python -m material_core.wp2_demo \
  --store /tmp/wp2-single --replay RUN_ID
```

Choose `homogeneous`, `layered` or `gradient`. Add
`--architecture gradient --achieved` for a separately labelled supplied
synthetic achieved-state geometry. The three objective IDs are
`thermal_transmission` (absolute W/m²),
`areal_mass` (kg/m²), and
`tensile_thermal_mismatch` (Pa, positive cell-centre equibiaxial stress).
The signed raw flux and stress profile remain in the persisted spatial fields.
No flow/CFD, drying, sintering or process-to-state prediction is implied.

Use `foundation/WP2_NUMERICAL_QUALIFICATION.md` for scientific equations,
reference values and limitations;
`foundation/WP2_ARCHITECTURE_AND_DECISIONS.md` for interfaces and extension
paths; and `foundation/WP2_COMPLETION_REPORT.md` for the WP2 exit review.
The two GitHub Actions jobs run separate locked-core and legacy-regression
environments; the core job uploads replay JSON evidence as an artifact.
Do not infer V1 validation, D1 completion or approval to merge.
