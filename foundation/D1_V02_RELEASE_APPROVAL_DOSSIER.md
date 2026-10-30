# D1 v0.2 — controlled integration and programme-owner approval dossier

**30 October 2026; PRE-MERGE candidate, not owner-approved, not tagged.** Final disposition requires *actual current candidate* CI conclusion and artifact inspection, not earlier accepted-source runs alone.

## Acceptance authority and exact identities
- Current v0.1.0 tag is an annotated tag object `8ba4331bab178bbdbef9e27cde77e1923cd7ee8e` targeting `ec4bea044858bc275a1be80c3df24be438085279`, same as current main before v0.2.
- Independently accepted corrected v0.2 implementation `d9e63ea468294eba4fc25493395ad68d60edf9a5`, source tree `f63327ed03e7b22bb8c655c2d7ec608f0b0d7bb2`.
- PR #22 later Markdown-only HEAD `f8b97b91889d61848bee7afbed80c5b3853edc23`. Reviewer branch PR #23 HEAD `6d689eab52329b57a821ca7eeac7f1cfcac3e483` is reviewer tests/CI/docs, not accepted implementation.
- Dedicated release-integration branch `d1-v0.2-controlled-integration-2026-10-30` begins directly from PR #22 documentation HEAD and accepted code; it must contain only original accepted scientific/application tree, additional release docs/governance records and the release qualification workflow. Git ancestry is directly from prior main, without merging history from PR #23 or research projects. Exact candidate HEAD/tree in PR and qualification artifact.
- GitHub compare main→accepted v0.2 enumerates 16 changed paths: v0.2 workflow, 7 implementation docs, 3 production visual/UI modules and source replacement, presentation/browser/unit/UI tests. No third-party scientific model or underlying WP2/3/4 numerical/feedback kernel modification.
- Independence: original final [review report](https://github.com/DavidOWilliams/Materials-design/blob/independent/d1-v02-scientific-display-review-2026-10-30/review/D1_V02_INDEPENDENT_SCIENTIFIC_PRESENTATION_VERIFICATION_2026-10-30.md) latest addendum; Gate 1 PASS bounded, Gate 2 PASS, Gate 3 PASS bounded, but not an approval to merge. F01 CLOSED, F02 OPEN nonblocking for bounded internal demonstration, F03 accepted synthetic limitation, F04 CLOSED and past failing evidence retained.

## Source-pinned evidence
- Independent science presentation [41046147946](https://github.com/DavidOWilliams/Materials-design/actions/runs/41046147946), artifact `12972198847`.
- Implementation [41047548183](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548183), artifact `12972374769`, external ZIP SHA256 `bc6fc216e5d6bea985d5f7017f4635b85a08bc4f98f8fad15f366d0d500053a7`, 159/159 entries rechecked independently.
- WP3 [41047548251](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548251), 359 scientific passed/2 skipped and all four jobs green; WP4 `41047548198`, WP7 `41047548148` green.
- Proposed candidate dedicated CI workflow `.github/workflows/d1-v02-release-integration.yml` asserts accepted implementation tree unchanged, source-only documentation/CI diff, exact checkout SHA, clean Python 3.12, foundation and isolated graphical tests, v0.1.0 numerical equivalence, 4096 full-resolution examples, distinct-process replay, real Chromium first-user/handoff recovery and checksummed archive.

## Scientific boundary and residual risks
WP3 intended-state architecture search and WP4 *estimated achieved-state* A/B-gradient manufacturing-feedback simulations are different evaluation contexts and their Pareto results never pool. Unknown/nonfinite and unsupported achieved-state overlays must not be promoted. No experimental ceramics validation, industrial production fitness, airworthiness certification, new scientific physics or P1/P2/P3/E1/E2/V1 claims. Four tabs retained; accessibility, assistive technology, real Codespaces/Windows/Edge and owner first-use testing remain OPEN (F02), nonblocking only for bounded **internal** integration; separate decision before wider distribution.

## Approval controls
- [x] Final original independent record and superseding 30 October Gate 3 PASS retrieved.
- [x] Accepted application SHA/tree and documentation-only later PR #22 delta confirmed.
- [x] Historical v0.1.0 tag target verified unchanged.
- [x] Controlled release branch from accepted v0.2 lineage created without P1.
- [ ] Verify exact final candidate workflow PASS and preserve artifact SHA256.
- [ ] Verify current HEAD/tree/source equivalence after final documentation commits.
- [ ] Owner separately authorises merging ONLY controlled integration PR into main.
- [ ] After merge, verify actual main checkout/tree, clean runtime, regression, exact baseline comparison, browser and archive; prepare separate post-merge decision.
- [ ] Owner separately authorises eventual `d1-v0.2.0` tag and publication/deployment. **None authorised.**

**Intended decision:** READY FOR OWNER APPROVAL only after live integration PR verification passes. Do not merge PR #22/#23 or controlled PR automatically.
