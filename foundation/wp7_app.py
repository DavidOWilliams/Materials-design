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
from material_core.wp5_brief_editor import open_brief
from material_core.wp4_feedback import starting_inputs

st.set_page_config(page_title="D1 synthetic materials design", layout="wide")
st.title("D1 — synthetic ceramic gradient design")
st.warning("Computational demonstration, NOT measured achieved-state evidence, physical ceramic validation, or production engineering guidance.")
st.caption("Two hypothetical scenario constituents; planar coupon; thermal transmission, areal mass and tensile thermal mismatch. The supported WP4 design-revision policy changes composition after an exceeded mass constraint.")
workspace = Path(st.text_input("D1 workspace", "d1-workspace")).expanduser()
tab_run, tab_review, tab_restore = st.tabs(["1. Run demonstration", "2. Inspect candidates and trade-offs", "3. Restore and replay"])
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
with tab_review:
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
