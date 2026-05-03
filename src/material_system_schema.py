from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


from src.contracts import (
    ConstituentRole,
    EvidenceMaturity,
    EvidencePackage,
    FactorScore,
    GradientType,
    MaterialSystemClass,
)
from src.requirement_schema_v2 import DesignSpace


class CompositionRange(TypedDict, total=False):
    element_or_phase: str
    minimum: Optional[float]
    maximum: Optional[float]
    nominal: Optional[float]
    unit: str


class Constituent(TypedDict, total=False):
    name: str
    role: ConstituentRole
    material_family: str
    composition: Dict[str, Any]
    composition_ranges: List[CompositionRange]
    volume_fraction: Optional[float]
    morphology: str
    scale: str
    interface_notes: str
    evidence: EvidencePackage


class GradientSegment(TypedDict, total=False):
    location: str
    from_value: Any
    to_value: Any
    unit: Optional[str]
    rationale: str


class GradientArchitecture(TypedDict, total=False):
    gradient_types: List[GradientType]
    composition_gradients: List[GradientSegment]
    microstructure_gradients: List[GradientSegment]
    porosity_gradients: List[GradientSegment]
    reinforcement_gradients: List[GradientSegment]
    phase_gradients: List[GradientSegment]
    surface_functional_gradients: List[GradientSegment]
    multi_material_transitions: List[GradientSegment]
    manufacturing_route: str
    transition_risks: List[str]
    inspection_needs: List[str]
    notes: str


class CoatingSystem(TypedDict, total=False):
    coating_type: str
    layers: List[Constituent]
    substrate_compatibility: str
    deposition_routes: List[str]
    failure_modes: List[str]
    repairability_notes: str
    evidence: EvidencePackage


class ProcessingRoute(TypedDict, total=False):
    route_name: str
    route_family: str
    additive: Optional[bool]
    conventional: Optional[bool]
    heat_treatment: List[str]
    post_processing: List[str]
    inspection: List[str]
    qualification_notes: str
    risks: List[str]


class MaterialSystemCandidate(TypedDict, total=False):
    candidate_id: str
    name: str
    system_class: MaterialSystemClass
    system_classes: List[MaterialSystemClass]
    summary: str
    base_material_family: str
    constituents: List[Constituent]
    coating_system: Optional[CoatingSystem]
    gradient_architecture: Optional[GradientArchitecture]
    processing_routes: List[ProcessingRoute]
    compatible_design_space: Optional[DesignSpace]
    property_estimates: Dict[str, Any]
    factor_scores: List[FactorScore]
    evidence: EvidencePackage
    evidence_maturity: EvidenceMaturity
    maturity_rationale: str
    generated_by_adapter: Optional[str]
    research_generated: bool
    assumptions: List[str]
    risks: List[str]
    validation_plan: List[str]
    provenance: Dict[str, Any]


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
