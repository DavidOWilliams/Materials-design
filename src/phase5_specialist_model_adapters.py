from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict


ADAPTER_SCHEMA_VERSION = "phase5_disabled_specialist_adapter_contracts_v1"

ADAPTER_STATUSES: tuple[str, ...] = (
    "disabled",
    "gated_research_only",
    "unavailable",
)

ADAPTER_ALLOWED_MODES: tuple[str, ...] = (
    "disabled_only",
    "gated_research_contract_only",
)

TASK_TYPES: tuple[str, ...] = (
    "candidate_generation",
    "property_estimation",
    "literature_evidence_extraction",
    "manufacturability_screening",
    "uncertainty_assessment",
)

RESPONSE_STATUSES: tuple[str, ...] = (
    "not_invoked_disabled",
    "live_call_blocked",
    "research_mode_required",
    "placeholder_response_only",
)

CANDIDATE_STATUSES: tuple[str, ...] = (
    "not_generated",
    "research_generated_only",
    "blocked_from_recommendation",
)

AUDIT_EVENT_TYPES: tuple[str, ...] = (
    "request_recorded",
    "live_call_blocked",
    "placeholder_response_created",
    "generated_candidate_wrapped",
)

SPECIALIST_SAFETY_FLAGS: tuple[str, ...] = (
    "no_live_call",
    "research_only",
    "no_mature_evidence_claim",
    "blocked_from_mature_recommendation",
    "no_final_recommendation",
    "no_qualification_approval",
    "no_certification_approval",
)

DEFAULT_DISABLED_ADAPTER_IDS: tuple[str, ...] = (
    "atomgpt_candidate_generator",
    "mattergen_candidate_generator",
    "property_surrogate_estimator",
    "literature_evidence_extractor",
    "manufacturability_screening_model",
)

DEFAULT_LIMITATIONS: tuple[str, ...] = (
    "Adapter contract only; no live model call is enabled.",
    "Generated outputs, if wrapped, are research-only.",
    "No mature evidence claim is allowed for generated outputs.",
    "Generated outputs are blocked from mature recommendation paths.",
    "No qualification or certification approval is implied.",
)


class SpecialistAdapterCapability(TypedDict, total=False):
    adapter_id: str
    adapter_label: str
    model_family: str
    supported_tasks: list[str]
    adapter_status: str
    allowed_mode: str
    live_calls_enabled: bool
    generated_candidates_allowed: bool
    mature_evidence_allowed: bool
    default_evidence_maturity: str
    limitations: list[str]
    warnings: list[str]


class SpecialistModelRequest(TypedDict, total=False):
    request_id: str
    adapter_id: str
    task_type: str
    prompt_summary: str
    input_constraints: dict[str, Any]
    requested_outputs: list[str]
    research_mode_enabled: bool
    live_call_requested: bool
    caller_notes: list[str]
    safety_flags: list[str]


class SpecialistModelResponse(TypedDict, total=False):
    request_id: str
    adapter_id: str
    response_status: str
    generated_candidates: list[dict[str, Any]]
    evidence_maturity: str
    audit_notes: list[str]
    limitations: list[str]
    warnings: list[str]


class GeneratedCandidateRecord(TypedDict, total=False):
    candidate_id: str
    source_adapter_id: str
    candidate_label: str
    candidate_payload: dict[str, Any]
    evidence_maturity: str
    candidate_status: str
    blocked_from_mature_recommendation: bool
    safety_flags: list[str]
    limitations: list[str]
    warnings: list[str]


class AdapterInvocationAuditRecord(TypedDict, total=False):
    audit_id: str
    request_id: str
    adapter_id: str
    event_type: str
    live_call_attempted: bool
    live_call_blocked: bool
    research_mode_enabled: bool
    notes: list[str]
    warnings: list[str]


class SpecialistAdapterRegistry(TypedDict, total=False):
    schema_version: str
    registry_status: str
    adapters: list[SpecialistAdapterCapability]
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


def normalise_token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def controlled_value(value: Any, allowed: Sequence[str], default: str) -> str:
    token = normalise_token(value)
    return token if token in allowed else default


