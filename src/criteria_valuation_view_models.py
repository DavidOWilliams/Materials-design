from __future__ import annotations

import copy
import re
from typing import TypedDict

from src.criteria_valuation_package import (
    hot_section_demo_criteria_valuation_package,
    validate_criteria_valuation_package,
)


CRITERIA_VALUATION_VIEW_MODEL_SCHEMA_VERSION = (
    "criteria_valuation_cockpit_view_model_v1"
)
VIEW_MODEL_SECTION_SCHEMA_VERSION = "criteria_valuation_view_model_section_v1"
SUMMARY_CARD_SCHEMA_VERSION = "criteria_valuation_summary_card_v1"
TABLE_ROW_SCHEMA_VERSION = "criteria_valuation_table_row_v1"
BADGE_SCHEMA_VERSION = "criteria_valuation_badge_v1"

VIEW_MODEL_SECTION_IDS: tuple[str, ...] = (
    "readiness_panel",
    "safety_panel",
    "candidate_summary_cards",
    "criterion_value_table",
    "evidence_gap_table",
    "action_worklist_table",
    "review_use_case_panel",
    "assumptions_panel",
    "warnings_panel",
    "hard_constraints_panel",
)

VIEW_MODEL_SECTION_STATUSES: tuple[str, ...] = (
    "present",
    "empty",
    "warning",
    "placeholder_only",
    "invalid_input",
)

DISPLAY_SEVERITIES: tuple[str, ...] = (
    "neutral",
    "info",
    "warning",
    "critical",
)

BADGE_TYPES: tuple[str, ...] = (
    "safety",
    "readiness",
    "coverage",
    "evidence_gap",
    "action_type",
    "live_call_status",
    "placeholder_status",
    "constraint",
)

REQUIRED_VIEW_MODEL_FIELDS: tuple[str, ...] = (
    "schema_version",
    "source_package_schema_version",
    "package_status",
    "readiness_level",
    "sections",
    "readiness_panel",
    "safety_panel",
    "candidate_summary_cards",
    "criterion_value_rows",
    "evidence_gap_rows",
    "action_worklist_rows",
    "review_use_case_panel",
    "assumptions_panel",
    "warnings_panel",
    "hard_constraints_panel",
    "badges",
    "candidate_count",
    "criterion_value_row_count",
    "evidence_gap_row_count",
    "action_worklist_row_count",
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "measurement_execution_allowed",
    "assumptions",
    "warnings",
)

REQUIRED_SECTION_FIELDS: tuple[str, ...] = (
    "schema_version",
    "section_id",
    "title",
    "section_status",
    "item_count",
    "summary_text",
    "payload",
    "badges",
    "assumptions",
    "warnings",
)

REQUIRED_SUMMARY_CARD_FIELDS: tuple[str, ...] = (
    "schema_version",
    "card_id",
    "title",
    "subtitle",
    "status",
    "severity",
    "metrics",
    "badges",
    "detail_rows",
    "assumptions",
    "warnings",
)

REQUIRED_TABLE_ROW_FIELDS: tuple[str, ...] = (
    "schema_version",
    "row_id",
    "row_type",
    "candidate_id",
    "primary_label",
    "secondary_label",
    "status",
    "severity",
    "cells",
    "badges",
    "assumptions",
    "warnings",
)

REQUIRED_BADGE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "badge_id",
    "badge_type",
    "label",
    "severity",
    "explanation",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)

_FORBIDDEN_RANKING_FIELDS: tuple[str, ...] = (
    "rank",
    "winner",
    "best_candidate",
    "score",
)

_FORBIDDEN_ROW_RUNTIME_FIELDS: tuple[str, ...] = (
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "measurement_execution_allowed",
)

_FORBIDDEN_OUTPUT_FIELDS: tuple[str, ...] = (
    *_FORBIDDEN_CLAIM_FIELDS,
    *_FORBIDDEN_RANKING_FIELDS,
)


class DisplayBadge(TypedDict, total=False):
    schema_version: str
    badge_id: str
    badge_type: str
    label: str
    severity: str
    explanation: str


class ViewModelSection(TypedDict, total=False):
    schema_version: str
    section_id: str
    title: str
    section_status: str
    item_count: int
    summary_text: str
    payload: object
    badges: list[dict]
    assumptions: list[str]
    warnings: list[str]


class SummaryCard(TypedDict, total=False):
    schema_version: str
    card_id: str
    title: str
    subtitle: str
    status: str
    severity: str
    metrics: dict
    badges: list[dict]
    detail_rows: list[dict]
    assumptions: list[str]
    warnings: list[str]


class TableRow(TypedDict, total=False):
    schema_version: str
    row_id: str
    row_type: str
    candidate_id: str
    primary_label: str
    secondary_label: str
    status: str
    severity: str
    cells: dict
    badges: list[dict]
    assumptions: list[str]
    warnings: list[str]


