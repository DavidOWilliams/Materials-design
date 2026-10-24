# WP0 decision pack — material-system inverse design

19 October 2026 | David Williams | Assessment and technical trial

## Decision and status

Recommend a new numerical inverse-design core within the existing Materials-design repository, with selective reuse and a preserved legacy application. Use one lead agent coordinating parallel bounded workstreams. David's son is not a dependency for initial implementation; he reviews the complete working bounded demonstration afterwards.

The WP0 architecture/environment assessment and technical trial are complete. **The original scientific G0 gate is not passed.** A compatible, openly reusable ceramic material/process/property benchmark has not been established sufficiently to freeze the material pair and manufacturing feedback model. This is a substantive remaining dependency, not something the successful software tests resolve.

Recommended next decision: permit product-foundation work while retaining the real-ceramic evidence gate. An alternative is to build the complete workflow first with explicitly assumed process-capability scenarios; that would narrow the initial demonstration's scientific claim and needs an explicit scope decision. Neither option requires involving David's son now. Do not treat provisional build permission as scientific acceptance.

## Agreed objectives and changes to the delivery baseline

The intended full demonstration starts with a performance brief, proposes materially different constituent/architecture/gradient alternatives, evaluates competing objectives, revises designs using manufacturing feedback, and presents the evidence through a usable interface. Comparison alone, keyword scores, or tuning a fixed supplied design do not satisfy this objective.

The vision remains unchanged. The implementation approach changes in three ways:

1. Preserve the repository, but do not let its historical architecture govern the new core.
2. Use multiple agents under one accountable integration lead; David does not manage individual agents or routine code changes.
3. Defer the son's scientific review until after the full bounded prototype. Record all questions, assumptions, consequences and sensitivity checks.

The 14 October Product Definition v1.0 requires scientific-reviewer acceptance at G0/G3. This pack records a proposed amendment: separate build-feasibility, numerical verification, functional demonstration, and scientific acceptance. The latter remains pending; the original document has not been silently overwritten.

## Baseline and repository evidence

Audited main: f3e6cfc7f7e9ed885ce681814c0927fc421163c8. Remote main was rechecked on 19 October and remained at that revision. Work is isolated on local branch wp0-feasibility-2026-10-19. No legacy production files have been modified.

The earlier audit counted 105 src Python files, approximately 34,600 lines and 65 test files. Its 1,120 passing tests excluded three import-dependent legacy modules; that was the earlier audit, not a newly repeated full-suite result. Current WP0 adds and executes 17 targeted checks plus separate-process replay. The supplied handover understates later ceramic, coating, gradient, evidence and comparison work present in main.

The build-4-material-system-architecture branch was previously checked: four commits ahead and 56 behind main. Its additional gradient/application diagnostics are candidates for selective extraction, not grounds to replace main wholesale. Current local inspection found no AGENTS.md. Before subsequent delivery, add a single current instruction/acceptance entry point and mark historical restrictions as phase-specific.

| Finding | Evidence | Consequence |
|---|---|---|
| Numerical capability is much less complete than the scaffolding | Ceramic factors use keyword proxies; specialist adapters are disabled; one optimisation path generates no variants | Do not count modules as working scientific capabilities |
| Existing criteria integration is predominantly planning | Demo produced 36 placeholders, zero populated values | Implement real evaluation contracts and backends |
| Optional and duplicate data shapes | Material-system TypedDict retains old/new fields | Introduce one strict versioned schema per numerical concept |
| Dependency direction is tangled | Criteria schema imports candidate-normalisation planning | Domain contracts must not depend on orchestration |
| Scientific and UI concerns are coupled in legacy path | Candidate generator imports Streamlit | Keep new core independent of UI and retrieval dependencies |
| Missing-data comparison is unsuitable for physics | Legacy Pareto can declare dominance using shared objectives despite another missing objective; accepts NaN | Replace physical eligibility and comparison logic |
| Qualitative references are useful but insufficient | Loader returns 3 ceramic, 6 CMC, 10 coating and 10 graded records | Use as discovery hints; require numerical provenance before simulation |

## Architecture alternatives and reuse decision

| Option | Benefit | Cost/risk | Decision |
|---|---|---|---|
| Extend current architecture | Retains all existing wiring | Multiple conventions, compatibility fields and historic no-execution boundaries | Not preferred |
| Completely new repository/application | Clean structure | Recreates useful concepts, reporting and regression lessons | Reserve if selective extraction becomes more expensive than replacement |
| New core in existing repository | Clear numerical contracts with history and reusable assets | Requires explicit boundary and disciplined integration | Recommended |

