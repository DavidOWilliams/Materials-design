# P1-IR-03 — frozen hypervolume degeneracy analysis (supplementary)

**Not a revised confirmatory result.** The original protocol, numerical outcomes, reference point, and manifests remain unchanged.

## Exact numerical observation
Using the 80 preserved paired records at `foundation/p1/evidence/confirmed-source-6eb62da/all_paired_trials.json`:
- Eligible objective vectors: **125 blind** and **126 feedback**.
- `tensile_thermal_mismatch` is recorded in **Pa**, with a positive cell-centre equibiaxial tensile mismatch convention. Its observed range was **5.759824041329242×10⁻⁹ to 2.0328790734103208×10⁻⁸ Pa** in each arm.
- Only **eight distinct numerical values** of that third objective occur per arm, compared with a frozen reference of **1,000,000,000 Pa**.
- Normalized stress coordinates are approximately **5.76×10⁻¹⁸ to 2.03×10⁻¹⁷**; the corresponding normalized dominance-box span, `1 − stress/reference`, rounds to **1.0** at ordinary IEEE double precision.
- All values are strictly nonzero, but their magnitude is numerically negligible relative to the normalisation reference. Therefore the so-called three-dimensional feasible hypervolume behaves **effectively as a two-dimensional area in thermal transmission versus areal mass** for this dataset.

## Physical and numerical interpretation
WP2's `tensile_thermal_mismatch` objective is a stress measure in Pa, but the specific selected synthetic fixture uses a free plate with force-and-moment-free restraint, and the observed qualifying configurations have almost zero tensile stress. The tiny nonzero estimates are consistent with floating-point/numerical residuals rather than a consequential engineering stress trade-off. This explanation is a scientific interpretation, not an independent analytical proof of stress convergence: numerically qualified statuses and mesh sensitivity must be inspected separately.

The frozen 1 GPa reference was chosen before outcomes and must not be tuned retrospectively. Because the observed stress-to-reference ratio is near machine precision, the measured 3D hypervolume's apparent precision and positive effect **must not be interpreted as demonstrated multiobjective stress improvement**. The result is mathematically valid for the frozen formula, fixed reference, and objective data. Its practical meaning is confined primarily to thermal/mass trade-offs under the synthetic assumptions.

## Preservation and limits
- Original paired mean normalized HV `+0.014069733796296294`, 95% paired bootstrap CI `[+0.0037037037037037043,+0.025925925925925925]` remain **historical outputs**, not altered.
- Exactly 6/80 paired effects were positive and 74/80 zero, with no negative effects under equal numerical-work accounting.
- This supplementary assessment cannot validate physical manufacturability, stress performance, independent process predictions, or genuinely three-objective optimisation.
- Correct subsequent studies should include scientific benchmarks with a consequential and numerically qualified stress objective; any alternative normalization, 2D endpoint or constraint is **new exploratory work** and must never replace the preregistered primary endpoint.

**Disposition suggested for independent review:** interpretation corrected; actual generalisation and physical/numerical qualifications remain open scientific limitations.
