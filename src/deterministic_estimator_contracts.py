from __future__ import annotations

import re
from typing import TypedDict

from src.candidate_criteria_valuation import (
    hot_section_demo_candidate_criteria_valuation_plan,
    validate_candidate_criteria_valuation_plan,
    validate_valuation_work_item,
)
from src.criteria_value_schema import (
    CRITERION_VALUE_SCHEMA_VERSION,
    criterion_value_placeholder,
    validate_criterion_value,
)


DETERMINISTIC_ESTIMATOR_CONTRACT_PLAN_SCHEMA_VERSION = (
    "deterministic_estimator_contract_plan_v1"
)
DETERMINISTIC_ESTIMATOR_REQUEST_SCHEMA_VERSION = "deterministic_estimator_request_v1"
DETERMINISTIC_ESTIMATOR_RESULT_SCHEMA_VERSION = "deterministic_estimator_result_v1"

ESTIMATOR_REQUEST_STATUSES: tuple[str, ...] = (
    "planned",
    "unsupported",
    "blocked_invalid_work_item",
    "placeholder_only",
)

ESTIMATOR_RESULT_STATUSES: tuple[str, ...] = (
    "placeholder_only",
    "not_run",
    "unsupported",
    "invalid_input",
)

DETERMINISTIC_ESTIMATOR_IDS: tuple[str, ...] = (
    "thermal_environment_rule_estimator",
    "degradation_resistance_rule_estimator",
    "failure_mode_rule_estimator",
    "manufacturability_rule_estimator",
    "inspection_repair_rule_estimator",
    "cost_burden_rule_estimator",
    "sustainability_burden_rule_estimator",
    "supply_risk_rule_estimator",
    "evidence_maturity_rule_estimator",
    "qualification_risk_rule_estimator",
    "gradient_feasibility_rule_estimator",
    "model_confidence_placeholder_estimator",
    "measurement_feedback_readiness_placeholder_estimator",
)

ESTIMATOR_ID_TO_LABEL: dict[str, str] = {
    "thermal_environment_rule_estimator": "Thermal environment rule estimator",
    "degradation_resistance_rule_estimator": "Degradation resistance rule estimator",
    "failure_mode_rule_estimator": "Failure mode rule estimator",
    "manufacturability_rule_estimator": "Manufacturability rule estimator",
    "inspection_repair_rule_estimator": "Inspection and repair rule estimator",
    "cost_burden_rule_estimator": "Cost burden rule estimator",
    "sustainability_burden_rule_estimator": "Sustainability burden rule estimator",
    "supply_risk_rule_estimator": "Supply risk rule estimator",
    "evidence_maturity_rule_estimator": "Evidence maturity rule estimator",
    "qualification_risk_rule_estimator": "Qualification risk rule estimator",
    "gradient_feasibility_rule_estimator": "Gradient feasibility rule estimator",
    "model_confidence_placeholder_estimator": "Model confidence placeholder estimator",
    "measurement_feedback_readiness_placeholder_estimator": "Measurement feedback readiness placeholder estimator",
}

ESTIMATOR_ID_TO_FAMILIES: dict[str, tuple[str, ...]] = {
    "thermal_environment_rule_estimator": ("functional_performance",),
    "degradation_resistance_rule_estimator": ("functional_performance",),
    "failure_mode_rule_estimator": ("failure_mode_resilience",),
    "manufacturability_rule_estimator": ("manufacturability",),
    "inspection_repair_rule_estimator": ("inspection_repair",),
    "cost_burden_rule_estimator": ("through_life_cost",),
    "sustainability_burden_rule_estimator": ("sustainability",),
    "supply_risk_rule_estimator": ("supply_risk",),
    "evidence_maturity_rule_estimator": ("evidence_maturity",),
    "qualification_risk_rule_estimator": ("qualification_risk",),
    "gradient_feasibility_rule_estimator": ("gradient_specific_feasibility",),
    "model_confidence_placeholder_estimator": ("model_confidence",),
    "measurement_feedback_readiness_placeholder_estimator": (
        "measurement_feedback_readiness",
    ),
}

