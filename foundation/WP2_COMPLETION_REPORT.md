# WP2 corrected completion and requalification report

24 October 2026 | Materials-design | Focused corrections to draft PR #2

## Decision and scope

**WP2 numerical software implementation is ready for WP3 within its bounded,
explicitly synthetic planar domain, subject to a green final-head CI workflow.**
The review defects have been reproduced against the exact original reviewed
commit, addressed in source, regression-tested, and documented. The original
"WP2 complete" claim of 23 October **did not establish scientific correctness**:
the original reports are superseded as numerical qualification evidence.

This is **not D1** (the integrated inverse-search and manufacturing-feedback
workflow), **not V1** (measured ceramic validation), and **not a prediction of
manufactured-ceramic reliability**. No WP3, WP4 or WP5 code was implemented as
part of this focused correction. The dedicated branch remains unmerged and
PR #2 remains draft, targeting `wp1-foundation-2026-10-22`.

Authority: `recovered_wp0/evidence/Material_System_Implementation_Plan_v2.md`
for delivery. The product's wider vision is unchanged. Scientific adapters,
typed applicability, source provenance and historical decisions remain
replaceable and traceable.

## The five independent findings and closure

| Review | Fix | Direct verification |
| --- | --- | --- |
| A — omitted within-cell thermal moment | Exact cellwise `Q alpha g h³/12` thermal moment integrated with bending stiffness; independent polynomial equilibrium checks | Homogeneous zero-stress 2/16/64/128/512 cells; analytical bilayer; orientation reversal and layered/gradient convergence |
| B — disabled refinement test | Literal backslash-newline comments replaced by executable assertions | Original test defect reproduced at reviewed SHA; corrected test fails on v1 spurious stress |
| C — two bounds, duplicate metric | One calculated constrained metric; distinct outcome per constraint ID, relation and limit | 29–31 kg/m² range, separate violations, equalities, contradiction, units, missingness and separate-process persistence |
| D — false compatibility and manufacture default | Full scenario/assumption/solver/method context; explicit `manufacturing_feasibility`, `numerical_quality`, numerical-only comparison API | Changed process route/capability invalidates context, unknown manufacturing persists, legitimate different geometries stay compatible |
| E — settings broadened property domain | Versioned min/max Kelvin for each property, required supported-domain intersection | 900 K fails with unchanged 290–410 K records despite settings 1000 K; missing, mismatched and revised wider synthetic pack tests |
| WP4 handoff wording | D1 assumed resolution feedback and V1 measured validation separated | This report, corrected architecture and correction log |

All five original problems were reproduced automatically against **unchanged**
source commit `ae052d6f70499eceb92e73436fd0de7cb1791777`.
See [correction log](WP2_CORRECTION_LOG.md) for reproduction commands,
analytical derivation, acceptance tolerances and remaining limitations.

## Before and after — same 128-element calculation

