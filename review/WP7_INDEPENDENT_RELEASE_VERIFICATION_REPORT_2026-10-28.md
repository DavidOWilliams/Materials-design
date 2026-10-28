# WP7 independent release verification — 28 October 2026

**Reviewer:** separately tasked independent ChatGPT reviewer; did not author WP7 implementation. This branch contains only reviewer-authored tests, a proposed reviewer CI workflow and this report. **Overall decision: NOT READY FOR D1 RELEASE APPROVAL (BLOCKED)**. Neither owner approval, PR merge, nor release tag is implied.

## 1. Exact source and independence

| Identity | Exact reference |
|---|---|
| Accepted upstream WP6 implementation | `1f89c2d1bf64b669ca98b81f4305d20d08104e5c` |
| WP7 **tested implementation** | `4fc1bc3bd07de146460be1729469c7ea1e35969c` |
| WP7 later documentation-only PR head inspected | `1d5d63c18acc5f87c952e00fe3b273e5cc9cc0c4` |
| WP7 completed exact-source workflow | https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977 |
| WP7 evidence artifact | `12808843984`, ZIP SHA256 `6c660389e94ed6873b4f8931f5647458159fbf2d989087a0b375e3476250b028` |
| WP7 implementation PR | https://github.com/DavidOWilliams/Materials-design/pull/16 (draft, unmerged) |
| Independent reviewer branch | `independent/wp7-d1-review-2026-10-28`, from exact implementation `4fc1bc3...` |
| Independent review PR | https://github.com/DavidOWilliams/Materials-design/pull/17 (draft, unmerged) |

GitHub comparison confirms the changes from tested implementation `4fc1bc3...` to PR #16 documentation head `1d5d63c...` are **six Markdown files only**; they are not fresh implementation tests. Compared with accepted WP6, WP7 adds the D1 Streamlit application, read-only presentation, portable WP3 ZIP functionality, example builder, tests and CI; no accepted WP2/WP3/WP4 scientific solver/search/feedback implementation module changed. PR #16 targets the separate WP7 governance branch, not main. P1 source is not integrated.

The independent reviewer downloaded the original WP7 evidence ZIP and directly recomputed **its outer SHA256 and all 67 internal SHA256SUMS entries**; all matched. This means 68 ZIP entries including the manifest. `source-sha.txt` contains exactly `4fc1bc3bd07de146460be1729469c7ea1e35969c`. Actual authored CI 40673439977 / job `122765726102` concluded success: seven WP7 focused tests, 357 foundation/recovered regressions, full-resolution example creation (4096 cells), three separate Python-process replays, a genuine Chromium WP4 journey and accompanying screenshots. Python 3.12.15 and foundation locked numerical dependencies are recorded; UI dependencies are pinned but not fully transitively hash-locked. These are **implementation-run** results, **not separately executed numerical challenge results by this reviewer**.

## 2. Gate dispositions

| Gate | Independent disposition | Reason |
|---|---|---|
| **Gate 1 Functional D1 release** | **BLOCKED** | Accepted WP3 mixed-architecture intended-state campaign and WP4 gradient-only estimated-state manufacturing-feedback campaign work, but remain distinct workflows without candidate transfer or a single manufacturing-aware three-architecture decision. Full real-browser WP3 ZIP upload/restore and restart user journey not executed by the implementation browser test or independently here. D1 Plan v2's original *complete workflow* criterion needs either actual integration or explicit justified owner scope decision. |
| **Gate 2 Independent challenges** | **BLOCKED (partial executed)** | Reviewer executed five independent **archived-data** probes successfully, and created separate reviewer-authored numerical tests and a GitHub Actions workflow on PR #17. The numerical tests' remote execution/conclusion were **not independently retrievable/confirmed**; do not label them passed. Original development-team 7/357 successful suites are corroboration, not replacement for independent numerical execution. |
| **Gate 3 Provenance/reproducibility/scientific assurance** | **BLOCKED (integrity independently passed)** | Source SHA and archive hashes independently checked, provenance and scientific labels sound, three independent-process *developer-executed* replays documented. Reviewer has not re-executed a clean independent numerical replay at frozen SHA or validated full ZIP browser import and restart. That part of the mandatory independent reproduction remains open. |

**FINAL: REJECT / BLOCKED for D1 release approval, without implying that the reviewed numerical solver is defective.** Current source is a strong release candidate for continued bounded qualification, **not** an independently approved release.

