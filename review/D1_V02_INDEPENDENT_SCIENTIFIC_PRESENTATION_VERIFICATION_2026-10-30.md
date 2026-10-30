# D1 v0.2 Independent Scientific-Presentation and Evidence Verification

**Review date:** 30 October 2026  
**Reviewer:** independent ChatGPT review, separately tasked; not author of D1 v0.2 implementation.  
**Formal decision:** **NOT READY FOR v0.2 MERGE/RELEASE** until the WP3 cross-work-package CI integration failure is resolved at a source-pinned revision. Scientific-presentation and challenge checks independently passed for the bounded synthetic scope; owner-led usability and formal accessibility are not certified.

## 1. Source/provenance

| Role | Exact identity |
|---|---|
| Release baseline tag | `d1-v0.1.0` (unchanged) |
| Frozen tested v0.2 application source | `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c` |
| PR #22 current documentation-only head | `fdf6d8407ef21706b6ab60ed020f9512bdaaa06e` |
| Implementation PR | https://github.com/DavidOWilliams/Materials-design/pull/22 (draft, unmerged) |
| Implementation workflow | https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174 (success; job `123740321190`) |
| Developer artifact | `12934327177`, SHA256 `f6f891aa72c458cfc59596968bfc0c6f6980185445498f9e64d2b5487d75feb9` |
| Independent reviewer branch | `independent/d1-v02-scientific-display-review-2026-10-30` (review code/docs only) |
| Independent reviewer workflow | https://github.com/DavidOWilliams/Materials-design/actions/runs/41046147946 (success; job `124030608615`) |
| Independent review CI checkout | `e72ee5f731026fd695bd59d9fb66be20d7efc05c` (ephemeral PR merge of v0.2 documentation head and review-only tests) |
| Independent reviewer artifact | `12972198847`, SHA256 `b642b5ef6af844271314dcbfb3628355c1d7ad4e393de0325f724a08af1840d3` |

Direct compare v0.2 frozen implementation vs current PR #22 HEAD shows only three Markdown files, not subsequent tested executable code. Direct compare from release tag `d1-v0.1.0` to v0.2 shows new presentation/data selector/Streamlit files, UI tests/workflow and six associated documentation files; no changes to `foundation/material_core` scientific kernels. Developer's exact-source baseline-compare files record identical WP3 intended-state qualified Pareto/proposals and WP4 feedback/numerical objective results. Reviewer inspected those archive data and separately generated/recomputed fresh WP3 and WP4 cases. CI checkout added only reviewer tests/workflow and the three later documentation changes relative to frozen v0.2; this is source-equivalent for execution, not the same Git commit identity.

## 2. Evidence integrity — independently checked

Reviewer downloaded developer Actions artifact `12934327177`, independently computed its full ZIP SHA256 as `f6f891aa72c458cfc59596968bfc0c6f6980185445498f9e64d2b5487d75feb9` and verified **158/158** listed SHA256SUMS entries against actual archived bytes. The archive has 159 members including the checksum manifest and includes original/v0.2 baseline numerical results, run stores, 4096-element examples, real-Chromium screenshots and replay files.

Reviewer separately downloaded independent artifact `12972198847`, verified its full ZIP SHA256 `b642b5ef6af844271314dcbfb3628355c1d7ad4e393de0325f724a08af1840d3` against GitHub metadata and recomputed **7/7** SHA256SUMS entries (no mismatch). Contents include exact CI checkout SHA, review-only source diff, Python/dependency freeze, four challenge results, Altair data-encoding tests and complete regression log.

## 3. Independently executed test matrix

All tests executed against the intact v0.2 application implementation plus reviewer-only assets; Python 3.12 CI runner with pinned Streamlit 1.40.2.

