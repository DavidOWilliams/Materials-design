from __future__ import annotations

from typing import Any, TypedDict

from src.candidate_normalisation_contracts import (
    hot_section_demo_candidate_normalisation_plan,
    validate_candidate_normalisation_plan,
)


CRITERIA_REGISTRY_SCHEMA_VERSION = "criteria_registry_v1"
CRITERION_VALUE_SCHEMA_VERSION = "criterion_value_v1"
CRITERIA_VALUATION_PLAN_SCHEMA_VERSION = "criteria_valuation_plan_v1"

CRITERION_FAMILIES: tuple[str, ...] = (
    "functional_performance",
    "failure_mode_resilience",
    "system_compatibility",
    "manufacturability",
    "inspection_repair",
    "through_life_cost",
    "sustainability",
    "supply_risk",
    "evidence_maturity",
    "qualification_risk",
    "gradient_specific_feasibility",
    "model_confidence",
    "measurement_feedback_readiness",
)

VALUE_TYPES: tuple[str, ...] = (
    "qualitative_band",
    "numeric_estimate",
    "numeric_range",
    "ordinal_score",
    "text_assessment",
    "pending",
)

CONFIDENCE_LEVELS: tuple[str, ...] = (
    "high",
    "medium",
    "low",
    "not_assessed",
    "unknown",
)

EVIDENCE_SOURCE_TYPES: tuple[str, ...] = (
    "reference_data",
    "engineering_rule",
    "deterministic_estimator",
    "computational_model",
    "surrogate_model",
    "specialist_ai_model",
    "literature_extractor",
    "measurement_feedback",
    "expert_assumption",
    "placeholder",
    "unknown",
)

UNCERTAINTY_LEVELS: tuple[str, ...] = (
    "low",
    "medium",
    "high",
    "not_assessed",
    "unknown",
)

CRITERION_IDS: tuple[str, ...] = (
    "temperature_capability",
    "oxidation_resistance",
    "corrosion_resistance",
    "thermal_cycling_resilience",
    "coating_spallation_risk",
    "gradient_transition_risk",
    "creep_resistance",
    "fatigue_resistance",
    "fracture_toughness",
    "thermal_shock_resistance",
    "density_weight",
    "manufacturability",
    "process_window_sensitivity",
    "inspection_burden",
    "repairability",
    "lifecycle_cost",
    "acquisition_cost",
    "manufacturing_cost",
    "inspection_cost",
    "repair_cost",
    "qualification_cost",
    "embodied_carbon",
    "critical_material_exposure",
    "recyclability",
    "process_energy_burden",
    "supply_risk",
    "evidence_maturity",
    "qualification_risk",
    "model_confidence",
    "measurement_feedback_readiness",
)

CRITERION_ID_TO_FAMILY: dict[str, str] = {
    "temperature_capability": "functional_performance",
    "oxidation_resistance": "functional_performance",
    "corrosion_resistance": "functional_performance",
    "thermal_cycling_resilience": "failure_mode_resilience",
    "coating_spallation_risk": "failure_mode_resilience",
    "gradient_transition_risk": "gradient_specific_feasibility",
    "creep_resistance": "failure_mode_resilience",
    "fatigue_resistance": "failure_mode_resilience",
    "fracture_toughness": "failure_mode_resilience",
    "thermal_shock_resistance": "failure_mode_resilience",
    "density_weight": "system_compatibility",
    "manufacturability": "manufacturability",
    "process_window_sensitivity": "manufacturability",
    "inspection_burden": "inspection_repair",
    "repairability": "inspection_repair",
    "lifecycle_cost": "through_life_cost",
    "acquisition_cost": "through_life_cost",
    "manufacturing_cost": "through_life_cost",
    "inspection_cost": "through_life_cost",
    "repair_cost": "through_life_cost",
    "qualification_cost": "through_life_cost",
    "embodied_carbon": "sustainability",
    "critical_material_exposure": "sustainability",
    "recyclability": "sustainability",
    "process_energy_burden": "sustainability",
    "supply_risk": "supply_risk",
    "evidence_maturity": "evidence_maturity",
    "qualification_risk": "qualification_risk",
    "model_confidence": "model_confidence",
    "measurement_feedback_readiness": "measurement_feedback_readiness",
}

