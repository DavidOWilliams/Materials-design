# D1 v0.2.0 — Publication approval package (prepared; not tagged or published)

**Publication classification:** bounded **internal synthetic demonstration**, *not* certified, experimentally validated, or production-ready engineering software. D1 v0.2 integrates visual/presentation usability and integrity improvements without introducing new physics or validated ceramic manufacturing capability.

## Precise immutable release target (must be reconfirmed before authorisation)

- Proposed annotated tag: **`d1-v0.2.0`**.
- **Target commit:** `280e21e3df62a6e2fcbf5bf4668b6b235ccd8384`.
- **Target complete Git tree:** `60d0ef541dfe9d2dd38860308d1524206f09c5f5`.
- Accepted corrected application provenance: `8ba23e859e920bcd7dbf19b87f2f07ddeeb4c62a`, tree `84513ca9aaa2d923bb3e3ff7a333eb8c131f9a93`.
- Owner-authorised integration PR #24 merged into main at the target commit, whose full tree equals the independently qualified pre-merge PR tree. Original `d1-v0.1.0` tag retains its historical target `ec4bea044858bc275a1be80c3df24be438085279` and must not move.
- **The proposed tag has not been created or moved; no GitHub Release has been published and no application has been deployed.** PR #30 workflow maintenance is a different, later commit; publishing this documented tested commit does not imply that PR #30's workflow change is included in the tagged source. If the programme owner instead wants PR #30 included in a tagged source, a new integration commit, source/tree identity and necessary verification are required before updating this package.

## Provenance and evidence

