# WP5 independent Gate 3 reviewer package — D1 bounded demonstration

**Review status:** awaiting independent reviewer; NOT independently accepted.
**Exact tested WP5 implementation commit:** `0c93ea2c91f2f6f0d29f0024d12722db9cf6931f`.
**Tested PR merge checkout:** `24a5d8d9f8e2b6aedecbb8cbd13c2c65e3cea94d`, base `f3e6cfc7f7e9ed885ce681814c0927fc421163c8`.
**Documentation/workflow commits after implementation:** tracked separately. Do not conflate with tested implementation.
**Draft PR:** https://github.com/DavidOWilliams/Materials-design/pull/6

## Verification evidence

- [WP4 qualification and WP5 browser CI run 40311326597](https://github.com/DavidOWilliams/Materials-design/actions/runs/40311326597) — success; 85 WP4 focused, 32 WP5 focused/widget tests, 323 full foundation tests; numerical reopen/recompute and review reproduction checks passed.
- [Source-pinned live Chromium browser artifact](https://github.com/DavidOWilliams/Materials-design/actions/runs/40311326597/artifacts/12644319171) — screenshot, persisted numerical dossier and environment freeze; live Streamlit UI launched, selected version 2 process scenario, executed campaign, inspected and numerically replayed dossier.
- [WP4 qualification dossier archive](https://github.com/DavidOWilliams/Materials-design/actions/runs/40311326597/artifacts/12644563653) — WP4 evidence and review reproductions.
- [Earlier passing CI 40310714682](https://github.com/DavidOWilliams/Materials-design/actions/runs/40310714682) — 85 WP4, 28 WP5, 319 foundation; not final implementation SHA.
- WP3 run 40311326479: three jobs success, one failed **at collection** because its environment did not install optional Streamlit required by WP5 UI tests. Workflow-only correction `b8a8744d2f80e1eed737e241f1825621a0860638` isolates the optional UI test from WP3's locked core-only environment; check rerun 40311898870 before closure.

## Gate 1 — functional acceptance assessment

Evidence supports bounded complete lifecycle: typed brief editing and immutable save, saved brief bound to numerical WP4 campaign, process version stored in evaluated process identity, numerical evaluations and persisted dossier, inspection, portable import, reopen and numerical replay. Streamlit AppTest covers the saved-brief lifecycle and import; real Chromium covers campaign execution, inspection and replay.

**Assessment:** Gate 1 functional D1 requirements supported by tests at exact source above. This is not empirical manufacturing validation.

## Gate 2 — challenge assessment

- Positive variants: original and revised process scenario versions, different layer resolution, saved brief revisions, supported synthetic routes.
- Negative contract/unsupported changes: invalid budgets, unsupported geometry and scientific edits, incompatible comparisons, corrupt manifests, forged imports, stale process-version dossier identity.
- Feasibility: explicit no-feasible-candidate challenge, unknown measured evidence remains null and manufacturing validation not established.
- Durability: cancellation before candidate, cancellation after one completed candidate, append-only journal inspection, recovery and checkpoint reuse, attempted duplicate overwrite rejection; WP4 interruption, failed transforms, failed numerical evaluations, write-failure and repeated recovery tests.
- Replay: WP4 numerical recomputation and versioned dossier replay; hash tampering fails closed.
- **Assessment:** source-level and widget challenge evidence supports Gate 2 for the bounded D1 functionality. Mid-solver interruption/restart, truly asynchronous user-initiated stop during a running solver, and measured physical validation are excluded; cancellation is at candidate boundaries with a user-selected threshold. No claim of coverage beyond the listed tests.

## Scientific boundary

Synthetic intended design, estimated achieved state and measured evidence are distinct. No measured achieved-state ceramic evidence is available; unknown remains unknown. Process version records declared assumption identity, not new empirical calibration. D1 is a bounded synthetic demonstration, not V1 validated ceramic capability. No new scientific model was introduced.

## Independent reviewer tasks

1. Independently fetch tested implementation SHA and verify checkout/PR merge provenance; do not substitute documentation HEAD.
2. Reproduce focused, foundation, WP3/WP4 regressions and live browser flow in fresh environment; check exact artifact hashes and replay.
3. Challenge saved-brief binding, unsupported scientific edits, changed process version, unknown evidence, no feasible candidate, stale/corrupt dossiers and comparisons.
4. Verify journal interruption/recovery accounting, immutability and distinction between cancellation at candidate boundaries and a live kill.
5. Check no claims of measured manufacturing validation or unsupported FE/CFD physics; explicitly decide Gate 3 with independent evidence.

## Immutable WP4 baselines (do not move)

- Tested implementation: `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b`
- Acceptance documentation: `1805811acdafacd66ba3574e8cb45c59bebdd8e5`
- Evidence preservation: `bb67e51029c5479361c59cea0b73b6bb722826f1`

No merge, force push, or baseline movement is authorised.
