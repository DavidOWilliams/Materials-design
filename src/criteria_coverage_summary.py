from __future__ import annotations

import copy
import re
from typing import TypedDict

from src.criteria_result_integration import (
    hot_section_demo_criteria_result_integration_plan,
    is_placeholder_criterion_value,
    validate_criteria_result_integration_plan,
)
from src.criteria_value_schema import validate_criterion_value


CRITERIA_COVERAGE_SUMMARY_PLAN_SCHEMA_VERSION = "criteria_coverage_summary_plan_v1"
CRITERION_COVERAGE_RECORD_SCHEMA_VERSION = "criterion_coverage_record_v1"
EVIDENCE_GAP_RECORD_SCHEMA_VERSION = "evidence_gap_record_v1"
CANDIDATE_COVERAGE_SUMMARY_SCHEMA_VERSION = "candidate_coverage_summary_v1"
PORTFOLIO_COVERAGE_SUMMARY_SCHEMA_VERSION = "portfolio_coverage_summary_v1"

CRITERION_COVERAGE_STATUSES: tuple[str, ...] = (
    "populated",
    "placeholder",
    "invalid_value",
    "missing",
)

EVIDENCE_BASIS_STATUSES: tuple[str, ...] = (
    "present",
    "placeholder_only",
    "missing",
    "invalid",
)

MODEL_PROVENANCE_STATUSES: tuple[str, ...] = (
    "present",
    "placeholder_only",
    "missing",
    "not_required",
)

MEASUREMENT_FEEDBACK_STATUSES: tuple[str, ...] = (
    "present",
    "placeholder_only",
    "missing",
    "not_required",
)

UNCERTAINTY_ASSESSMENT_STATUSES: tuple[str, ...] = (
    "assessed",
    "not_assessed",
    "unknown",
)

CANDIDATE_COVERAGE_STATUSES: tuple[str, ...] = (
    "populated",
    "populated_with_gaps",
    "partial_coverage",
    "placeholder_only",
    "no_criteria",
    "invalid_input",
)

EVIDENCE_GAP_TYPES: tuple[str, ...] = (
    "placeholder_value",
    "missing_evidence_basis",
    "placeholder_evidence_basis",
    "low_confidence",
    "high_uncertainty",
    "missing_uncertainty_assessment",
    "missing_model_provenance",
    "missing_measurement_feedback",
    "invalid_criterion_value",
)

NEXT_EVIDENCE_ACTION_TYPES: tuple[str, ...] = (
    "deterministic_estimator",
    "computational_model",
    "literature_evidence_review",
    "measurement_feedback",
    "engineering_review",
    "no_action_required",
)

GAP_SEVERITY_LEVELS: tuple[str, ...] = ("low", "medium", "high")

REQUIRED_CRITERION_COVERAGE_RECORD_FIELDS: tuple[str, ...] = (
    "schema_version",
    "candidate_id",
    "criterion_id",
    "criterion_label",
    "criterion_family",
    "coverage_status",
    "value_type",
    "confidence",
    "uncertainty_level",
    "evidence_basis_status",
    "model_provenance_status",
    "measurement_feedback_status",
    "uncertainty_assessment_status",
    "source_integration_status",
    "recommended_next_action_type",
    "assumptions",
    "warnings",
)

REQUIRED_EVIDENCE_GAP_RECORD_FIELDS: tuple[str, ...] = (
    "schema_version",
    "gap_id",
    "candidate_id",
    "criterion_id",
    "gap_type",
    "severity",
    "next_action_type",
    "reason",
    "suitable_for_deterministic_estimator",
    "suitable_for_computational_model",
    "suitable_for_measurement_feedback",
    "assumptions",
    "warnings",
)

REQUIRED_CANDIDATE_COVERAGE_SUMMARY_FIELDS: tuple[str, ...] = (
    "schema_version",
    "candidate_id",
    "coverage_status",
    "criterion_count",
    "populated_value_count",
    "placeholder_value_count",
    "invalid_value_count",
    "evidence_gap_count",
    "model_gap_count",
    "measurement_gap_count",
    "uncertainty_gap_count",
    "criterion_coverage_records",
    "evidence_gap_records",
    "assumptions",
    "warnings",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)


