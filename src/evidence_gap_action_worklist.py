from __future__ import annotations

import copy
import re
from typing import TypedDict

from src.criteria_coverage_summary import (
    hot_section_demo_criteria_coverage_summary_plan,
    validate_criteria_coverage_summary_plan,
    validate_evidence_gap_record,
)


EVIDENCE_GAP_ACTION_WORKLIST_PLAN_SCHEMA_VERSION = (
    "evidence_gap_action_worklist_plan_v1"
)
EVIDENCE_GAP_ACTION_WORK_ITEM_SCHEMA_VERSION = "evidence_gap_action_work_item_v1"

ACTION_WORK_ITEM_STATUSES: tuple[str, ...] = (
    "planned",
    "placeholder_only",
    "blocked_invalid_gap",
    "blocked_not_permitted",
    "deferred",
)

ACTION_TYPES: tuple[str, ...] = (
    "deterministic_estimator",
    "computational_model",
    "literature_evidence_review",
    "measurement_feedback",
    "engineering_review",
)

ACTION_PRIORITIES: tuple[str, ...] = ("low", "medium", "high")

EXPECTED_OUTPUT_RECORD_TYPES: tuple[str, ...] = (
    "criterion_value_update",
    "evidence_basis_update",
    "uncertainty_update",
    "model_provenance_update",
    "measurement_feedback_update",
    "engineering_review_note",
)

GAP_TYPE_TO_DEFAULT_ACTION_TYPE: dict[str, str] = {
    "placeholder_value": "deterministic_estimator",
    "missing_evidence_basis": "literature_evidence_review",
    "placeholder_evidence_basis": "literature_evidence_review",
    "low_confidence": "literature_evidence_review",
    "high_uncertainty": "computational_model",
    "missing_uncertainty_assessment": "deterministic_estimator",
    "missing_model_provenance": "computational_model",
    "missing_measurement_feedback": "measurement_feedback",
    "invalid_criterion_value": "engineering_review",
}

GAP_TYPE_TO_EXPECTED_OUTPUT_RECORD_TYPE: dict[str, str] = {
    "placeholder_value": "criterion_value_update",
    "missing_evidence_basis": "evidence_basis_update",
    "placeholder_evidence_basis": "evidence_basis_update",
    "low_confidence": "evidence_basis_update",
    "high_uncertainty": "uncertainty_update",
    "missing_uncertainty_assessment": "uncertainty_update",
    "missing_model_provenance": "model_provenance_update",
    "missing_measurement_feedback": "measurement_feedback_update",
    "invalid_criterion_value": "engineering_review_note",
}

ACTION_TYPE_TO_LABEL: dict[str, str] = {
    "deterministic_estimator": "Deterministic estimator action",
    "computational_model": "Computational model placeholder action",
    "literature_evidence_review": "Literature evidence review action",
    "measurement_feedback": "Measurement feedback placeholder action",
    "engineering_review": "Engineering review action",
}

REQUIRED_ACTION_WORK_ITEM_FIELDS: tuple[str, ...] = (
    "schema_version",
    "action_id",
    "action_type",
    "action_label",
    "action_status",
    "priority",
    "candidate_id",
    "criterion_id",
    "gap_id",
    "gap_type",
    "gap_severity",
    "gap_reason",
    "expected_output_record_type",
    "required_input_records",
    "downstream_use",
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "measurement_execution_allowed",
    "assumptions",
    "warnings",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)


class EvidenceGapActionWorkItem(TypedDict, total=False):
    schema_version: str
    action_id: str
    action_type: str
    action_label: str
    action_status: str
    priority: str
    candidate_id: str
    criterion_id: str
    gap_id: str
    gap_type: str
    gap_severity: str
    gap_reason: str
    expected_output_record_type: str
    required_input_records: list[str]
    downstream_use: list[str]
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    measurement_execution_allowed: bool
    assumptions: list[str]
    warnings: list[str]


class EvidenceGapActionWorklistPlan(TypedDict, total=False):
    schema_version: str
    source_criteria_coverage_summary_plan_version: str
    action_work_items: list[dict]
    action_work_items_by_candidate: dict[str, list[dict]]
    action_type_counts: dict[str, int]
    candidate_count: int
    action_work_item_count: int
    deterministic_action_count: int
    computational_model_placeholder_count: int
    literature_review_action_count: int
    measurement_feedback_placeholder_count: int
    engineering_review_action_count: int
    blocked_action_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    measurement_execution_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class EvidenceGapActionWorklistValidationResult(TypedDict, total=False):
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


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def normalise_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return unique_preserve_order([str(value) for value in values])


