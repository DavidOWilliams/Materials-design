from __future__ import annotations

from typing import TypedDict

from src.candidate_source_orchestrator import (
    hot_section_demo_source_orchestration_plan,
    validate_source_orchestration_plan,
)


GENERATOR_REQUEST_SCHEMA_VERSION = "candidate_generator_requests_v1"

GENERATOR_REQUEST_STATUSES: tuple[str, ...] = (
    "planned",
    "placeholder_only",
    "disabled",
    "blocked_research_mode",
)

GENERATOR_REQUEST_TYPES: tuple[str, ...] = (
    "candidate_generator",
    "component_generator",
    "template_generator",
    "system_assembler",
    "criteria_evidence_request",
    "model_estimate_request",
    "measurement_feedback_request",
)

GENERATOR_REQUEST_IDS: tuple[str, ...] = (
    "metallic_reference_generation",
    "ceramic_reference_generation",
    "cmc_reference_generation",
    "pmc_reference_generation",
    "coating_component_generation",
    "gradient_template_generation",
    "hybrid_reference_generation",
    "bulk_material_assembly",
    "substrate_plus_coating_assembly",
    "cmc_ebc_system_assembly",
    "pmc_system_assembly",
    "hybrid_system_assembly",
    "spatially_graded_am_system_assembly",
    "research_generated_system_wrapping",
    "criteria_evidence_preparation",
    "model_estimate_preparation",
    "measurement_feedback_preparation",
)

SOURCE_TO_GENERATOR_REQUESTS: dict[str, str] = {
    "metallic_reference_sources": "metallic_reference_generation",
    "ceramic_reference_sources": "ceramic_reference_generation",
    "cmc_reference_sources": "cmc_reference_generation",
    "pmc_reference_sources": "pmc_reference_generation",
    "coating_reference_sources": "coating_component_generation",
    "gradient_template_sources": "gradient_template_generation",
    "criteria_reference_sources": "criteria_evidence_preparation",
    "evidence_maturity_sources": "criteria_evidence_preparation",
    "model_estimate_sources": "model_estimate_preparation",
    "measurement_feedback_sources": "measurement_feedback_preparation",
}

REQUEST_ID_TO_TYPE: dict[str, str] = {
    "metallic_reference_generation": "candidate_generator",
    "ceramic_reference_generation": "candidate_generator",
    "cmc_reference_generation": "candidate_generator",
    "pmc_reference_generation": "candidate_generator",
    "coating_component_generation": "component_generator",
    "gradient_template_generation": "template_generator",
    "hybrid_reference_generation": "candidate_generator",
    "bulk_material_assembly": "system_assembler",
    "substrate_plus_coating_assembly": "system_assembler",
    "cmc_ebc_system_assembly": "system_assembler",
    "pmc_system_assembly": "system_assembler",
    "hybrid_system_assembly": "system_assembler",
    "spatially_graded_am_system_assembly": "system_assembler",
    "research_generated_system_wrapping": "system_assembler",
    "criteria_evidence_preparation": "criteria_evidence_request",
    "model_estimate_preparation": "model_estimate_request",
    "measurement_feedback_preparation": "measurement_feedback_request",
}

REQUEST_ID_TO_LABEL: dict[str, str] = {
    "metallic_reference_generation": "Metallic reference generation",
    "ceramic_reference_generation": "Ceramic reference generation",
    "cmc_reference_generation": "CMC reference generation",
    "pmc_reference_generation": "PMC reference generation",
    "coating_component_generation": "Coating component generation",
    "gradient_template_generation": "Gradient template generation",
    "hybrid_reference_generation": "Hybrid reference generation",
    "bulk_material_assembly": "Bulk material assembly",
    "substrate_plus_coating_assembly": "Substrate-plus-coating assembly",
    "cmc_ebc_system_assembly": "CMC + EBC system assembly",
    "pmc_system_assembly": "PMC system assembly",
    "hybrid_system_assembly": "Hybrid system assembly",
    "spatially_graded_am_system_assembly": "Spatially graded AM system assembly",
    "research_generated_system_wrapping": "Research-generated system wrapping",
    "criteria_evidence_preparation": "Criteria evidence preparation",
    "model_estimate_preparation": "Model-estimate preparation",
    "measurement_feedback_preparation": "Measurement-feedback preparation",
}


