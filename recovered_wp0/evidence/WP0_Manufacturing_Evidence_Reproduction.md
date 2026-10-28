# WP0: manufacturing\-feedback evidence reproduction

19 October 2026

## Decision

**Partially closed, not fully closed\.** An executable reproduction now connects a published processing\-related thermal\-mismatch calculation to a material\-architecture revision\. It reproduces the direction and magnitude of the design trade\-off, but reveals a source\-input inconsistency\. It does not reproduce an experimentally validated intended\-to\-achieved composition model or a complete manufacturing simulation\. WP0’s broader scientific gate remains open\.

No experiments were conducted, and nobody was contacted\. This work does not require your son’s involvement before the bounded prototype\.

## Reference and reproducible inputs

Pelz et al\., *Multi\-material additive manufacturing of functionally graded carbide ceramics via active, in\-line mixing*, Additive Manufacturing 37 &#40;2021&#41;, 101647\. [DOI](https://doi.org/10.1016/j.addma.2020.101647); [institutional full text](https://meyersgroup.ucsd.edu/papers/journals/Meyers%20481.pdf)\.

Source locations: section 3\.3 gives B4C/SiC layer thicknesses 549/526 micrometres; section 3\.4, equations 1–2 and Table 2 supply seven layers, cooling from 1950 to 25 C, E = 483/411 GPa, Poisson ratios 0\.17/0\.16 and expansion coefficients 5\.5/3\.0 microstrain/K\. Its stress convention is negative tension\. Reported stresses are \-1\.11/\+1\.42 GPa\. Pages 6 and 8 were visually checked against the extracted text\.

The source’s purge calibration uses Play\-Doh: 3\.2 cm3 lag volume, with 1\.2 mm cylindrical trace geometry\. It is not a ceramic\-composition calibration\.

## What I implemented and verified

A dependency\-free Python implementation uses the published laminate equations\. Four B4C and three SiC layers give fractions f1 = 4l1/&#40;4l1\+3l2&#41;, f2 = 1\-f1\. Biaxial stiffness is E/&#40;1\-nu&#41;\. A second calculation independently enforces compatible in\-plane strain and zero resultant force\.

Five automated tests pass: equilibrium/independent formulation, scale invariance and cooling proportionality, published\-number discrepancy regression, feedback trade\-off, and rejection of invalid inputs\. These verify implementation, not physical accuracy\.

|Calculation                   |B4C stress, GPa|SiC stress, GPa|Interpretation                            |
|------------------------------|--------------:|--------------:|------------------------------------------|
|Thicknesses as written        |-1.054761      |+1.467843      |Literal-input reproduction                |
|Thickness assignments reversed|-1.111606      |+1.420048      |Diagnostic only; matches reported rounding|

The literal calculation differs from the reported magnitudes by about 5\.0% and 3\.4%\. A reversed thickness assignment explains the rounded values, but does not prove an author error\. Do not silently correct the source or tune inputs to pass\. Keep both cases until the original calculation or a clarification resolves the discrepancy\.

## Demonstrated feedback into architecture

The following are my model calculations, not additional experimental results\. Change the B4C:SiC layer\-thickness ratio, retaining seven alternating layers and the same thermal/property assumptions:

|Thickness ratio|B4C tension magnitude, GPa|SiC compression, GPa|
|---------------|-------------------------:|-------------------:|
|1:1            |1.083                     |1.444               |
|2:1            |0.671                     |1.790               |
|4:1            |0.381                     |2.034               |
|8:1            |0.205                     |2.183               |

Thus a 4:1 revision reduces the predicted B4C tension by 64\.8% relative to equal layers, while increasing SiC compression by 40\.9%\. This is a genuine architecture change driven by processing\-related analysis, not merely a printer\-setting adjustment\. It is also a trade\-off, not proof of an optimum or a crack\-free design\. Composition fraction changes with thickness ratio, so these are not equal\-composition comparisons\.

For implementation in the prototype: propose architecture, evaluate thermal mismatch, propose revised thickness ratio, re\-evaluate both stresses, then check manufacturing feasibility\. Preserve the original design and explain the reason for revision\. Do not automatically accept the lower\-tension design: the thinner layer may be unprintable, and compression or other objectives may be unacceptable\.

## Separate purge reconstruction

Using the stated circular trace assumption, 3200/&#40;pi \* 0\.6^2&#41; gives an equivalent transition length of 2829\.4 mm\. At 5 mm/s that is 565\.9 seconds of equivalent trace travel, not a measured purge duration\. Six composition switches would require 19\.2 cm3 if each used the reported purge amount\. This is bookkeeping from an empirical calibration, not independent reproduction of its measured response curve\.

The prototype may expose such a calibration as a named scenario\. It must not infer a mixing time constant, guarantee pure end\-member layers, or apply this value to another print head or ink without evidence\.

## Domain of applicability

