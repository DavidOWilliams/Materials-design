# WP4 Vision and Product Definition requirement traceability

**Sources read:** *Material System Discovery and Design Vision v3.0*; *Material System Inverse Design — Product Definition and Delivery Pathway v1* (source tables for V01–V12 and FR01–FR12); WP4 Implementation Brief v1.0. The revised Implementation Plan v2 controls sequencing and delivery scope where Product Definition P1 gates differ. This is a bounded WP4 mapping, not certification of full P1/D1.

| Original ID | Original commitment / requirement | WP4 contract, implementation and evidence | Status / later dependency |
|---|---|---|---|
| V01 | General-purpose material systems | Typed `IntendedDesign`, `ProcessScenario`, material catalogue; no ceramics-only schema | WP4 bounded synthetic planar coupon; broad systems later |
| V02 | Inverse design and specialist discovery | Accepted WP3 `wp3_adapters`; WP4 `_revise` driven by feedback | Bounded density-guided policy, not general inverse search |
| V03 | Coating versus gradient and hybrid choice | `Homogeneous`, `Layered`, `Gradient` transformed and tested | Hybrid and coating-specific physics deferred |
| V04 | Multiple competing objectives | WP2 three-objective `Evaluation`; WP4 records raw objective vectors and mass constraint | WP3 Pareto retained; WP4 preference exploration incomplete |
| V05 | Material and gradient proposal stays central | `wp4_feedback._revise` changes constituent fractions with parent lineage | 4096-element synthetic mass-cap feedback case in CI |
| V06 | Manufacturing route and achieved state | `wp4_registry`, `wp4_resolution`, `wp4_uniform`, `wp4_bridge` | Two synthetic routes; empirical achieved-state validation later |
| V07 | CFD and coupled residual stress | Explicit excluded mechanisms; WP2 thermal mismatch distinct | CFD and manufacturing residual stress deferred |
| V08 | Multiscale specialist integration | Explicit process transformer registry and WP2 numerical identity | Other physics/scale adapters later |
| V09 | Uncertainty and evidence maturity | Process `status`, `provenance`, unresolved numerical qualification and `wp4_export` | No calibrated uncertainty/measurements |
| V10 | Human judgement and reproducibility | `wp4_feedback.save/reopen/recompute`, `wp4_journal`, draft PR | Human UI and independent Gate 3 later |
| V11 | Inspection repair and sustainability | Achieved field representation, unknown physics flagged | Lifecycle and inspection not scored |
| V12 | Research watch and explicit change | Versioned decisions and review documents | Weekly watch is separate, not a WP4 model feature |
| FR01 | Typed brief with units, bounds and confirmed assumptions | Inherited `Brief`, `Quantity`, `RunInputs`; WP4 retains unchanged duty | Confirmed physical interpretation deferred to domain review |
| FR02 | Constituent discovery with evidence and domain checks | WP2 synthetic `MaterialRecord` and applicability; WP3 provider | Real ceramic discovery deferred |
| FR03 | Generate material and spatial design alternatives | WP4 gradient revision; homogeneous/layered reference cases | General search inherited from WP3 |
| FR04 | Inverse search changes discrete and continuous variables | WP3 search engine; WP4 bounded composition revision | WP4 not a full mixed-variable optimiser |
| FR05 | Existing thermal and mechanics evaluations | `wp4_bridge.evaluate_estimated` calls qualified WP2 evaluator | Analytical independent thermal/stress audit still required |
| FR06 | Manufacturing evaluation changes a proposal or status | `wp4_feedback.run`; 4096-element qualified achieved-state mass-cap case | Synthetic feedback demonstrated, not measured |
| FR07 | At least three physical/engineering objectives | `thermal_transmission`, `areal_mass`, `tensile_thermal_mismatch` | WP2 scientific applicability applies |
| FR08 | Pareto set plus explicit preference exploration | Accepted WP3 Pareto; WP4 `wp4_comparisons` | WP4 preference/Pareto challenge incomplete |
| FR09 | Unknown, failed, infeasible and feasible remain distinct | `numerical_comparison_eligible`, conditional feasibility, terminal-state checks | Global manufacturability unknown |
| FR10 | Versioned sources, models, candidate parents and runs | `wp4_registry`, `wp4_journal`, `wp4_feedback.reopen/recompute` | Authenticated immutable external manifest absent |
| FR11 | Explain rejection, empty results and binding limits | Feedback metrics, signed balances, explicit stopping reasons | Detailed UX explanations deferred |
| FR12 | Export brief, alternatives, evidence and decision | `wp4_export.export` and complete JSON dossier | Independent Gate 3 reproduction pending |

The original identifiers and wording come from Product Definition v1's Vision-commitment and functional-requirements tables. This crosswalk does not silently promote deferred P1/P2/P3/P4/P5 requirements into WP4 acceptance.