| Test | Exact stimulus / independent expected result | Actual outcome | Status |
|---|---|---|---|
| **V02-IR01** | WP3 `run_search(seed=17,budget=9,elements=128,mass_limit=31)`; reconstruct all designs from run store, compare architecture types and qualified Pareto/exclusion flags to `mixed_summary`. Manufacturing status remains unknown; no measured state invented. | 9/9 complete candidates' original architectures matched (4 homogeneous, 3 layered, 2 gradient); Pareto IDs **4 and 7**, all marked numerically eligible; measured evidence null; manufacturing unknown | **PASS** |
| **V02-IR02** | WP4 `execute(elements=4096,mass_limit=31,budget=4)`; compare every displayed objective to saved `record.objectives`, correct WP4 Pareto exclusion, no measured promotion, persisted numerical replay. | 3 records, WP4 Pareto **ID 2**, objective values matched; 3 estimated profiles inspected, distinct geometry treated honestly, replay `passed` | **PASS** |
| **V02-IR03** | Inject NaN, infinity, non-Boolean qualification and layered interface discontinuity; reject nonfinite plot coordinates and preserve uncertainty and distinct source compositions | NaN/inf not plotted, Boolean-only eligibility retained, distinct layer-interface fractions persisted | **PASS** |
| **V02-IR04** | Existing output and `*.handoff.json` collision; unused-path suggestion; verify immutable source bytes. Export/import valid WP3 ZIP and mutate campaign payload without manifest update | Collision prevented, existing bytes unchanged, suffix `one-run-002.json`, valid ZIP numerical restore passed, altered ZIP rejected without output directory | **PASS** |
| **V02-CH01** | Capture actual Altair WP3 scatter chart object and compare every plotted coordinate/classification against source `mixed_summary` for mass vs thermal transmission, not just unit-test selectors | 9 plotted points, exact coordinates, eligible/dominated/excluded categories match source; no incompatible WP4 pooling | **PASS** |
| **V02-CH02** | Inspect actual Altair architecture sample data generated from original WP3 intended designs; preserve homogeneous, gradient knots and layered interface values | 4 homogeneous, 3 layered, 2 gradient designs; every chart sample matched source positions, constituents, fractions, basis and sample identity | **PASS** |
| **V02-CH03** | Capture WP4 scatter chart object for same objective pair and compare to saved WP4 source and original Pareto/exclusion | 3 plotted points, exact coordinates and classification | **PASS** |
| **V02-CH04** | Inspect `feedback_view` for intended/estimated architecture mismatch; no unsupported achieved-profile overlay | All three incompatible-geometry examples explicitly suppressed unsupported overlay | **PASS** |
| **V02-REG** | Independent `pytest foundation/tests recovered_wp0 -q`, pinned scientific and UI environment | **370 passed, 1 Altair-related warning**, 110.93 seconds | **PASS** |

The 128-element WP3 examples used for **display-contract checking** are not upgraded into externally physically validated science; the 4096-element WP4 execution is a synthetic numerical evaluation. Developer's separate 4096-element full example remains preserved. No manual user acceptance or hardware/assistive-tech accessibility qualification occurred in these tests.

Previous independently authored CI attempts `41045608014`, `41045769370`, `41046021645` failed due to **reviewer-test assumptions/paths**, not implementation defects: initially required intended and estimated geometries to be identical; then pointed to an uncreated fixture directory; then omitted the source sample index when comparing Altair records. These failures are retained; each reviewer-only test defect was corrected and `41046147946` passed. No v0.2 executable code was modified by the reviewer.

## 4. Gate findings and release decision

| Gate | Independent verdict | Rationale |
|---|---|---|
| **Gate 1 — Scientific-presentation functional correctness** | **PASS (bounded)** | Independently evaluated actual chart data records from WP3/WP4 against saved objectives/designs and eligibility; no fabricated achieved curves in inspected incompatible scenarios; developer real Chromium four-tab and handoff/recovery CI evidence inspected. This is **not** independent full human usability or formal accessibility certification. |
| **Gate 2 — Negative/edge/integrity/replay challenges** | **PASS (bounded)** | Source-pinned independent invalid/unknown/NaN and boundary tests, immutable evidence collisions, tampered ZIP rejection, actual WP4 numerical replay, 370 inherited regressions passed. |
| **Gate 3 — Environment/CI integration and release provenance** | **BLOCKED — targeted CI portability defect** | v0.2 dedicated pipeline passed, independent scientific/UI runner passed with Streamlit installed, but existing WP3 qualification workflow [40957223034](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223034), job `123740320489`, failed **two new UI tests** solely because that science-oriented job does not install `streamlit`. Three other WP3 jobs succeeded; this is environment/test-discovery compatibility, **not** a WP3 numerical model defect. Formal cross-package CI acceptance must not silently treat this as green. |

**Overall: D1 v0.2 is NOT READY FOR MERGE OR RELEASE as-is.** Correct the one CI test-portability issue, rerun the existing WP3 workflow and v0.2 source-specific qualification, and request a narrow independent finding closure at the new exact SHA. P1/P2/P3/E1/E2 and V1 remain separate physical-science/evidence workstreams.

