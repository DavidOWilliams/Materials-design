from __future__ import annotations

from typing import Any, Dict, Final, List, Literal, Optional, TypedDict


EvidenceMaturity = Literal["A", "B", "C", "D", "E", "F"]

EVIDENCE_MATURITY_LEVELS: Final[tuple[str, ...]] = ("A", "B", "C", "D", "E", "F")

EVIDENCE_MATURITY_DESCRIPTIONS: Final[Dict[str, str]] = {
    "A": "Qualified / production aerospace use",
    "B": "Mature aerospace analogue",
    "C": "Engineering reference / adjacent use",
    "D": "Laboratory / literature demonstrated",
    "E": "Database / computational exploratory",
    "F": "Generated / unvalidated research suggestion",
}

EVIDENCE_MATURITY_RECOMMENDATION_TREATMENT: Final[Dict[str, str]] = {
    "A": "May be presented as a mature aerospace reference, subject to normal engineering validation.",
    "B": "May be presented as a mature analogue, with explicit comparison to the target use case.",
    "C": "May be presented as an engineering reference or adjacent-use option.",
    "D": "Should be presented as literature/laboratory demonstrated and not qualified.",
    "E": "Should be presented as exploratory database or computational evidence only.",
    "F": "Should be presented as generated, unvalidated research-mode output only.",
}


MaterialSystemClass = Literal[
    "metallic",
    "monolithic_ceramic",
    "ceramic_matrix_composite",
    "polymer_matrix_composite",
    "coating_enabled",
    "hybrid",
    "spatially_graded_am",
    "research_generated",
]

MATERIAL_SYSTEM_CLASSES: Final[tuple[str, ...]] = (
    "metallic",
    "monolithic_ceramic",
    "ceramic_matrix_composite",
    "polymer_matrix_composite",
    "coating_enabled",
    "hybrid",
    "spatially_graded_am",
    "research_generated",
)


GradientType = Literal[
    "composition",
    "microstructure",
    "porosity",
    "reinforcement",
    "phase",
    "surface_functional",
    "multi_material_transition",
]

GRADIENT_TYPES: Final[tuple[str, ...]] = (
    "composition",
    "microstructure",
    "porosity",
    "reinforcement",
    "phase",
    "surface_functional",
    "multi_material_transition",
)


ConstituentRole = Literal[
    "matrix",
    "reinforcement",
    "fiber",
    "coating",
    "bond_coat",
    "interphase",
    "barrier_layer",
    "substrate",
    "phase",
    "additive",
    "filler",
    "transition_material",
    "surface_function",
    "other",
]

CONSTITUENT_ROLES: Final[tuple[str, ...]] = (
    "matrix",
    "reinforcement",
    "fiber",
    "coating",
    "bond_coat",
    "interphase",
    "barrier_layer",
    "substrate",
    "phase",
    "additive",
    "filler",
    "transition_material",
    "surface_function",
    "other",
)


ResearchAdapterStatus = Literal["disabled", "available", "error"]

RESEARCH_ADAPTER_STATUSES: Final[tuple[str, ...]] = (
    "disabled",
    "available",
    "error",
)


SourceType = Literal[
    "build31_metallic_baseline",
    "curated_engineering_reference",
    "materials_project",
    "literature_reference",
    "database_exploratory",
    "research_model_generated",
    "manual_engineering_entry",
]

SOURCE_TYPES: Final[tuple[str, ...]] = (
    "build31_metallic_baseline",
    "curated_engineering_reference",
    "materials_project",
    "literature_reference",
    "database_exploratory",
    "research_model_generated",
    "manual_engineering_entry",
)


class EvidencePackage(TypedDict, total=False):
    maturity: EvidenceMaturity
    maturity_label: str
    summary: str
    sources: List[str]
    aerospace_use: List[str]
    engineering_analogues: List[str]
    literature_refs: List[str]
    database_refs: List[str]
    computational_refs: List[str]
    generated_by: Optional[str]
    validation_gaps: List[str]
    assumptions: List[str]
    confidence: float


class FactorScore(TypedDict, total=False):
    factor: str
    score: float
    weight: float
    reason: str
    evidence: EvidencePackage
    uncertainty: Optional[float]
    flags: List[str]


class ResearchAdapterResult(TypedDict, total=False):
    adapter: str
    status: ResearchAdapterStatus
    enabled: bool
    message: str
    candidates: List[Dict[str, Any]]
    evidence: List[EvidencePackage]
    metadata: Dict[str, Any]


def evidence_maturity_label(level: str) -> str:
    """Return the display label for an A-F evidence maturity level."""
    return EVIDENCE_MATURITY_DESCRIPTIONS.get(
        str(level).upper(),
        "Unknown evidence maturity",
    )


def evidence_maturity_treatment(level: str) -> str:
    """Return the recommended treatment for an A-F evidence maturity level."""
    return EVIDENCE_MATURITY_RECOMMENDATION_TREATMENT.get(
        str(level).upper(),
        "Treat as unvalidated until evidence maturity is assigned.",
    )


def disabled_research_adapter_result(
    adapter_name: str,
    message: str | None = None,
) -> ResearchAdapterResult:
    """Standard disabled-result payload for Phase 1 research adapter stubs."""
    return {
        "adapter": adapter_name,
        "status": "disabled",
        "enabled": False,
        "message": message or f"{adapter_name} is disabled in Phase 1.",
        "candidates": [],
        "evidence": [],
        "metadata": {"phase": "Phase 1", "live_calls_permitted": False},
    }