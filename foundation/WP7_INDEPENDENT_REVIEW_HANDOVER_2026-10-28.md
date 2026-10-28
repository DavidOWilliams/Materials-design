# Independent WP7 Gate 3 Review Instructions

Independent reviewer must check implementation PR #16 against accepted WP6 implementation 1f89c2d1bf64b669ca98b81f4305d20d08104e5c and exact proposed WP7 tested SHA 4fc1bc3bd07de146460be1729469c7ea1e35969c. Do not substitute governance PR #12 documentation HEAD, CI merge checkout, or main. No release tag or merge is authorised.

Check real source diff and unchanged WP1/WP2 numerical and WP3/WP4 search, eligibility and manufacturing logic. Verify all three architecture classes are actually generated from the UI and carry a common numerical comparison context. Confirm intended-only WP3 Pareto is neither relabelled manufacturing-feasible nor compared to WP4 achieved-state Pareto.

Review focused tests, full regressions, full-resolution examples, separate-process replay, ZIP SHA256SUMS (nonempty, byte-verified), forged/tampered dossiers, invalid input/overwrite, and restart/restore. In a fresh environment launch Streamlit, inspect WP3 candidate/constraints/Pareto, WP4 feedback revisions and limits, upload/download ZIP, selection and export; record usability failures. Chromium, AppTest and health checks are separate evidence classes. Review final source dependency freeze and source SHA.

Check ten items of Material System Implementation Plan v2, particularly three architecture comparison, three objectives and units, binding feedback redesign, no-feasible outcome, numerical references, sensitivity, transparent evidence status, independent persistence/replay, full dossier provenance and runnable instructions. Decide whether two separately bounded scientific comparison contexts suffice for D1 or require further integrated functionality.

Record each reviewer finding, severity, test citation, pass/fail and explicit Gate 1/2/3 dispositions. Preserve negative evidence, and require source-specific retest after any code changes. No implied real ceramic manufacturing validation, P1 superiority, V1 acceptance or production readiness. Reviewer must be separate from implementation author; this report is NOT independent acceptance.