class CriterionCoverageRecord(TypedDict, total=False):
    schema_version: str
    candidate_id: str
    criterion_id: str
    criterion_label: str
    criterion_family: str
    coverage_status: str
    value_type: str
    confidence: str
    uncertainty_level: str
    evidence_basis_status: str
    model_provenance_status: str
    measurement_feedback_status: str
    uncertainty_assessment_status: str
    source_integration_status: str
    recommended_next_action_type: str
    assumptions: list[str]
    warnings: list[str]


class EvidenceGapRecord(TypedDict, total=False):
    schema_version: str
    gap_id: str
    candidate_id: str
    criterion_id: str
    gap_type: str
    severity: str
    next_action_type: str
    reason: str
    suitable_for_deterministic_estimator: bool
    suitable_for_computational_model: bool
    suitable_for_measurement_feedback: bool
    assumptions: list[str]
    warnings: list[str]


class CandidateCoverageSummary(TypedDict, total=False):
    schema_version: str
    candidate_id: str
    coverage_status: str
    criterion_count: int
    populated_value_count: int
    placeholder_value_count: int
    invalid_value_count: int
    evidence_gap_count: int
    model_gap_count: int
    measurement_gap_count: int
    uncertainty_gap_count: int
    criterion_coverage_records: list[dict]
    evidence_gap_records: list[dict]
    assumptions: list[str]
    warnings: list[str]


class PortfolioCoverageSummary(TypedDict, total=False):
    schema_version: str
    candidate_count: int
    total_criterion_count: int
    total_populated_value_count: int
    total_placeholder_value_count: int
    total_invalid_value_count: int
    total_evidence_gap_count: int
    total_model_gap_count: int
    total_measurement_gap_count: int
    total_uncertainty_gap_count: int
    placeholder_only_candidate_count: int
    partial_coverage_candidate_count: int
    populated_candidate_count: int
    assumptions: list[str]
    warnings: list[str]


class CriteriaCoverageSummaryPlan(TypedDict, total=False):
    schema_version: str
    source_criteria_result_integration_plan_version: str
    candidate_coverage_summaries: list[dict]
    portfolio_coverage_summary: dict
    criterion_coverage_records: list[dict]
    evidence_gap_records: list[dict]
    candidate_count: int
    criterion_coverage_record_count: int
    evidence_gap_count: int
    populated_value_count: int
    placeholder_value_count: int
    invalid_value_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class CriteriaCoverageValidationResult(TypedDict, total=False):
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


def criterion_values_from_candidate_value_set(value_set: dict) -> list[dict]:
    values = value_set.get("criterion_values", []) if isinstance(value_set, dict) else []
    if not isinstance(values, list):
        return []
    return copy.deepcopy([value for value in values if isinstance(value, dict)])


def criterion_value_candidate_id(value: dict, fallback_candidate_id: str = "") -> str:
    candidate_id = value.get("candidate_id") if isinstance(value, dict) else None
    if isinstance(candidate_id, str) and candidate_id:
        return candidate_id
    return fallback_candidate_id or "unknown_candidate"


def criterion_value_id(value: dict) -> str:
    criterion_id = value.get("criterion_id") if isinstance(value, dict) else None
    return criterion_id if isinstance(criterion_id, str) and criterion_id else "unknown_criterion"


def criterion_value_label(value: dict) -> str:
    label = value.get("criterion_label") if isinstance(value, dict) else None
    if isinstance(label, str) and label:
        return label
    return humanise_identifier(criterion_value_id(value))


def criterion_value_family(value: dict) -> str:
    family = value.get("criterion_family") if isinstance(value, dict) else None
    return family if isinstance(family, str) and family else "evidence_maturity"


def criterion_coverage_status(value: dict) -> str:
    validation = validate_criterion_value(value)
    if validation["errors"]:
        return "invalid_value"
    if is_placeholder_criterion_value(value):
        return "placeholder"
    return "populated"