class CriteriaValuationCockpitViewModel(TypedDict, total=False):
    schema_version: str
    source_package_schema_version: str
    package_status: str
    readiness_level: str
    sections: list[dict]
    readiness_panel: dict
    safety_panel: dict
    candidate_summary_cards: list[dict]
    criterion_value_rows: list[dict]
    evidence_gap_rows: list[dict]
    action_worklist_rows: list[dict]
    review_use_case_panel: dict
    assumptions_panel: dict
    warnings_panel: dict
    hard_constraints_panel: dict
    badges: list[dict]
    candidate_count: int
    criterion_value_row_count: int
    evidence_gap_row_count: int
    action_worklist_row_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    measurement_execution_allowed: bool
    assumptions: list[str]
    warnings: list[str]


class CriteriaValuationViewModelValidationResult(TypedDict, total=False):
    is_valid: bool
    errors: list[str]
    warnings: list[str]


def unique_preserve_order(values: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        text = str(value)
        if text in seen:
            continue
        seen.add(text)
        unique_values.append(text)
    return unique_values


def slugify_identifier(value: object) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(value).lower()).strip("_")
    return text or "unknown"


def humanise_identifier(value: object) -> str:
    if value is None:
        return "Not specified"
    text = str(value).replace("_", " ").replace("-", " ").strip()
    if not text:
        return "Not specified"
    return text[:1].upper() + text[1:]


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def normalise_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return unique_preserve_order([str(value) for value in values])


def safe_count(value: object) -> int:
    if isinstance(value, (list, dict)):
        return len(value)
    return 0


def _safe_int(value: object) -> int:
    return value if isinstance(value, int) else 0


def _display_safe_copy(value: object) -> object:
    if isinstance(value, dict):
        return {
            copy.deepcopy(key): _display_safe_copy(nested)
            for key, nested in value.items()
            if str(key) not in _FORBIDDEN_OUTPUT_FIELDS
        }
    if isinstance(value, list):
        return [_display_safe_copy(item) for item in value]
    return copy.deepcopy(value)


def _copy_list(value: object) -> list:
    return _display_safe_copy(value) if isinstance(value, list) else []


def _copy_dict(value: object) -> dict:
    return _display_safe_copy(value) if isinstance(value, dict) else {}


def display_badge(
    badge_id: str,
    *,
    badge_type: str,
    label: str,
    severity: str = "neutral",
    explanation: str = "",
) -> dict:
    normalised_type = badge_type if badge_type in BADGE_TYPES else "readiness"
    normalised_severity = severity if severity in DISPLAY_SEVERITIES else "neutral"
    return {
        "schema_version": BADGE_SCHEMA_VERSION,
        "badge_id": slugify_identifier(badge_id),
        "badge_type": normalised_type,
        "label": str(label),
        "severity": normalised_severity,
        "explanation": str(explanation),
    }


def severity_for_package_status(package_status: str) -> str:
    return {
        "contract_ready": "info",
        "partial_coverage": "warning",
        "placeholder_only": "warning",
        "invalid_input": "critical",
        "empty_package": "critical",
    }.get(package_status, "neutral")


def severity_for_readiness_level(readiness_level: str) -> str:
    return {
        "ready_for_review": "info",
        "ready_with_gaps": "warning",
        "placeholder_only": "warning",
        "blocked_invalid_input": "critical",
        "empty": "critical",
    }.get(readiness_level, "neutral")


def severity_for_coverage_status(status: str) -> str:
    return {
        "populated": "info",
        "populated_with_gaps": "warning",
        "partial_coverage": "warning",
        "placeholder_only": "warning",
        "no_criteria": "critical",
        "invalid_input": "critical",
    }.get(status, "neutral")


def severity_for_action_status(status: str) -> str:
    return {
        "planned": "info",
        "placeholder_only": "warning",
        "blocked_invalid_gap": "critical",
        "blocked_not_permitted": "critical",
        "deferred": "warning",
    }.get(status, "neutral")


def safety_badges_from_package(package: dict) -> list[dict]:
    return [
        display_badge(
            "live_model_calls_disabled",
            badge_type="live_call_status",
            label="Live model calls disabled",
            severity="info",
            explanation="The cockpit view model does not permit live model calls.",
        ),
        display_badge(
            "live_source_retrieval_disabled",
            badge_type="live_call_status",
            label="Live source retrieval disabled",
            severity="info",
            explanation="The cockpit view model does not retrieve external sources.",
        ),
        display_badge(
            "measurement_execution_disabled",
            badge_type="live_call_status",
            label="Measurement execution disabled",
            severity="info",
            explanation="The cockpit view model does not execute measurements.",
        ),
        display_badge(
            "decision_support_only",
            badge_type="safety",
            label="Decision-support only",
            severity="neutral",
            explanation="Records are for engineering review and planning support.",
        ),
        display_badge(
            "no_certification_approval_implied",
            badge_type="safety",
            label="No certification approval implied",
            severity="warning",
            explanation="The view model does not make approval or qualification claims.",
        ),
    ]


