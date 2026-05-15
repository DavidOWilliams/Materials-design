from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any, TypedDict


EVIDENCE_MATURITY_LEVELS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "unknown")

SUPPORTED_GRADIENT_TYPES: tuple[str, ...] = (
    "surface_oxidation_gradient",
    "surface_wear_gradient",
    "thermal_barrier_gradient",
    "tough_core_hard_surface",
    "metal_to_ceramic_transition",
)

REQUIRED_TEMPLATE_FIELDS: tuple[str, ...] = (
    "template_id",
    "template_name",
    "gradient_type",
    "activation_failure_modes",
    "applicable_candidate_classes",
    "applicable_substrate_families",
    "allowed_process_routes",
    "expected_benefits",
    "known_risks",
    "minimum_evidence_maturity_default",
    "research_mode_required",
    "applicability_guardrails",
)

LIST_TEMPLATE_FIELDS: tuple[str, ...] = (
    "activation_failure_modes",
    "applicable_candidate_classes",
    "applicable_substrate_families",
    "allowed_process_routes",
    "expected_benefits",
    "known_risks",
    "applicability_guardrails",
)


class GradientTemplate(TypedDict, total=False):
    template_id: str
    template_name: str
    gradient_type: str
    activation_failure_modes: list[str]
    applicable_candidate_classes: list[str]
    applicable_substrate_families: list[str]
    allowed_process_routes: list[str]
    property_targets_by_zone: dict[str, Any]
    expected_benefits: list[str]
    known_risks: list[str]
    minimum_evidence_maturity_default: str
    research_mode_required: bool
    applicability_guardrails: list[str]


