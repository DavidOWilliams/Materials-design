from __future__ import annotations

import copy
import re
from typing import TypedDict

from src.candidate_criteria_valuation import (
    hot_section_demo_candidate_criteria_valuation_plan,
    validate_candidate_criteria_valuation_plan,
)
from src.criteria_value_schema import (
    criterion_value_placeholder,
    validate_criterion_value,
)
from src.deterministic_estimator_contracts import (
    hot_section_demo_deterministic_estimator_contract_plan,
    validate_deterministic_estimator_contract_plan,
    validate_estimator_result,
)


CRITERIA_RESULT_INTEGRATION_PLAN_SCHEMA_VERSION = (
    "criteria_result_integration_plan_v1"
)
CANDIDATE_CRITERION_VALUE_SET_SCHEMA_VERSION = "candidate_criterion_value_set_v1"
INTEGRATED_VALUE_RECORD_SCHEMA_VERSION = "integrated_criterion_value_record_v1"

RESULT_INTEGRATION_STATUSES: tuple[str, ...] = (
    "integrated_placeholder",
    "integrated_value",
    "skipped_invalid_result",
    "skipped_missing_candidate",
    "skipped_duplicate_result",
    "fallback_placeholder",
)

CANDIDATE_VALUE_SET_STATUSES: tuple[str, ...] = (
    "placeholder_only",
    "partly_populated",
    "populated",
    "no_values",
    "invalid_input",
)

REQUIRED_INTEGRATED_VALUE_RECORD_FIELDS: tuple[str, ...] = (
    "schema_version",
    "candidate_id",
    "criterion_id",
    "criterion_value",
    "integration_status",
    "source_estimator_result_id",
    "source_estimator_id",
    "source_work_item_id",
    "trace",
    "assumptions",
    "warnings",
)

REQUIRED_CANDIDATE_VALUE_SET_FIELDS: tuple[str, ...] = (
    "schema_version",
    "candidate_id",
    "value_set_status",
    "criterion_values",
    "integrated_value_records",
    "criterion_count",
    "placeholder_value_count",
    "populated_value_count",
    "assumptions",
    "warnings",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)


class IntegratedCriterionValueRecord(TypedDict, total=False):
    schema_version: str
    candidate_id: str
    criterion_id: str
    criterion_value: dict
    integration_status: str
    source_estimator_result_id: str
    source_estimator_id: str
    source_work_item_id: str
    trace: dict
    assumptions: list[str]
    warnings: list[str]


class CandidateCriterionValueSet(TypedDict, total=False):
    schema_version: str
    candidate_id: str
    value_set_status: str
    criterion_values: list[dict]
    integrated_value_records: list[dict]
    criterion_count: int
    placeholder_value_count: int
    populated_value_count: int
    assumptions: list[str]
    warnings: list[str]


class CriteriaResultIntegrationPlan(TypedDict, total=False):
    schema_version: str
    source_candidate_criteria_valuation_plan_version: str
    source_deterministic_estimator_contract_plan_version: str
    candidate_value_sets: list[dict]
    criterion_values_by_candidate: dict[str, list[dict]]
    integrated_value_records: list[dict]
    skipped_result_records: list[dict]
    candidate_count: int
    integrated_value_count: int
    skipped_result_count: int
    placeholder_value_count: int
    populated_value_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class CriteriaResultIntegrationValidationResult(TypedDict, total=False):
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


def candidate_ids_from_candidate_criteria_plan(plan: dict) -> list[str]:
    candidate_ids: list[str] = []
    values_by_candidate = plan.get("criterion_values_by_candidate", {})
    if isinstance(values_by_candidate, dict):
        candidate_ids.extend(str(candidate_id) for candidate_id in values_by_candidate)

    work_items = plan.get("work_items", [])
    if isinstance(work_items, list):
        for work_item in work_items:
            if not isinstance(work_item, dict):
                continue
            candidate_id = work_item.get("candidate_id")
            if isinstance(candidate_id, str) and candidate_id:
                candidate_ids.append(candidate_id)

    return unique_preserve_order(candidate_ids)


def criterion_value_key(candidate_id: str, criterion_id: str) -> str:
    return f"{candidate_id}::{criterion_id}"


