# WP1 source review

The supplied attachments were read directly from the uploaded workspace copies,
including Word paragraphs and tables. Hashes identify the exact versions used;
their upload suffixes do not imply a new substantive version.

| Supplied document | SHA-256 |
|---|---|
| Material_System_Discovery_and_Design_Vision_v3(2).docx | ace6cf0526963438a19fce70656c43011ee7ced4efd67251ac5ee9c81876c4e7 |
| Material_System_Product_Definition_and_Delivery_v1 copy(1).docx | ef555db88bd0b055af94ab82c941387ba326261bd2f1eba30679602cf214986b |
| WP1_Complete_Implementation_Instructions(1).docx | 02c0e377561b9283d4bccf3fc96cceb594dba854eb1bc5cfd3576cf92f451e2e |
| Material_System_Implementation_Plan_v2 (1).md | d13eba15ea17b04b506a11a48bfe3f7f4ed48687e9035e1c05046660239b1168 |
| WP0R_Recovery_Report (1).md | 6da5b6f056c58f7590c44654a02919768debdc1b942ec0888f5932c0bffacb7e |

Verified repository recovery commit:
`2655d64f2d5a02dfeaf2a3c4c1e553cda218a89f`, tree
`a55d5ab30dd3afa750574a41b49c335875a05c6a`. The published recovery branch had not
advanced when inspected. No applicable AGENTS.md was found in the repository.
The new branch is based on this recovery commit, not main alone.

Reviewed repository sources from that commit:

- `recovered_wp0/evidence/Material_System_Implementation_Plan_v2.md`
- `recovered_wp0/evidence/WP0_Decision_Pack_and_Assumptions.md`
- `recovered_wp0/evidence/WP0_Manufacturing_Evidence_Reproduction.md`
- `recovered_wp0/README.md`
- `recovered_wp0/ceramic/Ceramic_Evidence_Milestone.md`
- `recovered_wp0/ceramic/ceramic_evidence.json`
- `recovered_wp0/ceramic/ceramic_evaluation.json`
- `recovered_wp0/thermal.py`, `laminate.py`, `test_recovery.py`
- `recovered_wp0/requirements.txt`, `environment-freeze.txt`, `inventory.json`
- `recovered_wp0/test-run.txt`, `thermal_results.json`, `laminate_results.json`
- `recovered_wp0/ceramic/evaluate_ceramic.py`
- Root `README.md`, `requirements.txt`, `pytest.ini`, relevant legacy source,
  test imports and the full offline regression collection
- `docs/phase5_scope_and_guardrails.md`, `phase5_consolidation_report.md`,
  `phase5_path_to_vision.md`
- `docs/phase6_to_full_optimisation_thin_slice_roadmap.md` (zero bytes)
- `docs/build4_practical_workflow_decision.md`,
  `build4_cli_review_workflow_guide.md`

The supplied implementation-plan attachment matches the repository plan hash.
Recovered file hashes remain available in `recovered_wp0/inventory.json`.
That inventory and historical test logs were inspected as prior evidence, not
substituted for the fresh verification in this WP1 task.

Older project attachments are historical context only and were not adopted as
new-core requirements. This source review does not claim a fresh download or
reinspection of the scientific papers cited by the recovered reports. No new
experimental dataset or source-rights clearance was inferred.
