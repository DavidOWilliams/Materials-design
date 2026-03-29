from __future__ import annotations
import pandas as pd
import plotly.express as px
import streamlit as st

from src.requirement_inference import infer_requirements
from src.candidate_generation import generate_candidates
from src.scoring import score_candidates
from src.ranking import rank_candidates
from src.provenance import add_provenance

st.set_page_config(page_title="Aviation Materials Prototype", layout="wide")

st.title("Application-Led Aviation Materials Design Assistant")
st.caption("Concept demonstrator only. For early-stage design exploration, not material qualification or certification.")

with st.sidebar:
    st.header("Inputs")
    application_prompt = st.text_area(
        "Application prompt",
        value="Design a material for a hot aviation component operating at 850°C where creep is critical and additive manufacturing is preferred."
    )
    operating_temperature = st.slider("Operating temperature (°C)", min_value=200, max_value=1200, value=850, step=25)
    am_preferred = st.checkbox("Additive manufacturing preferred", value=True)

if st.button("Generate concepts", type="primary"):
    requirements = infer_requirements(application_prompt, operating_temperature, am_preferred)
    candidates = generate_candidates(requirements)
    scored = score_candidates(candidates, requirements)
    scored = add_provenance(scored)
    top, near_miss = rank_candidates(scored)

    st.subheader("Inferred requirements")
    st.json(requirements)

    st.subheader("Top candidate concepts")
    display_cols = [
        "candidate_id", "material_family", "composition_concept", "base_process_route",
        "creep_score", "toughness_score", "temperature_score",
        "cost_score", "sustainability_score", "overall_score", "confidence", "notes"
    ]
    st.dataframe(top[display_cols], use_container_width=True)

    if len(top) > 0:
        best = top.iloc[0]
        st.subheader("Best overall concept")
        st.write(
            f"**{best['candidate_id']} — {best['material_family']}**. "
            f"This concept ranks highest because it best balances creep suitability, "
            f"temperature suitability, and the inferred priorities for the use case. "
            f"Main process route: {best['base_process_route']}. "
            f"Confidence: **{best['confidence']}**."
        )

    if len(near_miss) > 0:
        st.subheader("Near-miss options")
        st.dataframe(
            near_miss[["candidate_id", "material_family", "overall_score", "confidence", "notes"]],
            use_container_width=True
        )
    else:
        st.subheader("Near-miss options")
        st.write("No obvious near-miss candidates in the current seeded set.")

    chart_df = top.copy()
    chart_df["label"] = chart_df["candidate_id"] + " | " + chart_df["material_family"]
    fig = px.scatter(
        chart_df,
        x="cost_score",
        y="creep_score",
        size="overall_score",
        hover_name="label",
        title="Trade-off view: cost proxy vs creep suitability"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Provenance and disclaimers", expanded=False):
        st.write(top[["candidate_id", "provenance"]])
        st.write(
            "This prototype is a decision-support demonstrator. "
            "It generates and ranks candidate material/process concepts to support early-stage engineering exploration. "
            "It does not certify, qualify, or approve materials for aviation use."
        )
else:
    st.info("Set the inputs on the left, then click **Generate concepts**.")

