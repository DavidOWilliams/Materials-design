# P1 independent Gate 3 — supplementary verification, 2026-10-27

**Disposition: NOT ACCEPTED; verification incomplete.** This document is an independent, documentation-only review, not a modification of tested source or confirmatory evidence.

## Identifiers and access
- Tested P1 implementation: `6eb62daec638185f5c5dc170182e9e0454b6e061`
- Accepted WP5 baseline: `4078a83dc11e14703ff6cc03f5b62f4e48879d14`
- Protocol SHA256 asserted: `f874daae784fbba693ec44f856bb904d1ff4a2b06ca97ca59c10275dc75166f0` (not independently hash-verified).
- CI run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40483551395 (not independently executed).
- PR #9: https://github.com/DavidOWilliams/Materials-design/pull/9

GitHub connector successfully retrieved the frozen protocol and configuration at the tested commit. The connector retrieved the preserved paired summary, full 404-line SHA256 manifest, and four individual arm records from the P1 evidence branch. Local `git ls-remote` failed with `Could not resolve host: github.com`. No independent source checkout, test run, or full-file SHA256 verification was achieved.

## Independent findings

1. Earlier reviewer independently recalculated from the 80 paired summary entries: mean normalized feasible-HV delta +0.014069733796296294; 6 positive, 74 unchanged, 0 negative; 80/80 summary parity flags for four numerical evaluations and four transformations per arm; mean 80-ms CPU-prefix delta -0.0017288773148148146. **These are summary-level, not full raw-arm verification.**
2. Current reviewer verified the original manifest is present and contains 404 SHA256 entries; presence is not integrity verification. Retrieved `all_paired_trials.json` (201,217 characters) and inspected four raw arm records: sampling/feed 0.25/seeds 2001 and 2002, blind and feedback.
3. Seed 2001: blind qualified candidate objective vectors include (thermal 60000, mass 30, mismatch ~1.40946e-8) twice; feedback adds (thermal 40000, mass 25, mismatch ~1.24683e-8), marked `revision_applied=true` at candidate index 2. The raw records support a better feasible objective vector in this one pair. The summary reports blind HV 0.16666666666666669 and feedback HV 0.2962962962962963; these figures have **not** been independently recomputed from a validated scorer.
4. Seed 2002: both arms have a qualified (thermal 60000, mass 30, mismatch ~1.40946e-8) candidate; other records are marked unqualified. This supports unchanged qualified candidate performance in that inspected pair.
5. In the seed 2001 arm records, blind has four proposals, four transformations, four numerical evaluations and zero feedback calculations; feedback has the same work counts and four feedback calculations. Raw counters support equal **counts** in this pair, not identical CPU consumption or universal parity.
6. Mismatch objective values near 1e-8 occur for some qualified candidates, while some unqualified candidates show mismatch in the millions. This scale separation warrants a numerical/scoring diagnostic; it does not alone establish a defect.
7. A full 160-arm retrieval/reconstruction attempt exceeded the connector's per-script tool-call limit. The attempted batch did **not** complete and generated no independently verified aggregate result.

## Scientific limits and gates

- **Gate 1: CONDITIONAL PASS**, evidence and frozen protocol accessible; execution, source environment and complete SHA256 checks outstanding.
- **Gate 2: FAIL TO CLOSE**, comparator implementation and negative-control/challenge tests not independently executed.
- **Gate 3: FAIL TO CLOSE**, full raw-arm HV and bootstrap reproduction, integrity audit and independent CI execution outstanding.

Claims: A harness reproducibility **INCONCLUSIVE**; B equal audited numerical work **INCONCLUSIVE**; C feedback-specific synthetic HV improvement **INCONCLUSIVE** (positive archived summary, limited raw examples); D practical importance **UNSUPPORTED** (pooled mean 0.01407 below threshold 0.02); E equal-CPU efficiency improvement **UNSUPPORTED** by reported negative CPU-prefix mean, instrumentation unverified; F general feedback benefit **UNSUPPORTED**; G physical ceramic benefit **UNSUPPORTED**.

## Required closure

- F1 (HIGH, verification): retrieve and execute the tested source and existing regression/focused tests; archive commands, environment and results. Original confirmatory evidence remains intact; no automatic rerun required.
- F2 (HIGH, integrity): verify every original and expanded manifest entry and all 160 arm records. No existing-evidence invalidity demonstrated.
- F3 (HIGH, scoring): independent candidate-level normalized feasible 3D HV, bootstrap with 2000 prespecified resamples, 80-ms CPU prefix and scenario curves. No rerun merely to improve effect.
- F4 (HIGH, identification): inspect proposal generation, feedback revision, caching, eligibility and stop policies in tested code. If policy confounding is found, narrow causal claim and prospectively design new experiment.
- F5 (MEDIUM, runtime): audit timing measurement and repeatability; do not claim efficiency without independent support.
- F6 (MEDIUM, robustness): execute separate failure, no-feasible, cache, recovery, corruption and identity-feedback challenges.

**Recommendation:** withhold P1 acceptance; retain the original 80-pair synthetic result without altering it. Do not initiate a new confirmatory trial solely because the observed effect is modest. Do not merge the independent review or implementation PR without explicit authorization.