def readiness_badges_from_package(package: dict) -> list[dict]:
    readiness_summary = package.get("readiness_summary", {})
    readiness_level = (
        readiness_summary.get("readiness_level", "")
        if isinstance(readiness_summary, dict)
        else ""
    )
    package_status = str(package.get("package_status", ""))
    return [
        display_badge(
            f"package_status_{package_status}",
            badge_type="readiness",
            label=f"Package status: {humanise_identifier(package_status)}",
            severity=severity_for_package_status(package_status),
            explanation="Status reported by the CriteriaValuationPackage contract.",
        ),
        display_badge(
            f"readiness_level_{readiness_level}",
            badge_type="readiness",
            label=f"Readiness: {humanise_identifier(readiness_level)}",
            severity=severity_for_readiness_level(str(readiness_level)),
            explanation="Review readiness reported by the package readiness summary.",
        ),
    ]


def _all_rows_placeholder(payload: object) -> bool:
    if not isinstance(payload, list) or not payload:
        return False
    statuses = [
        item.get("status")
        for item in payload
        if isinstance(item, dict) and item.get("status") is not None
    ]
    return bool(statuses) and all(status in {"placeholder", "placeholder_only"} for status in statuses)


def view_model_section(
    section_id: str,
    *,
    title: str = "",
    payload: object = None,
    summary_text: str = "",
    badges: list[dict] | None = None,
    assumptions: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    copied_payload = _display_safe_copy(payload)
    copied_badges = _display_safe_copy(badges or [])
    normalised_assumptions = normalise_string_list(list(assumptions or []))
    normalised_warnings = normalise_string_list(list(warnings or []))
    item_count = safe_count(copied_payload)
    if section_id not in VIEW_MODEL_SECTION_IDS:
        section_status = "invalid_input"
    elif item_count == 0:
        section_status = "empty"
    elif normalised_warnings:
        section_status = "warning"
    elif section_id == "criterion_value_table" and _all_rows_placeholder(copied_payload):
        section_status = "placeholder_only"
    else:
        section_status = "present"
    return {
        "schema_version": VIEW_MODEL_SECTION_SCHEMA_VERSION,
        "section_id": section_id,
        "title": title or humanise_identifier(section_id),
        "section_status": section_status,
        "item_count": item_count,
        "summary_text": str(summary_text),
        "payload": copied_payload,
        "badges": copied_badges,
        "assumptions": normalised_assumptions,
        "warnings": normalised_warnings,
    }


def readiness_panel_from_package(package: dict) -> dict:
    readiness_summary = _copy_dict(package.get("readiness_summary", {}))
    package_status = str(package.get("package_status", ""))
    readiness_level = str(readiness_summary.get("readiness_level", ""))
    payload = {
        "package_status": package_status,
        "readiness_level": readiness_level,
        "candidate_count": _safe_int(package.get("candidate_count", 0)),
        "criterion_value_count": _safe_int(package.get("criterion_value_count", 0)),
        "evidence_gap_count": _safe_int(package.get("evidence_gap_count", 0)),
        "action_work_item_count": _safe_int(package.get("action_work_item_count", 0)),
    }
    return view_model_section(
        "readiness_panel",
        title="Readiness summary",
        payload=payload,
        summary_text=(
            f"{humanise_identifier(package_status)}; "
            f"{humanise_identifier(readiness_level)}."
        ),
        badges=readiness_badges_from_package(package),
        assumptions=normalise_string_list(readiness_summary.get("assumptions", [])),
        warnings=normalise_string_list(readiness_summary.get("warnings", [])),
    )


def safety_panel_from_package(package: dict) -> dict:
    payload = {
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
        "source_live_model_call_allowed": bool_value(package, "live_model_call_allowed"),
        "source_live_source_retrieval_allowed": bool_value(
            package, "live_source_retrieval_allowed"
        ),
        "source_measurement_execution_allowed": bool_value(
            package, "measurement_execution_allowed"
        ),
    }
    badges = safety_badges_from_package(package)
    return view_model_section(
        "safety_panel",
        title="Safety and constraints",
        payload=payload,
        summary_text="Live calls, source retrieval and measurements are disabled.",
        badges=badges,
    )


def candidate_summary_card(candidate_summary: dict) -> dict:
    candidate_id = str(candidate_summary.get("candidate_id", "unknown"))
    status = str(candidate_summary.get("coverage_status", ""))
    metrics = {
        "criterion_count": _safe_int(candidate_summary.get("criterion_count", 0)),
        "populated_value_count": _safe_int(
            candidate_summary.get("populated_value_count", 0)
        ),
        "placeholder_value_count": _safe_int(
            candidate_summary.get("placeholder_value_count", 0)
        ),
        "evidence_gap_count": _safe_int(candidate_summary.get("evidence_gap_count", 0)),
        "model_gap_count": _safe_int(candidate_summary.get("model_gap_count", 0)),
        "measurement_gap_count": _safe_int(
            candidate_summary.get("measurement_gap_count", 0)
        ),
        "uncertainty_gap_count": _safe_int(
            candidate_summary.get("uncertainty_gap_count", 0)
        ),
    }
    badges = [
        display_badge(
            f"{candidate_id}_{status}",
            badge_type="coverage",
            label=humanise_identifier(status),
            severity=severity_for_coverage_status(status),
            explanation="Candidate criterion coverage status.",
        )
    ]
    if status == "placeholder_only":
        badges.append(
            display_badge(
                f"{candidate_id}_placeholder_only",
                badge_type="placeholder_status",
                label="Placeholder values only",
                severity="warning",
                explanation="Criterion values require later valuation work.",
            )
        )
    detail_rows = _copy_list(candidate_summary.get("criterion_coverage_records", []))
    return {
        "schema_version": SUMMARY_CARD_SCHEMA_VERSION,
        "card_id": f"candidate_summary_{slugify_identifier(candidate_id)}",
        "title": humanise_identifier(candidate_id),
        "subtitle": f"Coverage: {humanise_identifier(status)}",
        "status": status,
        "severity": severity_for_coverage_status(status),
        "metrics": metrics,
        "badges": badges,
        "detail_rows": detail_rows,
        "assumptions": normalise_string_list(candidate_summary.get("assumptions", [])),
        "warnings": normalise_string_list(candidate_summary.get("warnings", [])),
    }


def candidate_summary_cards_from_package(package: dict) -> list[dict]:
    summaries = package.get("candidate_coverage_summaries", [])
    if not isinstance(summaries, list):
        return []
    return [
        candidate_summary_card(summary)
        for summary in summaries
        if isinstance(summary, dict)
    ]


def criterion_value_row(candidate_id: str, criterion_value: dict) -> dict:
    criterion_id = str(criterion_value.get("criterion_id", "unknown"))
    value_type = str(criterion_value.get("value_type", ""))
    valuation_status = str(criterion_value.get("valuation_status", ""))
    status = value_type or valuation_status
    severity = "warning" if status in {"pending", "placeholder", "placeholder_only"} else "info"
    cells = {
        "criterion_id": criterion_id,
        "criterion_label": str(
            criterion_value.get("criterion_label", humanise_identifier(criterion_id))
        ),
        "criterion_family": str(criterion_value.get("criterion_family", "")),
        "value_type": value_type,
        "estimated_value": _display_safe_copy(criterion_value.get("estimated_value", "")),
        "confidence": str(criterion_value.get("confidence", "")),
        "uncertainty_level": str(criterion_value.get("uncertainty_level", "")),
        "valuation_status": valuation_status,
    }
    return {
        "schema_version": TABLE_ROW_SCHEMA_VERSION,
        "row_id": (
            "criterion_value_"
            f"{slugify_identifier(candidate_id)}_{slugify_identifier(criterion_id)}"
        ),
        "row_type": "criterion_value",
        "candidate_id": str(candidate_id),
        "primary_label": cells["criterion_label"],
        "secondary_label": humanise_identifier(candidate_id),
        "status": status,
        "severity": severity,
        "cells": cells,
        "badges": [
            display_badge(
                f"{candidate_id}_{criterion_id}_{status}",
                badge_type="placeholder_status"
                if severity == "warning"
                else "coverage",
                label=humanise_identifier(status),
                severity=severity,
                explanation="Criterion value display status.",
            )
        ],
        "assumptions": normalise_string_list(criterion_value.get("assumptions", [])),
        "warnings": normalise_string_list(criterion_value.get("warnings", [])),
    }


def criterion_value_rows_from_package(package: dict) -> list[dict]:
    value_sets = package.get("candidate_value_sets", [])
    if not isinstance(value_sets, list):
        return []
    rows: list[dict] = []
    for value_set in value_sets:
        if not isinstance(value_set, dict):
            continue
        candidate_id = str(value_set.get("candidate_id", "unknown"))
        criterion_values = value_set.get("criterion_values", [])
        if not isinstance(criterion_values, list):
            continue
        rows.extend(
            criterion_value_row(candidate_id, criterion_value)
            for criterion_value in criterion_values
            if isinstance(criterion_value, dict)
        )
    return rows


def evidence_gap_row(gap: dict) -> dict:
    gap_id = str(gap.get("gap_id", "unknown"))
    gap_type = str(gap.get("gap_type", ""))
    gap_severity = str(gap.get("severity", ""))
    cells = {
        "gap_id": gap_id,
        "gap_type": gap_type,
        "severity": gap_severity,
        "next_action_type": str(gap.get("next_action_type", "")),
        "reason": str(gap.get("reason", "")),
        "suitable_for_deterministic_estimator": bool_value(
            gap, "suitable_for_deterministic_estimator"
        ),
        "suitable_for_computational_model": bool_value(
            gap, "suitable_for_computational_model"
        ),
        "suitable_for_measurement_feedback": bool_value(
            gap, "suitable_for_measurement_feedback"
        ),
    }
    severity = "critical" if gap_severity in {"critical", "high"} else "warning"
    return {
        "schema_version": TABLE_ROW_SCHEMA_VERSION,
        "row_id": f"evidence_gap_{slugify_identifier(gap_id)}",
        "row_type": "evidence_gap",
        "candidate_id": str(gap.get("candidate_id", "")),
        "primary_label": humanise_identifier(gap_type),
        "secondary_label": str(gap.get("criterion_id", "")),
        "status": gap_type,
        "severity": severity,
        "cells": cells,
        "badges": [
            display_badge(
                f"{gap_id}_{gap_type}",
                badge_type="evidence_gap",
                label=humanise_identifier(gap_type),
                severity=severity,
                explanation="Evidence gap type for review planning.",
            )
        ],
        "assumptions": normalise_string_list(gap.get("assumptions", [])),
        "warnings": normalise_string_list(gap.get("warnings", [])),
    }


def evidence_gap_rows_from_package(package: dict) -> list[dict]:
    gaps = package.get("evidence_gap_records", [])
    if not isinstance(gaps, list):
        return []
    return [evidence_gap_row(gap) for gap in gaps if isinstance(gap, dict)]


def action_worklist_row(action: dict) -> dict:
    action_id = str(action.get("action_id", "unknown"))
    action_type = str(action.get("action_type", ""))
    action_status = str(action.get("action_status", ""))
    cells = {
        "action_id": action_id,
        "action_type": action_type,
        "action_status": action_status,
        "priority": str(action.get("priority", "")),
        "expected_output_record_type": str(
            action.get("expected_output_record_type", "")
        ),
        "gap_type": str(action.get("gap_type", "")),
        "gap_severity": str(action.get("gap_severity", "")),
        "downstream_use": _copy_list(action.get("downstream_use", [])),
    }
    severity = severity_for_action_status(action_status)
    return {
        "schema_version": TABLE_ROW_SCHEMA_VERSION,
        "row_id": f"action_worklist_{slugify_identifier(action_id)}",
        "row_type": "action_worklist",
        "candidate_id": str(action.get("candidate_id", "")),
        "primary_label": humanise_identifier(action_type),
        "secondary_label": str(action.get("criterion_id", "")),
        "status": action_status,
        "severity": severity,
        "cells": cells,
        "badges": [
            display_badge(
                f"{action_id}_{action_type}",
                badge_type="action_type",
                label=humanise_identifier(action_type),
                severity=severity,
                explanation="Action type for evidence-gap worklist planning.",
            )
        ],
        "assumptions": normalise_string_list(action.get("assumptions", [])),
        "warnings": normalise_string_list(action.get("warnings", [])),
    }


def action_worklist_rows_from_package(package: dict) -> list[dict]:
    actions = package.get("action_work_items", [])
    if not isinstance(actions, list):
        return []
    return [action_worklist_row(action) for action in actions if isinstance(action, dict)]


def review_use_case_panel_from_package(package: dict) -> dict:
    readiness_summary = package.get("readiness_summary", {})
    use_cases = (
        normalise_string_list(readiness_summary.get("review_use_cases", []))
        if isinstance(readiness_summary, dict)
        else []
    )
    payload = [
        {
            "use_case_id": use_case,
            "label": humanise_identifier(use_case),
        }
        for use_case in use_cases
    ]
    return view_model_section(
        "review_use_case_panel",
        title="Review use cases",
        payload=payload,
        summary_text=f"{len(payload)} review use cases available.",
    )


def assumptions_panel_from_package(package: dict) -> dict:
    assumptions = normalise_string_list(package.get("assumptions", []))
    return view_model_section(
        "assumptions_panel",
        title="Assumptions",
        payload=assumptions,
        summary_text=f"{len(assumptions)} assumptions.",
        assumptions=assumptions,
    )


def warnings_panel_from_package(package: dict) -> dict:
    warnings = normalise_string_list(package.get("warnings", []))
    return view_model_section(
        "warnings_panel",
        title="Warnings",
        payload=warnings,
        summary_text=f"{len(warnings)} warnings.",
        warnings=warnings,
    )


def hard_constraints_panel_from_package(package: dict) -> dict:
    hard_constraints = normalise_string_list(package.get("hard_constraints", []))
    badges = [
        display_badge(
            f"constraint_{index}",
            badge_type="constraint",
            label="Hard constraint",
            severity="warning",
            explanation=constraint,
        )
        for index, constraint in enumerate(hard_constraints)
    ]
    return view_model_section(
        "hard_constraints_panel",
        title="Hard constraints",
        payload=hard_constraints,
        summary_text=f"{len(hard_constraints)} hard constraints.",
        badges=badges,
    )


def build_criteria_valuation_view_model(package: dict) -> dict:
    source_package = copy.deepcopy(package)
    package_validation = validate_criteria_valuation_package(source_package)
    readiness_panel = readiness_panel_from_package(source_package)
    safety_panel = safety_panel_from_package(source_package)
    candidate_cards = candidate_summary_cards_from_package(source_package)
    criterion_rows = criterion_value_rows_from_package(source_package)
    evidence_rows = evidence_gap_rows_from_package(source_package)
    action_rows = action_worklist_rows_from_package(source_package)
    review_use_case_panel = review_use_case_panel_from_package(source_package)
    assumptions_panel = assumptions_panel_from_package(source_package)
    warnings_panel = warnings_panel_from_package(source_package)
    hard_constraints_panel = hard_constraints_panel_from_package(source_package)

    table_sections = {
        "candidate_summary_cards": view_model_section(
            "candidate_summary_cards",
            title="Candidate summary cards",
            payload=candidate_cards,
            summary_text=f"{len(candidate_cards)} candidate summaries.",
        ),
        "criterion_value_table": view_model_section(
            "criterion_value_table",
            title="Criterion values",
            payload=criterion_rows,
            summary_text=f"{len(criterion_rows)} criterion value rows.",
        ),
        "evidence_gap_table": view_model_section(
            "evidence_gap_table",
            title="Evidence gaps",
            payload=evidence_rows,
            summary_text=f"{len(evidence_rows)} evidence gap rows.",
        ),
        "action_worklist_table": view_model_section(
            "action_worklist_table",
            title="Action worklist",
            payload=action_rows,
            summary_text=f"{len(action_rows)} action worklist rows.",
        ),
    }
    section_by_id = {
        "readiness_panel": readiness_panel,
        "safety_panel": safety_panel,
        "candidate_summary_cards": table_sections["candidate_summary_cards"],
        "criterion_value_table": table_sections["criterion_value_table"],
        "evidence_gap_table": table_sections["evidence_gap_table"],
        "action_worklist_table": table_sections["action_worklist_table"],
        "review_use_case_panel": review_use_case_panel,
        "assumptions_panel": assumptions_panel,
        "warnings_panel": warnings_panel,
        "hard_constraints_panel": hard_constraints_panel,
    }
    assumptions = unique_preserve_order(
        normalise_string_list(source_package.get("assumptions", []))
        + ["Criteria valuation view model derived from CriteriaValuationPackage."]
    )
    warnings = unique_preserve_order(
        normalise_string_list(source_package.get("warnings", []))
        + normalise_string_list(package_validation.get("warnings", []))
    )
    readiness_summary = source_package.get("readiness_summary", {})
    readiness_level = (
        str(readiness_summary.get("readiness_level", ""))
        if isinstance(readiness_summary, dict)
        else ""
    )
    badges = safety_badges_from_package(source_package) + readiness_badges_from_package(
        source_package
    )
    return {
        "schema_version": CRITERIA_VALUATION_VIEW_MODEL_SCHEMA_VERSION,
        "source_package_schema_version": str(source_package.get("schema_version", "")),
        "package_status": str(source_package.get("package_status", "")),
        "readiness_level": readiness_level,
        "sections": [section_by_id[section_id] for section_id in VIEW_MODEL_SECTION_IDS],
        "readiness_panel": readiness_panel,
        "safety_panel": safety_panel,
        "candidate_summary_cards": candidate_cards,
        "criterion_value_rows": criterion_rows,
        "evidence_gap_rows": evidence_rows,
        "action_worklist_rows": action_rows,
        "review_use_case_panel": review_use_case_panel,
        "assumptions_panel": assumptions_panel,
        "warnings_panel": warnings_panel,
        "hard_constraints_panel": hard_constraints_panel,
        "badges": badges,
        "candidate_count": _safe_int(source_package.get("candidate_count", 0)),
        "criterion_value_row_count": len(criterion_rows),
        "evidence_gap_row_count": len(evidence_rows),
        "action_worklist_row_count": len(action_rows),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
    }


def _find_forbidden_fields(
    value: object, forbidden_fields: tuple[str, ...], path: str = "root"
) -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            if key_text in forbidden_fields:
                hits.append(nested_path)
            hits.extend(_find_forbidden_fields(nested, forbidden_fields, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            hits.extend(_find_forbidden_fields(nested, forbidden_fields, f"{path}[{index}]"))
    return hits


def _append_forbidden_field_errors(errors: list[str], value: object) -> None:
    claim_hits = _find_forbidden_fields(value, _FORBIDDEN_CLAIM_FIELDS)
    if claim_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(claim_hits)
        )
    ranking_hits = _find_forbidden_fields(value, _FORBIDDEN_RANKING_FIELDS)
    if ranking_hits:
        errors.append(
            "Forbidden ranking, winner or score fields are present: "
            + ", ".join(ranking_hits)
        )


def _append_row_runtime_field_errors(errors: list[str], value: object) -> None:
    runtime_hits = _find_forbidden_fields(value, _FORBIDDEN_ROW_RUNTIME_FIELDS)
    if runtime_hits:
        errors.append(
            "Forbidden live-call or measurement control fields are present in row: "
            + ", ".join(runtime_hits)
        )


def _validation_result(errors: list[str], warnings: list[str]) -> dict:
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def validate_badge(badge: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(badge, dict):
        return {
            "is_valid": False,
            "errors": ["Badge must be a dictionary."],
            "warnings": [],
        }
    if badge.get("schema_version") != BADGE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {BADGE_SCHEMA_VERSION}.")
    for field_name in REQUIRED_BADGE_FIELDS:
        if field_name not in badge:
            errors.append(f"{field_name} is required.")
    if badge.get("badge_type") not in BADGE_TYPES:
        errors.append("badge_type must be controlled.")
    if badge.get("severity") not in DISPLAY_SEVERITIES:
        errors.append("severity must be controlled.")
    _append_forbidden_field_errors(errors, badge)
    return _validation_result(errors, warnings)


def validate_view_model_section(section: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(section, dict):
        return {
            "is_valid": False,
            "errors": ["View model section must be a dictionary."],
            "warnings": [],
        }
    if section.get("schema_version") != VIEW_MODEL_SECTION_SCHEMA_VERSION:
        errors.append(f"schema_version must be {VIEW_MODEL_SECTION_SCHEMA_VERSION}.")
    for field_name in REQUIRED_SECTION_FIELDS:
        if field_name not in section:
            errors.append(f"{field_name} is required.")
    if section.get("section_id") not in VIEW_MODEL_SECTION_IDS:
        errors.append("section_id must be controlled.")
    if section.get("section_status") not in VIEW_MODEL_SECTION_STATUSES:
        errors.append("section_status must be controlled.")
    if not isinstance(section.get("item_count"), int):
        errors.append("item_count must be an integer.")
    badges = section.get("badges")
    if not isinstance(badges, list):
        errors.append("badges must be a list.")
    else:
        for index, badge in enumerate(badges):
            validation = validate_badge(badge)
            if validation["errors"]:
                errors.append(
                    f"badges[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])
    if section.get("section_status") == "empty":
        warnings.append("View model section is empty.")
    _append_forbidden_field_errors(errors, section)
    return _validation_result(errors, warnings)


def validate_summary_card(card: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(card, dict):
        return {
            "is_valid": False,
            "errors": ["Summary card must be a dictionary."],
            "warnings": [],
        }
    if card.get("schema_version") != SUMMARY_CARD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {SUMMARY_CARD_SCHEMA_VERSION}.")
    for field_name in REQUIRED_SUMMARY_CARD_FIELDS:
        if field_name not in card:
            errors.append(f"{field_name} is required.")
    if card.get("severity") not in DISPLAY_SEVERITIES:
        errors.append("severity must be controlled.")
    if not isinstance(card.get("metrics"), dict):
        errors.append("metrics must be a dictionary.")
    if not isinstance(card.get("badges"), list):
        errors.append("badges must be a list.")
    if not isinstance(card.get("detail_rows"), list):
        errors.append("detail_rows must be a list.")
    _append_forbidden_field_errors(errors, card)
    return _validation_result(errors, warnings)


def validate_table_row(row: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(row, dict):
        return {
            "is_valid": False,
            "errors": ["Table row must be a dictionary."],
            "warnings": [],
        }
    if row.get("schema_version") != TABLE_ROW_SCHEMA_VERSION:
        errors.append(f"schema_version must be {TABLE_ROW_SCHEMA_VERSION}.")
    for field_name in REQUIRED_TABLE_ROW_FIELDS:
        if field_name not in row:
            errors.append(f"{field_name} is required.")
    if not isinstance(row.get("row_id"), str) or not row.get("row_id"):
        errors.append("row_id must be a non-empty string.")
    if not isinstance(row.get("row_type"), str) or not row.get("row_type"):
        errors.append("row_type must be a non-empty string.")
    if "candidate_id" not in row:
        errors.append("candidate_id must exist.")
    if row.get("severity") not in DISPLAY_SEVERITIES:
        errors.append("severity must be controlled.")
    if not isinstance(row.get("cells"), dict):
        errors.append("cells must be a dictionary.")
    if not isinstance(row.get("badges"), list):
        errors.append("badges must be a list.")
    _append_forbidden_field_errors(errors, row)
    _append_row_runtime_field_errors(errors, row)
    return _validation_result(errors, warnings)


def validate_criteria_valuation_view_model(view_model: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(view_model, dict):
        return {
            "is_valid": False,
            "errors": ["Criteria valuation view model must be a dictionary."],
            "warnings": [],
        }
    if view_model.get("schema_version") != CRITERIA_VALUATION_VIEW_MODEL_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {CRITERIA_VALUATION_VIEW_MODEL_SCHEMA_VERSION}."
        )
    for field_name in REQUIRED_VIEW_MODEL_FIELDS:
        if field_name not in view_model:
            errors.append(f"{field_name} is required.")
    if not isinstance(view_model.get("sections"), list):
        errors.append("sections must be a list.")
    if not isinstance(view_model.get("readiness_panel"), dict):
        errors.append("readiness_panel must be a dictionary.")
    if not isinstance(view_model.get("safety_panel"), dict):
        errors.append("safety_panel must be a dictionary.")
    for field_name in (
        "candidate_summary_cards",
        "criterion_value_rows",
        "evidence_gap_rows",
        "action_worklist_rows",
        "badges",
    ):
        if not isinstance(view_model.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    if view_model.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if view_model.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if view_model.get("measurement_execution_allowed") is not False:
        errors.append("measurement_execution_allowed must be false.")

    sections = view_model.get("sections", [])
    if isinstance(sections, list):
        for index, section in enumerate(sections):
            validation = validate_view_model_section(section)
            if validation["errors"]:
                errors.append(
                    f"sections[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])

    cards = view_model.get("candidate_summary_cards", [])
    if isinstance(cards, list):
        for index, card in enumerate(cards):
            validation = validate_summary_card(card)
            if validation["errors"]:
                errors.append(
                    f"candidate_summary_cards[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])

    for field_name in (
        "criterion_value_rows",
        "evidence_gap_rows",
        "action_worklist_rows",
    ):
        rows = view_model.get(field_name, [])
        if isinstance(rows, list):
            for index, row in enumerate(rows):
                validation = validate_table_row(row)
                if validation["errors"]:
                    errors.append(
                        f"{field_name}[{index}] failed validation: "
                        + "; ".join(validation["errors"])
                    )
                warnings.extend(validation["warnings"])

    badges = view_model.get("badges", [])
    if isinstance(badges, list):
        for index, badge in enumerate(badges):
            validation = validate_badge(badge)
            if validation["errors"]:
                errors.append(
                    f"badges[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])

    if isinstance(view_model.get("candidate_summary_cards"), list) and not view_model.get(
        "candidate_summary_cards"
    ):
        warnings.append("Candidate summary cards are empty.")
    if isinstance(view_model.get("criterion_value_rows"), list) and not view_model.get(
        "criterion_value_rows"
    ):
        warnings.append("Criterion value rows are empty.")
    _append_forbidden_field_errors(errors, view_model)
    return _validation_result(errors, warnings)


def criteria_valuation_view_model_summary(view_model: dict) -> dict:
    warnings = view_model.get("warnings", [])
    return {
        "schema_version": view_model.get("schema_version", ""),
        "package_status": view_model.get("package_status", ""),
        "readiness_level": view_model.get("readiness_level", ""),
        "section_count": safe_count(view_model.get("sections", [])),
        "candidate_count": _safe_int(view_model.get("candidate_count", 0)),
        "candidate_summary_card_count": safe_count(
            view_model.get("candidate_summary_cards", [])
        ),
        "criterion_value_row_count": _safe_int(
            view_model.get("criterion_value_row_count", 0)
        ),
        "evidence_gap_row_count": _safe_int(view_model.get("evidence_gap_row_count", 0)),
        "action_worklist_row_count": _safe_int(
            view_model.get("action_worklist_row_count", 0)
        ),
        "badge_count": safe_count(view_model.get("badges", [])),
        "live_model_call_allowed": bool_value(view_model, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(
            view_model, "live_source_retrieval_allowed"
        ),
        "measurement_execution_allowed": bool_value(
            view_model, "measurement_execution_allowed"
        ),
        "warning_count": safe_count(warnings),
    }


def hot_section_demo_criteria_valuation_view_model() -> dict:
    return build_criteria_valuation_view_model(
        hot_section_demo_criteria_valuation_package()
    )