def default_safety_flags(existing: Sequence[str] | None = None) -> list[str]:
    flags: list[str] = []
    for flag in existing or []:
        if isinstance(flag, str):
            _append_unique(flags, flag)
    for flag in SPECIALIST_SAFETY_FLAGS:
        _append_unique(flags, flag)
    return flags


def build_adapter_capability(
    adapter_id: str,
    *,
    adapter_label: str,
    model_family: str,
    supported_tasks: Sequence[str],
    adapter_status: str = "disabled",
    allowed_mode: str = "disabled_only",
) -> SpecialistAdapterCapability:
    normalised_status = controlled_value(adapter_status, ADAPTER_STATUSES, "disabled")
    normalised_mode = controlled_value(allowed_mode, ADAPTER_ALLOWED_MODES, "disabled_only")
    tasks: list[str] = []
    for task in supported_tasks:
        normalised_task = controlled_value(task, TASK_TYPES, "")
        if normalised_task and normalised_task not in tasks:
            tasks.append(normalised_task)

    warnings = ["Specialist adapter is disabled; live calls are blocked."]
    if normalised_status != "disabled":
        warnings.append("Adapter contract is not enabled for execution in Phase 5.")

    return {
        "adapter_id": normalise_token(adapter_id),
        "adapter_label": _as_string(adapter_label, normalise_token(adapter_id)),
        "model_family": normalise_token(model_family),
        "supported_tasks": tasks,
        "adapter_status": normalised_status,
        "allowed_mode": normalised_mode,
        "live_calls_enabled": False,
        "generated_candidates_allowed": False,
        "mature_evidence_allowed": False,
        "default_evidence_maturity": "F",
        "limitations": list(DEFAULT_LIMITATIONS),
        "warnings": warnings,
    }


def default_disabled_adapter_capabilities() -> list[SpecialistAdapterCapability]:
    return [
        build_adapter_capability(
            "atomgpt_candidate_generator",
            adapter_label="AtomGPT candidate generator",
            model_family="atomgpt_like",
            supported_tasks=("candidate_generation", "property_estimation"),
        ),
        build_adapter_capability(
            "mattergen_candidate_generator",
            adapter_label="MatterGen candidate generator",
            model_family="mattergen_like",
            supported_tasks=("candidate_generation",),
        ),
        build_adapter_capability(
            "property_surrogate_estimator",
            adapter_label="Property surrogate estimator",
            model_family="surrogate_model",
            supported_tasks=("property_estimation", "uncertainty_assessment"),
        ),
        build_adapter_capability(
            "literature_evidence_extractor",
            adapter_label="Literature evidence extractor",
            model_family="literature_model",
            supported_tasks=("literature_evidence_extraction",),
        ),
        build_adapter_capability(
            "manufacturability_screening_model",
            adapter_label="Manufacturability screening model",
            model_family="manufacturability_model",
            supported_tasks=("manufacturability_screening", "uncertainty_assessment"),
        ),
    ]


def build_specialist_adapter_registry(
    adapters: Sequence[Mapping[str, Any]] | None = None,
) -> SpecialistAdapterRegistry:
    unsafe_settings_blocked = False
    if adapters is None:
        capabilities = default_disabled_adapter_capabilities()
    else:
        capabilities = []
        for adapter in adapters:
            if adapter.get("live_calls_enabled") is True:
                unsafe_settings_blocked = True
            capabilities.append(
                build_adapter_capability(
                    _as_string(adapter.get("adapter_id"), "unknown_adapter"),
                    adapter_label=_as_string(adapter.get("adapter_label"), "Unknown adapter"),
                    model_family=_as_string(adapter.get("model_family"), "unknown_model"),
                    supported_tasks=_string_list(adapter.get("supported_tasks")),
                    adapter_status=_as_string(adapter.get("adapter_status"), "disabled"),
                    allowed_mode=_as_string(adapter.get("allowed_mode"), "disabled_only"),
                )
            )

    live_enabled = any(adapter.get("live_calls_enabled") is True for adapter in capabilities)
    warnings = ["All specialist adapters are disabled; no live calls are available."]
    if unsafe_settings_blocked:
        warnings.append("Unsafe supplied adapter settings were blocked.")

    return {
        "schema_version": ADAPTER_SCHEMA_VERSION,
        "registry_status": "unsafe_registry_blocked"
        if unsafe_settings_blocked or live_enabled
        else "disabled_registry",
        "adapters": capabilities,
        "notes": [
            "Specialist adapter contracts are for future integration only.",
            "Generated outputs are research-only and blocked from mature recommendation paths.",
        ],
        "warnings": warnings,
    }


