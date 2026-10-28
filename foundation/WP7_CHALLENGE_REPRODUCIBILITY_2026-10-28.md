# WP7 Challenge and Reproducibility — Gate 2

Proposed source SHA 4fc1bc3bd07de146460be1729469c7ea1e35969c (accepted upstream WP6 1f89c2d1bf64b669ca98b81f4305d20d08104e5c). Run https://github.com/DavidOWilliams/Materials-design/actions/runs/40673439977 is the exact source candidate qualification.

Tests are executable, not claimed successful until CI ends:
- test_d1_saved_campaign_pareto_and_independent_process: mass 31 synthetic dossier, WP3 Pareto readout, an actual separate interpreter replay.
- test_d1_infeasible_and_integrity_failure: mass 1 scenario, no eligible designs, tampered WP4 integrity failure.
- test_d1_invalid_input_no_overwrite_and_determinism: budget zero rejected without evidence creation; immutability, identical repeated WP4 dossier bytes.
- test_three_architectures_durable_zip_independent_process: WP3 homogeneous, layered and gradient classes; immutable store, ZIP manifest and restore, independent separate-process numerical recompute.
- test_wp3_archive_tamper_and_path_traversal_closed: checksum and path traversal rejection with no imported destination.
- test_wp3_real_streamlit_app_widgets and test_d1_actual_streamlit_widgets: UI interactions are real Streamlit AppTest calls, not mock services.
- foundation/wp7_create_examples.py: 4096-element WP3 mixed architecture nine-slot campaign, WP4 representative and infeasible dossiers, complete portable ZIP and three separately executed Python-process replays; all generated contents should be archived with nonempty SHA256SUMS.
- Full foundation/tests recovered_wp0 regression suite protects accepted numerical behavior; no scientific code altered.

Scientific interpretation: WP3 intended-state Pareto is qualified numerically only, manufacturing feasibility remains unknown. WP4 estimated achieved-state feasibility is conditional on synthetic layer/feed scenario. These are different comparison contexts. Missing/nonfinite or unqualified results must not enter Pareto, and no measured evidence is claimed.

Evidence archive and detailed counts must come from a completed exact-source workflow and hashes must be independently checked. Earlier source 823b4c49d5396f2af28dcd307551e764b336f1be completed the full-resolution example step, but its browser test failed. Gate 2 pending current run; no final PASS at authorship.
