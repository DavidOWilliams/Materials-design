# WP7 IR01/IR04 — coherent selected-candidate demonstration and recovery

This is the targeted response to the 28 October independent release review (PR #17). The reviewer BLOCKED functional Gate 1, while independently confirming Gate 2 challenge testing and bounded Gate 3 provenance. These instructions do not waive that finding. Use the corrective PR #18 exact implementation source and evidence, not a PR merge checkout.

## Scientific constraints

WP3 evaluates intended-state synthetic **homogeneous/layered/gradient** designs with A/B/C hypothetical catalogues. WP4's accepted constrained feedback policy is **two-constituent A/B gradient only**. Therefore a selected original WP3 *completed A/B gradient* can be transferred by **re-evaluating** it in a new two-constituent WP4 input context when actual A/B material records, thermal duty, objective and constraint contracts, solver, mesh and mass ceiling match. Other candidates fail explicitly. The source WP3 numerical eligibility (including false) is retained in the handoff manifest. No WP3 intended-only numerical Pareto result is inserted into WP4 estimated-state Pareto. Both source and recontextualised input hashes are preserved, and no measured achieved state is created.

## Complete user journey in one WP7 application

1. Install with `bash foundation/setup.sh`, then `.venv-foundation/bin/python -m pip install streamlit==1.40.2`; launch `PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py`.
2. On **Explore three architectures**, run the seeded WP3 mixed-space campaign at **4096 elements**, seed 17 and at least 4 proposals (recommended 9). Inspect the numerically qualified WP3 Pareto, incomplete/unknowns, geometry/constituent choices and all original candidate identities.
3. Select a completed **gradient using scenario_A and scenario_B**. The supported structured campaign initially proposes homogeneous, homogeneous, layered, gradient; a later gradient with scenario_A/C is *not* supported by this handoff. Click **Select WP3 candidate for WP4 handoff**. Incompatible selected designs are rejected with an explanation; no silent scientific substitution. The source numerical qualification flag remains explicit.
4. Open **Inspect feedback and trade-offs**. The selected source ledger and candidate appear. Choose a *new* WP4 dossier filename, layer/feed resolution and candidate budget. Click **Evaluate selected design through WP4 and save**. The accepted WP4 transformer generates an **estimated** achieved state, evaluates the new two-constituent context and performs density-guided revision **only if the synthetic mass constraint supplies a supported feedback trigger**. Inspect original selection hash, WP4 intended baseline, estimated candidate lineage, exclusions and WP4-only Pareto. Three outcome classes are valid: feasible conditional scenario, supported binding-feedback revisions, or a correct natural stop/no applicable revision. Never claim a revision occurred unless records show it.
5. To demonstrate cancellation and durable checkpointing, choose a **binding 1 kg/m² synthetic ceiling** in a *new* WP3 campaign and select the compatible gradient, or use an appropriately binding case. In the same WP7 tab, set a new journal location and **Cooperatively cancel after completed candidates** = 1; click **Start checkpointed selected-design campaign and cancel**. This is **between candidates**, not pre-emptive mid-solver cancellation.
6. Click **Inspect cancellation checkpoints**. Observe the durable journal, attempted evaluation events, checkpoint count and original source lineage. Click **Recover selected-design journal into immutable dossier** with a *new* destination. Recovery verifies journal and source, continues remaining work (or correctly reports natural terminal conditions), then preserves a new handoff manifest. Inspect and replay it in the same UI.
7. Close/restart Streamlit. Reopen WP4 dossier from file path, recompute via **Restore and replay**. A separate Python process can verify WP4 and source handoff with:

```sh
PYTHONPATH=foundation .venv-foundation/bin/python -c 'import sys,json;from material_core.wp7_handoff import verify_handoff;from material_core.wp5_service import replay;print(json.dumps({"handoff":verify_handoff(sys.argv[1]),"numerical":replay(sys.argv[1])}))' d1-workspace/selected-wp4.json
```

The handoff companion `<dossier>.handoff.json` stores the original WP3 ledger path and SHA256, run ID, source evaluation/input/design hash, original numerical eligibility and newly recontextualised baseline identity. Preserve the **source ledger and run-store** alongside a handoff dossier for independent replay. Deleting/moving source material without explicitly preserving it invalidates independent source-lineage verification; no location-independent signed bundle is claimed for this handoff.

## Independent Gate 1 must be reverified

Execute `foundation/tests/test_wp7_ir01_ir04.py` and `foundation/tests/wp7_ir_browser_acceptance.py` through GitHub Actions at an exact corrective source SHA. Re-run all regressions, check clean installation, source SHA, archived ZIP SHA256SUMS, selected-design dossier and recovered dossier, and repeat a real browser journey. All earlier WP7 and reviewer evidence remains immutable. PR #18 is draft; no D1 approval, merge or tag is authorised. A genuinely independent reviewer must reassess IR01 and IR04.

**IR05 historical WP6 final independent report:** the governance register documents a missing original record; no reviewer statement will be fabricated. **IR06** header now differentiates WP3 A/B/C and WP4 A/B.
