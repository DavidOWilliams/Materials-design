# WP2 focused correction log and numerical requalification

24 October 2026 | Original reviewed source: `ae052d6f70499eceb92e73436fd0de7cb1791777`

**Scope:** Correct reviewed WP2 only. No WP3, WP4 or WP5 implementation. PR #2 remains draft against WP1. Existing source is retained wherever sound.

The original implementation and both the 23 October completion and numerical-qualification reports remain permanently accessible at the reviewed commit above. The old numerical values are superseded for calculation/recommendation purposes, not erased.

## Independent reproduction, before edits

The GitHub Actions `wp2-reviewed-defects-and-history` job checks out the **exact original reviewed SHA** in a distinct directory and creates its own locked Python 3.12 environment. It executes `foundation/reproduce_reviewed_wp2_defects.py` against that immutable original checkout. All five reported failures were reproduced:

| ID | Original defect reproduced | Corrected behaviour | Requalification evidence |
| --- | --- | --- | --- |
| A | Homogeneous 128-cell free plate reported 3,663.778305 Pa of fictitious tensile mismatch | Within-cell linear thermal moment `Q alpha T' h³/12` incorporated exactly; force and moment use correct continuum integrals | Executable refinement, exact free-plate solution, quadrature-independent force/moment test, analytical bilayer, reversal and convergence |
| B | Literal escaped newline kept stress-refinement assertions within a Python comment | Assertions are now executable; old code violates the corrected near-zero stress requirement | Baseline repro script plus new `test_mesh_refinement_constant_coefficients` and `test_free_homogeneous_exact_linear_temperature_refinement` |
| C | A 31 kg/m² mass ceiling plus a 29 kg/m² floor produced duplicate constraint metric IDs | Exactly one value per metric; outcome records carry distinct constraint ID/relation/limit/outcome | `test_wp2_corrections.py`, `test_wp2_constraint_gate.py`, stored replay; equality, contradiction, missing values and units |
| D | Process route changes remained compatible; unknown manufacturing state became 'conditional' and eligible | Comparison context hashes the process/method/snapshots and separate manufacturing state; numerical-only APIs do not imply feasible manufacture | Original counterexample; same-context alternatives; changed process, assumption and solver; unknown and infeasible estimates persist |
| E | Hot face 900 K passed with original 290–410 K property records by widening settings to 1000 K | Explicit per-property numeric min/max domains are versioned and hashed; actual temperatures and reference state checked | Original counterexample; domain-boundary, widened-setting, missing/misaligned domain, and freshly identified wider scenario tests |
| WP4 wording | Process-state evidence presented as a D1 dependency | D1 resolution-scenario feedback and V1 measurement validation separated | Completion report, architecture handoff and plan-aligned wording |

## Corrected continuum thermal moments

For a cell with thickness `h`, midpoint coordinate `z_c`, constant biaxial
stiffness `Q`, constant expansion `alpha`, and an **exact linear**
conduction temperature field
`T(z)=T_c+g*(z-z_c)`:

```
N_T(cell) = Q alpha (T_c - T_ref) h
M_T(cell) = Q alpha ((T_c - T_ref) h z_c + g h^3/12)
D(cell)   = Q (h z_c^2 + h^3/12)
```

Here all z are relative to the laminate midplane. The free plate solves
`[[A,B],[B,D]] @ [epsilon_0, kappa] = [N_T,M_T]`.
The resultants used for *independent verification* integrate the reconstructed
linear stress polynomial `Q*(epsilon_0 + kappa*z - alpha*(T(z)-Tref))`
over cell endpoints for both `int sigma dz` and `int z*sigma dz`.
Thus the acceptance test does not use the solver's centre-temperature thermal
moment approximation.

For any homogeneous slab with a linear temperature profile, the exact
small-strain free-plate solution is
`epsilon_0 = alpha*((Th+Tc)/2 - Tref)`,
`kappa = alpha*(Tc-Th)/h`, `sigma(z)=0`.
The unit test guards absolute tensile stress **0.05 Pa** for 2, 16, 64,
128 and 512 cells; this tolerance covers floating-point cancellation
at 100 GPa-scale stiffness. It is not ceramic uncertainty.

For layered and graded spatially changing phase properties, the cell-centre
maximum is a sampling approximation; it is not the true interface/surface
limiting stress. Additional mesh-doubling tests gate eligible numerical
comparisons. Exact equilibrium cannot stand in for stress convergence.

## Numerics and comparison accuracy contract

A corrected mapped evaluation computes its nominal cell mesh and a separate
2x refined mesh on the **same** physical design and property assumptions.
The result is `numerical_quality=qualified` only when all pass:

- Sampled maximum tensile stress: absolute difference below 0.05 Pa when
  the refined stress is near zero; otherwise relative 0.1%.
- Bending curvature: absolute difference at most 2e-9 1/m when near zero;
  otherwise relative 0.1%.