## 5. Numbered findings

**V02-IR-F01 — MAJOR / release-blocking:** New UI tests `foundation/tests/test_d1_v02_ui_collision.py` import Streamlit but are auto-discovered by the historical WP3 foundation regression job without its UI runtime. **Expected:** all relevant scientific and UI workflows green at final source. **Actual:** WP3 job `123740320489` failed its test collection/calls with `ModuleNotFoundError: No module named 'streamlit'`; two new tests failed, while dedicated v0.2 and independent science/UI runs pass. **Required correction:** isolate UI tests into a dedicated test marker/directory or install the required pinned UI dependency in the WP3 job, preserving meaningful test coverage; avoid classifying silently skipped UI tests as executed. Rerun WP3 and dedicated v0.2 workflows from new frozen SHA, independently inspect conclusions. **Disposition: OPEN**.

**V02-IR-F02 — MINOR / usability evidence gap:** human-first-use, assistive-technology keyboard/contrast/screen-reader and Windows/Edge/Codespaces user setup are not independently validated. Screenshot evidence is real but does not prove accessible or intuitive use across environments. **Required:** short owner/first-time-engineer usability session and accessibility test before broad distribution; log substantive misinterpretations as blocking only if found. **Disposition: OPEN, not automatic blocker for the bounded internal D1 v0.2 candidate**.

**V02-IR-F03 — INFORMATIONAL / scientific boundary:** D1 v0.2 still has distinct WP3 intended-state numerical and WP4 synthetic estimated-state trade-off contexts and no measured ceramic achieved state. The inspected plots maintain separation and unknowns; full validation of colour contrast for red/green/grey/shape and all chart axis screen reader descriptions remains outside this test. **Disposition: ACCEPTED BOUNDED LIMITATION**, not a defect in numerical physics.

**V02-IR-F04 — INFORMATIONAL / archived negative evidence:** previous reviewer-test fixture failures and historical implementation development failures are retained. The failed first reviewer CI runs were authoring errors in reviewer tests, not product failures. **Disposition: CLOSED by successful final reviewer run; history preserved**.

## 6. Minimal implementation correction brief

In the v0.2 implementation chat, correct **only** test-discovery/CI dependency compatibility at PR #22, without changing numerical models, feedback, eligible/Pareto rules, plots or frozen v0.1.0 evidence. Specifically resolve `foundation/tests/test_d1_v02_ui_collision.py` running under WP3 CI without Streamlit. Preserve UI tests in an environment where they actually execute, and preserve the historic pure-numerical checks. Rerun WP3, WP4, dedicated v0.2 and appropriate full regressions at the new SHA. Archive source, workflow, test counts and digests. Return the exact frozen corrected source SHA and CI run links for targeted independent re-review.

Do not merge PR #22, move tag `d1-v0.1.0`, create `d1-v0.2.0` or declare release acceptance until reviewer clears F01 and owner explicitly authorises. The planned seven-stage journey and chart-click selection should remain follow-on usability work unless a demonstrated usability failure makes them urgent.

## 7. Independent record and authority

This report is an independent test/qualification assessment, **not** owner approval or physical validation. Its documentation commit is separate from the exact tested v0.2 source. The reviewer added only `review/d1_v02_independent_scientific_tests.py`, `review/d1_v02_chart_encoding_review.py`, the independent workflow and this report on a separate review branch. Original implementation PR #22, previous tests, archive and release tag are unchanged. Do not merge review PR simply to accept the findings.


---

## Final targeted Gate 3 re-review — 30 October 2026 (supersedes earlier F01 OPEN disposition)

**Decision: V02-IR-F01 CLOSED. Gate 3 PASS (bounded). All three independent D1 v0.2 technical acceptance gates are now PASS for the original evaluated scientific presentation and a narrow CI-only correction. Overall: READY FOR PROGRAMME-OWNER v0.2 INTEGRATION APPROVAL, NOT MERGED OR RELEASED.** The earlier failed WP3 run and reviewer OPEN judgement remain historical, not deleted. Independent human/assistive-tech/Windows-Codespaces usability confirmation remains a nonblocking distribution consideration, not a claim of passed testing.