def evidence_gap_records_from_plan(plan: dict) -> list[dict]:
    records = plan.get("evidence_gap_records", []) if isinstance(plan, dict) else []
    if isinstance(records, list) and records:
        return copy.deepcopy([record for record in records if isinstance(record, dict)])

    collected: list[dict] = []
    summaries = plan.get("candidate_coverage_summaries", []) if isinstance(plan, dict) else []
    if not isinstance(summaries, list):
        return []
    for summary in summaries:
        if not isinstance(summary, dict):
            continue
        summary_records = summary.get("evidence_gap_records", [])
        if isinstance(summary_records, list):
            collected.extend(
                copy.deepcopy([record for record in summary_records if isinstance(record, dict)])
            )
    return collected


def action_type_for_gap(gap: dict) -> str:
    gap_type = gap.get("gap_type") if isinstance(gap, dict) else None
    if str(gap_type) in GAP_TYPE_TO_DEFAULT_ACTION_TYPE:
        return GAP_TYPE_TO_DEFAULT_ACTION_TYPE[str(gap_type)]
    next_action = gap.get("next_action_type") if isinstance(gap, dict) else None
    if next_action in ACTION_TYPES:
        return str(next_action)
    return "engineering_review"


def expected_output_record_type_for_gap(gap: dict) -> str:
    gap_type = gap.get("gap_type") if isinstance(gap, dict) else None
    return GAP_TYPE_TO_EXPECTED_OUTPUT_RECORD_TYPE.get(
        str(gap_type), "engineering_review_note"
    )


def action_priority_for_gap(gap: dict) -> str:
    gap_type = str(gap.get("gap_type", "")) if isinstance(gap, dict) else ""
    if gap_type in {"invalid_criterion_value", "high_uncertainty"}:
        return "high"
    severity = gap.get("severity") if isinstance(gap, dict) else None
    return str(severity) if severity in ACTION_PRIORITIES else "medium"


def action_id_for_gap(gap: dict) -> str:
    return "action_" + "_".join(
        [
            slugify_identifier(gap.get("candidate_id", "") if isinstance(gap, dict) else ""),
            slugify_identifier(gap.get("criterion_id", "") if isinstance(gap, dict) else ""),
            slugify_identifier(gap.get("gap_type", "") if isinstance(gap, dict) else ""),
        ]
    )


def action_status_for_gap(gap: dict, action_type: str) -> str:
    validation = validate_evidence_gap_record(gap)
    if validation["errors"]:
        return "blocked_invalid_gap"
    if action_type in {"computational_model", "measurement_feedback"}:
        return "placeholder_only"
    return "planned"


def required_input_records_for_action(gap: dict, action_type: str) -> list[str]:
    records = ["evidence_gap_record"]
    if action_type == "deterministic_estimator":
        records.extend(
            [
                "candidate_criteria_valuation_work_item",
                "deterministic_estimator_request",
            ]
        )
    elif action_type == "computational_model":
        records.extend(["candidate_record", "model_adapter_contract", "criterion_value"])
    elif action_type == "literature_evidence_review":
        records.extend(["criterion_definition", "source_evidence_reference"])
    elif action_type == "measurement_feedback":
        records.extend(["measurement_target_record", "measurement_feedback_contract"])
    elif action_type == "engineering_review":
        records.extend(["candidate_record", "criterion_value", "evidence_gap_record"])
    return unique_preserve_order(records)


def downstream_use_for_action(gap: dict, action_type: str) -> list[str]:
    if action_type == "deterministic_estimator":
        uses = ["criteria_value_update", "criteria_result_integration"]
    elif action_type == "computational_model":
        uses = ["future_model_supported_estimate", "uncertainty_reduction"]
    elif action_type == "literature_evidence_review":
        uses = ["evidence_basis_update", "confidence_update"]
    elif action_type == "measurement_feedback":
        uses = ["measurement_feedback_loop", "model_confidence_update"]
    elif action_type == "engineering_review":
        uses = ["engineering_decision_support", "safety_review"]
    else:
        uses = []
    return unique_preserve_order(uses)


