from __future__ import annotations

import copy
import re
from typing import TypedDict

from src.criteria_coverage_summary import (
    hot_section_demo_criteria_coverage_summary_plan,
    validate_criteria_coverage_summary_plan,
)
from src.criteria_result_integration import (
    hot_section_demo_criteria_result_integration_plan,
    validate_criteria_result_integration_plan,
)
from src.evidence_gap_action_worklist import (
    hot_section_demo_evidence_gap_action_worklist_plan,
    validate_evidence_gap_action_worklist_plan,
)


CRITERIA_VALUATION_PACKAGE_SCHEMA_VERSION = "criteria_valuation_package_v1"
PACKAGE_SECTION_SCHEMA_VERSION = "criteria_valuation_package_section_v1"
PACKAGE_READINESS_SUMMARY_SCHEMA_VERSION = (
    "criteria_valuation_package_readiness_summary_v1"
)

PACKAGE_STATUSES: tuple[str, ...] = (
    "contract_ready",
    "placeholder_only",
    "partial_coverage",
    "invalid_input",
    "empty_package",
)

PACKAGE_SECTION_IDS: tuple[str, ...] = (
    "candidate_value_sets",
    "integrated_value_records",
    "candidate_coverage_summaries",
    "portfolio_coverage_summary",
    "evidence_gap_records",
    "action_work_items",
    "action_work_items_by_candidate",
    "assumptions",
    "warnings",
    "hard_constraints",
    "safety_flags",
)

PACKAGE_SECTION_STATUSES: tuple[str, ...] = (
    "present",
    "empty",
    "invalid",
    "placeholder_only",
)

READINESS_LEVELS: tuple[str, ...] = (
    "ready_for_review",
    "ready_with_gaps",
    "placeholder_only",
    "blocked_invalid_input",
    "empty",
)

REVIEW_USE_CASES: tuple[str, ...] = (
    "cockpit_display",
    "engineering_review",
    "evidence_gap_review",
    "estimator_planning",
    "model_adapter_planning",
    "measurement_feedback_planning",
    "export_package",
)

REQUIRED_PACKAGE_SECTION_FIELDS: tuple[str, ...] = (
    "schema_version",
    "section_id",
    "section_label",
    "section_status",
    "item_count",
    "payload",
    "assumptions",
    "warnings",
)

REQUIRED_READINESS_SUMMARY_FIELDS: tuple[str, ...] = (
    "schema_version",
    "readiness_level",
    "candidate_count",
    "candidate_value_set_count",
    "criterion_value_count",
    "populated_value_count",
    "placeholder_value_count",
    "evidence_gap_count",
    "action_work_item_count",
    "deterministic_action_count",
    "computational_model_placeholder_count",
    "literature_review_action_count",
    "measurement_feedback_placeholder_count",
    "engineering_review_action_count",
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "measurement_execution_allowed",
    "review_use_cases",
    "assumptions",
    "warnings",
)

REQUIRED_CRITERIA_VALUATION_PACKAGE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "package_status",
    "source_result_integration_plan_version",
    "source_coverage_summary_plan_version",
    "source_action_worklist_plan_version",
    "readiness_summary",
    "package_sections",
    "candidate_value_sets",
    "integrated_value_records",
    "candidate_coverage_summaries",
    "portfolio_coverage_summary",
    "evidence_gap_records",
    "action_work_items",
    "action_work_items_by_candidate",
    "candidate_count",
    "criterion_value_count",
    "evidence_gap_count",
    "action_work_item_count",
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "measurement_execution_allowed",
    "assumptions",
    "warnings",
    "hard_constraints",
)

_SECTION_LABELS: dict[str, str] = {
    "candidate_value_sets": "Candidate value sets",
    "integrated_value_records": "Integrated value records",
    "candidate_coverage_summaries": "Candidate coverage summaries",
    "portfolio_coverage_summary": "Portfolio coverage summary",
    "evidence_gap_records": "Evidence-gap records",
    "action_work_items": "Action work items",
    "action_work_items_by_candidate": "Action work items by candidate",
    "assumptions": "Assumptions",
    "warnings": "Warnings",
    "hard_constraints": "Hard constraints",
    "safety_flags": "Safety flags",
}

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


