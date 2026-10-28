"""Read-only D1 engineering charts; all plotted values originate in verified summary rows."""
from __future__ import annotations
import pandas as pd
import streamlit as st

OBJECTIVES = (
    ("thermal_transmission", "Thermal transmission", "W/m²"),
    ("areal_mass", "Areal mass", "kg/m²"),
    ("tensile_thermal_mismatch", "Tensile thermal mismatch", "Pa"),
)

def campaign_view(data, *, scope: str, key: str):
    """Keep WP3 intended and WP4 estimated-state campaigns in separate calls."""
    rows = data.get("rows", [])
    st.subheader(f"{scope} — candidate performance")
    st.caption("All three objectives: lower is preferred. Charts are descriptive, not a new eligibility or Pareto calculation.")
    if not rows:
        st.info("No persisted candidates are available for comparison.")
        return
    frame = pd.DataFrame(rows).copy()
    frame["candidate_label"] = frame["candidate"].map(lambda x: f"Candidate {x}")
    for field, label, unit in OBJECTIVES:
        if field not in frame:
            st.info(f"{label}: no supported values available.")
            continue
        valid = frame[["candidate_label", field]].copy()
        valid[field] = pd.to_numeric(valid[field], errors="coerce")
        valid = valid.dropna()
        if valid.empty:
            st.info(f"{label}: unresolved or missing numerical values; no chart drawn.")
            continue
        st.markdown(f"**{label}** — {unit} · lower is preferred")
        st.bar_chart(valid.set_index("candidate_label")[[field]], use_container_width=True)
    st.markdown("**Exact values, qualification and exclusion reasons**")
    st.dataframe(frame.drop(columns=["candidate_label"]), use_container_width=True, hide_index=True)
    st.caption("A plotted value does not establish feasibility. Consult eligibility, numerical quality and reasons in the table.")
    candidates = frame["candidate"].tolist()
    selected = st.selectbox("Inspect exact candidate", candidates, key=key)
    return int(selected)

def feedback_view(record):
    """Explain supported revision evidence without manufacturing invented profiles."""
    st.subheader("Manufacturing feedback and design lineage")
    st.caption("Intended design → synthetic manufacturing estimate → conditional evaluation → feedback (when applicable)")
    feedback = record.get("feedback")
    if feedback is None:
        st.info("No recorded feedback revision for this candidate. Do not infer improvement.")
    else:
        st.write("Recorded feedback", feedback)
    st.markdown("**Intended versus estimated inputs**")
    left, right = st.columns(2)
    with left:
        st.caption("Intended design — synthetic input")
        st.json(record.get("intended_design"))
    with right:
        st.caption("Estimated achieved inputs — synthetic prediction, NOT measurement")
        st.json(record.get("estimated_inputs"))
    with st.expander("Exact evaluation, balances and integrity hashes"):
        st.json({k:record.get(k) for k in ("evaluation","balances","intended_hash","estimated_hash","evaluation_hash")})