## 3. Executed reviewer challenges (direct artifact-byte and data checks)

Executed by independent reviewer using Python's `zipfile`, `hashlib`, `json` on the downloaded immutable ZIP `github-actions-artifact-12808843984.zip`. Archived reviewer output: `/mnt/data/wp7_independent_archive_challenge_results.json` in active review environment; this path is not a repository artifact. The direct checks are distinct from the reviewer-authored unconfirmed GitHub workflow and do **not** call the WP2/WP3/WP4 numerical evaluator.

| Test | Exact tested input / expected | Observed | Result |
|---|---|---|---|
| **IR-A01** Source and integrity | SHA256 of original artifact plus each of its `SHA256SUMS` entries must match | Outer digest `6c660389...`; **67/67** internal entries matched; `source-sha.txt=4fc1bc3...` | PASS |
| **IR-A02** Three classes/Pareto exclusion | `example-dossiers/wp3-mixed/campaign.json`, nine 4096-cell proposals; only qualified eligible; all manufacturing statuses unknown | homogeneous, layered, gradient; **7 eligible**, indices 1 and 8 excluded; Pareto ID 4 is eligible; **all manufacturing feasibility unknown** | PASS |
| **IR-A03** Valid and impossible manufacturing scenario | `representative-wp4.json` mass 31, `infeasible-wp4.json` mass 1; expect one conditionally qualified solution vs none | representative masses **37.5, 32.5, 27.5 kg/m²**, 1 conditionally feasible, stop `qualified_scenario_feasible`; impossible **37.5, 32.5, 27.5, 22.5**, none feasible, stop `evaluation_budget_exhausted`. All measured evidence null | PASS |
| **IR-A04** Portable ZIP static integrity and tamper differentiation | `example-dossiers/wp3-mixed-portable.zip`; compare member set and full digest manifest; append a byte to campaign.json and rehash | Original **21 members** consistent with manifest; modified campaign payload checksum no longer matches. This checks checksum detection only, **not runtime importer rejection** | PASS (bounded) |
| **IR-A05** Archived separate-process evidence | `example-dossiers/example-manifest.json` names independent-process replays for restored WP3, representative and infeasible WP4 | Three `separate_process=true` results all `passed`: WP3 9, WP4 3 and WP4 4 recomputed | PASS for **archived claim audit**, not for fresh independent solver execution |

**Additional source-based challenges requiring execution:** reviewer-authored `review/wp7_independent_challenges.py` specifies seven scenarios: IR01 representative feasible Pareto; IR02 no-feasible and precise reasons; IR03 mass boundary 30/31/31.000001; IR04 malformed/missing/forged immutable dossier; IR05 fresh Python-process portable replay; IR06 byte-for-byte deterministic repeat; IR07 mixed architecture/ZIP import, tamper rejection. Workflow `.github/workflows/wp7-independent-review.yml` would run these with foundation regressions, record source/tree identities, and archive hashes. **Authoring/committing these does not constitute execution.** Their CI conclusion was not available through the current GitHub workflow-listing connector as of this report. Do not substitute the developer's run.

## 4. Gate 1 UI journey classification

**Demonstrated by prior WP7 CI**: clean Python 3.12 setup; Streamlit process; interactive Chromium for WP4 run → saved dossier → inspect → recompute; Streamlit AppTest for WP3 generator, mixed candidate inspection and numerical replay; backend import/export of WP3 ZIP and WP4 JSON; three examples restored in separate processes. Browser screenshot/log from successful CI actually inspected. Developer Chromium browser script `foundation/tests/wp7_browser_acceptance.py` **does not navigate to WP3 tab, upload WP3 ZIP, click Verify and restore, select a WP3 candidate, restart the server, or traverse the full mixed-architecture UI after restart**. Backend/AppTest cannot be relabelled successful real-user browser journey.

**Scientifically consequential architectural boundary:** source `foundation/wp7_app.py` implements (a) WP3 *intended-state* three-architecture search/qualified numerical Pareto in tab 2, and (b) WP4 *estimated achieved-state* gradient-only feedback/revision/conditional feasibility in tab 1. The results are explicitly not pooled, as scientifically required. But there is no evidence or UI transfer from one WP3 proposed architecture/candidate into the manufacturing evaluation; therefore not one candidate family compared under manufacturing-aware achieved-state conditions. The original Implementation Plan v2 separately requires three architectures, a manufacturing revision and a complete usable inverse-design workflow. An acceptance interpretation permitting two disconnected but scientifically honest journeys **must be made explicitly**, not silently inferred from a green CI run. Do not blindly pool incomparable data to repair this.