class CriteriaValuationPackageSection(TypedDict, total=False):
    schema_version: str
    section_id: str
    section_label: str
    section_status: str
    item_count: int
    payload: object
    assumptions: list[str]
    warnings: list[str]


class CriteriaValuationPackageReadinessSummary(TypedDict, total=False):
    schema_version: str
    readiness_level: str
    candidate_count: int
    candidate_value_set_count: int
    criterion_value_count: int
    populated_value_count: int
    placeholder_value_count: int
    evidence_gap_count: int
    action_work_item_count: int
    deterministic_action_count: int
    computational_model_placeholder_count: int
    literature_review_action_count: int
    measurement_feedback_placeholder_count: int
    engineering_review_action_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    measurement_execution_allowed: bool
    review_use_cases: list[str]
    assumptions: list[str]
    warnings: list[str]


class CriteriaValuationPackage(TypedDict, total=False):
    schema_version: str
    package_status: str
    source_result_integration_plan_version: str
    source_coverage_summary_plan_version: str
    source_action_worklist_plan_version: str
    readiness_summary: dict
    package_sections: list[dict]
    candidate_value_sets: list[dict]
    integrated_value_records: list[dict]
    candidate_coverage_summaries: list[dict]
    portfolio_coverage_summary: dict
    evidence_gap_records: list[dict]
    action_work_items: list[dict]
    action_work_items_by_candidate: dict
    candidate_count: int
    criterion_value_count: int
    evidence_gap_count: int
    action_work_item_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    measurement_execution_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class CriteriaValuationPackageValidationResult(TypedDict, total=False):
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


def deep_copy_list(value: object) -> list:
    return copy.deepcopy(value) if isinstance(value, list) else []


def deep_copy_dict(value: object) -> dict:
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def section_label(section_id: str) -> str:
    return _SECTION_LABELS.get(section_id, humanise_identifier(section_id))


def _item_count(payload: object) -> int:
    if isinstance(payload, (list, dict)):
        return len(payload)
    return 1 if payload else 0


def _payload_appears_placeholder_only(payload: object) -> bool:
    if isinstance(payload, list):
        if not payload:
            return False
        statuses = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            if item.get("value_set_status"):
                statuses.append(item.get("value_set_status") == "placeholder_only")
            elif item.get("integration_status"):
                statuses.append(
                    item.get("integration_status")
                    in {"integrated_placeholder", "fallback_placeholder"}
                )
        return bool(statuses) and all(statuses)
    return False


