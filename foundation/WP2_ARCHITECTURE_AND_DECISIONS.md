# WP2 architecture and decision extension

23 October 2026 | Extends, does not overwrite, WP1's `ARCHITECTURE.md`
and `DECISIONS.md`.

## Design boundaries and extension map

| Boundary | WP2 implementation | Next adapter or package |
| --- | --- | --- |
| Shared immutable brief/candidate/material/run | Existing strict WP1 `contracts.py`, no fixed number of constituents or objectives | WP3 proposal/search and Pareto |
| Objective results versus hard constraints | `Metric` and independent `ConstraintMetric` | All optimisation campaigns; no constraint-as-objective hack |
| Numeric settings and applicability | `ThermalSettings` (original WP1), new `MappedThermalSettings`, `ThermoelasticSettings`, `CoupledThermomechanicalSettings` | New typed solvers, not arbitrary common dict fields |
| Design and numerical mesh | `Homogeneous`, arbitrary `Layered`, `Gradient` knots separately from mesh-cell discretisation | Coatings, 2D/3D, composite and interfaces via specialist representations |
| Property packs | `MaterialRecord.properties` with independent source, state, unit and uncertainty; strict synthetic scenario map and hashed pack | Process-matched experimental ceramic packs; temperature/porosity functions |
| Evaluation kernels | `wp2_kernel.py` exact cellwise steady series conduction and bending-aware classical laminate equilibrium | Replaceable FE for nonplanar and nonlinear/anisotropic cases; CFD remains separate |
| Integrated adapter | `wp2_numerical.py` maps achieved/intended spatial geometry into cells and returns three metrics plus raw fields | WP3 search controller, WP4 manufacturing state transform |
| Target/identity | Existing `RunInputs.evaluation_target`, full immutable inputs, source and scenario hashes plus `comparison_context_hash` | Measured-state geometry adapter and cross-scenario comparison |
| Persistent artifacts | Existing `RunStore` SQLite & SHA256 JSON; new mapped metadata validated at store boundary | Worker management, export and multiple-user governance |
| Human decision loop | Existing `DecisionRecord` with no search or UI implementation | WP3–WP5 |
| Broader vision | Coatings, composite/hybrids, microstructure, specialist discovery, repair, lifetime, sustainability are **not removed from scope** | Later programme, each behind explicit scientific domain adapters |

The `RunInputs.settings` union is discriminated by `kind`. Existing v1
thermal and Evaluation artifacts are loaded with their original schema and
canonical bytes; optional new result fields are omitted from canonical
serialization when absent. This is a **backward-compatible v1 additive
contract**, not an unrestricted migration of historic artifacts. Future
breaking semantics must introduce an explicit new version and a retained
v1 reader. WP1's recovered Fourier solver remains installed and reproducible
separately from the new mapped adapter; reading artifacts and replaying
historic code are tested independently.

## Recorded decisions

| Decision | Choice | Trade-off and preserved limitation |
| --- | --- | --- |
| W2-D01 | Correct R1 by adding constraint metric records rather than forcing mass into objectives | Status and unit checks independent; comparison eligibility never silently passes unknowns |
| W2-D02 | Use typed mechanics/coupled settings and spatial fields | Stable generic envelope; v1 bytes preserved; FE/CFD remain replaceable future tools |
| W2-D03 | Adopt steady planar series resistance and thin equibiaxial CLT | Existing documented physics on CPU with independent references; excludes arbitrary geometry, nonlinear response, interfaces and process residual stresses |
| W2-D04 | Allow free bending for asymmetric layers | Solves thermal force and moment equilibrium, rather than recovered scalar laminate shortcut |
| W2-D05 | Evaluate **absolute** transmission and preserve raw signed heat flux | Avoids ranking reversed temperature scenarios as favourable low negative flux |
| W2-D06 | Use neutral synthetic constituent properties and explicit distinct mixture relations | D1 functional scope without invented ceramic validation; real G0/V1 evidence remains open |
| W2-D07 | Restrict to common duty, temperature domain, property evidence, mesh/settings, material budget and target identity | Different physical scenarios may appear side-by-side, but cannot silently share a Pareto ranking |
| W2-D08 | Keep intended, estimated and measured targets semantically separate | Supplied estimated geometry is actually evaluated, and unknown measured geometry is not replaced with intended |
| W2-D09 | Retain A01–A15 unchanged; append A16–A21 | WP2 scenario enablement does not scientifically resolve original questions |
| W2-D10 | Do not change legacy selection/filter/reranking source or merge PR | Protects existing product and preserves independent verification history |

## Scientific and engineering limitations

The mesh solver's fields and three objective vectors are **numerical
scenario estimates** only. There is no ceramic process-matched conductivity,
stiffness, thermal expansion or density evidence pack in WP2. A
fully-qualified ceramic material system may require independent models for
phase compatibility, interface fracture, anisotropy, sintering, creep,
relaxation and residual stresses. Unknowns remain unresolved rather than
generated as optimistic numbers. WP2 does not implement Pareto search,
manufacturing feedback or the expert user workflow.