def evidence_basis_status(value: dict) -> str:
    evidence_basis = value.get("evidence_basis") if isinstance(value, dict) else None
    if not isinstance(evidence_basis, list):
        return "invalid"
    if not evidence_basis:
        return "missing"
    if all(
        isinstance(item, dict)
        and (item.get("source_type") == "placeholder" or item.get("confidence") == "not_assessed")
        for item in evidence_basis
    ):
        return "placeholder_only"
    return "present"


def model_provenance_status(
    value: dict, *, model_provenance_required: bool = False
) -> str:
    model_provenance = value.get("model_provenance") if isinstance(value, dict) else None
    if not isinstance(model_provenance, list) or not model_provenance:
        return "missing" if model_provenance_required else "not_required"
    if all(
        isinstance(record, dict)
        and (
            record.get("model_type") == "placeholder"
            or record.get("provenance_status") == "required"
        )
        for record in model_provenance
    ):
        return "placeholder_only"
    return "present"


def measurement_feedback_status(
    value: dict, *, measurement_feedback_required: bool = False
) -> str:
    records: list[dict] = []
    if isinstance(value, dict):
        links = value.get("measurement_feedback_links", [])
        if isinstance(links, list):
            records.extend([record for record in links if isinstance(record, dict)])
        actions = value.get("recommended_next_evidence", [])
        if isinstance(actions, list):
            records.extend(
                [
                    action
                    for action in actions
                    if isinstance(action, dict)
                    and "measurement" in str(action).lower()
                ]
            )
    if not records:
        return "missing" if measurement_feedback_required else "not_required"
    if all(
        str(record.get("feedback_status", record.get("status", ""))).lower()
        in {"placeholder", "placeholder_only", "not_available", "pending", ""}
        for record in records
    ):
        return "placeholder_only"
    return "present"


def uncertainty_assessment_status(value: dict) -> str:
    uncertainty_level = value.get("uncertainty_level") if isinstance(value, dict) else None
    if uncertainty_level == "not_assessed":
        return "not_assessed"
    if uncertainty_level == "unknown":
        return "unknown"
    return "assessed"


def recommended_next_action_type_for_value(value: dict, coverage_status: str) -> str:
    if coverage_status == "invalid_value":
        return "engineering_review"
    if coverage_status == "placeholder":
        return "deterministic_estimator"
    if evidence_basis_status(value) in {"missing", "placeholder_only"}:
        return "literature_evidence_review"
    if uncertainty_assessment_status(value) in {"not_assessed", "unknown"}:
        return "deterministic_estimator"
    if model_provenance_status(value, model_provenance_required=True) == "missing":
        return "computational_model"
    return "no_action_required"


def criterion_coverage_record(
    value: dict,
    *,
    fallback_candidate_id: str = "",
    source_integration_status: str = "",
    model_provenance_required: bool = False,
    measurement_feedback_required: bool = False,
) -> dict:
    copied_value = copy.deepcopy(value)
    validation = validate_criterion_value(copied_value)
    coverage_status = criterion_coverage_status(copied_value)
    warnings = normalise_string_list(validation.get("warnings", []))
    if validation["errors"]:
        warnings.extend([str(error) for error in validation["errors"]])
    warnings = unique_preserve_order(warnings)
    return {
        "schema_version": CRITERION_COVERAGE_RECORD_SCHEMA_VERSION,
        "candidate_id": criterion_value_candidate_id(
            copied_value, fallback_candidate_id
        ),
        "criterion_id": criterion_value_id(copied_value),
        "criterion_label": criterion_value_label(copied_value),
        "criterion_family": criterion_value_family(copied_value),
        "coverage_status": coverage_status,
        "value_type": str(copied_value.get("value_type", "")),
        "confidence": str(copied_value.get("confidence", "")),
        "uncertainty_level": str(copied_value.get("uncertainty_level", "")),
        "evidence_basis_status": evidence_basis_status(copied_value),
        "model_provenance_status": model_provenance_status(
            copied_value, model_provenance_required=model_provenance_required
        ),
        "measurement_feedback_status": measurement_feedback_status(
            copied_value, measurement_feedback_required=measurement_feedback_required
        ),
        "uncertainty_assessment_status": uncertainty_assessment_status(copied_value),
        "source_integration_status": source_integration_status,
        "recommended_next_action_type": recommended_next_action_type_for_value(
            copied_value, coverage_status
        ),
        "assumptions": normalise_string_list(copied_value.get("assumptions", [])),
        "warnings": warnings,
    }


