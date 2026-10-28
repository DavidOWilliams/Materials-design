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
st.title("D1 — synthetic ceramic material-system design")
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
    st.json({"duty": fixture.brief.duty,
             "constraints": [c.model_dump(mode="json") for c in fixture.brief.constraints],
             "materials": [m.id for m in fixture.materials],
             "measured_evidence": None})
    filename = st.text_input("New D1 dossier filename", "d1-example.json")
    elements = st.selectbox("Mesh elements", [128, 256, 512, 4096], index=0)
    mass_limit = st.number_input("Mass ceiling (kg/m²)", min_value=0.01, value=mass, key=preset)
    layer = st.selectbox("Assumed layer resolution (m)", [0.0025, 0.005, 0.01],
                         index=[0.0025, 0.005, 0.01].index(layer_default), key="layer-"+preset)
    feed = st.selectbox("Assumed feed increment", [0.125, 0.25, 0.5],
                        index=[0.125, 0.25, 0.5].index(feed_default), key="feed-"+preset)
    budget = st.number_input("Candidate evaluation budget", min_value=1, max_value=100, value=4, step=1)
    feedback = st.checkbox("Apply supported feedback composition revision", value=True)
    saved_brief = st.text_input("Optional immutable brief snapshot path", "")
    if st.button("Generate, evaluate and save dossier", type="primary"):
        try:
            target = workspace / filename
            if not filename or Path(filename).name != filename or not filename.endswith(".json"):
                raise ValueError("Use a plain .json dossier filename without directories")
            brief = open_brief(saved_brief).model_dump(mode="json") if saved_brief else None
            record = execute(target, elements=elements, mass_limit=mass_limit, layer=layer,
                             feed=feed, budget=int(budget), feedback=feedback, brief=brief)
            st.session_state["d1_path"] = str(target)
            st.success(f"Persisted {len(record['records'])} candidates to {target} (stop: {record['stop_reason']}). Open tab 2.")
        except Exception as exc:
            st.error(f"Campaign rejected or failed: {type(exc).__name__}: {exc}")
with tab_mixed:
    st.subheader("WP3 — homogeneous, layered and gradient exploration")
    st.warning("WP3 uses intended-state numerical evaluation only. Its Pareto eligibility does NOT establish manufacturing feasibility. These campaigns must not be mixed with WP4 estimated achieved-state results.")
    mixed_root = workspace / "mixed-architecture"
    mixed_path = mixed_root / "campaign.json"
    mixed_elements = st.selectbox("WP3 mesh elements", [128, 256, 512, 4096], index=3)
    mixed_budget = st.number_input("WP3 candidate budget", min_value=4, max_value=90, value=9, step=1)
    mixed_seed = st.number_input("WP3 deterministic seed", min_value=0, value=17, step=1)
    mixed_mass = st.number_input("WP3 mass ceiling (kg/m²)", min_value=0.01, value=31.0)
    if st.button("Generate three architecture classes and persist WP3 campaign"):
        try:
            if int(mixed_budget) < 4:
                raise ValueError("At least four proposals are needed: starting homogeneous, then homogeneous, layered and gradient")
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
        st.json({"source": mixed["ledger"], "stop_reason": mixed["stop_reason"],
                 "qualified_pareto": mixed["pareto"], "scientific_boundary": mixed["scientific_boundary"],
                 "measured_evidence": None})
        st.dataframe(mixed["rows"], use_container_width=True)
        if mixed["rows"]:
            chosen_mixed = st.selectbox("Select WP3 candidate", [r["candidate"] for r in mixed["rows"]])
            st.json(mixed_candidate(mixed["ledger"], int(chosen_mixed)))
            if st.button("Select WP3 candidate for WP4 handoff"):
                try:
                    cfg = mixed["config"]
                    chosen, provenance = qualified_handoff_source(
                        mixed["ledger"], int(chosen_mixed),
                        elements=cfg["elements"], mass_limit=cfg["mass_limit"])
                    st.session_state["wp7_handoff"] = {
                        "ledger": mixed["ledger"], "index": int(chosen_mixed),
                        "elements": cfg["elements"], "mass_limit": cfg["mass_limit"]}
                    st.success("Compatible, qualified gradient selected. A separate WP4 achieved-state evaluation is required.")
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
    if st.button("Verify and restore WP3 ZIP"):
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
        if st.button("Evaluate selected design through WP4 and save"):
            try:
                result = execute_handoff(chosen["ledger"], chosen["index"], handoff_file,
                    elements=chosen["elements"], mass_limit=chosen["mass_limit"],
                    layer=handoff_layer, feed=handoff_feed, budget=int(handoff_budget))
                st.json(verify_handoff(handoff_file))
                st.session_state["d1_path"] = handoff_file
                st.success("WP3 lineage verified and new WP4 estimated-state dossier saved; inspect below.")
            except Exception as exc:
                st.error(f"Selected-design evaluation rejected: {exc}")
        if st.button("Start checkpointed selected-design campaign and cancel"):
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
        if st.button("Recover selected-design journal into immutable dossier"):
            try:
                result = recover_checkpointed_handoff(journal_file, recovered_file)
                st.json(verify_handoff(recovered_file))
                st.json({"stop_reason":result["stop_reason"],"records":len(result["records"])})
                st.session_state["d1_path"] = recovered_file
                st.success("Recovered original selected design and verified source lineage.")
            except Exception as exc:
                st.error(f"Recovery rejected: {exc}")
    else:
        st.info("First explore WP3, inspect a numerically qualified A/B gradient, then select it for handoff. Unsupported designs are rejected explicitly.")
    st.subheader("WP4 dossier inspection and conditional Pareto")
    review_path = st.text_input("Verified dossier to inspect", st.session_state.get("d1_path", str(workspace / "d1-example.json")))
    if st.button("Inspect dossier and Pareto"):
        try:
            st.session_state["d1_review"] = summary(review_path)
        except Exception as exc:
            st.session_state.pop("d1_review", None)
            st.error(f"Dossier verification failed: {exc}")
    data = st.session_state.get("d1_review")
    if data:
        st.info("Eligibility and Pareto use accepted WP4 feasibility and WP3 strict dominance, not a new scientific model. Only candidates from this one common scenario are compared.")
        st.json({"source": data["path"], "brief_hash": data["brief_hash"],
                 "stop_reason": data["stop_reason"], "objective_definitions": data["directions"],
                 "pareto": data["pareto"], "measured_evidence": None,
                 "manufacturing_validation": data["manufacturing_validation"]})
        st.dataframe(data["rows"], use_container_width=True)
        if data["rows"]:
            chosen = st.selectbox("Select saved candidate", [r["candidate"] for r in data["rows"]])
            st.json(selected_candidate(data["path"], int(chosen)))
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
    if st.button("Restore copied dossier"):
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