**Exact tested corrected source:** `d9e63ea468294eba4fc25493395ad68d60edf9a5` on PR #22, distinct from subsequent documentation-only HEAD `f8b97b91889d61848bee7afbed80c5b3853edc23`. GitHub compare against the earlier documentation HEAD `fdf6d8407ef21706b6ab60ed020f9512bdaaa06e` proves **exactly two changed paths:** `foundation/tests/test_d1_v02_ui_collision.py` was renamed byte-identically to `foundation/ui_tests/test_d1_v02_ui_collision.py` (0 changes), and `.github/workflows/d1-v02-ui-verification.yml` now explicitly runs this three-case UI suite in its pinned Streamlit 1.40.2 environment. Source compared to accepted earlier scientific display `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c` has no new presentation/UI/scientific production code changes after earlier independent tests. Later PR HEAD difference: one Markdown correction report only. No accepted `d1-v0.1.0` tag or WP3/WP4/WP7 scientific code changes.

### Re-verified corrected-source CI

- [WP3 workflow 41047548251](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548251): all four jobs **SUCCESS**, including formerly failing contract/vertical job `124035245296`, with **359 passed, 2 skipped** broad WP3 scientific suite, fresh WP2/3 scenarios and nine-record numerical search recomputation. The two previous `ModuleNotFoundError: No module named streamlit` failures are no longer in WP3 scientific discovery.
- [Dedicated v0.2 workflow 41047548183](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548183): job `124035244651` **SUCCESS**. **339 foundation tests passed, one warning; the explicitly relocated collision suite ran and passed all 3 tests** (one warning); the seven original display-transform unit tests were retained; direct WP3 intended Pareto/proposals and WP4 feedback/numerical comparison against `d1-v0.1.0` reports **identical**. 4096-element examples, three separate-process replays, real first-user Chromium, existing-dossier protection, and integrated selected handoff/recovery browsers passed.
- [WP4 workflow 41047548198](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548198): direct-branch job **SUCCESS**.
- [WP7 exact-head workflow 41047548148](https://github.com/DavidOWilliams/Materials-design/actions/runs/41047548148): qualification job **SUCCESS**.
- Associated next docs-only PR HEAD `f8b97b...` also has four successful PR workflow conclusions, but is not substituted for the exact implementation source.

**Independently downloaded and verified implementation correction artifact:** WP7/D1 v0.2 Actions artifact `12972374769` from run `41047548183`. ZIP SHA256 `bc6fc216e5d6bea985d5f7017f4635b85a08bc4f98f8fad15f366d0d500053a7` independently computed and matching GitHub artifact metadata. All **159/159 SHA256SUMS manifest entries** independently matched archived file contents. Preserved original v0.2 review archive `12972198847` and reviewer branch remain unchanged.

### Final findings

| Finding | Targeted final decision | Remaining significance |
|---|---|---|
| **V02-IR-F01** | **CLOSED; release blocker resolved** | UI interaction tests explicitly executed in dedicated pinned graphical environment; WP3 pure-science regression environment remains independent and green. |
| **V02-IR-F02** | **OPEN informational/minor usability** | First-time owner user experience, formal screen-reader/keyboard/contrast and Windows/Edge/Codespaces observation have NOT been independently performed; not acceptance PASS for those experiences. |
| **V02-IR-F03** | **ACCEPTED BOUNDED SCIENTIFIC LIMITATION** | WP3 intended-state and WP4 estimated-achieved Pareto contexts remain distinct; no measured manufactured outcome or P1/P2/P3/V1 claim. |
| **V02-IR-F04** | **CLOSED** | Historical reviewer-script fixture errors preserved, original first WP3 CI failure retained. |

**Gate 1 — PASS (bounded):** original reviewer direct Altair-data-to-source and scientific presentation cases remain applicable, since correction is CI/test relocation only.  
**Gate 2 — PASS:** original four independent challenges, actual chart encoding checks, 370 foundation/recovery regressions retained, plus fresh dedicated v0.2 tests (339+3) and WP3 science (359) green; no source physics/UI behavioural delta.  
**Gate 3 — PASS (bounded):** four corrected-source workflows green; source identity, dependency/test scoping, historical baseline equivalence, evidence ZIP and 159/159 manifest hashes independently verified.

**Overall:** **READY FOR CONTROLLED D1 v0.2 INTEGRATION APPROVAL** for the bounded synthetic UI/presentation improvements at corrected source `d9e63ea...`. No PR #22/#23 merge, `d1-v0.2.0` tag, release publication, end-user deployment or owner approval has been performed or implied. Governance should prepare a controlled source-equivalent integration; programme owner must authorise it separately. Retain independent usability and accessibility as distribution follow-ups.
