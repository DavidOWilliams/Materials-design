# WP4 architecture and bounded decisions

## Lifecycle
Typed intended baseline (unchanged WP2/WP3 contract) → explicit versioned synthetic process scenario → registered transform → manufacturing commands and **estimated** achieved geometry → WP2 evaluation under the same brief, solver and property pack → feedback-driven intended constituent revision → repeat until supported stop condition.

The two registered synthetic process routes are ideal layer-resolved deposition and ideal uniform-batch deposition. Neither models ceramic manufacturing physics. The revision policy is the explicit `wp4-density-guided-revision-v1`; numerical evaluation is identified as `wp2-numerical-evaluate-v1`. Unknown implementation identities are rejected. Alternate duty uses the accepted WP3 typed provider baseline; generic orchestration does not silently construct default duty during continuation.

## Persistence and recovery
An immutable manifest freezes configuration, baseline, process and identities before execution. A chained candidate checkpoint journal and fsynced attempt-event sidecar distinguish transform and numerical evaluation starts/completions/failures. Resume validates source identity and configuration before appending, reuses completed numerical work and records cumulative actual numerical work. A separate `recompute` operation deliberately consumes additional verification solves. Legacy journals without sufficient manifest/event history cannot claim exact continuation and are rejected.

Reopening validates campaign schema, baseline/evaluation hashes, first-candidate lineage, configuration, feasibility and stopping causality. Checksums detect accidental corruption, **not authenticated adversarial forgery**. No multi-writer concurrency or solver-kernel restart is provided.

## Evidence boundary
Intended design is a proposal; estimated achieved state is a synthetic process projection; measured evidence is absent. A conditionally scenario-feasible result is not experimentally manufacturable. No new physics, no WP5, no PR merge.

## Review state
Independent Gate 3 has **been performed and returned changes required**. This correction submission awaits independent closure; no implementation self-approval.