class GeneratorRequest(TypedDict, total=False):
    request_id: str
    label: str
    request_type: str
    status: str
    enabled: bool
    live_source_retrieval_allowed: bool
    live_model_call_allowed: bool
    source_ids: list[str]
    required_inputs: list[str]
    request_parameters: dict
    research_only: bool
    reason: str


class CandidateGeneratorRequestPlan(TypedDict, total=False):
    schema_version: str
    source_orchestration_schema_version: str
    generator_requests: list[dict]
    generator_request_count: int
    placeholder_request_count: int
    system_assembly_request_count: int
    live_source_retrieval_allowed: bool
    live_model_call_allowed: bool
    research_mode_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class GeneratorRequestValidationResult(TypedDict, total=False):
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


def humanise_identifier(value: object) -> str:
    text = str(value).replace("_", " ").replace("-", " ").strip()
    if not text:
        return "Not specified"
    return text[:1].upper() + text[1:]


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def request_type(request_id: str) -> str:
    return REQUEST_ID_TO_TYPE.get(request_id, "candidate_generator")


def request_label(request_id: str) -> str:
    return REQUEST_ID_TO_LABEL.get(request_id, humanise_identifier(request_id))


def request_status_for_source_request(source_request: dict) -> str:
    if not isinstance(source_request, dict) or source_request.get("enabled") is not True:
        return "disabled"
    if source_request.get("status") == "placeholder_only":
        return "placeholder_only"
    return "planned"


def source_request_lookup(plan: dict) -> dict[str, dict]:
    source_requests = plan.get("source_requests", [])
    if not isinstance(source_requests, list):
        return {}
    lookup: dict[str, dict] = {}
    for source_request_record in source_requests:
        if not isinstance(source_request_record, dict):
            continue
        source_id = source_request_record.get("source_id")
        if isinstance(source_id, str) and source_id:
            lookup[source_id] = dict(source_request_record)
    return lookup


def generator_request(
    request_id: str,
    *,
    status: str = "planned",
    enabled: bool = True,
    source_ids: list[str] | None = None,
    required_inputs: list[str] | None = None,
    request_parameters: dict | None = None,
    research_only: bool = False,
    reason: str = "",
) -> dict:
    normalised_status = status if status in GENERATOR_REQUEST_STATUSES else "planned"
    return {
        "request_id": request_id,
        "label": request_label(request_id),
        "request_type": request_type(request_id),
        "status": normalised_status,
        "enabled": bool(enabled),
        "live_source_retrieval_allowed": False,
        "live_model_call_allowed": False,
        "source_ids": list(source_ids or []),
        "required_inputs": list(required_inputs or []),
        "request_parameters": dict(request_parameters or {}),
        "research_only": bool(research_only),
        "reason": reason,
    }


def request_parameters_from_source(source_request: dict) -> dict:
    source_parameters = source_request.get("request_parameters", {})
    parameters = dict(source_parameters) if isinstance(source_parameters, dict) else {}
    parameters["source_request_type"] = str(source_request.get("request_type", ""))
    parameters["source_request_status"] = str(source_request.get("status", ""))
    parameters["live_retrieval_allowed"] = bool_value(
        source_request, "live_retrieval_allowed"
    )
    return parameters


def _merged_status(statuses: list[str]) -> str:
    if any(status == "placeholder_only" for status in statuses):
        return "placeholder_only"
    if statuses and all(status == "disabled" for status in statuses):
        return "disabled"
    return "planned"


