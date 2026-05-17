from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from src.decision_language import (
    display_value,
    glossary_rows,
    status_label,
    term_label,
    tooltip_text,
)
from src.phase5_cockpit_review_export import (
    build_cockpit_review_export_package_from_view_model,
)
from src.phase5_decision_cockpit_view_models import (
    run_phase5_decision_cockpit_view_model,
)
from src.phase5_feedback_records import build_feedback_record_package_from_export_package
from src.phase5_specialist_model_adapters import (
    run_disabled_specialist_adapter_contract_review,
)


FORBIDDEN_DECISION_FIELDS: tuple[str, ...] = (
    "score",
    "rank",
    "winner",
    "certification_approval",
    "qualification_approval",
)


def build_demo_candidates() -> list[dict]:
    return [
        {
            "candidate_id": "demo_ni_tbc_reference",
            "system_name": "Ni superalloy + TBC reference",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED", "route_family": "additive_manufacturing"},
            "limiting_factors": ["thermal_gradient", "coating_spallation", "oxidation"],
        },
        {
            "candidate_id": "demo_sic_cmc_ebc_option",
            "system_name": "SiC/SiC CMC + EBC option",
            "candidate_class": "cmc",
            "substrate_family": "sic_sic_cmc",
            "process_route": {"route_name": "CVI", "route_family": "ceramic_composite"},
            "limiting_factors": ["oxidation", "recession", "inspection_repair"],
        },
        {
            "candidate_id": "demo_spatially_graded_am_surface",
            "system_name": "Spatially graded AM surface concept",
            "candidate_class": "metallic",
            "substrate_family": "nickel_alloy",
            "process_route": {"route_name": "DED", "route_family": "additive_manufacturing"},
            "limiting_factors": ["wear", "transition_zone_integrity", "manufacturability"],
        },
        {
            "candidate_id": "demo_refractory_oxidation_protection",
            "system_name": "Refractory alloy + oxidation protection concept",
            "candidate_class": "refractory",
            "substrate_family": "refractory_alloy",
            "process_route": {"route_name": "DED", "route_family": "additive_manufacturing"},
            "limiting_factors": ["high_temperature_oxidation", "oxidation", "evidence_maturity"],
        },
    ]


def build_demo_limiting_factors_by_candidate() -> dict[str, list[str]]:
    return {
        "demo_ni_tbc_reference": [
            "high_temperature_oxidation",
            "thermal_gradient",
            "coating_spallation",
            "inspection_repair",
        ],
        "demo_sic_cmc_ebc_option": [
            "high_temperature_oxidation",
            "coating_spallation",
            "inspection_repair",
            "evidence_maturity",
        ],
        "demo_spatially_graded_am_surface": [
            "manufacturability",
            "transition_zone_integrity",
            "wear",
            "inspection_repair",
        ],
        "demo_refractory_oxidation_protection": [
            "high_temperature_oxidation",
            "oxidation",
            "thermal_gradient",
            "evidence_maturity",
        ],
    }


def build_demo_cockpit_view_model(
    *,
    research_mode_enabled: bool = False,
) -> dict:
    return run_phase5_decision_cockpit_view_model(
        build_demo_candidates(),
        limiting_factors_by_candidate=build_demo_limiting_factors_by_candidate(),
        research_mode_enabled=research_mode_enabled,
    )


def build_demo_review_export_package(
    *,
    research_mode_enabled: bool = False,
) -> dict:
    view_model = build_demo_cockpit_view_model(
        research_mode_enabled=research_mode_enabled,
    )
    return build_cockpit_review_export_package_from_view_model(view_model)


def build_demo_feedback_package(
    *,
    research_mode_enabled: bool = False,
) -> dict:
    export_package = build_demo_review_export_package(
        research_mode_enabled=research_mode_enabled,
    )
    return build_feedback_record_package_from_export_package(export_package)