def estimator_result_id(result: dict) -> str:
    value = result.get("estimator_request_id") if isinstance(result, dict) else None
    if isinstance(value, str) and value:
        return value
    if not isinstance(result, dict):
        return "unknown"
    return slugify_identifier(
        f"{result.get('candidate_id', '')}_{result.get('criterion_id', '')}_{result.get('estimator_id', '')}"
    )


def is_placeholder_criterion_value(value: dict) -> bool:
    if not isinstance(value, dict):
        return False
    return (
        value.get("value_type") == "pending"
        or value.get("estimated_value") == "pending"
        or value.get("valuation_status") == "placeholder_only"
    )


def candidate_placeholder_values_from_plan(
    candidate_criteria_plan: dict,
) -> dict[str, list[dict]]:
    values_by_candidate = candidate_criteria_plan.get("criterion_values_by_candidate", {})
    if isinstance(values_by_candidate, dict) and values_by_candidate:
        copied: dict[str, list[dict]] = {}
        for candidate_id, values in values_by_candidate.items():
            if isinstance(values, list):
                copied[str(candidate_id)] = copy.deepcopy(values)
        return copied

    derived: dict[str, list[dict]] = {}
    work_items = candidate_criteria_plan.get("work_items", [])
    if not isinstance(work_items, list):
        return derived
    for work_item in work_items:
        if not isinstance(work_item, dict):
            continue
        candidate_id = work_item.get("candidate_id")
        criterion_value = work_item.get("criterion_value")
        if (
            isinstance(candidate_id, str)
            and candidate_id
            and isinstance(criterion_value, dict)
        ):
            derived.setdefault(candidate_id, []).append(copy.deepcopy(criterion_value))
    return derived


def valid_estimator_results_from_plan(estimator_plan: dict) -> tuple[list[dict], list[dict]]:
    valid_results: list[dict] = []
    skipped_records: list[dict] = []
    results = estimator_plan.get("placeholder_results", [])
    if not isinstance(results, list):
        return valid_results, skipped_records

    for index, result in enumerate(results):
        validation = validate_estimator_result(result) if isinstance(result, dict) else {
            "is_valid": False,
            "errors": ["Estimator result must be a dictionary."],
            "warnings": [],
        }
        if validation["errors"]:
            skipped_records.append(
                {
                    "integration_status": "skipped_invalid_result",
                    "reason": "Estimator result failed validation.",
                    "result_index": index,
                    "errors": list(validation["errors"]),
                    "warnings": list(validation["warnings"]),
                }
            )
            continue
        valid_results.append(copy.deepcopy(result))
    return valid_results, skipped_records


def integrated_value_record_from_result(result: dict) -> dict:
    candidate_id = str(result.get("candidate_id", ""))
    criterion_id = str(result.get("criterion_id", ""))
    criterion_value = result.get("criterion_value", {})
    if not (
        isinstance(criterion_value, dict)
        and validate_criterion_value(criterion_value)["is_valid"]
    ):
        criterion_value = criterion_value_placeholder(candidate_id, criterion_id)
    criterion_value = copy.deepcopy(criterion_value)
    integration_status = (
        "integrated_placeholder"
        if is_placeholder_criterion_value(criterion_value)
        else "integrated_value"
    )
    return {
        "schema_version": INTEGRATED_VALUE_RECORD_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "criterion_id": criterion_id,
        "criterion_value": criterion_value,
        "integration_status": integration_status,
        "source_estimator_result_id": estimator_result_id(result),
        "source_estimator_id": str(result.get("estimator_id", "")),
        "source_work_item_id": str(result.get("work_item_id", "")),
        "trace": {
            "estimator_request_id": str(result.get("estimator_request_id", "")),
            "result_status": str(result.get("result_status", "")),
            "source": "deterministic_estimator_contract",
        },
        "assumptions": [
            "Criterion value integrated from deterministic estimator result contract."
        ],
        "warnings": normalise_string_list(result.get("warnings", [])),
    }


