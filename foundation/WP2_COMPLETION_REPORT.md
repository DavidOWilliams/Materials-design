# WP2 completion report — bounded synthetic numerical evaluation

23 October 2026 | Materials-design | WP2 work-package handoff

## Exit decision

**WP2 numerical software scope: PASS for its expressly bounded, synthetic
planar thermomechanical demonstration.** This is a numerical implementation
and verification milestone, **not** scientifically validated printed-ceramic
performance or complete D1 inverse design. The assumed mixing relations and
phase properties remain conditional, and all A01–A21 scientific questions
retain their actual unresolved status.

The source was built from verified WP1 branch head
`22350b119d8a30248a9924ba375ebf4c8dabb4b7` without modifying main,
the recovery branch, recovered reference source or the legacy metallic
selection code. The dedicated WP2 branch is
`wp2-numerical-2026-10-23` with draft PR #2, targeting WP1 rather than main.

**Verified source/CI commit**:
`8d9f15a641c44e2c8346db7bf050dc60d09c9506`.
GitHub Actions verification:
https://github.com/DavidOWilliams/Materials-design/actions/runs/39986262631
The final report itself is documentation-only and will have a later
publishing commit. No merge was requested or performed.

## Scope delivered

From a common typed `Brief`, consistent hypothetical material catalogue
and a design with homogeneous, discrete layered or piecewise-linear graded
architecture, WP2 calculates three physical numerical quantities:

1. **Thermal transmission**, `W/m2`, the magnitude of steady
   through-thickness Fourier flux. The original signed flux and spatial
   temperatures are preserved.
2. **Areal mass**, `kg/m2`, from the same geometry and phase density
   accounting used by the other adapters.
3. **Tensile thermal mismatch**, `Pa`, the positive maximum over sampled
   equibiaxial in-plane elastic stress at cell centres, with signed stresses,
   force/moment equilibrium diagnostics and bending curvature retained.

All quantities use a common 10 mm duty, property pack, boundary conditions,
stress-free temperature, physical input range, and scenario identity.
A bounded classical laminate plate treatment includes bending for asymmetric
stacks. Constituent count, layer count and objective count are **not** fixed
in reusable core contracts. Coatings, additional geometries and process
physics require explicit future specialist adapters, not dummy outputs.

The source includes a separately labelled **synthetic supplied achieved-state**
fixture that changes actual evaluated geometry/composition. It demonstrates
that the new target is used without claiming any process transformation or
measured state. Unknown measured geometry never defaults to intended geometry.

## Scientific qualifier

Only neutral synthetic phases A and B, with explicit numerical conductivity,
density, biaxial stiffness and thermal expansion, are included in the runnable
catalogue. Effective-conductivity Voigt parallel-channel, volume-additive
density, iso-strain stiffness and stiffness-weighted expansion assumptions
are separately declared. These do not establish material compatibility,
manufacturing feasibility or validated composite-property prediction.
Properties are scenario-constant only across the declared 290–410 K domain.
All unsupported or incomplete physical inputs reject or become unresolved.

The implemented stress is an **elastic thermal-mismatch contribution** under
one selected thin plane-stress kinematic idealisation. It is not total
manufacturing residual stress, sintering/drying shrinkage, crack prediction,
fatigue, lifecycle performance or a certified material criterion.

## Fresh verification actually performed

The successful CI execution used Linux GitHub Actions runners, Python 3.12,
and two separate dependency environments. The baseline WP1 run was checked
out from the *immutable original* commit, not from the modified branch.

| Verification | Fresh outcome | Evidence |
| --- | --- | --- |
| Original WP1/recovery setup at reviewed SHA, `pip check` | Passed | CI job `wp1-immutable-baseline` |
| Original baseline suite | **74 passed**, 1.35 s | Same job |
| Original unmodified R1 defect reproduction | **Expected rejection reproduced**: constraint-only mass cannot be stored as objective | Same job |
| Modified WP2 setup via `foundation/setup.sh` and hash-locked 13 packages, `pip check` | Passed | CI `numerical-regression` |
| WP1 + recovery + WP2 unit/reference/integration suite | **116 passed**, 3.81 s | Same job |
| Saved WP1 homogeneous/layered/gradient artifact hashes and cross-process reader | Passed, original source files unchanged | `test_wp2_wp1_history.py` |
| Original WP1 three-architecture separate-process replay | Passed | `foundation/verify_demo.py` |
| WP2 homogeneous, layered, gradient and supplied achieved profile | **Four persisted runs and four separate-process replays passed** | `foundation/verify_wp2.py` plus downloadable CI artifact `wp2-numerical-evidence` |
| Independent Fourier slab, multilayer resistance, analytic variable conductivity, flux direction and mesh convergence | Passed within registered numerical tolerances | `test_wp2_kernel.py`, `test_wp2_mapped_integration.py` |
| Independent free/restrained expansion and exact analytic bilayer A/B/D thermal bending reference, equilibrium and refinement | Passed within stated domain/tolerances | Same tests |
| Property endpoint, intermediate, mass/volume basis, missing/invalid data and scenario state checks | Passed | `test_wp2_property_mapping.py` |
| Constraint-only, shared and objective-only metrics, absent and nonfinite values, satisfied/violated and durable replay | Passed | `test_wp2_constraint_gate.py`, mapped integration tests |
| Separate legacy requirements plus recovery regression suite, `pip check` | **1,148 passed**, 10 dependency-deprecation warnings, 31.03 s | CI `legacy-regression` |

No test exclusion, skip or expected-failure waiver is represented as a pass.
Earlier red CI runs during implementation were inspected and fixed. The
latest green run above, not earlier cached WP1 logs, is the acceptance source.
No external UI, Codespace, second-person laptop, live printer or production
service was verified. Python 3.12 is a supported configuration; the
independently runnable CI host is not material validation.