- Thermal flux magnitude: relative mesh-doubling difference at most 1e-5.
- Areal mass: absolute difference at most 1e-8 kg/m².

These are mathematical discretisation acceptance criteria, **not experimental
material precision**. An under-resolved run remains `status=complete`
because its numerical functions calculated results, but it is marked
`numerical_quality=unresolved` and refused by
`numerical_comparison_eligible`. Only the explicitly labelled
`exploratory_numerical_eligible` function admits unqualified but
complete, numerically calculated and constraint-satisfying vectors for
diagnostic review. `compatible_comparison` checks common method/context;
it makes **no** feasibility or qualification assertion.

Ordinary `Evaluation.comparison_eligible` is also **not** a substitute for
an established manufacturing-feasibility review. Intended state has
`manufacturing_feasibility=unknown`; estimated state's declared
`unknown`, `conditional` or `infeasible` passes through unchanged.

## Constraint and applicability contracts

There are four distinct quantities: numerical completion, evaluated hard
constraint outcomes, manufacturing feasibility, and evidence maturity. A fifth
numerical-resolution status is tracked separately. A contradictory floor and
ceiling yield an infeasible constraint vector instead of an exception or an
optimistic bound. Independent `ConstraintOutcome` objects record each ID,
relation, limit and pass/fail/unknown result; shared physical metrics are
calculated only once.

The effective-property layer reads the machine-checkable numeric lower and
upper temperatures for **every required property record** (conductivity,
density, biaxial modulus, thermal expansion). The intersection covers hot,
cold and prescribed stress-free temperatures. Settings may narrow but cannot
expand that intersection. Omitting applicability does not authorise a
default range. A wider hypothetical scenario must revise all affected
property records, provenance, property-pack hash and run identity.

## Historical-run semantics

- **WP1:** the original three input/evaluation canonical JSON objects, SHA256
  hashes and separate-process replay remain unchanged, with a fresh original
  WP1 baseline checked at `22350b119d8a30248a9924ba375ebf4c8dabb4b7`.
- **Reviewed WP2 v1:** a separate CI job checks out
  `ae052d6f70499eceb92e73436fd0de7cb1791777`, creates an original
  `wp2-bounded-1` persisted run and replays it with the original solver.
  The CI `wp2-cross-version-history` job then opens the same archived
  run using the corrected reader, checks its unchanged result hash and
  **rejects** attempting to reevaluate with a different solver source/version.
- **Corrected WP2 v2:** the solver is `wp2-bounded-2`, with its current
  source hash. A fresh corrected evaluation receives a new immutable input
  and result identity; no prior result is overwritten or quietly reinterpreted.
  Explicitly revised property-domain records further change pack identity.

## WP4 handoff correction

The authoritative Implementation Plan v2 states:

**D1 working demonstration:** an explicit, versioned layer/feed-resolution
*capability assumption* can transform an intended design to an estimated
achieved composition/geometry profile. The transform must preserve total
geometry and material accounting, propagate the achieved state into all
evaluators, expose binding manufacturing/material constraints, and trigger
redesign. It must not claim an experimentally verified manufacturing process.

**V1 measured ceramic validation:** independently verified commands,
manufacturing volumes, composition, geometry, porosity, uncertainties and
specimen/process provenance are needed for a measured comparison. A lack of
these records does not block D1.

WP2 delivers the typed integration boundaries and numerical evaluator, not a
WP4 manufacturing transformer. Neither D1 nor V1 is delivered in this
correction work package.

## Verification protocol

Use the final green *GitHub Actions* run linked by PR #2. Its jobs must show:

1. Immutable original WP1 hash-locked installation, 74-test suite, and
   reproduction of the original constraint defect.
2. Reproduction of the five original WP2 review failures on the exact
   23 October reviewed commit, creation of its archived run and independent
   replay with that original method.
3. Current Python 3.12 locked installation, `pip check`, all foundation,
   recovery and corrected WP2 tests, WP1 three-case replay, corrected WP2
   four-case persisted replay plus JSON evidence.
4. Independent legacy regression environment, `pip check`, complete
   `tests recovered_wp0` suite.
5. Cross-version reader opening original WP2 artifacts, verifying hashes
   and refusing a silent changed-method replay.

This correction log does not waive any numerical failure. Historical errors
and historical successful CI runs must be labelled by their exact revisions.

## Remaining domain limits

Synthetic neutral phase values; Voigt conductivity and stiffness estimates;
assumed 290–410 K property domain; perfect bonding; 1D stationary Fourier
conduction; small-strain equibiaxial laminate membrane/bending; positive
sampled in-plane tensile elastic mismatch only. No sintering, drying,
microstructure, porosity change, fracture, creep, fatigue, total residual
stress, experimentally qualified deposition model or measured V1 validation.
Scientific records A01–A21 retain their unresolved status where applicable.
