from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import json
from typing import Any, TypedDict

from src.phase5_decision_cockpit_view_models import (
    run_phase5_decision_cockpit_view_model,
)


EXPORT_SCHEMA_VERSION = "phase5_cockpit_review_export_v1"

EXPORT_LIMITATIONS: tuple[str, ...] = (
    "Decision-support export only.",
    "No final recommendation is made.",
    "No ranking or winner selection is included.",
    "No qualification approval is implied.",
    "No certification approval is implied.",
    "Engineering review is required before use.",
)


class ExportManifest(TypedDict, total=False):
    export_type: str
    phase: str
    schema_version: str
    candidate_count: int
    card_count: int
    chart_count: int
    includes_markdown: bool
    includes_json_payload: bool
    generated_by: str
    limitations: list[str]
    warnings: list[str]


class CandidateReviewSummary(TypedDict, total=False):
    candidate_id: str
    system_name: str
    headline: str
    tier_label: str
    frontier_status: str
    evidence_band: str
    plan_status: str
    research_mode_exposure: bool
    badge_labels: list[str]
    key_metrics: dict[str, str]
    priority_actions: list[str]
    caution_summary: list[str]
    validation_need_count: int
    warnings: list[str]


class CockpitReviewExportPackage(TypedDict, total=False):
    manifest: ExportManifest
    overview_metrics: list[dict[str, Any]]
    candidate_summaries: list[CandidateReviewSummary]
    chart_data: list[dict[str, Any]]
    markdown_report: str
    json_payload: dict[str, Any]
    notes: list[str]
    warnings: list[str]


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