DEFAULT_GRADIENT_TEMPLATES: tuple[GradientTemplate, ...] = (
    {
        "template_id": "surface_oxidation_gradient",
        "template_name": "Surface Oxidation Gradient",
        "gradient_type": "surface_oxidation_gradient",
        "activation_failure_modes": [
            "oxidation",
            "hot_corrosion",
            "steam_exposure",
            "surface_temperature_limit",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "refractory",
            "coating_enabled",
        ],
        "applicable_substrate_families": [
            "nickel_alloy",
            "cobalt_alloy",
            "refractory_alloy",
            "titanium_alloy",
        ],
        "allowed_process_routes": [
            "DED",
            "LPBF",
            "directed_energy_deposition",
        ],
        "property_targets_by_zone": {
            "surface": ["oxidation resistance", "hot-corrosion resistance"],
            "subsurface": ["substrate compatibility", "thermal-cycle tolerance"],
        },
        "expected_benefits": [
            "improved surface oxidation resistance",
            "reduced dependence on a discrete coating interface",
        ],
        "known_risks": [
            "residual stress",
            "brittle phases",
            "process repeatability",
            "inspection burden",
        ],
        "minimum_evidence_maturity_default": "D",
        "research_mode_required": False,
        "applicability_guardrails": [
            "Use only as a curated deterministic template.",
            "Do not treat as a qualified oxidation-protection system without validation.",
        ],
    },
    {
        "template_id": "surface_wear_gradient",
        "template_name": "Surface Wear Gradient",
        "gradient_type": "surface_wear_gradient",
        "activation_failure_modes": [
            "wear",
            "sliding_contact",
            "erosion",
            "fretting",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "coating_enabled",
            "ceramic",
        ],
        "applicable_substrate_families": [
            "titanium_alloy",
            "cobalt_alloy",
            "nickel_alloy",
            "steel",
            "ceramic",
        ],
        "allowed_process_routes": [
            "DED",
            "LPBF",
            "laser_cladding",
        ],
        "property_targets_by_zone": {
            "surface": ["wear resistance", "erosion resistance"],
            "core": ["damage tolerance", "substrate toughness"],
        },
        "expected_benefits": [
            "higher local wear resistance",
            "reduced need for a separate hard-facing layer",
        ],
        "known_risks": [
            "cracking",
            "local brittleness",
            "repairability burden",
        ],
        "minimum_evidence_maturity_default": "D",
        "research_mode_required": False,
        "applicability_guardrails": [
            "Check that local hardening does not compromise fatigue-sensitive regions.",
            "Treat repairability as a first-order review factor.",
        ],
    },
    {
        "template_id": "thermal_barrier_gradient",
        "template_name": "Thermal Barrier Gradient",
        "gradient_type": "thermal_barrier_gradient",
        "activation_failure_modes": [
            "thermal_barrier",
            "thermal_gradient",
            "surface_temperature_limit",
            "coating_spallation",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "ceramic",
            "hybrid",
        ],
        "applicable_substrate_families": [
            "nickel_alloy",
            "ceramic",
            "refractory_alloy",
        ],
        "allowed_process_routes": [
            "DED",
            "LPBF",
            "additive_manufacturing",
        ],
        "property_targets_by_zone": {
            "surface": ["low thermal conductivity", "thermal-cycle tolerance"],
            "subsurface": ["thermal expansion transition", "strain tolerance"],
        },
        "expected_benefits": [
            "reduced thermal mismatch at the surface",
            "potential coating-spallation mitigation",
        ],
        "known_risks": [
            "thermal stress",
            "conductivity uncertainty",
            "process sensitivity",
            "maturity risk",
        ],
        "minimum_evidence_maturity_default": "E",
        "research_mode_required": True,
        "applicability_guardrails": [
            "Require research-mode handling until evidence maturity improves.",
            "Do not present as a replacement for mature TBC evidence.",
        ],
    },
    {
        "template_id": "tough_core_hard_surface",
        "template_name": "Tough Core Hard Surface",
        "gradient_type": "tough_core_hard_surface",
        "activation_failure_modes": [
            "contact_damage",
            "wear",
            "fatigue_surface_sensitivity",
            "surface_hardness",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "hybrid",
        ],
        "applicable_substrate_families": [
            "titanium_alloy",
            "steel",
            "nickel_alloy",
            "cobalt_alloy",
        ],
        "allowed_process_routes": [
            "DED",
            "LPBF",
            "heat_treatment_gradient",
        ],
        "property_targets_by_zone": {
            "surface": ["surface hardness", "contact-damage resistance"],
            "core": ["toughness", "fatigue tolerance"],
        },
        "expected_benefits": [
            "improved surface damage resistance",
            "retained core toughness",
        ],
        "known_risks": [
            "transition-zone cracking",
            "residual stress",
            "inspection burden",
        ],
        "minimum_evidence_maturity_default": "D",
        "research_mode_required": False,
        "applicability_guardrails": [
            "Review transition-zone cracking risk before activation.",
            "Do not hide fatigue penalties behind surface-hardness gains.",
        ],
    },
    {
        "template_id": "metal_to_ceramic_transition",
        "template_name": "Metal to Ceramic Transition",
        "gradient_type": "metal_to_ceramic_transition",
        "activation_failure_modes": [
            "interface_mismatch",
            "cte_mismatch",
            "coating_spallation",
            "dissimilar_material_joining",
        ],
        "applicable_candidate_classes": [
            "hybrid",
            "coating_enabled",
            "research_generated",
        ],
        "applicable_substrate_families": [
            "nickel_alloy",
            "refractory_alloy",
            "ceramic",
            "cmc",
        ],
        "allowed_process_routes": [
            "DED",
            "additive_manufacturing",
            "joining",
        ],
        "property_targets_by_zone": {
            "metal_side": ["metal compatibility", "ductility retention"],
            "ceramic_side": ["thermal stability", "oxidation or environmental resistance"],
            "transition": ["CTE transition", "interface stress reduction"],
        },
        "expected_benefits": [
            "reduced abrupt interface mismatch",
            "structured path for dissimilar material joining review",
        ],
        "known_risks": [
            "brittle intermetallics",
            "CTE mismatch",
            "high uncertainty",
            "certification risk",
        ],
        "minimum_evidence_maturity_default": "F",
        "research_mode_required": True,
        "applicability_guardrails": [
            "Require research-mode handling.",
            "Do not present as production-ready without dedicated validation evidence.",
        ],
    },
)


def _caller_safe_template(template: Mapping[str, Any]) -> GradientTemplate:
    return deepcopy(dict(template))


def _normalise(value: str) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _normalised_values(values: list[str]) -> set[str]:
    return {_normalise(value) for value in values}


def get_gradient_templates() -> tuple[GradientTemplate, ...]:
    return tuple(_caller_safe_template(template) for template in DEFAULT_GRADIENT_TEMPLATES)


