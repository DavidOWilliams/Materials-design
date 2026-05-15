from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

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
    return [
        {"field": "candidate_id", "value": str(card.get("candidate_id", ""))},
        {"field": "system_name", "value": str(card.get("system_name", ""))},
        {"field": "tier_label", "value": str(card.get("tier_label", ""))},
        {"field": "frontier_status", "value": str(card.get("frontier_status", ""))},
        {"field": "evidence_band", "value": str(card.get("evidence_band", ""))},
        {"field": "plan_status", "value": str(card.get("plan_status", ""))},
        {
            "field": "validation_need_count",
            "value": find_metric(metrics, "validation_need_count"),
        },
        {
            "field": "research_mode_exposure",
            "value": "true" if card.get("research_mode_exposure") is True else "false",
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

    st.set_page_config(page_title="Phase 6.1 Decision Cockpit Prototype", layout="wide")
    st.title("Phase 6.1 Decision Cockpit Prototype")
    st.info(
        "Standalone prototype viewer only. This is not the production app, does not "
        "change analysis outputs, and does not provide approval."
    )

    research_mode_enabled = st.sidebar.checkbox("Enable research-mode view", value=False)
    st.sidebar.write(
        "Research mode remains gated. It does not enable live model calls or approval paths."
    )

    view_model = build_demo_cockpit_view_model(
        research_mode_enabled=research_mode_enabled,
    )
    export_package = build_cockpit_review_export_package_from_view_model(view_model)
    feedback_package = build_feedback_record_package_from_export_package(export_package)
    adapter_review = build_demo_adapter_contract_review()

    tabs = st.tabs(
        [
            "Overview",
            "Candidate cards",
            "Charts",
            "Review export",
            "Feedback records",
            "Specialist adapters",
        ]
    )

    with tabs[0]:
        st.subheader("Overview metrics")
        st.table(_table_rows(view_model.get("overview_metrics")))
        _show_bullets(st, "Global notes", view_model.get("global_notes", []))
        _show_bullets(st, "Global warnings", view_model.get("global_warnings", []))
        _show_bullets(st, "Prototype safety notes", prototype_safety_notes())

    with tabs[1]:
        for card in _table_rows(view_model.get("cards")):
            with st.expander(str(card.get("headline", card.get("candidate_id", "Candidate")))):
                st.table(build_candidate_card_display_rows(card))
                st.write("Badges")
                st.write(", ".join(str(badge.get("label", "")) for badge in _table_rows(card.get("badges"))))
                st.write("Metrics")
                st.table(_table_rows(card.get("metrics")))
                st.write("Priority validation needs")
                st.table(_table_rows(card.get("priority_validation_needs")))
                _show_bullets(st, "Review actions", card.get("review_actions", []))
                _show_bullets(st, "Caution summary", card.get("caution_summary", []))
                st.write("Detail sections")
                for section in _table_rows(card.get("detail_sections")):
                    st.write(str(section.get("title", "")))
                    st.table(_table_rows(section.get("rows")))

    with tabs[2]:
        for chart in _table_rows(view_model.get("charts")):
            st.subheader(str(chart.get("title", chart.get("chart_id", "Chart"))))
            rows = flatten_chart_data(chart)
            st.table(rows)
            if rows:
                st.bar_chart({row["label"]: row["value"] for row in rows})

    with tabs[3]:
        st.subheader("Manifest")
        st.json(export_package.get("manifest", {}))
        st.subheader("Candidate summaries")
        st.table(_table_rows(export_package.get("candidate_summaries")))
        st.subheader("Markdown report")
        st.code(str(export_package.get("markdown_report", "")), language="markdown")

    with tabs[4]:
        st.subheader("Feedback summaries")
        st.table(_table_rows(feedback_package.get("feedback_summaries")))
        st.subheader("Draft feedback templates")
        for summary in _table_rows(feedback_package.get("feedback_summaries")):
            st.write(str(summary.get("candidate_id", "")))
            st.table(_table_rows(summary.get("feedback_records")))
        st.caption("Draft records are templates only and do not modify analysis outputs.")

    with tabs[5]:
        st.subheader("Disabled adapter registry summary")
        st.json(adapter_review.get("summary", {}))
        registry = adapter_review.get("registry", {})
        adapters = registry.get("adapters", []) if isinstance(registry, Mapping) else []
        st.subheader("Adapters")
        st.table(_table_rows(adapters))
        st.warning("Live calls are disabled. Specialist adapters are contract placeholders only.")


if __name__ == "__main__":
    main()
