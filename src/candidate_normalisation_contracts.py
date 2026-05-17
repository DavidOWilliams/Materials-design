from __future__ import annotations

import re
from typing import Any, TypedDict

from src.candidate_generator_requests import (
    hot_section_demo_generator_request_plan,
    validate_generator_request_plan,
)


NORMALISED_CANDIDATE_SCHEMA_VERSION = "normalised_material_system_candidate_v1"
CANDIDATE_NORMALISATION_PLAN_SCHEMA_VERSION = "candidate_normalisation_plan_v1"

CANDIDATE_RECORD_STATUSES: tuple[str, ...] = (
    "normalised",
    "placeholder_only",
    "invalid_input",
    "contract_template",
)

ARCHITECTURE_TYPES: tuple[str, ...] = (
    "bulk_material",
    "metallic_system",
    "monolithic_ceramic_system",
    "cmc_system",
    "pmc_system",
    "substrate_plus_coating_system",
    "coating_enabled_system",
    "hybrid_system",
    "spatially_graded_am_system",
    "research_generated_system",
    "unknown",
)

EVIDENCE_MATURITY_LEVELS: tuple[str, ...] = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "unknown",
)

SOURCE_PROVENANCE_TYPES: tuple[str, ...] = (
    "reference_source",
    "component_source",
    "template_source",
    "generated_source",
    "model_estimate_placeholder",
    "measurement_feedback_placeholder",
    "unknown",
)

GENERATOR_REQUEST_TO_ARCHITECTURE_TYPE: dict[str, str] = {
    "metallic_reference_generation": "metallic_system",
    "ceramic_reference_generation": "monolithic_ceramic_system",
    "cmc_reference_generation": "cmc_system",
    "pmc_reference_generation": "pmc_system",
    "coating_component_generation": "coating_enabled_system",
    "gradient_template_generation": "spatially_graded_am_system",
    "hybrid_reference_generation": "hybrid_system",
    "bulk_material_assembly": "bulk_material",
    "substrate_plus_coating_assembly": "substrate_plus_coating_system",
    "cmc_ebc_system_assembly": "cmc_system",
    "pmc_system_assembly": "pmc_system",
    "hybrid_system_assembly": "hybrid_system",
    "spatially_graded_am_system_assembly": "spatially_graded_am_system",
    "research_generated_system_wrapping": "research_generated_system",
    "criteria_evidence_preparation": "unknown",
    "model_estimate_preparation": "unknown",
    "measurement_feedback_preparation": "unknown",
}

REQUIRED_TOP_LEVEL_CANDIDATE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "candidate_id",
    "system_name",
    "architecture_type",
    "material_family",
    "generator_request_id",
    "source_request_ids",
    "record_status",
    "substrate_or_bulk_material",
    "coating_or_surface_system",
    "gradient_architecture",
    "process_routes",
    "evidence_maturity",
    "source_provenance",
    "criteria_values",
    "model_provenance_placeholders",
    "measurement_feedback_links",
    "assumptions",
    "warnings",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)


class SourceProvenanceRecord(TypedDict, total=False):
    source_id: str
    provenance_type: str
    label: str
    request_id: str


class EvidenceMaturityRecord(TypedDict, total=False):
    level: str
    label: str
    basis: str
    confidence: str


class ProcessRouteRecord(TypedDict, total=False):
    route_id: str
    label: str
    role: str
    assumptions: list[str]


class CriterionValuePlaceholder(TypedDict, total=False):
    criterion_id: str
    estimated_value: str
    unit: str
    confidence: str
    evidence_basis: list[str]
    uncertainty_drivers: list[str]
    model_used: str
    recommended_next_evidence: list[str]


class ModelProvenancePlaceholder(TypedDict, total=False):
    model_estimate_id: str
    model_type: str
    model_name: str
    live_call_allowed: bool
    provenance_required: bool


class MeasurementFeedbackLinkPlaceholder(TypedDict, total=False):
    measurement_target_id: str
    measurement_record_id: str
    feedback_status: str
    provenance_required: bool


class NormalisedMaterialSystemCandidate(TypedDict, total=False):
    schema_version: str
    candidate_id: str
    system_name: str
    architecture_type: str
    material_family: str
    generator_request_id: str
    source_request_ids: list[str]
    record_status: str
    substrate_or_bulk_material: dict
    coating_or_surface_system: dict | None
    gradient_architecture: dict | None
    process_routes: list[dict]
    evidence_maturity: dict
    source_provenance: list[dict]
    criteria_values: list[dict]
    model_provenance_placeholders: list[dict]
    measurement_feedback_links: list[dict]
    assumptions: list[str]
    warnings: list[str]


