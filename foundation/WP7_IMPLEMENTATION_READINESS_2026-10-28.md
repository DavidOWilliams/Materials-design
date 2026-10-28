# WP7 readiness and implemented scope — 28 October 2026

**Evidence starting point:** original WP6 application commit `1f89c2d1bf64b669ca98b81f4305d20d08104e5c`, verified integration runs 40666591136 and 40668433992. Existing WP5 Streamlit app and WP6 evaluation runner inspected before modifying. Governance PR #12 at `6fdfce29c29f5b4ad26b974315adb0d4cd000c9f` is distinct, draft and documentation-only after WP6; PR #13 is separate workflow work. WP7 implementation draft PR #16 starts precisely at that accepted WP6 SHA, not at a governance/merge checkout.

## Readiness mapping

| Required journey | At accepted WP6 source | WP7 work now implemented | Qualification status |
|---|---|---|---|
| Startup and synthetic example | WP5 startup and HTTP check verified | Guided D1 app, example presets, instructions | New exact-source clean-install and browser test required |
| Bounded brief | WP5 typed snapshots and WP4 supported duty/budget edits | Built-in fixture, mass constraint and saved typed brief for WP4; WP3 supported common synthetic duty | Arbitrary physical changes still unsupported |
| Search across architecture/constituent classes | WP3 engine existed, but not integrated into WP5 | UI calls accepted `run_search`: nine-slot bounded A/B/C synthetic catalogue, homogeneous/layered/gradient | WP7 direct UI testing needed |
| Manufacturing feedback and gradient revisions | WP4 campaign accepted | UI calls same accepted `execute`, preserves resolution/balance/feedback | WP7 direct UI testing needed |
| Numerical evaluation | WP2/WP6 evidence verified upstream | No numerical kernel changes; reports objective/mesh/quality/status | Full WP7 regression and example replay required |
| Constraint and Pareto | WP3 and WP4 output existed in services | Distinct qualified WP3 numerical Pareto and WP4 scenario-feasible Pareto; no cross-context mixing | Inspect unknown/unresolved at qualifying SHA |
| Candidate inspection | Raw WP5 JSON | Architecture proposal, design/evaluation, feedback, hashes, explicit exclusions | UI tests pending independent user checks |
| Immutable dossier | WP3 ledger + store and WP4 JSON persisted | WP4 download and restore, WP3 ZIP with SHA256 manifest and closed-world archive validation | Full archive/restore tests needed |
| Separate-process replay | WP3/WP4 replay engines verified | UI commands and scripted full-resolution sample builder | WP7 evidence at candidate SHA required |
| Assumptions and limits | Scientific boundaries documented | Two independent evidence classes conspicuously labelled; measured evidence never synthesised | Independent documentation check required |

## Minimality and scientific change review

New WP7 components: `foundation/wp7_app.py`, `foundation/material_core/wp7_view.py`, `foundation/material_core/wp7_search_dossier.py`, `foundation/wp7_create_examples.py`, focused/browser/challenge tests and a separate D1 GitHub Actions workflow. No modifications to WP1/2 numerical code, WP3 search/evaluation/Pareto logic, WP4 process/feedback/feasibility or WP5 service. WP7 read-only WP4 view calls the accepted strict WP3 Pareto implementation using `feasible` from WP4 records. WP3 view reopens independently verified WP3 ledgers. These remain distinct comparison contexts. New archive creation/import and UI navigation are **software/reproducibility features**, which need their own test qualification and security/integrity review, not claims of new physics.

**Remaining hard issues:** (1) independent Gate 3 review and user journey sign-off, (2) no external measured validation (V1 scope, NOT D1 blocker), (3) process assumptions and mesh/domain limitations must remain plainly unresolved, (4) WP3 heterogeneous architecture exploration and WP4 gradient process feedback are two *distinct* validated stages, not a single optimised manufacturing-aware portfolio across architecture classes, (5) WP7 browser/clean-install evidence must actually pass at the frozen SHA.

**No P1 comparator/superiority algorithms, no production engineering claims, no release tag or merges.**
