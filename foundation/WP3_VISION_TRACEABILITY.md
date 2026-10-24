# WP3 vision traceability — initial implementation record

Status: **pre-implementation; no WP3 acceptance gates passed**. Prepared 24 October 2026 from the Vision v3, Product Definition v1, Implementation Plan v2 and WP3 brief v1.3. Branch based on corrected WP2 commit `7009189d9be4dfd5940999c88cbb5c3c70c8ce56`. This document records obligations, not delivered code.

| Vision section | WP3 contract / required behavioural verification | Deferred integration |
| --- | --- | --- |
| 1–2 material system and inverse design | Separate Brief, IntendedDesign, Evaluation; generate new constituent and architecture proposals; test changed brief and lineage | Other material families and spatial geometries |
| 3 specialist discovery | Pluggable proposal provider with recorded catalogue identity; alternative provider test double | Literature and pretrained discovery providers (MatterGen, AtomGPT) |
| 4, 6 architectures and evaluation | Homogeneous, layered, continuously defined gradient; evaluator contract with objective IDs, units, directions, applicability and evidence | Coatings, multiscale and coupled physics |
| 5, 7, 8 manufacturing and achieved state | Distinguish intended, estimated and measured state; evaluation-target contract and redesign hook; reject absent achieved state | WP4 process transform, CFD, residual stress history |
| 9, 11 multiobjective and lifecycle | Generic constraint and Pareto service, no hardcoded objective ordering; preference distinct from nondominance | Cost, sustainability, service-life objectives with validated functional units |
| 10, 12 evidence and control | Immutable campaign provenance, failures, unknowns, hashes, budget and cancellation; replay checks | Measured validation, next-evidence prioritisation |

## Non-negotiable acceptance

F01–F10, C01–C10 and separate independent-review checks in WP3 brief v1.3 must be executed against a single final source revision, with machine-readable evidence and resolved blocking findings. Historical WP2 tests are not fresh WP3 results. A green CI run does not constitute independent review. Do not infer D1, V1, real ceramic validation, or manufacturability from WP3.

## Source precedence

Current user instructions > Vision v3 (enduring scope) > Product Definition v1 (compatible requirements) > Implementation Plan v2 (delivery sequence and D1/V1 split) > WP3 brief v1.3 (WP3 acceptance). Legacy aviation selection logic is historical only.

## Current limitations

No WP3 implementation, tests, campaign examples, qualified numerical results, separate reviewer, or independent approval are evidenced by this initial record. The implementation must still inspect live repository contracts and AGENTS.md, reproduce WP2 qualification, and satisfy all gates.
