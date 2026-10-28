# Material System Implementation Plan v2

20 October 2026 | David Williams | Assumption-based bounded prototype

## Delivery decision

Proceed with a complete working demonstration before seeking input from David's son. Build the interface, inverse search, numerical evaluation, manufacturing feedback, design revision and evidence export as one usable workflow. Missing experimental data are represented by explicit scenario assumptions. Obtaining those data and securing scientific acceptance continue separately.

This is the current implementation plan. It supersedes the delivery sequence, dependencies, staffing assumptions and release gates in sections 12–18 of *Material System Product Definition and Delivery v1* where they conflict with this plan. The wider product vision and later capability pathway remain unchanged. The WP0 decision pack and evidence reports remain historical records; their open scientific findings are not retrospectively marked complete.

Two distinct outcomes will be tracked:

- **D1 Working demonstration:** complete bounded functionality, verified calculations and transparent assumptions. This is the immediate release and the point at which David may show his son the prototype.
- **V1 Measured ceramic validation:** linked manufacturing and achieved-state evidence supports an independently checked baseline/revised-design comparison. D1 does not imply V1.

## Current baseline and recovery

WP0 reported a repository audit, a clean-core architecture recommendation and numerical conduction checks across homogeneous, layered and graded fixtures. Subsequent work produced a partial B4C–SiC thermal-mismatch reproduction and a partial alumina/zirconia manufacturing dataset with retrospective comparison. These are useful reference assets, not an integrated prototype.

The earlier development checkout and output files are absent from the current scratch workspace. Prior work was reported as local and not pushed to GitHub. Before building, reconcile the remote repository and retained evidence packages, recover available source, and identify anything requiring reconstruction. Do not assume the earlier local commit is remotely recoverable or claim previous tests as fresh verification.

The prepared author email has not been confirmed sent. The one-page brief for David's son is prepared for later use. Neither an author response nor his involvement is a dependency for D1.

## Bounded release scope

Start with a planar thermal–mechanical coupon. Implement a homogeneous reference plus discrete layered and continuously specified gradient alternatives. Numerically discretising a gradient does not turn its design definition into a discrete-layer architecture. Add a distinct coating/substrate case only when its boundary conditions and interface representation have passed reference checks; otherwise show it as deferred.

The editable brief includes duty, geometry, thermal boundaries, mechanical constraints, objective directions, material-use constraints and evaluation budget. Initial objectives are thermal transmission, areal mass and a defined tensile thermal-mismatch measure. Every objective must use the same functional brief and declared boundary conditions across candidates. If one cannot be calculated reliably for a class, that class stays unresolved for the common comparison.

The search must generate new candidates and revise composition or geometry beyond an initial shortlist. It must vary constituent selection within an explicitly defined catalogue as well as layer/gradient parameters. Start with documented scenario material records where a compatible ceramic property pack is unavailable. Synthetic records must have neutral names and conspicuous labels; isolated real-material measurements cannot be assembled into an apparently validated material record.

Use existing scientific equations and open tools. No new scientific model, predictor training or fine-tuning is included. Missing parameters may be assigned as scenario inputs with units and bounds; a missing physical mechanism is not replaced by an invented formula. The core demonstration must run without an external language-model service.

## Architecture and numerical approach

Retain the existing repository and isolate a new numerical core. Reuse legacy loaders, evidence structures and tests only after inspection. Legacy keyword scores do not become physical objectives. The UI calls services; the core does not import the UI.

Keep separate versioned objects for Brief, MaterialRecord, IntendedDesign, ProcessScenario, EstimatedAchievedState, MeasuredAchievedState, Evaluation and DecisionRecord. An estimated state must never acquire a measured label through export or reuse. Record units, coordinates, composition basis, property conventions, source conditions, solver version and assumption versions.

Begin with the verified Fourier conduction approach, subject to recovery and fresh checks. Select the lightest suitable existing thermoelastic formulation after reproducing free expansion, restrained expansion and a layered reference. The Pelz calculation remains a separate benchmark with its thickness-assignment discrepancy preserved. It is not automatically transferable to asymmetric bending or continuous gradients.

The initial manufacturing mechanism is layer/feed resolution: map the intended design to the resolution permitted by an explicit capability scenario, preserve geometry and material accounting, then re-evaluate the mapped state. If rounding changes the material budget, enforce the constraint or report infeasibility. Do not silently renormalise away the effect.

Mixing lag, shrinkage and porosity effects are later additions within D1 only if an existing formulation can be configured and checked. Otherwise represent their omission and sensitivity limitations explicitly. Full CFD, drying/sintering simulation and total residual stress are outside the D1 critical path. Thermal mismatch must retain that name throughout the interface.

## Work packages and exit criteria

Timings are relative planning ranges for active implementation, not booked dates or guaranteed autonomous background work. Target approximately 4–6 weeks for D1, re-estimated after recovery and the first complete loop. The previous 8–12 week evidence-backed estimate is no longer a commitment for V1: external data availability currently prevents a defensible completion date.

