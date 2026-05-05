from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

import pandas as pd

from src.candidate_normalizer import normalize_system_candidates
from src.design_space import build_design_space
from src.evidence_model import evaluate_candidates_evidence
from src.requirement_schema_v2 import DesignSpace, RequirementSchemaV2
from src.source_orchestrator import generate_candidate_sources, summarise_source_mix
from src.system_assembler import assemble_material_systems, summarize_system_assembly


ANCHOR_PROMPT = (
    "Identify material-system options for a high-temperature aviation component with thermal "
    "cycling, oxidation/steam exposure, low-weight preference, inspection concern and high "
    "certification sensitivity. Consider whether surface protection could be provided by a "
    "coating-enabled system or by a spatially graded AM surface architecture."
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _maturity(candidate: Mapping[str, Any]) -> str:
    evidence = candidate.get("evidence_package") or candidate.get("evidence") or {}
    evidence_mapping = evidence if isinstance(evidence, Mapping) else {}
    return _text(
        evidence_mapping.get("maturity")
        or evidence_mapping.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    )


def _candidate_blob(candidate: Mapping[str, Any]) -> str:
    values = [
        candidate.get("candidate_id"),
        candidate.get("name"),
        candidate.get("system_name"),
        candidate.get("summary"),
        candidate.get("base_material_family"),
        candidate.get("coating_or_surface_system"),
        candidate.get("coating_system"),
        candidate.get("gradient_architecture"),
        candidate.get("constituents"),
        candidate.get("provenance"),
    ]
    return " ".join(str(value).lower() for value in values if value is not None)


def _package_warnings(
    source_result: Mapping[str, Any],
    assembled_candidates: list[Mapping[str, Any]],
) -> list[str]:
    warnings = list(_as_list(source_result.get("warnings")))
    for candidate in assembled_candidates:
        candidate_id = _text(candidate.get("candidate_id"), "unknown_candidate")
        for warning in _as_list(candidate.get("assembly_warnings")):
            message = f"{candidate_id}: {warning}"
            if message not in warnings:
                warnings.append(message)
    return warnings


def build_ceramics_first_anchor_schema() -> RequirementSchemaV2:
    """Return the deterministic v3 anchor prompt as a RequirementSchemaV2-compatible mapping."""
    return {
        "schema_version": "2.0",
        "design_intent": "new_material_system",
        "prompt_raw": ANCHOR_PROMPT,
        "prompt_normalized": ANCHOR_PROMPT,
        "operating_envelope": {
            "temperature_band": "high_temperature_hot_section",
            "thermal_cycling": True,
            "oxidation_steam_exposure": True,
            "environment_tags": ["oxidation", "steam", "thermal cycling"],
        },
        "component": {
            "component_class": "high-temperature aviation component",
            "use_case_summary": "Hot-section aviation component with surface protection tradeoffs.",
            "aviation_domain": "propulsion",
            "criticality": "flight_critical",
            "geometry_complexity": "moderate_to_complex",
            "surface_or_bulk_driven": "both",
        },
        "mechanical": {
            "creep": {
                "priority": 0.85,
                "mandatory": True,
                "rationale": "High-temperature aviation service requires creep resistance.",
            },
            "thermal_fatigue": {
                "priority": 0.95,
                "mandatory": True,
                "rationale": "Thermal cycling is an anchor-prompt driver.",
            },
            "fracture_toughness": {
                "priority": 0.75,
                "mandatory": False,
                "rationale": "Ceramic brittleness and damage tolerance must remain visible.",
            },
            "load_regime_tags": ["thermal cycling", "high temperature", "aviation hot section"],
        },
        "thermal": {
            "operating_temperature": {
                "minimum": 1000,
                "unit": "C",
                "priority": 0.9,
                "mandatory": True,
                "rationale": "Anchor prompt requests high-temperature options.",
            },
            "peak_temperature": {
                "minimum": 1200,
                "unit": "C",
                "priority": 0.8,
                "mandatory": False,
                "rationale": "Peak hot-section excursions may exceed steady operating temperature.",
            },
            "temperature_unit": "C",
            "temperature_band": "high",
        },
        "environment": {
            "tags": ["oxidation", "steam", "water vapor recession", "thermal cycling"],
            "oxidizing": True,
            "moisture": True,
            "hot_corrosion": True,
            "erosion": True,
            "notes": "Oxidation/steam exposure and thermal cycling drive surface protection needs.",
        },
        "manufacturing": {
            "preferred_routes": [
                "ceramic matrix composite processing",
                "coating deposition",
                "additive manufacturing",
            ],
            "acceptable_routes": [
                "powder metallurgy",
                "casting plus coating",
                "directed energy deposition",
                "powder bed fusion",
            ],
            "additive_manufacturing_preferred": False,
            "additive_manufacturing_required": False,
            "conventional_processing_acceptable": True,
            "joining_or_repair_constraints": [
                "repairability of coatings and EBCs must remain visible",
                "graded AM repair route is not assumed mature",
            ],
            "inspection_requirements": [
                "inspect coating adhesion and spallation risk",
                "inspect CMC/EBC recession and defects",
                "verify graded transition-zone properties through depth",
            ],
            "qualification_sensitivity": "high",
        },
        "lifecycle": {
            "certification_maturity": {
                "target": "high",
                "priority": 1.0,
                "mandatory": True,
                "rationale": "Anchor prompt states high certification sensitivity.",
            },
            "through_life_cost": {
                "priority": 0.55,
                "mandatory": False,
                "rationale": "Repairability and inspection burden affect through-life cost.",
            },
            "repairability": {
                "priority": 0.7,
                "mandatory": False,
                "rationale": "Surface protection systems can be repair-limited.",
            },
            "sustainability": {
                "priority": 0.35,
                "mandatory": False,
                "rationale": "Kept visible but not optimized in this foundation slice.",
            },
            "supply_risk": {
                "priority": 0.45,
                "mandatory": False,
                "rationale": "Rare-earth EBC and refractory concepts may carry supply risk.",
            },
            "evidence_maturity_floor": "C",
        },
        "material_system_intent": {
            "allow_bulk_material_only": True,
            "allow_substrate_plus_coating": True,
            "allow_spatial_gradients": True,
            "allow_composite_architecture": True,
            "allow_research_mode_candidates": False,
        },
        "spatial_property_intent": {
            "coating_replacement_allowed": True,
            "gradient_as_coating_alternative": True,
            "surface_to_core_property_needs": [
                "oxidation protection",
                "thermal protection",
                "thermal expansion transition management",
                "tougher or more damage-tolerant core",
            ],
        },
        "material_family_inclusions": [
            "metallic",
            "monolithic ceramic",
            "ceramic matrix composite",
            "coating-enabled system",
            "spatially graded AM system",
        ],
        "material_family_exclusions": [],
        "coating_allowed": True,
        "composite_allowed": True,
        "graded_architecture_allowed": True,
        "research_generated_allowed": False,
        "hard_constraints": {
            "no_live_specialist_model_calls": True,
            "no_materials_project_calls": True,
            "do_not_filter_candidates": True,
        },
        "soft_objectives": {
            "low_weight": 0.9,
            "oxidation_steam_resistance": 0.9,
            "thermal_cycling_resistance": 0.9,
            "inspection_accessibility": 0.75,
            "certification_maturity": 1.0,
            "repairability": 0.6,
            "through_life_cost": 0.45,
            "sustainability": 0.3,
            "supply_resilience": 0.35,
        },
        "tradeoff_mode": "ceramics_first_surface_protection_tradeoff",
        "ambiguities": [
            "Specific component geometry and load spectrum are unspecified.",
            "Exact temperature, steam partial pressure and thermal-cycle dwell are unspecified.",
            "Inspection access and repair interval are not yet quantified.",
        ],
        "assumptions": [
            "Treat coatings as system components rather than standalone bulk candidates.",
            "Treat graded AM concepts as distinguishable alternatives to discrete coatings.",
            "Keep research mode disabled for this deterministic vertical slice.",
        ],
        "interpreter_confidence": 0.82,
        "interpreter_trace": [
            "Manually constructed Build 4 ceramics-first anchor schema.",
            "Enabled coating, composite and spatial-gradient architecture flags.",
            "Disabled research-generated candidates and live specialist model calls.",
        ],
    }


def build_ceramics_first_design_space() -> DesignSpace:
    """Build the deterministic ceramics-first design space from the anchor schema."""
    design_space = build_design_space(build_ceramics_first_anchor_schema())
    design_space["coating_vs_gradient_comparison_required"] = True
    design_space["research_mode_enabled"] = False
    design_space["generation_hints"] = {
        **dict(design_space.get("generation_hints") or {}),
        "candidate_generation_enabled": False,
        "live_model_calls_enabled": False,
        "research_mode_enabled": False,
    }
    design_space["retrieval_hints"] = {
        **dict(design_space.get("retrieval_hints") or {}),
        "ceramics_first_vertical_slice": True,
        "include_monolithic_ceramic_references": True,
        "include_cmc_ebc_references": True,
        "include_coating_enabled_systems": True,
        "include_spatial_gradient_templates": True,
    }
    return design_space


def build_demo_build31_metallic_rows() -> pd.DataFrame:
    """Return tiny in-memory mature metallic comparison rows for the Build 3.1 adapter path."""
    return pd.DataFrame(
        [
            {
                "candidate_id": "demo_ni_superalloy_bondcoat_tbc_comparison",
                "candidate_source": "engineering_analogue",
                "candidate_role": "mature_metallic_surface_protection_comparison",
                "material_family": "nickel superalloy substrate with bond coat and TBC",
                "composition_concept": "Ni superalloy + MCrAlY bond coat + yttria-stabilized zirconia TBC",
                "chemsys": "Ni-Co-Cr-Al-Y-Zr-O",
                "recipe_mode": "curated_mature_comparison",
                "matched_alloy_name": "CMSX-4 / Rene N5 class nickel superalloy with TBC",
                "source_alloy_name": "nickel superalloy hot-section TBC reference",
                "evidence_maturity_score": 0.82,
                "creep_score": 0.78,
                "temperature_score": 0.82,
                "toughness_score": 0.7,
                "through_life_cost_score": 0.55,
                "sustainability_score_v1": 0.35,
                "manufacturability_score": 0.72,
                "route_suitability_score": 0.75,
                "supply_risk_score": 0.5,
                "recipe_support_score": 0.8,
                "base_process_route": "cast or wrought superalloy plus bond coat plus TBC",
                "manufacturing_primary_route": "conventional metallic substrate with coating deposition",
                "provenance": "handcrafted Build 4 vertical-slice demo row; no Materials Project call",
            },
            {
                "candidate_id": "demo_refractory_oxidation_protection_comparison",
                "candidate_source": "literature_reference",
                "candidate_role": "emerging_metallic_oxidation_protection_comparison",
                "material_family": "refractory alloy with oxidation protection",
                "composition_concept": "Nb or Mo refractory alloy plus silicide/aluminide oxidation protection",
                "chemsys": "Nb-Mo-Si-Al-O",
                "recipe_mode": "handcrafted_emerging_comparison",
                "matched_alloy_name": "refractory alloy oxidation-protection concept",
                "evidence_maturity_score": 0.45,
                "temperature_score": 0.75,
                "toughness_score": 0.55,
                "manufacturability_score": 0.42,
                "route_suitability_score": 0.45,
                "supply_risk_score": 0.35,
                "base_process_route": "powder metallurgy or coating-assisted refractory alloy route",
                "manufacturing_primary_route": "emerging refractory processing plus protective coating",
                "provenance": "handcrafted Build 4 vertical-slice demo row; no Materials Project call",
            },
        ]
    )


def build_ceramics_first_candidate_package() -> dict[str, Any]:
    """Assemble a deterministic candidate/evidence/interface package for the anchor prompt."""
    schema = build_ceramics_first_anchor_schema()
    design_space = build_ceramics_first_design_space()
    demo_df = build_demo_build31_metallic_rows()

    source_result = generate_candidate_sources(
        requirements=schema,
        design_space=design_space,
        build31_candidates_df=demo_df,
    )
    source_candidates = list(source_result.get("candidate_systems") or [])
    normalized_candidates = normalize_system_candidates(source_candidates)
    evidence_candidates = evaluate_candidates_evidence(normalized_candidates)
    assembled_candidates = assemble_material_systems(evidence_candidates)

    assembly_summary = summarize_system_assembly(assembled_candidates)
    diagnostics = {
        **dict(source_result.get("diagnostics") or {}),
        "vertical_slice": "ceramics_first",
        "anchor_prompt": "v3_ceramics_first",
        "normalization_candidate_count": len(normalized_candidates),
        "evidence_candidate_count": len(evidence_candidates),
        "assembled_candidate_count": len(assembled_candidates),
        "candidate_count_preserved": (
            len(source_candidates) == len(normalized_candidates) == len(evidence_candidates) == len(assembled_candidates)
        ),
        "live_model_calls_made": False,
        "materials_project_calls_made": False,
        "build31_candidate_generation_called": False,
        "ranking_or_optimisation_performed": False,
        "assembly_summary": assembly_summary,
    }

    evidence_maturity_summary = {
        "candidate_count": len(assembled_candidates),
        "maturity_counts": dict(sorted(Counter(_maturity(candidate) for candidate in assembled_candidates).items())),
    }

    return {
        "run_id": "build4_ceramics_first_anchor_v1",
        "requirement_schema": schema,
        "design_space": design_space,
        "candidate_systems": assembled_candidates,
        "ranked_recommendations": [],
        "pareto_front": [],
        "optimisation_summary": {"status": "not_implemented"},
        "source_mix_summary": summarise_source_mix(assembled_candidates),
        "evidence_maturity_summary": evidence_maturity_summary,
        "diagnostics": diagnostics,
        "warnings": _package_warnings(source_result, assembled_candidates),
    }


def summarize_ceramics_first_package(package: Mapping[str, Any]) -> dict[str, Any]:
    """Return coverage booleans and mixes for a ceramics-first package."""
    candidates = [
        candidate
        for candidate in _as_list(package.get("candidate_systems"))
        if isinstance(candidate, Mapping)
    ]
    design_space = package.get("design_space") or {}
    design_space_mapping = design_space if isinstance(design_space, Mapping) else {}

    class_mix = Counter(_candidate_class(candidate) for candidate in candidates)
    architecture_mix = Counter(_architecture(candidate) for candidate in candidates)
    maturity_mix = Counter(_maturity(candidate) for candidate in candidates)

    blobs = [_candidate_blob(candidate) for candidate in candidates]
    has_sic_sic_cmc_ebc_anchor = any(
        "sic/sic" in blob and ("ebc" in blob or "environmental barrier" in blob)
        for blob in blobs
    )
    has_ni_tbc_comparison = any(
        "ni superalloy" in blob and ("tbc" in blob or "thermal barrier" in blob)
        for blob in blobs
    )

    return {
        "candidate_count": len(candidates),
        "candidate_class_mix": dict(sorted(class_mix.items())),
        "system_architecture_mix": dict(sorted(architecture_mix.items())),
        "evidence_maturity_mix": dict(sorted(maturity_mix.items())),
        "has_ni_tbc_comparison": has_ni_tbc_comparison,
        "has_sic_sic_cmc_ebc_anchor": has_sic_sic_cmc_ebc_anchor,
        "has_monolithic_ceramic": any(_candidate_class(candidate) == "monolithic_ceramic" for candidate in candidates),
        "has_graded_am_alternative": any(
            _candidate_class(candidate) == "spatially_graded_am"
            or _architecture(candidate) == "spatial_gradient"
            for candidate in candidates
        ),
        "has_coating_enabled_system": any(
            _candidate_class(candidate) == "coating_enabled"
            or _architecture(candidate) == "substrate_plus_coating"
            for candidate in candidates
        ),
        "research_mode_enabled": design_space_mapping.get("research_mode_enabled") is True,
        "warnings": list(_as_list(package.get("warnings"))),
    }