CRITERION_ID_TO_LABEL: dict[str, str] = {
    "temperature_capability": "Temperature capability",
    "oxidation_resistance": "Oxidation resistance",
    "corrosion_resistance": "Corrosion resistance",
    "thermal_cycling_resilience": "Thermal cycling resilience",
    "coating_spallation_risk": "Coating spallation risk",
    "gradient_transition_risk": "Gradient transition risk",
    "creep_resistance": "Creep resistance",
    "fatigue_resistance": "Fatigue resistance",
    "fracture_toughness": "Fracture toughness",
    "thermal_shock_resistance": "Thermal shock resistance",
    "density_weight": "Density and weight",
    "manufacturability": "Manufacturability",
    "process_window_sensitivity": "Process-window sensitivity",
    "inspection_burden": "Inspection burden",
    "repairability": "Repairability",
    "lifecycle_cost": "Lifecycle cost",
    "acquisition_cost": "Acquisition cost",
    "manufacturing_cost": "Manufacturing cost",
    "inspection_cost": "Inspection cost",
    "repair_cost": "Repair cost",
    "qualification_cost": "Qualification cost",
    "embodied_carbon": "Embodied carbon",
    "critical_material_exposure": "Critical material exposure",
    "recyclability": "Recyclability",
    "process_energy_burden": "Process energy burden",
    "supply_risk": "Supply risk",
    "evidence_maturity": "Evidence maturity",
    "qualification_risk": "Qualification risk",
    "model_confidence": "Model confidence",
    "measurement_feedback_readiness": "Measurement feedback readiness",
}

CRITERION_ID_TO_DESCRIPTION: dict[str, str] = {
    "temperature_capability": "Ability to operate at the required thermal exposure.",
    "oxidation_resistance": "Resistance to oxidation under the intended environment.",
    "corrosion_resistance": "Resistance to corrosion mechanisms relevant to the service environment.",
    "thermal_cycling_resilience": "Ability to tolerate repeated heating and cooling cycles.",
    "coating_spallation_risk": "Risk of coating loss or delamination during operation.",
    "gradient_transition_risk": "Risk introduced by spatial property or composition transitions.",
    "creep_resistance": "Resistance to time-dependent deformation at elevated temperature.",
    "fatigue_resistance": "Resistance to cyclic mechanical damage.",
    "fracture_toughness": "Resistance to crack initiation and propagation.",
    "thermal_shock_resistance": "Resistance to rapid temperature-change damage.",
    "density_weight": "Mass contribution and density suitability for the application.",
    "manufacturability": "Practicality of producing the material system repeatably.",
    "process_window_sensitivity": "Sensitivity to manufacturing process-window variation.",
    "inspection_burden": "Inspection effort expected through manufacturing and service.",
    "repairability": "Ability to inspect, repair, restore or extend service life.",
    "lifecycle_cost": "Expected cost burden across manufacture, use, repair and replacement.",
    "acquisition_cost": "Initial procurement or material acquisition cost burden.",
    "manufacturing_cost": "Cost burden associated with production and processing.",
    "inspection_cost": "Cost burden associated with inspection and non-destructive testing.",
    "repair_cost": "Cost burden associated with repair or restoration.",
    "qualification_cost": "Evidence and review cost burden before engineering use.",
    "embodied_carbon": "Carbon burden associated with material and processing choices.",
    "critical_material_exposure": "Exposure to scarce, strategic or supply-sensitive materials.",
    "recyclability": "Potential for recycling or responsible end-of-life handling.",
    "process_energy_burden": "Energy burden associated with manufacturing routes.",
    "supply_risk": "Risk that sourcing or availability constrains use.",
    "evidence_maturity": "Maturity and traceability of the available evidence base.",
    "qualification_risk": "Risk that evidence gaps slow or prevent acceptance for intended use.",
    "model_confidence": "Confidence in any model-supported estimate used for valuation.",
    "measurement_feedback_readiness": "Readiness to absorb future measurement and test feedback.",
}

