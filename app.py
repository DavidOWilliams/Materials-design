from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.requirement_inference import infer_requirements
from src.candidate_generation import generate_candidates
from src.scoring import score_candidates
from src.reranking import scientific_rerank
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

if "last_run" not in st.session_state:
    st.session_state["last_run"] = None

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
    if df is None or len(df) == 0:
        return df

    out = df.copy()
    out = out.rename(
        columns={
            "candidate_id": "Candidate",
            "material_family": "Material family",
            "composition_concept": "Composition",
            "base_process_route": "Process route",
            "chemsys": "Chemical system",
            "n_elements": "No. of elements",
            "density": "Density",
            "energy_above_hull": "Energy above hull",
            "is_stable": "Stable",
            "theoretical": "Theoretical",
            "engineering_plausibility": "Engineering plausibility",
            "classification_reason": "Why included",
            "alloy_likeness_score": "Alloy likeness",
            "alloy_likeness_reason": "Alloy likeness note",
            "creep_score": "Creep suitability",
            "toughness_score": "Toughness proxy",
            "temperature_score": "Temperature suitability",
            "cost_score": "Cost proxy",
            "sustainability_score": "Sustainability proxy",
            "overall_score": "Overall fit",
            "scientific_rerank_score": "Scientific rerank",
            "confidence": "Confidence",
            "rerank_reason": "Rerank reason",
            "notes": "Commentary",
            "scientific_rerank_score": "Scientific rerank",
            "rerank_reason": "Rerank reason",
        }
    )
    keep_cols = [
        "Candidate",
        "Material family",
        "Composition",
        "Chemical system",
        "No. of elements",
        "Stable",
        "Theoretical",
        "Engineering plausibility",
        "Alloy likeness",
        "Density",
        "Energy above hull",
        "Process route",
        "Creep suitability",
        "Toughness proxy",
        "Temperature suitability",
        "Cost proxy",
        "Sustainability proxy",
        "Overall fit",
        "Scientific rerank",
        "Confidence",
        "Commentary",
        "Rerank reason",
        "Why included",
        "Alloy likeness note",
    ]
    existing = [c for c in keep_cols if c in out.columns]
    return out[existing]

def render_design_frame(requirements: dict):
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
        st.markdown("</div>", unsafe_allow_html=True)

    with info_col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Inference notes**")
        for note in req_view["notes"]:
            st.markdown(f"- {note}")
        st.markdown("</div>", unsafe_allow_html=True)

def render_empty_state(requirements: dict, candidates, scored, near_miss, diagnostics=None):
    render_design_frame(requirements)

    raw_count = len(candidates) if candidates is not None else 0
    scored_count = len(scored) if scored is not None else 0
    near_count = len(near_miss) if near_miss is not None else 0

    st.markdown("## What happened")
    st.write(
        f"- Raw retrieved candidates: **{raw_count}**\n"
        f"- Candidates after scoring/provenance stage: **{scored_count}**\n"
        f"- Near-feasible alternatives available: **{near_count}**"
    )

    if near_miss is not None and len(near_miss) > 0:
        st.markdown("## Near-Feasible Alternatives")
        near_cols = [
            c for c in [
                "candidate_id",
                "material_family",
                "overall_score",
                "confidence",
                "notes",
                "classification_reason",
                "alloy_likeness_reason",
            ]
            if c in near_miss.columns
        ]
        near_display = near_miss[near_cols].rename(
            columns={
                "candidate_id": "Candidate",
                "material_family": "Material family",
                "overall_score": "Overall fit",
                "confidence": "Confidence",
                "notes": "Commentary",
                "classification_reason": "Why included",
                "alloy_likeness_reason": "Alloy likeness note",
            }
        )
        st.dataframe(near_display, use_container_width=True, hide_index=True)
        st.caption(
            "These did not survive as top-ranked concepts, but are the closest available outputs from the current screened set."
        )
    else:
        st.info(
            "No near-feasible alternatives were identified. The current screening may be too strict for this search scope."
        )

    if diagnostics:
        warnings = diagnostics.get("warnings", [])
        if warnings:
            st.markdown("## Screening warnings")
            for warning in warnings:
                st.warning(warning)

        with st.expander("Diagnostics"):
            st.write(diagnostics)

