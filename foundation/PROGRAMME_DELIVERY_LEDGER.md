# Programme delivery ledger — authoritative current status index

**Established:** 26 October 2026 by separately tasked independent WP6 reviewer. **Policy:** one programme-wide status/forward-dependency index; do not overwrite WP1–WP5 package-level acceptance records or historical snapshots. Implementation Plan v2 remains delivery authority; this ledger indexes its WP0R–WP7/E1/E2 work packages plus P1–P3 scientific evidence. Do not infer statuses for unseen later changes.

## Governing order and boundaries

1. `recovered_wp0/evidence/Material_System_Implementation_Plan_v2.md` supersedes older product-delivery *timing/release-gate sequence* where inconsistent; long-term materials inverse-design Vision preserved.
2. The original WP6 preregistration, prospective amendment and tested CI evidence govern evaluation claims; `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` is current independent WP6 disposition.
3. `foundation/SCIENTIFIC_EVIDENCE_ROADMAP_P1_P3.md` is the **only programme P1/P2/P3 roadmap**. It is a prospective scientific plan, not test evidence.
4. Package-level WP3/WP4 acceptance ledgers and WP5 independent-acceptance record are retained as historical/technical source authorities. Older `WP6/EXECUTION_CHECKPOINT` and handover documents capture dated pre-review states and are not silently edited.
5. No merging of historic draft PRs or updating frozen baselines is authorized by this ledger.

## Programme status, evidence and release dependencies

| ID | Scope | Current programme disposition | Trace / controls | WP7 or V1 dependency |
|---|---|---|---|---|
| WP0R | Recovery/assumption-based prototype decision | Historical recovery recorded; scientific G0 **not passed** | `recovered_wp0/evidence/WP0_Decision_Pack_and_Assumptions.md` | Do not promote its evidence into V1 |
| WP1 | Contracts/run store/environment | Prior foundation implementation recorded; not independently re-reviewed in this WP6 session | `foundation/COMPLETION_REPORT.md`; WP5 regression compatibility | WP7 fresh setup/recovery still required |
| WP2 | Thermal and bounded mechanics numerical qualification | Prior package-specific qualification; no new external physics qualification from WP6 | `foundation/WP2_NUMERICAL_QUALIFICATION.md`; `foundation/WP2_CORRECTION_LOG.md` | Preserve applicability/reference limits |
| WP3 | Inverse search/eligibility/campaigns | **Accepted bounded synthetic scope** at `790c3521f09e3f61615702de3b149c9f315e9e74` | `foundation/WP3_ACCEPTANCE_LEDGER.md`; PR #3 draft | WP7 must show integrated D1 capabilities |
| WP4 | Intended-to-estimated manufacturing mapping/redesign | Prior independent accepted bounded implementation recorded in subsequent WP5 handoff; historic `WP4_ACCEPTANCE_LEDGER.md` contains older review-state text | WP4 tested `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b`; acceptance `1805811acdafacd66ba3574e8cb45c59bebdd8e5`; evidence `bb67e51029c5479361c59cea0b73b6bb722826f1` | conditional scenario not measured accuracy |
| WP5 | Interface, cancel/recover and portable replay | **Independently accepted bounded D1**, tested `4078a83dc11e14703ff6cc03f5b62f4e48879d14` | `foundation/WP5_INDEPENDENT_ACCEPTANCE.md`; PR #6 draft | WP7 independent user workflow/reinstall |
| WP6 | Held-out-duty brief, sensitivity, feedback comparisons, challenge/integrity | **INDEPENDENT REVIEW COMPLETE; Gate 2 OPEN, NOT FORMALLY ACCEPTED** at tested branch `c53dee793479843cc69926dd0da3663f22483b2f` | `foundation/WP6_INDEPENDENT_ACCEPTANCE.md`; CI `40354162508`; archive `12664928099`; PR #7 draft. No equal-effort superiority/new physics/measured validation | WP7 preparation only; formal release awaits WP6 Gate 2 closures |
| WP7 | Fresh-environment D1 release, restoration, user instructions and example dossier | **PREPARATION ALLOWED; D1 RELEASE BLOCKED PENDING WP6 GATE 2** | Implementation Plan v2 ten-item D1 checklist; WP7 needs its own tested source/artifacts and independent release gate | D1 blocked until WP7 checklist passes |
| P1 | Equal-actual-effort feedback / comparator evidence | **DEFERRED SCIENTIFIC EVIDENCE, NOT WP6/D1 BLOCKER** | `SCIENTIFIC_EVIDENCE_ROADMAP_P1_P3.md`, P1; freeze separate protocol | Can run alongside WP7; stronger algorithm claims only |
| P2 | Independent model benchmark / held-out generalisation | **DEFERRED SCIENTIFIC EVIDENCE, NOT WP6/D1 BLOCKER** | roadmap P2; separate published source/conditions/tolerances | Parallel WP7; qualifies later physical-domain expansion |
| E1 / P3 stage 1 | Rights and measurement data readiness | **OPEN / PARALLEL**; prior linked CODE and B4C–SiC records incomplete and noninterchangeable | Implementation Plan v2, `recovered_wp0/evidence/WP0_Manufacturing_Evidence_Reproduction.md`, roadmap P3 | Not D1 blocker; prerequisite for E2 |
| E2 / P3 stage 2 | Measured baseline/revision with external scientific review | **NOT VALIDATED / BLOCKED ON EVIDENCE** | roadmap P3, E1 data-rights readiness and separate scientific approval | **V1 BLOCKER**, not WP7 blocker |
| D1 | Bounded working demonstration | **NOT RELEASED**: WP6 Gate 2 and WP7 acceptance required | WP7 exact-release SHA and checklist | Must not label V1 |
| V1 | Measured ceramic validation | **NOT ACCEPTED** | E1+E2 measured achieved-state/uncertainty/independent baseline vs revision | No predicted completion date |

