from __future__ import annotations

import re
from typing import TypedDict

from src.candidate_normalisation_contracts import (
    hot_section_demo_candidate_normalisation_plan,
    normalised_candidate_template,
    validate_normalised_candidate,
)
from src.criteria_value_schema import (
    CRITERION_VALUE_SCHEMA_VERSION,
    build_criteria_valuation_plan,
    criterion_definition,
    criterion_value_placeholder,
    criterion_values_for_candidate,
    hot_section_demo_criteria_valuation_plan,
    validate_criteria_valuation_plan,
    validate_criterion_value,
)


CANDIDATE_CRITERIA_VALUATION_PLAN_SCHEMA_VERSION = (
    "candidate_criteria_valuation_plan_v1"
)
VALUATION_WORK_ITEM_SCHEMA_VERSION = "candidate_criteria_valuation_work_item_v1"

VALUATION_WORK_ITEM_STATUSES: tuple[str, ...] = (
    "planned",
    "placeholder_only",
    "blocked_invalid_candidate",
    "blocked_unknown_criterion",
    "completed_placeholder",
)

VALUATION_METHOD_TYPES: tuple[str, ...] = (
    "placeholder",
    "deterministic_estimator",
    "computational_model",
    "surrogate_model",
    "specialist_ai_model",
    "literature_extractor",
    "measurement_feedback",
)

ARCHITECTURE_TO_RELEVANT_CRITERIA_HINTS: dict[str, tuple[str, ...]] = {
    "metallic_system": (
        "temperature_capability",
        "oxidation_resistance",
        "creep_resistance",
        "fatigue_resistance",
        "manufacturability",
        "lifecycle_cost",
        "qualification_risk",
    ),
    "monolithic_ceramic_system": (
        "temperature_capability",
        "oxidation_resistance",
        "thermal_shock_resistance",
        "fracture_toughness",
        "manufacturability",
        "qualification_risk",
    ),
    "cmc_system": (
        "temperature_capability",
        "oxidation_resistance",
        "thermal_cycling_resilience",
        "coating_spallation_risk",
        "repairability",
        "qualification_risk",
    ),
    "pmc_system": (
        "density_weight",
        "manufacturability",
        "repairability",
        "recyclability",
        "lifecycle_cost",
    ),
    "substrate_plus_coating_system": (
        "temperature_capability",
        "oxidation_resistance",
        "coating_spallation_risk",
        "inspection_burden",
        "repairability",
        "qualification_risk",
    ),
    "coating_enabled_system": (
        "oxidation_resistance",
        "coating_spallation_risk",
        "inspection_burden",
        "repairability",
    ),
    "spatially_graded_am_system": (
        "gradient_transition_risk",
        "process_window_sensitivity",
        "manufacturability",
        "inspection_burden",
        "qualification_risk",
        "model_confidence",
    ),
    "hybrid_system": (
        "system_compatibility",
        "manufacturability",
        "inspection_burden",
        "repairability",
        "qualification_risk",
    ),
    "research_generated_system": (
        "model_confidence",
        "evidence_maturity",
        "qualification_risk",
    ),
    "unknown": ("evidence_maturity", "qualification_risk"),
}

REQUIRED_WORK_ITEM_FIELDS: tuple[str, ...] = (
    "schema_version",
    "work_item_id",
    "candidate_id",
    "criterion_id",
    "criterion_label",
    "criterion_family",
    "architecture_type",
    "generator_request_id",
    "valuation_status",
    "allowed_method_types",
    "preferred_placeholder_method",
    "criterion_value",
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "assumptions",
    "warnings",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)


class CandidateCriteriaValuationWorkItem(TypedDict, total=False):
    schema_version: str
    work_item_id: str
    candidate_id: str
    criterion_id: str
    criterion_label: str
    criterion_family: str
    architecture_type: str
    generator_request_id: str
    valuation_status: str
    allowed_method_types: list[str]
    preferred_placeholder_method: str
    criterion_value: dict
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    assumptions: list[str]
    warnings: list[str]


