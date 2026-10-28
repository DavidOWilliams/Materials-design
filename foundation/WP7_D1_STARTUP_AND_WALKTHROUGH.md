# WP7 D1 — installation, demonstration, export and replay

This is a **bounded synthetic** planar coupon, not a measured ceramic design recommendation. Begin with immutable WP6 implementation `1f89c2d1bf64b669ca98b81f4305d20d08104e5c` and the WP7 implementation PR/commit specified in the verification manifest. Use Python **3.12**, clean Linux environment and a source checkout of that exact revision.

From repository root (new checkout):

```sh
bash foundation/setup.sh
.venv-foundation/bin/python -m pip install streamlit==1.40.2
PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py
```

Streamlit pin is the historically tested WP5 UI dependency; separately record `pip freeze` and `pip check` for the WP7 clean installation. The foundation lock is hash-pinned but the Streamlit add-on is not part of it; full lock/independent reproducibility of its transitive dependencies remains open.

1. Open the local Streamlit URL. Observe the banner separating synthetic estimated-state calculations from measured validation.
2. Under **Run demonstration**, select *Representative mass-constrained coupon*; inspect fixture constraints, material IDs and objectives. Optionally select *Infeasible mass limit* (1 kg/m²) or *Resolution sensitivity*.
3. Choose a new plain filename, default 128 elements, mass ceiling 31 kg/m², assumed layer resolution 0.005 m, feed increment 0.25, budget 4, revision enabled. Optional brief must be previously immutable, valid, and within WP4 supported edits.
4. Click **Generate, evaluate and save dossier**. An immutable JSON dossier is written; never overwrite it. Inspect whether a revision was actually proposed. *Do not infer multiple designs when the first candidate is feasible*.
5. In **Inspect candidates and trade-offs**, click **Inspect dossier and Pareto**. Inspect eligible/ineligible rows, actual objective units/directions, exclusion reasons and the nondominated IDs. Select each persisted candidate for intended design, estimated inputs, numerical outcome, feedback and hashes. Pareto comparison is intra-campaign only and cannot certify general optimality.
6. In **Restore and replay**, click **Verify integrity and recompute**; download verified JSON or copy/import into a new immutable location. Stop and restart Streamlit; reopen the same dossier and replay.
7. For independent process verification (after closing Streamlit), use:

```sh
PYTHONPATH=foundation .venv-foundation/bin/python -c "import sys,json; from material_core.wp5_service import replay; print(json.dumps(replay(sys.argv[1])))" d1-workspace/d1-example.json
```

Expected success schema: `{"recomputed": <actual candidate count>, "status": "passed"}`; never assert a fixed count. Tampered content must fail. To keep original evidence intact, use new paths for each campaign and import.

**Evidence categories:** assumed process capability, computed intended and estimated achieved-state fields, qualified numerical checks only within their mesh/domain conditions, unknown physical accuracy, and **no measured achieved-state record**. Excluded: mixing lag, shrinkage, porosity, sintering, CFD, manufacturing residual stress, production engineering readiness. Tensile thermal mismatch is not full residual stress.

**Acceptance warning:** This guided WP7 gradient workflow alone does not satisfy the implementation plan's complete multi-architecture D1 release checklist. No release acceptance, merge or tag is implied.
