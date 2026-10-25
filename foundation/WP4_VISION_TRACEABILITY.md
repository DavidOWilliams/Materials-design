# WP4 Vision traceability — working crosswalk

Source authority: *Material System Discovery and Design Vision v3.0* (13 October 2026), *Material System Inverse Design — Product Definition and Delivery Pathway v1* (14 October 2026), and WP4 Manufacturing Feedback Implementation Brief v1.0 (25 October 2026). The WP4 brief explicitly places this work inside the assumption-based D1 demonstration, not the measured-evidence V1 milestone.

| Source theme | WP4 contract/service | Verification or deferral |
|---|---|---|
| Material design remains central | `IntendedDesign`, `wp4_feedback._revise` | Tests of changed constituent fraction and parent lineage; general material-system search deferred |
| Connected design/manufacturing loop | `ProcessScenario`, `wp4_resolution.transform`, `wp4_bridge.estimated_inputs` | Transformer and WP2 estimated-target tests; calibrated manufacturing simulation deferred |
| Distinct intended, estimated, measured | `RunInputs.evaluation_target`, `EstimatedAchievedState`, `MeasuredAchievedState` contract | WP4 uses estimated only; real measurements and uncertainty deferred to V1 |
| Multiple objectives and constraints | Existing WP2 `Evaluation` and numerical eligibility | WP4 mass-cap revision test; general Pareto and robust decisions remain incomplete |
| Evidence and reproducibility | `wp4_feedback.save/reopen/recompute` | Dossier mutation/replay tests; full interruption journal and independent review pending |
| Replaceable scientific tools | Existing WP2 solver identity; bounded transform ID/version | Formal WP4 transform registry and second capability scenario pending |
| Manufacturing physics and residual stress | Explicit excluded mechanisms; WP2 tensile thermal mismatch | CFD, shrinkage, sintering, porosity and total manufacturing residual stress remain unsupported |
| Product lifecycle and user workflow | CLI prototype and no WP5 UI | WP5 interface, measured validation and complete D1 delivery deferred |

This working crosswalk is not a claim that every original Product Definition requirement identifier has been audited. An exact identifier-level crosswalk remains required for Gate 3.