**Cancellation**: D1 UI offers no cancellation button. Startup guide explicitly directs cancellation to the older WP5 application. D1 Plan v2 item 8 calls for runs that can be cancelled, reopened and exported. Whether access to the older WP5 UI counts as complete D1 release functionality needs an explicit walkthrough and disposition.

## 5. Numbered independent finding register and required corrections

| ID | Severity | Expected versus actual / impact | Reproduction | Minimum corrective action | Re-execution | Status |
|---|---|---|---|---|---|---|
| **WP7-IR01** | **BLOCKING** | Integrated material architecture → feedback → revision decision under a usable D1 workflow expected; actual WP3 multi-architecture and WP4 gradient feedback are separate, with no candidate handoff. No false claim of combined manufacturing-aware Pareto should be made. | Inspect `wp7_app.py` button handlers and archived WP3/WP4 context IDs. | Implementation chat propose smallest scientific-contract-preserving integration or supply exact checklist justification to owner for a deliberate narrower D1 acceptance. Independent reviewer to decide on requirement fit; owner approval needed for scope deviation. | Yes, if software changes | OPEN |
| **WP7-IR02** | **BLOCKING** | Real browser ZIP import/restore, candidate selection and restart expected; WP7 Chromium script exercises only WP4 run/inspect/recompute, WP3 AppTest stops before ZIP upload and restore. | Inspect `wp7_browser_acceptance.py` and `test_wp7_mixed_architectures.py`. | Add real Chromium WP3 ZIP download/upload/restore, candidate inspection, close/relaunch app, reopened ledger and separate-process recomputation on immutable full-resolution release fixture. Capture screenshot/log and actual saved files; preserve failed attempts. | Yes | OPEN |
| **WP7-IR03** | **BLOCKING (evidence)** | Independent Gate 2 challenges must execute; author-run tests passed, reviewer-authored CI test result unconfirmed. | Review PR #17 scripts/workflow and seek actual Actions run/status; do not imply committed means run. | Execute reviewer-authored tests on source-pinned checkout and archive full logs, manifest, exact merge checkout; if workflow trigger unavailable, use a known enabled CI workflow runner or arrange minimal authorized workflow dispatch. | Yes | OPEN |
| **WP7-IR04** | **MAJOR** | D1 cancellation in main user journey per Implementation Plan v2; new simplified WP7 UI lacks it, old WP5 UI retains it separately. | Inspect `wp7_app.py` and `WP7_D1_STARTUP_AND_WALKTHROUGH.md`. | Verify cancellation/recovery through a documented combined user journey or obtain explicit bounded workflow restriction before release. Avoid claiming mid-solver cancellation. | Required for release | OPEN |
| **WP7-IR05** | **MINOR** | Source provenance documentation: original final WP6 independent 27 Oct report not yet linked in governance. | `D1_SOURCE_OF_TRUTH_REGISTER.md`, `WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md`. | Link the existing independent final reviewer decision from WP6 review PR #8; distinguish from owner transcription. Does not invalidate verified underlying WP6 source tests. | Documentation only | OPEN |
| **WP7-IR06** | **INFORMATIONAL** | End-user app header says “Two hypothetical scenario constituents” while WP3 mixed generator describes A/B/C synthetic catalogue. | `foundation/wp7_app.py` top-level caption vs WP3 output. | Clarify scenario-specific catalogue/constituent limits in user-facing help. | UI smoke after text change | OPEN |

No issue in this register should be marked CLOSED without new source-pinned direct evidence or a recorded independent disposition. No original negative run is erased.

## 6. Acceptance checklist and risks

