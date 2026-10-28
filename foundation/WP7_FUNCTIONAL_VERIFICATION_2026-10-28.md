# WP7 Functional Verification — Gate 1

Date: 28 October 2026. Proposed tested source: 4fc1bc3bd07de146460be1729469c7ea1e35969c. Accepted WP6 source: 1f89c2d1bf64b669ca98b81f4305d20d08104e5c.

The new foundation/tests/test_wp7_d1_demo.py exercises the actual Streamlit WP4 buttons (generate/save, inspect, recompute), tests immutable dossiers, invalid inputs and separate-process replay. The new foundation/tests/test_wp7_mixed_architectures.py covers WP3 homogeneous, layered and gradient candidates; it additionally runs genuine Streamlit AppTest widget interactions on the WP3 tab, checks numerical Pareto and replay. foundation/tests/wp7_browser_acceptance.py exercises real Chromium against a live Streamlit server and archives screenshots and browser logs. HTTP health is a separate limited check.

The workflow https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977 is configured to checkout the exact implementation source, install Python 3.12 and UI dependencies, run the two focused test files, full regressions, build full-resolution examples, and run Chromium. At report creation its focused test step has succeeded, but the complete workflow is IN PROGRESS. Thus Gate 1 is NOT YET PASSED; do not transfer successful steps of older source revisions.

Earlier source 823b4c49d5396f2af28dcd307551e764b336f1be: WP7 tests, regressions and full-resolution sample generation passed, but browser interaction failed in run 40672057889. A 28 October Chromium diagnostic run 40672883410 found a missing state commit between entering workspace and submitting the campaign. The current browser script explicitly commits workspace input and waits for Streamlit rerender. Final result still requires inspection of the new run.

Unqualified: comprehensive human usability and WP3 ZIP upload through real Chromium. A separate human/independent browser walkthrough is part of Gate 3. No release acceptance claimed.
