"""D1 bounded synthetic ceramic coupon demonstration.

Launch from repository root:
    PYTHONPATH=foundation .venv-foundation/bin/python -m streamlit run foundation/wp7_app.py
No new numerical physics, search policy or measured evidence is introduced.
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import streamlit as st
from d1_visuals import campaign_view, feedback_view, architecture_view
from d1_visual_data import output_conflicts, unused_output
from material_core.wp5_service import execute, replay, portable_import
from material_core.wp7_view import summary, selected_candidate
from material_core.wp3_search import run_search, recompute_search
from material_core.wp7_search_dossier import mixed_summary, mixed_candidate, export_mixed_zip, import_mixed_zip
from material_core.wp5_brief_editor import open_brief
from material_core.wp4_feedback import starting_inputs
from material_core.wp7_handoff import (qualified_handoff_source, execute_handoff, verify_handoff,
    start_checkpointed_handoff, recover_checkpointed_handoff)
from material_core.wp5_service import journal_status

st.set_page_config(page_title="D1 synthetic materials design", layout="wide")
st.title("D1 — guided material-system design")
st.markdown("**Journey:** Define challenge → Explore designs → Evaluate manufacturing → Compare alternatives → Preserve evidence")
st.warning("Computational demonstration, NOT measured achieved-state evidence, physical ceramic validation, or production engineering guidance.")
st.caption("WP3: three hypothetical A/B/C catalogue constituents across homogeneous, layered and gradient architectures. WP4: two-constituent A/B bounded gradient feedback only. The two Pareto sets are scientifically distinct.")
workspace = Path(st.text_input("D1 workspace", "d1-workspace")).expanduser()
tab_run, tab_mixed, tab_review, tab_restore = st.tabs(["1. Run demonstration", "2. Explore three architectures", "3. Inspect feedback and trade-offs", "4. Restore and replay"])
with tab_run:
    st.subheader("Representative built-in example")
    preset = st.selectbox("D1 scenario", ["Representative mass-constrained coupon", "Infeasible mass limit", "Resolution sensitivity"])
    defaults = {"Representative mass-constrained coupon": (31.0, 0.005, 0.25),
                "Infeasible mass limit": (1.0, 0.005, 0.25),
                "Resolution sensitivity": (31.0, 0.01, 0.5)}
    mass, layer_default, feed_default = defaults[preset]
    st.caption("Preset values are synthetic and may be edited. Only the stated bounded WP4 fixture is supported.")
    fixture = starting_inputs(elements=128, mass_limit=mass)
    st.write("**Engineering duty:**", fixture.brief.duty)
    st.write("**Synthetic constituent catalogue:**", ", ".join(m.id for m in fixture.materials))
    st.dataframe([c.model_dump(mode="json") for c in fixture.brief.constraints], use_container_width=True)
    with st.expander("Technical challenge and assumption details"):
        st.json({"duty": fixture.brief.duty, "constraints": [c.model_dump(mode="json") for c in fixture.brief.constraints], "materials": [m.id for m in fixture.materials], "measured_evidence": None})
    filename = st.text_input("New D1 dossier filename", "d1-example.json", key="d1_new_filename")
    filename_valid = bool(filename) and Path(filename).name == filename and filename.endswith(".json") and filename not in (".json", "..json")
    proposed = workspace / filename if filename_valid else None
    existing = output_conflicts(proposed) if proposed is not None else []
    if not filename_valid:
        st.error("Enter a simple filename ending in .json, without directory separators.")
    elif existing:
        st.warning("This dossier already exists and will never be overwritten: " + ", ".join(existing))
        st.info("To review it, use 'Inspect existing dossier' below, or choose a new filename.")
        if st.button("Use suggested unused filename", key="d1_suggest_name"):
            st.session_state["d1_new_filename"] = unused_output(proposed).name
            st.rerun()
        if st.button("Inspect existing dossier", key="d1_inspect_existing"):
            try:
                st.session_state["d1_review"] = summary(proposed)
                st.success("Verified existing dossier opened. See Tab 3 for charts and evidence.")
            except Exception as exc:
                st.error("Existing file could not be verified as a valid D1 dossier: " + str(exc))
    elements = st.selectbox("Mesh elements", [128, 256, 512, 4096], index=0)
    mass_limit = st.number_input("Mass ceiling (kg/m²)", min_value=0.01, value=mass, key=preset)
    layer = st.selectbox("Assumed layer resolution (m)", [0.0025, 0.005, 0.01],
                         index=[0.0025, 0.005, 0.01].index(layer_default), key="layer-"+preset)
    feed = st.selectbox("Assumed feed increment", [0.125, 0.25, 0.5],
                        index=[0.125, 0.25, 0.5].index(feed_default), key="feed-"+preset)
    budget = st.number_input("Candidate evaluation budget", min_value=1, max_value=100, value=4, step=1)
    feedback = st.checkbox("Apply supported feedback composition revision", value=True)
    saved_brief = st.text_input("Optional immutable brief snapshot path", "")
    if st.button("Create new run and save immutable dossier", type="primary", disabled=(not filename_valid or bool(existing))):
        try:
            target = workspace / filename
            if output_conflicts(target):
                raise FileExistsError("Destination became occupied; choose an unused filename. No record was replaced.")
            brief = open_brief(saved_brief).model_dump(mode="json") if saved_brief else None
            record = execute(target, elements=elements, mass_limit=mass_limit, layer=layer,
                             feed=feed, budget=int(budget), feedback=feedback, brief=brief)
            st.session_state["d1_path"] = str(target)
            st.session_state["d1_review"] = summary(target)
            st.success(f"Saved {len(record['records'])} candidates to {target} (stop: {record['stop_reason']}). Inspect them in step 3.")
        except Exception as exc:
            st.error(f"Campaign rejected or failed: {type(exc).__name__}: {exc}")
with tab_mixed:
    st.subheader("WP3 — homogeneous, layered and gradient exploration")
    st.warning("WP3 uses intended-state numerical evaluation only. Its Pareto eligibility does NOT establish manufacturing feasibility. These campaigns must not be mixed with WP4 estimated achieved-state results.")
    mixed_root = Path(st.text_input("New WP3 campaign directory", str(workspace / "mixed-architecture"), key="wp3_new_dir"))
    mixed_path = mixed_root / "campaign.json"
    mixed_collisions = [str(mixed_root)] if mixed_root.exists() else []
    if mixed_collisions:
        st.warning("A WP3 campaign directory already exists. Open its ledger below or choose a fresh destination.")
        if st.button("Suggest unused WP3 campaign directory"):
            st.session_state["wp3_new_dir"] = str(unused_output(mixed_root))
            st.rerun()
    mixed_elements = st.selectbox("WP3 mesh elements", [128, 256, 512, 4096], index=3)
    mixed_budget = st.number_input("WP3 candidate budget", min_value=4, max_value=90, value=9, step=1)
    mixed_seed = st.number_input("WP3 deterministic seed", min_value=0, value=17, step=1)
    mixed_mass = st.number_input("WP3 mass ceiling (kg/m²)", min_value=0.01, value=31.0)
    if st.button("Create new WP3 campaign", disabled=bool(mixed_collisions)):
        try:
            if int(mixed_budget) < 4:
                raise ValueError("At least four proposals are needed: starting homogeneous, then homogeneous, layered and gradient")
            if mixed_root.exists():
                raise FileExistsError("Existing campaign directory cannot be reused for a new run.")
            ledger = run_search(mixed_path, seed=int(mixed_seed), budget=int(mixed_budget),
                                elements=mixed_elements, mass_limit=mixed_mass, method="explore")
            st.success(f"Saved {len(ledger['proposals'])} intended-state proposals to {mixed_path}")
        except Exception as exc:
            st.error(f"WP3 search failed closed: {exc}")
    reopen_path = st.text_input("WP3 ledger path", str(mixed_path))
    if st.button("Inspect WP3 search and numerical Pareto"):
        try:
            st.session_state["wp7_mixed"] = mixed_summary(reopen_path)
        except Exception as exc:
            st.session_state.pop("wp7_mixed", None)
            st.error(f"WP3 ledger rejected: {exc}")
    mixed = st.session_state.get("wp7_mixed")
    if mixed:
        st.info("WP3 stopped: " + str(mixed["stop_reason"]) + ". These are intended-state numerical results, not achieved-state predictions or measurements.")
        with st.expander("WP3 source, scientific qualification and full Pareto evidence"):
            st.json({"source": mixed["ledger"], "stop_reason": mixed["stop_reason"], "qualified_pareto": mixed["pareto"], "scientific_boundary": mixed["scientific_boundary"], "measured_evidence": None})
        chosen_mixed = campaign_view(mixed, scope="WP3 intended-state only", key="wp3_visual_choice")
        if chosen_mixed is not None:
            candidate_detail = mixed_candidate(mixed["ledger"], int(chosen_mixed))
            if candidate_detail.get("intended_design"):
                architecture_view(candidate_detail["intended_design"], key="wp3_architecture")
            with st.expander("Full WP3 candidate source, numerical evaluation and provenance"):
                st.json(candidate_detail)
            if st.button("Select WP3 candidate for WP4 handoff"):
                try:
                    cfg = mixed["config"]
                    chosen, provenance = qualified_handoff_source(
                        mixed["ledger"], int(chosen_mixed),
                        elements=cfg["elements"], mass_limit=cfg["mass_limit"])
                    st.session_state["wp7_handoff"] = {
                        "ledger": mixed["ledger"], "index": int(chosen_mixed),
                        "elements": cfg["elements"], "mass_limit": cfg["mass_limit"]}
                    st.success("Compatible completed A/B gradient selected. Original WP3 numerical eligibility remains explicit; a separate WP4 achieved-state evaluation is required.")
                    st.json(provenance)
                except Exception as exc:
                    st.session_state.pop("wp7_handoff", None)
                    st.error(f"Selected candidate NOT compatible with bounded WP4 feedback: {exc}")
        try:
            zip_bytes = export_mixed_zip(mixed["ledger"])
            st.download_button("Download full verified WP3 dossier ZIP", data=zip_bytes,
                               file_name="d1-wp3-dossier.zip", mime="application/zip")
        except Exception as exc:
            st.error(f"WP3 evidence packaging rejected: {exc}")
    if st.button("Recompute WP3 numerical evidence"):
        try:
            st.json(recompute_search(reopen_path))
        except Exception as exc:
            st.error(f"WP3 numerical replay rejected: {exc}")
    source_upload = st.file_uploader("WP3 portable ZIP to restore", type=["zip"])
    restore_root = st.text_input("New WP3 destination directory", str(workspace / "mixed-restored"))
    if Path(restore_root).exists():
        st.warning("WP3 restore destination already exists. Select a new directory; evidence will not be overwritten.")
    if st.button("Verify and restore WP3 ZIP", disabled=Path(restore_root).exists()):
        try:
            if source_upload is None:
                raise ValueError("Select a WP3 ZIP archive")
            st.json(import_mixed_zip(source_upload.getvalue(), restore_root))
        except Exception as exc:
            st.error(f"WP3 archive restore rejected: {exc}")

with tab_review:
    st.subheader("Selected WP3 candidate → fresh WP4 manufacturing feedback")
    chosen = st.session_state.get("wp7_handoff")
    if chosen:
        st.info("Selected WP3 candidate " + str(chosen["index"]) + ". A fresh WP4 estimated-state evaluation is required; WP3 Pareto is not reused.")
        with st.expander("WP3 source lineage"):
            st.json({"source_ledger": chosen["ledger"], "candidate_index": chosen["index"],
                     "scope": "A/B gradient only; numerical context recomputed; no mixed Pareto"})
        handoff_file = st.text_input("New handoff WP4 dossier", str(workspace / "selected-wp4.json"))
        journal_file = st.text_input("New checkpoint journal", str(workspace / "selected-wp4-journal.jsonl"))
        recovered_file = st.text_input("New recovered dossier", str(workspace / "selected-wp4-recovered.json"))
        handoff_layer = st.selectbox("Selected design layer resolution (m)", [0.0025,0.005,0.01], index=1)
        handoff_feed = st.selectbox("Selected design feed increment", [0.125,0.25,0.5], index=1)
        handoff_budget = st.number_input("Selected design candidate budget", min_value=2, max_value=30, value=4)
        cancel_after = st.number_input("Cooperatively cancel after completed candidates", min_value=0,
                                       max_value=int(handoff_budget)-1, value=1)
        handoff_collisions = output_conflicts(handoff_file, (".handoff.json",))
        journal_collisions = output_conflicts(journal_file, (".manifest.json", ".attempts.jsonl"))
        recovery_collisions = output_conflicts(recovered_file, (".handoff.json",))
        if handoff_collisions:
            st.warning("Selected WP4 output or companion already exists: " + ", ".join(handoff_collisions))
            st.caption("Suggested new WP4 dossier: " + str(unused_output(handoff_file, (".handoff.json",))))
        if journal_collisions:
            st.warning("Checkpoint journal already exists: " + ", ".join(journal_collisions))
            st.caption("Suggested fresh journal: " + str(unused_output(journal_file, (".manifest.json", ".attempts.jsonl"))))
        if recovery_collisions:
            st.warning("Recovery output or companion exists: " + ", ".join(recovery_collisions))
            st.caption("Suggested new recovery dossier: " + str(unused_output(recovered_file, (".handoff.json",))))
        if st.button("Evaluate selected design through WP4 and save", disabled=bool(handoff_collisions)):
            try:
                result = execute_handoff(chosen["ledger"], chosen["index"], handoff_file,
                    elements=chosen["elements"], mass_limit=chosen["mass_limit"],
                    layer=handoff_layer, feed=handoff_feed, budget=int(handoff_budget))
                st.json(verify_handoff(handoff_file))
                st.session_state["d1_path"] = handoff_file
                st.session_state["d1_review"] = summary(handoff_file)
                st.success("WP3 lineage verified and new WP4 estimated-state dossier saved; inspect below.")
            except Exception as exc:
                st.error(f"Selected-design evaluation rejected: {exc}")
        if st.button("Start checkpointed selected-design campaign and cancel", disabled=bool(journal_collisions)):
            try:
                outcome = start_checkpointed_handoff(chosen["ledger"], chosen["index"],
                    journal_file, elements=chosen["elements"], mass_limit=chosen["mass_limit"],
                    layer=handoff_layer, feed=handoff_feed, budget=int(handoff_budget),
                    cancel_after=int(cancel_after))
                st.json(outcome)
            except Exception as exc:
                st.error(f"Checkpointed campaign rejected: {exc}")
        if st.button("Inspect cancellation checkpoints"):
            try:
                st.json(journal_status(journal_file))
            except Exception as exc:
                st.error(f"Journal rejected: {exc}")
        if st.button("Recover selected-design journal into immutable dossier", disabled=bool(recovery_collisions)):
            try:
                result = recover_checkpointed_handoff(journal_file, recovered_file)
                st.json(verify_handoff(recovered_file))
                st.json({"stop_reason":result["stop_reason"],"records":len(result["records"])})
                st.session_state["d1_path"] = recovered_file
                st.session_state["d1_review"] = summary(recovered_file)
                st.success("Recovered original selected design and verified source lineage.")
            except Exception as exc:
                st.error(f"Recovery rejected: {exc}")
    else:
        st.info("For selected-design WP4 handoff, first explore WP3 and choose a compatible qualified A/B gradient. You can separately inspect a standalone WP4 demonstration dossier below.")
    st.subheader("WP4 dossier inspection and conditional Pareto")
    review_path = st.text_input("Verified dossier to inspect", st.session_state.get("d1_path", str(workspace / "d1-example.json")), key="d1_review_path")
    if st.button("Inspect dossier and Pareto"):
        try:
            st.session_state["d1_review"] = summary(review_path)
            st.session_state["d1_path"] = review_path
        except Exception as exc:
            st.session_state.pop("d1_review", None)
            st.error(f"Dossier verification failed: {exc}")
    data = st.session_state.get("d1_review")
    if data:
        st.info("Eligibility and Pareto use accepted WP4 feasibility and WP3 strict dominance, not a new scientific model. Only candidates from this one common scenario are compared.")
        st.info("WP4 stopped: " + str(data["stop_reason"]) + ". All achieved states are synthetic estimates, not measurements.")
        with st.expander("WP4 verified source, objective definitions and scientific evidence"):
            st.json({"source": data["path"], "brief_hash": data["brief_hash"], "stop_reason": data["stop_reason"], "objective_definitions": data["directions"], "pareto": data["pareto"], "measured_evidence": None, "manufacturing_validation": data["manufacturing_validation"]})
        chosen = campaign_view(data, scope="WP4 synthetic estimated-achieved state", key="wp4_visual_choice")
        if chosen is not None:
            detail = selected_candidate(data["path"], int(chosen))
            feedback_view(detail)
            with st.expander("Full technical candidate record (JSON)"):
                st.json(detail)
with tab_restore:
    source = st.text_input("Source dossier", st.session_state.get("d1_path", str(workspace / "d1-example.json")))
    if st.button("Verify integrity and recompute"):
        try:
            report = replay(source)
            st.json(report)
            if report["status"] == "passed":
                st.success("Existing dossier independently recomputed within this process. Restart to check separate-process persistence.")
        except Exception as exc:
            st.error(f"Replay failed closed: {exc}")
    destination = st.text_input("Immutable import destination", str(workspace / "restored.json"))
    if output_conflicts(destination):
        st.warning("Restore destination already exists: " + destination + ". Suggested: " + str(unused_output(destination)))
    if st.button("Restore copied dossier", disabled=bool(output_conflicts(destination))):
        try:
            result = portable_import(source, destination)
            st.success(f"Imported {len(result['records'])} verified candidates without rewriting the original evidence.")
        except Exception as exc:
            st.error(f"Import failed closed: {exc}")
    if st.button("Replay restored dossier"):
        try:
            st.json(replay(destination))
        except Exception as exc:
            st.error(f"Restored replay failed: {exc}")
    try:
        raw = Path(source).read_bytes()
        summary(source)  # verify before permitting download
        st.download_button("Download verified original JSON", data=raw,
                           file_name=Path(source).name, mime="application/json")
        st.caption("Source file SHA256: " + hashlib.sha256(raw).hexdigest())
    except (OSError, ValueError, KeyError, TypeError):
        st.caption("A valid, integrity-checked dossier is needed before export.")
st.caption("No measured process state, material certificate, CFD, sintering, porosity, shrinkage or total residual stress is qualified in D1. Numerical quality remains visible, not automatically promoted.")