Reuse loaders only through a narrow boundary; preserve required-column checks and add units, conditions and source rights. Adapt evidence/review vocabulary, reference examples and export ideas. Keep legacy rankings/proxy factors separate. Replace numerical comparison, execution management, property contracts and inverse-loop control. Existing tests remain for the old route; port behavioural intent, not old prohibitions on new functionality.

Proposed new contracts: Brief, PropertyEvidence, IntendedDesign, ManufacturingPlan, ManufacturedState, Evaluation, Run and AssumptionReview. Validate finite values, units, coordinates, constituent fractions, supported domains and required objectives. Keep intended and achieved states separate and immutable. Changing an assumption creates a new run; cached results depend on input, solver and evidence hashes.

Begin with Python modules, SQLite run metadata and filesystem artifacts. UI calls application services. Scientific tools execute through adapters in isolated environments. No microservice platform, GPU dependency or multiuser infrastructure is needed for the first demonstration.

## Executed technical benchmark

Purpose: establish numerical integration and representation feasibility. It is not the full prototype, a real ceramic dataset, an inverse-search demonstration or a manufacturing model.

Specification: 10 mm planar slab, steady one-dimensional Fourier conduction, fixed boundaries 400 K and 300 K, synthetic conductivity endpoints 2 and 10 W/(m K). Homogeneous k=2; equal-thickness discrete layers k=2/10; graded k varies linearly through thickness. Conductivity is prescribed directly, not inferred from composition. No heat source, interface resistance or lateral heat loss. Meshes: 8,16,32,64,128 linear elements.

Backend: scikit-fem 12.0.2 finite-element assembly with NumPy 2.3.5 and SciPy 1.17.0, Python 3.12.14. Installed scikit-fem BSD-3-Clause licence inspected. Existing Fourier formulation is configured; no scientific model is trained or invented. Independent reference: series resistance integral, including the closed-form logarithmic resistance for the linear gradient.

| Case, 128 elements | Heat flux W/m² | Relative error against independent reference |
|---|---:|---:|
| Homogeneous | 20,000.000000 | 0 |
| Layered | 33,333.333333 | 8.22e-14 |
| Graded | 49,708.001008 | 2.43e-5 (0.00243%) |

The graded error decreases by more than a factor of three per mesh refinement. Flux conservation and boundary/temperature checks pass. These cases are not an optimisation contest: they have different conductivity distributions and no equal material-use constraint. Lower or higher flux does not by itself identify the preferred material system.

Nine spike tests pass, covering analytical agreement, convergence, conservation, persistence hashes, temperature bounds and strict comparison of complete finite objectives. Eight architecture tests pass, covering identical backend results, required fields, nonfinite/invalid values, legacy incompleteness, inconsistent architecture, explicit units and immutable input copies. Separate-process replay passes for stored inputs/results. No cross-machine reproducibility claim is made.

The same-backend comparison confirms that a legacy candidate can reach the new numerical backend only when explicit numerical fields are added. The clean contract and bridge deliver identical inputs and outputs for all three architectures. Actual legacy reference records without those fields are rejected rather than assigned invented values. This supports a narrow adapter strategy. It does not establish runtime superiority or measured end-to-end development-time savings, and does not constitute a full implementation of all three architecture options.

Reproduce from repository root:

```sh
python -m unittest discover -s wp0_spike -p 'test_*.py' -v
python -m unittest discover -s wp0_comparison -p 'test_*.py' -v
python wp0_spike/spike.py --replay
python -m wp0_comparison.compare
```

Install wp0_spike/requirements.txt in an isolated Python environment first. The observed run used the existing numerical runtime and an ignored local scikit-fem install; a clean Codespaces/container build remains unexecuted.

## Scientific resource qualification

| Resource | Confirmed | Not established / decision |
|---|---|---|
| scikit-fem | Installed, executed, BSD-3-Clause inspected, thermal reference checks pass | Assembly library; not a validated ceramic simulator |
| SfePy thermoelasticity | Official existing linear-elastic/thermal-strain example and BSD licence source inspected | Not installed/reproduced; first candidate for bounded thermal mismatch integration |
| MOOSE | Existing coupled thermal/mechanical tutorial identified | Heavier alternative; not installed/reproduced here |
| NIST dense alumina summary | Temperature-dependent property table with material conditions and uncertainties | SRD reuse terms need record-specific resolution; no matching printed/graded chain |
| Pelz B4C–SiC DIW paper | Full article accessible; active mixing and analytical thermal-mismatch treatment | Dataset redistribution rights and complete compatible service property pack not established |
| Alumina/zirconia DIW literature | Relevant process/interface research identified | Matching compositions, mixture properties and reusable model inputs not obtained |
| rheoTool | Open repository, non-Newtonian tools, documented supported OpenFOAM variants | No ceramic mixer/rheology/transition benchmark reproduced |
| Ghent CFD initiative | Relevant capability demonstrations | Public implementation download and implementation licence not verified |

