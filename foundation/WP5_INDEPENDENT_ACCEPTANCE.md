# WP5 independent finding disposition and bounded D1 acceptance

Date: 26 October 2026. Independent reviewer: separate ChatGPT review session, not the implementation chat. This is software/evidence review, not independent experimental or scientific expert validation.

## Disposition

**WP5-IR2 CLOSED — independently verified.** The strict positive-integer budget check precedes journal initialization. All ten challenge tests passed at exact tested source `4078a83dc11e14703ff6cc03f5b62f4e48879d14`. The prior WP5-R1 disposition remains CLOSED at `ccbca12dc3ff049a27d53fa77caf0db21d10e4d5`.

**Gate 3 closed for the documented bounded D1 WP5 scope.** Functional and challenge evidence support acceptance of that scope. This supersedes earlier “awaiting independent closure”, “Gate 3 OPEN” and “not independently accepted” statements in historical WP5 checkpoints/submissions. No remaining blocking finding from this targeted review. No merge or WP6 implementation was performed.

## Exact identities

- Source correction: `dd0bc5551cd630ff3ba1276564ab43f41fa4d81a`.
- Test addition: `42684f6de4db088126c944482bce94417e22761d`.
- Directly tested source/workflow commit: `4078a83dc11e14703ff6cc03f5b62f4e48879d14`.
- Developer CI PR merge checkout: `326598004be79f26184b43dcf2897b9af9b91bfd`.
- Documentation head examined before this disposition: `df620c5d3bf276d025200f99cc62c760e227970a`. Its differences from tested source are confined to two Markdown files.
- This disposition is committed separately as documentation/evidence only. Its containing commit is NOT a newly tested implementation. The tested source SHA above remains authoritative.
- WP4 tested baseline `beaf8a586c358ae04549d25c1bb7fbf8cd3f2c4b`, acceptance `1805811acdafacd66ba3574e8cb45c59bebdd8e5`, preservation `bb67e51029c5479361c59cea0b73b6bb722826f1` remain unchanged.

## Independently executed results

Clean detached worktree at the tested source; clean again after execution. Reused the isolated review Python 3.12.14 environment established for the previous review (not a newly rebuilt environment this time). Dependency health passed; actual freeze is preserved, including Streamlit 1.40.2 and packaging 24.2. The combined UI environment differs from the foundation lock's packaging 26.3.

1. `PYTHONPATH=foundation <review-python> -m pytest foundation/tests/test_wp5_service.py -k wp5_ir2 -vv --tb=long`: **10 passed, 19 deselected**, exit 0.
2. `PYTHONPATH=foundation <review-python> -m pytest foundation/tests recovered_wp0 -q`: **335 passed**, exit 0, 74.97 seconds.
3. Separately authored probe: eight invalid budgets (`0`, `-1`, `True`, `False`, `1.0`, `1.5`, `"1"`, `None`) each rejected with **no files or directories anywhere beneath a fresh temporary root**. This independently confirms no journal, manifest, attempt sidecar or newly created parent directory.
4. Valid retry at the exact rejected path succeeds. Cancellation after one candidate, recovery reusing one candidate, and numerical replay pass. Attempted overwrite leaves all existing file hashes unchanged. Saved-brief mismatch leaves the filesystem unchanged.
5. Historical sensitivity check: copied the current test module outside the old checkout and ran only `-k test_wp5_ir2` with the unchanged `ccbca12...` source on PYTHONPATH: **9 failed, 1 passed, 19 deselected**. The eight no-mutation cases and retry case detect the original defect; the pre-existing saved-brief mismatch behaviour already passes. This expected failure is evidence of regression sensitivity, not a failure at the corrected SHA.

## CI corroboration and limits

Independently inspected raw job log for [run 40331607545](https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607545), job 121602170546: checkout `326598004be79f26184b43dcf2897b9af9b91bfd`, Python 3.12.15, 10 targeted tests, 44 WP5 tests and 335 foundation tests passed. Job/step conclusions also confirm successful browser and numerical review steps. All four job conclusions for [WP3 run 40331607599](https://github.com/DavidOWilliams/Materials-design/actions/runs/40331607599) were success.

This targeted closure did not rerun live Chromium locally; that was independently exercised for R1, and the narrow new change is a service-entry guard plus tests/workflow/docs. The full corrected-source suite includes Streamlit interaction tests. No claim is made to have downloaded or hash-verified the CI ZIP archives. The independent evidence files below are preserved directly in Git, separately from CI artifacts.

## Scope and carry-forward limitations

- Intended design, estimated achieved state and measured evidence remain distinct. Unknown measured manufacturing evidence stays unknown. D1 is not V1 physical validation.
- Duty-description changes establish brief identity propagation, not qualification of new physical boundary conditions. Unsupported scientific edits remain rejected.
- Cancellation is at candidate boundaries using a selected threshold; no live asynchronous stop inside a solver or mid-kernel restart is accepted.
- No new scientific model, ceramic experiment, causal superiority, general-purpose Vision completion or unrestricted design capability is established by WP5 acceptance.
- Combined UI dependency locking remains a nonblocking reproducibility improvement.

## Evidence and next step

Evidence: [independent WP5-IR2 files](evidence/wp5-ir2-independent/), including the ten-test log, full-test log, separate probe and output, historical sensitivity log, dependency freeze and SHA256 manifest. The prior R1 review archive hash is `3990a70d970c5da5854d58a5f286af6fb77edbcc3da7213ce7904d4e97dcc898`.

The next programme work can proceed from this accepted bounded WP5 baseline under the implementation plan. Keep the exact tested implementation distinct from acceptance documentation and retain these limitations in the handover. PR #6 remains draft and unmerged; acceptance is not a merge action.
