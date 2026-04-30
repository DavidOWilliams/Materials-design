# Family Recall Diagnostic Insights

## Purpose
This harness checks whether prompt-sensitive family priors are reaching candidate-generation retrieval, and whether each requested chemistry is assigned the correct requested family before request-aware acceptance.

## Preflight findings
- Cases checked: **6**
- Requested-chemistry family-inference mismatches: **0**
- Cases where the top prompt family was absent from the query plan: **0**

No chemistry-family inference mismatches were found in the preflight query plan.

Every case had at least one query for the top prompt family.

## Live-generation findings
- Live cases run: **6**
- Live errors: **0**

- **hot_section_creep_am**: status=success, top_family=Ni-based superalloy, final_candidate_count=9, survivor_mix={"Ni-based superalloy": 9}
- **lightweight_strength_to_weight**: status=success, top_family=Ti alloy, final_candidate_count=18, survivor_mix={"Ni-based superalloy": 9, "Ti alloy": 9}
- **wear_hot_corrosion**: status=success, top_family=Co-based alloy, final_candidate_count=9, survivor_mix={"Ni-based superalloy": 9}
  - Alignment warning: Prompt scope favoured Co-based alloy, but no candidates from that family survived baseline retrieval/acceptance. The displayed results may therefore be dominated by fallback families rather than the intended design direction.
- **am_complex_geometry_creep**: status=success, top_family=Ni-based superalloy, final_candidate_count=9, survivor_mix={"Ni-based superalloy": 9}
- **certification_mature_conventional**: status=success, top_family=Ti alloy, final_candidate_count=18, survivor_mix={"Ni-based superalloy": 9, "Ti alloy": 9}
- **extreme_temperature_refractory**: status=success, top_family=Ni-based superalloy, final_candidate_count=16, survivor_mix={"Ni-based superalloy": 9, "Refractory alloy concept": 7}

## Recommended interpretation
- If preflight mismatches are zero but live non-Ni families still do not survive, the problem is likely Materials Project coverage, request-aware acceptance calibration, or family classification of returned records.
- If preflight mismatches exist, fix `_infer_requested_family` and same-family fallback logic before changing scoring or recipes.
- If the top family is absent from the query plan, fix `_choose_chemsys` ordering and query budgeting before investigating recipe fallback.