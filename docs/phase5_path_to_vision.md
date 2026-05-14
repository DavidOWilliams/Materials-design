# Phase 5 — Material-System Decision Cockpit and Deterministic Optimisation Foundation

## Purpose

This document defines the path from the current Build 4 review-pack workflow toward a material-system decision-support cockpit.

Phase 5 moves the project beyond a metallic alloy selector and toward comparison of complete material systems. The decision unit is no longer only a bulk material. It may include substrate or bulk material, coating or surface system, CMC/EBC architecture, spatially graded AM architecture, hybrid architecture, process route, inspection strategy, repair strategy, evidence maturity, uncertainty, cost, sustainability, and certification or qualification risk.

Phase 5 is documentation-guided implementation work, not a certification workflow. Its purpose is to produce transparent, auditable decision packages that show why a material-system architecture is attractive, limited, immature, expensive, hard to inspect, hard to repair, or validation-intensive.

## Current-State Summary

| Area | Current position |
| --- | --- |
| Build 3.1 | Protected metallic baseline. It remains valuable and should not be casually refactored. |
| Build 4 | Current clean CLI/review-pack and application-review workflow. |
| Current profile | `hot_section_thermal_cycling_oxidation`. |
| Current strengths | Application fit, limiting-factor analysis, controlled shortlist buckets, validation planning, and review-pack export. |
| Current limits | No deterministic optimisation foundation, no Pareto/frontier analysis, no trade-off vector model, no material-system cockpit view model, no feedback loop, and no specialist-model research mode. |

Build 4 is useful, but it is not the final product. It is the clean review and evidence-packaging foundation that Phase 5 should extend.

## Target Vision Summary

The long-term product direction is a Material-System Decision Cockpit that supports:

- application-aware material-system comparison
- deterministic optimisation
- coating-vs-gradient trade-off reasoning
- evidence-aware recommendation tiers
- Pareto/frontier analysis
- validation planning
- feedback capture
- gated specialist-model research mode
- clear separation between mature references, emerging options, and generated research suggestions

The cockpit should help reviewers compare mature, emerging, and exploratory architectures without hiding trade-offs behind a single score.

## Corrected Phase 5 Definition

Phase 5 is:

```text
Phase 5 — Material-System Decision Cockpit and Deterministic Optimisation Foundation
```

The objective is to convert the current Build 4 review-pack workflow into the foundation of a material-system decision-support cockpit. The first anchor remains the hot-section profile, especially comparison across:

- Ni superalloy + TBC
- SiC/SiC CMC + EBC
- monolithic ceramic reference
- refractory + oxidation-protection concept
- spatially graded AM surface alternative

Phase 5 must deliver the first deterministic optimisation foundation. It is not merely diagnostics, UI, or documentation.

## Why Optimisation Remains Central

Optimisation in Phase 5 should be deterministic, auditable, and bounded. It should propose controlled refinement moves and show before/after factor deltas rather than inventing arbitrary architectures.

The optimisation foundation should expose:

- the starting material-system architecture
- the active constraints and limiting factors
- the deterministic refinement operator applied
- the reason the operator was accepted or rejected
- before/after changes in application fit, uncertainty, cost, sustainability, inspection burden, repair burden, and certification or qualification risk
- trade-offs introduced by the move
- validation needs created or reduced by the move

This keeps optimisation central while preserving engineering review discipline.

## Hot-Section Anchor Scenario

The first Phase 5 flow should remain anchored to `hot_section_thermal_cycling_oxidation`.

For that profile, the cockpit should compare mature, emerging, and exploratory material-system architectures across hot-section concerns such as thermal cycling, oxidation, coating dependence, gradient feasibility, inspection burden, repair burden, validation maturity, cost, sustainability, and certification or qualification risk.

The output should not declare a final winner. It should produce a decision package that helps reviewers understand:

- application fit
- limiting factors
- deterministic optimisation moves
- before/after factor deltas
- trade-offs
- evidence maturity
- uncertainty
- cost
- sustainability
- inspection burden
- repair burden
- certification and qualification risk
- validation needs

## Roadmap

| Stage | Name | Purpose | Expected outcome |
| --- | --- | --- | --- |
| Stage 0 | Current checkpoint | Preserve the Build 3.1 baseline and Build 4 review-pack workflow as the starting point. | Clean documentation of current boundaries and Phase 5 direction. |
| Stage 1 | Material-system foundation | Introduce material-system and `GradientArchitecture` contracts. | Candidate data can represent substrate, coating, gradient, process, inspection, repair, evidence, uncertainty, cost, sustainability, and risk. |
| Stage 2 | Gradient template and coating-vs-gradient foundation | Add deterministic gradient template registry and coating-vs-gradient activation or rejection diagnostics. | The system can explain when a gradient path is relevant, when a coating path remains preferred, and why an option is rejected. |
| Stage 3 | Deterministic optimisation MVP | Add bounded optimisation controller, refinement operators, and before/after optimisation trace. | The system can apply controlled refinement moves and expose auditable factor deltas. |
| Stage 4 | Trade-off vectors and Pareto MVP | Represent multi-factor trade-offs and add first frontier analysis. | Reviewers can see non-dominated options and trade-off movement without a hidden single score. |
| Stage 5 | Recommendation tiers | Convert review results into evidence-aware tiers. | Mature references, validation-needed options, exploratory concepts, and research-only suggestions remain clearly separated. |
| Stage 6 | Decision cockpit viewer/export path | Add view models and a separate viewer/export path. | The cockpit can present decision packages without disturbing protected Build 3.1 runtime paths. |
| Stage 7 | Feedback and validation outcome loop | Add feedback and validation outcome records. | Review decisions and validation results can be captured for later evidence updates. |
| Stage 8 | Disabled research-adapter contracts | Define specialist-model adapter contracts with no live calls. | Interfaces exist for future AtomGPT/MatterGen-style research support, but remain disabled. |
| Stage 9 | Feature-flagged research mode | Add gated research mode around specialist-model adapters. | Generated suggestions are explicitly marked as research-only and cannot displace mature evidence options. |
| Stage 10 | Integrated multi-profile demonstrator | Extend beyond the hot-section flow only after semantics are proven. | A broader demonstrator can compare material systems across multiple well-defined application profiles. |

## Success Criteria

Phase 5 is successful when the hot-section flow can produce a transparent material-system decision package that includes:

- material-system records rather than bulk-material-only records
- deterministic gradient templates rather than arbitrary generated gradients
- coating-vs-gradient activation and rejection diagnostics
- deterministic optimisation controller MVP
- refinement operators with before/after traces
- trade-off vectors
- Pareto/frontier analysis
- evidence-aware recommendation tiers
- extended validation-plan generation
- decision-cockpit view models
- separate viewer/export path
- feedback and validation outcome records
- disabled specialist-model adapter contracts with no live calls

Phase 5 remains bounded if Build 3.1 stays protected, Build 4 remains the clean review-pack foundation, generated candidates remain clearly separated from mature evidence options, and no output claims certification or qualification approval.