| D1 Plan v2 item | Review position |
|---|---|
| 1. Three architectures and a newly generated proposal | WP3 supported and observed, but separate from manufacturing campaign |
| 2. Three physical objectives, directions, units, comparable contexts | WP3 and WP4 each support three, but **between-workflow comparisons prohibited** |
| 3. Achieved-state mapping changes evaluation and triggers redesign | WP4 synthetic gradient demonstrates this |
| 4. Second constraint/brief and no feasible result | WP4 31 vs 1 mass runs verified in archive; full brief edits restricted |
| 5. Numerical references/mesh refinement | Earlier accepted WP2 bounded references and source-specific regression; new independent external benchmark not attempted |
| 6. Sensitivity | WP6 layer/feed and scenario constraints tested; no statistical uncertainty or physical validation |
| 7. Numerical versus estimated versus measured status | Clear in UI and records; all measured unknown |
| 8. Cancel/reopen/export | Reopen/export supported in split WP7, cancellation in older WP5 UI only; release journey unresolved |
| 9. Evidence source, solver, lineage, constraints, exclusions, stop | Immutable WP3/WP4 dossiers and manifests present; 67 hashes independently verified |
| 10. Runnable demo, startup instructions, concise review pack | Startup documented, Chromium WP4 partial journey; full WP3 browser and integrated suitability outstanding |

Preserve all scientific boundaries: synthetic property pack and planar thermo-mechanical coupon; *tensile thermal mismatch*, not total residual manufacturing stress; assumed layer/feed resolution not actual machine capability; missing achieved measurements and porosity/shrinkage/sintering/CFD; no physical ceramic feasibility, causal algorithmic superiority, general-purpose physics qualification, P1 integration or V1. Numerical-quality unresolved is not positive qualification.

## 7. Next actions and approval boundary

1. WP7 implementation chat: address **WP7-IR01, IR02 and IR04**, with the smallest scientifically sound candidate-handoff or explicit deliberate bounded-scope release proposal, real browser ZIP restore and restart test, and cancellation journey. Do **not** create a false single Pareto by merging WP3 intended outputs with WP4 achieved outputs.
2. Reviewer: obtain **actual completed status/evidence** for independent PR #17 challenge workflow and inspect any failures; re-run affected numerical and UI checks after correction. Do not silently accept the test because the file exists.
3. Preserve exact tested candidate `4fc1bc3...`, CI run `40673439977` and artifact `12808843984`; no application merges or tags.
4. Owner David: only an explicit scope trade-off or D1 release authorization requires owner approval; routine testing and fixes do not.

**RELEASE STATUS: NOT READY.** D1 release approval is not recommended at this SHA. WP7 implementation and developer-tested reproducibility have significant merit, but an independent full user journey and specific original D1 integration requirements are not yet demonstrated.


---

## Final independent execution addendum — 28 October 2026 (supersedes earlier test-pending statuses)

The reviewer's source-isolated GitHub Actions execution has now **completed successfully**. This addendum supersedes this report's earlier statement that reviewer-authored numerical tests had not executed, and closes the corresponding evidence finding. Historical failed reviewer attempts remain retained, with provenance and cause; no implementation defect is falsely inferred from those reviewer-runner failures.

### Exact separately executed reviewer evidence

- **Independent review workflow:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40683793540 (job `122800889689`): **SUCCESS**. Reviewer authored both numerical challenges and real Chromium browser test, executed against a PR merge checkout of unchanged frozen WP7 application code and review-only files.
- **Reviewer workflow actual merge checkout SHA:** `054357153f2013df46ae547ba90d8af8aa0f0f46` (from independently downloaded `checkout-sha.txt`). Git tree `473094d239ecc0258c9b8edd203efc38131a6ebe`; baseline tested WP7 source tree `e2362c6123fb41e543264035ed2a40f743c46547`. Source-tree differences are reviewer scripts/workflow and six Markdown-only developer reports; **WP7 application and underlying scientific code are unchanged relative to exact tested source `4fc1bc3...`**.
- **Reviewer artifact:** `12813368786`, full ZIP SHA256 independently recomputed `3b59c38a6151337a725874b1e143c4bbe48e2500c846cab260580df1aac2eb2d` matching GitHub metadata. All **56/56 internal SHA256SUMS entries independently verified**. Evidence includes `independent-challenges.log`, `independent-browser.log`, `browser/result.json`, complete browser-generated WP3 ZIP and restored campaign/run store, three Chromium screenshots, Streamlit server log, Python/dependency provenance, and `regressions.log`.
- **Independent numerical challenge suite:** `review/wp7_independent_challenges.py` **IR01–IR07 all 7 passed**, run at the 4096-cell qualified fixture where needed; actual feasible candidate, infeasible mass, 30/31/31.000001 kg/m² constraint sweep, invalid/missing/forged/overwrite rejection, **fresh separate-process WP4 numerical replay of three candidates**, byte-deterministic repetition, three-class WP3 search, ZIP restore with numerical recomputation, ZIP payload tamper rejection. No new model/physics code written.
- **Independent real-browser WP3 usability test:** `review/wp7_independent_browser.py` **PASS** using real headless Chromium against a live fresh Streamlit server, not AppTest or HTTP health alone. Generated three architecture classes, persisted and inspected WP3 ledger, **downloaded real 742,698-byte ZIP through UI**, uploaded it via file picker, clicked Verify and restore, recomputed restored numerical evidence, **shut down and restarted Streamlit**, reopened restored campaign in real browser and selected candidate. Archived `browser/result.json`: `status=passed`, architectures `gradient/homogeneous/layered`, `restore_replay=passed`, `restart_verified=true`; screenshots and actual restored files preserved. **WP7-IR02 CLOSED**.
- **Fresh independent inherited foundation/recovery suite:** **357/357 PASSED** in 60.48 seconds, Python 3.12.15, `pip check` clean; frozen foundation lock plus pinned Streamlit/Playwright. This is review execution, not reuse of implementation's 357-test report.
- Reviewer first CI `40683335781` stopped before tests because shallow checkout omitted ancestor; second `40683425201` exposed an overstrict reviewer assumption that 128-element *preview* would meet 4096-element qualified feasibility; third `40683537767` executed seven numerics **PASS** but full regression collection failed solely because reviewer runner omitted Streamlit. Review-workflow-only corrections made; **none were WP7 application or solver defects**. Also completed independent numeric/regression run `40683663278` (artifact `12813892747`) separately passed 7/7 numerical probes + 357 regressions; independently verified ZIP SHA256 `d51c0fa00bfca3d58575a6252caba5b7e3cb63729c385caf0b411ed6ad4bed85`, **9/9** internal hashes.

