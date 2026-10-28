# WP7 Source / Environment / Evidence Manifest

Proposed release-candidate implementation source: 4fc1bc3bd07de146460be1729469c7ea1e35969c. Accepted frozen WP6 source: 1f89c2d1bf64b669ca98b81f4305d20d08104e5c. Compare source trees, not temporary GitHub PR merge checkouts or governance documentation HEAD.

Draft WP7 source PR: https://github.com/DavidOWilliams/Materials-design/pull/16. Its target is the existing WP7 governance branch, PR #12, NOT main. PR #12 and #13 remain untouched/unmerged. No release tag.

Implementation additions: foundation/wp7_app.py, foundation/material_core/wp7_view.py, foundation/material_core/wp7_search_dossier.py, foundation/wp7_create_examples.py. Tests: foundation/tests/test_wp7_d1_demo.py, foundation/tests/test_wp7_mixed_architectures.py, foundation/tests/wp7_browser_acceptance.py. Workflow: .github/workflows/wp7-d1.yml. Original WP1/WP2/WP3/WP4/WP5/WP6 numerical, search, process, eligibility and physics modules remain untouched.

Environment: GitHub Actions Ubuntu Linux runner; Python 3.12; foundation/setup.sh with hash-locked numerical requirements; separately pinned streamlit==1.40.2 and playwright==1.58.0; full transitive freeze, pip-check and platform logs recorded. UI dependencies are pinned but not all transitive wheels hash-locked.

Full workflow run: https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977. Expected evidence: source-sha.txt, changes-from-wp6.txt, install.log, python.txt, platform.txt, freeze.txt and final-freeze.txt, pip-check reports, wp7-focused.log, full-regression.log, examples.log, example-dossiers directory including WP3 ledger/run-store, portable ZIP, WP4 JSON dossiers, manifests, independent-process replay evidence, browser logs and screenshots, SHA256SUMS. Nonempty SHA256SUMS must pass verification.

At initial authorship: run in progress, exact artifact ID and ZIP SHA256 PENDING. Previously verified source-specific historical WP6 artifact 12807606181 remains preserved. Prior failed WP7 runs/artifacts remain negative evidence, not erased.