def gap_id_for(candidate_id: str, criterion_id: str, gap_type: str) -> str:
    return "gap_" + "_".join(
        [
            slugify_identifier(candidate_id),
            slugify_identifier(criterion_id),
            slugify_identifier(gap_type),
        ]
    )


def evidence_gap_record(
    candidate_id: str,
    criterion_id: str,
    gap_type: str,
    *,
    reason: str,
    severity: str = "medium",
    next_action_type: str = "engineering_review",
) -> dict:
    severity_value = severity if severity in GAP_SEVERITY_LEVELS else "medium"
    action_value = (
        next_action_type
        if next_action_type in NEXT_EVIDENCE_ACTION_TYPES
        else "engineering_review"
    )
    return {
        "schema_version": EVIDENCE_GAP_RECORD_SCHEMA_VERSION,
        "gap_id": gap_id_for(candidate_id, criterion_id, gap_type),
        "candidate_id": candidate_id,
        "criterion_id": criterion_id,
        "gap_type": str(gap_type),
        "severity": severity_value,
        "next_action_type": action_value,
        "reason": reason,
        "suitable_for_deterministic_estimator": gap_type
        in {"placeholder_value", "missing_uncertainty_assessment"},
        "suitable_for_computational_model": gap_type
        in {"high_uncertainty", "missing_model_provenance"},
        "suitable_for_measurement_feedback": gap_type == "missing_measurement_feedback",
        "assumptions": [],
        "warnings": [],
    }


def evidence_gaps_for_coverage_record(record: dict) -> list[dict]:
    candidate_id = str(record.get("candidate_id", "unknown_candidate"))
    criterion_id = str(record.get("criterion_id", "unknown_criterion"))
    next_action = str(record.get("recommended_next_action_type", "engineering_review"))
    gaps: list[dict] = []

    def add_gap(gap_type: str, reason: str, severity: str = "medium") -> None:
        gaps.append(
            evidence_gap_record(
                candidate_id,
                criterion_id,
                gap_type,
                reason=reason,
                severity=severity,
                next_action_type=next_action,
            )
        )

    if record.get("coverage_status") == "placeholder":
        add_gap("placeholder_value", "Criterion value is still a placeholder.")
    if record.get("coverage_status") == "invalid_value":
        add_gap("invalid_criterion_value", "Criterion value failed validation.", "high")
    if record.get("evidence_basis_status") == "missing":
        add_gap("missing_evidence_basis", "No evidence basis is attached.")
    if record.get("evidence_basis_status") == "placeholder_only":
        add_gap(
            "placeholder_evidence_basis",
            "Evidence basis is currently placeholder-only.",
        )
    if record.get("confidence") in {"low", "not_assessed"}:
        add_gap("low_confidence", "Criterion confidence is low or not assessed.")
    if record.get("uncertainty_assessment_status") == "not_assessed":
        add_gap(
            "missing_uncertainty_assessment",
            "Uncertainty has not yet been assessed.",
        )
    if record.get("uncertainty_level") == "high":
        add_gap("high_uncertainty", "Criterion uncertainty is high.", "high")
    if record.get("model_provenance_status") == "missing":
        add_gap("missing_model_provenance", "Required model provenance is missing.")
    if record.get("measurement_feedback_status") == "missing":
        add_gap(
            "missing_measurement_feedback",
            "Required measurement feedback is missing.",
        )
    return gaps


