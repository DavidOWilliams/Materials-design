# D1 v0.2 defect register and verification ledger

This document distinguishes **observed**, **corrected in source**, and **retested at exact SHA**. Not a scientific or independent acceptance declaration.

## Defects

| ID | Severity | Reproduction and actual result | Expected result / scientific implication | Corrective change | Disposition |
|---|---|---|---|---|---|
| D1-UI-001 | High | Launch a workspace containing `d1-example.json`; press Tab 1 Generate. Backend rejects with `Dossier already exists` after initiating user workflow. | Explain collision before execution; preserve immutable dossier and new distinct run. | Tab 1 pre-check; disable action; verify/inspect existing dossier; offer available `-run-NNN` filename. Original backend lock unchanged. | Source corrected; browser retest pending |
| D1-UI-002 | High | Regenerate WP3 into `mixed-architecture`; existing store can collide. | Detect existing campaign directory before run; offer new directory and existing ledger inspection. | WP3 pre-check and new-directory selection. | Source corrected; browser retest pending |
| D1-UI-003 | High | WP4 selected handoff, cancellation journal, recovered dossier, restored WP3 ZIP or copied dossier use existing destinations. | Never overwrite dossier, journal and companions; show actionable preflight. | Preflight for handoff `*.handoff.json`, journal `*.manifest.json` / `*.attempts.jsonl`, recovery, imported and restored files. | Source corrected; challenge retest pending |
| D1-UI-004 | High | Earlier GitHub WP3 workflow attempted to import `d1_visuals.py` without pandas installed in scientific-only environment; failed before tests. | Scientific tests should not import GUI dependencies. | Moved source selectors and destination checks to `d1_visual_data.py`; standalone unit tests import only this pure module. | **WP3 workflow success observed** for interim commit `40fee62c`; final SHA retest pending |
| D1-UI-005 | High | Existing WP7 CI UI tests looked for legacy button labels and failed (8 passed, 2 failed at interim `40fee62c`). | Preserve accepted automated UI contracts or update tests explicitly. | Restored existing button names, retaining immutable conflict controls; updated independent browser selectors. | Source corrected; final WP7 retest pending |
| D1-UI-006 | Critical scientific interpretation | Chart source could overlay incompatible coordinate systems or connect discontinuous layered interfaces. | Overlay only compatible and scientifically supported profiles; otherwise explain unknown. | Compare coordinate systems, constituent IDs and basis; disable unsupported layered overlays; source-matched points only for differences. | Source corrected; graphical browser/source verification pending |
| D1-UI-007 | Medium | First-user screens previously opened with technical JSON and no immediate graphical guidance. | Plain-language challenge, provenance behind disclosure, charts and exact numerical tables. | Existing D1 v0.2 graphical components and revised screen text. | Source corrected; usability validation pending |
| D1-UI-009 | High verification integrity | Dedicated Chromium script on interim source used a stale button selector after new-filename suggestion, failing after reproducing immutable collision. | Browser test must use actual labels, not falsely fail/pass feature. | Replaced all stale selectors in `d1_v02_browser_challenge.py`; previous run 40953991312 proves screenshot capture before failure but not full journey. | Corrected in source; final Chromium retest pending |
| D1-UI-010 | High verification integrity | Baseline comparator CI failed before running numerical comparison: `fatal: invalid reference: d1-v0.1.0` in shallow checkout (run 40954823890). | Must fetch immutable release tag explicitly to perform genuine two-process comparison. | CI now fetches tag ref before adding baseline worktree. | Corrected in source; final comparator retest pending |
| D1-UI-011 | High verification integrity | Original WP7 Chromium script expected v0.1 title and labels after v0.2 redesign; earlier run 40953991247 browser gate failed while preceding scientific gates passed. | Update presentation-only browser assertions without weakening numerical checks. | Updated `wp7_browser_acceptance.py`, plus `wp7_ir_browser_acceptance.py`. | Corrected in source; final WP7 browser retest pending |
| D1-UI-008 | Medium | Previously no beginner Codespaces Python 3.12 instructions. | Runnable environment without replacing system Python. | `D1_V02_CODESPACES_FIRST_USER_GUIDE.md`. | Documentation committed; Codespaces execution pending |

## Evidence actually inspected

- Interim GitHub Actions commit `a3a86cc8b371c40405a715cc0a6275fcef59fbc5`: **WP3 failure** (pandas unavailable in pure-science test context), **WP7 failure**, **WP4 success**.
- Interim GitHub Actions commit `40fee62c10200238b7b442f3eacb4e0c05c31fb6`: **WP3 success**; **WP7 failed** due two legacy UI control labels, while other eight WP7 focused tests passed. This is not final acceptance evidence.
- Tests and browser scripts in this branch are committed but their final run statuses must be obtained from GitHub Actions for the final implementation SHA.

## Execution required at final SHA

1. Validate `test_d1_visuals.py` under Python 3.12.
2. Run complete `foundation/tests` and applicable WP1–WP7 suites.
3. Generate 4096-element nine-proposal WP7 examples into unused workspace and compare with accepted baseline.
4. Execute actual Chromium Playwright D1 workflow and retain all browser screenshots.
5. Verify actual chart coordinates vs full source tables, test unsupported handoffs and cancellation/recovery in actual UI.
6. Compare real browser widths, keyboard focus, labels and user messages.
7. Store environment freeze, source hash, artifacts and SHA256SUMS with job links.
8. Repeat after any code fix; only the **final tested source** can be the acceptance candidate.

**Gate status: NOT VERIFIED** until successful final SHA evidence and independent review. Draft PR must not be merged or tagged.

## Final source retest and disposition — 2026-10-29

The exact implementation checkout `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c` passed [dedicated GitHub Actions run 40957223174](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174) (job conclusion **success**). Unit tests **7 passed**, full foundation scientific tests **342 passed, one warning**, exact WP3/WP4 baseline comparison **matched**, both real Chromium first-user and selected-gradient handoff/recovery scripts **passed**, and SHA256 evidence archive uploaded as artifact **12934327177**.

The interim stale-selector and shallow-tag CI failures D1-UI-004, 005, 009, 010 and 011 are **closed by executed final-source regression**; they are not outstanding product failures. D1-UI-001, 002 and 003 are **closed for tested immutable-collision workflows**, with actual AppTest and Chromium evidence. D1-UI-006 is **closed for implemented mismatch guards and unit/chart presentations**, but full independent review of all plotted coordinates remains an explicit acceptance task. D1-UI-007 and 008 are **implemented, with residual medium usability and environment-coverage limitations** below.

An additional test-harness finding D1-UI-012 (medium verification integrity): in an intermediate real-browser handoff run, the checkpoint journal was asserted immediately after button activation while Streamlit was still running. A bounded browser wait was added; final-source browser checkpoint/recovery test passed. No overwritten source or backend regression was observed.

**Unresolved critical findings:** none identified in executed implementation-team tests.  
**Unresolved high findings:** none identified in executed implementation-team tests.  
**Residual medium/low:** four inherited tabs rather than a wholly new seven-stage navigation; selecting candidates through a labelled control rather than directly clicking scatter markers; complete manual contrast and assistive-technology audit not conducted; independent scientific review of all graphical samples still required. These limitations must not be represented as final acceptance.

Evidence ZIP SHA256: `f6f891aa72c458cfc59596968bfc0c6f6980185445498f9e64d2b5487d75feb9`. Original test artifacts, screenshots, log captures, numeric comparisons and SHA256SUMS manifest are preserved at [GitHub Actions artifact 12934327177](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174/artifacts/12934327177).
