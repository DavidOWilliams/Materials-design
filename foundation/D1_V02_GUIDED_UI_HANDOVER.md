# D1 v0.2 — guided graphical demonstration (development branch)

**Status:** UI changes committed, verification pending. **Scientific source:** accepted WP7 implementation at `c8f0292351553129fbcbdac3bd4f7a84a39365f9`, tag `d1-v0.1.0`. Do not treat UI status colours as experimental qualification.

## Presentation decisions — owner-selected, 2026-10-28

- **A:** Combined material cross-section/architecture strip and constituent-vs-position graph, with expanded exact composition table (A1 + A2).
- **B:** Interactive scatter plot, separate for WP3 intended and WP4 estimated-achieved contexts, with status symbols and numerical source table.
- **C:** Intended-vs-estimated achieved profile overlay (C1), with optional pointwise difference (C3) **only if** both verified designs expose compatible recorded coordinates and constituent bases. Missing profile is reported rather than fabricated.

## Guided demonstration

From repository root, install per `foundation/D1_RELEASE_INSTALL_AND_DEMONSTRATION.md`, then:

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py
```

1. **Define challenge / run synthetic WP4 fixture.** Inspect plain-language duty and constraint table. Edit mass limit, process resolution and evaluation budget, then save to a new JSON name.
2. **Explore architectures / WP3.** Generate the deterministic nine-proposal mixed campaign, then inspect via the persisted ledger. The scatter displays **WP3 intended-state numerical** objective pairs; select a candidate ID to see its underlying architecture graph, source knots/layers and evaluation.
3. **Manufacturing / WP4.** Only a compatible qualified scenario_A / scenario_B gradient can be handed off from WP3. Select it and run a fresh WP4 synthetic estimated-state dossier. Alternatively, inspect the standalone WP4 fixture created in step 1.
4. **Compare / revise.** WP4 has a **separate** conditional Pareto comparison, candidate selection, feedback conditions and intended/estimated plots where geometry supports them. The C3 difference shows only matched recorded coordinate points; it is not a measurement. When no revision occurs the UI says so.
5. **Recover / preserve.** Use the unchanged checkpoint cancellation and recovery controls, replay original or restored dossiers, and download verified evidence ZIP/JSON. Keep WP4 `*.handoff.json` companions with their source evidence and original WP3 ledger/store.

## Interpretation

- All samples use hypothetical A/B/C ceramic constituents. No physical coupon, mixing-lag, porosity, shrinkage, sintering, CFD or manufacturing residual-stress validation is claimed.
- WP3 intended-state and WP4 estimated-achieved-state Pareto sets are never pooled.
- Every plotted numerical objective comes from an existing persisted row. Missing objective pairs are omitted, with the exact full candidate table always available.
- Architecture graph represents homogeneous constant composition, exact layered step interfaces, or explicitly declared piecewise-linear gradient knots. The architecture strip indicates boundaries, not measured microstructure.
- Blue and orange lines/labels are presentation encodings, not material-property assertions. Source file identities, original numerical quality and hashes remain available in expanded technical detail.
- No new numerical model, search policy, eligibility rule, revision algorithm or evidence source was added.

## Verification commands (not yet run in this environment)

```bash
PYTHONPATH=foundation .venv-foundation/bin/python -m unittest foundation.tests.test_d1_visuals -v
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests -q
PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py /tmp/d1-v02-examples --elements 4096 --budget 9
```

Open Streamlit with a browser and validate the complete flow against the baseline. Collect screenshot evidence for: challenge, each architecture class, WP3 scatter and exclusions, WP4 separate scatter, intended/estimated overlay, C3 differences (if available), cancellation and recovery, and restored replay. Record Python environment, source SHA, exact commands/logs and all artefact hashes.

## Independent-review focus

Verify objective keys and units separately in the two summaries, zero-truncation and the no-fabrication condition; compare the plotted source coordinates with archived JSON; check WP3→WP4 handoff and immutable companion; exercise feasible, infeasible and unresolved numerical states; check accessibility and browser interactions; independently run accepted scientific regression suite and compare representative hashed source outputs. This document **does not constitute acceptance**.

## Baseline usability assessment

The original UI presented large JSON sections, technical tabs and dense tables before helping users see material architectures or trade-offs. v0.2 adds source-based graphical inspection, clearer duty/constraints and progressive disclosure. An actual user-observed before/after timing or task-success assessment remains outstanding.

## Outstanding known limitations

- Browser end-to-end testing, screenshots, full scientific regressions and runtime dependency check not executed in this connector-only environment.
- Composition overlays are conditional on an actual WP4 estimated geometry with matched data; missing data is not filled in.
- The present screen layout retains four legacy tabs; a complete seven-stage navigation overhaul and accessible interaction testing still require work.
- Chart click-to-select is not yet implemented; selection is available through the adjacent candidate-ID selector.
