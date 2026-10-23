# WP2 progress and scientific qualification — incomplete

Date: 23 October 2026. Base: WP1 commit `22350b119d8a30248a9924ba375ebf4c8dabb4b7`.
This report is a **work-in-progress record, not WP2 acceptance**.

## Completed source changes

- R1 representation: objective metrics remain separate from optional `constraint_metrics`.
  Store validation checks declared constraint units and rejects unknown constraint
  metrics, or disagreeing values for shared objective/constraint quantities.
  Eligibility requires all objectives plus computed satisfied constraints.
  Unknown, violated and failed constraints are not eligible.
- WP1 artifact backwards-compatibility: empty constraint metrics are excluded from
  canonical Evaluation JSON, preserving exact historical evaluation bytes/hashes.
  This must still be proven using the original saved WP1 JSON snapshots.
- R2 initial schema: typed `ThermoelasticSettings` and
  `CoupledThermomechanicalSettings`, preserving the original `ThermalSettings`
  branch of the discriminated input union. All 1.0 physical domains remain explicit.
- Standalone `wp2_kernel.py`: steady 1D heat conduction across arbitrary
  piecewise-constant cells, areal mass integration, and thin-plate equibiaxial
  thermoelastic mismatch including membrane/bending equilibrium. Signed raw flux,
  absolute thermal transmission, coordinates and signed stress field are retained.
  This kernel does not define or validate a ceramic property map.

## Verification status

Tests are **committed, not yet confirmed to have run**:
`foundation/tests/test_wp2_constraint_gate.py` and
`foundation/tests/test_wp2_kernel.py`. The branch includes a GitHub Actions
workflow to run the locked WP1/recovery suites, but no successful remote build
has been observed. **Do not interpret saved WP1 74-test or 1,148-test reports as
fresh WP2 results.**

References registered before broader tuning:
- Constant slab Fourier flux: q=(T_hot-T_cold)/(h/k).
- Piecewise constant layers: q=(T_hot-T_cold)/sum(h_i/k_i).
- Mass: sum(rho_i*h_i).
- Thermoelastic laminate with equibiaxial stiffness Q_i: A=sum(Qh),
  B=sum(Qh*z), D=sum(Q(h*z²+h³/12)). Thermal force/moment resultants
  N_T=sum(Qh*alpha*(T-T_ref)) and
  M_T=sum(Qh*z*alpha*(T-T_ref)). For free membrane/bending conditions,
  [A B; B D] [eps0;kappa] = [N_T;M_T].
- Source: NASA/TM-2001-210656, classical laminate thermal resultants
  and A/B/D relations, equations 2.35–2.39:
  https://www.cs.odu.edu/~mln/ltrs-pdfs/NASA-2001-tm210656.pdf
- No arbitrary percentage tolerance is treated as material uncertainty.

## WP2 exit decision by criterion

| Criterion | Status | Reason |
| --- | --- | --- |
| 1 R1 constraints | Implemented, unverified | New schema/store logic and tests; no passing run demonstrated |
| 2 typed contracts/history | Partial | Typed mechanics input; historic artifact replay not independently demonstrated |
| 3 properties/mapping | Not met | No validated or labelled integrated property pack |
| 4 numerical methods | Partial | Bounded standalone kernel and reference tests; not qualified in full workflow |
| 5 three architecture objective vectors | Not met | No three-class persistent integrated D1 scenario |
| 6 statuses/context | Partial | Constraint eligibility corrected; full scenario compatibility not implemented |
| 7 consequential identity | Partial | RunInputs hashing retained; full property/solver/target cache proof outstanding |
| 8 persisted full fields/replay | Not met | R1 metrics storage implemented; new spatial kernel not integrated into RunStore |
| 9 clean setup/regressions | Not met | No fresh passing checkout/CI run established |
| 10 evidence/docs | Partial | Source/tests/report on branch; completion report cannot be issued |

A01–A15 remain **unresolved**; original registry records are unchanged.
WP1's D1 working demonstration and V1 ceramic validation remain **not complete**.

## Current numerical domain and exclusions

Planar, 1D, steady, perfectly bonded, source-free, lateral-loss-free,
piecewise-constant-cell heat transfer, with equibiaxial small-strain
plane-stress laminate thermoelasticity. Free membrane/bending or flat
restrained conditions are supported in the kernel. No ceramic print-state
material properties are inferred. No full residual stress, sintering, drying,
creep, phase changes, cracking, fracture or life estimates are claimed.
The peak tensile quantity is a cell-centroid stress sample, not a
singular interface peak or fracture criterion.

## Startup once an executable checkout is available

```bash
git checkout wp2-numerical-2026-10-23
bash foundation/setup.sh
export PYTHONPATH=foundation
.venv-foundation/bin/python -m pytest foundation/tests recovered_wp0 -q
.venv-foundation/bin/python foundation/verify_demo.py --output /tmp/wp2-replay
```

For kernel references only:
```bash
.venv-foundation/bin/python -m pytest foundation/tests/test_wp2_kernel.py -q
```

## Immediate remaining engineering work

1. Execute the fresh locked regression gate and inspect failures.
2. Load and replay saved WP1 homogeneous/layered/gradient inputs and evaluations,
   verify unaltered source bytes and original artifact SHA256.
3. Build an explicit scenario property catalogue with separate supported
   conductivity, density, thermal expansion and biaxial stiffness mappings;
   reject missing or incompatible phase/porosity/process inputs.
4. Integrate spatial state, three metrics, feasibility/context and fields
   into versioned persisted evaluations with a bounded replay adapter.
5. Qualify numerical domain by independent checks, refinement and known
   Pelz / CODE limitations before claiming criterion 5.
6. Only then build WP3 optimisation and the WP4 achieved-state feedback
   fixture without substituting intended values for unknown achieved fields.
