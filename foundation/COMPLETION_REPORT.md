# WP1 completion report

23 October 2026 | Materials-design | Foundation package

## Outcome and preserved revision

WP1 is complete against its ten exit criteria. It provides the validated
contracts, versioned assumptions, persistent run storage, locked CPU environment
and executable thermal integration check requested in the consolidated WP1
instructions. D1, the full inverse-design demonstration, is not complete.
V1, measured ceramic validation, remains a separate unresolved milestone.

The tested implementation is published at
[`729a9da54cf339cc7c97526879a5ec49e03fcd4f`](https://github.com/DavidOWilliams/Materials-design/commit/729a9da54cf339cc7c97526879a5ec49e03fcd4f)
on [the WP1 branch](https://github.com/DavidOWilliams/Materials-design/tree/wp1-foundation-2026-10-22).
Its tree `9b45f64e01dd90c410731e51f5eb31f0560f1f04` exactly matches the locally
tested commit `9fc44509bf45096d52d7abb8d84f13d786e31c60`. The different commit IDs
reflect publication through the authenticated GitHub connector. This report is
added in a subsequent documentation-only commit; it does not change that source.

The parent is the specified recovery commit
`2655d64f2d5a02dfeaf2a3c4c1e553cda218a89f`. Main and the recovery branch were not
merged, rewritten or deleted. Legacy application and recovery reference source
remain unchanged. Outside `foundation/`, only a README entry-point link and a
virtual-environment ignore entry were added.

## Implemented capability

The immutable contracts separate the brief, material evidence, intended design,
process scenario, manufacturing commands, estimated achieved state, measured
achieved state, evaluation and decision. They preserve composition basis,
coordinates, units, source conditions, conventions, unknown values, lineage and
solver identity. Continuous design knots and numerical discretisation are
different objects. There is no fixed core count of constituents, layers or
objectives.

The A01–A15 registry preserves the exact original questions, provisional
answers, evidence and consequences. Each record also carries owner, version,
affected calculations and a resolution criterion. Unjustified numeric values
remain null/unresolved. Updates append versions and change run identities;
historical runs store the complete assumption snapshots actually used.

SQLite records execution identity, status and lineage. Inputs and results are
immutable, canonical JSON artifacts addressed by SHA-256. The store validates
artifact integrity and result/input/brief/solver correspondence when reopening.
It retains created-but-interrupted, failed, incomplete and unsupported runs.
Terminal evaluations and decisions cannot be overwritten. Cache lookup verifies
integrity and uses full consequential-input identity, including assumptions,
evidence and numerical settings.

The thermal adapter calls the unchanged recovered Fourier implementation.
It runs homogeneous, equal two-layer and linear-gradient synthetic conductivity
fixtures, saves them and reopens/replays them in other Python processes. It
refuses unsupported architecture details and achieved-state targets. It does
not infer conductivity from composition, material names or legacy scores.

The reusable direction is protected by replaceable generator, manufacturing
transformer and evaluator protocols, typed objective metadata, explicit
unsupported results and immutable evidence history. The current planar/thermal
payload is deliberately bounded. [The architecture review](ARCHITECTURE.md)
identifies the typed variants and version-aware readers needed for coatings,
other routes/objectives and higher-dimensional geometry; it does not claim that
those solvers already exist.

## Verification actually executed

| Check | Result | Evidence |
|---|---|---|
| Fresh minimal hash-locked setup on 22 October | Passed, Python 3.12.14 and 13 locked packages; pip check clean | `evidence/environment-setup.txt`, `environment-freeze.txt`, `environment-platform.json`, `environment-pip-check.txt` |
| Second fresh setup on 23 October using the same setup script/lock | Passed in `wp1-final-env`; pip check clean | `evidence/final-environment-freeze.txt`, `final-pip-check.txt`; commands below |
| Final foundation plus recovery suite | **74 passed in 1.52 seconds**, no exclusions: 46 WP1 checks and 28 recovery checks | `evidence/final-foundation-tests.txt` |
| Fresh separate legacy plus recovery environment | **1,148 passed in 33.44 seconds**, no exclusions; 10 dependency deprecation warnings | `evidence/legacy-regression-tests.txt`, `legacy-verification.md`, freeze/install/pip-check records |
| Three executable fixtures, each created and replayed in separate processes | Passed | `evidence/demo-verification.json` and the six input/evaluation JSON snapshots |
| Repository preservation and publication | Published tree exactly matches tested local tree; legacy/recovery source unchanged | Commit and tree identities above |

The test counts overlap by the 28 recovery checks; they must not be added as if
every check were distinct. The 1,148-test result was executed during this WP1
task on 22 October; it is not the historical WP0R result copied forward.

Final commands from the repository root:

```sh
bash foundation/setup.sh /workspace/scratch/3c56ad540c71/wp1-final-env
PYTHONPATH=foundation /workspace/scratch/3c56ad540c71/wp1-final-env/bin/python -m pytest foundation/tests recovered_wp0 -q
PYTHONPATH=foundation /workspace/scratch/3c56ad540c71/wp1-final-env/bin/python foundation/verify_demo.py --output /workspace/scratch/3c56ad540c71/wp1-final-demo
/workspace/scratch/3c56ad540c71/wp1-final-env/bin/python -m pip check
git diff --check
```

Legacy setup and exact regression commands are retained in
`evidence/legacy-verification.md`. The second fresh setup was needed after the
working session resumed; it also re-exercised the supplied setup procedure.
Default user commands, without these task-specific paths, are in
[README.md](README.md).

| Fixture at 128 elements | Fresh heat flux W/m2 | Replay |
|---|---:|---|
| Homogeneous | 20,000.000000 | Passed |
| Equal-thickness discrete layers | 33,333.333333 | Passed |
| Linear conductivity gradient | 49,708.001008 | Passed |

Registered replay tolerances are relative `1e-10`, absolute `1e-7 W/m2` for flux
and conservation diagnostics, and absolute `1e-8 K` for temperature. Input,
brief and solver identity, status, missingness and interpretation metadata must
also match. Independent resistance references, conservation and refinement
checks retain the recovered tolerances. These are numerical checks, not bounds
on physical prediction uncertainty. Each create-plus-replay pair, including
Python startup and storage, took approximately 0.82–0.84 seconds on this host.

## Exit criteria disposition

| WP1 criterion | Status | Specific evidence |
|---|---|---|
| 1 Invalid fields, units, nonfinite values and inconsistent designs rejected | Passed | Contract tests cover NaN/infinity, booleans/coercion, unknown fields/versions, dimension mismatches, composition sums/duplicates, layer gaps/overlap and unordered knots; store/adapter revalidate boundaries. |
| 2 Estimated and measured states retain distinct identities | Passed | Separate tagged contracts, measurement-provenance guard and storage round-trip test; unknown porosity/geometry and failed specimen status retained. |
| 3 A01–A15 available with exact questions and traceable versions | Passed | Built-in registry JSON and tests compare every original source row; updates retain prior versions and reject tampering. |
| 4 Stable consequential-input identity and invalidation on change | Passed | Identical requests hash consistently; reordered/formatted assumption snapshots normalize; assumption, source evidence, settings and solver changes alter identity; old cache is not reused. |
| 5 Saved run reopened in a new process with inputs/provenance/outputs intact | Passed | Store subprocess test compares full input/result JSON; CLI replay runs independently for each fixture. |
| 6 Replay within declared tolerance and explicit corruption/incompleteness handling | Passed | Three fixture replays; missing/corrupt artifacts, valid-digest unknown schemas, inconsistent metadata, interrupted runs and terminal overwrite attempts tested. |
| 7 Fresh setup using supplied instructions and lock | Passed | Two new minimal environments created with `--require-hashes`, Python 3.12.14, numerical checks and clean pip check. |
| 8 Relevant legacy and recovery regressions satisfactory | Passed with stated limits | 1,148 fresh offline checks, zero exclusions; UI and live-service workflows not exercised. |
| 9 Source, tests, setup, decision log and completion report preserved in GitHub | Passed | Dedicated WP1 branch; tested source checkpoint above, followed by this report-only commit. No main merge. |
| 10 Two future-case walkthroughs and extension map | Passed | ARCHITECTURE.md covers coating/substrate and another route/process-energy objective, reuse, new contracts, migration and preservation of old runs. |

## Remaining limitations and assumptions

All A01–A15 scientific entries remain open. Software implementation has not
resolved the ceramic pair/property pack, effective-property mapping, printed
versus bulk transfer, thermoelastic applicability, reference temperature and
restraint, interface validity, stress metric, process response, omitted
drying/sintering physics, expansion conventions, objective relevance, justified
uncertainty, independent physical validation or expert-value comparison.

No manufacturing transformer, inverse search, bounded mechanics adapter or full
user interface is delivered by WP1. The nominal process scenario records layer
and feed resolution but does not manufacture an achieved state. Known/unknown
states and conditional numerical feasibility are not manufacturing acceptance.

V1 payloads currently contain a planar thermal brief, thermal settings and
thermal field outputs. New domains require explicit typed variants and retained
v1 decoders; mixed-version dispatch is not yet implemented. The extension map
flags the migration cost before those shapes spread into future UI/search code.
Higher-dimensional geometry, coating interface laws and alternative-route
physics are not represented by dummy temperatures or arbitrary text payloads.

The storage design is for a local single operator. It has no distributed worker
scheduler, automatic migration, multi-user access controls or independent
archival authenticity claim. Separate-process replay occurred on the same host,
not a second person's machine or a freshly built Codespace/container.

Full Streamlit UI and live Materials Project workflows were not exercised.
The separate legacy installation follows the recovered dependency freeze and
retains its installation/deprecation warnings, including a yanked legacy
`pymatgen-core` package warning. That package is not in the new core environment.

The Pelz literal/reversed thickness discrepancy remains unresolved. CODE
alumina/zirconia evidence remains distinct, with unknown command/geometry/
porosity fields, unequal composition budgets, failed specimens and limited
specimen linkage. No missing ceramic response was invented or calibrated.
No researcher or family member was contacted and no services were purchased.

## Decisions and next package

[DECISIONS.md](DECISIONS.md) records the stale recovery/publication statements,
document authority, phase-specific legacy restrictions, empty roadmap, solver
selection, synthetic fixture scope, assumption/cache policy and scientific
reference distinctions. [The source review](evidence/source-review.md) records
the exact supplied-document hashes and repository sources used.

The next step is WP2 numerical evaluation: qualify material/property mappings,
generalize thermal evaluation only within verified domains, and connect an
existing bounded thermoelastic formulation. First verify free expansion,
restrained expansion and a layered reference, preserve stress sign/reference
conventions and register tolerances before multiobjective campaigns. Add areal
mass only with explicit constituent/density accounting. Feed evaluations through
the existing run store so the subsequent search and manufacturing packages
share one traceable workflow.

There is no evidence from WP1 alone to widen or compress the provisional
**4–6 active-week D1 planning range**. Setup, storage and numerical integration
worked; mechanics qualification and the first complete feedback loop remain the
major estimation checkpoints. Re-estimate at that loop, provisionally around
implementation week two. This is not a calendar completion promise or a claim
of unattended background work. V1 still has no defensible date because measured
evidence and scientific acceptance remain outstanding.
