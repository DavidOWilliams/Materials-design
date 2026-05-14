# Phase 5 Scope and Guardrails

## Purpose

This document defines the implementation boundaries for Phase 5:

```text
Phase 5 — Material-System Decision Cockpit and Deterministic Optimisation Foundation
```

Phase 5 should convert the Build 4 review-pack workflow into the foundation of a material-system decision-support cockpit while preserving the protected Build 3.1 metallic baseline.

The tool is decision support. It does not provide formal engineering approval, qualification approval, certification approval, or permission to use a material system in service.

## Permanent Principles

| Principle | Meaning |
| --- | --- |
| Material-system first | The decision unit is a material system, not just a bulk material. |
| Evidence-aware | Mature references, emerging options, exploratory concepts, and generated research suggestions must remain distinct. |
| Deterministic before generative | Phase 5 optimisation must be deterministic, bounded, repeatable, and auditable. |
| No hidden single score | Trade-offs must be visible. Pareto/frontier logic is preferred over opaque ranking. |
| Build 3.1 protection | The metallic baseline remains protected and should not be refactored casually. |
| Build 4 continuity | Build 4 review-pack and application-review workflow remains the clean foundation. |
| Hot-section first | Broader profile expansion waits until the hot-section material-system flow works. |
| Review, not approval | Outputs support engineering review and validation planning; they do not grant certification or qualification. |

## Phase 5 In Scope

Phase 5 should include:

| Area | In-scope work |
| --- | --- |
| Contracts | Material-system and `GradientArchitecture` contracts. |
| Gradient templates | Deterministic gradient template registry. |
| Diagnostics | Coating-vs-gradient activation and rejection diagnostics. |
| Optimisation | Deterministic optimisation controller MVP. |
| Refinement | Controlled refinement operators. |
| Traceability | Before/after optimisation trace with factor deltas. |
| Trade-offs | Trade-off vectors for cost, sustainability, uncertainty, evidence maturity, inspection burden, repair burden, and certification or qualification risk. |
| Frontier analysis | Pareto/frontier analysis without hidden single-score selection. |
| Recommendation tiers | Evidence-aware recommendation tiers. |
| Validation planning | Extended validation-plan generation. |
| View models | Decision-cockpit view models. |
| Export path | Separate viewer/export path that does not patch the legacy app by default. |
| Feedback | Feedback and validation outcome records. |
| Research adapters | Disabled specialist-model adapter contracts, with no live calls. |

The first implementation target should remain the hot-section material-system flow for:

- Ni superalloy + TBC
- SiC/SiC CMC + EBC
- monolithic ceramic reference
- refractory + oxidation-protection concept
- spatially graded AM surface alternative

## Phase 5 Out of Scope

Phase 5 should not include:

- broad Build 3.1 refactoring
- casual changes to the protected metallic baseline
- patching the legacy `app.py` unless explicitly decided later
- arbitrary generated gradients
- live AtomGPT/MatterGen-style calls
- production use of generated candidates
- formal qualification claims
- formal certification claims
- broad profile expansion before the hot-section material-system flow works
- hidden single-score optimisation
- generated candidates displacing mature evidence options

## Allowed Implementation Pattern

Phase 5 implementation should follow this pattern:

1. Extend structured data contracts before extending presentation.
2. Keep deterministic material-system comparison separate from any future research-generation path.
3. Add gradient templates as named, bounded, reviewable options.
4. Add optimisation through explicit refinement operators.
5. Record every optimisation move in a before/after trace.
6. Expose trade-off vectors and Pareto/frontier outputs instead of collapsing the decision into one score.
7. Add recommendation tiers only after evidence maturity, uncertainty, and validation needs are represented.
8. Build a separate cockpit viewer/export path before considering changes to the legacy app.
9. Keep specialist-model adapters disabled until a feature-flagged research mode is explicitly introduced.

Implementation should be incremental and reviewable. Each step should preserve the ability to run the existing Build 4 review-pack workflow.

## Testing Expectations

Testing should confirm:

- material-system contracts serialize and validate deterministically
- gradient templates are selected from a registry, not generated freely
- coating-vs-gradient diagnostics explain activation and rejection paths
- optimisation operators produce repeatable before/after traces
- factor deltas are auditable and stable
- trade-off vectors expose changes without hiding penalties
- Pareto/frontier analysis is deterministic
- recommendation tiers preserve evidence maturity boundaries
- generated or research-only suggestions cannot displace mature reference options
- validation plans remain decision-support artifacts, not approval artifacts
- Build 3.1 behavior is not affected unless an explicitly approved later phase changes it

Tests should be focused around the hot-section material-system flow before new profiles are added.

## Git Hygiene Expectations

Before committing Phase 5 work, confirm that only intentional files changed.

Use:

```bash
git status --short --untracked-files=all
```

Do not commit generated review-pack outputs unless explicitly requested.

Do not commit:

- files under `outputs/`
- generated review packs
- `.docx` files
- `__pycache__` directories
- `.pyc` files
- `.pytest_cache` files or directories
- unrelated edits to `app.py`, `src/`, `tools/`, or `tests/`

## No-Go Rules

The following are not allowed in Phase 5 unless a later explicit decision changes the scope:

| No-go | Reason |
| --- | --- |
| Refactor Build 3.1 broadly | It is the protected metallic baseline. |
| Patch `app.py` opportunistically | The viewer/export path should be separate first. |
| Generate arbitrary gradients | Phase 5 requires deterministic templates and auditable operators. |
| Make live specialist-model calls | Research adapters must remain disabled. |
| Present generated candidates as production options | Generated suggestions are research-only until validated through a separate process. |
| Claim certification or qualification approval | The tool supports review and planning only. |
| Hide the decision in one score | Material-system selection requires visible trade-offs. |
| Expand profiles broadly before hot-section flow works | Profile semantics must be explicit and tested. |

## Deterministic Optimisation, Generated Candidates, and Research Mode

Phase 5 must keep three concepts separate:

| Concept | Allowed in Phase 5? | Description |
| --- | --- | --- |
| Deterministic optimisation | Yes | Bounded, repeatable refinement of known material-system architectures using explicit operators, traces, factor deltas, and trade-off vectors. |
| Generated candidates | Not for production use | Any generated option must be separated from mature and emerging evidence options and treated as exploratory or research-only. |
| Specialist-model research mode | Contracts only | Adapter contracts may be defined, but live calls remain disabled. A later feature-flagged mode may gate this capability. |

Deterministic optimisation is central to Phase 5. Generated candidates and specialist-model research support are not substitutes for deterministic optimisation, mature evidence, validation planning, or engineering review.

## Decision-Support Boundary

All Phase 5 outputs should be worded and structured as decision-support artifacts.

They may identify application fit, limiting factors, optimisation moves, trade-offs, evidence maturity, uncertainty, cost, sustainability, inspection burden, repair burden, certification or qualification risk, and validation needs.

They must not state or imply that a material system is certified, qualified, approved for service, or ready for production use.