CRITERION_ID_TO_PREFERRED_ESTIMATOR_ID: dict[str, str] = {
    "temperature_capability": "thermal_environment_rule_estimator",
    "oxidation_resistance": "degradation_resistance_rule_estimator",
    "corrosion_resistance": "degradation_resistance_rule_estimator",
    "thermal_cycling_resilience": "failure_mode_rule_estimator",
    "coating_spallation_risk": "failure_mode_rule_estimator",
    "gradient_transition_risk": "gradient_feasibility_rule_estimator",
    "creep_resistance": "failure_mode_rule_estimator",
    "fatigue_resistance": "failure_mode_rule_estimator",
    "fracture_toughness": "failure_mode_rule_estimator",
    "thermal_shock_resistance": "failure_mode_rule_estimator",
    "density_weight": "manufacturability_rule_estimator",
    "manufacturability": "manufacturability_rule_estimator",
    "process_window_sensitivity": "manufacturability_rule_estimator",
    "inspection_burden": "inspection_repair_rule_estimator",
    "repairability": "inspection_repair_rule_estimator",
    "lifecycle_cost": "cost_burden_rule_estimator",
    "acquisition_cost": "cost_burden_rule_estimator",
    "manufacturing_cost": "cost_burden_rule_estimator",
    "inspection_cost": "cost_burden_rule_estimator",
    "repair_cost": "cost_burden_rule_estimator",
    "qualification_cost": "cost_burden_rule_estimator",
    "embodied_carbon": "sustainability_burden_rule_estimator",
    "critical_material_exposure": "sustainability_burden_rule_estimator",
    "recyclability": "sustainability_burden_rule_estimator",
    "process_energy_burden": "sustainability_burden_rule_estimator",
    "supply_risk": "supply_risk_rule_estimator",
    "evidence_maturity": "evidence_maturity_rule_estimator",
    "qualification_risk": "qualification_risk_rule_estimator",
    "model_confidence": "model_confidence_placeholder_estimator",
    "measurement_feedback_readiness": "measurement_feedback_readiness_placeholder_estimator",
}

REQUIRED_ESTIMATOR_REQUEST_FIELDS: tuple[str, ...] = (
    "schema_version",
    "estimator_request_id",
    "work_item_id",
    "candidate_id",
    "criterion_id",
    "criterion_label",
    "criterion_family",
    "architecture_type",
    "generator_request_id",
    "estimator_id",
    "estimator_label",
    "request_status",
    "deterministic_estimation_allowed",
    "live_model_call_allowed",
    "live_source_retrieval_allowed",
    "input_work_item",
    "assumptions",
    "warnings",
)

REQUIRED_ESTIMATOR_RESULT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "estimator_request_id",
    "work_item_id",
    "candidate_id",
    "criterion_id",
    "estimator_id",
    "result_status",
    "criterion_value",
    "estimator_notes",
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


class DeterministicEstimatorCapability(TypedDict, total=False):
    estimator_id: str
    label: str
    supported_criteria_families: list[str]
    deterministic_only: bool
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    implementation_status: str


class DeterministicEstimatorRequest(TypedDict, total=False):
    schema_version: str
    estimator_request_id: str
    work_item_id: str
    candidate_id: str
    criterion_id: str
    criterion_label: str
    criterion_family: str
    architecture_type: str
    generator_request_id: str
    estimator_id: str
    estimator_label: str
    request_status: str
    deterministic_estimation_allowed: bool
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    input_work_item: dict
    assumptions: list[str]
    warnings: list[str]


class DeterministicEstimatorResult(TypedDict, total=False):
    schema_version: str
    estimator_request_id: str
    work_item_id: str
    candidate_id: str
    criterion_id: str
    estimator_id: str
    result_status: str
    criterion_value: dict
    estimator_notes: str
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    assumptions: list[str]
    warnings: list[str]


class DeterministicEstimatorContractPlan(TypedDict, total=False):
    schema_version: str
    source_candidate_criteria_valuation_plan_version: str
    estimator_capabilities: list[dict]
    estimator_requests: list[dict]
    placeholder_results: list[dict]
    estimator_request_count: int
    placeholder_result_count: int
    deterministic_estimation_allowed: bool
    live_model_call_allowed: bool
    live_source_retrieval_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class DeterministicEstimatorValidationResult(TypedDict, total=False):
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