def evidence_gap_action_work_item(gap: dict) -> dict:
    copied_gap = copy.deepcopy(gap)
    validation = validate_evidence_gap_record(copied_gap)
    action_type = action_type_for_gap(copied_gap)
    warnings = normalise_string_list(copied_gap.get("warnings", []))
    warnings.extend([str(error) for error in validation.get("errors", [])])
    warnings.extend([str(warning) for warning in validation.get("warnings", [])])
    warnings = unique_preserve_order(warnings)
    return {
        "schema_version": EVIDENCE_GAP_ACTION_WORK_ITEM_SCHEMA_VERSION,
        "action_id": action_id_for_gap(copied_gap),
        "action_type": action_type,
        "action_label": ACTION_TYPE_TO_LABEL.get(
            action_type, "Engineering review action"
        ),
        "action_status": action_status_for_gap(copied_gap, action_type),
        "priority": action_priority_for_gap(copied_gap),
        "candidate_id": str(copied_gap.get("candidate_id", "")),
        "criterion_id": str(copied_gap.get("criterion_id", "")),
        "gap_id": str(copied_gap.get("gap_id", "")),
        "gap_type": str(copied_gap.get("gap_type", "")),
        "gap_severity": str(copied_gap.get("severity", "medium")),
        "gap_reason": str(copied_gap.get("reason", "")),
        "expected_output_record_type": expected_output_record_type_for_gap(copied_gap),
        "required_input_records": required_input_records_for_action(
            copied_gap, action_type
        ),
        "downstream_use": downstream_use_for_action(copied_gap, action_type),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
        "assumptions": [
            "Evidence-gap action is a worklist contract only; no action has been executed."
        ],
        "warnings": warnings,
    }


def evidence_gap_action_work_items_from_plan(plan: dict) -> list[dict]:
    items: list[dict] = []
    seen_action_ids: set[str] = set()
    for gap in evidence_gap_records_from_plan(plan):
        item = evidence_gap_action_work_item(gap)
        action_id = item.get("action_id", "")
        if action_id in seen_action_ids:
            item["action_status"] = "blocked_not_permitted"
            item["warnings"] = unique_preserve_order(
                normalise_string_list(item.get("warnings", [])) + ["Duplicate action id."]
            )
        else:
            seen_action_ids.add(str(action_id))
        items.append(item)
    return items


def action_work_items_by_candidate(action_work_items: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for item in action_work_items:
        if not isinstance(item, dict):
            continue
        candidate_id = item.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id:
            grouped.setdefault(candidate_id, []).append(copy.deepcopy(item))
    return grouped


def action_type_counts(action_work_items: list[dict]) -> dict[str, int]:
    counts = {action_type: 0 for action_type in ACTION_TYPES}
    for item in action_work_items:
        if isinstance(item, dict) and item.get("action_type") in counts:
            counts[str(item["action_type"])] += 1
    return counts


def build_evidence_gap_action_worklist_plan(coverage_plan: dict) -> dict:
    validation = validate_criteria_coverage_summary_plan(coverage_plan)
    items = evidence_gap_action_work_items_from_plan(coverage_plan)
    grouped_items = action_work_items_by_candidate(items)
    counts = action_type_counts(items)
    assumptions = unique_preserve_order(
        normalise_string_list(coverage_plan.get("assumptions", []))
        + ["Evidence-gap action worklist derived from CriteriaCoverageSummaryPlan."]
    )
    warnings = unique_preserve_order(
        normalise_string_list(coverage_plan.get("warnings", []))
        + normalise_string_list(validation.get("warnings", []))
    )
    blocked_count = len(
        [
            item
            for item in items
            if item.get("action_status")
            in {"blocked_invalid_gap", "blocked_not_permitted"}
        ]
    )
    return {
        "schema_version": EVIDENCE_GAP_ACTION_WORKLIST_PLAN_SCHEMA_VERSION,
        "source_criteria_coverage_summary_plan_version": str(
            coverage_plan.get("schema_version", "")
        ),
        "action_work_items": items,
        "action_work_items_by_candidate": grouped_items,
        "action_type_counts": counts,
        "candidate_count": len(grouped_items),
        "action_work_item_count": len(items),
        "deterministic_action_count": counts["deterministic_estimator"],
        "computational_model_placeholder_count": counts["computational_model"],
        "literature_review_action_count": counts["literature_evidence_review"],
        "measurement_feedback_placeholder_count": counts["measurement_feedback"],
        "engineering_review_action_count": counts["engineering_review"],
        "blocked_action_count": blocked_count,
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": normalise_string_list(
            coverage_plan.get("hard_constraints", [])
        ),
    }


