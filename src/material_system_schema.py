from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypedDict


SYSTEM_ARCHITECTURE_TYPES: tuple[str, ...] = (
    "bulk_material",
    "coating_enabled",
    "cmc_plus_ebc",
    "spatially_graded_am_system",
    "hybrid_system",
    "research_generated_system",
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

GRADIENT_TYPES: tuple[str, ...] = (
    "composition_gradient",
    "microstructure_gradient",
    "porosity_gradient",
    "reinforcement_gradient",
    "phase_gradient",
    "surface_functional_gradient",
    "multi_material_transition",
    "surface_oxidation_gradient",
    "surface_wear_gradient",
    "thermal_barrier_gradient",
    "tough_core_hard_surface",
    "metal_to_ceramic_transition",
)


class CompositionRange(TypedDict, total=False):
    element_or_phase: str
    minimum: float | None
    maximum: float | None
    nominal: float | None
    unit: str


class Constituent(TypedDict, total=False):
    name: str
    role: str
    material_family: str
    composition: dict[str, Any]
    composition_ranges: list[CompositionRange]
    volume_fraction: float | None
    morphology: str
    scale: str
    interface_notes: str
    evidence: dict[str, Any]


class GradientSegment(TypedDict, total=False):
    location: str
    from_value: Any
    to_value: Any
    unit: str | None
    rationale: str


class GradientArchitecture(TypedDict, total=False):
    gradient_type: str
    spatial_direction: str
    zones: list[dict[str, Any]]
    property_targets_by_zone: dict[str, Any]
    composition_profile: dict[str, Any]
    microstructure_profile: dict[str, Any]
    porosity_profile: dict[str, Any]
    manufacturing_route: str
    process_control_requirements: list[str]
    gradient_template_id: str
    gradient_benefit_claim: str
    gradient_risks: list[str]
    evidence_maturity: str

    # Earlier Build 4 type-shape fields retained for import/type compatibility.
    gradient_types: list[str]
    composition_gradients: list[GradientSegment]
    microstructure_gradients: list[GradientSegment]
    porosity_gradients: list[GradientSegment]
    reinforcement_gradients: list[GradientSegment]
    phase_gradients: list[GradientSegment]
    surface_functional_gradients: list[GradientSegment]
    multi_material_transitions: list[GradientSegment]
    transition_risks: list[str]
    inspection_needs: list[str]
    notes: str


class CoatingSystem(TypedDict, total=False):
    coating_type: str
    layers: list[Constituent]
    substrate_compatibility: str
    deposition_routes: list[str]
    failure_modes: list[str]
    repairability_notes: str
    evidence: dict[str, Any]


class ProcessingRoute(TypedDict, total=False):
    route_name: str
    route_family: str
    additive: bool | None
    conventional: bool | None
    heat_treatment: list[str]
    post_processing: list[str]
    inspection: list[str]
    qualification_notes: str
    risks: list[str]


class MaterialSystemCandidate(TypedDict, total=False):
    candidate_id: str
    candidate_class: str
    system_architecture_type: str
    system_name: str
    constituents: list[dict[str, Any]]
    interfaces: list[dict[str, Any]]
    process_route: dict[str, Any]
    coating_or_surface_system: dict[str, Any] | None
    gradient_architecture: GradientArchitecture | None
    inspection_strategy: dict[str, Any]
    repair_strategy: dict[str, Any]
    source_type: str
    evidence_package: dict[str, Any]
    generated_candidate_flag: bool
    research_mode_flag: bool
    factor_scores: dict[str, Any]
    uncertainty_flags: list[str]
    certification_risk_flags: list[str]
    optimisation_history: list[dict[str, Any]]

    # Earlier Build 4 differently named fields retained for import/type compatibility.
    name: str
    system_class: str
    system_classes: list[str]
    summary: str
    base_material_family: str
    coating_system: dict[str, Any] | None
    processing_routes: list[dict[str, Any]]
    compatible_design_space: dict[str, Any] | None
    property_estimates: dict[str, Any]
    evidence: dict[str, Any]
    evidence_maturity: str
    maturity_rationale: str
    generated_by_adapter: str | None
    research_generated: bool
    assumptions: list[str]
    risks: list[str]
    validation_plan: list[str]
    provenance: dict[str, Any]


class FactorScore(TypedDict, total=False):
    factor_name: str
    candidate_class: str
    score: float
    confidence: float
    method: str
    components: dict[str, Any]
    reason: str
    evidence_refs: list[str]
    assumptions: list[str]
    warnings: list[str]


class RecommendationPackage(TypedDict, total=False):
    run_id: str
    requirement_schema: dict[str, Any]
    design_space: dict[str, Any]
    candidate_systems: list[MaterialSystemCandidate]
    ranked_recommendations: list[dict[str, Any]]
    pareto_front: list[dict[str, Any]]
    optimisation_summary: dict[str, Any]
    source_mix_summary: dict[str, Any]
    evidence_maturity_summary: dict[str, Any]
    diagnostics: dict[str, Any]
    warnings: list[str]


MaterialSystemCandidateKind = Literal[
    "metallic_system",
    "monolithic_ceramic_system",
    "ceramic_matrix_composite_system",
    "polymer_matrix_composite_system",
    "coating_enabled_system",
    "hybrid_system",
    "spatially_graded_am_material_system",
    "research_generated_system",
]


def validate_gradient_architecture(gradient: Mapping[str, Any] | None) -> list[str]:
    if gradient is None:
        return []
    if not isinstance(gradient, Mapping):
        return ["gradient_architecture must be a mapping or None"]

    errors: list[str] = []

    gradient_type = gradient.get("gradient_type")
    if gradient_type is not None and gradient_type not in GRADIENT_TYPES:
        errors.append(
            f"gradient_type must be one of {', '.join(GRADIENT_TYPES)}; got {gradient_type!r}"
        )

    maturity = gradient.get("evidence_maturity")
    if maturity is not None and maturity not in EVIDENCE_MATURITY_LEVELS:
        errors.append(
            "gradient_architecture.evidence_maturity must be one of "
            f"{', '.join(EVIDENCE_MATURITY_LEVELS)}; got {maturity!r}"
        )

    if "zones" in gradient and not isinstance(gradient.get("zones"), list):
        errors.append("gradient_architecture.zones must be a list when present")

    if "gradient_risks" in gradient and not isinstance(gradient.get("gradient_risks"), list):
        errors.append("gradient_architecture.gradient_risks must be a list when present")

    if "process_control_requirements" in gradient and not isinstance(
        gradient.get("process_control_requirements"), list
    ):
        errors.append(
            "gradient_architecture.process_control_requirements must be a list when present"
        )

    return errors


def validate_material_system_candidate(candidate: Mapping[str, Any]) -> list[str]:
    if not isinstance(candidate, Mapping):
        return ["candidate must be a mapping"]

    errors: list[str] = []

    for field in ("candidate_id", "system_name", "system_architecture_type"):
        if not candidate.get(field):
            errors.append(f"{field} is required")

    architecture_type = candidate.get("system_architecture_type")
    if architecture_type and architecture_type not in SYSTEM_ARCHITECTURE_TYPES:
        errors.append(
            "system_architecture_type must be one of "
            f"{', '.join(SYSTEM_ARCHITECTURE_TYPES)}; got {architecture_type!r}"
        )

    if "gradient_architecture" in candidate:
        gradient = candidate.get("gradient_architecture")
        if gradient is not None:
            errors.extend(
                f"gradient_architecture: {error}"
                for error in validate_gradient_architecture(gradient)
            )
            if architecture_type == "bulk_material":
                errors.append("bulk_material systems must not carry gradient_architecture")

    if candidate.get("generated_candidate_flag") or candidate.get("research_mode_flag"):
        maturity = evidence_maturity(candidate)
        if maturity in {"A", "B", "C"}:
            errors.append(
                "generated or research-mode candidates cannot use mature evidence "
                f"maturity {maturity!r}"
            )

    return errors


def assert_valid_material_system_candidate(candidate: Mapping[str, Any]) -> None:
    errors = validate_material_system_candidate(candidate)
    if errors:
        raise ValueError("; ".join(errors))


def evidence_maturity(candidate: Mapping[str, Any]) -> str:
    if not isinstance(candidate, Mapping):
        return "unknown"

    evidence_package = candidate.get("evidence_package")
    if not isinstance(evidence_package, Mapping):
        return "unknown"

    maturity = evidence_package.get("evidence_maturity")
    if maturity:
        return str(maturity)
    return "unknown"