def candidate_coverage_status_from_counts(
    criterion_count: int,
    populated_value_count: int,
    placeholder_value_count: int,
    invalid_value_count: int,
    evidence_gap_count: int,
) -> str:
    if criterion_count == 0:
        return "no_criteria"
    if invalid_value_count > 0:
        return "invalid_input"
    if populated_value_count == 0 and placeholder_value_count > 0:
        return "placeholder_only"
    if populated_value_count > 0 and placeholder_value_count > 0:
        return "partial_coverage"
    if populated_value_count == criterion_count and evidence_gap_count > 0:
        return "populated_with_gaps"
    if populated_value_count == criterion_count:
        return "populated"
    return "partial_coverage"


def candidate_coverage_summary(
    value_set: dict,
    *,
    model_provenance_required: bool = False,
    measurement_feedback_required: bool = False,
) -> dict:
    candidate_id = (
        value_set.get("candidate_id")
        if isinstance(value_set.get("candidate_id"), str) and value_set.get("candidate_id")
        else "unknown_candidate"
    )
    integrated_records = value_set.get("integrated_value_records", [])
    coverage_records: list[dict] = []
    if isinstance(integrated_records, list) and integrated_records:
        for record in integrated_records:
            if not isinstance(record, dict) or not isinstance(record.get("criterion_value"), dict):
                continue
            coverage_records.append(
                criterion_coverage_record(
                    record["criterion_value"],
                    fallback_candidate_id=candidate_id,
                    source_integration_status=str(record.get("integration_status", "")),
                    model_provenance_required=model_provenance_required,
                    measurement_feedback_required=measurement_feedback_required,
                )
            )
    else:
        for value in criterion_values_from_candidate_value_set(value_set):
            coverage_records.append(
                criterion_coverage_record(
                    value,
                    fallback_candidate_id=candidate_id,
                    model_provenance_required=model_provenance_required,
                    measurement_feedback_required=measurement_feedback_required,
                )
            )

    gap_records: list[dict] = []
    for record in coverage_records:
        gap_records.extend(evidence_gaps_for_coverage_record(record))

    criterion_count = len(coverage_records)
    populated_value_count = len(
        [record for record in coverage_records if record.get("coverage_status") == "populated"]
    )
    placeholder_value_count = len(
        [record for record in coverage_records if record.get("coverage_status") == "placeholder"]
    )
    invalid_value_count = len(
        [record for record in coverage_records if record.get("coverage_status") == "invalid_value"]
    )
    evidence_gap_count = len(gap_records)
    model_gap_count = len(
        [record for record in gap_records if record.get("gap_type") == "missing_model_provenance"]
    )
    measurement_gap_count = len(
        [record for record in gap_records if record.get("gap_type") == "missing_measurement_feedback"]
    )
    uncertainty_gap_count = len(
        [
            record
            for record in gap_records
            if record.get("gap_type")
            in {"missing_uncertainty_assessment", "high_uncertainty"}
        ]
    )
    return {
        "schema_version": CANDIDATE_COVERAGE_SUMMARY_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "coverage_status": candidate_coverage_status_from_counts(
            criterion_count,
            populated_value_count,
            placeholder_value_count,
            invalid_value_count,
            evidence_gap_count,
        ),
        "criterion_count": criterion_count,
        "populated_value_count": populated_value_count,
        "placeholder_value_count": placeholder_value_count,
        "invalid_value_count": invalid_value_count,
        "evidence_gap_count": evidence_gap_count,
        "model_gap_count": model_gap_count,
        "measurement_gap_count": measurement_gap_count,
        "uncertainty_gap_count": uncertainty_gap_count,
        "criterion_coverage_records": coverage_records,
        "evidence_gap_records": gap_records,
        "assumptions": [],
        "warnings": [],
    }