class NormalisationRequirement(TypedDict, total=False):
    request_id: str
    label: str
    architecture_type: str
    required_candidate_fields: list[str]
    record_status: str
    source_ids: list[str]
    research_only: bool
    placeholder_only: bool
    reason: str


class CandidateNormalisationPlan(TypedDict, total=False):
    schema_version: str
    source_generator_request_schema_version: str
    expected_candidate_schema_version: str
    normalisation_requirements: list[dict]
    active_criteria: list[str]
    criterion_value_placeholders_required: bool
    model_provenance_required: bool
    measurement_feedback_links_required: bool
    live_source_retrieval_allowed: bool
    live_model_call_allowed: bool
    research_mode_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class CandidateNormalisationValidationResult(TypedDict, total=False):
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
    if value is None:
        return "Not specified"
    text = str(value).replace("_", " ").replace("-", " ").strip()
    if not text:
        return "Not specified"
    return text[:1].upper() + text[1:]


def slugify_identifier(value: object) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", str(value).lower()).strip("_")
    return text or "unknown"


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def normalise_string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return unique_preserve_order([str(value) for value in values])


def architecture_type_for_request_id(request_id: str) -> str:
    return GENERATOR_REQUEST_TO_ARCHITECTURE_TYPE.get(request_id, "unknown")


def evidence_maturity_record(
    level: str = "unknown",
    *,
    label: str = "",
    basis: str = "",
    confidence: str = "unknown",
) -> dict:
    normalised_level = level if level in EVIDENCE_MATURITY_LEVELS else "unknown"
    return {
        "level": normalised_level,
        "label": label or humanise_identifier(normalised_level),
        "basis": basis,
        "confidence": confidence,
    }


def source_provenance_record(
    source_id: str,
    *,
    provenance_type: str = "unknown",
    label: str = "",
    request_id: str = "",
) -> dict:
    normalised_type = (
        provenance_type if provenance_type in SOURCE_PROVENANCE_TYPES else "unknown"
    )
    return {
        "source_id": source_id,
        "provenance_type": normalised_type,
        "label": label or humanise_identifier(source_id),
        "request_id": request_id,
    }


def criterion_value_placeholders(active_criteria: list[str]) -> list[dict]:
    return [
        {
            "criterion_id": str(criterion_id),
            "estimated_value": "pending",
            "unit": "not_specified",
            "confidence": "not_assessed",
            "evidence_basis": [],
            "uncertainty_drivers": [],
            "model_used": "",
            "recommended_next_evidence": [],
        }
        for criterion_id in active_criteria
    ]


def _request_ids(plan: dict) -> list[str]:
    requests = plan.get("generator_requests", [])
    if not isinstance(requests, list):
        return []
    return [
        str(request.get("request_id"))
        for request in requests
        if isinstance(request, dict) and request.get("request_id")
    ]


def model_provenance_placeholders_from_generator_plan(plan: dict) -> list[dict]:
    if "model_estimate_preparation" not in _request_ids(plan):
        return []
    return [
        {
            "model_estimate_id": "pending_model_estimate",
            "model_type": "placeholder",
            "model_name": "Model-estimate preparation",
            "live_call_allowed": False,
            "provenance_required": True,
        }
    ]


def measurement_feedback_links_from_generator_plan(plan: dict) -> list[dict]:
    if "measurement_feedback_preparation" not in _request_ids(plan):
        return []
    return [
        {
            "measurement_target_id": "pending_measurement_target",
            "measurement_record_id": "",
            "feedback_status": "not_available",
            "provenance_required": True,
        }
    ]


def required_candidate_fields_for_architecture(architecture_type: str) -> list[str]:
    fields = list(REQUIRED_TOP_LEVEL_CANDIDATE_FIELDS)
    if architecture_type in {
        "coating_enabled_system",
        "substrate_plus_coating_system",
        "cmc_system",
    }:
        fields.append("coating_or_surface_system")
    if architecture_type == "spatially_graded_am_system":
        fields.append("gradient_architecture")
    if architecture_type in {"cmc_system", "research_generated_system"}:
        fields.append("substrate_or_bulk_material")
    if architecture_type == "research_generated_system":
        fields.append("model_provenance_placeholders")
    return unique_preserve_order(fields)