class CandidateCriteriaValuationPlan(TypedDict, total=False):
    schema_version: str
    source_criteria_valuation_plan_version: str
    candidate_count: int
    active_criteria: list[str]
    work_items: list[dict]
    criterion_values_by_candidate: dict[str, list[dict]]
    work_item_count: int
    placeholder_value_count: int
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    require_confidence: bool
    require_uncertainty: bool
    require_evidence_basis: bool
    require_model_provenance: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class CandidateCriteriaValuationValidationResult(TypedDict, total=False):
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


def candidate_id(candidate: dict) -> str:
    value = candidate.get("candidate_id") if isinstance(candidate, dict) else None
    return value if isinstance(value, str) and value else "unknown_candidate"


def candidate_architecture_type(candidate: dict) -> str:
    value = candidate.get("architecture_type") if isinstance(candidate, dict) else None
    return value if isinstance(value, str) and value else "unknown"


def candidate_generator_request_id(candidate: dict) -> str:
    value = candidate.get("generator_request_id") if isinstance(candidate, dict) else None
    return value if isinstance(value, str) and value else ""


def active_criteria_from_criteria_plan(criteria_plan: dict) -> list[str]:
    return normalise_string_list(criteria_plan.get("active_criteria", []))


def relevant_criteria_for_candidate(
    candidate: dict, active_criteria: list[str]
) -> list[str]:
    criteria = normalise_string_list(active_criteria)
    if not criteria:
        architecture_type = candidate_architecture_type(candidate)
        criteria = list(
            ARCHITECTURE_TO_RELEVANT_CRITERIA_HINTS.get(
                architecture_type,
                ARCHITECTURE_TO_RELEVANT_CRITERIA_HINTS["unknown"],
            )
        )
    criteria = unique_preserve_order(criteria)
    return criteria or ["evidence_maturity", "qualification_risk"]


def allowed_method_types_for_work_item(
    candidate: dict,
    criterion_id: str,
    criteria_plan: dict,
) -> list[str]:
    methods = ["placeholder", "deterministic_estimator"]
    if bool_value(criteria_plan, "require_model_provenance") or criterion_id == "model_confidence":
        methods.append("computational_model")
    if bool_value(criteria_plan, "require_measurement_provenance"):
        methods.append("measurement_feedback")
    return unique_preserve_order(methods)


def work_item_id_for(candidate_id: str, criterion_id: str) -> str:
    return f"valuate_{slugify_identifier(candidate_id)}_{slugify_identifier(criterion_id)}"


def valuation_work_item(
    candidate: dict,
    criterion_id: str,
    *,
    criteria_plan: dict,
) -> dict:
    definition = criterion_definition(criterion_id)
    resolved_candidate_id = candidate_id(candidate)
    criterion_value = criterion_value_placeholder(resolved_candidate_id, criterion_id)
    return {
        "schema_version": VALUATION_WORK_ITEM_SCHEMA_VERSION,
        "work_item_id": work_item_id_for(resolved_candidate_id, criterion_id),
        "candidate_id": resolved_candidate_id,
        "criterion_id": criterion_id,
        "criterion_label": definition["label"],
        "criterion_family": definition["family"],
        "architecture_type": candidate_architecture_type(candidate),
        "generator_request_id": candidate_generator_request_id(candidate),
        "valuation_status": "placeholder_only",
        "allowed_method_types": allowed_method_types_for_work_item(
            candidate, criterion_id, criteria_plan
        ),
        "preferred_placeholder_method": "placeholder",
        "criterion_value": criterion_value,
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "assumptions": ["Criterion value is a placeholder pending valuation."],
        "warnings": normalise_string_list(criterion_value.get("warnings", [])),
    }


def valuation_work_items_for_candidate(
    candidate: dict,
    *,
    criteria_plan: dict,
) -> list[dict]:
    candidate_copy = dict(candidate) if isinstance(candidate, dict) else {}
    validation = validate_normalised_candidate(candidate_copy)
    active_criteria = active_criteria_from_criteria_plan(criteria_plan)
    criteria = relevant_criteria_for_candidate(candidate_copy, active_criteria)
    work_items = [
        valuation_work_item(candidate_copy, criterion_id, criteria_plan=criteria_plan)
        for criterion_id in criteria
    ]
    if not validation["is_valid"]:
        validation_warnings = list(validation["errors"])
        for work_item in work_items:
            work_item["valuation_status"] = "blocked_invalid_candidate"
            work_item["warnings"] = unique_preserve_order(
                normalise_string_list(work_item.get("warnings", [])) + validation_warnings
            )
    return work_items


