# WP7 Functional Verification — Gate 1

Date: 28 October 2026. Proposed tested source: 4fc1bc3bd07de146460be1729469c7ea1e35969c. Accepted WP6 source: 1f89c2d1bf64b669ca98b81f4305d20d08104e5c.

The new foundation/tests/test_wp7_d1_demo.py exercises the actual Streamlit WP4 buttons (generate/save, inspect, recompute), tests immutable dossiers, invalid inputs and separate-process replay. The new foundation/tests/test_wp7_mixed_architectures.py covers WP3 homogeneous, layered and gradient candidates; it additionally runs genuine Streamlit AppTest widget interactions on the WP3 tab, checks numerical Pareto and replay. foundation/tests/wp7_browser_acceptance.py exercises real Chromium against a live Streamlit server and archives screenshots and browser logs. HTTP health is a separate limited check.

The workflow https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977 is configured to checkout the exact implementation source, install Python 3.12 and UI dependencies, run the two focused test files, full regressions, build full-resolution examples, and run Chromium. At report creation its focused test step has succeeded, but the complete workflow is IN PROGRESS. Thus Gate 1 is NOT YET PASSED; do not transfer successful steps of older source revisions.

Earlier source 823b4c49d5396f2af28dcd307551e764b336f1be: WP7 tests, regressions and full-resolution sample generation passed, but browser interaction failed in run 40672057889. A 28 October Chromium diagnostic run 40672883410 found a missing state commit between entering workspace and submitting the campaign. The current browser script explicitly commits workspace input and waits for Streamlit rerender. Final result still requires inspection of the new run.

Unqualified: comprehensive human usability and WP3 ZIP upload through real Chromium. A separate human/independent browser walkthrough is part of Gate 3. No release acceptance claimed.


## Final source-specific evidence addendum — supersedes pending status above

**Gate 1 automated functional qualification: PASS (bounded scope)** on implementation SHA 4fc1bc3bd07de146460be1729469c7ea1e35969c, GitHub Actions run 40673439977, job 122765726102, conclusion success. Python 3.12.15 on Ubuntu. Exactly **7/7 new WP7 focused tests passed**, including two actual Streamlit AppTest WP3/WP4 journeys. Real Chromium Playwright job completed successfully at this exact source SHA: rendered launch, edited workspace committed, WP4 campaign generated a **3-candidate** dossier, verified persistence, selected inspection and numerical replay; screenshots and browser logs archived. Clean installation, startup and full regression succeeded. This is not a standalone WP3 Chromium upload test: that remains an explicit independent UI walkthrough requirement. No independent Gate 3 conducted.

Evidence artifact **12808843984**, SHA256 ZIP **6c660389e94ed6873b4f8931f5647458159fbf2d989087a0b375e3476250b028**, https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977/artifacts/12808843984. Browser issue fixed in implementation and tested rather than waived. Gate 1 status now PASS for the tested bounded automated journey, with noted independent usability follow-up.