NIST data describe dense high-purity sintered alumina under specified conditions. They cannot automatically represent printed parts. Its expansion column is referenced to 0 C; conversion must preserve that convention. The official NIST policy distinguishes copyrighted Standard Reference Data from other data. No general public-domain assumption is used for SRD150.

The preferred real-material investigation remains alumina plus a precisely identified stabilised-zirconia grade, but the pair is NOT frozen. B4C–SiC offers a useful published process/stress reference; switching to it is not automatically evidence that it suits the thermal-protection duty. Do not invent a generic zirconia grade, mixture law, sintering strain or mixing lag to close the gap.

A limited manufacturing scenario can map an intended gradient to finite layer/composition resolution and reevaluate the achieved field. It must state assumed capability limits and cannot be advertised as validated printer fidelity or CFD. A physically supported mixing/extrusion model needs compatible rheology, geometry, operating parameters and independent transition observations. Thermal mismatch alone is never labelled total manufacturing residual stress.

## Environment and autonomous delivery

The existing development container targets Python3.11 while this run used3.12. Its157 pinned packages mix UI, Jupyter, retrieval and scientific dependencies. Setup includes an unbounded OS upgrade, a separate unpinned Streamlit install and commands that can mask earlier failures. Attachment launches Streamlit with CORS/XSRF protections disabled. No CI workflow or current agent instructions were found. These are setup tasks, not reasons to preserve the existing architecture.

Use one Python3.12 core environment with a generated lock and optional dependency groups; fail-fast setup; identical local/CI commands; safe default UI settings; numerical worker environments pinned separately. Docker/Conda/MPI and heavy solver executables were not available here. Their availability in David's Codespace is not inferred. No external paid compute was provisioned.

WP0 demonstrated parallel work across scientific research, architecture and environment/spike implementation. The lead reviewed findings and reran the17 tests and replay. Agents used bounded separate directories. For sustained delivery use separate worktrees and contract ownership, with integration at small increments. This demonstrates practical delegation, not a measured multiplier over single-agent productivity.

Agents can implement code, prepare data, run tests, diagnose integration and produce review packs. David supplies product/scope/budget decisions only when needed. The son supplies no initial-build input. Unresolved scientific questions go into the register; they cannot be removed merely because code runs.

## Delivery path and revised estimate

Estimates are planning ranges, not observed full-build performance. With functioning CPU access and an agreed provisional scenario scope, allow approximately4–6 weeks for a complete bounded computational workflow using existing thermal/mechanical formulations and explicit process-capability scenarios. That is a narrower claim than a validated ceramic process chain. An evidence-backed ceramic/manufacturing demonstration retains the prior8–12-week planning range, conditional on closing data and solver reproduction gaps; the present evidence does not justify a guaranteed completion date.

| Increment | Outcome | Exit evidence |
|---|---|---|
| Foundation | Strict contracts, run ledger, clean setup, assumption IDs | Invalid inputs rejected; restart/replay; legacy untouched |
| Scientific adapters | Thermal and bounded thermoelastic evaluation | Analytical free/constrained expansion cases, convergence, source conditions |
| Inverse search | Multiple architectures and constituent choices within supported domain | Changed brief yields new proposals; fair sampling baseline; no fake solver outputs |
| Manufacturing feedback | Intended-to-achieved mapping followed by recalculation | Measured/evidenced process parameters OR explicitly approved scenario status |
| Interface and dossier | Usable brief entry, comparison, provenance, cancellation/export | Full end-to-end demonstration and saved-run recovery |
| Deferred scientific review | Son sees working prototype and prioritised questions | Assumptions accepted/revised; affected runs repeated; scientific acceptance recorded separately |

Before a real-material result is called feasible, resolve: exact material states, compatible properties and intermediate compositions, reuse terms, stress-free state, mechanical constraints, process mapping and validation reference. No live researcher contact is authorised or performed.

## G0 disposition and next decision

