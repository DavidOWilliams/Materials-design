# Candidate Source Diagnostic Insights

## Purpose
This harness checks whether Build 3.1 is adding explicitly labelled curated engineering analogue candidates, and whether those candidates improve source diversity and recipe support without relaxing Materials Project request-aware acceptance.

## Run summary
- Cases run: **6**
- Engineering analogue candidates added across all cases: **26**
- Ranked candidate source mix: `{"materials_project": 79, "engineering_analogue": 22}`
- Ranked recipe mode mix: `{"family_envelope": 79, "named_analogue": 22}`

## What to inspect
1. `candidate_source_summary.csv`: check that prompt-favoured families receive engineering analogues when MP candidates are sparse or simplified.
2. `candidate_source_ranked_candidates.csv`: check whether engineering analogue candidates produce `named_analogue` or `analogue_guided` recipe modes.
3. `candidate_source_supplementation.csv`: inspect why each family was supplemented and which named analogues were selected.

## Build 3.1 success signals
- Wear / hot-corrosion prompts should include at least one Co-based engineering analogue if MP Co candidates do not survive.
- Hot-section creep prompts should include stronger Ni engineering analogues, not only simplified Al-Cr-Ni / Al-Co-Ni MP ternaries.
- Lightweight prompts should keep Ti candidates visible and may add Ti engineering analogues where useful.
- Candidate-source labels should make clear which candidates are Materials Project records and which are curated engineering analogues.