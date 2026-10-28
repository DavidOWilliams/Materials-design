# WP7 D1 synthetic scientific qualification and known limitations

Date: 28 October 2026. Accepted WP6 baseline implementation 1f89c2d1bf64b669ca98b81f4305d20d08104e5c. Tested WP7 application source 4fc1bc3bd07de146460be1729469c7ea1e35969c.

## What the software computes
The accepted WP2 numerical model evaluates three bounded, explicitly unit-labelled objectives for planar ceramic-like hypothetical material systems: thermal transmission (W/m²; minimise), areal mass (kg/m²; minimise), and a tensile thermal mismatch measure (Pa; minimise). It evaluates homogeneous, layered and gradient alternatives via the existing WP3 intended-state mixed-catalogue generator. Their numerical quality, hard constraint outcomes and Pareto eligibility are derived by WP2/WP3. An intended-state numerical Pareto record is not a physically or manufacturing feasible design.

The accepted WP4 workflow uses an explicitly hypothetical layer and feed-resolution process capability scenario for a gradient, maps intended to an estimated achieved-state design, reevaluates with the accepted numerical evaluator, checks a binding synthetic mass limit and performs the supported composition revision. WP4 conditional scenario feasibility is not measured physical feasibility. WP3 intended-only comparisons and WP4 estimated-state comparisons have different scientific contexts and are not pooled into one Pareto ranking.

## What is NOT established
No verified experimental ceramic grade or actual feedstock property series has been supplied for this demonstration; scenario_A/B/C are hypothetical property records. No measured achieved-state geometry, phase distribution, composition accuracy, porosity, stress, performance or uncertainty supports the D1 conclusions. No real-print validation, repeatable process-history model, CFD, mixing lag, shrinkage, sintering, drying, damage, thermal transients, interface failure or manufacturing residual stress is qualified. Tensile thermal mismatch is not the same as general 3-D residual stress. Existing method applicability, mesh and numerical reference checks apply only within their recorded domains and tolerances. Search coverage and qualified Pareto are bounded by the scripted catalogue, objective definitions, budget, seed and process scenario: no globally optimal design, general search superiority or learned P1 feedback advantage is claimed.

## Interpretation
A result may be numerically qualified while physical evidence, manufacturability and input uncertainty remain unknown. Missing/nonfinite/unqualified objectives are excluded, not silently replaced by optimistic defaults. Infeasibility is reported, not disguised as absence of materials. Observed apparent improvements reflect assumed properties, the defined mesh, constraints and scenario policy only, and may reverse with different assumed parameters.

## D1 versus V1
WP7 may be ready for independent inspection of a bounded synthetic D1 demonstrator, subject to independent Gate 3 and the original Implementation Plan v2 checklist. D1 success is not V1 measured ceramic validation, engineering qualification, certification, production release, or a reliable recommendation for an aircraft or real ceramic component. No code change in WP7 requalifies scientific physics; all original WP2/WP3/WP4 assumptions and open scientific limitations are retained.

Evidence: exact-source successful WP7 Actions run 40673439977, artifact 12808843984, ZIP SHA256 6c660389e94ed6873b4f8931f5647458159fbf2d989087a0b375e3476250b028; independently verify artifact bytes and test source before accepting scientific statements.
