# WP3 vision traceability — implementation and limitations

Updated 24 October 2026. Applicable authorities: Vision v3, Product Definition v1, Implementation Plan v2, WP3 takeover v1.0; corrected WP2 ancestor `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`. This is a bounded synthetic planar-coupon work package, **not a reduction of the enduring Materials Design Platform vision**.

| Vision section | WP3 implementation and behavioural evidence | Preserved future scope |
| --- | --- | --- |
| 1–2 whole material system and inverse design | `contracts.py` keeps Brief, IntendedDesign, Evaluation distinct; `wp3_provider.py` searches synthetic A/B/C subsets and homogeneous/layered/continuous gradient architectures; `test_wp3_provider.py`, `test_wp3_search.py` | Richer compositions, coatings, composites, geometry families, route selection and measured results |
| 3 specialist discovery | Explicit `BoundedProvider` with versioned synthetic catalogue and provenance; injectable provider factory and contract test double | Literature/databases, MatterGen, AtomGPT and other scientifically qualified adapters |
| 4, 6 architecture and evaluation | Existing WP2 adapter, common synthetic property pack, WP2 numerical status and applicability; provider changes constituents, fractions, layer boundary and gradient knot position | Replaceable specialist solvers, spatial scale and coating/hybrid architecture |
| 5, 7, 8 manufacturing/evaluation loops | WP2 separates intended and externally supplied estimated achieved states; campaign ranks numerical-only results while manufacturing stays unknown for intended state | WP4 versioned process-resolution feedback, CFD and supported process-history residual stress models |
| 9, 11 multiobjective decisions | `wp3_pareto.py` accepts objective IDs/directions generically; `wp3_qualified.py` derives WP2 numerical eligibility; no hidden preference weight. Three raw supported objectives are flux, mass and sampled tensile thermal mismatch | Cost, lifecycle sustainability, inspectability, repair and preference exploration under defensible units/evidence |
| 10, 12 evidence, control and uncertainty | `wp3_search.py` records seeded search, versioned config digest, parent lineage, evaluation hashes, qualified comparison, failed/cancelled work, solve-accounting and paired baseline; `RunStore` and `recompute_search` replay | Experimentally measured feedback, broader evidence systems and decision-value prioritisation |

## Verification boundaries

- The numerical example records **mid_fraction=0.35** as mass-infeasible and **0.65** as constraint-satisfying and numerically qualified under its declared WP2 mesh. Both remain manufacturing-unknown in intended-only execution.
- An independent baseline retains the corrected thermal eigenstrain moment integral and mesh-doubling requirements. No new scientific constitutive law, predictor training or material calibration is introduced.
- The generic campaign can inject a different proposal provider and evaluator test double, but this demonstrates *software modularity only*, not evidence for a new scientific model.
- `WP3_ACCEPTANCE_LEDGER.md` and `WP3_REVIEW_PACKAGE.md` are the acceptance and review records. **Gate 3 is not passed** absent independent scientific/architecture review. CI self-testing does not approve WP3, nor complete D1, WP4/5 or measured V1.