def build_demo_adapter_contract_review() -> dict:
    return run_disabled_specialist_adapter_contract_review()


def flatten_chart_data(chart: dict) -> list[dict]:
    rows = chart.get("data") if isinstance(chart, Mapping) else None
    if not isinstance(rows, list):
        return []
    flattened: list[dict] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        flattened.append(
            {
                "label": str(row.get("label", "")),
                "value": row.get("value", 0),
            }
        )
    return flattened


def find_metric(metrics: list[dict], metric_id: str, default: str = "0") -> str:
    for metric in metrics:
        if isinstance(metric, Mapping) and metric.get("metric_id") == metric_id:
            return str(metric.get("value", default))
    return default


def short_label(value: object, *, max_length: int = 28) -> str:
    text = str(value).replace("_", " ").strip()
    if text:
        text = text[0].upper() + text[1:]
    if max_length >= 0 and len(text) > max_length:
        return f"{text[:max_length]}..."
    return text


def badge_tone_class(tone: str) -> str:
    return {
        "positive": "badge-positive",
        "neutral": "badge-neutral",
        "caution": "badge-caution",
        "high_caution": "badge-high-caution",
        "info": "badge-info",
    }.get(tone, "badge-info")


def priority_tone(priority: str) -> str:
    return {
        "high": "high_caution",
        "medium": "caution",
        "low": "neutral",
    }.get(priority, "info")


