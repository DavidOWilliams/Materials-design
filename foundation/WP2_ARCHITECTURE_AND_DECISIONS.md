# WP2 corrected architecture and decisions

24 October 2026. This document supersedes the 23 October WP2 architecture
decision report. The [original historical version](https://github.com/DavidOWilliams/Materials-design/blob/ae052d6f70499eceb92e73436fd0de7cb1791777/foundation/WP2_ARCHITECTURE_AND_DECISIONS.md)
remains available without alteration at its reviewed commit.

## Design intent and extension points

The enduring platform is a general-purpose material-system inverse-design
service with replaceable physics, optimisation, process models and
human/decision workflows. WP2 is one **bounded synthetic planar**
thermal/mass/elastic-mismatch numerical adapter, not a general ceramic
materials model, search implementation or manufacturing model.

| Architecture layer | Implemented and retained | Boundary / next package |
| --- | --- | --- |
| Immutable brief | Versioned geometry, objective direction, constraints, comparison duty, assumption references | Campaign/search API in WP3, without broadening common physical constraints |
| Materials | Provenance, process state, uncertainty, measured or synthetic evidence classification, phase properties and **per-property machine-readable thermal domains** | Other material systems add their own validated property/temperature/process mapping adapters |
| Design variables | Homogeneous composition, arbitrary layers and piecewise-linear gradient knots remain distinct from numerical grid | WP3 may vary constituent/architecture parameters under common duty |
| Settings | Tagged original `ThermalSettings`, `MappedThermalSettings`, `ThermoelasticSettings`, `CoupledThermomechanicalSettings` | New numerical domains add explicit versioned settings, not hidden defaults |
| Physics | Exact 1D cellwise steady Fourier series resistance and thermal force/moment integration for equibiaxial thin plate | 2D/3D stress, coatings and CFD require independently qualified scientific adapters |
| Numerical quality | Verified per run using 2x mesh, with separate `numerical_quality` label | Search must refuse to treat unqualified stress sampling as precise ranking |
| Evaluation | Three physical metrics, immutable spatial fields, source/method identity, hard constraint outcomes, evidence maturity and manufacturing feasibility | WP3 scalar/Pareto search should not overwrite scenario evaluations |
| Intended vs achieved | Explicit `evaluation_target`; estimated geometry evaluated from supplied state when present; missing measured geometry unsupported | WP4 supplies a bounded resolution-scenario transformer without changing WP2's evaluator |
| Storage | `RunStore` SHA256 input/result artifacts, source/dependency identity, replay and change detection | Further versions must keep v1 readers and clearly identify changed physics |
| User/decision | WP1 decisions and lineage retained | WP5 editable brief, campaign control, inspection and evidence export |

No assumptions A01–A21 were upgraded to resolved by software tests.

## Scope of comparison APIs — intentionally distinct

1. `compatible_comparison(a,b)`: only verifies that two evaluation objects
   were produced for the same *comparable physical/scientific context*.
   It does **not** certify either's numerical accuracy, feasibility or
   completeness of scientific/production evidence. It requires common
   brief hash, evidence class, solver ID/source and full context hash.
2. `Evaluation.comparison_eligible(brief)`: retains generic WP1-oriented
   feasibility checks. Corrected WP2 does **not** promote intended-only or
   estimated-unknown manufacturing states into manufacturing-feasible rankings.
3. `exploratory_numerical_eligible(e,brief)`: admits explicitly marked
   exploratory complete numerical vectors with satisfied hard bounds,
   while making **no convergence or manufacturing assertion**.
4. `numerical_comparison_eligible(e,brief)`: adds the independently
   mesh-doubling-verified `numerical_quality=qualified` requirement.
   It still does **not** imply actual manufacturing feasibility or V1 validation.

The shared context identity includes the common brief/duty/objectives/limits,
material pack/version/source hash, thermal/mechanical settings, declared
temperature domain, mesh and mapping rules, solver identity/source and
dependency versions, **full assumption snapshots**, selected target and,
where supplied, process/capability scenario and estimated-state method ID,
version and interpretation. It intentionally **excludes candidate-specific
composition and geometry** so real alternatives remain comparable, while
their own `RunInputs.content_hash` still distinguishes them.

A process route change or layer/feed capability change invalidates common
ranking even if a caller correctly updates the estimated-state process link.
An assumption's version/content change invalidates context even if brief text
looks identical. Actual achieved field content remains candidate-specific,
and *unknown* manufacturing feasibility is not silently converted to
conditional feasibility.

## Constraint design

The results layer stores one `ConstraintMetric` value for each physical
quantity, regardless of how many independent upper/lower constraints
refer to it. A separate `ConstraintOutcome` records the unique
constraint ID, relation (`le` or `ge`), original SI limit and
`satisfied/violated/unknown` outcome. Consistency of metric units is
verified within a brief and again at the immutable store boundary.
A shared objective/constraint quantity must have matching metric value
and status. A contradictory floor/ceiling is infeasible, not an exception
that blocks representing two-sided limits.

Separate result concepts:

- `status`: computed/incomplete/unsupported mathematical workflow.
- `feasibility`: outcome of *evaluated numerical constraints*,
  `conditional`, `infeasible` or `unknown`.
- `manufacturing_feasibility`: independently supplied process-state
  assessment; intended-only is `unknown` and estimated preserves
  `unknown/conditional/infeasible`.
- `evidence_status`: synthetic, provisional, supported property evidence.
- `numerical_quality`: qualified or unresolved spatial discretisation.

Those fields are not interchangeable. New consumers must not interpret
`status=complete` as a feasible manufactured material system.

## Material applicability decision

No source-provenance free-text parsing grants a supported material range.
The `Property.temperature_min` and `temperature_max` typed quantities
are explicit, individually versioned and included in immutable material
hashes and the property-pack hash. The numerical adapter requires all
necessary conductivity, density, modulus and expansion records to have
machine-checkable intervals covering hot boundary, cold boundary and
stress-free temperature. Solver settings may **narrow**, never **extend**,
the intersection. Old records without these optional fields remain
readable and retain their original canonical bytes, but fail closed for
the *corrected* v2 mapping rather than acquiring arbitrary validity.

A different broader synthetic range requires an explicitly revised
source manifest, material provenance, record bounds and resulting identity.

## Historical data semantics

All original WP1 inputs/evaluations remain byte- and SHA256-identical
through optional-field-aware serialization. The reviewed original WP2
`wp2-bounded-1` store reopens under the corrected contracts; its exact
historical input/result bytes, source hash and run interpretation are
retained. Replaying it under the new `wp2-bounded-2` solver is **rejected**.
To reproduce the v1 calculation use the original
`ae052d6f70499eceb92e73436fd0de7cb1791777` checkout and its locked
environment. New evaluations have new solver version/source, revised
material applicability and fresh immutable run/output hashes.

## Decisions W2-C01 through W2-C07

| ID | Decision | Implication |
| --- | --- | --- |
| C01 | Fix exact within-cell thermal moment while preserving original Fourier solver and stress sampling convention | Homogeneous free linear thermal profile is stress free; curvature/stress change and old outputs are superseded |
| C02 | Reinstate executable mesh assertions and register independent polynomial equilibrium integration | Passing a residual generated by the same inconsistent formula is not sufficient |
| C03 | Separate metric values from bound outcomes | Two-sided constraints, hard limits, missing values, shared objectives and durable outcomes work |
| C04 | Version full evaluation context and keep manufacturability independent | Prevents false compatibility or favourable status from unknown process conditions |
| C05 | Bind thermal applicability to each property record | No temperature-domain extension by solver settings |
| C06 | Require per-candidate mesh doubling for **qualified numerical comparison** | 128-cell gradient peak stress can be exploratory without pretending to meet sub-percent accuracy |
| C07 | D1 permits versioned assumed resolution feedback; V1 is evidence-backed | Missing measured process records do not block D1, while an assumed transform cannot be called measured validation |

## Agreed delivery handoff — Implementation Plan v2 authority

**WP3** is future inverse search and multiobjective trade-off generation; do
not start it as part of WP2 corrections.

**WP4 / D1** is an explicit versioned layer/feed-resolution capability
scenario. Transform intended composition/geometry into an *estimated*
achieved state, retain the geometry/material-accounting budget, recompute
thermal/mass/mismatch, expose new constraints and demonstrate a design
revision. Existing assumptions can be provisional and missing experiments
must **not** block D1. This implementation was **not** done during WP2.

**V1** is measured ceramic validation separately requiring compatible
command/process/achieved composition/geometry/porosity, uncertainty and
provenance. It is not delivered by a successful synthetic numerical run.

The original broader vision, specialised coating/composite applicability,
material-source governance, uncertainty and later scientific adapters are
preserved rather than silently removed.