def candidate_coverage_summaries_from_plan(
    integration_plan: dict,
    *,
    model_provenance_required: bool = False,
    measurement_feedback_required: bool = False,
) -> list[dict]:
    value_sets = integration_plan.get("candidate_value_sets", [])
    if not isinstance(value_sets, list):
        return []
    return [
        candidate_coverage_summary(
            value_set,
            model_provenance_required=model_provenance_required,
            measurement_feedback_required=measurement_feedback_required,
        )
        for value_set in value_sets
        if isinstance(value_set, dict)
    ]


def portfolio_coverage_summary(candidate_summaries: list[dict]) -> dict:
    summaries = [summary for summary in candidate_summaries if isinstance(summary, dict)]
    return {
        "schema_version": PORTFOLIO_COVERAGE_SUMMARY_SCHEMA_VERSION,
        "candidate_count": len(summaries),
        "total_criterion_count": sum(int(summary.get("criterion_count", 0)) for summary in summaries),
        "total_populated_value_count": sum(
            int(summary.get("populated_value_count", 0)) for summary in summaries
        ),
        "total_placeholder_value_count": sum(
            int(summary.get("placeholder_value_count", 0)) for summary in summaries
        ),
        "total_invalid_value_count": sum(
            int(summary.get("invalid_value_count", 0)) for summary in summaries
        ),
        "total_evidence_gap_count": sum(
            int(summary.get("evidence_gap_count", 0)) for summary in summaries
        ),
        "total_model_gap_count": sum(int(summary.get("model_gap_count", 0)) for summary in summaries),
        "total_measurement_gap_count": sum(
            int(summary.get("measurement_gap_count", 0)) for summary in summaries
        ),
        "total_uncertainty_gap_count": sum(
            int(summary.get("uncertainty_gap_count", 0)) for summary in summaries
        ),
        "placeholder_only_candidate_count": len(
            [summary for summary in summaries if summary.get("coverage_status") == "placeholder_only"]
        ),
        "partial_coverage_candidate_count": len(
            [summary for summary in summaries if summary.get("coverage_status") == "partial_coverage"]
        ),
        "populated_candidate_count": len(
            [
                summary
                for summary in summaries
                if summary.get("coverage_status") in {"populated", "populated_with_gaps"}
            ]
        ),
        "assumptions": [],
        "warnings": [],
    }