def make_json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def metric_map(metrics: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for metric in metrics:
        metric_id = _as_string(metric.get("metric_id"))
        if metric_id and metric_id not in mapped:
            mapped[metric_id] = _as_string(metric.get("value"))
    return mapped


def badge_labels(badges: Sequence[Mapping[str, Any]]) -> list[str]:
    labels: list[str] = []
    for badge in badges:
        label = _as_string(badge.get("label"))
        if label:
            labels.append(label)
    return labels


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _parse_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def summarise_candidate_card(card: Mapping[str, Any]) -> CandidateReviewSummary:
    metrics = metric_map(_mapping_list(card.get("metrics")))
    parsed_need_count = _parse_int(metrics.get("validation_need_count"))
    priority_needs = _mapping_list(card.get("priority_validation_needs"))
    validation_need_count = (
        parsed_need_count if parsed_need_count is not None else len(priority_needs)
    )

    return {
        "candidate_id": _as_string(card.get("candidate_id"), "unknown_candidate"),
        "system_name": _as_string(card.get("system_name"), "unknown_system"),
        "headline": _as_string(card.get("headline")),
        "tier_label": _as_string(card.get("tier_label"), "unknown"),
        "frontier_status": _as_string(card.get("frontier_status"), "unknown"),
        "evidence_band": _as_string(card.get("evidence_band"), "unknown"),
        "plan_status": _as_string(card.get("plan_status"), "unknown"),
        "research_mode_exposure": card.get("research_mode_exposure") is True,
        "badge_labels": badge_labels(_mapping_list(card.get("badges"))),
        "key_metrics": metrics,
        "priority_actions": _string_list(deepcopy(card.get("review_actions"))),
        "caution_summary": _string_list(deepcopy(card.get("caution_summary"))),
        "validation_need_count": validation_need_count,
        "warnings": _string_list(deepcopy(card.get("warnings"))),
    }


def summarise_cards(cards: Sequence[Mapping[str, Any]]) -> list[CandidateReviewSummary]:
    return [summarise_candidate_card(card) for card in cards]


def build_export_manifest(
    view_model: Mapping[str, Any],
    *,
    includes_markdown: bool = True,
    includes_json_payload: bool = True,
) -> ExportManifest:
    charts = view_model.get("charts")
    chart_count = len(charts) if isinstance(charts, list) else 0
    card_count = int(view_model.get("card_count") or 0)
    warnings = _string_list(deepcopy(view_model.get("global_warnings")))
    if card_count == 0:
        warnings.append("No candidate cards are available for export.")

    return {
        "export_type": "phase5_cockpit_review_export",
        "phase": "Phase 5",
        "schema_version": EXPORT_SCHEMA_VERSION,
        "candidate_count": int(view_model.get("candidate_count") or 0),
        "card_count": card_count,
        "chart_count": chart_count,
        "includes_markdown": includes_markdown,
        "includes_json_payload": includes_json_payload,
        "generated_by": "phase5_cockpit_review_export",
        "limitations": list(EXPORT_LIMITATIONS),
        "warnings": warnings,
    }


def markdown_escape(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    if not headers:
        return ""
    header_line = "| " + " | ".join(markdown_escape(header) for header in headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"
    row_lines = [
        "| " + " | ".join(markdown_escape(cell) for cell in row) + " |"
        for row in rows
    ]
    return "\n".join([header_line, separator_line, *row_lines])


def markdown_for_candidate_summary(summary: Mapping[str, Any]) -> str:
    candidate_id = _as_string(summary.get("candidate_id"), "unknown_candidate")
    headline = _as_string(summary.get("headline"), _as_string(summary.get("system_name")))
    key_metrics = summary.get("key_metrics")
    metrics_mapping = key_metrics if isinstance(key_metrics, Mapping) else {}
    metric_rows = [(key, value) for key, value in metrics_mapping.items()]
    actions = _string_list(summary.get("priority_actions"))
    cautions = _string_list(summary.get("caution_summary"))
    warnings = _string_list(summary.get("warnings"))
    badge_text = ", ".join(_string_list(summary.get("badge_labels"))) or "None"

    lines = [
        f"## {markdown_escape(candidate_id)} - {markdown_escape(headline)}",
        "",
        f"- Tier: {markdown_escape(_as_string(summary.get('tier_label'), 'unknown'))}",
        f"- Frontier status: {markdown_escape(_as_string(summary.get('frontier_status'), 'unknown'))}",
        f"- Evidence band: {markdown_escape(_as_string(summary.get('evidence_band'), 'unknown'))}",
        f"- Plan status: {markdown_escape(_as_string(summary.get('plan_status'), 'unknown'))}",
        f"- Research-mode exposure: {summary.get('research_mode_exposure') is True}",
        f"- Badges: {markdown_escape(badge_text)}",
        "",
        markdown_table(["Metric", "Value"], metric_rows),
        "",
        "Priority actions:",
    ]
    lines.extend(f"- {markdown_escape(action)}" for action in actions)
    if not actions:
        lines.append("- None")
    lines.append("")
    lines.append("Cautions:")
    lines.extend(f"- {markdown_escape(caution)}" for caution in cautions)
    if not cautions:
        lines.append("- None")
    if warnings:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {markdown_escape(warning)}" for warning in warnings)
    lines.extend(
        [
            "",
            "This section is decision-support only and does not imply recommendation, qualification approval or certification approval.",
        ]
    )
    return "\n".join(lines)


def build_markdown_report(
    manifest: Mapping[str, Any],
    overview_metrics: Sequence[Mapping[str, Any]],
    candidate_summaries: Sequence[Mapping[str, Any]],
    chart_data: Sequence[Mapping[str, Any]],
) -> str:
    manifest_rows = [
        ("Schema version", manifest.get("schema_version", "")),
        ("Candidate count", manifest.get("candidate_count", "")),
        ("Card count", manifest.get("card_count", "")),
        ("Chart count", manifest.get("chart_count", "")),
    ]
    overview_rows = [
        (
            metric.get("label", metric.get("metric_id", "")),
            metric.get("value", ""),
        )
        for metric in overview_metrics
    ]
    chart_rows = [
        (
            chart.get("chart_id", ""),
            chart.get("title", ""),
            chart.get("chart_type", ""),
            len(chart.get("data", [])) if isinstance(chart.get("data"), list) else 0,
        )
        for chart in chart_data
    ]

    lines = [
        "# Phase 5 Cockpit Review Export",
        "",
        "## Manifest Summary",
        markdown_table(["Field", "Value"], manifest_rows),
        "",
        "## Limitations",
    ]
    lines.extend(
        f"- {markdown_escape(limitation)}"
        for limitation in _string_list(manifest.get("limitations"))
    )
    lines.extend(
        [
            "",
            "## Overview Metrics",
            markdown_table(["Metric", "Value"], overview_rows),
            "",
            "## Chart Data Summary",
            markdown_table(["Chart ID", "Title", "Chart type", "Rows"], chart_rows),
            "",
            "## Candidate Summaries",
        ]
    )
    if candidate_summaries:
        for summary in candidate_summaries:
            lines.extend(["", markdown_for_candidate_summary(summary)])
    else:
        lines.append("")
        lines.append("No candidate summaries are available.")
    lines.extend(
        [
            "",
            "## Final Limitations",
        ]
    )
    lines.extend(
        f"- {markdown_escape(limitation)}"
        for limitation in _string_list(manifest.get("limitations"))
    )
    return "\n".join(lines)


def build_cockpit_review_export_package_from_view_model(
    view_model: Mapping[str, Any],
) -> CockpitReviewExportPackage:
    manifest = build_export_manifest(view_model)
    overview_metrics = make_json_safe(deepcopy(view_model.get("overview_metrics") or []))
    cards = _mapping_list(view_model.get("cards"))
    candidate_summaries = summarise_cards(cards)
    chart_data = make_json_safe(deepcopy(view_model.get("charts") or []))
    json_payload = make_json_safe(
        {
            "manifest": manifest,
            "overview_metrics": overview_metrics,
            "candidate_summaries": candidate_summaries,
            "chart_data": chart_data,
            "global_notes": _string_list(deepcopy(view_model.get("global_notes"))),
            "global_warnings": _string_list(deepcopy(view_model.get("global_warnings"))),
        }
    )
    markdown_report = build_markdown_report(
        manifest,
        overview_metrics if isinstance(overview_metrics, list) else [],
        candidate_summaries,
        chart_data if isinstance(chart_data, list) else [],
    )

    return {
        "manifest": manifest,
        "overview_metrics": overview_metrics if isinstance(overview_metrics, list) else [],
        "candidate_summaries": candidate_summaries,
        "chart_data": chart_data if isinstance(chart_data, list) else [],
        "markdown_report": markdown_report,
        "json_payload": json_payload,
        "notes": [
            "Export package is in-memory only; no files are written.",
            "No final recommendation, ranking, qualification approval or certification approval is implied.",
        ],
        "warnings": list(manifest.get("warnings", [])),
    }


def export_package_to_json_string(
    package: Mapping[str, Any],
    *,
    indent: int = 2,
) -> str:
    payload = package.get("json_payload") if "json_payload" in package else package
    return json.dumps(make_json_safe(payload), indent=indent, sort_keys=True)


def run_phase5_cockpit_review_export(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> CockpitReviewExportPackage:
    view_model = run_phase5_decision_cockpit_view_model(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    package = build_cockpit_review_export_package_from_view_model(view_model)
    if research_mode_enabled:
        warning = "Research mode is enabled; export may include research-mode review content."
        warnings = list(package.get("warnings", []))
        warnings.append(warning)
        package["warnings"] = warnings
        manifest = dict(package.get("manifest", {}))
        manifest_warnings = list(manifest.get("warnings", []))
        manifest_warnings.append(warning)
        manifest["warnings"] = manifest_warnings
        package["manifest"] = manifest
        payload = dict(package.get("json_payload", {}))
        payload["manifest"] = make_json_safe(manifest)
        package["json_payload"] = payload
    return package
