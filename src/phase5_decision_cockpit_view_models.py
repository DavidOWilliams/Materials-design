from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.phase5_validation_needs import run_phase5_validation_needs


BADGE_TONES: tuple[str, ...] = (
    "positive",
    "neutral",
    "caution",
    "high_caution",
    "info",
)

METRIC_TONES: tuple[str, ...] = (
    "positive",
    "neutral",
    "caution",
    "high_caution",
    "info",
)

CHART_TYPES: tuple[str, ...] = (
    "bar",
    "stacked_bar",
    "summary_table",
)


class CockpitBadge(TypedDict, total=False):
    badge_id: str
    label: str
    tone: str
    tooltip: str


class CockpitMetric(TypedDict, total=False):
    metric_id: str
    label: str
    value: str
    tone: str
    help_text: str


class CockpitChartData(TypedDict, total=False):
    chart_id: str
    title: str
    chart_type: str
    data: list[dict[str, Any]]
    notes: list[str]
    warnings: list[str]


class CandidateCockpitCard(TypedDict, total=False):
    candidate_id: str
    system_name: str
    headline: str
    tier: str
    tier_label: str
    frontier_status: str
    evidence_maturity: str
    evidence_band: str
    plan_status: str
    research_mode_exposure: bool
    badges: list[CockpitBadge]
    metrics: list[CockpitMetric]
    priority_validation_needs: list[dict[str, Any]]
    caution_summary: list[str]
    review_actions: list[str]
    detail_sections: list[dict[str, Any]]
    notes: list[str]
    warnings: list[str]


class DecisionCockpitViewModel(TypedDict, total=False):
    candidate_count: int
    card_count: int
    research_mode_enabled: bool
    overview_metrics: list[CockpitMetric]
    cards: list[CandidateCockpitCard]
    charts: list[CockpitChartData]
    global_notes: list[str]
    global_warnings: list[str]


def _as_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    if not all(isinstance(item, str) for item in value):
        return []
    return list(value)


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def tone_for_tier(tier: str) -> str:
    return {
        "mature_reference_option": "positive",
        "validation_needed_option": "caution",
        "exploratory_option": "high_caution",
        "research_only_suggestion": "high_caution",
        "parked_not_preferred": "neutral",
    }.get(_as_string(tier), "info")


def tone_for_plan_status(plan_status: str) -> str:
    return {
        "validation_needs_available": "caution",
        "no_validation_needs_identified": "neutral",
        "research_mode_validation_required": "high_caution",
    }.get(_as_string(plan_status), "info")


def tone_for_priority(priority: str) -> str:
    return {
        "high": "high_caution",
        "medium": "caution",
        "low": "neutral",
    }.get(_as_string(priority), "info")


def build_badge(
    badge_id: str,
    *,
    label: str,
    tone: str = "info",
    tooltip: str = "",
) -> CockpitBadge:
    return {
        "badge_id": badge_id,
        "label": label,
        "tone": tone,
        "tooltip": tooltip,
    }


def build_metric(
    metric_id: str,
    *,
    label: str,
    value: Any,
    tone: str = "info",
    help_text: str = "",
) -> CockpitMetric:
    return {
        "metric_id": metric_id,
        "label": label,
        "value": str(value),
        "tone": tone,
        "help_text": help_text,
    }


def _human_label(value: Any) -> str:
    text = _as_string(value, "unknown").replace("_", " ")
    return text[:1].upper() + text[1:]