DEFAULT_HOT_SECTION_CRITERIA: tuple[str, ...] = (
    "temperature_capability",
    "oxidation_resistance",
    "thermal_cycling_resilience",
    "coating_spallation_risk",
    "gradient_transition_risk",
    "manufacturability",
    "inspection_burden",
    "repairability",
    "lifecycle_cost",
    "embodied_carbon",
    "critical_material_exposure",
    "qualification_risk",
    "model_confidence",
)

_HIGHER_IS_BETTER: set[str] = {
    "temperature_capability",
    "oxidation_resistance",
    "corrosion_resistance",
    "thermal_cycling_resilience",
    "creep_resistance",
    "fatigue_resistance",
    "fracture_toughness",
    "thermal_shock_resistance",
    "repairability",
    "recyclability",
    "manufacturability",
}

_LOWER_IS_BETTER: set[str] = {
    "coating_spallation_risk",
    "gradient_transition_risk",
    "lifecycle_cost",
    "acquisition_cost",
    "manufacturing_cost",
    "inspection_cost",
    "repair_cost",
    "qualification_cost",
    "embodied_carbon",
    "critical_material_exposure",
    "qualification_risk",
    "inspection_burden",
    "process_energy_burden",
    "supply_risk",
    "process_window_sensitivity",
    "density_weight",
}

_NUMERIC_CRITERIA_MARKERS: tuple[str, ...] = (
    "cost",
    "carbon",
    "density",
    "weight",
    "temperature",
)

_FORBIDDEN_CLAIM_FIELDS: tuple[str, ...] = (
    "certification_approval",
    "qualification_approval",
    "approved",
    "certified",
)


class CriterionDefinition(TypedDict, total=False):
    criterion_id: str
    label: str
    family: str
    description: str
    value_types: list[str]
    higher_is_better: bool | None
    requires_uncertainty: bool
    requires_evidence_basis: bool


class EvidenceBasisRecord(TypedDict, total=False):
    source_type: str
    source_id: str
    description: str
    confidence: str


class UncertaintyRecord(TypedDict, total=False):
    driver_id: str
    description: str
    uncertainty_level: str
    reducible_by_evidence: bool


class ModelProvenanceRecord(TypedDict, total=False):
    model_id: str
    model_type: str
    model_name: str
    live_call_allowed: bool
    provenance_status: str


class RecommendedEvidenceAction(TypedDict, total=False):
    action_id: str
    label: str
    purpose: str
    priority: str


class CriterionValue(TypedDict, total=False):
    schema_version: str
    candidate_id: str
    criterion_id: str
    criterion_label: str
    criterion_family: str
    value_type: str
    estimated_value: Any
    unit: str
    confidence: str
    uncertainty_level: str
    evidence_basis: list[dict]
    uncertainty_drivers: list[dict]
    model_provenance: list[dict]
    assumptions: list[str]
    warnings: list[str]
    recommended_next_evidence: list[dict]
    valuation_status: str


class CriteriaValuationPlan(TypedDict, total=False):
    schema_version: str
    source_candidate_normalisation_plan_version: str
    criteria_registry_schema_version: str
    active_criteria: list[str]
    criterion_definitions: list[dict]
    criterion_value_placeholders: list[dict]
    require_confidence: bool
    require_uncertainty: bool
    require_evidence_basis: bool
    require_model_provenance: bool
    require_measurement_provenance: bool
    live_model_call_allowed: bool
    assumptions: list[str]
    warnings: list[str]
    hard_constraints: list[str]


class CriteriaValueValidationResult(TypedDict, total=False):
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