def normalisation_requirement_for_request(request: dict) -> dict:
    request_id = str(request.get("request_id", ""))
    architecture_type = architecture_type_for_request_id(request_id)
    placeholder_only = request.get("status") == "placeholder_only"
    return {
        "request_id": request_id,
        "label": str(request.get("label", humanise_identifier(request_id))),
        "architecture_type": architecture_type,
        "required_candidate_fields": required_candidate_fields_for_architecture(
            architecture_type
        ),
        "record_status": "placeholder_only" if placeholder_only else "contract_template",
        "source_ids": normalise_string_list(request.get("source_ids", [])),
        "research_only": bool_value(request, "research_only"),
        "placeholder_only": placeholder_only,
        "reason": str(request.get("reason", "")),
    }


def normalisation_requirements_from_generator_plan(plan: dict) -> list[dict]:
    requests = plan.get("generator_requests", [])
    if not isinstance(requests, list):
        return []
    requirements = []
    for request in requests:
        if not isinstance(request, dict) or request.get("enabled") is not True:
            continue
        requirements.append(normalisation_requirement_for_request(request))
    return requirements


def _criteria_from_parameters(parameters: object) -> list[str]:
    if not isinstance(parameters, dict):
        return []
    criteria = []
    criteria.extend(normalise_string_list(parameters.get("active_criteria", [])))
    nested = parameters.get("request_parameters", {})
    if isinstance(nested, dict):
        criteria.extend(normalise_string_list(nested.get("active_criteria", [])))
    sources = parameters.get("source_parameters_by_id", {})
    if isinstance(sources, dict):
        for source_parameters in sources.values():
            if isinstance(source_parameters, dict):
                criteria.extend(
                    normalise_string_list(source_parameters.get("active_criteria", []))
                )
    return criteria


def active_criteria_from_generator_plan(plan: dict) -> list[str]:
    requests = plan.get("generator_requests", [])
    if not isinstance(requests, list):
        return []
    criteria = []
    for request in requests:
        if isinstance(request, dict):
            criteria.extend(_criteria_from_parameters(request.get("request_parameters", {})))
    return unique_preserve_order(criteria)


def normalised_candidate_template(
    request_id: str,
    *,
    candidate_id: str = "",
    system_name: str = "",
    architecture_type: str = "",
    material_family: str = "",
    active_criteria: list[str] | None = None,
    source_request_ids: list[str] | None = None,
) -> dict:
    resolved_name = system_name or humanise_identifier(request_id)
    resolved_id = candidate_id or slugify_identifier(resolved_name or request_id)
    return {
        "schema_version": NORMALISED_CANDIDATE_SCHEMA_VERSION,
        "candidate_id": resolved_id,
        "system_name": resolved_name,
        "architecture_type": architecture_type or architecture_type_for_request_id(request_id),
        "material_family": material_family or "unknown",
        "generator_request_id": request_id,
        "source_request_ids": list(source_request_ids or []),
        "record_status": "contract_template",
        "substrate_or_bulk_material": {},
        "coating_or_surface_system": None,
        "gradient_architecture": None,
        "process_routes": [],
        "evidence_maturity": evidence_maturity_record(),
        "source_provenance": [],
        "criteria_values": criterion_value_placeholders(active_criteria or []),
        "model_provenance_placeholders": [],
        "measurement_feedback_links": [],
        "assumptions": ["Candidate record is a normalisation contract template."],
        "warnings": [],
    }


def _copy_dict(value: object) -> dict:
    return dict(value) if isinstance(value, dict) else {}


