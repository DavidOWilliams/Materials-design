# WP2 numerical qualification — bounded synthetic scenario

23 October 2026 | Materials-design | Numerical method and evidence review

## Decision

The implemented WP2 numerical *software* method is bounded to a steady,
planar, 1D, layered/graded ideal coupon with an equibiaxial small-strain
plane-stress plate model. Homogeneous, arbitrary perfectly bonded discrete
layers and piecewise-linear composition gradients can be evaluated against
**three declared engineering quantities**, within the expressly assumed,
fully synthetic neutral constituent property catalogue.

The numerical implementation is not an experimentally validated ceramic
property pack, a manufacturing process model, a crack prediction, or total
manufacturing residual-stress analysis. D1 needs inverse search, process
feedback and expert workflow; V1 requires linked real-material measurements.
Neither is completed by WP2.

## Domain and conventions

- Coordinate `z` increases from the hot face to the cold face, over total
  thickness `h>0`. Positive signed through-thickness Fourier flux means
  heat flows hot-to-cold. The **minimised thermal-transmission objective is
  absolute flux magnitude**, so reversing boundaries does not produce an
  artificial improvement.
- Steady conduction has no heat source or lateral loss. Perfect thermal
  contact is assumed. Each independently stored mesh cell has constant
  conductivity; the composition design remains distinct from that mesh.
- Effective conductivity is the **parallel-transport Voigt upper bound**,
  `k_eff=sum(v_i*k_i)`, with the declared phase arrangement assumption.
  Density is `rho_eff=sum(v_i*rho_i)`. Iso-strain biaxial stiffness is
  `Q_eff=sum(v_i*Q_i)`. The thermal eigenstrain coefficient under the same
  iso-strain assumption is
  `alpha_eff=sum(v_i*Q_i*alpha_i)/sum(v_i*Q_i)`.
  These are different assumptions for different properties; the relationship
  does **not** establish a printable effective ceramic microstructure.
  Mass fractions become volume fractions using densities; atomic basis is
  unsupported without molar masses.
- `Q=E/(1-nu)` is equibiaxial plane-stress stiffness for an *isotropic*
  thin plate. Small-strain elastic thermal stress for each cell is
  `sigma=Q*(epsilon0+kappa*(z-h/2)-alpha*(T-Tref))`.
  In the **free** case, thermal force and moment resultants are balanced
  through a two-by-two A/B/D laminate matrix, permitting bending; a
  fully-flat restrained case sets the membrane strain and curvature to zero.
  No through-thickness or interface shear stress is claimed.
- The tensile metric is `max(0,max_i(sigma_i))` over **cell-centre samples**
  of the in-plane equibiaxial stress. Signed cell stress, coordinates and
  temperature survive storage; it is not a singular interface peak.
- Synthetic phase properties are constant only on the stated **290–410 K**
  domain. The two neutral hypothetical phases have no assigned ceramic
  chemistry. Other phase states, unknown/missing input quantities, unsupported
  settings, process mismatches and out-of-range temperatures fail closed.
- `evidence_status=synthetic` is distinct from successful numerics,
  conditional comparative eligibility, hard constraint satisfaction, and
  experimental support. A candidate outside a hard constraint cannot enter a
  feasible ranking even if all physical metrics were computed.

## Registered independent reference equations

1. Homogeneous slab: `q=(Th-Tc)/(h/k)`, and
   `m/A=rho*h`.
2. Unequal layer slab: `q=(Th-Tc)/sum(h_i/k_i)`, perfect interfaces.
3. Linear conductivity field `k(x)=2+8x`, `x=z/h`:
   `q=8*(Th-Tc)/(h*ln(5))` exactly, converged by midpoint-cell quadrature.
4. Uniform free expansion: zero stress, `eps=alpha*(T-Tref)`;
   fully restrained thermal expansion:
   `sigma=-Q*alpha*(T-Tref)`.
5. Unequal-material layer with free bending: thin-plate laminate
   `[A B;B D]*[eps0;kappa]=[NT;MT]`, where
   `A=int Q dz`, `B=int Q*(z-h/2) dz`,
   `D=int Q*(z-h/2)^2 dz`, and `NT,MT`
   integrate `Q*alpha*(T-Tref)` with the same weights.
   Analytically integrated bilayer at 400/300 K, 5/5 mm with
   `Q=100/160 GPa`, `alpha=5/12e-6 1/K`, and `k=2/10 W/(m K)`:
   `eps0=703/3540000`, `kappa=-763/17700 1/m`,
   maximum idealised tensile stress `680000000/59 Pa`.
6. Force and moment equilibrium are checked independently of the scalar
   tensile metric. Refined cell centres approach, but do not replicate,
   discontinuous-interface limiting stresses exactly.
