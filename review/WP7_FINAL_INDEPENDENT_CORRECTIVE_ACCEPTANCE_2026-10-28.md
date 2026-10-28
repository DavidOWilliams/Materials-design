# WP7 — Final Independent Corrective Release Re-review
**Date:** 28 October 2026  
**Decision:** **READY FOR D1 RELEASE APPROVAL** — bounded synthetic computational D1 only; owner authorisation required before merge/release.  
**Independent reviewer:** separately tasked ChatGPT reviewer, not WP7 implementation author. No WP7 application, WP2 numerical, WP3 search or WP4 manufacturing-feedback production code changed by this reviewer.

## 1. Exact immutable source and provenance

- Accepted WP6 source: `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`.
- Original independent WP7 candidate: `4fc1bc3bd07de146460be1729469c7ea1e35969c` (Gate 1 blocked in review PR #17).
- **Corrected independently accepted WP7 implementation source:** `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, draft unmerged implementation PR #18.
- Current PR #18 head: `b17ed112082bc21ab3833d57062be6d56d0d5918`, **documentation-only addendum** after tested implementation. Diff between exact tested source and PR head consists only of `foundation/WP7_IR01_IR06_CORRECTIVE_DISPOSITION_2026-10-28.md`.
- Implementation evidence run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663 (job `122810313169`, success); archive ID `12815911040`; ZIP SHA256 `456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e`, independently verified; **99/99** archive SHA256SUMS entries valid. Source pin in original evidence `source-sha.txt` = `c8f029...`. The original code regression suite has ten new focused tests and **360 foundation/recovery tests passing**, real Chromium interaction, 4096-element examples and three separate-process replays.
- Independent re-review branch `independent/wp7-correction-rereview-2026-10-28`, draft PR #19. Independently authored two test files and CI workflow only; started from exact corrected source. **Final independent GitHub Actions run:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40690784535, job `122824717424`, **success**. CI temporary merge checkout `6de0c5b...` (full identity in `ci-checkout.txt`). Reviewer artifact `12818005576`, ZIP SHA256 `59c9a931d23093f2e7bb29a0a392ce03ceb9988abb8856e843665191cbeb9fe5`, independently downloaded and all **41/41** SHA256SUMS entries matched. The reviewer checkout differs from the exact accepted application SHA by only `.github/workflows/wp7-independent-correction.yml`, two reviewer test scripts and the one documentation-only PR #18 addendum. No numerical/production code changed.

## 2. Final gate decisions

| Gate | Formal decision | Independent evidence |
|---|---|---|
| **Gate 1 — Functional D1 workflow** | **PASS (bounded)** | Genuine WP3 A/B gradient selection, compatibility checking, auditable transfer into separate WP4 intended/estimated numerical context, immutable dossier with hash lineage, source/recovered dossier reopening, real browser review and restart, checkpointed binding cancellation and recovery. This is **not** manufacturing feedback for every WP3 architecture. |
| **Gate 2 — Independent challenge tests** | **PASS** | Previous independently executed seven adversarial WP7 tests, 357 legacy regressions and true browser ZIP restoration preserved; new reviewer-authored IR01/IR04 tests all **4/4 PASS** and **360/360** full foundation/recovery tests PASS. Unsupported architectures, mesh/mass mismatch, invalid index, corrupted handoff companion and duplicate recovered-output rejected; separate Python-process recomputation passed. |
| **Gate 3 — Source, replay and scientific provenance** | **PASS (bounded)** | Independently verified exact implementation-vs-doc commit, 99/99 author archive checks and 41/41 independent archive checks, clean Python/runtime and dependencies, immutable hash-carrying WP3→WP4 handoff, separate-process numeric replay, genuine binding cancel/recover, 4096-cell reference browser evidence. No measured/material/algorithmic superiority or V1 claim. |

**Overall independent reviewer recommendation: ACCEPT the WP7 corrected implementation for the bounded D1 release candidate and submit it for OWNER D1 RELEASE APPROVAL.** This is reviewer recommendation, not owner authorisation or release tagging. It does not grant permission to merge PR #18, #16, #19 or any historical WP branch.

## 3. Independently executed correction challenges (new source, new reviewer tests)

Executed `PYTHONPATH=foundation .venv-foundation/bin/python review/wp7_corrective_independent_tests.py` in independent GitHub Actions at the unchanged WP7 source with review-only test scripts.

| Test | Executed input / expectation | Observed | Disposition |
|---|---|---|---|
| **CR-IR01a** | Original WP3 `run_search(seed=17,budget=4,elements=128,mass_limit=31)`, choose homogeneous/layered indices 0–2, incompatible mesh 256, incompatible mass 30, invalid index 99; all must reject. | All rejects worked; original A/B gradient index 3 accepted; source design hash `f34d428...`, measured evidence null. Source numerical quality flag **false** at this 128-element *preview*, correctly preserved rather than promoted. | **PASS** |
| **CR-IR01b** | Recontextualise index 3 in WP4, preserve WP3 ledger/evaluation/design hashes, save and reopen dossier; independently launch different Python interpreter to verify lineage + numerical replay. | WP4 dossier created, initial hash/evaluation unchanged in handoff, `verified=true`, separate-process replay `passed` on saved candidate. | **PASS** |
| **CR-IR04** | New WP3 mass-ceiling **1 kg/m²**, index 3, budget 4, `cancel_after=1` — require actual cancellation and durable journal, then recover without overwriting original, reverify/replay. | Actual `stop_reason=cancelled`, **one checkpoint**, recovered **four candidate records**, fresh replay `passed`, overwrite rejected. | **PASS** |
| **CR-IR01c** | Mutate stored original handoff source-design hash without updating companion hash, reopen. | Tampered handoff rejected. | **PASS** |
| **CR-UI** | New independently authored Chromium workflow: fresh Streamlit, generate three architecture classes, select WP3 A/B gradient, hand off to new WP4 dossier, inspect/start checkpoint, recover and replay, shut down server, restart, reopen recovered dossier through browser. | **INDEPENDENT_BROWSER_PASS**, `browser/handoff/recovered/restart/replay=pass`; architectures `gradient/homogeneous/layered`. Screenshots, actual files and source/server logs in reviewer artifact `12818005576`. | **PASS** |
| **CR-REG** | Full foundation/recovered-WP0 regression at source-compatible reviewer checkout, Python 3.12. | **360 passed in 66.22s**. | **PASS** |

Prior reviewer-authored first corrective challenge run https://github.com/DavidOWilliams/Materials-design/actions/runs/40689926207 also succeeded 4/4 + 360 regressions (artifact `12816253344`, 8/8 hashes independently checked). First augmented browser run `40690558397` failed due to an unintended literal newline in the *reviewer's own test script*, not implementation. Reviewer corrected that test and final run `40690784535` passed. Preserve historical negative evidence; don't convert those tests to PASS.

## 4. Corrective finding dispositions and limitations

| Finding | Final reviewer disposition | Grounding |
|---|---|---|
| **IR01** — No WP3→WP4 integrated design workflow | **CLOSED FOR BOUNDED D1** | Original selected WP3 A/B gradient transferred with strict source/duty/material/solver/mesh/constraint matching and separate new WP4 estimated-state evaluation. Invalid/unsupported options reject. This does **not** imply homogeneous/layered manufacturing optimisation or a common achieved-state Pareto. |
| **IR02** — WP3 browser ZIP download, upload, restore and restart | **CLOSED**, prior independent run `40683793540` | Original real browser successful at previous WP7; no changes to WP3 ZIP implementation in PR #18. |
| **IR03** — independently executed adversarial numerical challenges | **CLOSED**, prior 7/7 and new 4/4 | Fresh source-specific 360/360 foundation regressions passed; source changes reviewed. |
| **IR04** — cancellation and recovery absent from WP7 coherent journey | **CLOSED FOR COOPERATIVE BOUNDARY CANCELLATION** | New WP7 UI supports checkpoint/cancel/inspect/recover; separate **binding** independent test produced actual `cancelled` after one record, reconstructed 4 and replayed. A nonbinding 31 kg/m² browser case stops naturally before cancellation; it must not be reported as cancelled. No mid-solver interruption supported. |
| **IR05** — original WP6 acceptance provenance linkage | **MINOR DOCUMENTATION FOLLOW-UP; NONBLOCKING** | Reviewer final WP6 record exists on review PR #8, `foundation/WP6_INDEPENDENT_ACCEPTANCE.md` at docs-only commit `5c6c2e368664ee91a038f2677d4304eed7db7a4e`; governance `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md` remains an incomplete transcription. Link exact original independent review record during release packaging without moving application source SHA. |
| **IR06** — ambiguous A/B versus A/B/C header | **CLOSED** | WP7 header and descriptive text now distinguish hypothetical WP3 three-catalogue exploration from WP4 A/B feedback. |

### Bounded D1 scope judgement

The *Implementation Plan v2 D1 checklist* requires (item 1) three supported architecture alternatives and new proposals, (item 2) three correctly unit-labelled objectives with separate incompatible comparison contexts, (item 3) a manufacturing achieved-state mapping with a consequential feedback-driven material/gradient revision, and (item 8) cancellation/reopen/export; it does **not** require current WP4 manufacturing feedback for **all three** architecture classes. Therefore one auditable **supported A/B gradient** WP3→WP4 handoff, together with the already accepted WP3 cross-architecture numerical search and WP4 feedback/revision evidence, is a sufficient **bounded** integrated user journey. The full-scale genuinely 4096-element WP7 author browser evidence used a numerically qualified WP3 source; the independent 128-element source was **not qualified**, and remained explicitly recorded as such. Do not call the 128-element example scientifically qualified.

The new WP4 handoff manifest depends on the original WP3 ledger path and run store remaining available. It is **not self-contained for relocation**. The release instructions must require retaining/exporting the accompanying WP3 original campaign/ZIP plus WP4 dossier and handoff manifest; no fully portable combined single-file bundle is accepted. Reopening a full workspace is supported; moving only the WP4 dossier without WP3 evidence will break verifiable lineage. This is a **user-facing limitation** requiring clear documented handling, not a reason to invent a passing portable combined export.

Cancellation is **cooperative at candidate boundaries**; an already naturally completed or feasible campaign does not report `cancelled`; there is no mid-solver pre-emption.

P1 algorithmic superiority, P2 external benchmark generalisation and P3/E1/E2 measured ceramic manufacturing/uncertainty remain separate scientific tracks. D1 does not provide physical ceramics validation, residual stress history, CFD, shrinkage, sintering, process uncertainties or aviation/engineering certification. D1 ≠ V1.

## 5. Owner approval and release packaging next steps

1. Programme owner reviews this bounded D1 acceptance: three-architecture numerical comparison plus **gradient A/B-only** source-linked manufacturing feedback, scenario uncertainty, and candidate-boundary cancellation. **Owner approval required before D1 release merge or tag.**
2. In separate documentation-only release packaging, link original independent final WP6 record on PR #8, current final WP7 review PR #19 and source-specific CI artifacts. Preserve reviewed implementation `c8f029...` separately from later docs-only commits. Fix IR05 governance pointer.
3. Ensure user startup instructions and example workspace carry the full WP3 ledger/run store or verified ZIP alongside WP4 dossier and `*.handoff.json`, since linked dossier is not portable standalone.
4. Perform controlled release integration/merge **only after owner approval**, retaining source provenance, and qualify actual merged/tagged D1 tree if merge introduces changed application code/config; no automatic merge/tag from this review.
5. Plan longer-term multi-architecture manufacturing feedback and physical evidence as separate enhancements, not release promises.

**FINAL: READY FOR D1 RELEASE APPROVAL** at tested implementation source `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, restricted as above. No PR merged, tag created, deploy claimed, or owner approval presumed.
