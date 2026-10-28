# WP7 qualification gates and independent release handover — current controls

**Accepted pre-WP7 baseline:** `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`. WP7 implementation draft PR #16, isolated from governance PR #12 and verification PR #13. Do not substitute merge checkout SHAs for actual source checkout. The final tested implementation SHA, run references, archive identities and disposition must be recorded in the dated WP7 completion report **only after actual execution**. No source code changes permitted after a PASS without retesting affected tests.

## Gate 1 — actual runnable interface
1. Clean Python 3.12 setup using `foundation/setup.sh` + Streamlit 1.40.2; freeze and pip-check.
2. `foundation/tests/test_wp7_d1_demo.py` actually interacts via Streamlit AppTest, including WP4 generation/inspection/replay. `foundation/tests/test_wp7_mixed_architectures.py` tests the WP3 integrated service path, three architecture classes, ZIP restore and separate-process recompute. This is *not* a real Chromium test.
3. `foundation/tests/wp7_browser_acceptance.py` drives a real running Streamlit process in Chromium; capture initial/final screenshots, raw browser/server logs. Browser coverage is currently bounded to the WP4 user journey; WP3 mixed-architecture rendered interaction additionally needs specific independent walkthrough or browser extension.
4. Restart/reopen/copy/restore, selected candidate and evidence detail, raw export; no claim based on HTTP health alone.

## Gate 2 — challenges and reproducibility
- Valid mass limit 31, impossible mass limit 1; 4096 element evidence archive includes WP3 three architectures and WP4 representative/infeasible examples.
- Invalid budget, existing path, tampered WP4 checksum, forged WP3 ZIP payload, path traversal and replay in separate Python process; unknown status must stay unknown, never promoted to eligible.
- Numerical/reference regressions `foundation/tests recovered_wp0`; verify exact WP7 source, preserve prior WP2/WP6 evidence.
- Create full example archive from `foundation/wp7_create_examples.py`, independently check SHA256SUMS nonempty, derive evidence hashes from bytes. Record output SHA, seed, budget, system version, environment, workflow identity and limitations.

## Gate 3 — genuinely separate reviewer
Verify every requirement in Implementation Plan v2; inspect actual PR #16 diff from accepted WP6, all tests, browser and failure evidence, portable ZIP, independent-process recompute and scientific labels. Review whether the separate WP3 numerical-only and WP4 gradient-feedback demonstrations meet bounded D1 scope, or require one unified user dossier before D1 release. Check no cross-context Pareto comparison and no invented V1 evidence. Sign finding dispositions and explicit go/no-go **independently**. The implementation author cannot self-declare independent acceptance.

## Outstanding issues pending evidence
- **High:** Independent WP7 Gate 3 acceptance not performed. No tag/merge.
- **Medium:** WP3/UI and WP4/UI are separate scientific comparisons; no manufacturing-aware Pareto across all three architectures. Whether this meets original D1 checklist needs reviewer judgement.
- **Medium:** User-facing WP3 ZIP browser import is currently implemented, but needs actual upload/multi-process validation and independent UI review.
- **Medium:** Streamlit and Playwright test dependencies pinned but not fully hash locked; final freeze must be retained.
- **Scientific limits, not software bugs:** Synthetic scenario inputs, unknown manufacturing feasibility of intended-only WP3, omitted process physics, no real ceramic V1 evidence.
- **Provenance:** WP6 original final Gate 3 reviewer report still not archived; this does not reclassify the independently verified 28 October D1 integration baseline.

## Current release disposition
Only claim actual WP7 gate executions with evidence-linked result lines in a separate completion report. Until then **NOT ACCEPTED / NOT TAGGED / NOT MERGED**.
