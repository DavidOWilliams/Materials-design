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