|Domain                                                   |Permitted interpretation                                      |Boundary                                                                          |
|---------------------------------------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------|
|B4C/SiC alternating laminate, ideal bonded elastic layers|Thermal-mismatch screening and thickness-ratio sensitivity    |Pure-layer, constant-property idealisation; no defect-resolved prediction         |
|Seven-layer symmetric architecture                       |Reproduce this benchmark and its parameter sweep              |New layer counts, asymmetric bending and 3D geometries need a suitable formulation|
|Cooling from assumed stress-free joining state           |Estimate elastic mismatch stress before relaxation by cracking|Not total residual stress after shrinkage, creep, damage and cooling history      |
|Published mixer/surrogate setup                          |Trace-volume conversion and conditional purge budget          |Not validated ceramic response or general manufacturing capability                |
|Other material pairs, coatings or continuous gradients   |Software structure may be reusable                            |Physical inputs and models must be independently qualified                        |

No claim is made for aviation qualification, strength certification, ballistic performance, thermal performance, continuous\-gradient optimisation or prediction of crack spacing\.

## What still closes the gap

1. **Resolve numerical provenance\.** Obtain a corrected input assignment or original calculation\. Acceptance: independently specified geometry reproduces the reported result within an agreed rounding tolerance\. If unresolved, retain the literal\-input calculation as a transparent benchmark with discrepancy status\.
2. **Establish ceramic manufacturing response\.** Obtain feed\-command and outlet\-composition measurements versus extruded volume, including settings, repeat runs and uncertainty\. Acceptance: an existing response model predicts held\-out ceramic transitions to a stated error tolerance\. An arbitrary fitted smoothing kernel is not acceptable evidence\.
3. **Connect achieved geometry and properties\.** Obtain post\-processing layer/composition/porosity measurements and compatible property data\. Acceptance: downstream analysis consumes achieved\-state fields with units, provenance and uncertainty; no hidden ideal\-geometry substitutions\.
4. **Validate the design revision\.** Compare baseline and revised specimens, or a suitable published validation dataset, using the relevant stress/damage observations\. Acceptance: the claimed improvement survives model uncertainty and manufacturing constraints\. Lower elastic stress alone is insufficient\.
5. **Complete product integration\.** Add domain guards, evidence labels, revision history and out\-of\-domain refusal to the inverse\-design workflow\. Test unsupported inputs as well as successful cases\.

Steps 1–3 may be possible from further public evidence\. Author contact requires your permission; experiments require separate resources and agreement\. Step 5 is software work that can proceed autonomously with clearly labelled provisional scenarios\. Access to a paper is not permission to redistribute all its figures or data; this deliverable contains original code and analysis rather than a copied paper\.

## Deferred questions and assumptions register

|Question for your son later                                                      |Provisional assumption                                             |Basis and sensitivity                                    |Priority / consequence                         |
|---------------------------------------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------|-----------------------------------------------|
|Is this laminate a useful first ceramic benchmark for your intended applications?|Use it as one screening case, not the product’s full domain        |Published calculable example; relevance unconfirmed      |High: may change first demonstration pair      |
|Is the pure-layer elastic approximation adequate for a demonstration?            |Accept only with an explicit idealisation label                    |Benchmark model; inclusions/damage can change predictions|High: determines permitted claims              |
|What stress-free temperature and temperature-dependent properties are defensible?|Replay the paper’s constants only                                  |Stress scales directly with cooling span                 |High: absolute stresses uncertain              |
|What evidence resolves the thickness assignment discrepancy?                     |Preserve both interpretations; do not choose silently              |Diagnostic reversal matches rounding                     |High: exact reproduction remains unresolved    |
|What layer sizes and mixing response can the intended process achieve?           |No universal limit; treat purge result as surrogate-specific       |No validated ceramic transfer function reproduced        |Critical before physical design recommendations|
|What counts as a successful revised design?                                      |Demonstrate transparent trade-offs, not safe/no-crack certification|No approved acceptance thresholds                        |High: constrains ranking and claims            |

These questions are recorded for later review\. Your son’s opinion would help scope and interpretation, but cannot replace missing experimental data\.

## Re\-run and handoff

Repository directory: `wp0_manufacturing/`\. Run `python3 wp0_manufacturing/reproduce.py` from the repository root\. The script runs five tests and regenerates `results.json` deterministically\. Existing application code was not modified\. No changes were pushed to GitHub\.

Recommendation: use this as an **auditable partial\-reproduction benchmark** in the bounded prototype\. Do not mark the general manufacturing\-feedback gap closed\. The next evidence milestone is a ceramic command\-to\-achieved\-state dataset with documented feed commands, extruded volume, measured outlet composition, achieved layer geometry, porosity, uncertainty, and provenance, followed by validated re\-evaluation of the revised design against the baseline using those achieved\-state measurements and manufacturing constraints\.