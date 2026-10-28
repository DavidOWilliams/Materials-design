# WP7 Source / Environment / Evidence Manifest

Proposed release-candidate implementation source: 4fc1bc3bd07de146460be1729469c7ea1e35969c. Accepted frozen WP6 source: 1f89c2d1bf64b669ca98b81f4305d20d08104e5c. Compare source trees, not temporary GitHub PR merge checkouts or governance documentation HEAD.

Draft WP7 source PR: https://github.com/DavidOWilliams/Materials-design/pull/16. Its target is the existing WP7 governance branch, PR #12, NOT main. PR #12 and #13 remain untouched/unmerged. No release tag.

Implementation additions: foundation/wp7_app.py, foundation/material_core/wp7_view.py, foundation/material_core/wp7_search_dossier.py, foundation/wp7_create_examples.py. Tests: foundation/tests/test_wp7_d1_demo.py, foundation/tests/test_wp7_mixed_architectures.py, foundation/tests/wp7_browser_acceptance.py. Workflow: .github/workflows/wp7-d1.yml. Original WP1/WP2/WP3/WP4/WP5/WP6 numerical, search, process, eligibility and physics modules remain untouched.

Environment: GitHub Actions Ubuntu Linux runner; Python 3.12; foundation/setup.sh with hash-locked numerical requirements; separately pinned streamlit==1.40.2 and playwright==1.58.0; full transitive freeze, pip-check and platform logs recorded. UI dependencies are pinned but not all transitive wheels hash-locked.

Full workflow run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977. Expected evidence: source-sha.txt, changes-from-wp6.txt, install.log, python.txt, platform.txt, freeze.txt and final-freeze.txt, pip-check reports, wp7-focused.log, full-regression.log, examples.log, example-dossiers directory including WP3 ledger/run-store, portable ZIP, WP4 JSON dossiers, manifests, independent-process replay evidence, browser logs and screenshots, SHA256SUMS. Nonempty SHA256SUMS must pass verification.

At initial authorship: run in progress, exact artifact ID and ZIP SHA256 PENDING. Previously verified source-specific historical WP6 artifact 12807606181 remains preserved. Prior failed WP7 runs/artifacts remain negative evidence, not erased.


## Final manifest — verified from completed workflow

Source SHA: **4fc1bc3bd07de146460be1729469c7ea1e35969c**. Actions run **40673439977** (job **122765726102**) concluded **SUCCESS**. Archive name wp7-d1-exact-source-evidence, artifact ID **12808843984**, uploaded ZIP size **3,285,296 bytes**, SHA256 **6c660389e94ed6873b4f8931f5647458159fbf2d989087a0b375e3476250b028**. Link: https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977/artifacts/12808843984.

Environment Python **3.12.15**, Linux Ubuntu GitHub runner, hash-locked foundation with separately pinned Streamlit and Playwright (full versions in final-freeze.txt). Seven focused WP7 tests passed, **357 full regression tests passed**, 4096 mesh examples and 3 separate-process replays succeeded; one true Chromium journey successful. **68 archive files** each checked by SHA256SUMS in CI; includes WP3 mixed-architecture ledger + store + ZIP and original/restored evidence, WP4 valid/infeasible dossiers, screenshots and logs. Independent auditor should separately download/recheck archive; this authorship is automated archive verification only. Earlier negative run evidence remains preserved and distinct.

The implementation/qualifying SHA above is the source baseline. Subsequent commits to these Markdown reports are **documentation-only and NOT a new tested implementation**. Do not copy the result to modified application/dependency/evidence content.