## Numerical examples — 128-element synthetic catalogue

The following **observed** numbers were printed by the successful CI job
and independently replayed; they are not made-up ceramic property values.

| Intended or labelled achieved design | Thermal transmission W/m2 | Areal mass kg/m2 | Tensile mismatch Pa |
| --- | ---: | ---: | ---: |
| Homogeneous 50:50 A/B | 60000.00000000 | 30.0 | 3663.77830506 |
| Discrete equal A/B layers | 33333.33333333 | 30.0 | 11368069.04871642 |
| Continuous linear A→B gradient | 49708.00100817 | 30.0 | 4640168.56558629 |
| Supplied *estimated achieved* profile | 58376.02189673 | 32.5 | 9269091.99693567 |

The three **intended** architectures have the same 30 kg/m2 material budget.
An example hard mass ceiling is 31 kg/m2: the estimated achieved state is
**infeasible** for this ceiling, although its numerical vector is fully
computed. The original WP1 synthetic heat fixtures, Pelz literal and
reversed assignments and CODE case are preserved but are not treated as
experimental corroboration.

## WP2 exit criteria, one by one

| ID | Outcome | Direct support and qualification |
| --- | --- | --- |
| 1 R1 | PASS | Separate constraint results, unit checks, missing and nonfinite handling, hard feasibility and SQLite replay without adding objectives |
| 2 R2 and history | PASS | Typed thermal/mechanics/coupled settings; three actual WP1 artifact classes retain canonical hashes; original solver replay retained |
| 3 Property pack and mapping | PASS (synthetic domain) | Versioned and SHA256-bound neutral catalogue, source conditions, individual mapping rules, unsupported input rejection; real ceramic validation absent |
| 4 Thermal/mass/mechanics methods | PASS (bounded domain) | Registered independent analytical references, force/moment equilibrium, signed fields and mesh checks; process stresses excluded |
| 5 Common vector, three classes | PASS (synthetic scenario) | Three complete vectors under the same duty and nominal budget, with no fabricated measured property pack |
| 6 Distinct result categories | PASS | Numerical completion, hard feasibility, scientific evidence maturity and comparison contexts independent; unknown never silently passes |
| 7 Cache/identity | PASS | Full input hash, solver source/settings, catalogue provenance, assumptions and target; context mismatch and stale/changed pack rejected |
| 8 Storage and achieved target | PASS | Full input, fields, three metrics, limitations, context, synthetic evidence and constraint results persist and separately replay; achieved fixture changes values |
| 9 Fresh regressions | PASS | Immutable 74 original and R1 defect; 116 new; 1,148 legacy/recovery; both replay pathways |
| 10 Preserved deliverables | PASS | Source, tests, CI workflow, locked setup, reference report, architecture/decision map and this completion review on independent WP2 branch |

The **WP2 software exit passes**, conditional on the already explicit
synthetic domain, not on evidence of general printed ceramic applicability.

## Scientific assumption status

Original A01–A15 remain **unchanged, unresolved except as historically
recorded**. No record has been silently upgraded to "resolved". The
separate A16–A21 registry adds exact expert-review questions for
effective-property microgeometry, density/porosity, elasticity and stress-free
state, perfect interfaces, assumed temperature response and process-to-achieved
composition/geometry evidence. Each version retains provisional answer,
null value for unsupported physical claims, evidence, affected calculations,
priority, reviewer role and resolution criteria.

## How to reproduce and where to continue

From repository root (Python 3.12):

```bash
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python foundation/verify_demo.py --output /tmp/wp1-replay
.venv-foundation/bin/python foundation/verify_wp2.py --output /tmp/wp2-qualification
.venv-foundation/bin/python -m material_core.wp2_demo \
  --store /tmp/wp2-example --architecture gradient
# Use the printed run_id:
.venv-foundation/bin/python -m material_core.wp2_demo \
  --store /tmp/wp2-example --replay RUN_ID
```

Follow `foundation/README.md` and
`foundation/WP2_NUMERICAL_QUALIFICATION.md` for details.

**WP3 immediate implementation**: introduce bounded architecture proposal,
multiobjective search and a Pareto comparison service using the same brief,
solver API and context/evidence guard. Benchmark against reproducible simple
sampling with equal run budgets. A gradient is not preferred a priori: a
homogeneous or layered option may win.

**WP4 first real feedback loop**: replace the supplied achieved-state
fixture with a verified manufacturing data/process adapter linking feed
commands to deposited geometry and composition, then recompute the three
objectives on that achieved state. A model or measured link must carry
uncertainty and compatible process conditions; absent evidence cannot be
called successful manufacturing feedback.

**WP5**: expose the brief, spatial results, Pareto evidence and
decision/rejection history without inventing missing physics.

**Updated planning assessment**: the small CPU numerical core now runs in
seconds per 116-check regression and four-case replay; the legacy isolation
suite runs in tens of seconds. Compute capacity is not the first remaining
risk. A provisional focused implementation allowance is **about 3–6 active
work-weeks** for WP3 search, WP4 bounded feedback, WP5 workflow and integration
checks, with the largest uncertainty in credible process-state data and the
scientific scope of that mapping. This is a new risk-based estimate from the
working interfaces and actual CI runtimes, **not** a subtraction from an
earlier schedule and **not** a guarantee. External measured V1 validation
could require a separate research timescale.

## Change controls

No main merge, force push, deletion of old work, commercial purchase,
researcher communication or family contact occurred. The PR remains a draft
until explicitly reviewed. A green build permits WP3 to start from the
verified WP2 branch, but does not approve certification or physical ranking
of ceramic materials.