def generator_requests_from_source_requests(plan: dict) -> list[dict]:
    source_requests = plan.get("source_requests", [])
    if not isinstance(source_requests, list):
        return []

    grouped: dict[str, dict] = {}
    order: list[str] = []
    for source_request_record in source_requests:
        if not isinstance(source_request_record, dict):
            continue
        if source_request_record.get("enabled") is not True:
            continue
        source_id = source_request_record.get("source_id")
        if not isinstance(source_id, str):
            continue
        request_id = SOURCE_TO_GENERATOR_REQUESTS.get(source_id)
        if not request_id:
            continue
        parameters = request_parameters_from_source(source_request_record)
        status = request_status_for_source_request(source_request_record)
        if request_id not in grouped:
            grouped[request_id] = {
                "source_ids": [],
                "statuses": [],
                "source_parameters_by_id": {},
            }
            order.append(request_id)
        grouped[request_id]["source_ids"].append(source_id)
        grouped[request_id]["statuses"].append(status)
        grouped[request_id]["source_parameters_by_id"][source_id] = parameters

    requests: list[dict] = []
    for request_id in order:
        group = grouped[request_id]
        source_ids = unique_preserve_order(group["source_ids"])
        source_parameters_by_id = {
            source_id: group["source_parameters_by_id"][source_id]
            for source_id in source_ids
        }
        if len(source_ids) == 1:
            request_parameters = dict(source_parameters_by_id[source_ids[0]])
        else:
            request_parameters = {
                "merged_sources": source_ids,
                "source_parameters_by_id": source_parameters_by_id,
            }
        requests.append(
            generator_request(
                request_id,
                status=_merged_status(group["statuses"]),
                enabled=True,
                source_ids=source_ids,
                request_parameters=request_parameters,
                reason="Generator request derived from source request contract.",
            )
        )
    return requests


def assembler_request(
    request_id: str,
    *,
    required_inputs: list[str],
    enabled: bool = True,
    research_only: bool = False,
    reason: str = "",
) -> dict:
    return generator_request(
        request_id,
        status="planned",
        enabled=enabled,
        required_inputs=required_inputs,
        research_only=research_only,
        reason=reason,
    )


def assembler_requests_from_source_plan(plan: dict) -> list[dict]:
    base_requests = generator_requests_from_source_requests(plan)
    request_ids = [request["request_id"] for request in base_requests]
    requests: list[dict] = []

    def add(request_id: str, required_inputs: list[str], reason: str, research_only: bool = False) -> None:
        if request_id not in [request["request_id"] for request in requests]:
            requests.append(
                assembler_request(
                    request_id,
                    required_inputs=required_inputs,
                    reason=reason,
                    research_only=research_only,
                )
            )

    if "metallic_reference_generation" in request_ids:
        add(
            "bulk_material_assembly",
            ["metallic_reference_generation"],
            "Metallic reference generation is available.",
        )
    if {
        "metallic_reference_generation",
        "coating_component_generation",
    } <= set(request_ids):
        add(
            "substrate_plus_coating_assembly",
            ["metallic_reference_generation", "coating_component_generation"],
            "Metallic references and coating components are available.",
        )
    if {"cmc_reference_generation", "coating_component_generation"} <= set(request_ids):
        add(
            "cmc_ebc_system_assembly",
            ["cmc_reference_generation", "coating_component_generation"],
            "CMC references and coating components are available.",
        )
    if "pmc_reference_generation" in request_ids:
        add(
            "pmc_system_assembly",
            ["pmc_reference_generation"],
            "PMC reference generation is available.",
        )
    if "gradient_template_generation" in request_ids:
        add(
            "spatially_graded_am_system_assembly",
            ["gradient_template_generation"],
            "Gradient template generation is available.",
        )
    if "hybrid_reference_generation" in request_ids:
        add(
            "hybrid_system_assembly",
            ["hybrid_reference_generation"],
            "Hybrid reference generation is available.",
        )
    elif {"metallic_reference_generation", "gradient_template_generation"} <= set(request_ids):
        add(
            "hybrid_system_assembly",
            ["metallic_reference_generation", "gradient_template_generation"],
            "Metallic references and gradient templates can support future hybrid assembly.",
        )
    if (
        bool_value(plan, "research_mode_allowed")
        and "model_estimate_preparation" in request_ids
    ):
        add(
            "research_generated_system_wrapping",
            ["model_estimate_preparation"],
            "Research mode is allowed for future generated-system wrapping.",
            research_only=True,
        )
    return requests


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values]


