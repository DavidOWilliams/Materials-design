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