def adapter_lookup(
    registry: Mapping[str, Any],
) -> dict[str, SpecialistAdapterCapability]:
    lookup: dict[str, SpecialistAdapterCapability] = {}
    adapters = registry.get("adapters")
    if not isinstance(adapters, list):
        return lookup
    for adapter in adapters:
        if not isinstance(adapter, Mapping):
            continue
        adapter_id = _as_string(adapter.get("adapter_id"))
        if adapter_id:
            lookup[adapter_id] = dict(adapter)
    return lookup


def build_specialist_model_request(
    *,
    adapter_id: str,
    task_type: str,
    prompt_summary: str = "",
    input_constraints: Mapping[str, Any] | None = None,
    requested_outputs: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
    live_call_requested: bool = False,
    caller_notes: Sequence[str] | None = None,
    request_id: str | None = None,
) -> SpecialistModelRequest:
    normalised_adapter_id = normalise_token(adapter_id)
    controlled_task = controlled_value(task_type, TASK_TYPES, "candidate_generation")
    return {
        "request_id": _as_string(
            request_id,
            f"request:{normalised_adapter_id}:{controlled_task}",
        ),
        "adapter_id": normalised_adapter_id,
        "task_type": controlled_task,
        "prompt_summary": _as_string(prompt_summary),
        "input_constraints": dict(deepcopy(input_constraints or {})),
        "requested_outputs": list(requested_outputs or []),
        "research_mode_enabled": research_mode_enabled,
        "live_call_requested": live_call_requested,
        "caller_notes": list(caller_notes or []),
        "safety_flags": default_safety_flags(),
    }


def live_call_allowed(
    request: Mapping[str, Any],
    capability: Mapping[str, Any] | None = None,
) -> bool:
    return False


def build_blocked_response_for_request(
    request: Mapping[str, Any],
    *,
    capability: Mapping[str, Any] | None = None,
) -> SpecialistModelResponse:
    live_requested = request.get("live_call_requested") is True
    research_mode_enabled = request.get("research_mode_enabled") is True
    if live_requested:
        response_status = "live_call_blocked"
    elif not research_mode_enabled:
        response_status = "research_mode_required"
    else:
        response_status = "not_invoked_disabled"

    warnings = ["Specialist adapter is disabled; no live call was made."]
    if live_requested:
        warnings.append("Live specialist-model call was requested and blocked.")
    if not research_mode_enabled:
        warnings.append("Research mode is required for specialist adapter placeholders.")

    return {
        "request_id": _as_string(request.get("request_id"), "unknown_request"),
        "adapter_id": _as_string(request.get("adapter_id"), "unknown_adapter"),
        "response_status": response_status,
        "generated_candidates": [],
        "evidence_maturity": "F",
        "audit_notes": [
            "No specialist model call was made.",
            "Adapters are disabled in this Phase 5 contract layer.",
        ],
        "limitations": list(DEFAULT_LIMITATIONS),
        "warnings": warnings,
    }


def audit_record_for_request(
    request: Mapping[str, Any],
    response: Mapping[str, Any] | None = None,
) -> AdapterInvocationAuditRecord:
    live_attempted = request.get("live_call_requested") is True
    if live_attempted:
        event_type = "live_call_blocked"
    elif response is not None:
        event_type = "placeholder_response_created"
    else:
        event_type = "request_recorded"
    request_id = _as_string(request.get("request_id"), "unknown_request")
    warnings: list[str] = []
    if live_attempted:
        warnings.append("Live specialist-model call was attempted and blocked.")

    return {
        "audit_id": f"audit:{request_id}",
        "request_id": request_id,
        "adapter_id": _as_string(request.get("adapter_id"), "unknown_adapter"),
        "event_type": event_type,
        "live_call_attempted": live_attempted,
        "live_call_blocked": live_attempted,
        "research_mode_enabled": request.get("research_mode_enabled") is True,
        "notes": [
            "Audit record documents request handling only; it does not prove model execution.",
            "No qualification or certification approval is implied.",
        ],
        "warnings": warnings,
    }