def get_gradient_template(template_id: str) -> GradientTemplate | None:
    normalised_id = _normalise(template_id)
    for template in DEFAULT_GRADIENT_TEMPLATES:
        if _normalise(template["template_id"]) == normalised_id:
            return _caller_safe_template(template)
    return None


def validate_gradient_template(template: Mapping[str, Any]) -> list[str]:
    if not isinstance(template, Mapping):
        return ["gradient template must be a mapping"]

    errors: list[str] = []

    for field in REQUIRED_TEMPLATE_FIELDS:
        if field not in template:
            errors.append(f"{field} is required")

    for field in LIST_TEMPLATE_FIELDS:
        if field in template and not isinstance(template.get(field), list):
            errors.append(f"{field} must be a list")

    if "research_mode_required" in template and not isinstance(
        template.get("research_mode_required"), bool
    ):
        errors.append("research_mode_required must be a bool")

    maturity = template.get("minimum_evidence_maturity_default")
    if maturity is not None and maturity not in EVIDENCE_MATURITY_LEVELS:
        errors.append(
            "minimum_evidence_maturity_default must be one of "
            f"{', '.join(EVIDENCE_MATURITY_LEVELS)}; got {maturity!r}"
        )

    gradient_type = template.get("gradient_type")
    if gradient_type is not None and gradient_type not in SUPPORTED_GRADIENT_TYPES:
        errors.append(
            "gradient_type must be one of "
            f"{', '.join(SUPPORTED_GRADIENT_TYPES)}; got {gradient_type!r}"
        )

    return errors


def validate_default_gradient_templates() -> list[str]:
    errors: list[str] = []

    if len(DEFAULT_GRADIENT_TEMPLATES) != 5:
        errors.append(
            f"DEFAULT_GRADIENT_TEMPLATES must contain exactly 5 templates; got {len(DEFAULT_GRADIENT_TEMPLATES)}"
        )

    seen_template_ids: set[str] = set()
    for index, template in enumerate(DEFAULT_GRADIENT_TEMPLATES):
        template_id = (
            str(template.get("template_id"))
            if isinstance(template, Mapping) and template.get("template_id")
            else f"template_{index}"
        )

        for error in validate_gradient_template(template):
            errors.append(f"{template_id}: {error}")

        if template_id in seen_template_ids:
            errors.append(f"{template_id}: template_id must be unique")
        seen_template_ids.add(template_id)

        maturity = template.get("minimum_evidence_maturity_default")
        if maturity in {"A", "B", "C"}:
            errors.append(
                f"{template_id}: minimum_evidence_maturity_default must not be A, B or C"
            )

        if template.get("research_mode_required") is True and maturity not in {"E", "F"}:
            errors.append(
                f"{template_id}: research-mode-required templates must default to E or F"
            )

    return errors


def match_gradient_templates(
    limiting_factors: list[str],
    *,
    candidate_class: str | None = None,
    substrate_family: str | None = None,
    process_routes: list[str] | None = None,
    research_mode_enabled: bool = False,
) -> list[GradientTemplate]:
    normalised_limiting_factors = _normalised_values(limiting_factors)
    normalised_candidate_class = _normalise(candidate_class) if candidate_class else None
    normalised_substrate_family = _normalise(substrate_family) if substrate_family else None
    normalised_process_routes = (
        _normalised_values(process_routes) if process_routes is not None else None
    )

    matches: list[GradientTemplate] = []
    for template in DEFAULT_GRADIENT_TEMPLATES:
        if template["research_mode_required"] and not research_mode_enabled:
            continue

        activation_modes = _normalised_values(template["activation_failure_modes"])
        if not activation_modes.intersection(normalised_limiting_factors):
            continue

        if normalised_candidate_class is not None:
            candidate_classes = _normalised_values(template["applicable_candidate_classes"])
            if normalised_candidate_class not in candidate_classes:
                continue

        if normalised_substrate_family is not None:
            substrate_families = _normalised_values(template["applicable_substrate_families"])
            if normalised_substrate_family not in substrate_families:
                continue

        if normalised_process_routes is not None:
            allowed_routes = _normalised_values(template["allowed_process_routes"])
            if not allowed_routes.intersection(normalised_process_routes):
                continue

        matches.append(_caller_safe_template(template))

    return matches