def badges_for_candidate_plan(plan: Mapping[str, Any]) -> list[CockpitBadge]:
    tier = _as_string(plan.get("tier"), "unknown")
    tier_label = _as_string(plan.get("tier_label"), _human_label(tier))
    frontier_status = _as_string(plan.get("frontier_status"), "unknown")
    evidence_band = _as_string(plan.get("evidence_band"), "unknown")
    plan_status = _as_string(plan.get("plan_status"), "unknown")
    research_mode_exposure = plan.get("research_mode_exposure") is True

    badges = [
        build_badge(
            "tier",
            label=tier_label,
            tone=tone_for_tier(tier),
            tooltip="Decision-support tier label only; not a final recommendation.",
        ),
        build_badge(
            "frontier_status",
            label=f"Frontier: {_human_label(frontier_status)}",
            tone="info" if frontier_status == "on_frontier" else "neutral",
            tooltip="Frontier status supports review only; it is not a ranking.",
        ),
        build_badge(
            "evidence_band",
            label=f"Evidence: {_human_label(evidence_band)}",
            tone="positive" if evidence_band == "mature" else "caution",
            tooltip="Evidence band summarises maturity signals for review.",
        ),
        build_badge(
            "plan_status",
            label=f"Plan: {_human_label(plan_status)}",
            tone=tone_for_plan_status(plan_status),
            tooltip="Validation-needs status is a planning prompt only.",
        ),
    ]
    if research_mode_exposure:
        badges.append(
            build_badge(
                "research_mode_exposure",
                label="Research mode",
                tone="high_caution",
                tooltip="Research-mode exposure requires gated review before promotion.",
            )
        )
    badges.append(
        build_badge(
            "no_certification_claim",
            label="No certification claim",
            tone="info",
            tooltip="No qualification or certification approval is implied.",
        )
    )
    return badges