def estimator_label(estimator_id: str) -> str:
    return ESTIMATOR_ID_TO_LABEL.get(estimator_id, humanise_identifier(estimator_id))


def preferred_estimator_id_for_criterion(criterion_id: str) -> str:
    return CRITERION_ID_TO_PREFERRED_ESTIMATOR_ID.get(
        criterion_id, "evidence_maturity_rule_estimator"
    )


def estimator_capability(estimator_id: str) -> dict:
    return {
        "estimator_id": estimator_id,
        "label": estimator_label(estimator_id),
        "supported_criteria_families": list(
            ESTIMATOR_ID_TO_FAMILIES.get(estimator_id, ())
        ),
        "deterministic_only": True,
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "implementation_status": "contract_only",
    }


def estimator_capabilities() -> list[dict]:
    return [
        estimator_capability(estimator_id)
        for estimator_id in DETERMINISTIC_ESTIMATOR_IDS
    ]


def work_item_supports_deterministic_estimation(work_item: dict) -> bool:
    if not isinstance(work_item, dict):
        return False
    return (
        "deterministic_estimator"
        in normalise_string_list(work_item.get("allowed_method_types", []))
        and work_item.get("valuation_status") != "blocked_invalid_candidate"
        and work_item.get("live_model_call_allowed") is False
        and work_item.get("live_source_retrieval_allowed") is False
    )


def estimator_request_id_for(work_item_id: str, estimator_id: str) -> str:
    return (
        "deterministic_"
        f"{slugify_identifier(work_item_id)}_"
        f"{slugify_identifier(estimator_id)}"
    )


def estimator_request_for_work_item(work_item: dict) -> dict:
    input_work_item = dict(work_item) if isinstance(work_item, dict) else {}
    validation = validate_valuation_work_item(input_work_item)
    criterion_id = str(input_work_item.get("criterion_id", ""))
    estimator_id = preferred_estimator_id_for_criterion(criterion_id)
    deterministic_allowed = work_item_supports_deterministic_estimation(input_work_item)
    if validation["is_valid"] and deterministic_allowed:
        request_status = "planned"
    elif not validation["is_valid"]:
        request_status = "blocked_invalid_work_item"
    else:
        request_status = "unsupported"
    warnings = unique_preserve_order(
        normalise_string_list(input_work_item.get("warnings", []))
        + normalise_string_list(validation.get("errors", []))
        + normalise_string_list(validation.get("warnings", []))
    )
    return {
        "schema_version": DETERMINISTIC_ESTIMATOR_REQUEST_SCHEMA_VERSION,
        "estimator_request_id": estimator_request_id_for(
            str(input_work_item.get("work_item_id", "")), estimator_id
        ),
        "work_item_id": str(input_work_item.get("work_item_id", "")),
        "candidate_id": str(input_work_item.get("candidate_id", "")),
        "criterion_id": criterion_id,
        "criterion_label": str(input_work_item.get("criterion_label", "")),
        "criterion_family": str(input_work_item.get("criterion_family", "")),
        "architecture_type": str(input_work_item.get("architecture_type", "")),
        "generator_request_id": str(input_work_item.get("generator_request_id", "")),
        "estimator_id": estimator_id,
        "estimator_label": estimator_label(estimator_id),
        "request_status": request_status,
        "deterministic_estimation_allowed": deterministic_allowed,
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "input_work_item": input_work_item,
        "assumptions": [
            "Deterministic estimator request is contract-only; no estimate has been run."
        ],
        "warnings": warnings,
    }


def estimator_requests_from_valuation_plan(plan: dict) -> list[dict]:
    work_items = plan.get("work_items", [])
    if not isinstance(work_items, list):
        return []
    return [
        estimator_request_for_work_item(work_item)
        for work_item in work_items
        if isinstance(work_item, dict)
    ]