def normalise_candidate_record(
    raw_candidate: dict,
    *,
    generator_request: dict | None = None,
    active_criteria: list[str] | None = None,
    source_request_ids: list[str] | None = None,
) -> dict:
    raw = dict(raw_candidate) if isinstance(raw_candidate, dict) else {}
    request = dict(generator_request) if isinstance(generator_request, dict) else {}
    request_id = str(request.get("request_id", ""))
    system_name = str(
        raw.get("system_name") or raw.get("name") or raw.get("candidate_id") or raw.get("id") or ""
    )
    candidate_id = str(
        raw.get("candidate_id") or raw.get("id") or slugify_identifier(system_name)
    )
    architecture_type = str(
        raw.get("architecture_type") or architecture_type_for_request_id(request_id)
    )
    material_family = str(raw.get("material_family") or raw.get("family") or "unknown")
    resolved_source_ids = (
        normalise_string_list(source_request_ids)
        if source_request_ids is not None
        else normalise_string_list(request.get("source_ids", []))
    )
    evidence_value = raw.get("evidence_maturity")
    source_provenance = raw.get("source_provenance")
    criteria_values = raw.get("criteria_values")
    warnings = normalise_string_list(raw.get("warnings", []))

    if architecture_type == "unknown":
        warnings.append("Architecture type is unknown.")
    if not candidate_id or candidate_id == "unknown":
        warnings.append("Candidate identifier is unknown or empty.")

    return {
        "schema_version": NORMALISED_CANDIDATE_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "system_name": system_name or candidate_id,
        "architecture_type": architecture_type,
        "material_family": material_family,
        "generator_request_id": request_id,
        "source_request_ids": resolved_source_ids,
        "record_status": "normalised",
        "substrate_or_bulk_material": _copy_dict(
            raw.get("substrate_or_bulk_material") or raw.get("material")
        ),
        "coating_or_surface_system": (
            dict(raw.get("coating_or_surface_system"))
            if isinstance(raw.get("coating_or_surface_system"), dict)
            else dict(raw.get("coating"))
            if isinstance(raw.get("coating"), dict)
            else None
        ),
        "gradient_architecture": (
            dict(raw.get("gradient_architecture"))
            if isinstance(raw.get("gradient_architecture"), dict)
            else None
        ),
        "process_routes": list(raw.get("process_routes", []))
        if isinstance(raw.get("process_routes"), list)
        else [],
        "evidence_maturity": (
            dict(evidence_value)
            if isinstance(evidence_value, dict)
            else evidence_maturity_record(str(raw.get("evidence_level", "unknown")))
        ),
        "source_provenance": (
            [dict(record) for record in source_provenance if isinstance(record, dict)]
            if isinstance(source_provenance, list)
            else [
                source_provenance_record(source_id, request_id=request_id)
                for source_id in resolved_source_ids
            ]
        ),
        "criteria_values": (
            [dict(record) for record in criteria_values if isinstance(record, dict)]
            if isinstance(criteria_values, list)
            else criterion_value_placeholders(active_criteria or [])
        ),
        "model_provenance_placeholders": (
            [
                dict(record)
                for record in raw.get("model_provenance_placeholders", [])
                if isinstance(record, dict)
            ]
            if isinstance(raw.get("model_provenance_placeholders"), list)
            else []
        ),
        "measurement_feedback_links": (
            [
                dict(record)
                for record in raw.get("measurement_feedback_links", [])
                if isinstance(record, dict)
            ]
            if isinstance(raw.get("measurement_feedback_links"), list)
            else []
        ),
        "assumptions": normalise_string_list(raw.get("assumptions", [])),
        "warnings": unique_preserve_order(warnings),
    }