7. Absolute/relative tolerances are **numerical verification criteria**,
   not measured material uncertainty. The actual test cases and thresholds
   are specified in `foundation/tests/test_wp2_kernel.py`,
   `test_wp2_mapped_integration.py`, and
   `test_wp2_property_mapping.py`.

### Scientific reference basis

- Fourier's law and the exact series-resistance integral (classical conduction).
- NASA/TM-2001-210656, *Classical Laminate Theory*, thermal A/B/D,
  eigenstrain force and moment resultants; equations 2.35–2.39:
  https://www.cs.odu.edu/~mln/ltrs-pdfs/NASA-2001-tm210656.pdf
- NASA practical micromechanics implementation and laminate applicability
  background: https://github.com/nasa/Practical-Micromechanics
- Archived WP0 Pelz B4C/SiC literal versus reversed thickness assignments
  and unresolved source discrepancy are preserved in `recovered_wp0/evidence`
  and `recovered_wp0/test_recovery.py`. These are separate from the CODE
  alumina/zirconia manufacturing-evidence case; they are **not** used as
  substitute validation for the synthetic neutral WP2 property catalogue.

No new solver package, scientific-model fitting, predictor training,
fine-tuning or calibrating is introduced. NumPy, SciPy and scikit-fem remain
available for the recovered independent WP0 reference suite in the locked
foundation environment; the new small 1D kernel uses standard Python.

## Fixed common synthetic comparison

Both constituent inventory *volume fraction* and coupon geometry are held
fixed across the three intended alternatives: 0.01 m total thickness, half
A/half B nominal volume, 400/300 K, stress-free 300 K, perfect contacts,
equal mechanical restraint and the same mesh/settings/evidence pack. Three
properties are not inferred from external experimental values: they are
declared hypothetical demonstration scenarios.

| Alternative | Heat flux magnitude W/m² | Areal mass kg/m² | Tensile elastic mismatch Pa |
| --- | ---: | ---: | ---: |
| Homogeneous mixture A/B | 60000.00000000 | 30.0 | 3663.77830506 |
| Perfect discrete A/B bilayer | 33333.33333333 | 30.0 | 11368069.04871642 |
| Continuous A→B linear gradient (meshed) | 49708.00100817 | 30.0 | 4640168.56558629 |
| Supplied *estimated achieved* gradient | 58376.02189673 | 32.5 | 9269091.99693567 |

Results from GitHub Actions run 39985173170, 128-element synthetic scenario;
values are numerical scenario illustrations, not a validated physical ranking.
The homogeneous nonzero tensile residual is a small **spatial discretisation
sampling effect**, not a claim of a true material-stress advantage.
For the achieved profile, a hypothetical change in gradient composition
changes areal mass from 30 to 32.5 kg/m² and violates the shared 31 kg/m²
ceiling. The achieved-state example demonstrates correct *data-path
selection*, **not** a manufacturing transform; it cannot establish
process feasibility.

## Evidence and reproducibility

- `foundation/setup.sh` creates an isolated Python 3.12 environment
  with 13 pinned, hash-locked packages.
- `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest
  foundation/tests recovered_wp0 -q` checks foundational contracts,
  WP0R numerical fixtures, new constraint metrics, historical run hashes,
  mapping, thermal/mechanics references, convergence, and separate-process replay.
- `foundation/verify_demo.py` independently reopens and replays all three
  original WP1 thermal architectures.
- `foundation/verify_wp2.py --output <path>` independently runs four
  synthetic examples in new Python processes; it persists complete inputs,
  results, fields and assumption snapshots, then reopens and recalculates
  each example in another process. JSON reports are retained as a GitHub
  Actions downloadable evidence artifact.
- `PYTHONPATH=foundation .venv-foundation/bin/python -m
  material_core.wp2_demo --store /tmp/wp2 --architecture gradient`
  prints the three objective values and run identifier; use the same
  command with `--replay RUN_ID` to compare immutable saved result bytes.

For CI results, use the head commit on branch
`wp2-numerical-2026-10-23` and its green
`WP2 foundation regression` workflow. Earlier failed CI attempts
were engineering diagnosis and must not be misrepresented as passes.

## Scientific questions and deferred work

Historical A01–A15 records are unchanged and **not resolved** by these
calculations. WP2 adds A16–A21, all explicitly open, covering mixture
microgeometry, density/porosity, elasticity and reference state, interfaces,
temperature dependencies, and process-to-achieved mappings. Exact questions,
provisional answers, evidence, affected calculations, priorities and
resolution criteria are versioned under
`material_core/data/assumptions_wp2_v1.json` and snapshotted into each
new WP2 run.

Numerical success cannot certify sintering shrinkage, fracture, stress
relaxation, microstructural phase compatibility, porosity, full manufacturing
residual stresses, or a printed ceramic composition-property relation.
WF3/WP3 optimisation may vary supported design variables but must not
relax the brief or treat synthetic results as measured; WP4 supplies and
verifies one real manufacturing transformation or retains an unresolved
process status.
