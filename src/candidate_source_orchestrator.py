from __future__ import annotations

from typing import TypedDict

from src.material_system_scope_planner import (
    hot_section_demo_scope_plan,
    validate_scope_plan,
)


SOURCE_ORCHESTRATION_SCHEMA_VERSION = "candidate_source_orchestration_v1"

SOURCE_REQUEST_STATUSES: tuple[str, ...] = (
    "planned",
    "disabled",
    "blocked_research_mode",
    "placeholder_only",
)

SOURCE_REQUEST_TYPES: tuple[str, ...] = (
    "candidate_reference",
    "component_reference",
    "template_reference",
    "process_reference",
    "criteria_reference",
    "evidence_reference",
    "model_estimate_placeholder",
    "measurement_feedback_placeholder",
)

SOURCE_ID_TO_REQUEST_TYPE: dict[str, str] = {
    "metallic_reference_sources": "candidate_reference",
    "ceramic_reference_sources": "candidate_reference",
    "cmc_reference_sources": "candidate_reference",
    "pmc_reference_sources": "candidate_reference",
    "coating_reference_sources": "component_reference",
    "gradient_template_sources": "template_reference",
    "process_route_sources": "process_reference",
    "criteria_reference_sources": "criteria_reference",
    "evidence_maturity_sources": "evidence_reference",
    "model_estimate_sources": "model_estimate_placeholder",
    "measurement_feedback_sources": "measurement_feedback_placeholder",
}

SOURCE_ID_TO_LABEL: dict[str, str] = {
    "metallic_reference_sources": "Metallic reference sources",
    "ceramic_reference_sources": "Ceramic reference sources",
    "cmc_reference_sources": "CMC reference sources",
    "pmc_reference_sources": "PMC reference sources",
    "coating_reference_sources": "Coating reference sources",
    "gradient_template_sources": "Gradient template sources",
    "process_route_sources": "Process-route sources",
    "criteria_reference_sources": "Criteria reference sources",
    "evidence_maturity_sources": "Evidence maturity sources",
    "model_estimate_sources": "Model-estimate placeholders",
    "measurement_feedback_sources": "Measurement-feedback placeholders",
}

SOURCE_REQUEST_PURPOSES: dict[str, str] = {
    "metallic_reference_sources": "Provide mature and emerging metallic material-system candidates.",
    "ceramic_reference_sources": "Provide monolithic ceramic material-system candidates.",
    "cmc_reference_sources": "Provide ceramic matrix composite material-system candidates.",
    "pmc_reference_sources": "Provide polymer matrix composite material-system candidates.",
    "coating_reference_sources": "Provide coating, bond coat and surface-system components for assembly.",
    "gradient_template_sources": "Provide spatial gradient templates for future graded material-system assembly.",
    "process_route_sources": "Provide process-route context for manufacturing and refinement planning.",
    "criteria_reference_sources": "Provide criterion definitions and evidence context for future valuation.",
    "evidence_maturity_sources": "Provide evidence maturity context for candidate and criterion review.",
    "model_estimate_sources": "Reserve placeholder requests for future model-supported criterion estimates.",
    "measurement_feedback_sources": "Reserve placeholder requests for future measurement and test-result feedback.",
}


class SourceRequest(TypedDict, total=False):
    source_id: str
    label: str
    request_type: str
    status: str
    enabled: bool
    live_retrieval_allowed: bool
    purpose: str
    reason: str
    request_parameters: dict
    required_for: list[str]


class CandidateSourceOrchestrationPlan(TypedDict, total=False):
    schema_version: str
    source_scope_plan_version: str
    source_requests: list[dict]
    enabled_request_count: int
    disabled_request_count: int
    placeholder_request_count: int
    model_placeholder_count: int
    measurement_placeholder_count: int
    research_mode_allowed: bool
    live_retrieval_allowed: bool
    live_model_call_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class SourceOrchestrationValidationResult(TypedDict, total=False):
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


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(value) for value in values]


def _humanise_identifier(identifier: str) -> str:
    text = str(identifier).replace("_", " ").replace("-", " ").strip()
    if not text:
        return "Unknown source"
    return text[:1].upper() + text[1:]