def package_section(
    section_id: str,
    payload: object,
    *,
    assumptions: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    copied_payload = copy.deepcopy(payload)
    item_count = _item_count(copied_payload)
    if item_count == 0:
        section_status = "empty"
    elif section_id in {"candidate_value_sets", "integrated_value_records"} and (
        _payload_appears_placeholder_only(copied_payload)
    ):
        section_status = "placeholder_only"
    else:
        section_status = "present"
    return {
        "schema_version": PACKAGE_SECTION_SCHEMA_VERSION,
        "section_id": section_id,
        "section_label": section_label(section_id),
        "section_status": section_status,
        "item_count": item_count,
        "payload": copied_payload,
        "assumptions": normalise_string_list(list(assumptions or [])),
        "warnings": normalise_string_list(list(warnings or [])),
    }


def candidate_ids_from_value_sets(value_sets: list[dict]) -> list[str]:
    candidate_ids: list[str] = []
    for value_set in value_sets:
        if not isinstance(value_set, dict):
            continue
        candidate_id = value_set.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id:
            candidate_ids.append(candidate_id)
    return unique_preserve_order(candidate_ids)


def candidate_ids_from_coverage_summaries(summaries: list[dict]) -> list[str]:
    candidate_ids: list[str] = []
    for summary in summaries:
        if not isinstance(summary, dict):
            continue
        candidate_id = summary.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id:
            candidate_ids.append(candidate_id)
    return unique_preserve_order(candidate_ids)


def package_candidate_consistency_warnings(
    result_integration_plan: dict,
    coverage_summary_plan: dict,
    action_worklist_plan: dict,
) -> list[str]:
    warnings: list[str] = []
    result_ids = set(
        candidate_ids_from_value_sets(
            deep_copy_list(result_integration_plan.get("candidate_value_sets", []))
        )
    )
    coverage_ids = set(
        candidate_ids_from_coverage_summaries(
            deep_copy_list(coverage_summary_plan.get("candidate_coverage_summaries", []))
        )
    )
    action_groups = action_worklist_plan.get("action_work_items_by_candidate", {})
    action_ids = set(action_groups.keys()) if isinstance(action_groups, dict) else set()

    if result_ids != coverage_ids:
        warnings.append(
            "Candidate ids differ between result integration and coverage summaries."
        )
    missing_action_ids = coverage_ids - action_ids
    if missing_action_ids:
        warnings.append(
            "Some coverage candidates have no action work items: "
            + ", ".join(sorted(missing_action_ids))
        )
    extra_action_ids = action_ids - coverage_ids
    if extra_action_ids:
        warnings.append(
            "Some action work item candidates are not present in coverage summaries: "
            + ", ".join(sorted(extra_action_ids))
        )
    return warnings


def count_criterion_values(candidate_value_sets: list[dict]) -> int:
    return sum(
        len(value_set.get("criterion_values", []))
        for value_set in candidate_value_sets
        if isinstance(value_set, dict)
        and isinstance(value_set.get("criterion_values", []), list)
    )


def _value_is_placeholder(value: dict) -> bool:
    return (
        isinstance(value, dict)
        and (
            value.get("value_type") == "pending"
            or value.get("estimated_value") == "pending"
            or value.get("valuation_status") == "placeholder_only"
        )
    )


def count_populated_values(candidate_value_sets: list[dict]) -> int:
    total = 0
    for value_set in candidate_value_sets:
        if not isinstance(value_set, dict):
            continue
        if isinstance(value_set.get("populated_value_count"), int):
            total += int(value_set["populated_value_count"])
            continue
        values = value_set.get("criterion_values", [])
        if isinstance(values, list):
            total += len(
                [
                    value
                    for value in values
                    if isinstance(value, dict) and not _value_is_placeholder(value)
                ]
            )
    return total


def count_placeholder_values(candidate_value_sets: list[dict]) -> int:
    total = 0
    for value_set in candidate_value_sets:
        if not isinstance(value_set, dict):
            continue
        if isinstance(value_set.get("placeholder_value_count"), int):
            total += int(value_set["placeholder_value_count"])
            continue
        values = value_set.get("criterion_values", [])
        if isinstance(values, list):
            total += len([value for value in values if _value_is_placeholder(value)])
    return total


def package_status_from_counts(
    candidate_count: int,
    criterion_value_count: int,
    populated_value_count: int,
    placeholder_value_count: int,
    evidence_gap_count: int,
    validation_error_count: int,
) -> str:
    if validation_error_count > 0:
        return "invalid_input"
    if candidate_count == 0 or criterion_value_count == 0:
        return "empty_package"
    if populated_value_count == 0 and placeholder_value_count > 0:
        return "placeholder_only"
    if placeholder_value_count > 0 or evidence_gap_count > 0:
        return "partial_coverage"
    return "contract_ready"


def readiness_level_from_package_status(package_status: str) -> str:
    if package_status == "invalid_input":
        return "blocked_invalid_input"
    if package_status == "empty_package":
        return "empty"
    if package_status == "placeholder_only":
        return "placeholder_only"
    if package_status == "partial_coverage":
        return "ready_with_gaps"
    if package_status == "contract_ready":
        return "ready_for_review"
    return "ready_with_gaps"


def build_readiness_summary(
    *,
    package_status: str,
    candidate_value_sets: list[dict],
    evidence_gap_records: list[dict],
    action_work_items: list[dict],
    action_worklist_plan: dict,
) -> dict:
    action_type_counts = action_worklist_plan.get("action_type_counts", {})
    if not isinstance(action_type_counts, dict):
        action_type_counts = {}

    def action_count(action_type: str) -> int:
        if action_type in action_type_counts:
            return int(action_type_counts[action_type])
        return len(
            [
                item
                for item in action_work_items
                if isinstance(item, dict) and item.get("action_type") == action_type
            ]
        )

    warnings = []
    if not candidate_value_sets:
        warnings.append("No candidate value sets are present.")
    if not action_work_items:
        warnings.append("No action work items are present.")
    return {
        "schema_version": PACKAGE_READINESS_SUMMARY_SCHEMA_VERSION,
        "readiness_level": readiness_level_from_package_status(package_status),
        "candidate_count": len(candidate_value_sets),
        "candidate_value_set_count": len(candidate_value_sets),
        "criterion_value_count": count_criterion_values(candidate_value_sets),
        "populated_value_count": count_populated_values(candidate_value_sets),
        "placeholder_value_count": count_placeholder_values(candidate_value_sets),
        "evidence_gap_count": len(evidence_gap_records),
        "action_work_item_count": len(action_work_items),
        "deterministic_action_count": action_count("deterministic_estimator"),
        "computational_model_placeholder_count": action_count("computational_model"),
        "literature_review_action_count": action_count("literature_evidence_review"),
        "measurement_feedback_placeholder_count": action_count("measurement_feedback"),
        "engineering_review_action_count": action_count("engineering_review"),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
        "review_use_cases": list(REVIEW_USE_CASES),
        "assumptions": ["Readiness summary is for review planning only."],
        "warnings": warnings,
    }


def package_sections_from_payloads(
    *,
    candidate_value_sets: list[dict],
    integrated_value_records: list[dict],
    candidate_coverage_summaries: list[dict],
    portfolio_coverage_summary: dict,
    evidence_gap_records: list[dict],
    action_work_items: list[dict],
    action_work_items_by_candidate: dict,
    assumptions: list[str],
    warnings: list[str],
    hard_constraints: list[str],
) -> list[dict]:
    safety_flags = {
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
    }
    payload_by_section = {
        "candidate_value_sets": candidate_value_sets,
        "integrated_value_records": integrated_value_records,
        "candidate_coverage_summaries": candidate_coverage_summaries,
        "portfolio_coverage_summary": portfolio_coverage_summary,
        "evidence_gap_records": evidence_gap_records,
        "action_work_items": action_work_items,
        "action_work_items_by_candidate": action_work_items_by_candidate,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": hard_constraints,
        "safety_flags": safety_flags,
    }
    return [
        package_section(section_id, payload_by_section[section_id])
        for section_id in PACKAGE_SECTION_IDS
    ]


def build_criteria_valuation_package(
    result_integration_plan: dict,
    coverage_summary_plan: dict,
    action_worklist_plan: dict,
) -> dict:
    result_validation = validate_criteria_result_integration_plan(result_integration_plan)
    coverage_validation = validate_criteria_coverage_summary_plan(coverage_summary_plan)
    action_validation = validate_evidence_gap_action_worklist_plan(action_worklist_plan)
    candidate_value_sets = deep_copy_list(result_integration_plan.get("candidate_value_sets", []))
    integrated_value_records = deep_copy_list(
        result_integration_plan.get("integrated_value_records", [])
    )
    candidate_coverage_summaries = deep_copy_list(
        coverage_summary_plan.get("candidate_coverage_summaries", [])
    )
    portfolio_summary = deep_copy_dict(
        coverage_summary_plan.get("portfolio_coverage_summary", {})
    )
    evidence_gap_records = deep_copy_list(coverage_summary_plan.get("evidence_gap_records", []))
    action_work_items = deep_copy_list(action_worklist_plan.get("action_work_items", []))
    action_items_by_candidate = deep_copy_dict(
        action_worklist_plan.get("action_work_items_by_candidate", {})
    )
    assumptions = unique_preserve_order(
        normalise_string_list(result_integration_plan.get("assumptions", []))
        + normalise_string_list(coverage_summary_plan.get("assumptions", []))
        + normalise_string_list(action_worklist_plan.get("assumptions", []))
        + [
            "Criteria valuation package derived from result integration, coverage summary and evidence-gap action worklist contracts."
        ]
    )
    warnings = unique_preserve_order(
        normalise_string_list(result_integration_plan.get("warnings", []))
        + normalise_string_list(coverage_summary_plan.get("warnings", []))
        + normalise_string_list(action_worklist_plan.get("warnings", []))
        + normalise_string_list(result_validation.get("warnings", []))
        + normalise_string_list(coverage_validation.get("warnings", []))
        + normalise_string_list(action_validation.get("warnings", []))
        + package_candidate_consistency_warnings(
            result_integration_plan, coverage_summary_plan, action_worklist_plan
        )
    )
    hard_constraints = unique_preserve_order(
        normalise_string_list(result_integration_plan.get("hard_constraints", []))
        + normalise_string_list(coverage_summary_plan.get("hard_constraints", []))
        + normalise_string_list(action_worklist_plan.get("hard_constraints", []))
    )
    candidate_count = len(candidate_value_sets)
    criterion_value_count = count_criterion_values(candidate_value_sets)
    populated_value_count = count_populated_values(candidate_value_sets)
    placeholder_value_count = count_placeholder_values(candidate_value_sets)
    validation_error_count = (
        len(result_validation.get("errors", []))
        + len(coverage_validation.get("errors", []))
        + len(action_validation.get("errors", []))
    )
    package_status = package_status_from_counts(
        candidate_count,
        criterion_value_count,
        populated_value_count,
        placeholder_value_count,
        len(evidence_gap_records),
        validation_error_count,
    )
    readiness_summary = build_readiness_summary(
        package_status=package_status,
        candidate_value_sets=candidate_value_sets,
        evidence_gap_records=evidence_gap_records,
        action_work_items=action_work_items,
        action_worklist_plan=action_worklist_plan,
    )
    package_sections = package_sections_from_payloads(
        candidate_value_sets=candidate_value_sets,
        integrated_value_records=integrated_value_records,
        candidate_coverage_summaries=candidate_coverage_summaries,
        portfolio_coverage_summary=portfolio_summary,
        evidence_gap_records=evidence_gap_records,
        action_work_items=action_work_items,
        action_work_items_by_candidate=action_items_by_candidate,
        assumptions=assumptions,
        warnings=warnings,
        hard_constraints=hard_constraints,
    )
    return {
        "schema_version": CRITERIA_VALUATION_PACKAGE_SCHEMA_VERSION,
        "package_status": package_status,
        "source_result_integration_plan_version": str(
            result_integration_plan.get("schema_version", "")
        ),
        "source_coverage_summary_plan_version": str(
            coverage_summary_plan.get("schema_version", "")
        ),
        "source_action_worklist_plan_version": str(
            action_worklist_plan.get("schema_version", "")
        ),
        "readiness_summary": readiness_summary,
        "package_sections": package_sections,
        "candidate_value_sets": candidate_value_sets,
        "integrated_value_records": integrated_value_records,
        "candidate_coverage_summaries": candidate_coverage_summaries,
        "portfolio_coverage_summary": portfolio_summary,
        "evidence_gap_records": evidence_gap_records,
        "action_work_items": action_work_items,
        "action_work_items_by_candidate": action_items_by_candidate,
        "candidate_count": candidate_count,
        "criterion_value_count": criterion_value_count,
        "evidence_gap_count": len(evidence_gap_records),
        "action_work_item_count": len(action_work_items),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "measurement_execution_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": hard_constraints,
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


def validate_package_section(section: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(section, dict):
        return {
            "is_valid": False,
            "errors": ["Package section must be a dictionary."],
            "warnings": [],
        }
    if section.get("schema_version") != PACKAGE_SECTION_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PACKAGE_SECTION_SCHEMA_VERSION}.")
    for field_name in REQUIRED_PACKAGE_SECTION_FIELDS:
        if field_name not in section:
            errors.append(f"{field_name} is required.")
    if section.get("section_id") not in PACKAGE_SECTION_IDS:
        errors.append("section_id must be controlled.")
    if section.get("section_status") not in PACKAGE_SECTION_STATUSES:
        errors.append("section_status must be controlled.")
    if not isinstance(section.get("item_count"), int):
        errors.append("item_count must be an integer.")
    if "payload" not in section:
        errors.append("payload must exist.")
    if section.get("section_status") == "empty":
        warnings.append("Package section is empty.")
    _append_forbidden_field_errors(errors, section)
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_readiness_summary(summary: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(summary, dict):
        return {
            "is_valid": False,
            "errors": ["Readiness summary must be a dictionary."],
            "warnings": [],
        }
    if summary.get("schema_version") != PACKAGE_READINESS_SUMMARY_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {PACKAGE_READINESS_SUMMARY_SCHEMA_VERSION}."
        )
    for field_name in REQUIRED_READINESS_SUMMARY_FIELDS:
        if field_name not in summary:
            errors.append(f"{field_name} is required.")
    if summary.get("readiness_level") not in READINESS_LEVELS:
        errors.append("readiness_level must be controlled.")
    if summary.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if summary.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if summary.get("measurement_execution_allowed") is not False:
        errors.append("measurement_execution_allowed must be false.")
    if not isinstance(summary.get("review_use_cases"), list):
        errors.append("review_use_cases must be a list.")
    if summary.get("readiness_level") in {"placeholder_only", "ready_with_gaps"}:
        warnings.append("Readiness summary indicates gaps remain.")
    _append_forbidden_field_errors(errors, summary)
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_criteria_valuation_package(package: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(package, dict):
        return {
            "is_valid": False,
            "errors": ["Criteria valuation package must be a dictionary."],
            "warnings": [],
        }
    if package.get("schema_version") != CRITERIA_VALUATION_PACKAGE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CRITERIA_VALUATION_PACKAGE_SCHEMA_VERSION}.")
    for field_name in REQUIRED_CRITERIA_VALUATION_PACKAGE_FIELDS:
        if field_name not in package:
            errors.append(f"{field_name} is required.")
    if package.get("package_status") not in PACKAGE_STATUSES:
        errors.append("package_status must be controlled.")

    readiness_summary = package.get("readiness_summary")
    if not isinstance(readiness_summary, dict):
        errors.append("readiness_summary must be a dictionary.")
    else:
        validation = validate_readiness_summary(readiness_summary)
        if validation["errors"]:
            errors.append(
                "readiness_summary failed validation: "
                + "; ".join(validation["errors"])
            )
        warnings.extend(validation["warnings"])

    for field_name in (
        "package_sections",
        "candidate_value_sets",
        "integrated_value_records",
        "candidate_coverage_summaries",
        "evidence_gap_records",
        "action_work_items",
    ):
        if not isinstance(package.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    if not isinstance(package.get("portfolio_coverage_summary"), dict):
        errors.append("portfolio_coverage_summary must be a dictionary.")
    if not isinstance(package.get("action_work_items_by_candidate"), dict):
        errors.append("action_work_items_by_candidate must be a dictionary.")
    if package.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if package.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if package.get("measurement_execution_allowed") is not False:
        errors.append("measurement_execution_allowed must be false.")

    sections = package.get("package_sections", [])
    if isinstance(sections, list):
        for index, section in enumerate(sections):
            validation = validate_package_section(section)
            if validation["errors"]:
                errors.append(
                    f"package_sections[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])
    if package.get("package_status") in {"placeholder_only", "partial_coverage"}:
        warnings.append("Criteria valuation package still contains gaps.")
    _append_forbidden_field_errors(errors, package)
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def criteria_valuation_package_summary(package: dict) -> dict:
    warnings = package.get("warnings", [])
    readiness_summary = package.get("readiness_summary", {})
    readiness_level = (
        readiness_summary.get("readiness_level", "")
        if isinstance(readiness_summary, dict)
        else ""
    )
    return {
        "schema_version": package.get("schema_version", ""),
        "package_status": package.get("package_status", ""),
        "readiness_level": readiness_level,
        "candidate_count": int(package.get("candidate_count", 0)),
        "criterion_value_count": int(package.get("criterion_value_count", 0)),
        "evidence_gap_count": int(package.get("evidence_gap_count", 0)),
        "action_work_item_count": int(package.get("action_work_item_count", 0)),
        "package_section_count": len(package.get("package_sections", []))
        if isinstance(package.get("package_sections"), list)
        else 0,
        "live_model_call_allowed": bool_value(package, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(
            package, "live_source_retrieval_allowed"
        ),
        "measurement_execution_allowed": bool_value(
            package, "measurement_execution_allowed"
        ),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_criteria_valuation_package() -> dict:
    return build_criteria_valuation_package(
        hot_section_demo_criteria_result_integration_plan(),
        hot_section_demo_criteria_coverage_summary_plan(),
        hot_section_demo_evidence_gap_action_worklist_plan(),
    )