def placeholder_result_for_request(request: dict) -> dict:
    input_work_item = request.get("input_work_item", {})
    criterion_value = (
        input_work_item.get("criterion_value", {})
        if isinstance(input_work_item, dict)
        else {}
    )
    if not (
        isinstance(criterion_value, dict)
        and validate_criterion_value(criterion_value)["is_valid"]
    ):
        criterion_value = criterion_value_placeholder(
            str(request.get("candidate_id", "")),
            str(request.get("criterion_id", "")),
        )

    request_status = request.get("request_status")
    if request_status == "planned":
        result_status = "placeholder_only"
    elif request_status == "unsupported":
        result_status = "unsupported"
    elif request_status == "blocked_invalid_work_item":
        result_status = "invalid_input"
    else:
        result_status = "not_run"

    return {
        "schema_version": DETERMINISTIC_ESTIMATOR_RESULT_SCHEMA_VERSION,
        "estimator_request_id": str(request.get("estimator_request_id", "")),
        "work_item_id": str(request.get("work_item_id", "")),
        "candidate_id": str(request.get("candidate_id", "")),
        "criterion_id": str(request.get("criterion_id", "")),
        "estimator_id": str(request.get("estimator_id", "")),
        "result_status": result_status,
        "criterion_value": dict(criterion_value),
        "estimator_notes": "Placeholder result only; deterministic estimator has not been implemented or run.",
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "assumptions": ["Result is a placeholder contract, not an estimate."],
        "warnings": normalise_string_list(request.get("warnings", [])),
    }