## Cross-dependencies and no-go conditions

- **WP7 planning/clean-environment preparation can begin** with accepted WP5 and the reviewed WP6 candidate source; **do not claim frozen accepted WP6** until required no-improvement and unresolved numerical-quality challenge outcomes are actually recorded, independently verified and accepted. P1, P2, P3/E1 are not on D1 critical path. WP7 must perform clean-env replay, restore, complete workflow, sensitivity and example dossier, accurate UI labels, no invented measurement, and final separate review.
- **Do not claim** equal-effort feedback superiority (P1), generalisation beyond supported numerical cases (P2), or physical ceramic validation (P3/E2) from WP6.
- **No scientific model training/new unqualified physics** within retrospective WP6 documentation. Any feature or benchmark extension needs new scope/branch/test evidence.
- **D1 demonstration review by David's son is optional and after a bounded working demonstration**; no automatic contact. E2 may request scientific expert involvement when David approves.
- Long-term research themes visible, **not implemented claims**: specialist/material discovery, multiple architectures (including future coating/substrate), manufacturing feedback, thermal mismatch vs full residual stress, future open-source FE/CFD for extrusion and other mechanisms, sustainable lifecycle objectives, and general-purpose inverse design. Historical aviation prototype naming is not the product Vision.

## Decision / workstream change control

Every new P1/P2/P3 proposal must identify owner, protocol SHA/date, scientific question, dataset licence, numerical context, applicable assumptions, measurable success criterion, tests, evidence archive URI/manifest SHA, cost/compute authorization and reviewer. Track 'not started', 'in progress', 'executed', 'reviewed', 'accepted', 'inconclusive', 'blocked' separately. Negative evidence is retained. No uncertain finding becomes 'passed' through editing only.

**Next programme action:** issue a narrow WP6 Gate 2 corrective brief for direct no-improvement and unresolved-numerical-quality challenge evidence; WP7 preparation may run in parallel from a source-pinned integration point after inspecting current branches (no silent merges); retain P1–P3 as parallel evidence tracks. An independent reviewer evaluates WP7 before D1 release.

**Document provenance:** this ledger is a documentation-only review artifact on `review/wp6-gate3-scientific-roadmap-2026-10-26`; it does not alter tested WP6 code or evidence.

## WP6 re-review update — 27 October 2026