def bool_value(mapping: dict, field_name: str) -> bool:
    return isinstance(mapping, dict) and mapping.get(field_name) is True


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return unique_preserve_order([str(value) for value in values])


def criterion_family(criterion_id: str) -> str:
    return CRITERION_ID_TO_FAMILY.get(criterion_id, "evidence_maturity")


def criterion_label(criterion_id: str) -> str:
    return CRITERION_ID_TO_LABEL.get(criterion_id, humanise_identifier(criterion_id))


def criterion_description(criterion_id: str) -> str:
    return CRITERION_ID_TO_DESCRIPTION.get(
        criterion_id, "No controlled description is available yet."
    )


def criterion_definition(criterion_id: str) -> dict:
    value_types = ["qualitative_band", "pending"]
    if any(marker in criterion_id for marker in _NUMERIC_CRITERIA_MARKERS):
        value_types.extend(["numeric_estimate", "numeric_range"])
    higher_is_better: bool | None = None
    if criterion_id in _HIGHER_IS_BETTER:
        higher_is_better = True
    elif criterion_id in _LOWER_IS_BETTER:
        higher_is_better = False
    return {
        "criterion_id": criterion_id,
        "label": criterion_label(criterion_id),
        "family": criterion_family(criterion_id),
        "description": criterion_description(criterion_id),
        "value_types": unique_preserve_order(value_types),
        "higher_is_better": higher_is_better,
        "requires_uncertainty": True,
        "requires_evidence_basis": True,
    }


def criteria_registry(criteria_ids: list[str] | None = None) -> list[dict]:
    selected_criteria = CRITERION_IDS if criteria_ids is None else criteria_ids
    return [
        criterion_definition(criterion_id)
        for criterion_id in unique_preserve_order(list(selected_criteria))
    ]


def evidence_basis_record(
    source_type: str = "placeholder",
    *,
    source_id: str = "",
    description: str = "",
    confidence: str = "not_assessed",
) -> dict:
    return {
        "source_type": source_type if source_type in EVIDENCE_SOURCE_TYPES else "unknown",
        "source_id": source_id,
        "description": description,
        "confidence": confidence if confidence in CONFIDENCE_LEVELS else "unknown",
    }


def uncertainty_record(
    driver_id: str,
    *,
    description: str = "",
    uncertainty_level: str = "not_assessed",
    reducible_by_evidence: bool = True,
) -> dict:
    return {
        "driver_id": driver_id,
        "description": description,
        "uncertainty_level": uncertainty_level
        if uncertainty_level in UNCERTAINTY_LEVELS
        else "unknown",
        "reducible_by_evidence": bool(reducible_by_evidence),
    }


def model_provenance_record(
    model_id: str,
    *,
    model_type: str = "placeholder",
    model_name: str = "",
    live_call_allowed: bool = False,
    provenance_status: str = "required",
) -> dict:
    return {
        "model_id": model_id,
        "model_type": model_type,
        "model_name": model_name,
        "live_call_allowed": False,
        "provenance_status": provenance_status,
    }


def recommended_evidence_action(
    action_id: str,
    *,
    label: str = "",
    purpose: str = "",
    priority: str = "medium",
) -> dict:
    return {
        "action_id": action_id,
        "label": label or humanise_identifier(action_id),
        "purpose": purpose,
        "priority": priority,
    }


