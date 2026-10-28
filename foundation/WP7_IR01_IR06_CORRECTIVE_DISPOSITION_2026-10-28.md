# WP7 independent findings — targeted implementation response (28 October 2026)

Original independent review: PR #17, https://github.com/DavidOWilliams/Materials-design/pull/17 ; reviewer execution 40683793540; independent evidence archive 12813368786. Reviewed WP7 implementation SHA `4fc1bc3bd07de146460be1729469c7ea1e35969c`. Gate 1 BLOCKED, Gate 2 PASS, Gate 3 bounded PASS; D1 release NOT APPROVED. This document is an implementation response, not a replacement or alteration of the independent report.

| ID | Original severity | Corrective disposition |
|---|---|---|
| WP7-IR01 | Blocking | Implemented narrowly: select a completed original WP3 gradient with exactly scenario_A and scenario_B, verify original candidate/run/ledger and identical supported WP4 material and duty context, construct new WP4 intended baseline, map to synthetic estimated achieved-state under explicit scenario, run accepted feedback/revision, store source-to-dossier hash lineage. Homogeneous, layered and third-catalogue selections are **rejected**, not re-labelled. WP3 original and WP4 newly computed Pareto are never pooled. This is a restricted supported gradient handoff rather than general multi-architecture process optimisation. Requires independent retest. |
| WP7-IR02 | Closed | Independent Chromium ZIP download/upload/restart success retained, not re-opened. |
| WP7-IR03 | Closed | Independent numerical challenges and 357 regressions retained; run affected tests at new SHA. |
| WP7-IR04 | Major | Integrated WP7 tab now runs checkpointed selected-design campaign, cooperative candidate-boundary cancellation, journal inspection, and deterministic resumption into new immutable dossier. Original candidate source verified again before resumption; no mid-solver cancellation claimed. Requires real-browser and independent review. |
| WP7-IR05 | Minor | Historical WP6 provenance gap remains OPEN: original final independent Gate 3 record is not available in the project source. The 28 October governance transcription `foundation/WP6_FINAL_ACCEPTANCE_PROVENANCE_2026-10-27.md` explicitly states its limits. Do not fabricate an original reviewer record; link it when available. |
| WP7-IR06 | Information | Corrected WP7 header/caption to identify WP3 three-constituent A/B/C catalogue, versus WP4 two-constituent A/B feedback. |

## Scientific boundary
The candidate handoff intentionally *does not* pretend the WP3 three-member property pack is identical to the WP4 two-member model. It re-contextualises a fully typed, original A/B gradient design and evaluates a new WP4 intended baseline and estimated-state process. An original WP3 eligibility flag (including false) is preserved in lineage, and no eligibility is silently upgraded. All results are synthetic, not measured physical ceramics. Supported duty, objectives, constraints, solver, A/B property records, mesh and mass ceilings must agree, otherwise the operation fails closed.

## Acceptance gate
PR #18 is an implementation correction, not an owner-approved scope exception. Dedicated `test_wp7_ir01_ir04.py` plus WP7 workflow and independent browser extension are required. Preserve original WP7 source, reviewer artifact and prior failures. Do not merge, tag, or self-declare independent Gate 1 closure.

## Executed corrective qualification — 28 October 2026

**Exactly tested corrective application SHA:** `c8f0292351553129fbcbdac3bd4f7a84a39365f9`. **CI run:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663, **SUCCESS**. Python 3.12.15 on Ubuntu; clean install + dependency checks successful. New and existing focused tests: **10 passed**. Entire foundation/recovered suite: **360 passed**. WP3/WP4 synthetic 4096-element reproducible examples: **PASS**, three separate Python-process replays. Existing WP7 real Chromium test: **PASS**. New WP7 IR real Chromium test: **PASS**, selecting an original completed A/B gradient from WP3, evaluating/saving new WP4 scenario, verifying source provenance, inspecting the journal, and recovering/replaying a saved independent WP4 dossier. These browser outputs are present in the archive, including `wp7-ir01-browser.png`, `wp7-ir04-browser.png`, `selected-wp4.json`, source-hash manifest and `selected-wp4-recovered.json`.

**Evidence archive:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40686565663/artifacts/12815911040, artifact ID **12815911040**, size **4,886,481 bytes**. ZIP SHA256 **456e0211e8dd8c4b9c639857a3ed02b471836cce1395be2acf383b57c7e37c0e**. Workflow's SHA256SUMS verification succeeded. Earlier failing attempts 40685691836 (natural stop vs requested cancellation) and 40686044140 (old title locator) are retained separately and do not provide a PASS.

**Corrective implementation qualification:** WP7-IR01 and WP7-IR04 are **implemented and implementation-tested; awaiting independent reviewer repeat/disposition**. WP7-IR02 and IR03 remain independently closed. WP7-IR05 remains OPEN, historic provenance record not found. WP7-IR06 is corrected in the interface and tested. Independent Gate 1 has NOT been re-approved, nor is release authorized. No merge or tag.
