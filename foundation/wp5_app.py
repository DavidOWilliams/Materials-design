"""WP5 bounded demonstration UI. Run: streamlit run foundation/wp5_app.py.

Synthetic scenario only; numerical qualification is not measured validation.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import streamlit as st
from material_core.wp4_feedback import starting_inputs
from material_core.wp5_brief_editor import validate_brief, revise_brief, save_brief, open_brief
from material_core.wp5_service import execute, inspect, replay, compare_compatible, execute_journal, recover_journal, journal_status, portable_import, compare_scenarios, versioned_scenario

st.set_page_config(page_title="WP5 Materials Design", layout="wide")
st.title("Materials design — bounded WP5 demonstration")
st.warning("Synthetic process assumptions. Estimated achieved state is NOT measured evidence. D1 is not V1.")
workspace = Path(st.text_input("Workspace directory", "wp5-workspace")).expanduser()
tab1, tab2, tab3, tab4 = st.tabs(["Brief editor", "Campaign", "Inspect / compare", "Replay / export"])
with tab1:
    fixture = starting_inputs(elements=128)
    initial = fixture.brief.model_dump(mode="json")
    raw = st.text_area("Typed brief JSON (complete contract)", json.dumps(initial, indent=2), height=300)
    try:
        candidate = validate_brief(json.loads(raw))
        st.success("Brief contract valid")
        st.caption("Editing scientific duty/geometry beyond WP4 supported fixtures will be rejected by the execution adapter.")
        name = st.text_input("Brief filename", "brief.json", key="brief_file")
        if st.button("Save new immutable brief"):
            path = workspace / name
            save_brief(path, candidate)
            st.success(f"Saved {path}: {candidate.content_hash}")
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        st.error(f"Brief invalid: {exc}")
with tab2:
    dossier = st.text_input("New dossier filename", "campaign.json")
    elements = st.selectbox("Numerical elements", [128, 256, 512, 4096], index=0)
    mass_limit = st.number_input("Areal mass limit (kg/m²)", value=31.0)
    layer = st.selectbox("Synthetic layer resolution (m)", [0.0025, 0.005, 0.01], index=1)
    feed = st.selectbox("Synthetic feed fraction step", [0.125, 0.25, 0.5], index=1)
    budget = st.number_input("Maximum evaluations", min_value=1, max_value=100, value=4, step=1)
    feedback = st.checkbox("Enable bounded feedback revision", value=True)
    version = st.number_input("Process scenario version", min_value=1, value=1, step=1)
    brief_path = st.text_input("Saved brief to use (optional; must match supported WP4 fixture)", "")
    if st.button("Execute and persist campaign", type="primary"):
        try:
            with st.spinner("Running WP4 numerical core..."):
                result = execute(workspace / dossier, elements=elements, mass_limit=mass_limit,
                                 layer=layer, feed=feed, budget=int(budget), feedback=feedback,
                                 brief=open_brief(brief_path).model_dump(mode="json") if brief_path else None,
                                 process_version=int(version))
            st.success(f"Saved: {result['stop_reason']}")
            st.json({"stop_reason": result["stop_reason"], "evaluations": result["evaluations"],
                     "proposals": result["proposals"], "records": result["records"],
                     "measured_evidence": None})
        except Exception as exc:
            st.error(f"Execution failed closed: {exc}")
with tab3:
    existing = st.text_input("Existing dossier path", str(workspace / "campaign.json"))
    if st.button("Inspect verified dossier"):
        try:
            data = inspect(existing)
            st.json(data)
        except Exception as exc:
            st.error(str(exc))
    other = st.text_input("Second dossier path (same duty and process only)", "")
    if st.button("Compare verified dossiers"):
        try:
            st.json(compare_compatible(existing, other))
        except Exception as exc:
            st.error(str(exc))
with tab4:
    source = st.text_input("Replay/export dossier", str(workspace / "campaign.json"))
    if st.button("Recompute numerical evidence"):
        try:
            st.json(replay(source))
        except Exception as exc:
            st.error(str(exc))
    if st.button("Prepare conservative export"):
        try:
            payload = Path(source).read_bytes()
            inspect(source)  # verify immutable dossier before offering download
            st.download_button("Download JSON dossier", payload,
                               file_name="wp5-export.json", mime="application/json")
        except Exception as exc:
            st.error(str(exc))

with st.expander("Durable cancellation and recovery (between numerical evaluations)"):
    journal_path = st.text_input("Journal path", str(workspace / "campaign-journal.jsonl"))
    journal_output = st.text_input("Recovered dossier path", str(workspace / "recovered.json"))
    if st.button("Start checkpointed campaign with cancellation"):
        try:
            record = execute_journal(journal_path, elements=elements, mass_limit=mass_limit,
                                     layer=layer, feed=feed, budget=int(budget),
                                     feedback=feedback, process_version=int(version),
                                     cancel_requested=lambda: True)
            st.json({"stop_reason": record["stop_reason"],
                     "journal": journal_path, "measured_evidence": None})
        except Exception as exc:
            st.error(f"Checkpointed run failed: {exc}")
    if st.button("Inspect journal and attempt history"):
        try:
            st.json(journal_status(journal_path))
        except Exception as exc:
            st.error(str(exc))
    if st.button("Resume from durable journal"):
        try:
            result = recover_journal(journal_path, journal_output)
            st.json({"stop_reason": result["stop_reason"],
                     "accounting": result.get("accounting"),
                     "output": journal_output})
        except Exception as exc:
            st.error(f"Recovery rejected: {exc}")

with st.expander("Portable dossier import and replay"):
    import_source = st.text_input("Source dossier to import", "")
    import_target = st.text_input("New immutable destination", str(workspace / "imported.json"))
    if st.button("Import verified dossier"):
        try:
            imported = portable_import(import_source, import_target)
            st.success(f"Imported {len(imported['records'])} candidate records")
        except Exception as exc:
            st.error(f"Import rejected: {exc}")
    if st.button("Replay imported dossier"):
        try:
            st.json(replay(import_target))
        except Exception as exc:
            st.error(f"Replay rejected: {exc}")

with st.expander("Versioned process assumptions and scenario comparison"):
    try:
        process = versioned_scenario(layer=layer, feed=feed, version=int(version))
        st.json(process.model_dump(mode="json"))
        st.caption("WP4 process resolution parameters only. Other manufacturing mechanisms remain excluded.")
    except Exception as exc:
        st.error(str(exc))
    alternate = st.text_input("Distinct scenario dossier", "")
    if st.button("Compare distinct process scenarios (noncausal)"):
        try:
            st.json(compare_scenarios(existing, alternate))
        except Exception as exc:
            st.error(f"Scenario comparison rejected: {exc}")
