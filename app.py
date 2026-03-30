from __future__ import annotations
import plotly.express as px
import streamlit as st

from src.requirement_inference import infer_requirements
from src.candidate_generation import generate_candidates
from src.scoring import score_candidates
from src.ranking import rank_candidates
from src.provenance import add_provenance

st.set_page_config(
    page_title="Aviation Materials Design Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .small-muted {
            color: #6b7280;
            font-size: 0.92rem;
        }
        .section-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(120,120,120,0.2);
            border-radius: 0.9rem;
            background: rgba(250,250,250,0.02);
            margin-bottom: 0.75rem;
        }
        .highlight-card {
            padding: 1.1rem 1.2rem;
            border-radius: 1rem;
            border: 1px solid rgba(120,120,120,0.25);
            background: rgba(0, 104, 201, 0.06);
            margin-bottom: 1rem;
        }
        .disclaimer-box {
            padding: 0.9rem 1rem;
            border-left: 4px solid #9ca3af;
            background: rgba(120,120,120,0.08);
            border-radius: 0.5rem;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Application-Led Aviation Materials Design Assistant")
st.markdown(
    """
    **Prototype purpose:** demonstrate how an engineer could move from an application-level need
    to a short list of plausible material-and-process concepts, with trade-offs, confidence notes,
    and near-feasible alternatives in one workflow.
    """
)

st.markdown(
    """
    <div class="disclaimer-box">
    <strong>Concept demonstrator only.</strong> This app supports early-stage engineering exploration.
    It does not qualify, certify, or approve materials for aviation use.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Design Inputs")
    application_prompt = st.text_area(
        "Application prompt",
        value=(
            "Design a material for a hot aviation component operating at 850°C "
            "where creep is critical and additive manufacturing is preferred."
        ),
        height=160,
        help="Describe the intended use case in plain language.",
    )
    operating_temperature = st.slider(
        "Operating temperature (°C)",
        min_value=200,
        max_value=1200,
        value=850,
        step=25,
    )
    am_preferred = st.checkbox("Additive manufacturing preferred", value=True)

    st.markdown("---")
    st.markdown("### What the prototype returns")
    st.markdown(
        """
        - 3–5 ranked concept candidates  
        - process-route suggestions  
        - property proxy scores  
        - best-option summary  
        - near-miss alternatives  
        - confidence and provenance notes
        """
    )

def format_requirements(requirements: dict) -> dict:
    weights = requirements["weights"]
    weight_labels = {
        "creep_priority": "Creep",
        "toughness_priority": "Toughness",
        "temperature_priority": "Temperature suitability",
        "cost_priority": "Cost",
        "sustainability_priority": "Sustainability",
    }
    ranked_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    top_priorities = [weight_labels[k] for k, _ in ranked_weights[:3]]

    return {
        "application": requirements["application_prompt"],
        "temperature": f"{requirements['operating_temperature']}°C",
        "am_preferred": "Yes" if requirements["am_preferred"] else "No",
        "allowed_families": ", ".join(requirements["allowed_material_families"]),
        "top_priorities": ", ".join(top_priorities),
        "notes": requirements["notes"],
    }

def make_display_table(df):
    out = df.copy()
    out = out.rename(
        columns={
            "candidate_id": "Candidate",
            "material_family": "Material family",
            "composition_concept": "Composition",
            "base_process_route": "Process route",
            "chemsys": "Chemical system",
            "density": "Density",
            "energy_above_hull": "Energy above hull",
            "is_stable": "Stable",
            "theoretical": "Theoretical",
            "creep_score": "Creep suitability",
            "toughness_score": "Toughness proxy",
            "temperature_score": "Temperature suitability",
            "cost_score": "Cost proxy",
            "sustainability_score": "Sustainability proxy",
            "overall_score": "Overall fit",
            "confidence": "Confidence",
            "notes": "Commentary",
        }
    )
    keep_cols = [
        "Candidate",
        "Material family",
        "Composition",
        "Chemical system",
        "Density",
        "Energy above hull",
        "Stable",
        "Theoretical",
        "Process route",
        "Creep suitability",
        "Toughness proxy",
        "Temperature suitability",
        "Cost proxy",
        "Sustainability proxy",
        "Overall fit",
        "Confidence",
        "Commentary",
    ]
    existing = [c for c in keep_cols if c in out.columns]
    return out[existing]

if st.button("Generate concepts", type="primary", use_container_width=False):
    requirements = infer_requirements(application_prompt, operating_temperature, am_preferred)
    candidates = generate_candidates(requirements)
    scored = score_candidates(candidates, requirements)
    scored = add_provenance(scored)
    top, near_miss = rank_candidates(scored)

    req_view = format_requirements(requirements)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Operating temperature", req_view["temperature"])
    col2.metric("AM preferred", req_view["am_preferred"])
    col3.metric("Candidate families", len(requirements["allowed_material_families"]))
    col4.metric("Top priorities", req_view["top_priorities"])

    st.markdown("## Inferred Design Frame")
    info_col1, info_col2 = st.columns([1.3, 1])
    with info_col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Application prompt interpreted as**")
        st.write(req_view["application"])
        st.markdown("**Material families currently in scope**")
        st.write(req_view["allowed_families"])
        st.markdown('</div>', unsafe_allow_html=True)
    with info_col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Inference notes**")
        for note in req_view["notes"]:
            st.markdown(f"- {note}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## Ranked Candidate Concepts")
    display_table = make_display_table(top)
    st.dataframe(display_table, use_container_width=True, hide_index=True)

    if len(top) > 0:
        best = top.iloc[0]
        st.markdown("## Best Overall Concept")
        st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            ### {best['candidate_id']} — {best['material_family']}

            **Composition concept:** {best['composition_concept']}

            **Recommended process route:** {best['base_process_route']}

            **Why it ranks first:** this concept currently offers the strongest balance of
            creep suitability, elevated-temperature suitability, and fit with the inferred
            engineering priorities for the use case.

            **Main trade-off:** cost and sustainability remain less favorable than for some lower-performance alternatives.

            **Confidence:** {best['confidence']}
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("## Trade-off View")
        chart_df = top.copy()
        chart_df["label"] = chart_df["candidate_id"] + " | " + chart_df["material_family"]
        fig = px.scatter(
            chart_df,
            x="cost_score",
            y="creep_score",
            size="overall_score",
            hover_name="label",
            title="Cost proxy vs creep suitability",
        )
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("## Near-Feasible Alternatives")
        if len(near_miss) > 0:
            near_display = near_miss[
                ["candidate_id", "material_family", "overall_score", "confidence", "notes"]
            ].rename(
                columns={
                    "candidate_id": "Candidate",
                    "material_family": "Material family",
                    "overall_score": "Overall fit",
                    "confidence": "Confidence",
                    "notes": "Commentary",
                }
            )
            st.dataframe(near_display, use_container_width=True, hide_index=True)
            st.caption(
                "These concepts do not rank highest overall, but may be useful where cost, "
                "risk, or process considerations outweigh raw performance."
            )
        else:
            st.write(
                "No obvious near-feasible alternatives were identified in the current seeded set."
            )

    with st.expander("Method, provenance, and disclaimer"):
        st.markdown("**How this prototype currently works**")
        st.markdown(
            """
            - infers design priorities from the application prompt and temperature  
            - filters a small seeded candidate set  
            - applies simple proxy scoring for performance and trade-offs  
            - ranks concepts and highlights best / near-feasible options
            """
        )

        st.markdown("**Provenance**")
        st.write(
            top[["candidate_id", "provenance"]].rename(
                columns={"candidate_id": "Candidate", "provenance": "Provenance note"}
            )
        )

        st.markdown("**Important disclaimer**")
        st.write(
            "This prototype is a decision-support demonstrator for early-stage exploration only. "
            "It is not a qualification, certification, or manufacturing approval tool. "
            "All outputs require expert engineering review and validation."
        )
else:
    st.markdown("## How to use this prototype")
    st.markdown(
        """
        1. Enter the application need in plain language.  
        2. Set the operating temperature and process preference.  
        3. Click **Generate concepts**.  
        4. Review the ranked concepts, best-option summary, and near-feasible alternatives.
        """
    )

    st.markdown("## Recommended demo prompt")
    st.code(
        "Design a material for a hot aviation component operating at 850°C "
        "where creep is critical and additive manufacturing is preferred."
    )