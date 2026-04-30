from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.requirement_inference import infer_requirements
from src.candidate_generation import generate_candidates
from src.evaluation import DECISION_PROFILES, PROFILE_ORDER, apply_decision_profile
from src.scoring import score_candidates
from src.reranking import scientific_rerank
from src.ranking import rank_candidates
from src.provenance import add_provenance
from src.requirement_schema import FACTOR_LABELS, FACTOR_REASON_COLUMNS, FACTOR_SCORE_COLUMNS

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

        .review-intro {
            padding: 0.9rem 1rem;
            border-radius: 0.8rem;
            background: rgba(2, 132, 199, 0.08);
            border: 1px solid rgba(2, 132, 199, 0.18);
            margin-bottom: 1rem;
            font-size: 1.0rem;
        }
        .summary-card {
            min-height: 8.3rem;
            padding: 1rem 1.1rem;
            border: 1px solid rgba(120,120,120,0.20);
            border-radius: 1rem;
            background: rgba(255,255,255,0.04);
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
            margin-bottom: 0.8rem;
        }
        .primary-card {
            border-color: rgba(2, 132, 199, 0.35);
            background: rgba(2, 132, 199, 0.08);
        }
        .summary-label {
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-size: 0.74rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .summary-value {
            font-size: 1.7rem;
            font-weight: 750;
            line-height: 1.12;
            margin-bottom: 0.4rem;
        }
        .small-value {
            font-size: 1.18rem;
        }
        .summary-note, .muted {
            color: #6b7280;
            font-size: 0.88rem;
            line-height: 1.35;
        }
        .plain-card {
            padding: 1rem 1.1rem;
            border: 1px solid rgba(120,120,120,0.18);
            border-radius: 1rem;
            background: rgba(255,255,255,0.025);
            margin-bottom: 0.8rem;
        }
        .badge-row {
            margin: 0.35rem 0 0.7rem 0;
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
        }
        .badge {
            display: inline-block;
            padding: 0.26rem 0.55rem;
            border-radius: 999px;
            background: rgba(55, 65, 81, 0.08);
            border: 1px solid rgba(55, 65, 81, 0.12);
            font-size: 0.86rem;
            font-weight: 600;
        }
        .family-card, .factor-card {
            display: flex;
            justify-content: space-between;
            gap: 0.9rem;
            align-items: flex-start;
            padding: 0.8rem 0.9rem;
            border: 1px solid rgba(120,120,120,0.17);
            border-radius: 0.85rem;
            background: rgba(255,255,255,0.025);
            margin-bottom: 0.55rem;
        }
        .family-title, .factor-title {
            font-weight: 700;
            margin-bottom: 0.12rem;
        }
        .family-status, .priority-pill {
            white-space: nowrap;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.25rem 0.5rem;
            border-radius: 999px;
            background: rgba(2, 132, 199, 0.10);
            color: #075985;
            border: 1px solid rgba(2, 132, 199, 0.18);
        }
        .compact-list {
            margin-top: 0.2rem;
            padding-left: 1.1rem;
        }

    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Application-Led Aviation Materials Design Assistant")
st.markdown(
    """
    **Prototype purpose:** demonstrate how an engineer could move from an application-level need
    to a short list of plausible material-and-process concepts, with explicit trade-offs, confidence notes,
    and recipe-style manufacturing concepts in one workflow.
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
if "pending_interpretation" not in st.session_state:
    st.session_state["pending_interpretation"] = None
if "last_error" not in st.session_state:
    st.session_state["last_error"] = None

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
    scenario_profile = st.selectbox(
        "Decision scenario",
        options=PROFILE_ORDER,
        index=PROFILE_ORDER.index("Balanced"),
        help="Controls downstream ranking weights only. It does not change baseline survival.",
    )
    st.caption(DECISION_PROFILES[scenario_profile]["summary"])

    st.markdown("---")
    st.markdown("### What the prototype returns")
    st.markdown(
        """
        - ranked concept candidates  
        - performance and decision summaries  
        - factor breakdowns per candidate  
        - strengths and watch-outs  
        - recipe-style manufacturing concepts  
        - confidence, reranking, and provenance notes
        """
    )


def _input_signature(application_prompt: str, operating_temperature: int, am_preferred: bool, scenario_profile: str) -> dict:
    """Small comparable signature used to detect stale interpretations."""
    return {
        "application_prompt": application_prompt or "",
        "operating_temperature": int(operating_temperature),
        "am_preferred": bool(am_preferred),
        "scenario_profile": scenario_profile,
    }


def _same_signature(left: dict | None, right: dict | None) -> bool:
    return dict(left or {}) == dict(right or {})


def _priority_table(values: dict, *, label_lookup: dict | None = None, minimum: float = 0.0) -> pd.DataFrame:
    label_lookup = label_lookup or {}
    rows = []
    for key, value in (values or {}).items():
        try:
            numeric = float(value)
        except Exception:
            continue
        if numeric < minimum:
            continue
        rows.append({"Item": label_lookup.get(key, str(key).replace("_", " ").title()), "Priority": round(numeric, 3)})
    if not rows:
        return pd.DataFrame(columns=["Item", "Priority"])
    return pd.DataFrame(rows).sort_values("Priority", ascending=False).reset_index(drop=True)


def _family_prior_table(scope_plan: dict) -> pd.DataFrame:
    priors = scope_plan.get("family_priors", {}) or {}
    rationale = scope_plan.get("family_rationale", {}) or {}
    rows = []
    for family, prior in priors.items():
        rows.append(
            {
                "Family": family,
                "Prior": round(float(prior), 3),
                "Rationale": rationale.get(family, ""),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["Family", "Prior", "Rationale"])
    return pd.DataFrame(rows).sort_values("Prior", ascending=False).reset_index(drop=True)


def _factor_weight_table(scope_plan: dict) -> pd.DataFrame:
    weights = scope_plan.get("active_factor_weights", {}) or {}
    active = scope_plan.get("active_factor_set", []) or []
    rows = []
    for factor in active:
        rows.append(
            {
                "Active factor": FACTOR_LABELS.get(factor, str(factor).replace("_", " ").title()),
                "Weight / priority": round(float(weights.get(factor, 0.0) or 0.0), 3),
            }
        )
    if not rows:
        return pd.DataFrame(columns=["Active factor", "Weight / priority"])
    return pd.DataFrame(rows).sort_values("Weight / priority", ascending=False).reset_index(drop=True)


def _humanise_token(value: object) -> str:
    """Convert internal schema tokens into short engineer-readable labels."""
    if value is None:
        return "Not specified"
    text = str(value).strip()
    if not text:
        return "Not specified"
    replacements = {
        "am": "Additive manufacturing",
        "lpbf": "LPBF",
        "dmls": "DMLS",
        "hot_section": "Hot-section component",
        "high_temperature": "High temperature",
        "sustained_high_temperature_load": "Sustained high-temperature load",
        "thermal_cycling": "Thermal cycling",
        "hot_corrosion": "Hot corrosion",
        "salt_contaminant": "Salt / contaminant exposure",
        "sliding_contact": "Sliding contact",
        "complex_internal_channels": "Complex internal channels",
        "strength_to_weight": "Strength-to-weight",
        "fatigue": "Fatigue",
        "creep": "Creep",
        "oxidation": "Oxidation",
        "wear": "Wear",
        "erosion": "Erosion",
        "fracture_toughness": "Fracture toughness",
        "thermal_fatigue": "Thermal fatigue",
        "route_suitability": "Route suitability",
        "manufacturability": "Manufacturability",
        "evidence_maturity": "Evidence maturity",
        "recipe_support": "Recipe support",
        "through_life_cost": "Through-life cost",
        "supply_risk": "Supply risk",
    }
    key = text.lower().replace(" ", "_").replace("-", "_")
    if key in replacements:
        return replacements[key]
    return text.replace("_", " ").replace("-", " ").title()


def _priority_label(value: object) -> str:
    try:
        score = float(value)
    except Exception:
        return "Normal"
    if score >= 0.75:
        return "Critical"
    if score >= 0.50:
        return "High"
    if score >= 0.25:
        return "Relevant"
    return "Background"


def _confidence_label(value: object) -> str:
    try:
        score = float(value)
    except Exception:
        return "Not assessed"
    if score >= 0.75:
        return "Good"
    if score >= 0.55:
        return "Moderate"
    return "Low"


def _html_list(items: list[str], empty_text: str = "None detected") -> str:
    clean = [str(item).strip() for item in items if str(item).strip()]
    if not clean:
        return f"<span class='muted'>{empty_text}</span>"
    return "".join(f"<li>{item}</li>" for item in clean)


def _top_items(values: dict, *, minimum: float = 0.0, limit: int = 5) -> list[tuple[str, float]]:
    items = []
    for key, value in (values or {}).items():
        try:
            numeric = float(value)
        except Exception:
            continue
        if numeric >= minimum:
            items.append((str(key), numeric))
    return sorted(items, key=lambda item: item[1], reverse=True)[:limit]


def _render_badges(items: list[str], *, empty_text: str = "None detected") -> None:
    clean = [str(item).strip() for item in items if str(item).strip()]
    if not clean:
        st.markdown(f"<span class='muted'>{empty_text}</span>", unsafe_allow_html=True)
        return
    html = "".join(f"<span class='badge'>{item}</span>" for item in clean)
    st.markdown(f"<div class='badge-row'>{html}</div>", unsafe_allow_html=True)


def _format_family_summary(family_df: pd.DataFrame) -> tuple[str, list[str]]:
    if family_df is None or len(family_df) == 0:
        return "No preferred family identified", []
    top_family = str(family_df.iloc[0]["Family"])
    alternatives = [str(v) for v in family_df["Family"].iloc[1:3].tolist()]
    return top_family, alternatives


def _factor_explanation(factor: str) -> str:
    explanations = {
        "creep": "resistance to long-duration deformation at temperature",
        "temperature": "fit to the stated operating temperature",
        "route_suitability": "fit with the preferred manufacturing route",
        "manufacturability": "practicality of producing a usable engineering alloy",
        "oxidation": "surface stability in hot oxidising conditions",
        "hot_corrosion": "resistance to salt or contaminant assisted attack",
        "wear": "surface damage resistance under sliding or contact",
        "erosion": "resistance to particle or flow-driven surface loss",
        "fatigue": "cyclic-load durability",
        "thermal_fatigue": "damage tolerance under thermal cycling",
        "lightweight": "density-sensitive strength-to-weight fit",
        "repairability": "practicality of inspection, repair, or replacement",
        "certification_maturity": "evidence maturity for aerospace use",
        "through_life_cost": "expected lifecycle cost pressure",
        "sustainability": "material burden and circularity pressure",
        "supply_risk": "critical-material and supply exposure",
        "recipe_support": "strength of route and analogue support",
        "evidence_maturity": "database and plausibility support",
    }
    return explanations.get(factor, "prompt-relevant engineering factor")


def _render_factor_cards(scope_plan: dict, *, limit: int = 7) -> None:
    weights = scope_plan.get("active_factor_weights", {}) or {}
    active = scope_plan.get("active_factor_set", []) or []
    rows = []
    for factor in active:
        rows.append((factor, float(weights.get(factor, 0.0) or 0.0)))
    rows = sorted(rows, key=lambda item: item[1], reverse=True)[:limit]
    if not rows:
        st.write("Default factor set will be used.")
        return

    for factor, weight in rows:
        label = FACTOR_LABELS.get(factor, _humanise_token(factor))
        priority = _priority_label(weight)
        st.markdown(
            f"""
            <div class="factor-card">
                <div>
                    <div class="factor-title">{label}</div>
                    <div class="muted">{_factor_explanation(factor)}</div>
                </div>
                <div class="priority-pill">{priority}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_family_cards(family_df: pd.DataFrame) -> None:
    if family_df is None or len(family_df) == 0:
        st.info("No material-family preference was identified. The baseline scope will remain broad.")
        return

    for idx, row in family_df.head(5).iterrows():
        family = str(row.get("Family", "Unknown family"))
        prior = float(row.get("Prior", 0.0) or 0.0)
        if idx == 0:
            status = "Primary search direction"
        elif prior >= 0.45:
            status = "Strong alternative"
        elif prior >= 0.25:
            status = "Keep in scope"
        else:
            status = "Low priority"
        rationale = str(row.get("Rationale", "") or "")
        rationale = rationale.split(".")[0].strip()
        if not rationale:
            rationale = "Included by the current aviation-metallic scope."
        st.markdown(
            f"""
            <div class="family-card">
                <div>
                    <div class="family-title">{family}</div>
                    <div class="muted">{rationale}.</div>
                </div>
                <div class="family-status">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_interpretation_review(requirements: dict):
    """Professional pre-retrieval review for engineering users."""
    schema = requirements.get("requirement_schema", {}) or {}
    scope_plan = requirements.get("scope_plan", {}) or {}
    operating = schema.get("operating_envelope", {}) or {}
    component = schema.get("component_context", {}) or {}
    manufacturing = schema.get("manufacturing_intent", {}) or {}
    lifecycle = schema.get("lifecycle_priorities", {}) or {}
    failure = schema.get("failure_mode_priorities", {}) or {}
    soft_objectives = schema.get("soft_objectives", {}) or {}

    family_df = _family_prior_table(scope_plan)
    top_family, alternatives = _format_family_summary(family_df)
    active_factors = scope_plan.get("active_factor_set", requirements.get("active_factor_set", [])) or []
    confidence = _confidence_label(schema.get("interpreter_confidence"))
    temperature = requirements.get("operating_temperature", operating.get("temperature_c", ""))
    temp_band = _humanise_token(operating.get("temperature_band", "unknown"))

    top_failure_items = _top_items(failure, minimum=0.15, limit=4)
    top_failure_labels = [f"{_humanise_token(name)} ({_priority_label(value)})" for name, value in top_failure_items]

    environment_labels = [_humanise_token(v) for v in operating.get("environment_tags", [])]
    loading_labels = [_humanise_token(v) for v in operating.get("load_regime_tags", [])]
    preferred_routes = [_humanise_token(v) for v in manufacturing.get("preferred_routes", [])]
    if requirements.get("am_preferred") and "Additive manufacturing" not in preferred_routes:
        preferred_routes.insert(0, "Additive manufacturing")

    st.markdown("## Review the interpreted design brief")
    st.markdown(
        """
        <div class="review-intro">
            The app has interpreted the engineering intent below. Please confirm this before material retrieval starts.
            This keeps you in the design loop and avoids ranking candidates against the wrong requirement set.
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_cols = st.columns(4)
    with summary_cols[0]:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Operating condition</div>
                <div class="summary-value">{temperature}°C</div>
                <div class="summary-note">{temp_band}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[1]:
        use_case = _humanise_token(component.get("component_class", "Aviation component"))
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Use case</div>
                <div class="summary-value small-value">{use_case}</div>
                <div class="summary-note">{_humanise_token(component.get('geometry_complexity', 'Geometry not specified'))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[2]:
        st.markdown(
            f"""
            <div class="summary-card primary-card">
                <div class="summary-label">Material direction</div>
                <div class="summary-value small-value">{top_family}</div>
                <div class="summary-note">Alternatives: {', '.join(alternatives) if alternatives else 'none highlighted'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[3]:
        route_text = ", ".join(preferred_routes) if preferred_routes else "Route not specified"
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-label">Manufacturing direction</div>
                <div class="summary-value small-value">{route_text}</div>
                <div class="summary-note">Interpretation confidence: {confidence}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Engineering interpretation")
    interpretation_cols = st.columns([1.15, 0.85])
    with interpretation_cols[0]:
        st.markdown('<div class="plain-card">', unsafe_allow_html=True)
        st.markdown("**What the app thinks you are asking for**")
        use_case_summary = component.get("use_case_summary", requirements.get("application_prompt", ""))
        st.write(use_case_summary)
        st.markdown("**Main design drivers**")
        _render_badges(top_failure_labels, empty_text="No dominant failure mode detected")
        st.markdown("**Environment and loading cues**")
        _render_badges(environment_labels + loading_labels, empty_text="No special environment or load cue detected")
        st.markdown('</div>', unsafe_allow_html=True)

    with interpretation_cols[1]:
        st.markdown('<div class="plain-card">', unsafe_allow_html=True)
        st.markdown("**Manufacturing and lifecycle cues**")
        manuf_bits = []
        if requirements.get("am_preferred"):
            manuf_bits.append("Additive manufacturing preferred")
        if manufacturing.get("qualification_sensitivity") and manufacturing.get("qualification_sensitivity") != "normal":
            manuf_bits.append(f"Qualification sensitivity: {_humanise_token(manufacturing.get('qualification_sensitivity'))}")
        if manufacturing.get("inspection_sensitivity") and manufacturing.get("inspection_sensitivity") != "normal":
            manuf_bits.append(f"Inspection sensitivity: {_humanise_token(manufacturing.get('inspection_sensitivity'))}")
        lifecycle_items = _top_items(lifecycle, minimum=0.15, limit=3)
        manuf_bits.extend([f"{_humanise_token(k)} considered" for k, _ in lifecycle_items])
        st.markdown(f"<ul class='compact-list'>{_html_list(manuf_bits, 'Default route and lifecycle assumptions')}</ul>", unsafe_allow_html=True)
        st.markdown("**Decision scenario**")
        st.write(requirements.get("downstream_profile_name", "Balanced"))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Planned material search")
    search_cols = st.columns([0.95, 1.05])
    with search_cols[0]:
        st.markdown("**Material families to prioritise**")
        _render_family_cards(family_df)
    with search_cols[1]:
        st.markdown("**What the ranking will care about most**")
        _render_factor_cards(scope_plan)

    with st.expander("Technical details for debugging"):
        tech_cols = st.columns(2)
        with tech_cols[0]:
            st.markdown("**Allowed families passed to the frozen baseline**")
            for family in requirements.get("allowed_material_families", []):
                st.markdown(f"- {family}")
            st.markdown("**Full active factor weights**")
            factor_df = _factor_weight_table(scope_plan)
            if len(factor_df):
                st.dataframe(factor_df, use_container_width=True, hide_index=True)
            else:
                st.write("No active factor weights were available.")
        with tech_cols[1]:
            retrieval_hints = scope_plan.get("retrieval_hints", {}) or {}
            st.markdown("**Retrieval policy**")
            st.write(retrieval_hints.get("expansion_policy", "Baseline generator controls retrieval."))
            notes = retrieval_hints.get("notes", []) or []
            if notes:
                st.markdown("**Retrieval notes**")
                for note in notes:
                    st.markdown(f"- {note}")
            st.markdown("**Interpreter / planner trace**")
            trace_items = (schema.get("interpreter_trace", []) or []) + (scope_plan.get("planner_trace", []) or [])
            if trace_items:
                for trace_item in trace_items:
                    st.markdown(f"- {trace_item}")
            else:
                st.write("No trace notes were available.")

    ambiguities = schema.get("ambiguities", []) or []
    warnings = scope_plan.get("scope_warnings", []) or []
    if ambiguities or warnings:
        st.markdown("### Check before continuing")
        for item in ambiguities:
            st.warning(item)
        for item in warnings:
            st.warning(item)

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

    scope_plan = requirements.get("scope_plan", {}) or {}
    active_factors = scope_plan.get("active_factor_set", requirements.get("active_factor_set", []))
    active_factor_labels = [FACTOR_LABELS.get(f, f.replace("_", " ").title()) for f in active_factors]

    return {
        "application": requirements["application_prompt"],
        "temperature": f"{requirements['operating_temperature']}°C",
        "am_preferred": "Yes" if requirements["am_preferred"] else "No",
        "allowed_families": ", ".join(requirements["allowed_material_families"]),
        "top_priorities": ", ".join(top_priorities),
        "notes": requirements["notes"],
        "decision_profile_name": requirements.get("downstream_profile_name", "Balanced"),
        "decision_profile_summary": requirements.get("downstream_profile", {}).get("summary", ""),
        "active_factors": active_factor_labels,
        "family_priors": scope_plan.get("family_priors", requirements.get("family_priors", {})),
    }


def make_display_table(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or len(df) == 0:
        return df

    out = df.copy()
    out = out.rename(
        columns={
            "candidate_id": "Candidate",
            "material_family": "Material family",
            "composition_concept": "Composition",
            "performance_summary_score": "Performance summary",
            "decision_summary_score": "Decision summary",
            "final_rank_score": "Final rank",
            "recipe_mode": "Recipe mode",
            "matched_alloy_name": "Analogue",
            "manufacturing_primary_route": "Primary route",
            "confidence": "Confidence",
            "strengths": "Strengths",
            "watch_outs": "Watch-outs",
        }
    )
    keep_cols = [
        "Candidate",
        "Material family",
        "Composition",
        "Performance summary",
        "Decision summary",
        "Final rank",
        "Recipe mode",
        "Analogue",
        "Primary route",
        "Confidence",
        "Strengths",
        "Watch-outs",
    ]
    existing = [col for col in keep_cols if col in out.columns]
    return out[existing]


def build_factor_breakdown(row: pd.Series) -> pd.DataFrame:
    recipe_expl = (
        f"{row.get('analogue_explanation', '')} | "
        f"Similarity={row.get('analogue_similarity_score', '')}, "
        f"Route={row.get('analogue_route_compatibility_score', '')}, "
        f"Mode={row.get('recipe_mode', '')}"
    )
    items = [
        {"Factor": "Creep suitability", "Score": row.get("creep_score"), "Explanation": row.get("creep_reason")},
        {"Factor": "Toughness proxy", "Score": row.get("toughness_score"), "Explanation": row.get("toughness_reason")},
        {"Factor": "Temperature suitability", "Score": row.get("temperature_score"), "Explanation": row.get("temperature_reason")},
        {"Factor": "Through-life cost", "Score": row.get("through_life_cost_score"), "Explanation": row.get("through_life_cost_reason")},
        {"Factor": "Sustainability", "Score": row.get("sustainability_score_v1"), "Explanation": row.get("sustainability_reason")},
        {"Factor": "Manufacturability", "Score": row.get("manufacturability_score"), "Explanation": row.get("manufacturability_reason")},
        {"Factor": "Preferred-route suitability", "Score": row.get("route_suitability_score"), "Explanation": row.get("route_suitability_reason")},
        {"Factor": "Supply-chain / critical-material risk", "Score": row.get("supply_risk_score"), "Explanation": row.get("supply_risk_reason")},
        {"Factor": "Evidence / maturity", "Score": row.get("evidence_maturity_score"), "Explanation": row.get("evidence_maturity_reason")},
        {"Factor": "Recipe support", "Score": row.get("recipe_support_score"), "Explanation": recipe_expl},
    ]
    # Append prompt-activated optional factors when present. Baseline/common factors above remain visible.
    try:
        active_factors = json.loads(row.get("active_factor_set", "[]"))
    except Exception:
        active_factors = []
    existing_labels = {item["Factor"] for item in items}
    for factor in active_factors:
        label = FACTOR_LABELS.get(factor, str(factor).replace("_", " ").title())
        if label in existing_labels:
            continue
        score_col = FACTOR_SCORE_COLUMNS.get(factor)
        reason_col = FACTOR_REASON_COLUMNS.get(factor)
        if score_col and score_col in row.index:
            items.append({"Factor": label, "Score": row.get(score_col), "Explanation": row.get(reason_col, "")})
    return pd.DataFrame(items)


def _json_to_df(value, *, empty_columns=None) -> pd.DataFrame:
    empty_columns = empty_columns or []
    if value is None:
        return pd.DataFrame(columns=empty_columns)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return pd.DataFrame(columns=empty_columns)
        try:
            parsed = json.loads(stripped)
        except Exception:
            return pd.DataFrame(columns=empty_columns)
    else:
        parsed = value
    if isinstance(parsed, dict):
        parsed = [parsed]
    if not isinstance(parsed, list):
        return pd.DataFrame(columns=empty_columns)
    if not parsed:
        return pd.DataFrame(columns=empty_columns)
    return pd.DataFrame(parsed)


def render_run_debug_summary(top: pd.DataFrame, requirements: dict, diagnostics: dict | None = None):
    with st.expander("Debug / sensitivity diagnostics"):
        scope_plan = requirements.get("scope_plan", {}) or {}
        req_cols = st.columns(5)
        req_cols[0].metric("Allowed families", len(requirements.get("allowed_material_families", [])))
        req_cols[1].metric("Active factors", len(scope_plan.get("active_factor_set", requirements.get("active_factor_set", []))))
        req_cols[2].metric("Profile", requirements.get("downstream_profile_name", "Balanced"))
        req_cols[3].metric("Top candidate count", len(top) if top is not None else 0)
        req_cols[4].metric(
            "Unique top recipe modes",
            len(set(top["recipe_mode"].astype(str).tolist())) if top is not None and "recipe_mode" in top.columns else 0,
        )

        if top is not None and len(top) > 0:
            summary_rows = [{
                "Metric": "Unique top families",
                "Value": len(set(top["material_family"].astype(str).tolist())) if "material_family" in top.columns else 0,
            },{
                "Metric": "Unique top analogues",
                "Value": len({str(v) for v in top.get("matched_alloy_name", pd.Series(dtype=str)).fillna("").tolist() if str(v).strip()}),
            },{
                "Metric": "Final-rank spread",
                "Value": round(float(top["final_rank_score"].max() - top["final_rank_score"].min()), 2) if "final_rank_score" in top.columns and len(top) > 1 else 0.0,
            },{
                "Metric": "Recipe-support spread",
                "Value": round(float(top["recipe_support_score"].max() - top["recipe_support_score"].min()), 2) if "recipe_support_score" in top.columns and len(top) > 1 else 0.0,
            }]
            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

            warning_flags = []
            if "material_family" in top.columns and len(set(top["material_family"].astype(str).tolist())) == 1:
                warning_flags.append("Top set is dominated by one family.")
            if "recipe_mode" in top.columns and len(set(top["recipe_mode"].astype(str).tolist())) == 1:
                warning_flags.append("Top set is using one recipe mode only.")
            if "final_rank_score" in top.columns and len(top) > 1 and float(top["final_rank_score"].max() - top["final_rank_score"].min()) < 3.0:
                warning_flags.append("Final-rank spread is narrow (<3).")
            if "recipe_support_score" in top.columns and len(top) > 1 and float(top["recipe_support_score"].max() - top["recipe_support_score"].min()) < 4.0:
                warning_flags.append("Recipe-support spread is narrow (<4).")

            if warning_flags:
                for item in warning_flags:
                    st.warning(item)
            else:
                st.success("No immediate flattening flags were detected in the top set.")

        if diagnostics:
            warnings = diagnostics.get("warnings", [])
            if warnings:
                st.write("**Baseline / retrieval warnings**")
                for item in warnings:
                    st.markdown(f"- {item}")


def _list_value(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        return [stripped]
    return [value]


def render_design_frame(requirements: dict):
    req_view = format_requirements(requirements)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Operating temperature", req_view["temperature"])
    col2.metric("AM preferred", req_view["am_preferred"])
    col3.metric("Candidate families", len(requirements["allowed_material_families"]))
    col4.metric("Decision scenario", req_view["decision_profile_name"])

    st.markdown("## Inferred design frame")
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
        st.markdown("**Downstream evaluation mode**")
        st.write(req_view["decision_profile_summary"])
        st.markdown("**Active prompt factors**")
        active_factors = req_view.get("active_factors", [])
        st.write(", ".join(active_factors[:8]) if active_factors else "Default factor set")
        st.markdown("</div>", unsafe_allow_html=True)

    schema = requirements.get("requirement_schema", {}) or {}
    scope_plan = requirements.get("scope_plan", {}) or {}
    with st.expander("Requirement schema and scope plan"):
        schema_col, scope_col = st.columns(2)
        with schema_col:
            st.write("**Interpreted operating envelope**")
            st.json(schema.get("operating_envelope", {}))
            st.write("**Failure-mode priorities**")
            st.json(schema.get("failure_mode_priorities", {}))
            if schema.get("ambiguities"):
                st.write("**Ambiguities**")
                for item in schema.get("ambiguities", []):
                    st.warning(item)
        with scope_col:
            st.write("**Family priors**")
            priors = scope_plan.get("family_priors", {})
            if priors:
                st.dataframe(
                    pd.DataFrame([{"Family": k, "Prior": v} for k, v in priors.items()]).sort_values("Prior", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                )
            st.write("**Active factor weights**")
            weights = scope_plan.get("active_factor_weights", {})
            if weights:
                st.dataframe(
                    pd.DataFrame([{"Factor": FACTOR_LABELS.get(k, k), "Weight": v} for k, v in weights.items()]).sort_values("Weight", ascending=False),
                    use_container_width=True,
                    hide_index=True,
                )


def render_empty_state(requirements: dict, candidates, scored, near_miss, diagnostics=None):
    render_design_frame(requirements)

    raw_count = len(candidates) if candidates is not None else 0
    scored_count = len(scored) if scored is not None else 0
    near_count = len(near_miss) if near_miss is not None else 0

    st.markdown("## What happened")
    st.write(
        f"- Raw retrieved candidates: **{raw_count}**\n"
        f"- Candidates after downstream evaluation: **{scored_count}**\n"
        f"- Near-feasible alternatives available: **{near_count}**"
    )

    if near_miss is not None and len(near_miss) > 0:
        st.markdown("## Near-feasible alternatives")
        near_cols = [
            c for c in [
                "candidate_id",
                "material_family",
                "overall_score",
                "confidence",
                "strengths",
                "watch_outs",
            ]
            if c in near_miss.columns
        ]
        near_display = near_miss[near_cols].rename(
            columns={
                "candidate_id": "Candidate",
                "material_family": "Material family",
                "overall_score": "Overall fit",
                "confidence": "Confidence",
                "strengths": "Strengths",
                "watch_outs": "Watch-outs",
            }
        )
        st.dataframe(near_display, use_container_width=True, hide_index=True)
    else:
        st.info("No near-feasible alternatives were identified.")

    if diagnostics:
        warnings = diagnostics.get("warnings", [])
        if warnings:
            st.markdown("## Screening warnings")
            for warning in warnings:
                st.warning(warning)

        with st.expander("Diagnostics"):
            st.write("**Baseline diagnostics**")
            st.write(diagnostics)
            st.write("**Requirement schema**")
            st.json(requirements.get("requirement_schema", {}))
            st.write("**Scope plan**")
            st.json(requirements.get("scope_plan", {}))


def render_recipe_block(row: pd.Series):
    st.write("**Manufacturing recipe mode**")
    st.write(f"{row.get('recipe_mode', 'family_envelope')}")

    top_cols = st.columns(3)
    top_cols[0].metric("Recipe support", f"{row.get('recipe_support_score', 0):.1f}")
    top_cols[1].metric("Recipe confidence", str(row.get("recipe_confidence", "Low")))
    top_cols[2].metric("Analogue confidence", str(row.get("analogue_confidence", "Low")))

    matched_name = str(row.get("matched_alloy_name", "") or "").strip()
    if matched_name:
        st.write(f"**Closest analogue:** {matched_name}")
    else:
        st.write("**Closest analogue:** none — using family-envelope fallback")

    primary_route = str(row.get("manufacturing_primary_route", "") or "").strip()
    secondary_route = str(row.get("manufacturing_secondary_route", "") or "").strip()
    if primary_route:
        st.write(f"**Primary route:** {primary_route}")
    if secondary_route:
        st.write(f"**Secondary route:** {secondary_route}")

    ingredients = row.get("ingredient_rows", [])
    if ingredients:
        st.write("**Ingredients / composition view**")
        st.dataframe(pd.DataFrame(ingredients), use_container_width=True, hide_index=True)

    steps = _list_value(row.get("process_steps"))
    if steps:
        st.write("**Recipe steps**")
        for idx, step in enumerate(steps, start=1):
            st.markdown(f"{idx}. {step}")

    why_route = _list_value(row.get("why_this_route"))
    if why_route:
        st.write("**Why this route**")
        for item in why_route:
            st.markdown(f"- {item}")

    watch_outs = _list_value(row.get("recipe_watch_outs"))
    if watch_outs:
        st.write("**Recipe watch-outs**")
        for item in watch_outs:
            st.markdown(f"- {item}")

    provenance_refs = _list_value(row.get("recipe_provenance_refs"))
    if provenance_refs:
        st.write("**Recipe provenance refs**")
        for item in provenance_refs:
            st.code(str(item))

    analogue_candidates_df = _json_to_df(
        row.get("top_analogue_candidates_json"),
        empty_columns=["alloy_id", "canonical_name", "weighted_score", "similarity_score", "route_compatibility_score"],
    )
    if len(analogue_candidates_df) > 0:
        st.write("**Top analogue candidates considered**")
        st.dataframe(analogue_candidates_df, use_container_width=True, hide_index=True)

    recipe_support_df = _json_to_df(
        row.get("recipe_support_breakdown_json"),
        empty_columns=[
            "analogue_confidence_component",
            "analogue_similarity_component",
            "route_match_component",
            "manufacturability_component",
            "route_suitability_component",
            "evidence_component",
            "alloy_likeness_component",
            "mode_adjustment",
            "stable_adjustment",
            "theoretical_adjustment",
        ],
    )
    if len(recipe_support_df) > 0:
        st.write("**Recipe-support component breakdown**")
        st.dataframe(recipe_support_df.T.reset_index().rename(columns={"index": "Component", 0: "Contribution"}), use_container_width=True, hide_index=True)


def render_candidate_detail_cards(top: pd.DataFrame):
    st.markdown("## Candidate breakdown")
    for i, (_, row) in enumerate(top.iterrows(), start=1):
        title = f"{i}. {row['candidate_id']} — {row['material_family']}"
        with st.expander(title, expanded=(i == 1)):
            summary_col1, summary_col2, summary_col3, summary_col4, summary_col5 = st.columns(5)
            summary_col1.metric("Performance summary", f"{row.get('performance_summary_score', 0):.1f}")
            summary_col2.metric("Decision summary", f"{row.get('decision_summary_score', 0):.1f}")
            summary_col3.metric("Evidence", f"{row.get('evidence_maturity_score', 0):.1f}")
            summary_col4.metric("Recipe support", f"{row.get('recipe_support_score', 0):.1f}")
            summary_col5.metric("Final rank", f"{row.get('final_rank_score', 0):.1f}")

            st.write(f"**Strengths:** {row.get('strengths', 'None surfaced')}")
            st.write(f"**Watch-outs:** {row.get('watch_outs', 'None surfaced')}")

            factor_breakdown = build_factor_breakdown(row)
            st.dataframe(factor_breakdown, use_container_width=True, hide_index=True)

            route_df = pd.DataFrame(
                [
                    {"Route": "AM route score", "Score": row.get("am_route_score")},
                    {"Route": "Conventional route score", "Score": row.get("conventional_route_score")},
                ]
            )
            st.write("**Route comparison**")
            st.dataframe(route_df, use_container_width=True, hide_index=True)

            st.write("---")
            render_recipe_block(row)

            warning = str(row.get("recipe_layer_warning", "") or "").strip()
            if warning:
                st.warning(warning)

            if "provenance" in row.index:
                st.write(f"**Provenance:** {row['provenance']}")
            st.write(f"**Rerank reason:** {row.get('rerank_reason', '')}")


def render_multidimensional_charts(top: pd.DataFrame):
    if top is None or len(top) == 0:
        return

    st.markdown("## Multidimensional comparison")

    parallel_dims = [
        "creep_score",
        "temperature_score",
        "through_life_cost_score",
        "sustainability_score_v1",
        "manufacturability_score",
        "route_suitability_score",
        "recipe_support_score",
        "evidence_maturity_score",
        "final_rank_score",
    ]
    parallel_dims = [c for c in parallel_dims if c in top.columns]

    if len(parallel_dims) >= 3:
        fig_parallel = go.Figure(
            data=go.Parcoords(
                line=dict(color=top["final_rank_score"], showscale=True),
                dimensions=[
                    dict(label=col.replace("_", " ").title(), values=top[col])
                    for col in parallel_dims
                ],
            )
        )
        fig_parallel.update_layout(margin=dict(l=30, r=30, t=40, b=20))
        st.plotly_chart(fig_parallel, use_container_width=True)
    else:
        st.info("Parallel coordinates unavailable for the current result set.")

    radar_metrics = [
        "creep_score",
        "temperature_score",
        "through_life_cost_score",
        "sustainability_score_v1",
        "manufacturability_score",
        "route_suitability_score",
        "recipe_support_score",
        "evidence_maturity_score",
    ]
    radar_metrics = [c for c in radar_metrics if c in top.columns]
    radar_df = top.head(3).copy()

    if len(radar_df) > 0 and len(radar_metrics) >= 3:
        fig_radar = go.Figure()
        theta = [metric.replace("_", " ").title() for metric in radar_metrics]
        theta_closed = theta + [theta[0]]
        for _, row in radar_df.iterrows():
            values = [float(row[m]) for m in radar_metrics]
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=values + [values[0]],
                    theta=theta_closed,
                    fill="toself",
                    name=str(row["candidate_id"]),
                )
            )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            margin=dict(l=30, r=30, t=40, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Radar chart unavailable for the current result set.")


def render_success_state(requirements: dict, top: pd.DataFrame, near_miss: pd.DataFrame | None, diagnostics=None):
    render_design_frame(requirements)

    st.markdown("## Ranked candidate concepts")
    display_table = make_display_table(top)
    st.dataframe(display_table, use_container_width=True, hide_index=True)
    render_run_debug_summary(top, requirements, diagnostics)

    if len(top) > 0:
        best = top.iloc[0]
        st.markdown("## Best overall concept")
        st.markdown('<div class="highlight-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            ### {best['candidate_id']} — {best['material_family']}

            **Composition concept:** {best['composition_concept']}

            **Recipe mode:** {best.get('recipe_mode', 'family_envelope')}

            **Closest analogue:** {best.get('matched_alloy_name', 'None')}

            **Primary manufacturing route:** {best.get('manufacturing_primary_route', best.get('base_process_route', 'Not available'))}

            **Why it ranks first:** it currently offers the strongest combined balance of
            prompt-specific active factors, performance summary, downstream decision factors, evidence/maturity, and recipe support.

            **Key strengths:** {best.get('strengths', 'None surfaced')}

            **Main watch-outs:** {best.get('watch_outs', 'None surfaced')}

            **Confidence:** {best['confidence']}
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("## Trade-off view")
        axis_options = {
            "Creep suitability": "creep_score",
            "Temperature suitability": "temperature_score",
            "Through-life cost": "through_life_cost_score",
            "Sustainability": "sustainability_score_v1",
            "Manufacturability": "manufacturability_score",
            "Route suitability": "route_suitability_score",
            "Recipe support": "recipe_support_score",
            "Evidence / maturity": "evidence_maturity_score",
            "Overall fit": "overall_score",
        }
        chart_x_label = st.selectbox("X-axis", options=list(axis_options.keys()), index=2, key="tradeoff_x_axis")
        chart_y_label = st.selectbox("Y-axis", options=list(axis_options.keys()), index=6, key="tradeoff_y_axis")
        x_col = axis_options[chart_x_label]
        y_col = axis_options[chart_y_label]

        required_chart_cols = {"candidate_id", "material_family", x_col, y_col, "final_rank_score"}
        if required_chart_cols.issubset(set(top.columns)) and len(top) > 0:
            chart_df = top.copy()
            chart_df["label"] = chart_df["candidate_id"] + " | " + chart_df["material_family"]
            fig = px.scatter(
                chart_df,
                x=x_col,
                y=y_col,
                size="final_rank_score",
                text="candidate_id",
                hover_name="label",
                title=f"{chart_x_label} vs {chart_y_label}",
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Trade-off chart unavailable for the current result set.")

    with right:
        st.markdown("## Near-feasible alternatives")
        if near_miss is not None and len(near_miss) > 0:
            near_cols = [
                c for c in [
                    "candidate_id",
                    "material_family",
                    "overall_score",
                    "recipe_mode",
                    "matched_alloy_name",
                    "confidence",
                    "strengths",
                    "watch_outs",
                ]
                if c in near_miss.columns
            ]
            near_display = near_miss[near_cols].rename(
                columns={
                    "candidate_id": "Candidate",
                    "material_family": "Material family",
                    "overall_score": "Overall fit",
                    "recipe_mode": "Recipe mode",
                    "matched_alloy_name": "Analogue",
                    "confidence": "Confidence",
                    "strengths": "Strengths",
                    "watch_outs": "Watch-outs",
                }
            )
            st.dataframe(near_display, use_container_width=True, hide_index=True)
            st.caption("These concepts do not rank highest overall, but remain interesting trade-off options.")
        else:
            st.write("No near-feasible alternatives were identified in the current screened set.")

    render_multidimensional_charts(top)
    render_candidate_detail_cards(top)

    with st.expander("Method, provenance, and disclaimer"):
        st.markdown("**How this prototype currently works**")
        st.markdown(
            """
            - infers design priorities from the application prompt and temperature  
            - retrieves baseline candidates from Materials Project  
            - preserves baseline survival inside the frozen candidate-generation layer  
            - adds an explicit downstream evaluation layer for cost, sustainability, manufacturability, route fit, and evidence  
            - attaches a deterministic manufacturing-recipe layer using analogue matches where confidence is high and family-envelope fallback where it is not  
            - reranks already-plausible survivors without turning reranking into a survival filter
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
            st.write("**Baseline diagnostics**")
            st.write(diagnostics)
            st.write("**Requirement schema**")
            st.json(requirements.get("requirement_schema", {}))
            st.write("**Scope plan**")
            st.json(requirements.get("scope_plan", {}))


def run_pipeline_from_requirements(requirements: dict):
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
            "message": "Candidates were retrieved, but none survived downstream evaluation.",
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
            "message": "Candidates were retrieved, but none survived the current ranking thresholds.",
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


def run_pipeline_once(application_prompt, operating_temperature, am_preferred, scenario_profile):
    requirements = infer_requirements(application_prompt, operating_temperature, am_preferred)
    requirements = apply_decision_profile(requirements, scenario_profile)
    return run_pipeline_from_requirements(requirements)


def interpret_prompt_for_review(application_prompt, operating_temperature, am_preferred, scenario_profile):
    requirements = infer_requirements(application_prompt, operating_temperature, am_preferred)
    return apply_decision_profile(requirements, scenario_profile)


generate_clicked = st.button("Generate concepts", type="primary", use_container_width=False)
current_signature = _input_signature(application_prompt, operating_temperature, am_preferred, scenario_profile)

if generate_clicked:
    try:
        with st.spinner("Interpreting design intent..."):
            interpreted_requirements = interpret_prompt_for_review(
                application_prompt,
                operating_temperature,
                am_preferred,
                scenario_profile,
            )
        st.session_state["pending_interpretation"] = {
            "requirements": interpreted_requirements,
            "input_signature": current_signature,
        }
        st.session_state["last_run"] = None
        st.session_state["last_error"] = None
    except Exception as exc:
        st.session_state["pending_interpretation"] = None
        st.session_state["last_run"] = None
        st.session_state["last_error"] = {
            "message": "The backend encountered an error while interpreting the prompt.",
            "error_detail": str(exc),
        }

pending = st.session_state.get("pending_interpretation")
if pending is not None:
    pending_signature = pending.get("input_signature", {})
    if not _same_signature(pending_signature, current_signature):
        st.warning(
            "The inputs have changed since the interpretation below was created. Press Generate concepts again to review the updated interpretation."
        )
        if st.button("Clear old interpretation", use_container_width=False):
            st.session_state["pending_interpretation"] = None
    else:
        render_interpretation_review(pending["requirements"])

        action_col1, action_col2 = st.columns([1, 1])
        with action_col1:
            confirm_clicked = st.button(
                "Confirm interpretation and retrieve candidates",
                type="primary",
                use_container_width=True,
            )
        with action_col2:
            revise_clicked = st.button(
                "Revise prompt or inputs",
                use_container_width=True,
            )

        if revise_clicked:
            st.session_state["pending_interpretation"] = None
            st.info("Update the prompt or sidebar inputs, then press Generate concepts again.")

        if confirm_clicked:
            try:
                with st.spinner("Retrieving and ranking candidate concepts..."):
                    result = run_pipeline_from_requirements(pending["requirements"])
                result["input_signature"] = pending_signature
                st.session_state["last_run"] = result
                st.session_state["pending_interpretation"] = None
                st.session_state["last_error"] = None
            except Exception as exc:
                st.session_state["last_run"] = {
                    "status": "error",
                    "message": "The backend encountered an error while retrieving or ranking concepts.",
                    "error_detail": str(exc),
                    "requirements": pending.get("requirements", {}),
                }
                st.session_state["pending_interpretation"] = None

last_error = st.session_state.get("last_error")
if last_error:
    st.error(last_error["message"])
    if last_error.get("error_detail"):
        with st.expander("Technical detail"):
            st.code(last_error["error_detail"])

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
elif pending is None and not last_error:
    st.markdown("## How to use this prototype")
    st.markdown(
        """
        1. Enter the application need in plain language.  
        2. Set the operating temperature and process preference.  
        3. Choose the downstream decision scenario.  
        4. Click **Generate concepts** to review the interpreted design intent.  
        5. If the interpretation looks right, click **Looks right — retrieve and rank candidates**.  
        6. Review the ranking table, recipe mode, trade-off chart, multidimensional charts, and detailed recipe cards.
        """
    )

    st.markdown("## Recommended demo prompt")
    st.code(
        "Design a material for a hot aviation component operating at 850°C "
        "where creep is critical and additive manufacturing is preferred."
    )