def _validation_needs(plan: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    needs = plan.get("validation_needs")
    if not isinstance(needs, list):
        return []
    return [need for need in needs if isinstance(need, Mapping)]


def metrics_for_candidate_plan(plan: Mapping[str, Any]) -> list[CockpitMetric]:
    needs = _validation_needs(plan)
    high_count = sum(1 for need in needs if need.get("priority") == "high")
    medium_count = sum(1 for need in needs if need.get("priority") == "medium")
    low_count = sum(1 for need in needs if need.get("priority") == "low")
    warning_count = len(_string_list(plan.get("warnings")))
    need_warning_count = sum(len(_string_list(need.get("warnings"))) for need in needs)
    caution_count = warning_count + need_warning_count
    research_mode_exposure = plan.get("research_mode_exposure") is True

    return [
        build_metric(
            "validation_need_count",
            label="Validation needs",
            value=int(plan.get("validation_need_count") or len(needs)),
            tone=tone_for_plan_status(_as_string(plan.get("plan_status"))),
            help_text="Number of review or evidence-building prompts.",
        ),
        build_metric(
            "high_priority_need_count",
            label="High priority",
            value=high_count,
            tone=tone_for_priority("high") if high_count else "neutral",
            help_text="High-priority validation needs.",
        ),
        build_metric(
            "medium_priority_need_count",
            label="Medium priority",
            value=medium_count,
            tone=tone_for_priority("medium") if medium_count else "neutral",
            help_text="Medium-priority validation needs.",
        ),
        build_metric(
            "low_priority_need_count",
            label="Low priority",
            value=low_count,
            tone=tone_for_priority("low"),
            help_text="Low-priority validation needs.",
        ),
        build_metric(
            "caution_count",
            label="Cautions",
            value=caution_count,
            tone="caution" if caution_count else "neutral",
            help_text="Plan warnings plus validation-need warnings.",
        ),
        build_metric(
            "research_mode_exposure",
            label="Research mode",
            value="true" if research_mode_exposure else "false",
            tone="high_caution" if research_mode_exposure else "neutral",
            help_text="Whether the option has research-mode exposure.",
        ),
    ]


def priority_validation_needs(
    plan: Mapping[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    priority_order = {"high": 0, "medium": 1, "low": 2}
    indexed_needs = list(enumerate(_validation_needs(plan)))
    indexed_needs.sort(
        key=lambda item: (
            priority_order.get(_as_string(item[1].get("priority")), 3),
            item[0],
        )
    )

    selected: list[dict[str, Any]] = []
    for _, need in indexed_needs[:limit]:
        selected.append(
            {
                "need_id": _as_string(need.get("need_id")),
                "category": _as_string(need.get("category")),
                "priority": _as_string(need.get("priority"), "unknown"),
                "validation_activity": _as_string(need.get("validation_activity")),
                "trigger": _as_string(need.get("trigger")),
                "status": _as_string(need.get("status"), "unknown"),
                "warnings": _string_list(deepcopy(need.get("warnings"))),
            }
        )
    return selected


def caution_summary_for_plan(plan: Mapping[str, Any]) -> list[str]:
    cautions: list[str] = []
    for warning in _string_list(plan.get("warnings")):
        _append_unique(cautions, warning)
    for need in _validation_needs(plan):
        for warning in _string_list(need.get("warnings")):
            _append_unique(cautions, warning)
    _append_unique(cautions, "No certification or qualification approval is implied.")
    return cautions


def review_actions_for_plan(plan: Mapping[str, Any]) -> list[str]:
    actions: list[str] = []
    for need in priority_validation_needs(plan, limit=len(_validation_needs(plan))):
        _append_unique(actions, _as_string(need.get("validation_activity")))
        if len(actions) >= 5:
            break
    if not actions:
        return ["Review assumptions and evidence gaps before engineering use."]
    return actions


def detail_sections_for_plan(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    needs = priority_validation_needs(plan, limit=len(_validation_needs(plan)))
    cautions = caution_summary_for_plan(plan)
    return [
        {
            "section_id": "tier_and_evidence",
            "title": "Tier and evidence",
            "rows": [
                {"label": "Tier", "value": _as_string(plan.get("tier_label"))},
                {"label": "Frontier status", "value": _as_string(plan.get("frontier_status"))},
                {"label": "Evidence maturity", "value": _as_string(plan.get("evidence_maturity"))},
                {"label": "Evidence band", "value": _as_string(plan.get("evidence_band"))},
            ],
        },
        {
            "section_id": "validation_needs",
            "title": "Validation needs",
            "rows": list(needs),
        },
        {
            "section_id": "cautions_and_warnings",
            "title": "Cautions and warnings",
            "rows": [{"warning": warning} for warning in cautions],
        },
        {
            "section_id": "decision_support_limitations",
            "title": "Decision-support limitations",
            "rows": [
                {"limitation": "No final recommendation."},
                {"limitation": "No qualification approval."},
                {"limitation": "No certification approval."},
                {"limitation": "Engineering review required."},
            ],
        },
    ]


def build_candidate_cockpit_card(
    plan: Mapping[str, Any],
) -> CandidateCockpitCard:
    candidate_id = _as_string(plan.get("candidate_id"), "unknown_candidate")
    system_name = _as_string(plan.get("system_name"), "unknown_system")
    tier = _as_string(plan.get("tier"), "unknown")
    tier_label = _as_string(plan.get("tier_label"), _human_label(tier))

    return {
        "candidate_id": candidate_id,
        "system_name": system_name,
        "headline": f"{system_name} - {tier_label}",
        "tier": tier,
        "tier_label": tier_label,
        "frontier_status": _as_string(plan.get("frontier_status"), "unknown"),
        "evidence_maturity": _as_string(plan.get("evidence_maturity"), "unknown"),
        "evidence_band": _as_string(plan.get("evidence_band"), "unknown"),
        "plan_status": _as_string(plan.get("plan_status"), "unknown"),
        "research_mode_exposure": plan.get("research_mode_exposure") is True,
        "badges": badges_for_candidate_plan(plan),
        "metrics": metrics_for_candidate_plan(plan),
        "priority_validation_needs": priority_validation_needs(plan),
        "caution_summary": caution_summary_for_plan(plan),
        "review_actions": review_actions_for_plan(plan),
        "detail_sections": detail_sections_for_plan(plan),
        "notes": [
            "Card is a view model only; it does not render UI.",
            "No final recommendation, qualification approval or certification approval is implied.",
        ],
        "warnings": _string_list(deepcopy(plan.get("warnings"))),
    }


def count_by_key(items: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = _as_string(item.get(key), "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


def chart_from_counts(
    chart_id: str,
    *,
    title: str,
    counts: Mapping[str, int],
    chart_type: str = "bar",
) -> CockpitChartData:
    return {
        "chart_id": chart_id,
        "title": title,
        "chart_type": chart_type,
        "data": [
            {"label": label, "value": count}
            for label, count in counts.items()
        ],
        "notes": [
            "Chart data is UI-ready only; no chart is rendered here.",
        ],
        "warnings": [],
    }


def overview_metrics_for_validation_run(
    validation_run: Mapping[str, Any],
) -> list[CockpitMetric]:
    summary = validation_run.get("validation_summary")
    summary_mapping = summary if isinstance(summary, Mapping) else {}
    by_priority = summary_mapping.get("by_priority")
    by_priority_mapping = by_priority if isinstance(by_priority, Mapping) else {}
    high_priority_count = int(by_priority_mapping.get("high") or 0)
    research_mode_plan_count = int(summary_mapping.get("research_mode_plan_count") or 0)
    research_mode_enabled = validation_run.get("research_mode_enabled") is True

    return [
        build_metric(
            "candidate_count",
            label="Candidates",
            value=int(validation_run.get("candidate_count") or 0),
            tone="info",
            help_text="Candidate count represented in the view model.",
        ),
        build_metric(
            "plan_count",
            label="Plans",
            value=int(validation_run.get("plan_count") or 0),
            tone="info",
            help_text="Validation-needs plan count.",
        ),
        build_metric(
            "validation_need_count",
            label="Validation needs",
            value=int(validation_run.get("validation_need_count") or 0),
            tone="caution",
            help_text="Total validation/review prompts.",
        ),
        build_metric(
            "research_mode_enabled",
            label="Research mode",
            value="true" if research_mode_enabled else "false",
            tone="high_caution" if research_mode_enabled else "neutral",
            help_text="Whether research-mode options were allowed upstream.",
        ),
        build_metric(
            "high_priority_need_count",
            label="High priority needs",
            value=high_priority_count,
            tone="high_caution" if high_priority_count else "neutral",
            help_text="High-priority validation needs across all candidates.",
        ),
        build_metric(
            "research_mode_plan_count",
            label="Research-mode plans",
            value=research_mode_plan_count,
            tone="high_caution" if research_mode_plan_count else "neutral",
            help_text="Plans requiring research-mode validation gates.",
        ),
    ]


def charts_for_validation_run(
    validation_run: Mapping[str, Any],
) -> list[CockpitChartData]:
    summary = validation_run.get("validation_summary")
    summary_mapping = summary if isinstance(summary, Mapping) else {}
    plans = validation_run.get("candidate_validation_needs")
    plan_list = [plan for plan in plans if isinstance(plan, Mapping)] if isinstance(plans, list) else []

    return [
        chart_from_counts(
            "plan_status_distribution",
            title="Plan Status Distribution",
            counts=summary_mapping.get("by_plan_status", {})
            if isinstance(summary_mapping.get("by_plan_status"), Mapping)
            else {},
        ),
        chart_from_counts(
            "validation_category_distribution",
            title="Validation Category Distribution",
            counts=summary_mapping.get("by_category", {})
            if isinstance(summary_mapping.get("by_category"), Mapping)
            else {},
        ),
        chart_from_counts(
            "validation_priority_distribution",
            title="Validation Priority Distribution",
            counts=summary_mapping.get("by_priority", {})
            if isinstance(summary_mapping.get("by_priority"), Mapping)
            else {},
        ),
        chart_from_counts(
            "tier_distribution",
            title="Tier Distribution",
            counts=count_by_key(plan_list, "tier"),
        ),
    ]


def build_decision_cockpit_view_model_from_validation_run(
    validation_run: Mapping[str, Any],
) -> DecisionCockpitViewModel:
    plans = validation_run.get("candidate_validation_needs")
    plan_list = [plan for plan in plans if isinstance(plan, Mapping)] if isinstance(plans, list) else []
    cards = [build_candidate_cockpit_card(plan) for plan in plan_list]
    warnings = _string_list(deepcopy(validation_run.get("warnings")))
    if not cards:
        warnings.append("No candidate cockpit cards are available.")

    return {
        "candidate_count": int(validation_run.get("candidate_count") or 0),
        "card_count": len(cards),
        "research_mode_enabled": validation_run.get("research_mode_enabled") is True,
        "overview_metrics": overview_metrics_for_validation_run(validation_run),
        "cards": cards,
        "charts": charts_for_validation_run(validation_run),
        "global_notes": [
            "Decision cockpit view model is presentation data only.",
            "No final recommendation, ranking, qualification approval or certification approval is implied.",
        ],
        "global_warnings": warnings,
    }


def run_phase5_decision_cockpit_view_model(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> DecisionCockpitViewModel:
    validation_run = run_phase5_validation_needs(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    view_model = build_decision_cockpit_view_model_from_validation_run(validation_run)
    view_model["research_mode_enabled"] = research_mode_enabled
    if research_mode_enabled:
        warnings = list(view_model.get("global_warnings", []))
        warnings.append("Research mode is enabled; cockpit cards may include research-mode gates.")
        view_model["global_warnings"] = warnings
    return view_model