def build_deterministic_estimator_contract_plan(candidate_criteria_plan: dict) -> dict:
    validation = validate_candidate_criteria_valuation_plan(candidate_criteria_plan)
    requests = estimator_requests_from_valuation_plan(candidate_criteria_plan)
    results = [placeholder_result_for_request(request) for request in requests]
    assumptions = unique_preserve_order(
        normalise_string_list(candidate_criteria_plan.get("assumptions", []))
        + [
            "Deterministic estimator contract plan derived from CandidateCriteriaValuationPlan."
        ]
    )
    warnings = unique_preserve_order(
        normalise_string_list(candidate_criteria_plan.get("warnings", []))
        + normalise_string_list(validation.get("warnings", []))
    )
    return {
        "schema_version": DETERMINISTIC_ESTIMATOR_CONTRACT_PLAN_SCHEMA_VERSION,
        "source_candidate_criteria_valuation_plan_version": str(
            candidate_criteria_plan.get("schema_version", "")
        ),
        "estimator_capabilities": estimator_capabilities(),
        "estimator_requests": requests,
        "placeholder_results": results,
        "estimator_request_count": len(requests),
        "placeholder_result_count": len(results),
        "deterministic_estimation_allowed": any(
            request.get("request_status") == "planned" for request in requests
        ),
        "live_model_call_allowed": False,
        "live_source_retrieval_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": normalise_string_list(
            candidate_criteria_plan.get("hard_constraints", [])
        ),
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


def validate_estimator_request(request: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(request, dict):
        return {
            "is_valid": False,
            "errors": ["Estimator request must be a dictionary."],
            "warnings": [],
        }
    if request.get("schema_version") != DETERMINISTIC_ESTIMATOR_REQUEST_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {DETERMINISTIC_ESTIMATOR_REQUEST_SCHEMA_VERSION}."
        )
    for field_name in REQUIRED_ESTIMATOR_REQUEST_FIELDS:
        if field_name not in request:
            errors.append(f"{field_name} is required.")
    for field_name in ("estimator_request_id", "work_item_id", "candidate_id", "criterion_id"):
        if not isinstance(request.get(field_name), str) or not request.get(field_name):
            errors.append(f"{field_name} must be a non-empty string.")
    if request.get("estimator_id") not in DETERMINISTIC_ESTIMATOR_IDS:
        errors.append("estimator_id must be controlled.")
    if request.get("request_status") not in ESTIMATOR_REQUEST_STATUSES:
        errors.append("request_status must be controlled.")
    if not isinstance(request.get("deterministic_estimation_allowed"), bool):
        errors.append("deterministic_estimation_allowed must be a boolean.")
    if request.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if request.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if not isinstance(request.get("input_work_item"), dict):
        errors.append("input_work_item must be a dictionary.")
    forbidden_hits = _find_forbidden_claim_fields(request)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_estimator_result(result: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(result, dict):
        return {
            "is_valid": False,
            "errors": ["Estimator result must be a dictionary."],
            "warnings": [],
        }
    if result.get("schema_version") != DETERMINISTIC_ESTIMATOR_RESULT_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {DETERMINISTIC_ESTIMATOR_RESULT_SCHEMA_VERSION}."
        )
    for field_name in REQUIRED_ESTIMATOR_RESULT_FIELDS:
        if field_name not in result:
            errors.append(f"{field_name} is required.")
    for field_name in ("estimator_request_id", "work_item_id", "candidate_id", "criterion_id"):
        if not isinstance(result.get(field_name), str) or not result.get(field_name):
            errors.append(f"{field_name} must be a non-empty string.")
    if result.get("estimator_id") not in DETERMINISTIC_ESTIMATOR_IDS:
        errors.append("estimator_id must be controlled.")
    if result.get("result_status") not in ESTIMATOR_RESULT_STATUSES:
        errors.append("result_status must be controlled.")
    if not isinstance(result.get("criterion_value"), dict):
        errors.append("criterion_value must be a dictionary.")
    else:
        value_result = validate_criterion_value(result["criterion_value"])
        if value_result["errors"]:
            errors.append(
                "criterion_value failed validation: "
                + "; ".join(value_result["errors"])
            )
        warnings.extend(value_result["warnings"])
    if result.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if result.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    forbidden_hits = _find_forbidden_claim_fields(result)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_deterministic_estimator_contract_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Deterministic estimator contract plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != DETERMINISTIC_ESTIMATOR_CONTRACT_PLAN_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {DETERMINISTIC_ESTIMATOR_CONTRACT_PLAN_SCHEMA_VERSION}."
        )
    for field_name in ("estimator_capabilities", "estimator_requests", "placeholder_results"):
        if not isinstance(plan.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    if not isinstance(plan.get("deterministic_estimation_allowed"), bool):
        errors.append("deterministic_estimation_allowed must be a boolean.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")

    requests = plan.get("estimator_requests", [])
    if isinstance(requests, list):
        if not requests:
            warnings.append("No estimator requests are present.")
        if not any(
            isinstance(request, dict) and request.get("request_status") == "planned"
            for request in requests
        ):
            warnings.append("No planned estimator requests are present.")
        for index, request in enumerate(requests):
            result = validate_estimator_request(request)
            if result["errors"]:
                errors.append(
                    f"estimator_requests[{index}] failed validation: "
                    + "; ".join(result["errors"])
                )
            warnings.extend(result["warnings"])

    results = plan.get("placeholder_results", [])
    if isinstance(results, list):
        for index, result in enumerate(results):
            validation = validate_estimator_result(result)
            if validation["errors"]:
                errors.append(
                    f"placeholder_results[{index}] failed validation: "
                    + "; ".join(validation["errors"])
                )
            warnings.extend(validation["warnings"])

    return {"is_valid": not errors, "errors": errors, "warnings": unique_preserve_order(warnings)}


def deterministic_estimator_contract_summary(plan: dict) -> dict:
    requests = plan.get("estimator_requests", [])
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "estimator_capability_count": len(plan.get("estimator_capabilities", []))
        if isinstance(plan.get("estimator_capabilities"), list)
        else 0,
        "estimator_request_count": int(plan.get("estimator_request_count", 0)),
        "planned_estimator_request_count": len(
            [
                request
                for request in requests
                if isinstance(request, dict) and request.get("request_status") == "planned"
            ]
        )
        if isinstance(requests, list)
        else 0,
        "unsupported_estimator_request_count": len(
            [
                request
                for request in requests
                if isinstance(request, dict)
                and request.get("request_status") == "unsupported"
            ]
        )
        if isinstance(requests, list)
        else 0,
        "placeholder_result_count": int(plan.get("placeholder_result_count", 0)),
        "deterministic_estimation_allowed": bool_value(
            plan, "deterministic_estimation_allowed"
        ),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "live_source_retrieval_allowed": bool_value(
            plan, "live_source_retrieval_allowed"
        ),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_deterministic_estimator_contract_plan() -> dict:
    return build_deterministic_estimator_contract_plan(
        hot_section_demo_candidate_criteria_valuation_plan()
    )
