# WP0R recovered reference assets

21 October 2026. These are standalone verification assets, not D1 or V1.

`ceramic/` is recovered byte-for-byte from the retained WP0 ZIP.
`thermal.py`, `laminate.py` and `test_recovery.py` are new reconstructions from
the saved reports. They are not the missing original commit `51c84ac`.
`evidence/` preserves the saved reports and implementation plan, including
the later-review questions A01–A15 and their assumptions.

## Run from repository root

Use Python 3.12.14, create an isolated virtual environment and install
`recovered_wp0/requirements.txt`. Then run:

```sh
python -m pytest recovered_wp0 -q
python -m recovered_wp0.thermal --output recovered_wp0/thermal_results.json
python -m recovered_wp0.thermal --output recovered_wp0/thermal_results.json --replay
python -m recovered_wp0.laminate
python recovered_wp0/ceramic/evaluate_ceramic.py
```

The direct numerical dependencies retain the original WP0 versions.
`environment-freeze.txt` records the observed expanded verification environment;
it is not a claim to have reproduced every pin in the legacy requirements file.

## Acceptance limits registered in the reconstructed checks

- At 128 elements, Fourier flux relative error <3e-5 for all three fixtures;
  flux spread <1e-5 W/m²; temperature boundaries and bounds retained.
- Graded relative error falls by more than a factor of three per refinement.
- Separate-process replay: temperature rtol 1e-10, atol 1e-8 K; flux rtol
  1e-10, atol 1e-7 W/m². Input hashes must match.
- Laminate force balance residual <1e-5 Pa and independent compatible-strain
  formulation agrees to rtol 1e-12. Preserve both thickness assignments.
- Ceramic evaluation output must remain byte-identical on replay. Missing
  fields remain null and its validation gate remains false.

These tolerances verify the code against retained reference definitions.
They are not uncertainty bounds or criteria for physical ceramic validation.

## Claim boundaries and open work

Thermal fixtures prescribe synthetic spatial conductivity directly. The laminate
benchmark assumes seven symmetric ideal bonded layers and constant properties;
negative stress means tension in its source convention. The reversed-thickness
case is diagnostic, not a correction to the publication. No shrinkage, porosity,
mixing-lag or crack-prediction model has been added.

The ceramic comparison has unequal composition budgets, incomplete specimen
linkage, and missing command logs, achieved layer geometry, porosity and
measurement uncertainty. The recovered `paired_group_differences_deg` field
is an arithmetic subtraction by table group index, not evidence of a paired
experimental design or a paired statistical significance test. Use the group
means descriptively only. Access and reuse terms remain as recorded in the source.

The remaining work begins with WP1 strict product contracts, assumption registry,
run storage and dependency locking, then bounded mechanics and the first complete
UI-to-feedback loop. These small WP0 contracts do not replace the WP1 product schema.
No request has been sent to David's son or to the paper authors.
