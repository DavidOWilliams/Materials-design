# Ceramic command-to-achieved-state evidence milestone

19 October 2026

## Outcome

The requested milestone is **not yet met**. I assembled an auditable partial ceramic dataset and executed a retrospective comparison of manufactured gradient designs. Missing measurements prevent the full achieved-state simulation and independent validation requested. Filling these fields with assumptions would change the meaning of the milestone.

There are two distinct cases. The previous B4C-SiC 4:1 revision remains an analytical proposal without measured revised specimens. The new alumina/zirconia case offers stronger manufacturing-response evidence and a measured comparison of alternative gradients. Results from the latter cannot validate the former.

The package contains `ceramic_evidence.json`, `evaluate_ceramic.py`, and `ceramic_evaluation.json`. Missing values are null, with reasons. Data are classified by stage, composition basis and source location. No experiment or external contact has occurred.

## Sources inspected and choice

Primary extraction: Li et al. (2018), *Fabricating Functionally Graded Materials by Ceramic On-Demand Extrusion with Dynamic Mixing*, pp.1087–1099, [DOI](https://doi.org/10.26153/tsw/17109), [institutional PDF](https://utw10945.utweb.utexas.edu/sites/default/files/2018/088%20FabricatingFunctionallyGradedMaterialsbyCeram.pdf). The downloaded PDF hash is recorded in the dataset. Figures 3 and 7 and Table 1 were visually checked. Numeric labels were transcribed; original figures are not redistributed.

Supporting discovery: the [2021 journal study](https://doi.org/10.1016/j.jeurceramsoc.2020.10.029) and [institutional record](https://scholarsmine.mst.edu/matsci_eng_facwork/2739/) describe composition and dimensional evaluation. The journal full-text retrieval returned HTTP 403. The [2019 dissertation](https://scholarsmine.mst.edu/doctoral_dissertations/2783/) was located, but its download also returned HTTP 403. Their inaccessible contents were not assumed to fill gaps or treated as independent replications.

Other leads inspected through primary publication records: [Pelz 2021](https://doi.org/10.1016/j.addma.2020.101647), [Gong 2026](https://doi.org/10.1016/j.addma.2026.105336), and [active-mixing printhead 2024](https://doi.org/10.1016/j.addlet.2024.100217). Pelz's transition calibration is a surrogate; Gong's full-text retrieval was blocked; the 2024 paper states data are available on request and was not established as a matching ceramic dataset. Targeted searches of institutional records and indexed data repositories did not locate a complete linked raw dataset. This is a documented search outcome, not proof that none exists.

## What the new source supplies

The CODE experiment uses alumina/3Y-zirconia pastes. Ceramic transition EDS was measured after sintering; it is an indirect outlet record. Reported delivery/transition volumes are 0.12/0.36 mL; purge is 0.5 mL per change. Eleven-layer designs use 5%, 10% or 50% composition steps. Figure 7 provides rounded per-layer composition means; Table 1 provides three curling observations per design. No complete specimen-linked porosity or layer-geometry dataset was recovered.

| Required field | What is in our dataset | Qualification |
|---|---|---|
| Feed commands | Layer composition recipes and transition command description | Reconstructed intent; actual G-code, timing and feed-rate logs missing |
| Extruded volume | Published delay endpoints and purge quantity | No measured cumulative-volume trace or instrument uncertainty |
| Outlet composition | Three visually read transition anchors; eleven labelled layer means | Sintered measurements, not live outlet samples; full raw EDS missing |
| Achieved layer geometry | Curling observations | Individual layer boundaries, thicknesses and final dimensions missing |
| Porosity | Null | Neither zero nor a generic process density substituted |
| Uncertainty | Replicate curling variability, display resolution, extraction allowance | Instrument uncertainty and raw composition variability missing |
| Provenance | DOI, URL, page/figure, stage, extraction method, file hash | Specimen identities do not join all measurements |

The transition anchors have a declared visual-reading allowance of +/-2 percentage points, assigned for extraction only. It is not experimental uncertainty. Figure 3 locations are unevenly spaced: interpolation of location numbers into equally spaced extrusion volumes would create false data. The three volume anchors alone cannot identify or validate a general mixer-response model.

EDS atomic fraction is retained as atomic fraction. It is not equated with commanded ceramic volume fraction. Conversion requires a documented chemical/phase basis, density and stabilizer treatment. Figure 7 means are aggregated across specimens and cannot be silently assigned to the curling specimens.

## Executed baseline/revision comparison

For this alternative case only, I designated the 10% step design as baseline and the 5% step design as revised. These are retrospective labels for published specimens, not evidence that we prospectively designed and manufactured a revision.

| Quantity | Baseline, 10% steps | Revised, 5% steps |
|---|---:|---:|
| Observed curling, degrees | 3.6, 3.8, 3.7 | 2.7, 2.3, 2.9 |
| Calculated mean, degrees | 3.700 | 2.633 |
| Calculated sample standard deviation, degrees | 0.100 | 0.306 |
| Composition changes | 5 | 10 |
| Calculated purge, mL | 2.5 | 5.0 |
| Nominal mean zirconia fraction, equal-layer assumption | 27.27% | 25.00% |

The observed mean reduction is **28.83%**, with reductions of 0.9, 1.5 and 0.8 degrees across the reported groups. The purge calculation adds 2.5 mL. Standard deviations describe the three observed specimens; they do not quantify measurement accuracy or future process reliability.

The finer gradient has lower observed curling and higher calculated waste, so neither design dominates on both objectives. A purge budget below 5 mL would exclude the finer recipe if this purge policy is retained. No user acceptance limit for curling or waste has been assumed. These are recipe-specific constraints, not universal machine limits.

The nominal composition budgets also differ. Consequently the observed improvement cannot be attributed solely to gradient smoothness at fixed material usage. In the abrupt-step reference, one specimen cracked and two delaminated. The evaluator preserves those failure states and refuses to average only the surviving angle.

The labelled composition values yield a mean absolute difference of 1.091 percentage points and maximum 2 points against the labelled nominal values. This is a check of rounded published labels, not an independent validation of composition prediction.

## What validation is and is not complete

Completed: transcription checks, reproducible descriptive calculations, purge arithmetic, preservation of failure outcomes, and an explicit failed completeness gate. The script checks recipe bounds and layer count, purge accounting and failure handling.

Incomplete: fitting or selecting an existing physical response model with adequate inputs; prediction of a held-out command sequence; stress or deformation re-evaluation using measured per-layer geometry, composition and porosity; validation against independent revised specimens; validation of the B4C-SiC 4:1 proposal. No such predictions are reported.

In particular, the previous symmetric laminate stress equations cannot simply be applied to an asymmetric curling specimen. A compatible existing bending/thermomechanical formulation and shrinkage history would be required. Neither a newly invented scientific model nor a fitted proxy has been substituted.

## Concrete data acquisition request, ready for review

The next action is to request the underlying CODE records from the authors. This text has not been sent:

> We are building a research prototype that evaluates how ceramic manufacturing changes an intended composition and geometry, and are seeking to reproduce your CODE gradient experiments. Could you share the data supporting the 2018 conference study and its 2021 journal development, together with permission or licensing terms for research reuse? We need the original G-code and time-stamped feed commands, actual extrusion-flow or cumulative-volume measurements and calibrations, raw EDS spectra/counts with sampling positions and replicates for the transition trace and each gradient design, and the link between these records and specimen IDs. We also need green/dried/sintered dimensions and individual layer boundaries, density/porosity measurements and methods, thermal schedules and machine settings, raw curling/height observations, failures, instrument uncertainties and calibration information. Please identify any fields that were not measured. Repeat transition runs or held-out specimens would be especially useful. We would preserve provenance, distinguish measured values from assumptions, and attribute the work.

This request should initially go to the corresponding author of the CODE work, with the current contact address verified before sending. The author data may still be incomplete; contact cannot guarantee completion. Your son need not be involved.

## Acquisition contract if additional measurements are needed

Every measurement must retain specimen ID, run ID, feedstock batch, stage, units, method, uncertainty definition, source file/hash, and the coordinate transform connecting nozzle deposition to final position. Tables should join as follows:

| Table | Minimum fields |
|---|---|
| Runs | material batches, solids loading, machine/nozzle/mixer, settings, thermal history |
| Commands | run ID, timestamp, feed A/B commands, units, intended composition basis, purge events |
| Extrusion | timestamp, cumulative actual volume, calibration and uncertainty; command volume separately |
| Outlet samples | volume interval, sampling time, measured composition/basis, raw replicates, method and uncertainty |
| Achieved layers | specimen/layer ID, geometry and coordinates at each stage, measured composition, porosity, uncertainty |
| Outcomes | specimen ID, deformation/stress or other approved target, failure category, raw measurements |

If existing records are inadequate, use the same material batches/process for baseline and revision; include end-member controls, both transition directions and the intermediate feed ratios used by the designs. Reserve complete runs and specimens for validation before model calibration. A provisional pilot would use at least three independent specimens per design and three transition runs per direction; this is a starting design, not a statistically justified final sample size. A laboratory should set the final number from variability and the decision threshold.

Measure total and local porosity with methods appropriate to the required resolution, stating open/closed porosity coverage and detection limits. Do not infer local porosity from a single bulk density without justification. Measure geometry at green, dried and sintered stages so dimensional change is not attributed to the wrong process. Include failure specimens in the results.

Before evaluation, freeze the baseline/revision definition, material budget policy, target outcome and acceptable error. Select an existing published model only after confirming that the recovered inputs support it. Evaluate held-out composition-versus-volume errors, geometry errors and outcome errors separately. Propagate measurement and parameter uncertainty. Accept an improvement only if it meets the chosen outcome threshold and manufacturing constraints across the justified uncertainty range. Thresholds remain provisional until there is an application requirement; choosing them after seeing results would bias validation.

## Questions deferred for your son

| Question | Assumption used now | Impact / priority |
|---|---|---|
| Is alumina/zirconia an acceptable additional prototype benchmark? | Include it as an explicitly separate case | High: stronger manufacturing evidence, different domain |
| Should revision hold total material fractions fixed? | Report the current difference; make no equal-budget causal claim | High: affects optimisation comparison |
| Which outcome and tolerance matter first? | Compare observed curling and purge without a pass/fail application threshold | High: no engineering acceptance claim |
| Which porosity scale and geometry resolution are needed? | Require specimen/layer-resolved evidence before local-property evaluation | High: affects measurement effort and model applicability |
| Which existing model adequately represents shrinkage, bending and damage? | Defer selection until inputs are available | Critical for physical validation |

The questions and assumptions are recorded so that the prototype can progress without early involvement from him. Missing physical measurements cannot be replaced by expert opinion.

## Reproduction and completion boundary

Run `python3 evaluate_ceramic.py` with the JSON input in the same directory. It regenerates `ceramic_evaluation.json`; `milestone_gate.passed` remains false with explicit blockers. No third-party Python dependency is needed. Code and data were added locally in `wp0_manufacturing/`; nothing was pushed to GitHub.

I can complete the ingestion, calculations and validation once the missing records are obtained. Full completion currently depends on author-supplied raw data or new laboratory measurements. The attached package makes that dependency precise and provides a useful measured ceramic comparison in the meantime.