Latest WP6 branch tested source `5f92fe47ce8c3aee4ad4bfacc7c5ec7567404f44`; CI merge checkout `5b7b1dc20a4916cc1fb1d8ab06ee9b71ca65cdf8`; Actions run `40386166153`, artifact `12681955393`. CI 14 WP6 and 349 regression tests passed; nine full campaigns and nine ordinary dossier replays passed; all 23 archive manifest entries independently checked. **G2-01 no-improvement evidence CLOSED** (actual `no_improvement_possible`; five proposals; five replayed candidate records; no feasible winner). **G2-02 unresolved numerical ineligibility demonstrated** (completed two-cell WP2 evaluation with `numerical_quality=unresolved`, eligibility false) but its preregistered **separate-process rerun of serialized RunInputs remains OPEN**. Hence formal WP6 Gate 2 acceptance remains withheld pending only this narrow evidence subcriterion. Current independent decision is `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` on review PR #8. WP7 preparation may continue; D1 release not authorized. P1/P2/P3 scientific workstreams are unchanged and do not block WP6 bounded D1 acceptance.

## WP6 last scientific challenge closure and regression portability finding — 27 October 2026

At WP6 source `328625ede938734e0ac40383b9b80fdd542136fa`, corrected run `40502217784` (artifact `12733636704`, temporary PR checkout `0589a35697722d6fc7cca4252b92f98f8cbab349`) verifies **G2-02 CLOSED**: original two-element numerical result recomputed in separate process from saved input, unchanged `complete/unresolved/ineligible`, numeric comparison zero differences, 27/27 SHA256SUMS valid. WP6 suite 14 + 1 focused tests, 350 full foundation/recovery tests, nine 4096-element campaigns and nine dossier replays pass. G2-01 remains CLOSED.

**New integration regression caveat:** simultaneous WP3 `40502217773` and WP4 `40502217918` integration runs failed their general test suite because the newly added WP6 reproduction test requires environment variable `WP6_ORIGINAL_NUMERICAL_ATTEMPTS` which is only configured within WP6 CI (343 passed/1 failed WP3; 349 passed/1 failed WP4). This is an evidence-fixture/test-portability defect, not a numerical result discrepancy. **Formal WP6 acceptance remains withheld** until portable test fixture handling is corrected and both integration workflows pass. Preserve prior successful scientific evidence. WP7 preparation may proceed; D1 release remains blocked by WP6 acceptance and WP7 own gate. P1/P2/P3 scientific evidence roadmap remains unchanged.


## FINAL WP6 acceptance and WP7 handover — 27 October 2026