def _mapping_rows(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [dict(row) for row in value if isinstance(row, Mapping)]
    return []


def _metric_value(metrics: list[dict], metric_id: str) -> int:
    value = find_metric(metrics, metric_id)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _yes_no(value: object) -> str:
    return "Yes" if value is True else "No"


def _boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return False


def display_field_value(field_name: str, value: object) -> str:
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        value = value.strip().lower() == "true"
    return display_value(field_name, value)


def build_metric_card_models(view_model: dict) -> list[dict]:
    cards: list[dict] = []
    for metric in _mapping_rows(view_model.get("overview_metrics")):
        metric_id = str(metric.get("metric_id", ""))
        cards.append(
            {
                "metric_id": metric_id,
                "label": str(metric.get("label", "")),
                "value": display_field_value(metric_id, metric.get("value", "")),
                "tone": str(metric.get("tone", "info")),
                "help_text": str(metric.get("help_text", "")),
            }
        )
    return cards


def build_candidate_board_cards(view_model: dict) -> list[dict]:
    board_cards: list[dict] = []
    for card in _mapping_rows(view_model.get("cards")):
        metrics = _mapping_rows(card.get("metrics"))
        research_mode_exposure = _boolish(card.get("research_mode_exposure"))
        board_cards.append(
            {
                "candidate_id": str(card.get("candidate_id", "")),
                "system_name": str(card.get("system_name", "")),
                "tier_label": str(card.get("tier_label", "")),
                "frontier_status": status_label(card.get("frontier_status", "")),
                "evidence_band": display_field_value(
                    "evidence_maturity", card.get("evidence_band", "")
                ),
                "plan_status": status_label(card.get("plan_status", "")),
                "validation_need_count": _metric_value(metrics, "validation_need_count"),
                "high_priority_need_count": _metric_value(metrics, "high_priority_need_count"),
                "medium_priority_need_count": _metric_value(metrics, "medium_priority_need_count"),
                "low_priority_need_count": _metric_value(metrics, "low_priority_need_count"),
                "research_mode_exposure": research_mode_exposure,
                "research_mode_exposure_label": display_field_value(
                    "research_mode_exposure", research_mode_exposure
                ),
                "badges": [
                    str(badge.get("label", ""))
                    for badge in _mapping_rows(card.get("badges"))
                    if str(badge.get("label", ""))
                ],
                "top_review_actions": [str(action) for action in card.get("review_actions", [])[:3]],
                "caution_summary": [str(caution) for caution in card.get("caution_summary", [])[:3]],
            }
        )
    return board_cards


def build_candidate_comparison_matrix(view_model: dict) -> list[dict]:
    rows: list[dict] = []
    for card in build_candidate_board_cards(view_model):
        rows.append(
            {
                "Candidate": card["system_name"],
                "Tier": card["tier_label"],
                "Trade-off boundary": card["frontier_status"],
                "Evidence maturity": card["evidence_band"],
                term_label("validation_needs"): card["validation_need_count"],
                "High priority": card["high_priority_need_count"],
                "Research-mode exposure": card["research_mode_exposure_label"],
            }
        )
    return rows


def build_validation_burden_rows(view_model: dict) -> list[dict]:
    rows: list[dict] = []
    for card in build_candidate_board_cards(view_model):
        high = int(card["high_priority_need_count"])
        medium = int(card["medium_priority_need_count"])
        low = int(card["low_priority_need_count"])
        rows.append(
            {
                "Candidate": card["system_name"],
                "High": high,
                "Medium": medium,
                "Low": low,
                "Total": high + medium + low,
            }
        )
    return rows


def build_chart_display_models(view_model: dict) -> list[dict]:
    chart_models: list[dict] = []
    for chart in _mapping_rows(view_model.get("charts")):
        chart_models.append(
            {
                "chart_id": str(chart.get("chart_id", "")),
                "title": str(chart.get("title", chart.get("chart_id", "Chart"))),
                "rows": [
                    {
                        "label": short_label(status_label(row.get("label", ""))),
                        "value": row.get("value", 0),
                    }
                    for row in flatten_chart_data(chart)
                ],
            }
        )
    return chart_models


def build_review_export_summary(export_package: dict) -> dict:
    manifest = export_package.get("manifest", {})
    if not isinstance(manifest, Mapping):
        manifest = {}
    return {
        "export_type": str(manifest.get("export_type", "")),
        "schema_version": str(manifest.get("schema_version", "")),
        "candidate_count": int(manifest.get("candidate_count", 0)),
        "card_count": int(manifest.get("card_count", 0)),
        "chart_count": int(manifest.get("chart_count", 0)),
        "limitation_count": len(manifest.get("limitations", []))
        if isinstance(manifest.get("limitations"), list)
        else 0,
        "warning_count": len(manifest.get("warnings", []))
        if isinstance(manifest.get("warnings"), list)
        else 0,
    }


def build_feedback_summary_rows(feedback_package: dict) -> list[dict]:
    rows: list[dict] = []
    for summary in _mapping_rows(feedback_package.get("feedback_summaries")):
        records = _mapping_rows(summary.get("feedback_records"))
        rows.append(
            {
                "Candidate": str(summary.get("system_name", "")),
                "Feedback records": int(summary.get("feedback_count", len(records))),
                "Follow-up required": display_field_value(
                    "follow_up_required", bool(summary.get("follow_up_count", 0))
                ),
                "Review state": short_label(summary.get("review_state", "")),
                "Draft template count": len(records),
            }
        )
    return rows


def build_adapter_summary_rows(adapter_review: dict) -> list[dict]:
    registry = adapter_review.get("registry", {})
    adapters = registry.get("adapters", []) if isinstance(registry, Mapping) else []
    rows: list[dict] = []
    for adapter in _mapping_rows(adapters):
        rows.append(
            {
                "Adapter": str(adapter.get("adapter_label", adapter.get("adapter_id", ""))),
                "Model family": short_label(adapter.get("model_family", "")),
                "Tasks": ", ".join(short_label(task) for task in adapter.get("supported_tasks", [])),
                "Status": short_label(adapter.get("adapter_status", "")),
                "Live calls": display_field_value(
                    "live_calls_enabled", adapter.get("live_calls_enabled")
                ),
                "Generated candidates allowed": display_field_value(
                    "generated_candidates_allowed",
                    adapter.get("generated_candidates_allowed"),
                ),
                "Mature evidence allowed": display_field_value(
                    "mature_evidence_allowed", adapter.get("mature_evidence_allowed")
                ),
            }
        )
    return rows


def cockpit_glossary_rows() -> list[dict]:
    return glossary_rows(
        [
            "frontier",
            "validation_needs",
            "validation_burden",
            "evidence_maturity",
            "recommendation_tier",
            "criterion_value",
            "confidence",
            "uncertainty",
            "model_supported_estimate",
            "optimisation_iteration",
            "measurement_feedback",
        ]
    )


def css_styles() -> str:
    return """
<style>
.cockpit-card {
  border: 1px solid #d8dee8;
  border-radius: 8px;
  padding: 1rem;
  margin: 0.35rem 0 1rem 0;
  background: #ffffff;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.05);
}
.metric-card {
  min-height: 8.5rem;
}
.candidate-card {
  min-height: 20rem;
}
.candidate-card h3, .metric-card h3 {
  margin: 0 0 0.4rem 0;
  line-height: 1.25;
}
.badge {
  display: inline-block;
  border-radius: 999px;
  padding: 0.15rem 0.5rem;
  margin: 0.1rem 0.2rem 0.1rem 0;
  font-size: 0.78rem;
  font-weight: 650;
}
.badge-positive { background: #e6f4ea; color: #137333; }
.badge-neutral { background: #eef2f7; color: #344054; }
.badge-caution { background: #fff4d6; color: #8a5a00; }
.badge-high-caution { background: #fde7e9; color: #b42318; }
.badge-info { background: #e8f1ff; color: #175cd3; }
.safety-box {
  border-left: 5px solid #175cd3;
  background: #f3f7ff;
  padding: 0.9rem 1rem;
  margin: 0.75rem 0 1.2rem 0;
  border-radius: 6px;
  color: #1d2939;
}
.muted-text {
  color: #667085;
  font-size: 0.9rem;
}
.section-header {
  margin-top: 1.25rem;
  margin-bottom: 0.35rem;
  font-weight: 700;
  color: #101828;
}
ul.compact-list {
  margin-top: 0.25rem;
  padding-left: 1.1rem;
}
</style>
"""


def _escape_html(value: object) -> str:
    return str(value).replace("<", "&lt;").replace(">", "&gt;")


def render_badges_html(labels: list[str], *, tone: str = "info") -> str:
    css_class = badge_tone_class(tone)
    return "".join(
        f'<span class="badge {css_class}">{_escape_html(label)}</span>'
        for label in labels
    )


def _list_html(values: Sequence[str]) -> str:
    if not values:
        return '<p class="muted-text">None listed</p>'
    items = "".join(f"<li>{_escape_html(value)}</li>" for value in values)
    return f'<ul class="compact-list">{items}</ul>'


def build_candidate_card_html(card_model: dict) -> str:
    counts = (
        f'{card_model.get("validation_need_count", 0)} total | '
        f'{card_model.get("high_priority_need_count", 0)} high | '
        f'{card_model.get("medium_priority_need_count", 0)} medium | '
        f'{card_model.get("low_priority_need_count", 0)} low'
    )
    return f"""
<div class="cockpit-card candidate-card">
  <h3>{_escape_html(card_model.get("system_name", ""))}</h3>
  {render_badges_html([str(card_model.get("tier_label", ""))], tone="positive")}
  {render_badges_html(card_model.get("badges", [])[:3], tone="info")}
  <p class="muted-text">
    Trade-off boundary: {_escape_html(card_model.get("frontier_status", ""))} |
    Evidence maturity: {_escape_html(card_model.get("evidence_band", ""))} |
    Evidence/review plan: {_escape_html(card_model.get("plan_status", ""))}
  </p>
  <p class="muted-text">
    Research-mode exposure: {_escape_html(card_model.get("research_mode_exposure_label", ""))}
  </p>
  <p><strong>Evidence still needed:</strong> {_escape_html(counts)}</p>
  <div class="section-header">Review actions</div>
  {_list_html(card_model.get("top_review_actions", []))}
  <div class="section-header">Caution summary</div>
  {_list_html(card_model.get("caution_summary", []))}
  <p class="muted-text"><strong>Decision-support only</strong></p>
</div>
"""


def build_metric_card_html(metric: dict) -> str:
    tone_class = badge_tone_class(str(metric.get("tone", "info")))
    return f"""
<div class="cockpit-card metric-card">
  <span class="badge {tone_class}">{_escape_html(metric.get("metric_id", ""))}</span>
  <h3>{_escape_html(metric.get("value", ""))}</h3>
  <p><strong>{_escape_html(metric.get("label", ""))}</strong></p>
  <p class="muted-text">{_escape_html(metric.get("help_text", ""))}</p>
</div>
"""


def collect_forbidden_decision_fields(value: object) -> list[str]:
    hits: list[str] = []

    def visit(item: object, path: str) -> None:
        if isinstance(item, Mapping):
            for key, nested in item.items():
                key_text = str(key)
                next_path = f"{path}.{key_text}"
                if key_text in FORBIDDEN_DECISION_FIELDS:
                    hits.append(next_path)
                visit(nested, next_path)
        elif isinstance(item, list):
            for index, nested in enumerate(item):
                visit(nested, f"{path}[{index}]")

    visit(value, "root")
    return hits


def view_model_has_no_forbidden_decision_fields(view_model: dict) -> bool:
    return collect_forbidden_decision_fields(view_model) == []


def build_candidate_card_display_rows(card: dict) -> list[dict]:
    metrics = card.get("metrics") if isinstance(card.get("metrics"), list) else []
    research_mode_exposure = _boolish(card.get("research_mode_exposure"))
    return [
        {"field": "Candidate ID", "value": str(card.get("candidate_id", ""))},
        {"field": "System name", "value": str(card.get("system_name", ""))},
        {"field": term_label("recommendation_tier"), "value": str(card.get("tier_label", ""))},
        {"field": "Trade-off boundary", "value": status_label(card.get("frontier_status", ""))},
        {
            "field": term_label("evidence_maturity"),
            "value": display_field_value("evidence_maturity", card.get("evidence_band", "")),
        },
        {"field": "Evidence/review plan", "value": status_label(card.get("plan_status", ""))},
        {
            "field": term_label("validation_needs"),
            "value": find_metric(metrics, "validation_need_count"),
        },
        {
            "field": "Research-mode exposure",
            "value": display_field_value("research_mode_exposure", research_mode_exposure),
        },
    ]


def prototype_safety_notes() -> list[str]:
    return [
        "Prototype viewer only.",
        "No final recommendation is made.",
        "No ranking or winner selection is provided.",
        "No qualification approval is implied.",
        "No certification approval is implied.",
        "Engineering review is required before use.",
    ]


def _table_rows(value: Any) -> list[dict]:
    if isinstance(value, list):
        return [dict(row) for row in value if isinstance(row, Mapping)]
    return []


def _show_bullets(st: Any, title: str, values: Sequence[str]) -> None:
    st.write(title)
    if values:
        for value in values:
            st.write(f"- {value}")
    else:
        st.write("- None")


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="Phase 6.2 Decision Cockpit Prototype", layout="wide")
    st.markdown(css_styles(), unsafe_allow_html=True)
    st.title("Material-System Decision Cockpit")
    st.caption("Standalone Phase 6 prototype using Phase 5 decision-support outputs")
    st.markdown(
        """
<div class="safety-box">
Prototype viewer only. No final recommendation is made. No ranking or winner
selection is provided. No qualification approval is implied. No certification
approval is implied. Engineering review is required before use.
</div>
""",
        unsafe_allow_html=True,
    )

    research_mode_enabled = st.sidebar.checkbox("Enable research-mode view", value=False)
    st.sidebar.caption(
        "Research mode remains gated and does not enable live specialist-model calls."
    )

    view_model = build_demo_cockpit_view_model(
        research_mode_enabled=research_mode_enabled,
    )
    export_package = build_cockpit_review_export_package_from_view_model(view_model)
    feedback_package = build_feedback_record_package_from_export_package(export_package)
    adapter_review = build_demo_adapter_contract_review()

    tabs = st.tabs(
        [
            "Cockpit overview",
            "Candidate options",
            "Trade-off evidence",
            "Candidate drilldown",
            "Review package",
            "Feedback",
            "Specialist adapters",
        ]
    )

    with tabs[0]:
        st.subheader("Cockpit overview")
        metric_columns = st.columns(3)
        for index, metric in enumerate(build_metric_card_models(view_model)):
            with metric_columns[index % 3]:
                st.markdown(build_metric_card_html(metric), unsafe_allow_html=True)

        st.markdown(
            '<div class="section-header">Candidate comparison</div>',
            unsafe_allow_html=True,
        )
        st.caption(tooltip_text("frontier"))
        st.caption(tooltip_text("criterion_value"))
        st.caption(tooltip_text("model_supported_estimate"))
        st.table(build_candidate_comparison_matrix(view_model))

        with st.expander("Guide to cockpit terms", expanded=False):
            st.table(cockpit_glossary_rows())

        with st.expander("Safety notes", expanded=False):
            _show_bullets(st, "Prototype boundaries", prototype_safety_notes())
            _show_bullets(st, "Global notes", view_model.get("global_notes", []))
            _show_bullets(st, "Global warnings", view_model.get("global_warnings", []))

    with tabs[1]:
        st.subheader("Candidate options")
        columns = st.columns(2)
        for index, card_model in enumerate(build_candidate_board_cards(view_model)):
            with columns[index % 2]:
                st.markdown(build_candidate_card_html(card_model), unsafe_allow_html=True)

    with tabs[2]:
        st.subheader("Trade-off evidence")
        validation_rows = build_validation_burden_rows(view_model)
        st.markdown(
            '<div class="section-header">Evidence and review effort by candidate</div>',
            unsafe_allow_html=True,
        )
        st.caption(tooltip_text("validation_burden"))
        st.table(validation_rows)
        if validation_rows:
            st.bar_chart(validation_rows, x="Candidate", y=["High", "Medium", "Low"])

        for chart_model in build_chart_display_models(view_model):
            st.markdown(
                f'<div class="section-header">{_escape_html(chart_model["title"])}</div>',
                unsafe_allow_html=True,
            )
            rows = chart_model["rows"]
            st.table(rows)
            if rows:
                st.bar_chart(rows, x="label", y="value")

    with tabs[3]:
        st.subheader("Candidate drilldown")
        cards = _table_rows(view_model.get("cards"))
        names = [
            str(card.get("system_name", card.get("candidate_id", "Candidate")))
            for card in cards
        ]
        selected_name = st.selectbox("Candidate", names)
        selected_card = cards[names.index(selected_name)] if selected_name in names else {}
        selected_board_card = build_candidate_board_cards({"cards": [selected_card]})[0]

        st.markdown(build_candidate_card_html(selected_board_card), unsafe_allow_html=True)
        st.markdown(
            '<div class="section-header">Card fields</div>',
            unsafe_allow_html=True,
        )
        st.table(build_candidate_card_display_rows(selected_card))
        st.markdown('<div class="section-header">Badges</div>', unsafe_allow_html=True)
        st.markdown(
            render_badges_html(selected_board_card.get("badges", []), tone="info"),
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-header">Metrics</div>', unsafe_allow_html=True)
        st.table(
            [
                {
                    "Metric": metric.get("label", ""),
                    "Value": metric.get("value", ""),
                    "Tone": short_label(metric.get("tone", "")),
                    "Help": metric.get("help_text", ""),
                }
                for metric in _table_rows(selected_card.get("metrics"))
            ]
        )
        st.markdown(
            '<div class="section-header">Priority validation needs</div>',
            unsafe_allow_html=True,
        )
        st.table(
            [
                {
                    "Priority": short_label(need.get("priority", "")),
                    "Category": short_label(need.get("category", "")),
                    "Activity": need.get("validation_activity", ""),
                    "Status": short_label(need.get("status", "")),
                }
                for need in _table_rows(selected_card.get("priority_validation_needs"))
            ]
        )
        _show_bullets(st, "Review actions", selected_card.get("review_actions", []))
        _show_bullets(st, "Caution summary", selected_card.get("caution_summary", []))

        for section in _table_rows(selected_card.get("detail_sections")):
            with st.expander(str(section.get("title", "Detail section")), expanded=False):
                st.table(_table_rows(section.get("rows")))

    with tabs[4]:
        st.subheader("Review package")
        st.markdown(
            '<div class="section-header">Compact export summary</div>',
            unsafe_allow_html=True,
        )
        st.table([build_review_export_summary(export_package)])
        st.markdown(
            '<div class="section-header">Candidate summaries</div>',
            unsafe_allow_html=True,
        )
        st.table(
            [
                {
                    "Candidate ID": summary.get("candidate_id", ""),
                    "System name": summary.get("system_name", ""),
                    term_label("recommendation_tier"): summary.get("tier_label", ""),
                    "Trade-off boundary": status_label(
                        summary.get("frontier_status", "")
                    ),
                    term_label("evidence_maturity"): display_field_value(
                        "evidence_maturity", summary.get("evidence_band", "")
                    ),
                    "Evidence/review plan": status_label(
                        summary.get("plan_status", "")
                    ),
                    term_label("validation_needs"): summary.get(
                        "validation_need_count", 0
                    ),
                }
                for summary in _table_rows(export_package.get("candidate_summaries"))
            ]
        )
        with st.expander("Markdown report", expanded=False):
            st.code(str(export_package.get("markdown_report", "")), language="markdown")

    with tabs[5]:
        st.subheader("Feedback")
        st.table(build_feedback_summary_rows(feedback_package))
        st.caption("Draft records are templates only and do not modify analysis outputs.")
        for summary in _table_rows(feedback_package.get("feedback_summaries")):
            label = str(summary.get("system_name", summary.get("candidate_id", "Candidate")))
            with st.expander(f"{label} draft templates", expanded=False):
                st.caption("Templates only. They do not alter the analysis output.")
                st.table(
                    [
                        {
                            "Feedback type": short_label(record.get("feedback_type", "")),
                            "Review state": short_label(record.get("record_status", "")),
                            "Follow-up required": display_field_value(
                                "follow_up_required",
                                record.get("follow_up_required"),
                            ),
                            "Decision position": short_label(
                                record.get("decision_position", "")
                            ),
                            "Warnings": "; ".join(record.get("warnings", [])),
                        }
                        for record in _table_rows(summary.get("feedback_records"))
                    ]
                )

    with tabs[6]:
        st.subheader("Specialist adapters")
        st.warning("All specialist adapters are disabled. No live calls are available.")
        summary = adapter_review.get("summary", {})
        if isinstance(summary, Mapping):
            st.table(
                [
                    {
                        "Adapters": summary.get("adapter_count", 0),
                        "Live enabled": summary.get("live_enabled_count", 0),
                        "Generated candidates allowed": summary.get(
                            "generated_candidates_allowed_count", 0
                        ),
                        "Mature evidence allowed": summary.get(
                            "mature_evidence_allowed_count", 0
                        ),
                        "Registry safe": display_field_value(
                            "registry_safe", summary.get("registry_safe")
                        ),
                    }
                ]
            )
        st.table(build_adapter_summary_rows(adapter_review))


if __name__ == "__main__":
    main()