def integrate_estimator_results(
    candidate_criteria_plan: dict,
    estimator_plan: dict,
) -> tuple[list[dict], list[dict]]:
    candidate_ids = candidate_ids_from_candidate_criteria_plan(candidate_criteria_plan)
    candidate_id_set = set(candidate_ids)
    valid_results, skipped_records = valid_estimator_results_from_plan(estimator_plan)
    integrated_records: list[dict] = []
    seen_keys: set[str] = set()

    for result in valid_results:
        record = integrated_value_record_from_result(result)
        candidate_id = record["candidate_id"]
        criterion_id = record["criterion_id"]
        record_key = criterion_value_key(candidate_id, criterion_id)

        if candidate_id not in candidate_id_set:
            skipped_records.append(
                {
                    "integration_status": "skipped_missing_candidate",
                    "candidate_id": candidate_id,
                    "criterion_id": criterion_id,
                    "source_estimator_result_id": record["source_estimator_result_id"],
                    "reason": "Estimator result candidate is not present in the candidate criteria plan.",
                }
            )
            continue
        if record_key in seen_keys:
            skipped_records.append(
                {
                    "integration_status": "skipped_duplicate_result",
                    "candidate_id": candidate_id,
                    "criterion_id": criterion_id,
                    "source_estimator_result_id": record["source_estimator_result_id"],
                    "reason": "A result for this candidate and criterion has already been integrated.",
                }
            )
            continue

        seen_keys.add(record_key)
        integrated_records.append(record)

    return integrated_records, skipped_records


def fallback_integrated_records_from_placeholders(
    candidate_criteria_plan: dict,
    existing_integrated_records: list[dict],
) -> list[dict]:
    existing_keys = {
        criterion_value_key(str(record.get("candidate_id", "")), str(record.get("criterion_id", "")))
        for record in existing_integrated_records
        if isinstance(record, dict)
    }
    fallback_records: list[dict] = []
    values_by_candidate = candidate_placeholder_values_from_plan(candidate_criteria_plan)
    for candidate_id, values in values_by_candidate.items():
        for value in values:
            if not isinstance(value, dict):
                continue
            criterion_id = str(value.get("criterion_id", ""))
            record_key = criterion_value_key(candidate_id, criterion_id)
            if record_key in existing_keys:
                continue
            fallback_records.append(
                {
                    "schema_version": INTEGRATED_VALUE_RECORD_SCHEMA_VERSION,
                    "candidate_id": candidate_id,
                    "criterion_id": criterion_id,
                    "criterion_value": copy.deepcopy(value),
                    "integration_status": "fallback_placeholder",
                    "source_estimator_result_id": "",
                    "source_estimator_id": "",
                    "source_work_item_id": "",
                    "trace": {"source": "candidate_criteria_valuation_placeholder"},
                    "assumptions": [
                        "Fallback placeholder retained because no estimator result was integrated."
                    ],
                    "warnings": normalise_string_list(value.get("warnings", [])),
                }
            )
            existing_keys.add(record_key)
    return fallback_records


def candidate_value_set(candidate_id: str, integrated_records: list[dict]) -> dict:
    records = [
        copy.deepcopy(record)
        for record in integrated_records
        if isinstance(record, dict) and record.get("candidate_id") == candidate_id
    ]
    criterion_values = [
        copy.deepcopy(record.get("criterion_value", {}))
        for record in records
        if isinstance(record.get("criterion_value"), dict)
    ]
    criterion_count = len(criterion_values)
    placeholder_value_count = len(
        [value for value in criterion_values if is_placeholder_criterion_value(value)]
    )
    populated_value_count = criterion_count - placeholder_value_count

    if criterion_count == 0:
        value_set_status = "no_values"
    elif placeholder_value_count == criterion_count:
        value_set_status = "placeholder_only"
    elif populated_value_count == criterion_count:
        value_set_status = "populated"
    else:
        value_set_status = "partly_populated"

    return {
        "schema_version": CANDIDATE_CRITERION_VALUE_SET_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "value_set_status": value_set_status,
        "criterion_values": criterion_values,
        "integrated_value_records": records,
        "criterion_count": criterion_count,
        "placeholder_value_count": placeholder_value_count,
        "populated_value_count": populated_value_count,
        "assumptions": [],
        "warnings": [],
    }


def candidate_value_sets_from_integrated_records(
    candidate_ids: list[str],
    integrated_records: list[dict],
) -> list[dict]:
    return [
        candidate_value_set(candidate_id, integrated_records)
        for candidate_id in unique_preserve_order(candidate_ids)
    ]