def build_criteria_coverage_summary_plan(
    integration_plan: dict,
    *,
    model_provenance_required: bool = False,
    measurement_feedback_required: bool = False,
) -> dict:
    validation = validate_criteria_result_integration_plan(integration_plan)
    candidate_summaries = candidate_coverage_summaries_from_plan(
        integration_plan,
        model_provenance_required=model_provenance_required,
        measurement_feedback_required=measurement_feedback_required,
    )
    criterion_records = [
        record
        for summary in candidate_summaries
        for record in summary.get("criterion_coverage_records", [])
    ]
    gap_records = [
        record
        for summary in candidate_summaries
        for record in summary.get("evidence_gap_records", [])
    ]
    portfolio_summary = portfolio_coverage_summary(candidate_summaries)
    assumptions = unique_preserve_order(
        normalise_string_list(integration_plan.get("assumptions", []))
        + [
            "Criteria coverage summary plan derived from CriteriaResultIntegrationPlan."
        ]
    )
    warnings = unique_preserve_order(
        normalise_string_list(integration_plan.get("warnings", []))
        + normalise_string_list(validation.get("warnings", []))
    )
    return {
        "schema_version": CRITERIA_COVERAGE_SUMMARY_PLAN_SCHEMA_VERSION,
        "source_criteria_result_integration_plan_version": str(
            integration_plan.get("schema_version", "")
        ),
        "candidate_coverage_summaries": candidate_summaries,
        "portfolio_coverage_summary": portfolio_summary,
        "criterion_coverage_records": criterion_records,
        "evidence_gap_records": gap_records,
        "candidate_count": len(candidate_summaries),
        "criterion_coverage_record_count": len(criterion_records),
        "evidence_gap_count": len(gap_records),
        "populated_value_count": sum(
            int(summary.get("populated_value_count", 0)) for summary in candidate_summaries
        ),
        "placeholder_value_count": sum(
            int(summary.get("placeholder_value_count", 0)) for summary in candidate_summaries
        ),
        "invalid_value_count": sum(
            int(summary.get("invalid_value_count", 0)) for summary in candidate_summaries
        ),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": normalise_string_list(integration_plan.get("hard_constraints", [])),
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


def validate_criterion_coverage_record(record: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return {
            "is_valid": False,
            "errors": ["Criterion coverage record must be a dictionary."],
            "warnings": [],
        }
    if record.get("schema_version") != CRITERION_COVERAGE_RECORD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CRITERION_COVERAGE_RECORD_SCHEMA_VERSION}.")
    for field_name in REQUIRED_CRITERION_COVERAGE_RECORD_FIELDS:
        if field_name not in record:
            errors.append(f"{field_name} is required.")
    if not isinstance(record.get("candidate_id"), str) or not record.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if not isinstance(record.get("criterion_id"), str) or not record.get("criterion_id"):
        errors.append("criterion_id must be a non-empty string.")
    if record.get("coverage_status") not in CRITERION_COVERAGE_STATUSES:
        errors.append("coverage_status must be controlled.")
    if record.get("evidence_basis_status") not in EVIDENCE_BASIS_STATUSES:
        errors.append("evidence_basis_status must be controlled.")
    if record.get("model_provenance_status") not in MODEL_PROVENANCE_STATUSES:
        errors.append("model_provenance_status must be controlled.")
    if record.get("measurement_feedback_status") not in MEASUREMENT_FEEDBACK_STATUSES:
        errors.append("measurement_feedback_status must be controlled.")
    if record.get("uncertainty_assessment_status") not in UNCERTAINTY_ASSESSMENT_STATUSES:
        errors.append("uncertainty_assessment_status must be controlled.")
    if record.get("recommended_next_action_type") not in NEXT_EVIDENCE_ACTION_TYPES:
        errors.append("recommended_next_action_type must be controlled.")
    forbidden_hits = _find_forbidden_claim_fields(record)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_evidence_gap_record(record: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(record, dict):
        return {
            "is_valid": False,
            "errors": ["Evidence gap record must be a dictionary."],
            "warnings": [],
        }
    if record.get("schema_version") != EVIDENCE_GAP_RECORD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {EVIDENCE_GAP_RECORD_SCHEMA_VERSION}.")
    for field_name in REQUIRED_EVIDENCE_GAP_RECORD_FIELDS:
        if field_name not in record:
            errors.append(f"{field_name} is required.")
    for field_name in ("gap_id", "candidate_id", "criterion_id"):
        if not isinstance(record.get(field_name), str) or not record.get(field_name):
            errors.append(f"{field_name} must be a non-empty string.")
    if record.get("gap_type") not in EVIDENCE_GAP_TYPES:
        errors.append("gap_type must be controlled.")
    if record.get("severity") not in GAP_SEVERITY_LEVELS:
        errors.append("severity must be controlled.")
    if record.get("next_action_type") not in NEXT_EVIDENCE_ACTION_TYPES:
        errors.append("next_action_type must be controlled.")
    for field_name in (
        "suitable_for_deterministic_estimator",
        "suitable_for_computational_model",
        "suitable_for_measurement_feedback",
    ):
        if not isinstance(record.get(field_name), bool):
            errors.append(f"{field_name} must be a boolean.")
    forbidden_hits = _find_forbidden_claim_fields(record)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_candidate_coverage_summary(summary: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(summary, dict):
        return {
            "is_valid": False,
            "errors": ["Candidate coverage summary must be a dictionary."],
            "warnings": [],
        }
    if summary.get("schema_version") != CANDIDATE_COVERAGE_SUMMARY_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CANDIDATE_COVERAGE_SUMMARY_SCHEMA_VERSION}.")
    for field_name in REQUIRED_CANDIDATE_COVERAGE_SUMMARY_FIELDS:
        if field_name not in summary:
            errors.append(f"{field_name} is required.")
    if not isinstance(summary.get("candidate_id"), str) or not summary.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if summary.get("coverage_status") not in CANDIDATE_COVERAGE_STATUSES:
        errors.append("coverage_status must be controlled.")
    criterion_records = summary.get("criterion_coverage_records", [])
    gap_records = summary.get("evidence_gap_records", [])
    if not isinstance(criterion_records, list):
        errors.append("criterion_coverage_records must be a list.")
        criterion_records = []
    if not isinstance(gap_records, list):
        errors.append("evidence_gap_records must be a list.")
        gap_records = []
    for index, record in enumerate(criterion_records):
        validation = validate_criterion_coverage_record(record)
        if validation["errors"]:
            errors.append(
                f"criterion_coverage_records[{index}] failed validation: "
                + "; ".join(validation["errors"])
            )
        warnings.extend(validation["warnings"])
    for index, record in enumerate(gap_records):
        validation = validate_evidence_gap_record(record)
        if validation["errors"]:
            errors.append(
                f"evidence_gap_records[{index}] failed validation: "
                + "; ".join(validation["errors"])
            )
        warnings.extend(validation["warnings"])
    if summary.get("coverage_status") == "placeholder_only":
        warnings.append("Candidate coverage is placeholder-only.")
    if int(summary.get("evidence_gap_count", 0)) > 0:
        warnings.append("Candidate coverage has evidence gaps.")
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def validate_criteria_coverage_summary_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Criteria coverage summary plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != CRITERIA_COVERAGE_SUMMARY_PLAN_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {CRITERIA_COVERAGE_SUMMARY_PLAN_SCHEMA_VERSION}."
        )
    if not isinstance(plan.get("candidate_coverage_summaries"), list):
        errors.append("candidate_coverage_summaries must be a list.")
    if not isinstance(plan.get("portfolio_coverage_summary"), dict):
        errors.append("portfolio_coverage_summary must be a dictionary.")
    if not isinstance(plan.get("criterion_coverage_records"), list):
        errors.append("criterion_coverage_records must be a list.")
    if not isinstance(plan.get("evidence_gap_records"), list):
        errors.append("evidence_gap_records must be a list.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")

    summaries = plan.get("candidate_coverage_summaries", [])
    if isinstance(summaries, list):
        if not summaries:
            warnings.append("No candidate coverage summaries are present.")
        for index, summary in enumerate(summaries):
            validation = validate_candidate_coverage_summary(summary)
            if validation["errors"]:
                errors.append(
                    f"candidate_coverage_summaries[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])
        if summaries and all(
            isinstance(summary, dict)
            and summary.get("coverage_status") == "placeholder_only"
            for summary in summaries
        ):
            warnings.append("All candidates have placeholder-only coverage.")

    for field_name, validator in (
        ("criterion_coverage_records", validate_criterion_coverage_record),
        ("evidence_gap_records", validate_evidence_gap_record),
    ):
        records = plan.get(field_name, [])
        if isinstance(records, list):
            for index, record in enumerate(records):
                validation = validator(record)
                if validation["errors"]:
                    errors.append(
                        f"{field_name}[{index}] failed validation: "
                        + "; ".join(validation["errors"])
                    )
                warnings.extend(validation["warnings"])

    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": unique_preserve_order(warnings),
    }


def criteria_coverage_summary(plan: dict) -> dict:
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "candidate_count": int(plan.get("candidate_count", 0)),
        "criterion_coverage_record_count": int(
            plan.get("criterion_coverage_record_count", 0)
        ),
        "evidence_gap_count": int(plan.get("evidence_gap_count", 0)),
        "populated_value_count": int(plan.get("populated_value_count", 0)),
        "placeholder_value_count": int(plan.get("placeholder_value_count", 0)),
        "invalid_value_count": int(plan.get("invalid_value_count", 0)),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(
            plan, "live_source_retrieval_allowed"
        ),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_criteria_coverage_summary_plan() -> dict:
    return build_criteria_coverage_summary_plan(
        hot_section_demo_criteria_result_integration_plan(),
        model_provenance_required=True,
        measurement_feedback_required=False,
    )
