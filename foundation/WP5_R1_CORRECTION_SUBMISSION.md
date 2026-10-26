# WP5-R1 correction submission for independent closure testing

**Finding:** WP5-R1 — checkpointed Streamlit campaign did not consume the selected immutable saved brief.
**Submission status:** implementation corrected and developer verification passed; **independent closure NOT claimed**. Gate 3 OPEN.
**Previously frozen WP5 implementation:** `0c93ea2c91f2f6f0d29f0024d12722db9cf6931f` (unchanged historical tested source).
**Corrected implementation + finding-specific test/workflow HEAD tested:** `ccbca12dc3ff049a27d53fa77caf0db21d10e4d5`.
**Actual GitHub Actions PR merge checkout:** `336ab2533d2f4297b17c92481b83ee4090e04103`, incorporating correction HEAD into base `f3e6cfc7f7e9ed885ce681814c0927fc421163c8`.
**Source correction commit:** `d52a1a5e563f2f0285c59b58d0654ae3636a2f33`.
**Branch:** `wp5-application-2026-10-26`; draft PR #6. No merge, force-push or WP4 baseline movement.

## Finding-specific change

File `foundation/wp5_app.py`, in the **checkpointed** `Start checkpointed campaign with cancellation` button handler:

```diff
+ selected_brief = open_brief(brief_path) if brief_path else None
+ if selected_brief is not None and selected_brief.evaluation_budget != int(budget):
+     raise ValueError("Saved brief evaluation budget must match campaign budget")
  record = execute_journal(journal_path, elements=elements, mass_limit=mass_limit,
                           layer=layer, feed=feed, budget=int(budget),
                           feedback=feedback, process_version=int(version),
+                          brief=selected_brief.model_dump(mode="json") if selected_brief is not None else None,
                           cancel_requested=lambda: len(recover_candidate_checkpoints(journal_path)) >= int(cancel_after))
```

The UI resolves the selected immutable brief via the existing integrity-checked `open_brief` and rejects a mismatched budget before any journal creation. The existing service `execute_journal` independently validates the same budget and constructs the WP4 journal using `prepared_inputs(..., brief=...)`. The WP4 journal manifest retains the revised baseline inputs and the recovery path reuses that frozen manifest. No WP4 numerical core or scientific model was changed.

## Finding-specific tests (new; not weakened)

`foundation/tests/test_wp5_streamlit_interaction.py`:

1. `test_wp5_r1_revised_saved_brief_checkpoint_cancel_recover_import_replay` — starts from the WP4-supported fixture, makes a **real changed duty string** and evaluation-budget revision, saves a new immutable brief, selects it through the Streamlit UI, starts checkpointed execution, cancels after exactly one completed candidate, verifies the manifest's saved duty and typed brief hash, resumes, verifies reused candidate count, verifies recovered dossier brief hash, conservative export intended-baseline identity, byte-identical portable import, imported brief hash and numerical replay.
2. `test_wp5_r1_incompatible_saved_budget_creates_no_journal` — selects a revised duty/budget brief but sets an incompatible campaign budget; asserts visible UI error and **absence of journal, manifest and attempt sidecar**.

No mocks of the numerical or WP4 services. The original UI and service tests remain active. No test weakening.

## Actual CI evidence

**Primary source-pinned run:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40315521412 — **SUCCESS**.

- WP4 focused regressions: **85 passed**.
- WP5 focused, service and Streamlit UI interaction tests: **34 passed**.
- WP5-R1 finding-specific interactive tests: **2 passed**, 4 deselected by the finding-specific `-k wp5_r1` selection (all 6 UI tests already included in 34 passed).
- Live Chromium Streamlit browser acceptance: **passed**.
- Full foundation/recovery regressions: **325 passed**.
- WP4 portable reopen/recompute, higher resolution, sensitivity, paired comparison, interruption/recovery and evaluation accounting: all workflow steps passed.
- WP3 compatibility run https://github.com/DavidOWilliams/Materials-design/actions/runs/40315521408 — **all four jobs successful**.

**Raw finding-specific artifact:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40315521412/artifacts/12645949083 — `wp5-r1-336ab2533d2f4297b17c92481b83ee4090e04103`, including revised saved brief, original journal chain, integrity-checked manifest, attempt events, recovered dossier, imported dossier, expected brief content hash, focused pytest log and exact actual checkout SHA.

**Live browser artifact:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40315521412/artifacts/12646941446 — Chromium screenshot, browser-produced dossier, runtime dependency freeze and Streamlit log.

**WP4 qualification artifact:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40315521412/artifacts/12647265882 — source-pinned WP4 numerical qualification evidence and actual checkout identity.

**Raw logs:** https://github.com/DavidOWilliams/Materials-design/actions/runs/40315521412 (job `121547033360`); WP3 run above.

**Compare corrected implementation against frozen source:** https://github.com/DavidOWilliams/Materials-design/compare/0c93ea2c91f2f6f0d29f0024d12722db9cf6931f...ccbca12dc3ff049a27d53fa77caf0db21d10e4d5
**Finding-specific source patch:** https://github.com/DavidOWilliams/Materials-design/commit/d52a1a5e563f2f0285c59b58d0654ae3636a2f33

## Acceptance boundary and reviewer instructions

This submission is **developer-verified, not independently accepted**. Gate 3 remains open pending the reviewer's independent reproduction and disposition of WP5-R1. The corrected implementation is distinct from the prior frozen source; this report is a subsequent documentation-only commit and must not be substituted for the tested SHA.

Reviewer should independently inspect the raw revised brief, compare its typed content hash to the journal manifest and recovered/imported dossier, verify one-candidate checkpoint reuse and numerical replay, and reproduce budget mismatch failure before journal creation. Compare actual checkout SHA with the source correction SHA and base merge. Confirm WP4 immutable baselines remain intact.

**WP4 immutable anchors:** tested numerical core `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b`; acceptance docs `1805811acdafacd66ba3574e8cb45c59bebdd8e5`; evidence preservation `bb67e51029c5479361c59cea0b73b6bb722826f1`.

No empirical ceramic measurements are introduced. D1 remains a bounded synthetic demonstration, not V1 physical manufacturing validation.
