# P1 independent Gate 3 review assignment — not yet performed

**Separate reviewer required.** Do not use this implementation chat as the independent reviewer and do not self-close Gate 3. The review must consider adverse findings as seriously as positive ones.

## Exact artifacts and immutable boundaries

- Working draft PR: https://github.com/DavidOWilliams/Materials-design/pull/9 (not merged).
- Original accepted WP5 tested source: `4078a83dc11e14703ff6cc03f5b62f4e48879d14`.
- P1 confirmatory tested source: `6eb62daec638185f5c5dc170182e9e0454b6e061`.
- Successful confirmatory Actions: https://github.com/DavidOWilliams/Materials-design/actions/runs/40483551395, artifact 12724002391.
- Frozen scientific plan: `foundation/p1/CONFIRMATORY_PROTOCOL_FROZEN.md` and `CONFIRMATORY_CONFIG_FROZEN.json`, committed *before* confirmatory outcomes.
- Permanent evidence snapshot: `foundation/p1/evidence/confirmed-source-6eb62da/`, contains raw arm records, independent in-model scoring artifacts, trial analysis, CSV/graph, dependency/source snapshot, two SHA256 manifests and CI raw logs.
- Any documentation/evidence commits after the exact P1 tested SHA do not constitute newer tested source.
- Independent WP6 review remains formally open; P1 does not modify WP6 acceptance.

## Reviewer reproduction

1. Checkout the exact tested source SHA in a clean isolated worktree; do not substitute the documentation branch HEAD. Create a Python 3.12 environment with `bash foundation/setup.sh`, and install the documented Streamlit test dependency (1.40.2) in the isolated environment.
2. Run `PYTHONPATH=foundation .venv-foundation/bin/python -m pytest foundation/tests/test_p1_comparator.py foundation/tests/test_p1_analysis.py -vv` and the full `foundation/tests recovered_wp0` regression. Inspect raw Actions log for actual command exit codes and exact SHA.
3. Verify both original and expanded SHA256 manifests. Confirm `environment_and_source.json` gives exact `6eb62da...` and confirmatory grid contains **80 unique method/feed/seed pairs**, **160 arm records**, and fixed four slots per arm. No exclusions are permitted.
4. Independently rebuild at least one held-out score and a positive-effect seed (sampling/feed=0.25 seed=2001; sampling/feed=0.50 seed=2001); also inspect zero-effect cases. Call `score_saved(path)` and `score_saved(path, heldout_feed=opposite_feed)`. Compare objective and achieved-state hashes to raw evidence. Independently calculate 3D hypervolume via another algorithm (e.g. inclusion-exclusion) and bootstrap paired differences from the raw trials, without reading calculated confidence limits.
5. Inspect paired information parity and candidate histories. The feedback arm may use previous achieved mass violations only; blind must never use any achieved output for subsequent proposal selection. Confirm the WP4 density-guided revision rule is unchanged, the WP3 catalogue remains synthetic, and no new physics has been introduced.
6. Audit proposal/method/seed/transform/evaluation counts and per-row CPU totals for **both** arms, including measured feedback overhead, failures and absence of caches. Check prefix CPU time at 80ms, handling of observations that exceed threshold and resource variability. **Potential concern:** a four-slot budget is not a matched CPU-time budget; conclusions must remain separate.
7. Test adversarial no-feasible candidates, numerical failures, invalid objectives, tampered config and objective hashes, incompatible seeds/feeds, repeated/invalid proposals, missing files, interrupted execution and restart after partial completion. If trial-level durability does not satisfy the originally requested per-candidate recovery contract, keep Gate 1 OPEN and require a bounded correction.
8. Scrutinize fixed reference choice (120000 W/m²,45 kg/m²,1e9 Pa), claimed eligibility at mesh 32, strong dependence on synthetic WP2 catalogue and false physical generalisation. The exact identity-process negative control for heterogeneous WP3 candidates is unsupported; do not invent a physics-equivalent control.
9. Confirm no outcome switching or adaptive trial exclusion. Heterogeneity is critical: **only six of eighty** paired trials have nonzero positive equal-work HV gains, none negative, and both methods are feasible at least once in all 80 trials. The trial-level feasibility endpoint is therefore saturated and cannot establish effects on feasibility under challenging constraints.
10. Examine held-out 0.25 ↔ 0.50 feed rescoring as assumption sensitivity **within the same synthetic WP4 model family**, not a physically independent evaluator. Assess whether the concentration of all primary gains in sampling is scientifically generalisable.
11. Determine whether effect size meets the preregistered engineering relevance threshold and whether trial count, paired CI methodology and null interpretation are satisfactory. Mean +0.014070 HV and 95% CI +0.003704 to +0.025926 at equal numerical work, versus -0.001729 and CI -0.005187 to 0 at 80ms CPU, and zero feasible-rate difference. All three must be evaluated together.

## Independent disposition to provide

State **Gate 1** (infrastructure and restart), **Gate 2** (adversarial scientific challenges) and **Gate 3** (independent acceptance), each PASS, OPEN, or FAIL with evidence. The reviewer must list any unresolved findings, exact tested SHA and source checkout, numerical quantities independently recalculated, retention status, and restrictions on claims. Do not infer superiority in manufactured ceramics from synthetic in-model improvement. WP6 formal acceptance remains entirely separate.

The implementer has NOT independently approved these findings.