| G0 item | Status |
|---|---|
| Repository audit / architecture recommendation | Complete |
| Autonomous implementation/environment trial | Complete,17 checks and replay passed |
| Numerical thermal verification fixture | Complete, three synthetic architecture classes |
| Complete real ceramic benchmark / final material pair | Open |
| Thermomechanical reference reproduction | Open |
| Evidence-backed manufacturing feedback | Open |
| Scientific data reuse terms | Partly checked; critical dataset terms open |
| Assumption/deferred-question register | Complete initial version; all scientific entries open |
| Son's scientific acceptance | Intentionally deferred until full prototype |

Recommendation: proceed with the new-core foundation and continue the targeted evidence work; do not claim G0 scientific pass. If prioritising a complete working demonstration immediately, explicitly approve a computational scenario demonstration with assumed manufacturing-capability limits as the first release. Keep the real-ceramic evidence-backed case as a separate acceptance milestone. This is the one material scope decision emerging from WP0.

## Deferred questions and assumptions

The companion assumption_review_register.md contains15 exact questions with provisional answers, affected work, sensitivity and priority. Topics: useful geometry/duty; exact ceramic pair; transfer from bulk to printed properties; elasticity domain; stress-free temperature/restraint; mixture mapping; interface bonding; signed stress metrics; manufacturing mechanism/resolution; omitted drying/sintering/phase physics; expansion conventions; objectives; uncertainty; physical validation; expert comparison. No questions have been sent to the son.

## Sources and evidence locations

Accessed19 October2026 unless noted. Availability is not validation; this is targeted feasibility research, not an exhaustive literature review.

- Project delivery baseline: Material_System_Product_Definition_and_Delivery_v1.docx,14 October2026; agreed vision v3; user decisions in this conversation.
- Audited source: https://github.com/DavidOWilliams/Materials-design/tree/f3e6cfc7f7e9ed885ce681814c0927fc421163c8
- scikit-fem: https://github.com/kinnala/scikit-fem and installed12.0.2 licence metadata.
- SfePy formulation: https://sfepy.org/doc-devel/examples/multi_physics-thermo_elasticity.html ; licence: https://github.com/sfepy/sfepy/blob/master/LICENSE
- MOOSE candidate: https://mooseframework.inl.gov/modules/combined/tutorials/introduction/thermomech_step01.html
- NIST alumina: https://srdata.nist.gov/CeramicDataPortal/Pds/Scdaos ; policy: https://www.nist.gov/open/license
- Pelz et al.: https://doi.org/10.1016/j.addma.2020.101647 ; accessible article https://meyersgroup.ucsd.edu/papers/journals/Meyers%20481.pdf
- Alumina/zirconia interface research: https://doi.org/10.1016/j.addma.2026.105336 (abstract-level assessment; reusable full inputs unverified).
- rheoTool: https://github.com/fppimenta/rheotool ; Ghent: https://cfdmodels.ugent.be/
- Executed artifacts: wp0_spike/results.json, wp0_spike/README.md, wp0_comparison/results.json and their scripts/tests.

No engineering qualification, full ceramic physical validation, complete inverse-design prototype, working CFD coupling, expert-value evaluation or paid deployment is claimed by this WP0 pack.
# WP0 assumption and deferred scientific review register

Date: 19 October 2026. Owner: delivery lead. Reviewer: David's son, only after the complete bounded prototype. All entries are OPEN unless explicitly resolved. These assumptions authorise transparent implementation choices, not claims of physical validity. No request has been sent to the reviewer.

Every future run must record applicable IDs and assumption versions. A change creates a new run and invalidates dependent cached evaluations. Critical missing inputs remain unresolved; absence is never converted to a favourable value. Sensitivity work below is planned unless the numerical results explicitly record execution.