def build_generator_request_plan(plan: dict) -> dict:
    validation = validate_source_orchestration_plan(plan)
    generator_requests = generator_requests_from_source_requests(plan)
    assembler_requests = assembler_requests_from_source_plan(plan)
    combined_requests = generator_requests + assembler_requests
    warnings = unique_preserve_order(
        _string_list(plan.get("warnings", []))
        + _string_list(validation.get("warnings", []))
    )
    assumptions = unique_preserve_order(
        _string_list(plan.get("assumptions", []))
        + ["Generator request plan derived from CandidateSourceOrchestrationPlan."]
    )
    return {
        "schema_version": GENERATOR_REQUEST_SCHEMA_VERSION,
        "source_orchestration_schema_version": str(plan.get("schema_version", "")),
        "generator_requests": combined_requests,
        "generator_request_count": len(combined_requests),
        "placeholder_request_count": len(
            [
                request
                for request in combined_requests
                if request.get("status") == "placeholder_only"
            ]
        ),
        "system_assembly_request_count": len(
            [
                request
                for request in combined_requests
                if request.get("request_type") == "system_assembler"
            ]
        ),
        "live_source_retrieval_allowed": False,
        "live_model_call_allowed": False,
        "research_mode_allowed": bool_value(plan, "research_mode_allowed"),
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": _string_list(plan.get("hard_constraints", [])),
    }


def validate_generator_request_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Generator request plan must be a dictionary."],
            "warnings": [],
        }

    if plan.get("schema_version") != GENERATOR_REQUEST_SCHEMA_VERSION:
        errors.append(f"schema_version must be {GENERATOR_REQUEST_SCHEMA_VERSION}.")
    if not isinstance(plan.get("generator_requests"), list):
        errors.append("generator_requests must be a list.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")

    required_fields = (
        "request_id",
        "label",
        "request_type",
        "status",
        "enabled",
        "live_source_retrieval_allowed",
        "live_model_call_allowed",
        "source_ids",
        "required_inputs",
        "request_parameters",
        "research_only",
        "reason",
    )
    requests = plan.get("generator_requests", [])
    if isinstance(requests, list):
        if not requests:
            warnings.append("No generator requests exist.")
        for index, request in enumerate(requests):
            if not isinstance(request, dict):
                errors.append(f"generator_requests[{index}] must be a dictionary.")
                continue
            for field_name in required_fields:
                if field_name not in request:
                    errors.append(f"generator_requests[{index}].{field_name} is required.")
            if request.get("request_id") not in GENERATOR_REQUEST_IDS:
                errors.append(f"generator_requests[{index}].request_id must be controlled.")
            if request.get("request_type") not in GENERATOR_REQUEST_TYPES:
                errors.append(
                    f"generator_requests[{index}].request_type must be controlled."
                )
            if request.get("status") not in GENERATOR_REQUEST_STATUSES:
                errors.append(f"generator_requests[{index}].status must be controlled.")
            if request.get("live_source_retrieval_allowed") is not False:
                errors.append(
                    f"generator_requests[{index}].live_source_retrieval_allowed must be false."
                )
            if request.get("live_model_call_allowed") is not False:
                errors.append(
                    f"generator_requests[{index}].live_model_call_allowed must be false."
                )
            if (
                request.get("request_id") == "research_generated_system_wrapping"
                and request.get("enabled") is True
                and plan.get("research_mode_allowed") is False
            ):
                warnings.append(
                    "Research-generated system wrapping is enabled while research mode is not allowed."
                )
            if (
                request.get("request_id") == "model_estimate_preparation"
                and plan.get("live_model_call_allowed") is not False
            ):
                warnings.append(
                    "Model-estimate preparation is present, but live model calls are not explicitly disabled."
                )

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def generator_request_summary(plan: dict) -> dict:
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "generator_request_count": int(plan.get("generator_request_count", 0)),
        "placeholder_request_count": int(plan.get("placeholder_request_count", 0)),
        "system_assembly_request_count": int(
            plan.get("system_assembly_request_count", 0)
        ),
        "live_source_retrieval_allowed": bool_value(
            plan, "live_source_retrieval_allowed"
        ),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "research_mode_allowed": bool_value(plan, "research_mode_allowed"),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_generator_request_plan() -> dict:
    return build_generator_request_plan(hot_section_demo_source_orchestration_plan())