- Original D1 v0.2 independent scientific-presentation acceptance [PR #23](https://github.com/DavidOWilliams/Materials-design/pull/23) — Gates 1 PASS bounded, 2 PASS, 3 PASS bounded; old BLOCKED decision preserved in historical addendum.
- Recovery correction Issue #25 accepted [PR #28](https://github.com/DavidOWilliams/Materials-design/pull/28) — R1–R5 PASS; D1-V02-IR25-01 CLOSED; rejected corrupt `*.handoff.json`, removed stale green notice, provided warning, did not restore stale green when bytes reappeared, fresh browser reopen/replay and immutability passed. Independent run [41089182257](https://github.com/DavidOWilliams/Materials-design/actions/runs/41089182257), archive **12993441777**, ZIP SHA256 `3edfd431602a3bb8aecd130cbba541d095ce02a572000577f5e4f9c5aeb4b635`, internal **39/39** checked. Corrected author run [41082638967](https://github.com/DavidOWilliams/Materials-design/actions/runs/41082638967), archive **12991415168**, ZIP SHA256 `460b147a560e1491d3501a18a3e2b23eedc17d2b931e5f666282ab2747cde48c`, internal **161/161** checked.
- Pre-merge actual PR #24 HEAD `4e72b327a6e48394d2b3870d3a84c641bd997e98`, accepted v0.2 implementation files and tests byte-identical. Exact-head [run 41096182000](https://github.com/DavidOWilliams/Materials-design/actions/runs/41096182000) SUCCESS, artifact **12997465218**, ZIP SHA256 `f1e03705ee8df9b12571ff8b53472354935dc51752dac428adbe009097103e1f`, internal **168/168**; 339 foundation, isolated UI, v0.1 comparison, WP3/WP4 4096-element examples, three separate-process replays and real Chromium recovery/companion corruption passed. WP3 [41096182131](https://github.com/DavidOWilliams/Materials-design/actions/runs/41096182131) all four jobs green (359 passed, two skipped); WP4 [41096182058](https://github.com/DavidOWilliams/Materials-design/actions/runs/41096182058) SUCCESS; WP7 [41096182256](https://github.com/DavidOWilliams/Materials-design/actions/runs/41096182256) SUCCESS; D1 UI [41096181982](https://github.com/DavidOWilliams/Materials-design/actions/runs/41096181982) SUCCESS (339 foundation and nine UI).
- **Actual merged-main qualification:** audit [run 41099626877](https://github.com/DavidOWilliams/Materials-design/actions/runs/41099626877), workflow-audit branch source `89ff8fb0a17669db0207d85ad3a3e33086409dfd`, explicitly checked out detached **tested source `280e21e3df62a6e2fcbf5bf4668b6b235ccd8384`**, exact tree `60d0ef...`. Job **SUCCESS**, including clean Python 3.12, scientific/regression/UI tests, identical v0.1 numerical comparison, 4096-element WP3/WP4 dossiers, separate-process replay, real Chromium first-user and recovery integrity. Artifact **12998706707**, ZIP SHA256 `eb0d47e5509dd1d0be637fe30ada6fe3f3cc7eed9a38a3f3045bb53d85722fec`, **169/169** internal SHA256 entries independently verified. Audit workflow SHA is not the app SHA.
- Preserve source-specific ZIPs beyond GitHub artifact retention (currently 90 days per workflow) in programme-controlled archival storage with SHA256SUMS. Do not claim historic negative reviewer/CI runs passed retrospectively.

## Supported bounded demonstration

WP3 presents homogeneous/layered/gradient **synthetic intended-state** proposals and trade-offs with exact source coordinates, compositions and numerical qualification/eligibility. WP4 provides strictly compatible A/B gradients with **synthetic estimated-achieved-state** layer/feed and mass feedback. They are distinct evaluation/Pareto contexts: never pool WP3 and WP4 Pareto. Missing, nonfinite, unsupported or unresolved results remain unknown/unavailable; no invented measured overlay. Cooperative cancellation is only between candidates, not mid-solver. Immutable dossier and checkpoint replay supported.

**Critical portability condition:** a WP4 dossier `*.json` plus its `*.handoff.json` is **not a standalone relocatable combined bundle**: retain corresponding original WP3 workspace/ledger/run-store and hash-addressed artifacts or a verified complete WP3 ZIP. Validate lineage and replay after restoration.

## Scientific claims explicitly excluded

No measured ceramic composition/geometry/porosity/process outcomes; no experimentally validated manufacturing, full sintering/stress/simulation physics, generalised inverse-design superiority, outside-dataset benchmark qualification, aviation/airworthiness certification or production engineering readiness. P1/P2/P3, E1/E2, V1 separate. Numerical synthetic feasibility is conditional on assumptions, not real-world manufacturing readiness.

## Residual findings and publication gate

- [Issue #29](https://github.com/DavidOWilliams/Materials-design/issues/29): inherited **v0.1** source equivalence on `main` failed [run 41099491180](https://github.com/DavidOWilliams/Materials-design/actions/runs/41099491180) because valid v0.2 `foundation/d1_visual_data.py` did not satisfy old v0.1 allowlist. Genuine failed CI (before numerical tests), **not evidence of a failed scientific regression**. Draft [PR #30](https://github.com/DavidOWilliams/Materials-design/pull/30) proposes narrowly restricting this old workflow to historical v0.1. It remains unmerged until owner approves; close issue only after merge + verification.
- **V02-IR-F02 OPEN nonblocking for internal integration, distribution-limiting:** real first-time human usability, accessibility/keyboard/screen-reader/contrast, Windows/Edge and Codespaces have not been independently qualified. Complete these before broader distribution. Automated Chromium is not comprehensive UX/accessibility certification.
- Existing docs in `main` retain historical pre-merge and candidate wording; this new dated publication package provides the current authoritative target without rewriting past records.

## Decisions required (independent, not bundled)

1. **Workflow-only merge:** separately approve [PR #30](https://github.com/DavidOWilliams/Materials-design/pull/30) after audit. Verify actual merged CI-only commit and workflow behaviour; close issue #29 after that.
2. **Annotated tag:** explicitly approve creation of **`d1-v0.2.0`** at **`280e21e3df62a6e2fcbf5bf4668b6b235ccd8384`** (even if `main` advances for workflow maintenance); annotate with bounded synthetic internal release and recorded source/tree. Do not tag without approval.
3. **GitHub release publication:** separate explicit approval, release visibility and audience *internal only*; attach/link evidence and release notes; no deployment implied.
4. **Deployment / wider distribution:** requires further explicit approval and risk/UX assessment; do not treat tag/publication as deployment authority.

**This document is an unmerged documentation-only publication-preparation artifact on a branch started from the verified merged commit; its future HEAD is not a retested application source.**