| Package | Indicative window | Work | Exit evidence |
|---|---|---|---|
| WP0R Recover and reconcile | First 1–2 active days | Inspect remote state; recover reference code/data; record source and missing assets; establish isolated branch | Reconciled inventory, current tests and recovery record; estimate revised if reconstruction is material |
| WP1 Foundation | Week 1 | Strict contracts, assumption registry, persistent run store, dependency lock, CPU-first setup | Invalid units/fields rejected; input hashes and saved-run recovery; clean setup exercised |
| WP2 Numerical evaluation | Weeks 1–2 | Thermal and bounded mechanics adapters; property mappings and applicability checks | Independent references, convergence and conservation checks; declared outputs/domain for each architecture |
| WP3 Inverse search | Weeks 2–3 | Constituent and architecture proposals, bounded parameter search, Pareto comparison, budgets | New evaluated proposals; changed brief changes design; equal-budget sampling comparison; failures retained |
| WP4 Manufacturing feedback | Weeks 2–4 | Resolution scenario, intended-to-estimated-state mapping, re-evaluation and redesign | Before/after fields and objectives; at least one revision triggered by a binding manufacturing constraint |
| WP5 User workflow | Weeks 1–4, integrated progressively | Brief editor, campaign execution, design views, comparisons, assumption editing, cancellation and export | David can complete and replay the workflow from the interface without code edits |
| WP6 Demonstration evaluation | Weeks 4–5 | Held-out brief, sensitivity, feedback-on/off comparison, data-integrity tests | Quantified evaluation report, including no-improvement and unresolved cases; no expert-superiority claim |
| WP7 D1 release | Weeks 5–6, earlier if ready | Clean-environment replay, restore test, instructions, example dossier and known limits | Complete demonstration passes the D1 checklist below; evidence package tied to a source revision |
| E1 Evidence acquisition | Parallel, bounded effort | Track author request status; assess incoming data/rights; retain missing-field ledger | Data-readiness decision; no invented completion date |
| E2 Scientific review and V1 | After D1, when evidence permits | David may invite his son to review and propose a suitable case; validate models and revised designs | Separate scientific acceptance record and measured comparison, or explicit remaining blockers |

Build the first complete loop by the end of approximately week 2 using small numerical cases and one manufacturing scenario. Broaden search and improve the interface after that loop works. Do not defer integration until the final week.

## D1 acceptance checklist

1. An editable brief produces multiple evaluated alternatives across at least three supported architecture classes, including a homogeneous reference. At least one evaluated design is generated beyond the initial shortlist.
2. Three consequential objectives have units, declared directions and common comparison conditions. Missing/nonfinite outputs cannot improve ranking. Incompatible scenarios are compared separately.
3. A manufacturing assumption changes an estimated achieved composition/geometry field. The changed field reaches the evaluators and alters performance or feasibility. At least one search iteration responds by changing the material/gradient design, rather than only process settings or explanatory prose.
4. A second brief or binding constraint produces an appropriate design response. The no-feasible-solution outcome is handled honestly.
5. Reference calculations pass tolerances registered before search. Use analytical agreement and mesh refinement appropriate to each problem; near-zero and singular quantities require absolute or regional measures. The previous 2% refinement target is a provisional starting point, not a universal validation rule.
6. A small sensitivity study varies the assumptions most likely to change the preferred design. Show ranking reversals and inconclusive results. Scenario ranges are not probability distributions or confidence intervals unless justified.
7. The UI distinguishes published evidence, numerical verification, assumed inputs, estimated states and measured validation. Scenario feasibility is worded as conditional on the named scenario.
8. Runs can be cancelled, reopened and exported. A fresh environment reproduces a selected run within registered tolerances; an independent person replay remains a later acceptance item until someone actually performs it.
9. Export includes the brief, candidate lineage, solver settings, raw objective values, relevant fields, assumptions, sources, exclusions and stopping reason. Credentials are excluded.
10. David receives a runnable demonstration, startup instructions and a concise review pack. His son's review is not required for this release.

## Assumptions and questions

Carry forward WP0 A01–A15. Give every assumption an ID, exact question for the later reviewer, provisional answer, value/range and units, evidence basis, affected models, sensitivity priority, owner, version and resolution criterion. Register numerical choices before running campaigns; changes invalidate affected cached results and create new evaluations.

