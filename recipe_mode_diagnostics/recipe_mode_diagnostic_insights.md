# Recipe Mode Diagnostic Insights

## What this harness checks

This harness checks whether prompt-sensitive interpretation is reaching the recipe layer, and why candidates — especially Ni-based candidates — fall back to `family_envelope` recipes.

## Knowledge-table health

- Knowledge table loaded: `/workspaces/Materials-design/data/starter_alloy_knowledge_table_seed_rows.csv`
- Knowledge-table rows: **21**
- Rows by family: Ni-based=9, Ti-based=6, Refractory=4, Co-based=2

## Live pipeline result summary

- Case statuses: `{"success": 6}`
- Cases with Ni candidates: **6 / 6**
- Average Ni family-envelope fallback rate in cases with Ni candidates: **100.0%**

## Most likely causes

- 54 Ni fallback candidate(s) had knowledge-table rows but the best analogue score was below 0.72 median=0.57. This is the most likely cause when the table is present.
- Every candidate is family-envelope. That usually indicates either missing/failed knowledge-table loading, overly strict analogue thresholds, or seed analogues that are too sparse for the retrieved chemistries.

## What to inspect first

1. Open `recipe_candidate_diagnostics.csv` and filter `material_family` contains `Ni-based`.
2. Sort by `analogue_weighted_score` descending.
3. Check whether the best Ni analogue scores are just below `0.72` or much lower.
4. Check `analogue_similarity_score` and `analogue_route_compatibility_score` to see whether chemistry or route support is the limiting component.
5. Check `knowledge_table_health.csv` to confirm Ni-family seed rows exist and template keys are valid.

## Likely next fixes, depending on the result

- If the knowledge table is missing: copy `data/starter_alloy_knowledge_table_seed_rows.csv` into the deployed project.
- If Ni seed rows are missing or sparse: expand the Ni seed table with more named Ni analogue rows covering AM, wrought, corrosion, and creep-oriented routes.
- If many best scores sit just below 0.72: consider adding an intermediate `weak_analogue_guided` or `family_plus_nearest_analogue` mode rather than overclaiming named analogue support.
- If AM route compatibility is the limiter: add AM-supported Ni seed analogues or make the route component less punitive for analogue-guided, not named-analogue, matching.
- If prompt family priors change but the final pool remains Ni-only: that is a candidate-generation/retrieval-scope issue, not a recipe-layer issue. Treat it as a targeted recall investigation, not a broad baseline redesign.