**Independent Gate 3 decision: WP6 formally ACCEPTED for bounded D1 synthetic demonstration/evaluation at tested branch source `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.** The latest dated section of `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` is authoritative; all prior OPEN snapshots in this ledger are historical and **superseded**. Current acceptance status: Gate 1 **PASS**, Gate 2 **PASS**, Gate 3 **PASS**.

Source-controlled evidence: WP6 workflow `40538857738` (CI merge checkout `7f039f070bcb044b8bf0fc9112a15a0f7d2f7157`, artifact `12748729866`, verified ZIP SHA256 `ff8c4ecad1be50f5a5b6d5c5496ade2bb906cd615cb9819bf8d585a3e7f459b2`; 28/28 manifest entries checked); 14 WP6 tests, portable and archived reproduction cases, 350 foundation/recovery tests, nine full campaigns and nine separate-process replays passed. WP3 `40538857597` all four jobs successful; WP4 `40538857615` passed. G2-01 and G2-02 and the cross-work-package portable-test defect are independently CLOSED. No accepted WP2–WP5 scientific code changed. PR #7 and review PR #8 remain draft/unmerged and no source baseline was moved.

**WP7 READY TO IMPLEMENT, NOT YET D1 RELEASED.** Implement Plan v2's ten D1 checklist items and WP7's fresh-environment, restore/replay, runnable instructions, example dossier and acceptance evidence against a source-pinned integration point; avoid silently merging historical work-package PRs. **P1** equal-cost feedback superiority, **P2** genuinely held-out scientific/generalisation references, and **P3/E1/E2** measured ceramic command→achieved-state evidence remain deferred separate scientific tracks and **do not block WP7**. **V1 remains blocked** on real measured evidence and independent physical/technical validation. This is an acceptance record, not a new tested implementation SHA.


---

## D1 governance addendum — 28 October 2026 (supersedes historical WP6/WP7 status above for current programme tracking)

**Do not silently rewrite the historical 26 October review:** its WP6 Gate 2 OPEN decision remains accurate for the then-reviewed source `c53dee793479843cc69926dd0da3663f22483b2f` and CI 40354162508. The programme owner reports a later independent all-three-gates PASS decision on 27 October at accepted source `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`; the original final independent-review document itself has not been located in current repository branches. See separate `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`. This addendum records owner-supplied authoritative status without representing itself as a newly authored independent review.

**D1 exact-source executable evidence now exists:** workflow_dispatch [40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136), actual checkout `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`, job `122742537320` success, artifact `12805993031`; 350 foundation/recovery tests, 15 WP6 focused tests, Gate 2 challenges, clean installation and dependencies on Ubuntu 24.04 / Python 3.12.15 passed. The downloaded archive's 12-file SHA256 manifest independently matches all twelve files. **Repository-manifest verification DID NOT VERIFY anything:** both manifest-list and manifest-check logs are empty. The success of that step is vacuous. No claim of existing repository archive integrity from this run.

**Current integration disposition: CONDITIONAL for WP7 bounded preparatory work, NOT VERIFIED for D1 release.** Additional required exact-source checks: WP3/WP4 integration tests, WP1/WP2 numerical dossier reconstruction/replay, WP4 4096-element recompute, WP6 nine-case 4096-element full evaluation and distinct-process replay, pinned external evidence ZIP + internal SHA256, and Streamlit app HTTP startup. Workflow-only [PR #15](https://github.com/DavidOWilliams/Materials-design/pull/15) is prepared but not merged or executed; it requires owner review/approval. Independent WP7 release review and tag remain barred pending these checks. Reconcile WP2 final tested SHA from job logs; preserve P1 exclusion and D1/V1 boundaries.

**Source identities and branches:** accepted WP6 source unchanged. WP7 source/governance PR #12 remains distinct from verification PR #13 and workflow-only PR #15. The main branch CI workflow was merged via #14 only; no accepted scientific implementation merges or final release tag occurred during this work.


---

## Current programme ledger closure — 28 October 2026, final integration-baseline gate

**D1 INTEGRATION BASELINE: VERIFIED** for the bounded synthetic implementation at source `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`. This supersedes the older *integration verification* BLOCKED/CONDITIONAL status above but **does not** supersede the independent WP7 *release* gate (still OPEN) or the earlier dated WP6 Gate 2 review at its historical SHA.

**Recorded executable checks:** [40666591136](https://github.com/DavidOWilliams/Materials-design/actions/runs/40666591136) 350 regressions + 15 WP6 tests; [40668433992](https://github.com/DavidOWilliams/Materials-design/actions/runs/40668433992) 157 WP3/WP4 tests, WP1/WP2 numerical replays, WP4 high-res dossier recompute, nine WP6 full-resolution campaign replays, external historical evidence digest and required manifest checks, Streamlit HTTP startup. Both use the same immutable `1f89c2d` code. Full evidence artifact `12807606181`, ZIP SHA256 `d8367e5c25699609e14f8038b8b5932bbe6c819fc3fc36086e737fd0d73fcdfb`, 99/99 SHA256 manifest entries independently verified. Prior artifact `12805993031`, ZIP hash `62ce54d59bc9de714941d4158bfe86750fcb0340b5d03a010f67b75cc7bc5ee9` (12/12 verified). Earlier empty repository manifest list remains recorded as vacuous, not a successful historical check.

**WP1** tested source `729a9da5`, documentation `22350b11`. **WP2** last implementation-changing `a3a4d592`; actual last fully green five-job CI checkout `7009189d` (one report-only commit; no application-code diff), run `40073237148`; bounded numeric qualification. WP3/WP4/WP5 identities remain in source register. **WP6** later 27 October independent Gate PASS as reported by programme owner and held separately in owner-provenance record; original final independent reviewer document still not retrieved. No retrospective rewrite of earlier PR #8 decision.

**WP7 next:** proceed on `wp7-d1-reproducible-release-2026-10-27` from immutable accepted source; complete WP7 delivery/package checklist, independent user workflow and documentation review, freeze its own tested candidate, obtain separate independent WP7 release review and owner approval before any merge/tag. P1 excluded; no measured V1 claims. No release SHA/tag established here.


## D1 v0.1.0 controlled release candidate appendix — 28 October 2026

- Accepted WP7 application `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, tested tree `b9ab5ed7b54ff670783e7fb6a8816538be7eb1ae`; accepted WP6 integration ancestor `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- Later PR #18 `b17ed112082bc21ab3833d57062be6d56d0d5918` is **one Markdown-only commit**, and not a newly tested implementation.
- Final independent WP7 approval recommendation [PR #19](https://github.com/DavidOWilliams/Materials-design/pull/19), dated 28 October, Gates 1–3 PASS bounded, not owner publication approval. Final reviewed report: `review/WP7_FINAL_INDEPENDENT_CORRECTIVE_ACCEPTANCE_2026-10-28.md` on independent review branch, not yet in accepted implementation tree.
- Author source CI [40686565663](https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663) artifact `12815911040`, ZIP SHA256 `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`. Independent review CI [40690784535](https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535) artifact `12818005576`, ZIP SHA256 `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`. Reviewer independently checked 99/99 and 41/41 source-specific manifest entries.
- Release integration branch `d1-release-candidate-2026-10-28` starts directly at accepted WP7 implementation, **without importing extra unreviewed code**, and holds D1 release documents. Final release commit/tree must be recorded after documentation completion. Release branch differs from accepted application only by documentation; see `foundation/D1_RELEASE_SOURCE_AND_EVIDENCE_MANIFEST.md` and `foundation/D1_RELEASE_INTEGRATION_REPORT.md`.
- WP3 intended-state Pareto and WP4 estimated-achieved-state Pareto separate. WP4 can consume **compatible A/B gradient** WP3 selection only. Cooperatively cancel at candidate boundaries. WP4 `*.handoff.json` is not independently relocatable with WP4 dossier: preserve WP3 workspace/ledger/run store or verified WP3 ZIP.
- Scientific limits D1 synthetic demonstration; no P1/P2/P3/E1/E2 scientific claims or measured ceramics / V1. IR05 historical WP6 original *final* Gate 3 PASS report remains unlocated. Earlier WP6 PR #8 review with Gate 2 OPEN at older SHA remains preserved; do not cite it as the final later PASS record.
- **READY FOR OWNER APPROVAL only if exact release packaging/code tree and checks are evidenced.** No application merge, tag or published release authorised by this appendix.


---

## IR05 documentary-source correction — 28 October 2026 (authoritative supersession of outdated gap statements above)

**IR05 CLOSED — original final independent WP6 acceptance recovered:** [`foundation/WP6_INDEPENDENT_ACCEPTANCE.md` at documentation-only commit `5c6c2e368664ee91a038f2677d4304eed7db7a4e`](https://github.com/DavidOWilliams/Materials-design/blob/5c6c2e368664ee91a038f2677d4304eed7db7a4e/foundation/WP6_INDEPENDENT_ACCEPTANCE.md). Its final dated section, **“FINAL independent WP6 Gate 3 acceptance — 27 October 2026”**, explicitly accepts bounded WP6 at tested `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`, Gates 1, 2 and 3 PASS. Independent WP6 workflow [40538857738](https://github.com/DavidOWilliams/Materials-design/actions/runs/40538857738), artifact `12748729866`, ZIP SHA256 `ff8c4ecad1be50f5a5b6d5c5496ade2bb906cd615cb9819bf8d585a3e7f459b2`, archived manifest 28/28; independent WP3 run `40538857597` and WP4 run `40538857615` succeeded. The same original report retains earlier Gate 2 OPEN and withheld findings as historical, source-specific snapshots; those are **superseded by the final acceptance section, not overwritten**. The final report commit is documentation-only, distinct from tested WP6 application source.