def source_ids_from_scope_plan(scope_plan: dict) -> list[str]:
    source_plan = scope_plan.get("source_plan", [])
    if not isinstance(source_plan, list):
        return []
    source_ids = []
    for record in source_plan:
        if not isinstance(record, dict):
            continue
        if record.get("enabled") is not True:
            continue
        source_id = record.get("source_id")
        if isinstance(source_id, str) and source_id:
            source_ids.append(source_id)
    return unique_preserve_order(source_ids)


def source_request_type(source_id: str) -> str:
    return SOURCE_ID_TO_REQUEST_TYPE.get(source_id, "evidence_reference")


def source_label(source_id: str) -> str:
    return SOURCE_ID_TO_LABEL.get(source_id, _humanise_identifier(source_id))


def source_purpose(source_id: str) -> str:
    return SOURCE_REQUEST_PURPOSES.get(
        source_id, "No controlled purpose has been defined for this source yet."
    )


def source_request(
    source_id: str,
    *,
    enabled: bool = True,
    status: str = "planned",
    reason: str = "",
    request_parameters: dict | None = None,
    required_for: list[str] | None = None,
) -> dict:
    normalised_status = status if status in SOURCE_REQUEST_STATUSES else "planned"
    return {
        "source_id": source_id,
        "label": source_label(source_id),
        "request_type": source_request_type(source_id),
        "status": normalised_status,
        "enabled": bool(enabled),
        "live_retrieval_allowed": False,
        "purpose": source_purpose(source_id),
        "reason": reason,
        "request_parameters": dict(request_parameters or {}),
        "required_for": list(required_for or []),
    }