| Topic | Default implementation decision | Question retained for later review |
|---|---|---|
| Geometry and duty | Planar coupon with explicit thermal/mechanical boundaries | Is this geometry and duty useful for a first real ceramic case? |
| Material records | Compatible evidenced records where available; clearly synthetic records otherwise | Which actual grades, states and intermediate compositions have suitable properties? |
| Property mapping | Existing documented formulation within its stated domain; otherwise unresolved | Which mixture or effective-property relationship applies? |
| Stress | Bounded elastic thermal mismatch with explicit stress-free state and restraint | Which omitted history, creep, damage or phase mechanisms could reverse the result? |
| Manufacturing | Scenario layer/feed resolution, editable and versioned | What resolution and transition response does the intended process actually achieve? |
| Shrinkage and porosity | No hidden correction; omitted or separate supported scenarios | What measured geometry/porosity fields and mappings are defensible? |
| Success criterion | Common brief, trade-offs and fixed constraints | Which measured outcome and improvement threshold matter for the chosen case? |

An assumption can authorise a software scenario while leaving a physical claim unresolved. No code path may turn an unknown measurement into zero porosity, perfect fidelity or demonstrated feasibility. Perfect bonding and other idealisations must be explicit inputs when used.

## Evidence and validation workstream

Keep the B4C–SiC reproduction and CODE alumina/zirconia dataset separate. The CODE case offers a retrospective deformation-versus-purge comparison, but its composition budgets differ and its measurements do not validate the earlier B4C–SiC revision. Neither case closes the linked achieved-state evidence gap.

The author request is prepared for David to send. Record its actual dispatch only when confirmed. Do not contact researchers or David's son automatically. Reserve a small evidence-review allocation, provisionally up to half an active day per week, so unbounded literature search does not displace D1 implementation. No recurring automation has been scheduled by this plan.

For V1, require documented commands/recipes, actual volume mapping, composition measurements with their basis, achieved geometry, porosity, process history, uncertainty and provenance joined by specimen/run identifiers. Confirm reuse terms before incorporation. Missing fields trigger a narrowed validation claim or a separate experiment proposal.

Freeze the baseline/revision comparison and success criteria before fitting or checking outcomes. Use an existing applicable model; retain complete runs/specimens for independent validation. Re-evaluate using measured achieved states and manufacturing constraints, propagate justified uncertainty, and retain failed specimens. Obtain scientific review after D1. New calibration/model development or laboratory work requires a separately scoped decision.

## Autonomous delivery and coordination

The lead owns contracts, integration, scientific claim boundaries and release evidence. Parallel agents can handle numerical adapters/reference checks, workflow/UI, and environment/data provenance once interfaces are agreed. Use isolated worktrees and bounded tasks; merge and execute each increment through the lead. Agent review does not count as independent experimental or expert validation.

Routine coding, testing, debugging, documentation, scenario configuration and release preparation proceed without repeated questions to David. Record reversible implementation choices in the decision log. Ask him only where a decision materially changes scope, cost, external communication or the intended demonstration. Do not invent a monetary budget. Start on available CPU resources; optional paid compute is not assumed.

David's expected involvement is reviewing concise demonstrations and making consequential product decisions. His son has no initial-build responsibilities. After D1, David can use the prepared one-page brief to ask for a suitable case and help prioritising assumptions. That invitation does not presume an ongoing unpaid review commitment.

## Risks and responses

| Trigger | Response |
|---|---|
| Earlier code cannot be recovered | Reconstruct the smallest reference assets from retained evidence; re-estimate before expanding |
| Mechanics reference fails | Diagnose or select another existing supported formulation; do not ship fabricated stress output |
| Real-material property pack remains incomplete | Continue labelled scenario demonstration; keep real-material claims unresolved |
| Manufacturing mapping changes total material use | Enforce the selected budget or disclose and constrain the change |
| Assumed process produces a preferred design | Test sensitivity and label its conditional status; no manufactured-performance claim |
| Experimental records remain unavailable | Complete D1; keep V1 blocked and propose a specific acquisition route |
| Scope starts to require new physics or heavy infrastructure | Defer the mechanism or obtain a concrete scope decision; preserve the complete bounded loop |

## First implementation backlog

Execute in this order: reconcile and recover repository assets; record the current baseline; establish locked core environment and assumption-aware contracts; restore thermal references; reproduce bounded mechanics; connect one design through the run store and UI; add resolution mapping and achieved-state re-evaluation; then add inverse proposal generation and automatic revision.

At the first complete-loop checkpoint, publish actual setup time, calculation runtimes, outstanding scientific assumptions and the revised delivery estimate. Keep source, fixtures and manifests in the Git-backed project and preserve review deliverables durably. Reconcile previously unpushed work before choosing any remote write operation.

## Source and decision record

Based on the current *Material System Product Definition and Delivery v1* (14 October), *WP0 Decision Pack and Assumptions* (19 October), subsequent manufacturing reproduction and ceramic evidence work, and David's approval on 20 October to proceed with assumptions and involve his son only after a working prototype.

Key changes: clean numerical core with selective reuse; assumption-based D1 release; experimental evidence removed from the D1 critical path; separate V1 scientific gate; late expert involvement; CPU-first autonomous delivery with coordinated parallel work; explicit recovery task; time estimates revisited using observed progress. This document updates the plan only. It does not claim that the prototype has been implemented or that the scientific gate has passed.
