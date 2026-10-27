# P1 post-confirmatory implementation-team audit (not independent Gate 3)

Date: 27 October 2026. Source tested `6eb62daec638185f5c5dc170182e9e0454b6e061`, GitHub Actions run 40483551395. **Post-outcome supplementary audit; not preregistration, not external peer review and not a new scientific result.** Raw trial/score artifacts and SHA256 manifests remain unchanged under `foundation/p1/evidence/confirmed-source-6eb62da/`.

## Independent-algorithm hypervolume cross-check
Downloaded the exact GitHub Actions artifact to an isolated local evidence directory and verified all **404** entries in its original SHA256 manifest: **zero mismatches**.

Recomputed feasible 3D hypervolume for each of the 160 arm results using a separate inclusion-exclusion union-of-cuboids calculation, rather than the experiment's sorted 3D sweep algorithm. For every nonempty subset of the arm's up-to-four feasible objective vectors, calculate its intersection box volume relative to the frozen reference and alternately add/subtract by subset cardinality. Across **160/160** arm-level HV results the absolute disagreement was <1e-9.

The pooled mean reconstructed feedback-minus-control normalized HV difference was **+0.0140697337963**, matching the archived confirmatory estimate. This is an implementation-team verification of analysis arithmetic, not an independent scientific opinion.

## Critical heterogeneity and feasibility saturation
Of 80 paired trials, **six** had positive equal-numerical-work HV differences, **zero** were negative and **74** were exactly zero. Nonzero cases:
- sampling, feed 0.25: seeds 2001, 2010, 2015;
- sampling, feed 0.50: seeds 2001, 2015, 2017.
Both structured-exploration strata had 20/20 zero differences.

**All 80/80 pairs in each arm achieved at least one numerically qualified conditional-feasible design**; trial-level feasibility therefore saturated at 100% for both treatments. The feasibility-rate difference of zero does not establish that feedback is ineffective under harder constraints. Across all 80 pairs, blind had 125 feasible candidate records and feedback 126, but raw candidate counts are secondary and not the preregistered trial-level primary endpoint.

Exactly **320 proposed candidate slots per arm**, with equality of WP4 manufacturing and WP2 numerical calls in every pair. Across both arms, no numerical evaluations failed and cache hits were zero by design. Four-slot per-arm mean measured process CPU time in the archived environment was approximately 109.44 ms blind and 111.63 ms feedback; this is descriptive and not an independent CPU-time replication.

## Interpretation and unresolved scientific objections
The equal-work gain is sparse, concentrated entirely within sampling, and lower than the prespecified practical threshold +0.02. The mean 80ms CPU-budget result is negative. A synthetic feedback implementation may systematically favour designs under its own process model; within-family feed-resolution heldout scoring is not independent external validation.

The implementation plus existing tests does NOT fully establish per-candidate mid-trial recovery after forced process termination, a general identity negative control across heterogeneous designs, performance under a truly infeasible confirmatory scenario, or physical model independence. These are candidate Gate 1/2 findings for a separate reviewer; do not silently claim closure.

**Reviewer instruction:** reproduce these calculations independently using raw saved objects; do not accept this audit as Gate 3 sign-off.
