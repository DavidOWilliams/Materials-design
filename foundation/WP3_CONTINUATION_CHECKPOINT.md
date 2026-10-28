# WP3 continuation checkpoint — updated implementation state, 24 October 2026

This document supersedes its original early-vertical-slice snapshot. The branch `wp3-inverse-search-2026-10-24` and draft PR #3 are retained, with the corrected WP2 baseline `7009189d9be4dfd5940999c88cbb5c3c70c8ce56` unchanged. No merge or WP4 start.

## Implemented WP3 capability

- `wp3_provider.py`: bounded synthetic A/B/C common catalogue, homogeneous, discrete layers and continuously defined gradients; vary constituent pair, layer boundary, composition and gradient knot position. These are hypothetical numerical properties, not engineering ceramic evidence.
- `wp3_qualified.py`, `wp3_pareto.py`: conservative WP2-derived qualified numerical eligibility, common context, deterministic nondominated output. Manufacturing feasibility and evidence maturity remain distinct.
- `wp3_search.py`: bounded seeded mixed search, parent lineage, immutable run links, reasoned exclusions, explicit resource counters, cancellation, append-only resume, integrity-checked open and numerical recomputation. Alternate provider and evaluator contract injections are version-labelled software test fixtures.
- Separate `explore` and `sampling` campaigns with shared start and 11/23/37 paired seeds, isolated stores, fixed evaluation limits, and honest portfolio coverage metrics without assumed superiority.
- CI jobs: locked foundation + recovered WP0 regressions, original corrected WP2 verifier, single-run and mixed-campaign replay/recomputation, paired comparison and independent legacy-environment regression. CI is execution evidence, not independent engineering approval.

## Required review sources

- `foundation/WP3_ACCEPTANCE_LEDGER.md` — F01–F10 and C01–C10 mapped to test and limitation.
- `foundation/WP3_VISION_TRACEABILITY.md` — actual module mapping and retained full platform vision.
- `foundation/WP3_REVIEW_PACKAGE.md` — independent numerical, Pareto, architecture and completion review request.
- `foundation/WP3_USAGE.md` — fresh setup, commands, replay and recovery contracts.
- Workflow: `.github/workflows/wp3-verification.yml`.

## Remaining gate

Gate 3 is **pending genuinely independent reviewer assignment and sign-off**. GitHub Actions/implementation-owned tests are not independent approval. Scientific limitations remain synthetic property pack, planar idealisation, no validated manufacturing process, no full residual stress/fracture/lifetime and no V1 measurement. D1 and WP4/5 are not claimed.

## Publication integrity

For final review record the current branch SHA and final-head full two-job CI run, job logs and artifact IDs. These must be inspected after any later documentation updates. A historical green run does not qualify a newer SHA.

## Independent review R1–R4 corrective continuation (24 October 2026)

The review of `d62023d7205d48beba11269d4c358a7380ab9ca4` found four problems *after* the previous 185-test success. All four were reproduced without changing the reviewed historical source using `foundation/reproduce_reviewed_wp3_r1_r4.py` in a pinned Actions checkout. The updated WP3 source now retires the unvalidated schema-1 campaign API (historical labelled reader only), validates completed evidence during an unrelated pending recovery, validates campaign stop reasons and terminal events, and delegates scenario-specific proposal construction, validation and objective/constraint/brief identity to versioned adapters. The alternate provider uses 380/320 K and a variable three-layer synthetic two-phase design; the main provider retains the original A/B/C catalogue. Both reuse corrected WP2 and preserve intended-only manufacturing unknown.

Supported executable campaign entry point: `python -m material_core.wp3_search`. The `wp3_campaign` command without `--legacy-read-unvalidated` is deliberately rejected; old schema-1 artifacts cannot meet current qualification assurances and are not rewritten. The `explore` policy is structured seeded sampling, not evaluation-driven adaptive optimisation. Any unregistered evaluator cannot be silently substituted during independent numerical recomputation.

Evidence and explicit correction status: `foundation/WP3_R1_R4_CORRECTION_RECORD.md`, `WP3_ACCEPTANCE_LEDGER.md`, `WP3_REVIEW_PACKAGE.md`, `WP3_USAGE.md`, `WP3_VISION_TRACEABILITY.md`, workflow `.github/workflows/wp3-verification.yml`. Record the exact corrected commit, checkout merge/branch identities, workflow jobs and run-store artifact IDs after the final full CI. Gate 3 remains pending independent re-review. No merge or WP4 work.
