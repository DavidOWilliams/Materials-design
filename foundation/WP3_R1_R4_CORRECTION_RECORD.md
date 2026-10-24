# WP3 independent re-review corrections R1–R4 — implementation decision record

**Reviewed source:** `d62023d7205d48beba11269d4c358a7380ab9ca4`; **branch:** `wp3-inverse-search-2026-10-24`; **draft PR:** #3. The Vision, Product Definition, current WP3 brief and corrected WP2 `7009189d9be4dfd5940999c88cbb5c3c70c8ce56` remain authoritative. No new numerical physics or validated real materials have been introduced.

## R1 — unprotected old public campaign

**Reproduction:** run schema-1 `material_core.wp3_campaign.run_campaign` with 1 proposal; rewrite `unique_evaluations=999` and `qualified_comparison.pareto_ids=["invented"]`; old `reopen_campaign` returned both altered fields. Historical checked-out source reproduction is `foundation/reproduce_reviewed_wp3_r1_r4.py` executed in CI against the exact reviewed commit.

**Correction choice: explicitly retire rather than silently route.** `wp3_campaign.run_campaign`, `reopen_campaign`, and the normal `python -m material_core.wp3_campaign` CLI now raise a clear error. Retain the atomic `_write_ledger` utility used by the supported schema-2 service. `read_legacy_unvalidated` and `--legacy-read-unvalidated` preserve historical schema-1 JSON contents but label them `UNVALIDATED_LEGACY_V1`, `review_eligible=false`. Old immutable stores are not overwritten or misrepresented as migrated/verified. New campaigns use `material_core.wp3_search`; archival viewing is not a qualified replay. Remove old v1 execution from CI and replace with explicit retirement tests.

## R2 — completed record corruption masked by another pending run

**Reproduction:** complete proposal 0, interrupt genuine WP2 evaluation in proposal 1, then change proposal 0's objective/constraints/qualification/manufacturing/evidence fields. The old `open_search(recovery=True)` bypassed all derived-field checks when *any* created item existed, then ordinary resume replaced the corrupted summary.

**Correction:** no blanket recovery exemption. Always validate every previously complete proposal against its immutable run, and compare the full qualified decision even when campaign stop state is `running`. Pending items may legitimately have a committed complete run before their ledger transitions; the intact journal's `created` state remains counted as uncertain until explicit reconciliation. A mismatch in completed fields causes a useful error and no file rewrite. After valid interruption, resume separately reconciles the pending item, preserving the result if committed or marking it failed if not. The persistence, subprocess interruption and post-commit fault-injection tests remain in force.

## R3 — unsupported campaign termination and inconsistent transitions

**Reproduction:** after full campaign, alter `stop_reason` to `manufacturing_validated`; the reviewed `open_search` accepted it.

**Correction:** permitted values are `running`, `cancelled`, `wall_time_budget_exhausted`, and `evaluation_budget_exhausted`. Terminated campaigns must carry a corresponding `termination_event={"reason":..., "proposal_slots":...}`. A terminated campaign cannot have pending proposals; exhaustion must consume the exact configured proposal budget; early termination cannot claim a full-budget outcome. A running campaign cannot simultaneously assert a terminal event. Resume records prior stop reason in `stop_history`, clears the terminal event and returns to `running` before executing another proposal. A crashed final-journal update may leave a running campaign with all slots committed; the next explicit resume reconciles it.

**Durability limit:** the journal is the durable declaration of an externally requested cancellation or elapsed wall-time cutoff. It does not cryptographically attest to an external button press or elapsed monotonic time. Coordinated rewriting of all related data remains beyond the integrity guarantees. Termination does not claim manufacturing status.

## R4 — fixture-specific orchestration

**Reproduction:** the reviewed orchestrator owned the A/B initial design, hardcoded the three objective names, directly called `propose`, and unpacked homogeneous, layered and three-knot gradient geometry during validation. A small substitute generator still depended on the same fixture constructor.

**Correction:** `wp3_adapters.py` defines two explicitly versioned **registered scenario adapters** with `start()`, `proposal(index)`, `build(spec,parent_hashes)`, `validate(spec,typed_inputs)`, and `baseline()`. The search service delegates scenario construction and typed design validation and obtains objective IDs, constraint IDs, brief identity and material-pack hash from the scenario baseline. An unavailable provider identity fails at resolution. Persisted campaigns are reopened using the same registered provider identity, with context checks against stored typed WP2 inputs. Numerical recomputation rejects any evaluator other than the registered corrected WP2 adapter rather than secretly substituting WP2.

- `wp3-synthetic-catalogue-provider-v1`: retains historical synthetic A/B/C three-architecture scenario; keeps 0.35 mass-infeasible and 0.65 conditionally qualified checks.
- `wp3-alternate-duty-layered-provider-v1`: **materially different** hypothetical WP2-supported software scenario: 380 K/320 K duty instead of 400 K/300 K; two constituent records; a genuine three-layer sandwich with variable middle-layer thickness. Uses existing WP2 conduction and mechanics, not any new physics, proprietary data or ceramics claim. The same campaign runner handles cancellation, resume, comparison, persisted immutable runs, reopening, fresh-process CLI replay and numerical recomputation.
- A one-off callable wrapper with unregistered evaluator identity is usable only when explicitly supplied for fault testing; independent recomputation refuses it. New persistent providers must be registered with versioned identities for durable reopening. No speculative plugin subsystem was added.

**Exploration policy:** `explore` is **structured seeded sampling**, not evaluation-driven adaptive optimisation. Neither algorithm uses past WP2 results to update proposal distributions. The paired random sampling comparison is descriptive; the observed three-seed study does not establish superiority.

## Evidence / scientific boundaries

Source-driven verification uses `foundation/reproduce_reviewed_wp3_r1_r4.py` against exact reviewed commit; new regressions `foundation/tests/test_wp3_review_r1_r4.py`, `test_wp3_campaign.py`, `test_wp3_search.py`, and `test_wp3_inspection_corrections.py`; locked foundation/recovery and legacy jobs; corrected WP2 verifier; full campaign store, separate-process reopen and recomputation, and paired comparison artifacts. Check actual job logs and SHA distinctions, then record final test counts and artifacts in the acceptance ledger.

Manufacturing feasibility remains unknown for intended-only designs. Numerical qualification, hard constraint satisfaction and evidence maturity remain independent. The platform's Vision is not narrowed; D1, measured V1, WP4/5 and physical ceramic manufacturability remain outside the bounded WP3 demonstration. Gate 3 independent scientific and architecture approval is **PENDING re-review**.