def _generator_architectures(scope_plan: dict, wanted: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    generators = scope_plan.get("candidate_generators", [])
    if not isinstance(generators, list):
        return []
    for generator in generators:
        if not isinstance(generator, dict) or generator.get("enabled") is not True:
            continue
        architectures = generator.get("architecture_families", [])
        if not isinstance(architectures, list):
            continue
        for architecture in architectures:
            architecture_text = str(architecture)
            if architecture_text in wanted:
                values.append(architecture_text)
    return unique_preserve_order(values)


def _enabled_model_adapter_ids(scope_plan: dict) -> list[str]:
    adapters = scope_plan.get("model_adapter_scope", [])
    if not isinstance(adapters, list):
        return []
    return [
        str(adapter.get("adapter_id"))
        for adapter in adapters
        if isinstance(adapter, dict)
        and adapter.get("enabled") is True
        and adapter.get("adapter_id")
    ]


def request_parameters_for_source(source_id: str, scope_plan: dict) -> dict:
    criteria_scope = scope_plan.get("criteria_valuation_scope", {})
    measurement_scope = scope_plan.get("measurement_feedback_scope", {})
    if not isinstance(criteria_scope, dict):
        criteria_scope = {}
    if not isinstance(measurement_scope, dict):
        measurement_scope = {}

    if source_id == "metallic_reference_sources":
        return {
            "architecture_families": _generator_architectures(
                scope_plan, ("metallic_system", "bulk_material")
            ),
            "active_criteria": _string_list(criteria_scope.get("active_criteria", [])),
        }
    if source_id == "ceramic_reference_sources":
        return {
            "architecture_families": _generator_architectures(
                scope_plan, ("monolithic_ceramic_system",)
            )
        }
    if source_id == "cmc_reference_sources":
        return {
            "architecture_families": _generator_architectures(
                scope_plan, ("cmc_system",)
            )
        }
    if source_id == "pmc_reference_sources":
        return {
            "architecture_families": _generator_architectures(
                scope_plan, ("pmc_system",)
            )
        }
    if source_id == "coating_reference_sources":
        routes = _string_list(scope_plan.get("process_routes_in_scope", []))
        return {
            "coating_options_in_scope": _string_list(
                scope_plan.get("coating_options_in_scope", [])
            ),
            "process_routes_in_scope": [
                route for route in routes if route == "coating_deposition"
            ],
        }
    if source_id == "gradient_template_sources":
        routes = _string_list(scope_plan.get("process_routes_in_scope", []))
        am_routes = {
            "additive_manufacturing",
            "directed_energy_deposition",
            "laser_powder_bed_fusion",
        }
        return {
            "gradient_options_in_scope": _string_list(
                scope_plan.get("gradient_options_in_scope", [])
            ),
            "process_routes_in_scope": [route for route in routes if route in am_routes],
        }
    if source_id == "process_route_sources":
        return {
            "process_routes_in_scope": _string_list(
                scope_plan.get("process_routes_in_scope", [])
            )
        }
    if source_id == "criteria_reference_sources":
        return {
            "active_criteria": _string_list(criteria_scope.get("active_criteria", [])),
            "active_criteria_families": _string_list(
                criteria_scope.get("active_criteria_families", [])
            ),
        }
    if source_id == "evidence_maturity_sources":
        return {
            "active_criteria_families": _string_list(
                criteria_scope.get("active_criteria_families", [])
            ),
            "require_evidence_basis": bool_value(
                criteria_scope, "require_evidence_basis"
            ),
        }
    if source_id == "model_estimate_sources":
        return {
            "enabled_model_adapter_ids": _enabled_model_adapter_ids(scope_plan),
            "require_model_provenance": bool_value(
                criteria_scope, "require_model_provenance"
            ),
            "live_model_call_allowed": False,
        }
    if source_id == "measurement_feedback_sources":
        return {
            "measurement_feedback_scope": dict(measurement_scope),
            "live_retrieval_allowed": False,
        }
    return {}


def required_for_for_source(source_id: str, scope_plan: dict) -> list[str]:
    comparison_required = bool_value(
        scope_plan, "coating_vs_gradient_comparison_required"
    )
    uses_by_source = {
        "metallic_reference_sources": [
            "candidate_generation",
            "baseline_reference_comparison",
        ],
        "ceramic_reference_sources": [
            "candidate_generation",
            "baseline_reference_comparison",
        ],
        "cmc_reference_sources": ["candidate_generation", "system_assembly"],
        "pmc_reference_sources": ["candidate_generation", "system_assembly"],
        "process_route_sources": ["process_context", "manufacturing_review"],
        "criteria_reference_sources": ["criteria_valuation", "trade_off_engine"],
        "evidence_maturity_sources": ["evidence_review", "criteria_valuation"],
        "model_estimate_sources": [
            "future_model_supported_estimates",
            "criteria_valuation",
        ],
        "measurement_feedback_sources": [
            "future_measurement_feedback",
            "model_confidence_update",
        ],
    }
    if source_id == "coating_reference_sources":
        uses = ["component_generation", "system_assembly"]
        if comparison_required:
            uses.append("coating_vs_gradient_comparison")
        return uses
    if source_id == "gradient_template_sources":
        uses = ["gradient_template_generation", "system_assembly"]
        if comparison_required:
            uses.append("coating_vs_gradient_comparison")
        return uses
    return list(uses_by_source.get(source_id, ["evidence_review"]))


def source_requests_from_scope_plan(scope_plan: dict) -> list[dict]:
    requests = []
    for source_id in source_ids_from_scope_plan(scope_plan):
        status = (
            "placeholder_only"
            if source_id in {"model_estimate_sources", "measurement_feedback_sources"}
            else "planned"
        )
        requests.append(
            source_request(
                source_id,
                enabled=True,
                status=status,
                reason="Source request derived from enabled scope-plan source.",
                request_parameters=request_parameters_for_source(source_id, scope_plan),
                required_for=required_for_for_source(source_id, scope_plan),
            )
        )
    return requests


def build_source_orchestration_plan(scope_plan: dict) -> dict:
    validation = validate_scope_plan(scope_plan)
    source_requests = source_requests_from_scope_plan(scope_plan)
    warnings = unique_preserve_order(
        _string_list(scope_plan.get("warnings", []))
        + _string_list(validation.get("warnings", []))
    )
    assumptions = unique_preserve_order(
        _string_list(scope_plan.get("assumptions", []))
        + ["Source orchestration plan derived from MaterialSystemScopePlan."]
    )
    enabled_request_count = len(
        [request for request in source_requests if request.get("enabled") is True]
    )
    disabled_request_count = len(
        [request for request in source_requests if request.get("enabled") is not True]
    )
    placeholder_request_count = len(
        [
            request
            for request in source_requests
            if request.get("status") == "placeholder_only"
        ]
    )
    model_placeholder_count = len(
        [
            request
            for request in source_requests
            if request.get("source_id") == "model_estimate_sources"
            and request.get("status") == "placeholder_only"
        ]
    )
    measurement_placeholder_count = len(
        [
            request
            for request in source_requests
            if request.get("source_id") == "measurement_feedback_sources"
            and request.get("status") == "placeholder_only"
        ]
    )
    return {
        "schema_version": SOURCE_ORCHESTRATION_SCHEMA_VERSION,
        "source_scope_plan_version": str(scope_plan.get("schema_version", "")),
        "source_requests": source_requests,
        "enabled_request_count": enabled_request_count,
        "disabled_request_count": disabled_request_count,
        "placeholder_request_count": placeholder_request_count,
        "model_placeholder_count": model_placeholder_count,
        "measurement_placeholder_count": measurement_placeholder_count,
        "research_mode_allowed": bool_value(scope_plan, "research_mode_allowed"),
        "live_retrieval_allowed": False,
        "live_model_call_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": _string_list(scope_plan.get("hard_constraints", [])),
    }


def validate_source_orchestration_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Source orchestration plan must be a dictionary."],
            "warnings": [],
        }

    if plan.get("schema_version") != SOURCE_ORCHESTRATION_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SOURCE_ORCHESTRATION_SCHEMA_VERSION}."
        )
    if not isinstance(plan.get("source_requests"), list):
        errors.append("source_requests must be a list.")
    if plan.get("live_retrieval_allowed") is not False:
        errors.append("live_retrieval_allowed must be false.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")

    required_request_fields = (
        "source_id",
        "label",
        "request_type",
        "status",
        "enabled",
        "live_retrieval_allowed",
        "purpose",
        "request_parameters",
        "required_for",
    )
    source_requests = plan.get("source_requests", [])
    if isinstance(source_requests, list):
        if not source_requests:
            warnings.append("No source requests exist.")
        for index, request in enumerate(source_requests):
            if not isinstance(request, dict):
                errors.append(f"source_requests[{index}] must be a dictionary.")
                continue
            for field_name in required_request_fields:
                if field_name not in request:
                    errors.append(f"source_requests[{index}].{field_name} is required.")
            if request.get("request_type") not in SOURCE_REQUEST_TYPES:
                errors.append(
                    f"source_requests[{index}].request_type must be controlled."
                )
            if request.get("status") not in SOURCE_REQUEST_STATUSES:
                errors.append(f"source_requests[{index}].status must be controlled.")
            if request.get("live_retrieval_allowed") is not False:
                errors.append(
                    f"source_requests[{index}].live_retrieval_allowed must be false."
                )
            if (
                request.get("source_id") == "model_estimate_sources"
                and plan.get("live_model_call_allowed") is not False
            ):
                warnings.append(
                    "Model estimate placeholders exist, but live model calls are not explicitly disabled."
                )
            if (
                request.get("source_id") == "measurement_feedback_sources"
                and plan.get("live_retrieval_allowed") is not False
            ):
                warnings.append(
                    "Measurement feedback placeholders exist, but live retrieval is not explicitly disabled."
                )

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def source_orchestration_summary(plan: dict) -> dict:
    source_requests = plan.get("source_requests", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "source_request_count": len(source_requests)
        if isinstance(source_requests, list)
        else 0,
        "enabled_request_count": int(plan.get("enabled_request_count", 0)),
        "disabled_request_count": int(plan.get("disabled_request_count", 0)),
        "placeholder_request_count": int(plan.get("placeholder_request_count", 0)),
        "model_placeholder_count": int(plan.get("model_placeholder_count", 0)),
        "measurement_placeholder_count": int(
            plan.get("measurement_placeholder_count", 0)
        ),
        "research_mode_allowed": bool_value(plan, "research_mode_allowed"),
        "live_retrieval_allowed": bool_value(plan, "live_retrieval_allowed"),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "warning_count": len(plan.get("warnings", []))
        if isinstance(plan.get("warnings"), list)
        else 0,
    }


def hot_section_demo_source_orchestration_plan() -> dict:
    return build_source_orchestration_plan(hot_section_demo_scope_plan())