### Superseding gate and finding dispositions

| Gate | FINAL | Evidence / outstanding limitation |
|---|---|---|
| **Gate 1 Functional user release** | **BLOCKED** | WP4 real-browser flow and newly independent WP3 real-browser ZIP restore/restart both succeed; however there is **no user-facing candidate transfer from multi-architecture WP3 search into WP4 estimated-achieved feedback/revision** and no demonstrated cancellation from the new WP7 D1 interface. The original complete integrated D1 workflow and cancellation checklist require resolution, not an invented combined Pareto. |
| **Gate 2 Independent challenge testing** | **PASS** | Executed independent IR01–IR07, independent real-browser journey, 357 regression tests and five independent archived-data challenges; negative/inconclusive and unsupported cases preserved. |
| **Gate 3 Provenance, reproducibility, scientific assurance** | **PASS for bounded source and evidence** | Verified exact tested WP7 SHA and later docs-only changes, developer artifact 67/67 plus independent artifact 56/56 hashes, fresh reviewer Python 3.12 environment, separate-process numerical replays, honest scientific limits. This is bounded computational/engineering software verification, **not** measured physical validation or external numerical physics benchmark. |

| Finding | FINAL |
|---|---|
| WP7-IR01 — integrated candidate-to-manufacturing workflow | **OPEN — release blocker** |
| WP7-IR02 — browser WP3 download/upload/restore/restart | **CLOSED — independently executed** |
| WP7-IR03 — independent numerical challenge execution | **CLOSED — 7/7 independently executed, 357 regression pass** |
| WP7-IR04 — user-facing cancellation in D1 journey | **OPEN — major; needs demonstrable accepted workflow or explicit restriction** |
| WP7-IR05 — historical WP6 final reviewer report provenance | **OPEN — minor documentary traceability** |
| WP7-IR06 — two-constituent caption versus mixed catalogue | **OPEN — informational UI clarity** |

### Formal release disposition

**WP7 remains NOT READY FOR D1 RELEASE APPROVAL solely on Gate 1's integration and cancellation requirements.** The source **passes independent numerical challenge, restart/ZIP UI and evidence integrity**. No P1 or V1 physical-science issue is an additional D1 gate. The minimal WP7 correction brief is: document/prove a continuous candidate-handoff and manufacturing-feedback experience for at least one chosen WP3 proposed design **without silently pooling intended vs achieved Pareto**, and prove cancellation/recovery as part of a coherent release-user walkthrough; alternatively place a precise bounded-scope exception before the owner for explicit approval. If implementation changes, new source SHA, fresh targeted UI/numerical regression and independent recheck are compulsory. Never merge PR #16/#17 or tag before release approval.