def _find_forbidden_claim_fields(value: object, path: str = "root") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            nested_path = f"{path}.{key_text}"
            if key_text in _FORBIDDEN_CLAIM_FIELDS:
                hits.append(nested_path)
            hits.extend(_find_forbidden_claim_fields(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            hits.extend(_find_forbidden_claim_fields(nested, f"{path}[{index}]"))
    return hits


def validate_action_work_item(item: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(item, dict):
        return {
            "is_valid": False,
            "errors": ["Action work item must be a dictionary."],
            "warnings": [],
        }
    if item.get("schema_version") != EVIDENCE_GAP_ACTION_WORK_ITEM_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {EVIDENCE_GAP_ACTION_WORK_ITEM_SCHEMA_VERSION}."
        )
    for field_name in REQUIRED_ACTION_WORK_ITEM_FIELDS:
        if field_name not in item:
            errors.append(f"{field_name} is required.")
    for field_name in ("action_id", "candidate_id", "criterion_id", "gap_id"):
        if not isinstance(item.get(field_name), str) or not item.get(field_name):
            errors.append(f"{field_name} must be a non-empty string.")
    if item.get("action_type") not in ACTION_TYPES:
        errors.append("action_type must be controlled.")
    if item.get("action_status") not in ACTION_WORK_ITEM_STATUSES:
        errors.append("action_status must be controlled.")
    if item.get("priority") not in ACTION_PRIORITIES:
        errors.append("priority must be controlled.")
    if item.get("expected_output_record_type") not in EXPECTED_OUTPUT_RECORD_TYPES:
        errors.append("expected_output_record_type must be controlled.")
    if not isinstance(item.get("required_input_records"), list):
        errors.append("required_input_records must be a list.")
    if not isinstance(item.get("downstream_use"), list):
        errors.append("downstream_use must be a list.")
    if item.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if item.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if item.get("measurement_execution_allowed") is not False:
        errors.append("measurement_execution_allowed must be false.")
    forbidden_hits = _find_forbidden_claim_fields(item)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_evidence_gap_action_worklist_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Evidence-gap action worklist plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != EVIDENCE_GAP_ACTION_WORKLIST_PLAN_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {EVIDENCE_GAP_ACTION_WORKLIST_PLAN_SCHEMA_VERSION}."
        )
    if not isinstance(plan.get("action_work_items"), list):
        errors.append("action_work_items must be a list.")
    if not isinstance(plan.get("action_work_items_by_candidate"), dict):
        errors.append("action_work_items_by_candidate must be a dictionary.")
    if not isinstance(plan.get("action_type_counts"), dict):
        errors.append("action_type_counts must be a dictionary.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if plan.get("measurement_execution_allowed") is not False:
        errors.append("measurement_execution_allowed must be false.")

    items = plan.get("action_work_items", [])
    if isinstance(items, list):
        if not items:
            warnings.append("No action work items are present.")
        for index, item in enumerate(items):
            validation = validate_action_work_item(item)
            if validation["errors"]:
                errors.append(
                    f"action_work_items[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])
        if items and all(
            isinstance(item, dict) and item.get("action_status") == "placeholder_only"
            for item in items
        ):
            warnings.append("All action work items are placeholder-only.")
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def evidence_gap_action_worklist_summary(plan: dict) -> dict:
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "candidate_count": int(plan.get("candidate_count", 0)),
        "action_work_item_count": int(plan.get("action_work_item_count", 0)),
        "deterministic_action_count": int(plan.get("deterministic_action_count", 0)),
        "computational_model_placeholder_count": int(
            plan.get("computational_model_placeholder_count", 0)
        ),
        "literature_review_action_count": int(
            plan.get("literature_review_action_count", 0)
        ),
        "measurement_feedback_placeholder_count": int(
            plan.get("measurement_feedback_placeholder_count", 0)
        ),
        "engineering_review_action_count": int(
            plan.get("engineering_review_action_count", 0)
        ),
        "blocked_action_count": int(plan.get("blocked_action_count", 0)),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(
            plan, "live_source_retrieval_allowed"
        ),
        "measurement_execution_allowed": bool_value(
            plan, "measurement_execution_allowed"
        ),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_evidence_gap_action_worklist_plan() -> dict:
    return build_evidence_gap_action_worklist_plan(
        hot_section_demo_criteria_coverage_summary_plan()
    )
