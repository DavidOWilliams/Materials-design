# WP4 independent Gate 3 review — changes required; corrective submission

An independent reviewer **has performed Gate 3 review** of earlier WP4 commits and identified five areas needing correction. That review did not approve WP4. The corrected branch must be reviewed again; implementation authors cannot independently close findings.

## Findings and review evidence
- R1: Reopen the forged schema=999, no-improvement, baseline-input-hash, feedback-disabled and resolution-mismatch dossiers; all must fail without relying on numerical recomputation.
- R2: Independently count evaluator calls before/after interruption and confirm durable completed work is reused; inspect event sidecar, manifest, checkpoint and cumulative counters; reject legacy incomplete history.
- R3: Confirm exported baseline hash is canonical content hash and changes with design content even when readable ID does not.
- R4: Interrupt and resume alternate duty, preserving original WP3 380/320 K baseline, property pack and numerical settings; reject unavailable transform, evaluator and revision identities.
- R5: Cross-check each F01–F12/C01–C12 row against the exact tested checkout and archived logs, and resolve any outstanding limitations.

## Handover
Freeze source SHA and actual CI checkout SHA; record workflow IDs, artifact SHA, reviewer identity, independent methods, finding dispositions and any new failures. Historical test evidence is not proof for a later source revision. Do not merge PR #4 or begin WP5.

**Scope:** bounded synthetic software and numerical qualification only. No measured ceramic evidence, physical manufacturability or manufacturing residual-stress claim.