| ID | Exact question for reviewer | Provisional answer used/planned | Basis and affected work | Sensitivity / acceptance consequence | Priority |
|---|---|---|---|---|---|
| A01 | Is a planar ceramic coupon an appropriate first comparison geometry for the intended material-system discovery task? | Use a planar coupon; begin with through-thickness conduction. | Simplifies numerical verification. WP0 thermal spike is synthetic, not an aviation part. | Later compare 2D geometry/edge effects before stress conclusions. | Required before interpreting application value |
| A02 | Which ceramic pair and processing states give a defensible common property dataset? | Investigate alumina/zirconia first; do not freeze a real pair until compatible data are obtained. WP0 uses anonymous synthetic A/B conductivities. | Existing agreed direction; pairing is NOT established by the synthetic trial. | Pair substitution changes evidence, interfaces and manufacturing feasibility. | Blocking real-material conclusions |
| A03 | Can the selected property measurements represent the printed and fired material? | Dense bulk properties are not assumed to be printed-paste or as-manufactured properties. | Porosity, grain size, phase and process history differ. Evidence catalogue must preserve these conditions. | Run alternatives only within supported measured domains; missing mapping stays unresolved. | Blocking manufactured-state claims |
| A04 | Is isotropic linear thermoelasticity adequate for the selected duty and temperature range? | Use only for bounded elastic thermal-mismatch estimates after reference reproduction. | Existing SfePy thermoelastic example is a candidate, not yet reproduced. | Check load/temperature ranges; creep, damage and phase changes remain excluded. | Required before stress interpretation |
| A05 | What stress-free temperature and restraint represent each manufacturing route? | No single universal firing temperature is assigned. Require explicit scenario values and provenance. | Thermal strain depends on history and constraints. | Sweep justified reference-temperature and restraint scenarios; report ranking reversals. | Blocking residual-stress conclusions |
| A06 | How should constituent properties map across a composition gradient? | No undocumented mixture rule is accepted as measured evidence. Synthetic spatial conductivity is prescribed directly in WP0. | Constituent endpoints alone do not establish effective mixture properties. | Compare supported bounds/laws only after their applicability is documented. | Blocking quantitative graded-ceramic claims |
| A07 | Are perfectly bonded interfaces a reasonable first assumption? | Treat perfect bonding as an explicit idealisation, never as demonstrated interface strength. | Existing continuum interface treatment; no adhesion data established. | Contact resistance/interface compliance scenarios where supported; otherwise mark unassessed. | Required before architecture preference |
| A08 | Which stress metric is informative for cracking or delamination? | Retain signed tensile/compressive fields and use nonsingular regional measures; no lifetime claim. | Compression can help one failure mode while another worsens. | Region/mesh checks and separate interface assessment. | Required before failure-risk conclusions |
| A09 | Is finite layer/feed resolution an adequate first manufacturing feedback mechanism, or is mixing lag essential? | Evaluate the simplest evidenced mechanism; do not invent a mixing time constant. | Process capabilities require source-specific parameters. WP0 has not implemented manufacturing physics. | Compare intended and achieved fields, then recompute; unresolved process data block physical coupling. | Blocking manufacturing-feedback acceptance |
| A10 | Which drying, debinding, sintering and phase-change mechanisms could reverse the comparison? | Full residual stress remains unresolved; thermal mismatch is only one contribution. | No complete supported process-history chain obtained. | Explicit exclusions per candidate, not a single confidence score. | Required before trusting preferred material |
| A11 | Are temperature dependence and expansion-reference conventions handled correctly? | Preserve source conventions; secant expansion from 0 C is not silently treated as instantaneous alpha. | NIST alumina source identifies its expansion reference. | Check strain conversion against reference values and vary interpolation. | Required before using those data |
| A12 | Are thermal transmission, mass and tensile stress the appropriate three objectives? | Proposed objectives only; each requires physical units and common boundary conditions. | Agreed multiobjective intent; no proxy score replaces missing physics. | Change objective constraints and test whether the design changes coherently. | Useful product refinement; required for scientific framing |
| A13 | What material variability and uncertainty ranges are justified? | Use source uncertainties where available; clearly distinguish analyst scenarios from statistical distributions. | No universal percentage or invented probability model. | Report sensitivity and ranking reversals, not unsupported confidence intervals. | Required before robustness claims |
| A14 | What should constitute an independent physical validation case? | Analytical checks verify numerical implementation; they do not validate a printed ceramic. | WP0 verifies conduction and replay only. | Match published measurements with their conditions and uncertainty before claiming physical agreement. | Blocking scientific acceptance |
| A15 | Does the discovered alternative offer meaningful improvement over an expert shortlist? | Defer expert shortlist and expert-time comparison until the full demonstration is available. | User explicitly postpones son's involvement. Use transparent algorithmic baselines meanwhile. | No claim that expert productivity/value has already been established. | Required for post-build product evaluation |

## Operational assumptions decided without scientific reviewer

- O01: retain existing repository and historical implementation; introduce an isolated new numerical core.
- O02: one lead coordinates parallel agents; ownership and contracts are agreed before concurrent changes.
- O03: CPU-first setup; no paid worker or GPU is provisioned without a concrete requirement and budget decision.
- O04: new code may be written and tested autonomously within the bounded scope; external communication with researchers/reviewer is not authorised.
- O05: source accessibility is not a licence. Reuse rights are recorded separately for code, data and weights.
- O06: prototype functional completion precedes scientific acceptance. Original G0/G3 scientific acceptance is not silently waived.

