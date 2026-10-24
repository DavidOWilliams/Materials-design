# WP2 corrected numerical qualification — synthetic planar thermoelastic coupon

Requalified 24 October 2026. Applies to `wp2-bounded-2`, **not** the
historical `wp2-bounded-1` implementation. The original 23 October report
and its reported stress values are permanently preserved at
[reviewed WP2 commit ae052d6f](https://github.com/DavidOWilliams/Materials-design/blob/ae052d6f70499eceb92e73436fd0de7cb1791777/foundation/WP2_NUMERICAL_QUALIFICATION.md).
Read [WP2 correction log](WP2_CORRECTION_LOG.md) for independent defect
reproduction and numerical-qualification conditions.

## Scientific scope

The numerical model evaluates an assumed isotropic, thin planar coupon with
piecewise-constant cell conductivity, density, biaxial stiffness and expansion
coefficient. Thermal boundary conditions are steady Dirichlet temperatures
at two faces. There are no sources, transverse heat losses or interface
contact resistance. A spatially defined `Gradient` remains a continuous
piecewise-linear design parameterisation, not a renamed layer-stack design.

The elastic calculation is a **thermal mismatch component only**:
equibiaxial small-strain plane stress `Q=E/(1-nu)`, uniform free or
fully-flat restraint, thermal stress-free reference temperature, with free
membrane expansion and bending curvature. No 3D interface stress, sintering,
creep, damage, fracture or manufacturing residual stress is claimed.

Material entries are **neutral, synthetic scenarios**, not measured ceramic
grades. The prescribed mixture rules are Voigt/parallel conductivity,
volume-additive density, iso-strain biaxial modulus and stiffness-weighted
thermal expansion. Every required property now has a machine-readable
temperature interval, provenance, material-state identity and versioned
SHA256 pack identity. A solver setting can narrow but never extend property
applicability. The stress-free reference temperature is checked against the
same intersection as the thermal boundary range because constant thermal
expansion is integrated from that reference within the supported domain.

## Exact cellwise thermal resultants (correction A)

Let a cell of thickness `h_i` occupy midplane-relative coordinates with
centre `z_i`. The solved conduction field inside the cell is precisely
linear: `T(z)=T_i + g_i(z-z_i)`, with
`g_i = -q/k_i`. Cell properties `Q_i` and `alpha_i` are constant.
Then the exact thermal force and bending-moment integrals are

```
N_T,i = Q_i alpha_i h_i (T_i - T_ref)
M_T,i = Q_i alpha_i [ h_i z_i (T_i-T_ref) + g_i h_i^3/12 ]

A_i = Q_i h_i
B_i = Q_i h_i z_i
D_i = Q_i [ h_i z_i^2 + h_i^3/12 ]
```

The free plate solves
`A*eps_0+B*kappa=N_T` and `B*eps_0+D*kappa=M_T`.
The second term in `M_T,i` is **not negligible merely because the
temperature is linear**. WP2 v1 omitted it even while retaining
`Q_i h_i^3/12` in bending stiffness. The corrected code includes that
term in the solved moment *and* the reported residual.

For independent verification, tests integrate the affine stress field
`sigma_i(z)=Q_i*[eps_0+kappa*z-alpha_i*(T_i+g_i*(z-z_i)-T_ref)]`
directly using polynomial endpoint integrals for force and first moment.
The reference does not reuse the solver's centre-temperature approximation.
Cell-centre stress samples are used for the **reported tensile objective**;
do not relabel those as interface or surface limiting stresses.

### Independent references and registered tolerances

| Reference | Exact condition | Acceptance | Reason |
| --- | --- | --- | --- |
| Homogeneous Fourier | `q=(Th-Tc)k/h` | Relative 1e-13 in direct-cell test | Analytical resistance, double precision |
| Multi-layer Fourier | `q=(Th-Tc)/sum(h_i/k_i)` | Relative 1e-10 | Independent series resistance |
| Linear graded conduction | `k(x)=2+8x`, `q=8(Th-Tc)/(h ln 5)` | Relative 1e-4 at 128 cells; monotone refinement | Midpoint approximation for property field |
| Homogeneous free thermal bending | `eps0=alpha*((Th+Tc)/2-Tref)`, `kappa=alpha*(Tc-Th)/h` | 0.05 Pa maximum tensile stress; curvature absolute 2e-9 1/m | Exact representability and floating-point stress cancellation at 100 GPa |
| Uniform free thermal expansion | `eps0=alpha*(T-Tref)`, zero curvature/stress | 0.01 Pa | Exact constant state |
| Uniform fully restrained expansion | `sigma=-Q alpha*(T-Tref)` | Pytest strict numeric closeness | Analytic stress |
| Bilayer bending | Exact independent A/B/D solution: `kappa=-763/17700` 1/m and interface tensile limit `680000000/59` Pa | Curvature relative 2e-4; stress within 0.5% at 512 cells | Max stress evaluated at cell centres, not exact interface |
| Free equilibrium | Direct polynomial integrals `int sigma dz`, `int z sigma dz` | Force 1e-4 N/m; moment 1e-6 N | Independent conservation residual, *not* error estimate for peak stress |
| Orientation/reversal | Reverse cells and interchange hot/cold | Same stress field in reverse order, curvature and signed flux reverse | Geometry and thermal sign invariance |

These verification tolerances are properties of numerical precision and spatial
sampling, not estimated uncertainty in printed ceramic phases. The original
homogeneous v1 test expectation that 128-cell **3,664 Pa spurious stress**
would shrink slowly with mesh refinement is *invalid*; an exactly representable
homogeneous linear profile must have virtually zero stress at every mesh.

### A separate convergence gate for comparisons

Because a cell-centre peak may converge much more slowly than integrated
mass or flux, each corrected evaluation additionally computes a **2x finer
mesh** under identical conditions. It persists
`numerical_quality=qualified` only if all four checks pass:

- Peak sampled tensile mismatch: absolute difference under 0.05 Pa when
  effectively zero, otherwise relative difference at most 0.1%.
- Curvature: difference at most 2e-9 1/m near zero, otherwise at most 0.1%.
- Flux magnitude: relative difference at most 1e-5.
- Areal mass: absolute difference at most 1e-8 kg/m².

If any fails, the result is `numerical_quality=unresolved`: mathematical
evaluation can still have `status=complete`, but
`numerical_comparison_eligible` **rejects** it. The separate
`exploratory_numerical_eligible` API permits an explicitly exploratory
comparison without implying converged numerical accuracy or manufactured
feasibility. Both require evaluated hard constraints to pass.
`compatible_comparison` checks common context only, never feasibility.

For gradients, 128 cells are useful **illustrative calculations**, not
sufficient qualification of sampled peak stress. The replay demonstration
also creates refined 4096-cell cases. Tests require a 4096-cell gradient to
meet the 2x mesh gate; this is a tested scenario-specific result, not a
universal geometry/mesh requirement. The convergence gate is re-evaluated
per candidate rather than hard-coding an unconditional mesh threshold.

## Before/after results: same 128-cell demonstration

The **reviewed v1** source and **corrected v2** reference scenarios have the
same nominal phase conductivity, mass, stiffness, expansion, 400/300 K
boundary temperatures and 10 mm thickness. The corrected pack now stores
explicit temperature applicability and a new version/provenance hash.

| Architecture | v1 peak centre stress (Pa) | v2 peak centre stress (Pa) | v1 curvature (1/m) | v2 curvature (1/m) |
| --- | ---: | ---: | ---: | ---: |
| Homogeneous A/B | 3,663.7783 | approximately 1.4e-8 | -0.0930712421 | -0.0930769231 |
| Two equal layers | 11,368,069.05 | 11,368,290.96 | -0.0431037421 | -0.0431073446 |
| A→B gradient | 4,640,168.57 | 4,642,799.60 | -0.0531338513 | -0.0531387618 |
| Supplied estimated achieved gradient | 9,269,092.00 | 9,272,019.83 | -0.0558459070 | -0.0558513864 |

Original data: isolated reproduction against
`ae052d6f70499eceb92e73436fd0de7cb1791777` in the
`wp2-reviewed-defects-and-history` workflow job. Corrected table: executable
`foundation/verify_wp2.py`, at 128 cells, reported by a successful
`numerical-regression` workflow job on 24 October 2026. Numerical fluxes
and areal masses retain their physical definitions; the thermal-moment fix
changes stress/curvature, **not** conduction or density accounting.
For the intended alternatives areal mass remains 30 kg/m², with
transmissions 60,000, 33,333.333 and 49,708.001 W/m².
The hypothetical achieved-state mass remains 32.5 kg/m² and violates a
31 kg/m² hard ceiling. Numerical completion never overrules this violation.

These 128-cell stress numbers are **exploratory** until mesh-doubling
qualifies each candidate; neither v1 nor v2 is experimental ceramic evidence.

## Reproducibility and identity

`solver_identity()` now identifies `wp2-bounded-2` and SHA256 of the
corrected numerical adapter and kernel. The corrected property pack has
explicit versioned validity limits and a different content hash.
`foundation/verify_wp2.py` saves all scenario input, evaluation and spatial
artifacts in the existing immutable SQLite+SHA256 store and checks new-process
replay. The archived `wp2-bounded-1` result remains readable by the
corrected contracts but is not recalculated under the changed method;
original replay uses a separate checkout at the exact reviewed commit.

### Scientific sources and limits

- Classical Fourier series resistance and resistance integral.
- Classical Laminate Theory for thermal A/B/D stiffness and resultants:
  NASA/TM-2001-210656, equations 2.35–2.39.
- WP0R retained Pelz B4C/SiC ambiguities and CODE manufacturing evidence
  are **not** treated as validation of this neutral synthetic pack.

A01–A21 remain open as actually recorded. Real chemistry/property-state
applicability, interfaces, anisotropy, material compatibility, shrinkage,
time-dependent response and measurement-based V1 are excluded.
