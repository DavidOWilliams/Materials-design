# D1 v0.2 — Independent-review handover

**Disposition:** Implementation verification passed at checkout `2bc11618ed5696bce200ed8c9b5fbcdf46d0648c`; **INDEPENDENT ACCEPTANCE PENDING**. PR #22 remains draft; no main merge and no tag changes.

**CI and preserved evidence:** [Green run 40957223174](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174), [artifact 12934327177](https://github.com/DavidOWilliams/Materials-design/actions/runs/40957223174/artifacts/12934327177), ZIP SHA256 `f6f891aa72c458cfc59596968bfc0c6f6980185445498f9e64d2b5487d75feb9`. This run includes 7 display unit tests, 342 foundation tests (one warning), exact v0.1 comparison, 4096-element example, first-user Chromium Tab 1–4, and browser handoff/cancellation/recovery. Documentation-only commits after the tested checkout must not be presented as the tested implementation.

## Accepted baseline and governance

- Scientific implementation: `c8f0292351553129fbcbdac3bd4f7a84a39365f9`; release tag `d1-v0.1.0`.
- Development branch: `d1-v0.2-guided-ui`.
- All interface changes are read-only presentation or navigation controls; WP2/WP3/WP4/WP7 algorithms and replay/lineage engines remain unchanged.
- The review must use the **exact tested checkout SHA** from successful CI logs; a later documentation-only commit must not be mistaken for that source.

## Implementation deliverables

- Graphical objective scatter plots and exact tables for separate WP3 intended and WP4 synthetic estimated-achieved campaigns.
- Homogeneous, layered and piecewise-linear gradient architecture strip/profile views with exact source compositions.
- Conditional intended / estimated achieved profile overlays and source-matched position differences; absence/incompatibility is not interpolated or hidden.
- Source-backed WP4 revision lineage and explicit natural termination, budget exhaustion and cancellation explanations.
- Preflight immutable output collision detection for all four tabs, including WP4 handoff and journal sidecars. New run suggestions and existing-dossier inspection do not bypass backend integrity checks.
- New Codespaces setup and first-user guide; Vision coverage/known limitations; defect register.
- UI unit and AppTest challenge tests; actual Chromium tests; full scientific regression and baseline comparator; reusable GitHub Actions SHA256 evidence artifact.

## Independent review reproducibility

From a clean clone at the **exact tested SHA**:

```bash
PYTHON=python3.12 bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2 playwright==1.56.0
.venv-foundation/bin/python -m pip check
.venv-foundation/bin/python -m playwright install chromium
PYTHONPATH=foundation .venv-foundation/bin/python -m unittest foundation.tests.test_d1_visuals -v
PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests -q
PYTHONPATH=foundation .venv-foundation/bin/python foundation/wp7_create_examples.py /tmp/d1-review-unique --elements 4096 --budget 9
```

Use a new workspace/dossier filename each time. For the real browser steps use the committed GitHub Actions workflow at `.github/workflows/d1-v02-ui-verification.yml` to provision Chromium, launch Streamlit, run browser scripts and upload SHA256SUMS, screenshots, generated dossiers and logs.

## Critical independent challenges

1. Reuse an existing Tab 1 dossier, inspect it and create a new immutable run with an unused filename. Compare original hash before and after.
2. Reproduce existing outputs and companion collisions in Tab 2/3/4; assert none are modified.
3. Compare every plotted source value and candidate ID against persisted WP3 ledger or verified WP4 dossier; verify status membership is from original source comparison, not recomputed by UI.
4. Inspect homogeneous, layered and gradient coordinates/constituent basis, especially layer boundary discontinuities and incompatible WP4 profiles.
5. Verify WP3 intended Pareto never merges with WP4 estimated-achieved population, and unknown or unresolved numerical states remain excluded.
6. Exercise supported qualified A/B gradient handoff; reject unsupported architecture/materials and manipulated lineage.
7. Exercise actual cancellation, recovery, numerical replay, ZIP integrity, corrupted archives and immutable copies.
8. Compare WP3 and WP4 numerical outcomes with tag `d1-v0.1.0` in separate Python processes.
9. Inspect screenshots and keyboard/narrow-width navigation; ensure synthetic estimates are not presented as measurements or full manufacturing validation.
10. Verify stop reason, budget and feedback revision causal chain without asserting universal improvement.

## Gates

- **Functional:** full browser first-user Tab 1–4, handoff, cancellation, recovery, export and replay, with screenshots and immutable source hashes.
- **Scientific:** full foundation pytest, exact numerical baseline comparison, no changes to scientific engine files.
- **Presentation:** plotted coordinates, source tables, qualifications, units and provenance checked; unsupported graphs fail visibly.
- **Evidence integrity:** exact source SHA, environment freeze, commands/results, artifact hashes, stop reasons and known gaps.
- **Independent review:** conducted by someone other than implementation agent, recorded at the exact source SHA.

**Acceptance remains withheld** if any critical or high finding remains unresolved or any required gate lacks executed evidence. The reviewer must not convert this handover into self-certification.