def render_success_state(requirements: dict, top, near_miss, diagnostics=None):
    render_design_frame(requirements)

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

            **Illustrative process route:** {best['base_process_route']}

            **Why it ranks first:** this candidate currently offers the strongest balance of
            inferred creep relevance, elevated-temperature suitability, and chemistry-based
            fit with the prototype's alloy-family rules.

            **Why it was included:** {best.get('classification_reason', 'Matched prototype screening rules.')}

            **Main trade-off:** the current ranking is still based on engineering proxy scores,
            not validated creep or toughness prediction models.

            **Confidence:** {best['confidence']}
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("## Trade-off View")
        required_chart_cols = {"candidate_id", "material_family", "cost_score", "creep_score", "overall_score"}
        if required_chart_cols.issubset(set(top.columns)) and len(top) > 0:
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
        else:
            st.info("Trade-off chart unavailable for the current result set.")

    with right:
        st.markdown("## Near-Feasible Alternatives")
        if near_miss is not None and len(near_miss) > 0:
            near_cols = [
                c for c in [
                    "candidate_id",
                    "material_family",
                    "overall_score",
                    "confidence",
                    "notes",
                ]
                if c in near_miss.columns
            ]
            near_display = near_miss[near_cols].rename(
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
            st.write("No obvious near-feasible alternatives were identified in the current screened set.")

    with st.expander("Method, provenance, and disclaimer"):
        st.markdown("**How this prototype currently works**")
        st.markdown(
            """
            - infers design priorities from the application prompt and temperature  
            - retrieves candidates from Materials Project  
            - filters them using prototype alloy-family rules  
            - applies simple proxy scoring for performance and trade-offs  
            - ranks concepts and highlights best / near-feasible options
            """
        )

        st.markdown("**Provenance**")
        if "candidate_id" in top.columns and "provenance" in top.columns:
            st.write(
                top[["candidate_id", "provenance"]].rename(
                    columns={"candidate_id": "Candidate", "provenance": "Provenance note"}
                )
            )
        else:
            st.write("Provenance columns were not available in the current result set.")

        st.markdown("**Important disclaimer**")
        st.write(
            "This prototype is a decision-support demonstrator for early-stage exploration only. "
            "It is not a qualification, certification, or manufacturing approval tool. "
            "All outputs require expert engineering review and validation."
        )

    if diagnostics:
        warnings = diagnostics.get("warnings", [])
        if warnings:
            st.markdown("## Screening warnings")
            for warning in warnings:
                st.warning(warning)

        with st.expander("Diagnostics"):
            st.write(diagnostics)

def run_pipeline_once(application_prompt, operating_temperature, am_preferred):
    requirements = infer_requirements(application_prompt, operating_temperature, am_preferred)

    candidate_result = generate_candidates(requirements)

    if candidate_result["status"] == "error":
        return {
            "status": "error",
            "message": candidate_result["message"],
            "error_detail": candidate_result.get("error_detail"),
            "requirements": requirements,
            "candidates": candidate_result.get("candidates"),
            "diagnostics": candidate_result.get("diagnostics", {}),
        }

    candidates = candidate_result["candidates"]

    if candidate_result["status"] == "empty" or candidates is None or len(candidates) == 0:
        return {
            "status": "empty",
            "requirements": requirements,
            "candidates": candidates,
            "scored": None,
            "top": None,
            "near_miss": None,
            "diagnostics": candidate_result.get("diagnostics", {}),
            "message": candidate_result["message"],
        }

    scored = score_candidates(candidates, requirements)

    if scored is None or len(scored) == 0:
        return {
            "status": "empty",
            "requirements": requirements,
            "candidates": candidates,
            "scored": scored,
            "top": None,
            "near_miss": None,
            "diagnostics": candidate_result.get("diagnostics", {}),
            "message": "Candidates were retrieved, but none survived scoring.",
        }

    scored = scientific_rerank(scored, requirements)
    scored = add_provenance(scored)
    top, near_miss = rank_candidates(scored)

    if top is None or len(top) == 0:
        return {
            "status": "empty",
            "requirements": requirements,
            "candidates": candidates,
            "scored": scored,
            "top": top,
            "near_miss": near_miss,
            "diagnostics": candidate_result.get("diagnostics", {}),
            "message": "Candidates were retrieved, but none survived the current screening/ranking thresholds.",
        }

    return {
        "status": "success",
        "requirements": requirements,
        "candidates": candidates,
        "scored": scored,
        "top": top,
        "near_miss": near_miss,
        "diagnostics": candidate_result.get("diagnostics", {}),
        "message": candidate_result["message"],
    }

generate_clicked = st.button("Generate concepts", type="primary", use_container_width=False)

if generate_clicked:
    try:
        with st.spinner("Generating candidate concepts..."):
            result = run_pipeline_once(application_prompt, operating_temperature, am_preferred)
        st.session_state["last_run"] = result
    except Exception as exc:
        st.session_state["last_run"] = {
            "status": "error",
            "message": "The backend encountered an error while generating concepts.",
            "error_detail": str(exc),
        }

result = st.session_state.get("last_run")

if result is not None:
    if result["status"] == "success":
        render_success_state(
            requirements=result["requirements"],
            top=result["top"],
            near_miss=result["near_miss"],
            diagnostics=result.get("diagnostics", {}),
        )
    elif result["status"] == "empty":
        st.warning(result["message"])
        render_empty_state(
            requirements=result["requirements"],
            candidates=result.get("candidates"),
            scored=result.get("scored"),
            near_miss=result.get("near_miss"),
            diagnostics=result.get("diagnostics", {}),
        )
    else:
        st.error(result["message"])
        if result.get("error_detail"):
            with st.expander("Technical detail"):
                st.code(result["error_detail"])
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