def criterion_values_by_candidate_from_value_sets(
    value_sets: list[dict],
) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for value_set in value_sets:
        if not isinstance(value_set, dict):
            continue
        candidate_id = value_set.get("candidate_id")
        values = value_set.get("criterion_values")
        if isinstance(candidate_id, str) and isinstance(values, list):
            grouped[candidate_id] = copy.deepcopy(values)
    return grouped


def build_criteria_result_integration_plan(
    candidate_criteria_plan: dict,
    estimator_plan: dict,
) -> dict:
    candidate_validation = validate_candidate_criteria_valuation_plan(
        candidate_criteria_plan
    )
    estimator_validation = validate_deterministic_estimator_contract_plan(estimator_plan)
    integrated_records, skipped_records = integrate_estimator_results(
        candidate_criteria_plan, estimator_plan
    )
    fallback_records = fallback_integrated_records_from_placeholders(
        candidate_criteria_plan, integrated_records
    )
    all_integrated_records = integrated_records + fallback_records
    candidate_ids = candidate_ids_from_candidate_criteria_plan(candidate_criteria_plan)
    value_sets = candidate_value_sets_from_integrated_records(
        candidate_ids, all_integrated_records
    )
    skipped_warnings = [
        f"{record.get('integration_status', 'skipped_result')}: {record.get('reason', '')}"
        for record in skipped_records
        if isinstance(record, dict)
    ]
    assumptions = unique_preserve_order(
        normalise_string_list(candidate_criteria_plan.get("assumptions", []))
        + [
            "Criteria result integration plan derived from CandidateCriteriaValuationPlan and DeterministicEstimatorContractPlan."
        ]
    )
    warnings = unique_preserve_order(
        normalise_string_list(candidate_criteria_plan.get("warnings", []))
        + normalise_string_list(candidate_validation.get("warnings", []))
        + normalise_string_list(estimator_validation.get("warnings", []))
        + skipped_warnings
    )
    placeholder_value_count = sum(
        int(value_set.get("placeholder_value_count", 0)) for value_set in value_sets
    )
    populated_value_count = sum(
        int(value_set.get("populated_value_count", 0)) for value_set in value_sets
    )
    return {
        "schema_version": CRITERIA_RESULT_INTEGRATION_PLAN_SCHEMA_VERSION,
        "source_candidate_criteria_valuation_plan_version": str(
            candidate_criteria_plan.get("schema_version", "")
        ),
        "source_deterministic_estimator_contract_plan_version": str(
            estimator_plan.get("schema_version", "")
        ),
        "candidate_value_sets": value_sets,
        "criterion_values_by_candidate": criterion_values_by_candidate_from_value_sets(
            value_sets
        ),
        "integrated_value_records": all_integrated_records,
        "skipped_result_records": copy.deepcopy(skipped_records),
        "candidate_count": len(candidate_ids),
        "integrated_value_count": len(all_integrated_records),
        "skipped_result_count": len(skipped_records),
        "placeholder_value_count": placeholder_value_count,
        "populated_value_count": populated_value_count,
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": normalise_string_list(
            candidate_criteria_plan.get("hard_constraints", [])
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


def validate_integrated_value_record(record: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return {
            "is_valid": False,
            "errors": ["Integrated value record must be a dictionary."],
            "warnings": [],
        }
    if record.get("schema_version") != INTEGRATED_VALUE_RECORD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {INTEGRATED_VALUE_RECORD_SCHEMA_VERSION}.")
    for field_name in REQUIRED_INTEGRATED_VALUE_RECORD_FIELDS:
        if field_name not in record:
            errors.append(f"{field_name} is required.")
    if not isinstance(record.get("candidate_id"), str) or not record.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if not isinstance(record.get("criterion_id"), str) or not record.get("criterion_id"):
        errors.append("criterion_id must be a non-empty string.")
    criterion_value = record.get("criterion_value")
    if not isinstance(criterion_value, dict):
        errors.append("criterion_value must be a dictionary.")
    else:
        value_validation = validate_criterion_value(criterion_value)
        if value_validation["errors"]:
            errors.append(
                "criterion_value failed validation: "
                + "; ".join(value_validation["errors"])
            )
        warnings.extend(value_validation["warnings"])
    if record.get("integration_status") not in RESULT_INTEGRATION_STATUSES:
        errors.append("integration_status must be controlled.")
    if not isinstance(record.get("trace"), dict):
        errors.append("trace must be a dictionary.")
    forbidden_hits = _find_forbidden_claim_fields(record)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def validate_candidate_value_set(value_set: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(value_set, dict):
        return {
            "is_valid": False,
            "errors": ["Candidate value set must be a dictionary."],
            "warnings": [],
        }
    if value_set.get("schema_version") != CANDIDATE_CRITERION_VALUE_SET_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {CANDIDATE_CRITERION_VALUE_SET_SCHEMA_VERSION}."
        )
    for field_name in REQUIRED_CANDIDATE_VALUE_SET_FIELDS:
        if field_name not in value_set:
            errors.append(f"{field_name} is required.")
    if not isinstance(value_set.get("candidate_id"), str) or not value_set.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if value_set.get("value_set_status") not in CANDIDATE_VALUE_SET_STATUSES:
        errors.append("value_set_status must be controlled.")
    criterion_values = value_set.get("criterion_values")
    integrated_records = value_set.get("integrated_value_records")
    if not isinstance(criterion_values, list):
        errors.append("criterion_values must be a list.")
        criterion_values = []
    if not isinstance(integrated_records, list):
        errors.append("integrated_value_records must be a list.")
        integrated_records = []
    if value_set.get("criterion_count") != len(criterion_values):
        errors.append("criterion_count must equal len(criterion_values).")
    for index, record in enumerate(integrated_records):
        validation = validate_integrated_value_record(record)
        if validation["errors"]:
            errors.append(
                f"integrated_value_records[{index}] failed validation: "
                + "; ".join(validation["errors"])
            )
        warnings.extend(validation["warnings"])
    if value_set.get("value_set_status") == "no_values":
        warnings.append("Candidate value set has no values.")
    if value_set.get("value_set_status") == "placeholder_only":
        warnings.append("Candidate value set contains placeholder values only.")
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def validate_criteria_result_integration_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Criteria result integration plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != CRITERIA_RESULT_INTEGRATION_PLAN_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {CRITERIA_RESULT_INTEGRATION_PLAN_SCHEMA_VERSION}."
        )
    for field_name in (
        "candidate_value_sets",
        "integrated_value_records",
        "skipped_result_records",
    ):
        if not isinstance(plan.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    if not isinstance(plan.get("criterion_values_by_candidate"), dict):
        errors.append("criterion_values_by_candidate must be a dictionary.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")

    integrated_records = plan.get("integrated_value_records", [])
    if isinstance(integrated_records, list):
        for index, record in enumerate(integrated_records):
            validation = validate_integrated_value_record(record)
            if validation["errors"]:
                errors.append(
                    f"integrated_value_records[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])

    value_sets = plan.get("candidate_value_sets", [])
    if isinstance(value_sets, list):
        if not value_sets:
            warnings.append("No candidate value sets are present.")
        for index, value_set in enumerate(value_sets):
            validation = validate_candidate_value_set(value_set)
            if validation["errors"]:
                errors.append(
                    f"candidate_value_sets[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])
        if value_sets and all(
            isinstance(value_set, dict)
            and value_set.get("value_set_status") == "placeholder_only"
            for value_set in value_sets
        ):
            warnings.append("All candidate value sets contain placeholders only.")

    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def criteria_result_integration_summary(plan: dict) -> dict:
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "candidate_count": int(plan.get("candidate_count", 0)),
        "candidate_value_set_count": len(plan.get("candidate_value_sets", []))
        if isinstance(plan.get("candidate_value_sets"), list)
        else 0,
        "integrated_value_count": int(plan.get("integrated_value_count", 0)),
        "skipped_result_count": int(plan.get("skipped_result_count", 0)),
        "placeholder_value_count": int(plan.get("placeholder_value_count", 0)),
        "populated_value_count": int(plan.get("populated_value_count", 0)),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(
            plan, "live_source_retrieval_allowed"
        ),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_criteria_result_integration_plan() -> dict:
    return build_criteria_result_integration_plan(
        hot_section_demo_candidate_criteria_valuation_plan(),
        hot_section_demo_deterministic_estimator_contract_plan(),
    )