def criterion_value_placeholder(
    candidate_id: str,
    criterion_id: str,
    *,
    assumptions: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    return {
        "schema_version": CRITERION_VALUE_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "criterion_id": criterion_id,
        "criterion_label": criterion_label(criterion_id),
        "criterion_family": criterion_family(criterion_id),
        "value_type": "pending",
        "estimated_value": "pending",
        "unit": "not_specified",
        "confidence": "not_assessed",
        "uncertainty_level": "not_assessed",
        "evidence_basis": [
            evidence_basis_record(
                "placeholder",
                description="Criterion value has not yet been estimated.",
                confidence="not_assessed",
            )
        ],
        "uncertainty_drivers": [],
        "model_provenance": [],
        "assumptions": list(assumptions or []),
        "warnings": list(warnings or []),
        "recommended_next_evidence": [],
        "valuation_status": "placeholder_only",
    }


def criterion_values_for_candidate(candidate_id: str, criteria_ids: list[str]) -> list[dict]:
    return [
        criterion_value_placeholder(candidate_id, criterion_id)
        for criterion_id in unique_preserve_order(criteria_ids)
    ]


def active_criteria_from_normalisation_plan(plan: dict) -> list[str]:
    active_criteria = _string_list(plan.get("active_criteria", []))
    return active_criteria or list(DEFAULT_HOT_SECTION_CRITERIA)


def criteria_value_placeholders_from_normalisation_plan(plan: dict) -> list[dict]:
    return criterion_values_for_candidate(
        "candidate_placeholder", active_criteria_from_normalisation_plan(plan)
    )


def build_criteria_valuation_plan(normalisation_plan: dict) -> dict:
    validation = validate_candidate_normalisation_plan(normalisation_plan)
    active_criteria = active_criteria_from_normalisation_plan(normalisation_plan)
    assumptions = unique_preserve_order(
        _string_list(normalisation_plan.get("assumptions", []))
        + ["Criteria valuation plan derived from CandidateNormalisationPlan."]
    )
    warnings = unique_preserve_order(
        _string_list(normalisation_plan.get("warnings", []))
        + _string_list(validation.get("warnings", []))
    )
    return {
        "schema_version": CRITERIA_VALUATION_PLAN_SCHEMA_VERSION,
        "source_candidate_normalisation_plan_version": str(
            normalisation_plan.get("schema_version", "")
        ),
        "criteria_registry_schema_version": CRITERIA_REGISTRY_SCHEMA_VERSION,
        "active_criteria": active_criteria,
        "criterion_definitions": criteria_registry(active_criteria),
        "criterion_value_placeholders": criteria_value_placeholders_from_normalisation_plan(
            normalisation_plan
        ),
        "require_confidence": True,
        "require_uncertainty": bool_value(
            normalisation_plan, "criterion_value_placeholders_required"
        ),
        "require_evidence_basis": True,
        "require_model_provenance": bool_value(
            normalisation_plan, "model_provenance_required"
        ),
        "require_measurement_provenance": bool_value(
            normalisation_plan, "measurement_feedback_links_required"
        ),
        "live_model_call_allowed": False,
        "assumptions": assumptions,
        "warnings": warnings,
        "hard_constraints": _string_list(normalisation_plan.get("hard_constraints", [])),
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


def validate_criterion_value(value: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(value, dict):
        return {
            "is_valid": False,
            "errors": ["CriterionValue must be a dictionary."],
            "warnings": [],
        }
    if value.get("schema_version") != CRITERION_VALUE_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CRITERION_VALUE_SCHEMA_VERSION}.")
    if not isinstance(value.get("candidate_id"), str) or not value.get("candidate_id"):
        errors.append("candidate_id must be a non-empty string.")
    if not isinstance(value.get("criterion_id"), str) or not value.get("criterion_id"):
        errors.append("criterion_id must be a non-empty string.")
    if value.get("criterion_family") not in CRITERION_FAMILIES:
        errors.append("criterion_family must be controlled.")
    if value.get("value_type") not in VALUE_TYPES:
        errors.append("value_type must be controlled.")
    if value.get("confidence") not in CONFIDENCE_LEVELS:
        errors.append("confidence must be controlled.")
    if value.get("uncertainty_level") not in UNCERTAINTY_LEVELS:
        errors.append("uncertainty_level must be controlled.")
    for field_name in (
        "evidence_basis",
        "uncertainty_drivers",
        "model_provenance",
        "recommended_next_evidence",
    ):
        if not isinstance(value.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    model_provenance = value.get("model_provenance", [])
    if isinstance(model_provenance, list):
        for index, record in enumerate(model_provenance):
            if isinstance(record, dict) and record.get("live_call_allowed") is True:
                errors.append(f"model_provenance[{index}].live_call_allowed must be false.")

    forbidden_hits = _find_forbidden_claim_fields(value)
    if forbidden_hits:
        errors.append(
            "Forbidden approval or certification claim fields are present: "
            + ", ".join(forbidden_hits)
        )
    if value.get("value_type") == "pending":
        warnings.append("Criterion value is pending.")
    if value.get("confidence") == "not_assessed":
        warnings.append("Criterion confidence has not been assessed.")

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def validate_criteria_valuation_plan(plan: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(plan, dict):
        return {
            "is_valid": False,
            "errors": ["Criteria valuation plan must be a dictionary."],
            "warnings": [],
        }
    if plan.get("schema_version") != CRITERIA_VALUATION_PLAN_SCHEMA_VERSION:
        errors.append(f"schema_version must be {CRITERIA_VALUATION_PLAN_SCHEMA_VERSION}.")
    if plan.get("criteria_registry_schema_version") != CRITERIA_REGISTRY_SCHEMA_VERSION:
        errors.append(f"criteria_registry_schema_version must be {CRITERIA_REGISTRY_SCHEMA_VERSION}.")
    for field_name in ("active_criteria", "criterion_definitions", "criterion_value_placeholders"):
        if not isinstance(plan.get(field_name), list):
            errors.append(f"{field_name} must be a list.")
    for field_name in (
        "require_confidence",
        "require_uncertainty",
        "require_evidence_basis",
        "require_model_provenance",
        "require_measurement_provenance",
    ):
        if not isinstance(plan.get(field_name), bool):
            errors.append(f"{field_name} must be a boolean.")
    if plan.get("live_model_call_allowed") is not False:
        errors.append("live_model_call_allowed must be false.")

    definitions = plan.get("criterion_definitions", [])
    if isinstance(definitions, list):
        for index, definition in enumerate(definitions):
            if isinstance(definition, dict) and definition.get("family") not in CRITERION_FAMILIES:
                errors.append(f"criterion_definitions[{index}].family must be controlled.")

    placeholders = plan.get("criterion_value_placeholders", [])
    if isinstance(placeholders, list):
        for index, placeholder in enumerate(placeholders):
            result = validate_criterion_value(placeholder)
            if result["errors"]:
                errors.append(
                    f"criterion_value_placeholders[{index}] failed validation: "
                    + "; ".join(result["errors"])
                )

    if plan.get("active_criteria") == []:
        warnings.append("No active criteria are defined.")

    return {"is_valid": not errors, "errors": errors, "warnings": warnings}


def criteria_valuation_summary(plan: dict) -> dict:
    warnings = plan.get("warnings", [])
    return {
        "schema_version": plan.get("schema_version", ""),
        "active_criteria_count": len(plan.get("active_criteria", []))
        if isinstance(plan.get("active_criteria"), list)
        else 0,
        "criterion_definition_count": len(plan.get("criterion_definitions", []))
        if isinstance(plan.get("criterion_definitions"), list)
        else 0,
        "criterion_value_placeholder_count": len(
            plan.get("criterion_value_placeholders", [])
        )
        if isinstance(plan.get("criterion_value_placeholders"), list)
        else 0,
        "require_confidence": bool_value(plan, "require_confidence"),
        "require_uncertainty": bool_value(plan, "require_uncertainty"),
        "require_evidence_basis": bool_value(plan, "require_evidence_basis"),
        "require_model_provenance": bool_value(plan, "require_model_provenance"),
        "require_measurement_provenance": bool_value(
            plan, "require_measurement_provenance"
        ),
        "live_model_call_allowed": bool_value(plan, "live_model_call_allowed"),
        "warning_count": len(warnings) if isinstance(warnings, list) else 0,
    }


def hot_section_demo_criteria_valuation_plan() -> dict:
    return build_criteria_valuation_plan(hot_section_demo_candidate_normalisation_plan())
