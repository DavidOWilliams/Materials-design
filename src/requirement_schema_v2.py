from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


from src.contracts import EvidenceMaturity


CriticalityLevel = Literal["low", "medium", "high", "flight_critical"]
TemperatureUnit = Literal["C", "F", "K"]
DesignIntent = Literal[
    "selection",
    "substitution",
    "new_material_system",
    "coating_or_surface_system",
    "graded_am_system",
    "research_exploration",
]


class RequirementValue(TypedDict, total=False):
    target: Any
    minimum: Any
    maximum: Any
    unit: Optional[str]
    priority: float
    mandatory: bool
    rationale: str


class EnvironmentRequirement(TypedDict, total=False):
    tags: List[str]
    oxidizing: Optional[bool]
    hot_corrosion: Optional[bool]
    salt_contaminants: Optional[bool]
    moisture: Optional[bool]
    fuel_or_oil_contact: Optional[bool]
    erosion: Optional[bool]
    wear_or_sliding_contact: Optional[bool]
    notes: str


class MechanicalRequirement(TypedDict, total=False):
    strength: RequirementValue
    stiffness: RequirementValue
    fracture_toughness: RequirementValue
    fatigue: RequirementValue
    creep: RequirementValue
    thermal_fatigue: RequirementValue
    wear: RequirementValue
    impact: RequirementValue
    load_regime_tags: List[str]


class ThermalRequirement(TypedDict, total=False):
    operating_temperature: RequirementValue
    peak_temperature: RequirementValue
    thermal_gradient: RequirementValue
    thermal_conductivity: RequirementValue
    thermal_expansion: RequirementValue
    temperature_unit: TemperatureUnit
    temperature_band: str


class ManufacturingRequirement(TypedDict, total=False):
    preferred_routes: List[str]
    acceptable_routes: List[str]
    disallowed_routes: List[str]
    additive_manufacturing_preferred: Optional[bool]
    additive_manufacturing_required: Optional[bool]
    conventional_processing_acceptable: Optional[bool]
    joining_or_repair_constraints: List[str]
    inspection_requirements: List[str]
    qualification_sensitivity: str


class LifecycleRequirement(TypedDict, total=False):
    certification_maturity: RequirementValue
    through_life_cost: RequirementValue
    repairability: RequirementValue
    sustainability: RequirementValue
    supply_risk: RequirementValue
    recyclability: RequirementValue
    evidence_maturity_floor: Optional[EvidenceMaturity]


class ComponentRequirement(TypedDict, total=False):
    component_class: str
    use_case_summary: str
    aviation_domain: str
    criticality: CriticalityLevel
    geometry_complexity: str
    surface_or_bulk_driven: Literal["surface", "bulk", "both", "unknown"]


class RequirementSchemaV2(TypedDict, total=False):
    schema_version: str
    design_intent: DesignIntent
    prompt_raw: str
    prompt_normalized: str
    component: ComponentRequirement
    mechanical: MechanicalRequirement
    thermal: ThermalRequirement
    environment: EnvironmentRequirement
    manufacturing: ManufacturingRequirement
    lifecycle: LifecycleRequirement
    material_family_inclusions: List[str]
    material_family_exclusions: List[str]
    coating_allowed: Optional[bool]
    composite_allowed: Optional[bool]
    graded_architecture_allowed: Optional[bool]
    research_generated_allowed: Optional[bool]
    hard_constraints: Dict[str, Any]
    soft_objectives: Dict[str, float]
    tradeoff_mode: str
    ambiguities: List[str]
    assumptions: List[str]
    interpreter_confidence: float
    interpreter_trace: List[str]


class DesignSpace(TypedDict, total=False):
    design_space_version: str
    requirement_schema_version: str
    allowed_system_classes: List[str]
    allowed_material_families: List[str]
    excluded_material_families: List[str]
    allowed_constituent_roles: List[str]
    allowed_gradient_types: List[str]
    allowed_manufacturing_routes: List[str]
    excluded_manufacturing_routes: List[str]
    target_property_windows: Dict[str, RequirementValue]
    active_failure_modes: List[str]
    active_factor_weights: Dict[str, float]
    evidence_maturity_floor: Optional[EvidenceMaturity]
    retrieval_hints: Dict[str, Any]
    generation_hints: Dict[str, Any]
    warnings: List[str]
    planner_trace: List[str]