def build_candidate_normalisation_plan(generator_request_plan: dict) -> dict:
    validation = validate_generator_request_plan(generator_request_plan)
    requirements = normalisation_requirements_from_generator_plan(generator_request_plan)
    active_criteria = active_criteria_from_generator_plan(generator_request_plan)
    request_ids = _request_ids(generator_request_plan)
    assumptions = unique_preserve_order(
        normalise_string_list(generator_request_plan.get("assumptions", []))
        + ["Candidate normalisation plan derived from CandidateGeneratorRequestPlan."]
    )
    warnings = unique_preserve_order(
        normalise_string_list(generator_request_plan.get("warnings", []))
        + normalise_string_list(validation.get("warnings", []))
    )
    return {
        "schema_version": CANDIDATE_NORMALISATION_PLAN_SCHEMA_VERSION,
        "source_generator_request_schema_version": str(
            generator_request_plan.get("schema_version", "")
        ),
        "expected_candidate_schema_version": NORMALISED_CANDIDATE_SCHEMA_VERSION,
        "normalisation_requirements": requirements,
        "active_criteria": active_criteria,
        "criterion_value_placeholders_required": bool(active_criteria),
        "model_provenance_required": "model_estimate_preparation" in request_ids,
        "measurement_feedback_links_required": "measurement_feedback_preparation"
        in request_ids,
        "live_source_retrieval_allowed": False,
        "live_model_call_allowed": False,
        "research_mode_allowed": bool_value(generator_request_plan, "research_mode_allowed"),
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": normalise_string_list(
            generator_request_plan.get("hard_constraints", [])
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


def validate_normalised_candidate(candidate: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(candidate, dict):
        return {
            "is_valid": False,
            "errors": ["Candidate must be a dictionary."],
            "warnings": [],
        }

    if candidate.get("schema_version") != NORMALISED_CANDIDATE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {NORMALISED_CANDIDATE_SCHEMA_VERSION}.")
    for field_name in REQUIRED_TOP_LEVEL_CANDIDATE_FIELDS:
        if field_name not in candidate:
            errors.append(f"{field_name} is required.")
    if not isinstance(candidate.get("candidate_id"), str) or not candidate.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if not isinstance(candidate.get("system_name"), str) or not candidate.get("system_name"):
        errors.append("system_name must be a non-empty string.")
    if candidate.get("architecture_type") not in ARCHITECTURE_TYPES:
        errors.append("architecture_type must be controlled.")
    if candidate.get("record_status") not in CANDIDATE_RECORD_STATUSES:
        errors.append("record_status must be controlled.")
    for field_name in (
        "source_request_ids",
        "process_routes",
        "criteria_values",
        "model_provenance_placeholders",
        "measurement_feedback_links",
    ):
        if not isinstance(candidate.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    if not isinstance(candidate.get("evidence_maturity"), dict):
        errors.append("evidence_maturity must be a dictionary.")

    if candidate.get("architecture_type") == "unknown":
        warnings.append("Architecture type is unknown.")
    evidence_maturity = candidate.get("evidence_maturity", {})
    if isinstance(evidence_maturity, dict) and evidence_maturity.get("level") == "unknown":
        warnings.append("Evidence maturity level is unknown.")

    forbidden_hits = _find_forbidden_claim_fields(candidate)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_candidate_normalisation_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Candidate normalisation plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != CANDIDATE_NORMALISATION_PLAN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CANDIDATE_NORMALISATION_PLAN_SCHEMA_VERSION}.")
    if plan.get("expected_candidate_schema_version") != NORMALISED_CANDIDATE_SCHEMA_VERSION:
        errors.append(f"expected_candidate_schema_version must be {NORMALISED_CANDIDATE_SCHEMA_VERSION}.")
    if not isinstance(plan.get("normalisation_requirements"), list):
        errors.append("normalisation_requirements must be a list.")
    if not isinstance(plan.get("active_criteria"), list):
        errors.append("active_criteria must be a list.")
    for field_name in (
        "criterion_value_placeholders_required",
        "model_provenance_required",
        "measurement_feedback_links_required",
    ):
        if not isinstance(plan.get(field_name), bool):
            errors.append(f"{field_name} must be a boolean.")
    if plan.get("live_source_retrieval_allowed") is not False:
        errors.append("live_source_retrieval_allowed must be false.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")

    requirements = plan.get("normalisation_requirements", [])
    allowed_unknown_request_ids = {
        "criteria_evidence_preparation",
        "model_estimate_preparation",
        "measurement_feedback_preparation",
    }
    if isinstance(requirements, list):
        if not requirements:
            warnings.append("No normalisation requirements exist.")
        for index, requirement in enumerate(requirements):
            if not isinstance(requirement, dict):
                errors.append(f"normalisation_requirements[{index}] must be a dictionary.")
                continue
            if (
                requirement.get("architecture_type") == "unknown"
                and requirement.get("request_id") not in allowed_unknown_request_ids
            ):
                errors.append(
                    f"normalisation_requirements[{index}].architecture_type must be known for material-system candidate requests."
                )

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def candidate_normalisation_summary(plan: dict) -> dict:
    warnings = plan.get("warnings", [])
    requirements = plan.get("normalisation_requirements", [])
    active_criteria = plan.get("active_criteria", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "normalisation_requirement_count": len(requirements)
        if isinstance(requirements, list)
        else 0,
        "active_criteria_count": len(active_criteria)
        if isinstance(active_criteria, list)
        else 0,
        "criterion_value_placeholders_required": bool_value(
            plan, "criterion_value_placeholders_required"
        ),
        "model_provenance_required": bool_value(plan, "model_provenance_required"),
        "measurement_feedback_links_required": bool_value(
            plan, "measurement_feedback_links_required"
        ),
        "live_source_retrieval_allowed": bool_value(
            plan, "live_source_retrieval_allowed"
        ),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "research_mode_allowed": bool_value(plan, "research_mode_allowed"),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_candidate_normalisation_plan() -> dict:
    return build_candidate_normalisation_plan(hot_section_demo_generator_request_plan())
