from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class ComponentContext(TypedDict, total=False):
    component_class: str
    use_case_summary: str
    geometry_complexity: str
    repairability_importance: str


class OperatingEnvelope(TypedDict, total=False):
    temperature_c: int
    temperature_band: str
    environment_tags: List[str]
    load_regime_tags: List[str]


class HardConstraints(TypedDict, total=False):
    must_support_am: bool
    must_avoid_am: bool
    must_be_lightweight: bool
    max_density: float | None
    family_inclusions: List[str]
    family_exclusions: List[str]
    process_exclusions: List[str]


class SoftObjectives(TypedDict, total=False):
    priority_order: List[str]
    factor_importance: Dict[str, float]
    tradeoff_mode: str


class ManufacturingIntent(TypedDict, total=False):
    preferred_routes: List[str]
    disfavoured_routes: List[str]
    inspection_sensitivity: str
    qualification_sensitivity: str


class LifecyclePriorities(TypedDict, total=False):
    through_life_cost: float
    sustainability: float
    supply_risk: float
    repairability: float
    certification_maturity: float


class RequirementSchema(TypedDict, total=False):
    schema_version: str
    prompt_raw: str
    prompt_normalized: str
    component_context: ComponentContext
    operating_envelope: OperatingEnvelope
    hard_constraints: HardConstraints
    soft_objectives: SoftObjectives
    failure_mode_priorities: Dict[str, float]
    manufacturing_intent: ManufacturingIntent
    lifecycle_priorities: LifecyclePriorities
    ambiguities: List[str]
    interpreter_confidence: float
    interpreter_trace: List[str]


class ScopePlan(TypedDict, total=False):
    scope_version: str
    allowed_families: List[str]
    family_priors: Dict[str, float]
    family_rationale: Dict[str, str]
    retrieval_hints: Dict[str, Any]
    active_factor_set: List[str]
    inactive_factor_set: List[str]
    active_factor_weights: Dict[str, float]
    scope_warnings: List[str]
    planner_trace: List[str]


FAMILY_KEYS = ["Ni-based superalloy", "Co-based alloy", "Fe-Ni alloy", "Ti alloy", "Refractory alloy concept"]

FAMILY_DISPLAY_NAMES = {
    "Ni-based superalloy": "Ni-based superalloy",
    "Co-based alloy": "Co-based alloy",
    "Fe-Ni alloy": "Fe-Ni alloy",
    "Ti alloy": "Ti alloy",
    "Refractory alloy concept": "Refractory alloy concept",
}

# Maps candidate-generation material_family labels back into scope-plan keys.
CANDIDATE_FAMILY_TO_SCOPE_KEY = {
    "Ni-based superalloy-like candidate": "Ni-based superalloy",
    "Ni-based": "Ni-based superalloy",
    "Co-based high-temperature candidate": "Co-based alloy",
    "Co-based": "Co-based alloy",
    "Refractory-alloy-like candidate": "Refractory alloy concept",
    "Refractory": "Refractory alloy concept",
    "Ti-alloy-like candidate": "Ti alloy",
    "Ti-based": "Ti alloy",
    "Fe-Ni high-temperature candidate": "Fe-Ni alloy",
    "Fe-Ni": "Fe-Ni alloy",
}

BASELINE_FACTORS = [
    "creep",
    "toughness",
    "temperature",
    "through_life_cost",
    "sustainability",
    "manufacturability",
    "route_suitability",
    "supply_risk",
    "evidence_maturity",
    "recipe_support",
]

OPTIONAL_FACTORS = [
    "lightweight",
    "oxidation",
    "hot_corrosion",
    "wear",
    "erosion",
    "fatigue",
    "thermal_fatigue",
    "repairability",
    "certification_maturity",
]

FACTOR_LABELS = {
    "creep": "Creep suitability",
    "toughness": "Toughness / damage tolerance",
    "temperature": "Temperature suitability",
    "through_life_cost": "Through-life cost",
    "sustainability": "Sustainability",
    "manufacturability": "Manufacturability",
    "route_suitability": "Preferred-route suitability",
    "supply_risk": "Supply-chain / critical-material risk",
    "evidence_maturity": "Evidence / maturity",
    "recipe_support": "Recipe support",
    "lightweight": "Lightweight / strength-to-weight fit",
    "oxidation": "Oxidation resistance",
    "hot_corrosion": "Hot-corrosion resistance",
    "wear": "Wear resistance",
    "erosion": "Erosion resistance",
    "fatigue": "Fatigue resistance proxy",
    "thermal_fatigue": "Thermal-fatigue resistance proxy",
    "repairability": "Repairability / maintainability",
    "certification_maturity": "Certification maturity",
}

# Column names used by the scoring and UI layers.
FACTOR_SCORE_COLUMNS = {
    "creep": "creep_score",
    "toughness": "toughness_score",
    "temperature": "temperature_score",
    "through_life_cost": "through_life_cost_score",
    "sustainability": "sustainability_score_v1",
    "manufacturability": "manufacturability_score",
    "route_suitability": "route_suitability_score",
    "supply_risk": "supply_risk_score",
    "evidence_maturity": "evidence_maturity_score",
    "recipe_support": "recipe_support_score",
    "lightweight": "lightweight_score",
    "oxidation": "oxidation_score",
    "hot_corrosion": "hot_corrosion_score",
    "wear": "wear_score",
    "erosion": "erosion_score",
    "fatigue": "fatigue_score",
    "thermal_fatigue": "thermal_fatigue_score",
    "repairability": "repairability_score",
    "certification_maturity": "certification_maturity_score",
}

FACTOR_REASON_COLUMNS = {
    factor: column.replace("_score", "_reason") for factor, column in FACTOR_SCORE_COLUMNS.items()
}