def wrap_research_generated_candidate(
    *,
    source_adapter_id: str,
    candidate_label: str,
    candidate_payload: Mapping[str, Any] | None = None,
    sequence_number: int = 1,
) -> GeneratedCandidateRecord:
    adapter_id = normalise_token(source_adapter_id)
    return {
        "candidate_id": f"research:{adapter_id}:{sequence_number}",
        "source_adapter_id": adapter_id,
        "candidate_label": _as_string(candidate_label, "research candidate"),
        "candidate_payload": dict(deepcopy(candidate_payload or {})),
        "evidence_maturity": "F",
        "candidate_status": "research_generated_only",
        "blocked_from_mature_recommendation": True,
        "safety_flags": default_safety_flags(),
        "limitations": list(DEFAULT_LIMITATIONS),
        "warnings": [
            "Research-generated candidate wrapper only; no model call was made.",
            "Candidate is blocked from mature recommendation paths.",
        ],
    }


def candidate_allowed_for_mature_recommendation(
    candidate: Mapping[str, Any],
) -> bool:
    if candidate.get("candidate_status") == "research_generated_only":
        return False
    if candidate.get("blocked_from_mature_recommendation") is True:
        return False
    evidence_maturity = _as_string(candidate.get("evidence_maturity"), "unknown").upper()
    if evidence_maturity in ("F", "UNKNOWN"):
        return False
    flags = _string_list(candidate.get("safety_flags"))
    if "no_mature_evidence_claim" in flags:
        return False
    if "blocked_from_mature_recommendation" in flags:
        return False
    return False


def adapter_contract_review_summary(
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    adapters = registry.get("adapters")
    adapter_list = [adapter for adapter in adapters if isinstance(adapter, Mapping)] if isinstance(adapters, list) else []
    live_enabled_count = sum(1 for adapter in adapter_list if adapter.get("live_calls_enabled") is True)
    generated_allowed_count = sum(
        1 for adapter in adapter_list if adapter.get("generated_candidates_allowed") is True
    )
    mature_allowed_count = sum(
        1 for adapter in adapter_list if adapter.get("mature_evidence_allowed") is True
    )
    return {
        "adapter_count": len(adapter_list),
        "live_enabled_count": live_enabled_count,
        "generated_candidates_allowed_count": generated_allowed_count,
        "mature_evidence_allowed_count": mature_allowed_count,
        "registry_safe": (
            live_enabled_count == 0
            and generated_allowed_count == 0
            and mature_allowed_count == 0
        ),
        "adapter_ids": [
            _as_string(adapter.get("adapter_id"))
            for adapter in adapter_list
            if _as_string(adapter.get("adapter_id"))
        ],
        "warnings": _string_list(deepcopy(registry.get("warnings"))),
    }


def run_disabled_specialist_adapter_contract_review(
    *,
    request: Mapping[str, Any] | None = None,
    registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    selected_registry = (
        build_specialist_adapter_registry()
        if registry is None
        else build_specialist_adapter_registry(registry.get("adapters", []))
    )
    response: SpecialistModelResponse | None = None
    audit_record: AdapterInvocationAuditRecord | None = None
    if request is not None:
        response = build_blocked_response_for_request(request)
        audit_record = audit_record_for_request(request, response)

    warnings = _string_list(deepcopy(selected_registry.get("warnings")))
    if response is not None:
        for warning in _string_list(response.get("warnings")):
            _append_unique(warnings, warning)

    return {
        "registry": selected_registry,
        "summary": adapter_contract_review_summary(selected_registry),
        "request": dict(deepcopy(request)) if request is not None else None,
        "response": response,
        "audit_record": audit_record,
        "notes": [
            "No live specialist-model calls are enabled.",
            "Generated outputs remain research-only and blocked from mature recommendation paths.",
        ],
        "warnings": warnings,
    }