def criterion_values_by_candidate(work_items: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for work_item in work_items:
        if not isinstance(work_item, dict):
            continue
        candidate_key = str(work_item.get("candidate_id", "unknown_candidate"))
        value = work_item.get("criterion_value")
        if isinstance(value, dict):
            grouped.setdefault(candidate_key, []).append(dict(value))
    return grouped


def build_candidate_criteria_valuation_plan(
    candidates: list[dict],
    criteria_plan: dict,
) -> dict:
    criteria_validation = validate_criteria_valuation_plan(criteria_plan)
    candidate_records = [dict(candidate) for candidate in candidates]
    work_items: list[dict] = []
    for candidate_record in candidate_records:
        work_items.extend(
            valuation_work_items_for_candidate(
                candidate_record, criteria_plan=criteria_plan
            )
        )
    assumptions = unique_preserve_order(
        normalise_string_list(criteria_plan.get("assumptions", []))
        + [
            "Candidate criteria valuation plan derived from CriteriaValuationPlan and normalised candidates."
        ]
    )
    warnings = unique_preserve_order(
        normalise_string_list(criteria_plan.get("warnings", []))
        + normalise_string_list(criteria_validation.get("warnings", []))
    )
    return {
        "schema_version": CANDIDATE_CRITERIA_VALUATION_PLAN_SCHEMA_VERSION,
        "source_criteria_valuation_plan_version": str(
            criteria_plan.get("schema_version", "")
        ),
        "candidate_count": len(candidates),
        "active_criteria": active_criteria_from_criteria_plan(criteria_plan),
        "work_items": work_items,
        "criterion_values_by_candidate": criterion_values_by_candidate(work_items),
        "work_item_count": len(work_items),
        "placeholder_value_count": len(
            [
                work_item
                for work_item in work_items
                if isinstance(work_item.get("criterion_value"), dict)
                and work_item["criterion_value"].get("schema_version")
                == CRITERION_VALUE_SCHEMA_VERSION
            ]
        ),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "require_confidence": bool_value(criteria_plan, "require_confidence"),
        "require_uncertainty": bool_value(criteria_plan, "require_uncertainty"),
        "require_evidence_basis": bool_value(criteria_plan, "require_evidence_basis"),
        "require_model_provenance": bool_value(criteria_plan, "require_model_provenance"),
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": normalise_string_list(criteria_plan.get("hard_constraints", [])),
    }


def _find_forbidden_claim_fields(value: object, path: str = "root") -> list[str]:
    hits = []
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


def validate_valuation_work_item(work_item: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(work_item, dict):
        return {
            "is_valid": False,
            "errors": ["Valuation work item must be a dictionary."],
            "warnings": [],
        }
    if work_item.get("schema_version") != VALUATION_WORK_ITEM_SCHEMA_VERSION:
        errors.append(f"schema_version must be {VALUATION_WORK_ITEM_SCHEMA_VERSION}.")
    for field_name in REQUIRED_WORK_ITEM_FIELDS:
        if field_name not in work_item:
            errors.append(f"{field_name} is required.")
    if not isinstance(work_item.get("work_item_id"), str) or not work_item.get("work_item_id"):
        errors.append("work_item_id must be a non-empty string.")
    if not isinstance(work_item.get("candidate_id"), str) or not work_item.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if not isinstance(work_item.get("criterion_id"), str) or not work_item.get("criterion_id"):
        errors.append("criterion_id must be a non-empty string.")
    if work_item.get("valuation_status") not in VALUATION_WORK_ITEM_STATUSES:
        errors.append("valuation_status must be controlled.")
    if not isinstance(work_item.get("allowed_method_types"), list):
        errors.append("allowed_method_types must be a list.")
    else:
        for method in work_item["allowed_method_types"]:
            if method not in VALUATION_METHOD_TYPES:
                errors.append(f"allowed_method_types contains unsupported method: {method}.")
    if not isinstance(work_item.get("criterion_value"), dict):
        errors.append("criterion_value must be a dictionary.")
    else:
        result = validate_criterion_value(work_item["criterion_value"])
        if result["errors"]:
            errors.append(
                "criterion_value failed validation: " + "; ".join(result["errors"])
            )
        warnings.extend(result["warnings"])
    if work_item.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if work_item.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")

    forbidden_hits = _find_forbidden_claim_fields(work_item)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_candidate_criteria_valuation_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Candidate criteria valuation plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != CANDIDATE_CRITERIA_VALUATION_PLAN_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {CANDIDATE_CRITERIA_VALUATION_PLAN_SCHEMA_VERSION}."
        )
    if not isinstance(plan.get("active_criteria"), list):
        errors.append("active_criteria must be a list.")
    if not isinstance(plan.get("work_items"), list):
        errors.append("work_items must be a list.")
    if not isinstance(plan.get("criterion_values_by_candidate"), dict):
        errors.append("criterion_values_by_candidate must be a dictionary.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    for field_name in (
        "require_confidence",
        "require_uncertainty",
        "require_evidence_basis",
        "require_model_provenance",
    ):
        if not isinstance(plan.get(field_name), bool):
            errors.append(f"{field_name} must be a boolean.")

    work_items = plan.get("work_items", [])
    if isinstance(work_items, list):
        if not work_items:
            warnings.append("No work items are present.")
        for index, work_item in enumerate(work_items):
            result = validate_valuation_work_item(work_item)
            if result["errors"]:
                errors.append(
                    f"work_items[{index}] failed validation: "
                    + "; ".join(result["errors"])
                )
            warnings.extend(result["warnings"])
    if plan.get("candidate_count") == 0:
        warnings.append("No candidates are provided.")

    return {"is_valid": not errors, "errors": errors, "warnings": unique_preserve_order(warnings)}


def candidate_criteria_valuation_summary(plan: dict) -> dict:
    values_by_candidate = plan.get("criterion_values_by_candidate", {})
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "candidate_count": int(plan.get("candidate_count", 0)),
        "active_criteria_count": len(plan.get("active_criteria", []))
        if isinstance(plan.get("active_criteria"), list)
        else 0,
        "work_item_count": int(plan.get("work_item_count", 0)),
        "placeholder_value_count": int(plan.get("placeholder_value_count", 0)),
        "candidate_with_values_count": len(values_by_candidate)
        if isinstance(values_by_candidate, dict)
        else 0,
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(plan, "live_source_retrieval_allowed"),
        "require_confidence": bool_value(plan, "require_confidence"),
        "require_uncertainty": bool_value(plan, "require_uncertainty"),
        "require_evidence_basis": bool_value(plan, "require_evidence_basis"),
        "require_model_provenance": bool_value(plan, "require_model_provenance"),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_candidates() -> list[dict]:
    return [
        normalised_candidate_template(
            "metallic_reference_generation",
            candidate_id="demo_metallic_candidate",
            system_name="Demo metallic candidate",
            material_family="contract_template",
            active_criteria=[],
        ),
        normalised_candidate_template(
            "cmc_ebc_system_assembly",
            candidate_id="demo_cmc_ebc_system",
            system_name="Demo CMC EBC system",
            material_family="contract_template",
            active_criteria=[],
        ),
        normalised_candidate_template(
            "spatially_graded_am_system_assembly",
            candidate_id="demo_spatial_gradient_system",
            system_name="Demo spatial gradient system",
            material_family="contract_template",
            active_criteria=[],
        ),
    ]


def hot_section_demo_candidate_criteria_valuation_plan() -> dict:
    return build_candidate_criteria_valuation_plan(
        hot_section_demo_candidates(),
        hot_section_demo_criteria_valuation_plan(),
    )


def hot_section_demo_candidate_criteria_valuation_plan_from_normalisation() -> dict:
    return build_candidate_criteria_valuation_plan(
        hot_section_demo_candidates(),
        build_criteria_valuation_plan(hot_section_demo_candidate_normalisation_plan()),
    )