The *old* values remain in the original
[23 October report](https://github.com/DavidOWilliams/Materials-design/blob/ae052d6f70499eceb92e73436fd0de7cb1791777/foundation/WP2_COMPLETION_REPORT.md).
Revised synthetic property records are now versioned with an explicit
290–410 K supported domain. Their nominal phase values, thermal boundaries,
coupon thickness and material accounting are unchanged.

| Design | v1 tensile mismatch (Pa) | v2 tensile mismatch (Pa) | v1 curvature (1/m) | v2 curvature (1/m) |
| --- | ---: | ---: | ---: | ---: |
| Homogeneous 50:50 A/B | 3,663.78 | ~0.00000001 | -0.093071242 | -0.093076923 |
| Two-layer equal-budget | 11,368,069.05 | 11,368,290.96 | -0.043103742 | -0.043107345 |
| Linear gradient A→B | 4,640,168.57 | 4,642,799.60 | -0.053133851 | -0.053138762 |
| Supplied synthetic estimated achieved profile | 9,269,092.00 | 9,272,019.83 | -0.055845907 | -0.055851386 |

The material/geometry budgets and Fourier definitions have not changed:
three intended designs have 30 kg/m² areal mass; the supplied estimated state
has 32.5 kg/m² and breaches the fixed 31 kg/m² hard ceiling. Intended thermal
transmissions are respectively 60,000, 33,333.333 and 49,708.001 W/m².
The achieved demonstration has approximately 58,376 W/m².

**Crucially, the 128-cell layered and gradient stress figures are exploratory.**
Force/moment equilibrium is not enough to qualify their sampled maximum
stress against spatial discretisation error. The corrected evaluator runs
a separate 2x mesh and stores `numerical_quality=unresolved` if its
registered error threshold is missed. No unresolved result is admitted by
`numerical_comparison_eligible`.

### High-resolution qualified numerical examples

The corrected verifier additionally persists and independently replays
4096-element versions of the four examples. The independent mesh-doubling
gate qualifies the intended scenarios and is checked for the achieved
example by the verification CLI.

| Design, 4096 cells | Thermal transmission W/m² | Areal mass kg/m² | Sampled tensile stress Pa |
| --- | ---: | ---: | ---: |
| Homogeneous | 60,000 | 30.0 | ~0.00000375 |
| Layered | 33,333.333 | 30.0 | 11,520,513.33 |
| Gradient | 49,706.796 | 30.0 | 4,785,159.66 |
| Supplied estimated achieved gradient | 58,373.568 | 32.5 | 9,532,502.28 |

These remain **synthetic, numerical** and do not demonstrate printable
ceramic material properties, manufacturing feasibility or measurement
agreement. The difference between 128-cell and 4096-cell sampled peak
stresses shows why the qualification gate is essential.

## Five distinct statuses in the corrected evaluation

1. `status`: whether mathematical objectives were computed.
2. `feasibility`: evaluation of the declared hard numerical limits;
   all constraint IDs, relations and outcomes are separately retained.
3. `manufacturing_feasibility`: intended-only **unknown**, or exact
   `unknown/conditional/infeasible` carried from supplied estimated state.
4. `evidence_status`: synthetic / provisional / supported property evidence.
5. `numerical_quality`: 2x-mesh qualified / unresolved.

`compatible_comparison` validates scenario compatibility but does not
constitute a feasibility or accuracy decision. Changed process-capability
routes/resolutions, selected target, assumptions, solver and material pack
invalidate context. Candidate-specific geometry and composition do not:
homogeneous, layered and gradient alternatives remain comparable when
their scientific context is genuinely identical.

`exploratory_numerical_eligible` is intentionally not a manufacturing
ranking and may accept an unresolved spatially sampled result if all declared
mathematical constraints pass. `numerical_comparison_eligible` additionally
requires verified mesh convergence. The generic stored
`Evaluation.comparison_eligible` does not promote intended or
manufacturing-unknown states into a feasible manufacture assertion.
An unknown feasibility is **never silently made conditional**.

## Fresh execution and regression evidence

The current branch has a five-job GitHub Actions qualification workflow:

| Job | Scope checked | Observed result on passing 24 October run |
| --- | --- | --- |
| `wp1-immutable-baseline` | Fresh original Python 3.12 hash-locked setup, `pip check`, exact original WP1/recovery code and R1 defect reproduction | **74 passed** plus expected R1 rejection |
| `wp2-reviewed-defects-and-history` | Fresh reviewed SHA checkout and locked environment, reproducible A–E defects, original v1 store and replay | **All five reproduced**, historical replay passed |
| `numerical-regression` | Fresh corrected locked environment and `pip check`, foundation/recovery/WP2 tests, original WP1 replay, corrected eight examples plus separate-process replay | **130 passed** in the last source-verification run before documentation; 8 persisted/replayed examples |
| `legacy-regression` | Separate legacy pinned runtime + scikit-fem, `pip check`, `python -m pytest tests recovered_wp0 -q` | **1,148 passed**, 10 warnings |
| `wp2-cross-version-history` | Load unchanged original v1 SQLite/JSON into corrected reader; check source/result hash, refuse changed-solver replay | **Passed** |

The code-verification reference before documentation updates is
[GitHub Actions run 40072532460](https://github.com/DavidOWilliams/Materials-design/actions/runs/40072532460).
Final acceptance must use the **latest complete green workflow at the
published PR head**, not that earlier run alone. Script output includes
results and curvature, separate-process replay checks, and downloadable
JSON evidence artifacts.

The test totals are not a substitute for verification. Independent
conduction, membrane/bending thermal results, force/moment integrals,
reference temperatures and property validity, separate-process results,
physical limits and solver/source identity are checked behaviourally.

## Historical integrity

- The original WP1 `RunInputs` and `Evaluation` JSON bytes, SHA256
  hashes and three-architecture replay remain unchanged by optional v2
  fields; the original WP1 baseline is reexecuted in CI.
- Historical WP2 `wp2-bounded-1` records are **readable** in the corrected
  run store with their original hash and interpretation. Original-method
  **replay** is supported using the exact reviewed checkout, independently
  tested as a separate CI job.
- A historical v1 run is **not** silently recomputed using
  `wp2-bounded-2`. Its older results remain superseded scientific
  evidence; a fresh run receives new solver source identity, property pack,
  assumptions and input/output hashes.
- A01–A21 remain open to the extent indicated in the existing append-only
  assumption registry. Tests do not scientifically resolve them.

## Setup and repeatability

With a fresh Python 3.12 environment from the repository root:

```bash
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pip check
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python foundation/verify_demo.py --output /tmp/wp1-replay
.venv-foundation/bin/python foundation/verify_wp2.py --output /tmp/wp2-corrected-evidence
```

The last command performs both the standard 128-cell illustrations and
the 4096-cell accuracy-qualified cases, persisting their spatial fields,
hard constraints and eight independent-process replays. Run an individual
case at high resolution with:

```bash
.venv-foundation/bin/python -m material_core.wp2_demo --store /tmp/wp2-case --architecture gradient --elements 4096
.venv-foundation/bin/python -m material_core.wp2_demo --store /tmp/wp2-case --replay RUN_ID
```

Historical WP2 v1 source must be replayed using its archived checkout,
not the corrected command.

## D1 and V1 handoff — correct Implementation Plan v2 interpretation

**D1** does **not** require experimental manufacturing records. WP4 can
configure an *explicit versioned assumed* layer/feed-resolution capability,
transform intended into estimated achieved fields, preserve geometry and
material accounting, recompute performance, expose binding constraint
violations and show a design revision. That will be a transparent simulation
under stated assumptions, **not a scientifically validated printer predictor**.
Nothing in the WP2 correction implements that transformer.

**V1** is separate measured ceramic validation, requiring compatible
process/feed commands, achieved composition/geometry, porosity, provenance
and uncertainty. Missing such experimental evidence does not delay D1,
but it prevents a V1 or physical-ceramic validation claim.

Further work beyond WP2 includes WP3 multiobjective inverse search,
WP4 bounded feed/layer-resolution feedback, WP5 user workflow and the
remaining D1 integration/replay package. No downstream work has begun in
this correction task. The agreed Implementation Plan v2 remains the
delivery authority; the 4–6 active week D1 working-target estimate is a
planning assumption, not a guaranteed clock schedule or V1 commitment.

## WP2 exit judgement

The **revised WP2 software and bounded numerical qualification** has
demonstrable closure of review findings A–E and is suitable as the foundation
for WP3 **once final-head CI is green**. That does not authorise a merge
or imply material-science acceptance; independent expert selection of a real
ceramic case and evidence-backed V1 remain future decisions.

Draft PR #2 is preserved; no merge, destructive rewrite, purchase,
researcher contact or WP3 implementation was made.
