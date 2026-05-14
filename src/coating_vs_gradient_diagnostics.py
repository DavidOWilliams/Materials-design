from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.contracts import evidence_maturity_label
from src.gradient_templates import GradientTemplate, match_gradient_templates
from src.surface_function_model import classify_function_kind


PAIRWISE_COMPARISON_LIMIT = 12
_LOW_MATURITY = {"D", "E", "F"}
EVIDENCE_MATURITY_LEVELS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "unknown")

REQUIRED_COATING_OPTION_FIELDS: tuple[str, ...] = (
    "option_id",
    "option_name",
    "coating_family",
    "activation_failure_modes",
    "applicable_candidate_classes",
    "applicable_substrate_families",
    "expected_benefits",
    "known_risks",
    "evidence_maturity_default",
    "inspection_burden",
    "repair_burden",
    "applicability_guardrails",
)

LIST_COATING_OPTION_FIELDS: tuple[str, ...] = (
    "activation_failure_modes",
    "applicable_candidate_classes",
    "applicable_substrate_families",
    "expected_benefits",
    "known_risks",
    "applicability_guardrails",
)


class CoatingOption(TypedDict, total=False):
    option_id: str
    option_name: str
    coating_family: str
    activation_failure_modes: list[str]
    applicable_candidate_classes: list[str]
    applicable_substrate_families: list[str]
    expected_benefits: list[str]
    known_risks: list[str]
    evidence_maturity_default: str
    inspection_burden: str
    repair_burden: str
    applicability_guardrails: list[str]


class CoatingVsGradientDiagnostic(TypedDict, total=False):
    limiting_factors: list[str]
    candidate_class: str | None
    substrate_family: str | None
    process_routes: list[str]
    research_mode_enabled: bool
    coating_options_considered: list[CoatingOption]
    gradient_templates_considered: list[GradientTemplate]
    coating_option_count: int
    gradient_template_count: int
    comparison_status: str
    notes: list[str]
    warnings: list[str]


DEFAULT_COATING_OPTIONS: tuple[CoatingOption, ...] = (
    {
        "option_id": "thermal_barrier_coating",
        "option_name": "Thermal Barrier Coating",
        "coating_family": "tbc",
        "activation_failure_modes": [
            "thermal_barrier",
            "thermal_gradient",
            "surface_temperature_limit",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "coating_enabled",
        ],
        "applicable_substrate_families": [
            "nickel_alloy",
            "cobalt_alloy",
            "refractory_alloy",
        ],
        "expected_benefits": [
            "reduced substrate surface temperature",
            "mature coating reference path for hot-section comparison",
        ],
        "known_risks": [
            "coating spallation",
            "CTE mismatch",
            "inspection burden",
            "repair burden",
        ],
        "evidence_maturity_default": "B",
        "inspection_burden": "medium",
        "repair_burden": "medium",
        "applicability_guardrails": [
            "Review substrate and bond-coat compatibility.",
            "Do not treat coating maturity as certification approval.",
        ],
    },
    {
        "option_id": "environmental_barrier_coating",
        "option_name": "Environmental Barrier Coating",
        "coating_family": "ebc",
        "activation_failure_modes": [
            "oxidation",
            "steam_exposure",
            "recession",
            "water_vapour_recession",
        ],
        "applicable_candidate_classes": [
            "cmc",
            "ceramic",
            "coating_enabled",
        ],
        "applicable_substrate_families": [
            "cmc",
            "sic_sic_cmc",
            "ceramic",
        ],
        "expected_benefits": [
            "environmental protection for ceramic or CMC hot-section systems",
            "reduced recession sensitivity where evidence supports the architecture",
        ],
        "known_risks": [
            "recession",
            "coating spallation",
            "interface degradation",
            "repair burden",
        ],
        "evidence_maturity_default": "B",
        "inspection_burden": "medium",
        "repair_burden": "high",
        "applicability_guardrails": [
            "Review CMC/EBC interface evidence and recession exposure.",
            "Do not present as qualification approval without programme evidence.",
        ],
    },
    {
        "option_id": "oxidation_protection_coating",
        "option_name": "Oxidation Protection Coating",
        "coating_family": "oxidation_protection",
        "activation_failure_modes": [
            "oxidation",
            "hot_corrosion",
            "steam_exposure",
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
        "expected_benefits": [
            "surface oxidation and hot-corrosion protection",
            "reviewable coating path for oxidation-limited systems",
        ],
        "known_risks": [
            "coating spallation",
            "substrate compatibility",
            "inspection burden",
            "repair burden",
        ],
        "evidence_maturity_default": "C",
        "inspection_burden": "medium",
        "repair_burden": "medium",
        "applicability_guardrails": [
            "Check substrate compatibility and thermal-cycle exposure.",
            "Retain validation needs for the specific environment.",
        ],
    },
    {
        "option_id": "wear_resistant_coating",
        "option_name": "Wear Resistant Coating",
        "coating_family": "wear_resistant",
        "activation_failure_modes": [
            "wear",
            "sliding_contact",
            "erosion",
            "fretting",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "ceramic",
            "coating_enabled",
        ],
        "applicable_substrate_families": [
            "titanium_alloy",
            "cobalt_alloy",
            "nickel_alloy",
            "steel",
            "ceramic",
        ],
        "expected_benefits": [
            "improved surface wear resistance",
            "separable surface treatment path for wear-limited systems",
        ],
        "known_risks": [
            "cracking",
            "adhesion loss",
            "surface preparation burden",
            "repair burden",
        ],
        "evidence_maturity_default": "C",
        "inspection_burden": "medium",
        "repair_burden": "medium",
        "applicability_guardrails": [
            "Check adhesion and surface preparation sensitivity.",
            "Do not hide fatigue or repair penalties behind wear benefits.",
        ],
    },
    {
        "option_id": "bond_coat_interface_system",
        "option_name": "Bond Coat Interface System",
        "coating_family": "bond_coat_interface",
        "activation_failure_modes": [
            "coating_spallation",
            "interface_mismatch",
            "cte_mismatch",
        ],
        "applicable_candidate_classes": [
            "metallic",
            "coating_enabled",
            "hybrid",
        ],
        "applicable_substrate_families": [
            "nickel_alloy",
            "cobalt_alloy",
            "refractory_alloy",
            "ceramic",
        ],
        "expected_benefits": [
            "improved coating/substrate interface management",
            "explicit review path for thermal-expansion and adhesion concerns",
        ],
        "known_risks": [
            "CTE mismatch",
            "interdiffusion",
            "interface degradation",
            "inspection burden",
        ],
        "evidence_maturity_default": "C",
        "inspection_burden": "high",
        "repair_burden": "medium",
        "applicability_guardrails": [
            "Review interface chemistry, interdiffusion and thermal-cycle evidence.",
            "Treat as decision support rather than approval for service.",
        ],
    },
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=str)
    return [value]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _blob(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_blob(item)}" for key, item in value.items()).lower()
    if isinstance(value, (list, tuple, set)):
        return " ".join(_blob(item) for item in value).lower()
    return _text(value).lower()


def _caller_safe_option(option: Mapping[str, Any]) -> CoatingOption:
    return deepcopy(dict(option))


def _normalise(value: str) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def _normalised_values(values: list[str]) -> set[str]:
    return {_normalise(value) for value in values}


def get_coating_options() -> tuple[CoatingOption, ...]:
    return tuple(_caller_safe_option(option) for option in DEFAULT_COATING_OPTIONS)


def get_coating_option(option_id: str) -> CoatingOption | None:
    normalised_id = _normalise(option_id)
    for option in DEFAULT_COATING_OPTIONS:
        if _normalise(option["option_id"]) == normalised_id:
            return _caller_safe_option(option)
    return None


def validate_coating_option(option: Mapping[str, Any]) -> list[str]:
    if not isinstance(option, Mapping):
        return ["coating option must be a mapping"]

    errors: list[str] = []

    for field in REQUIRED_COATING_OPTION_FIELDS:
        if field not in option:
            errors.append(f"{field} is required")

    for field in LIST_COATING_OPTION_FIELDS:
        if field in option and not isinstance(option.get(field), list):
            errors.append(f"{field} must be a list")

    maturity = option.get("evidence_maturity_default")
    if maturity is not None and maturity not in EVIDENCE_MATURITY_LEVELS:
        errors.append(
            "evidence_maturity_default must be one of "
            f"{', '.join(EVIDENCE_MATURITY_LEVELS)}; got {maturity!r}"
        )

    return errors


def validate_default_coating_options() -> list[str]:
    errors: list[str] = []

    if len(DEFAULT_COATING_OPTIONS) != 5:
        errors.append(
            f"DEFAULT_COATING_OPTIONS must contain exactly 5 options; got {len(DEFAULT_COATING_OPTIONS)}"
        )

    seen_option_ids: set[str] = set()
    for index, option in enumerate(DEFAULT_COATING_OPTIONS):
        option_id = (
            str(option.get("option_id"))
            if isinstance(option, Mapping) and option.get("option_id")
            else f"option_{index}"
        )

        for error in validate_coating_option(option):
            errors.append(f"{option_id}: {error}")

        if option_id in seen_option_ids:
            errors.append(f"{option_id}: option_id must be unique")
        seen_option_ids.add(option_id)

    return errors


def match_coating_options(
    limiting_factors: list[str],
    *,
    candidate_class: str | None = None,
    substrate_family: str | None = None,
) -> list[CoatingOption]:
    normalised_limiting_factors = _normalised_values(limiting_factors)
    normalised_candidate_class = _normalise(candidate_class) if candidate_class else None
    normalised_substrate_family = _normalise(substrate_family) if substrate_family else None

    matches: list[CoatingOption] = []
    for option in DEFAULT_COATING_OPTIONS:
        activation_modes = _normalised_values(option["activation_failure_modes"])
        if not activation_modes.intersection(normalised_limiting_factors):
            continue

        if normalised_candidate_class is not None:
            candidate_classes = _normalised_values(option["applicable_candidate_classes"])
            if normalised_candidate_class not in candidate_classes:
                continue

        if normalised_substrate_family is not None:
            substrate_families = _normalised_values(option["applicable_substrate_families"])
            if normalised_substrate_family not in substrate_families:
                continue

        matches.append(_caller_safe_option(option))

    return matches


def _build_template_coating_vs_gradient_diagnostic(
    limiting_factors: list[str],
    *,
    candidate_class: str | None = None,
    substrate_family: str | None = None,
    process_routes: list[str] | None = None,
    research_mode_enabled: bool = False,
) -> CoatingVsGradientDiagnostic:
    copied_limiting_factors = list(limiting_factors)
    copied_process_routes = list(process_routes) if process_routes is not None else []

    coating_options = match_coating_options(
        copied_limiting_factors,
        candidate_class=candidate_class,
        substrate_family=substrate_family,
    )
    gradient_templates = match_gradient_templates(
        copied_limiting_factors,
        candidate_class=candidate_class,
        substrate_family=substrate_family,
        process_routes=copied_process_routes if process_routes is not None else None,
        research_mode_enabled=research_mode_enabled,
    )

    if not copied_limiting_factors:
        comparison_status = "no_surface_driver_found"
    elif coating_options and gradient_templates:
        comparison_status = "coating_and_gradient_options_available"
    elif coating_options:
        comparison_status = "coating_options_only"
    elif gradient_templates:
        comparison_status = "gradient_templates_only"
    else:
        comparison_status = "no_options_after_filters"

    notes = [
        "Diagnostic only: coating options and spatial-gradient templates are alternatives for review.",
        "No score, rank, optimisation move or winner is selected.",
    ]
    warnings: list[str] = []
    if research_mode_enabled:
        warnings.append("Research-mode gradient templates remain exploratory and require gated review.")
    if gradient_templates:
        warnings.append(
            "Gradient alternatives require feasibility, inspection, repair and maturity review."
        )
    if coating_options:
        warnings.append(
            "Coating options require substrate/interface, inspection and repair review."
        )

    return {
        "limiting_factors": copied_limiting_factors,
        "candidate_class": candidate_class,
        "substrate_family": substrate_family,
        "process_routes": copied_process_routes,
        "research_mode_enabled": research_mode_enabled,
        "coating_options_considered": coating_options,
        "gradient_templates_considered": gradient_templates,
        "coating_option_count": len(coating_options),
        "gradient_template_count": len(gradient_templates),
        "comparison_status": comparison_status,
        "notes": notes,
        "warnings": warnings,
    }


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _evidence(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(candidate.get("evidence_package") or candidate.get("evidence"))


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _evidence(candidate)
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _source_type(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("source_type") or candidate.get("source_label"), "unknown")


def _interface_types(candidate: Mapping[str, Any]) -> list[str]:
    return [
        _text(_mapping(interface).get("interface_type"), "unknown_interface")
        for interface in _as_list(candidate.get("interfaces"))
        if _mapping(interface)
    ]


def is_coating_enabled_candidate(candidate: Mapping[str, Any]) -> bool:
    return _candidate_class(candidate) == "coating_enabled" or _architecture(candidate) == "substrate_plus_coating"


def is_spatial_gradient_candidate(candidate: Mapping[str, Any]) -> bool:
    return _candidate_class(candidate) == "spatially_graded_am" or _architecture(candidate) == "spatial_gradient"


def classify_surface_function(candidate: Mapping[str, Any]) -> list[str]:
    profile = _mapping(candidate.get("surface_function_profile"))
    if profile:
        function_ids = [
            _text(item.get("function_id"))
            for item in _as_list(profile.get("surface_functions"))
            if isinstance(item, Mapping) and _text(item.get("function_id"))
        ]
        if function_ids:
            return function_ids
    text = _blob(
        {
            "candidate_id": candidate.get("candidate_id"),
            "system_name": candidate.get("system_name") or candidate.get("name"),
            "coating": candidate.get("coating_or_surface_system") or candidate.get("coating_system"),
            "gradient": candidate.get("gradient_architecture"),
            "route_risks": candidate.get("route_risks"),
            "route_benefits": candidate.get("route_benefits"),
            "process_route_details": candidate.get("process_route_details"),
        }
    )
    tags: list[str] = []

    def add(tag: str) -> None:
        if tag not in tags:
            tags.append(tag)

    if any(term in text for term in ("tbc", "thermal barrier", "thermal protection", "thermal-margin")):
        add("thermal_barrier")
    if any(term in text for term in ("ebc", "environmental barrier", "steam", "recession")):
        add("environmental_barrier")
    if any(term in text for term in ("oxidation", "oxidation-resistant", "corrosion")):
        add("oxidation_resistance")
    if "wear" in text or "fretting" in text:
        add("wear_resistance")
    if "erosion" in text:
        add("erosion_resistance")
    if "hard surface" in text or ("hard" in text and "surface" in text):
        add("hard_surface")
    if any(term in text for term in ("transition", "gradient", "cte", "mismatch", "interface")):
        add("transition_zone_management")
    if not tags:
        add("unknown_surface_function")
    return tags


def _coating_summary(candidate: Mapping[str, Any]) -> str:
    coating = _mapping(
        candidate.get("coating_or_surface_system")
        or candidate.get("coating_system")
        or candidate.get("environmental_barrier_coating")
    )
    if not coating:
        return ""
    return _text(
        coating.get("coating_type")
        or coating.get("coating_name")
        or coating.get("name"),
        "coating or surface system",
    )


def _gradient_summary(candidate: Mapping[str, Any]) -> str:
    gradient = _mapping(candidate.get("gradient_architecture"))
    if not gradient:
        return ""
    gradient_types = [_text(item) for item in _as_list(gradient.get("gradient_types")) if _text(item)]
    return ", ".join(gradient_types) if gradient_types else _text(gradient.get("notes"), "gradient architecture")


def build_surface_protection_profile(candidate: Mapping[str, Any]) -> dict[str, Any]:
    evidence = _evidence(candidate)
    maturity = _evidence_maturity(candidate)
    details = _mapping(candidate.get("process_route_details"))
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))
    surface_function_profile = _mapping(candidate.get("surface_function_profile"))
    surface_functions = classify_surface_function(candidate)
    primary_service_functions = [
        _text(item)
        for item in _as_list(surface_function_profile.get("primary_service_functions"))
        if _text(item)
    ] or [
        function_id
        for function_id in surface_functions
        if classify_function_kind(function_id) == "primary_service_function"
    ]
    secondary_service_functions = [
        _text(item)
        for item in _as_list(surface_function_profile.get("secondary_service_functions"))
        if _text(item)
    ] or [
        function_id
        for function_id in surface_functions
        if classify_function_kind(function_id) == "secondary_service_function"
    ]
    support_considerations = [
        _text(item)
        for item in _as_list(surface_function_profile.get("support_or_lifecycle_considerations"))
        if _text(item)
    ] or [
        function_id
        for function_id in surface_functions
        if classify_function_kind(function_id) == "support_or_lifecycle_consideration"
    ]
    risk_considerations = [
        _text(item)
        for item in _as_list(surface_function_profile.get("risk_or_interface_considerations"))
        if _text(item)
    ] or [
        function_id
        for function_id in surface_functions
        if classify_function_kind(function_id) == "risk_or_interface_consideration"
    ]
    return {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "evidence_maturity": maturity,
        "evidence_label": _text(evidence.get("maturity_label"), evidence_maturity_label(maturity)),
        "source_type": _source_type(candidate),
        "surface_functions": surface_functions,
        "primary_surface_functions": list(_as_list(surface_function_profile.get("primary_surface_functions"))),
        "secondary_surface_functions": list(_as_list(surface_function_profile.get("secondary_surface_functions"))),
        "primary_service_functions": primary_service_functions,
        "secondary_service_functions": secondary_service_functions,
        "support_or_lifecycle_considerations": support_considerations,
        "risk_or_interface_considerations": risk_considerations,
        "coating_or_surface_summary": _coating_summary(candidate),
        "gradient_summary": _gradient_summary(candidate),
        "interface_types": _interface_types(candidate),
        "process_route_template_id": _text(candidate.get("process_route_template_id"), "unknown_route"),
        "process_family": _text(details.get("process_family"), "unknown"),
        "inspection_burden": _text(inspection.get("inspection_burden"), "unknown"),
        "repairability_level": _text(repairability.get("repairability_level"), "unknown"),
        "qualification_burden": _text(qualification.get("qualification_burden"), "unknown"),
        "route_risks": [_text(item) for item in _as_list(candidate.get("route_risks")) if _text(item)],
        "route_benefits": [_text(item) for item in _as_list(candidate.get("route_benefits")) if _text(item)],
        "validation_gaps": [_text(item) for item in _as_list(candidate.get("route_validation_gaps")) if _text(item)],
        "generated_candidate_flag": candidate.get("generated_candidate_flag") is True,
        "research_mode_flag": candidate.get("research_mode_flag") is True,
    }


def _contrast(label: str, coating_value: Any, gradient_value: Any) -> str:
    return f"{label}: coating={_text(coating_value, 'unknown')}; gradient={_text(gradient_value, 'unknown')}."


def _contains_any(values: Sequence[Any], *terms: str) -> bool:
    text = _blob(values)
    return any(term in text for term in terms)


def _profile_strengths(profile: Mapping[str, Any], *, gradient: bool) -> list[str]:
    strengths: list[str] = []
    maturity = _text(profile.get("evidence_maturity"))
    functions = set(_as_list(profile.get("primary_service_functions"))) | set(
        _as_list(profile.get("secondary_service_functions"))
    )
    benefits = _as_list(profile.get("route_benefits"))
    if maturity in {"A", "B", "C"}:
        strengths.append(f"evidence maturity {maturity} is comparatively visible")
    if "thermal_barrier" in functions:
        strengths.append("thermal-barrier function is explicit")
    if "environmental_barrier" in functions or "oxidation_resistance" in functions:
        strengths.append("environmental or oxidation-protection function is explicit")
    if "wear_resistance" in functions or "hard_surface" in functions:
        strengths.append("wear or hard-surface function is explicit")
    if gradient and "transition_zone_management" in functions:
        strengths.append("transition-management intent is explicit")
    if benefits:
        strengths.extend(_text(item) for item in benefits[:2])
    return list(dict.fromkeys(strengths))[:5]


def _profile_risks(profile: Mapping[str, Any], *, gradient: bool) -> list[str]:
    risks = [_text(item) for item in _as_list(profile.get("route_risks")) if _text(item)]
    if profile.get("inspection_burden") == "high":
        risks.append("high inspection burden")
    if profile.get("repairability_level") in {"limited", "poor"}:
        risks.append(f"{profile.get('repairability_level')} repairability")
    if profile.get("qualification_burden") in {"high", "very_high"}:
        risks.append(f"{profile.get('qualification_burden')} qualification burden")
    if profile.get("evidence_maturity") in _LOW_MATURITY:
        risks.append(f"exploratory evidence maturity {profile.get('evidence_maturity')}")
    if gradient:
        risks.append("gradient transition-zone and process-window assumptions require validation")
    elif profile.get("interface_types"):
        risks.append("discrete coating or substrate interface requires validation")
    return list(dict.fromkeys(risks))[:6]


def compare_surface_profiles(
    coating_profile: Mapping[str, Any],
    gradient_profile: Mapping[str, Any],
) -> dict[str, Any]:
    coating_functions = set(_as_list(coating_profile.get("surface_functions")))
    gradient_functions = set(_as_list(gradient_profile.get("surface_functions")))
    coating_primary = set(_as_list(coating_profile.get("primary_service_functions")))
    gradient_primary = set(_as_list(gradient_profile.get("primary_service_functions")))
    coating_secondary = set(_as_list(coating_profile.get("secondary_service_functions")))
    gradient_secondary = set(_as_list(gradient_profile.get("secondary_service_functions")))
    coating_support = set(_as_list(coating_profile.get("support_or_lifecycle_considerations")))
    gradient_support = set(_as_list(gradient_profile.get("support_or_lifecycle_considerations")))
    coating_risk_considerations = set(_as_list(coating_profile.get("risk_or_interface_considerations")))
    gradient_risk_considerations = set(_as_list(gradient_profile.get("risk_or_interface_considerations")))
    shared = sorted(coating_functions & gradient_functions)
    shared_primary = sorted(coating_primary & gradient_primary)
    shared_secondary = sorted(coating_secondary & gradient_secondary)
    shared_support = sorted(coating_support & gradient_support)
    shared_risk_considerations = sorted(coating_risk_considerations & gradient_risk_considerations)
    coating_only = sorted(coating_functions - gradient_functions)
    gradient_only = sorted(gradient_functions - coating_functions)
    coating_only_primary = sorted(coating_primary - gradient_primary)
    gradient_only_primary = sorted(gradient_primary - coating_primary)
    support_or_risk_overlap = bool(shared_support or shared_risk_considerations)
    if not coating_functions or not gradient_functions or coating_functions == {"unknown_surface_function"} or gradient_functions == {"unknown_surface_function"}:
        overlap_status = "unknown_overlap"
    elif shared_primary:
        overlap_status = "strong_primary_overlap" if len(shared_primary) >= 1 else "partial_primary_overlap"
    elif shared_secondary or (coating_primary & gradient_secondary) or (gradient_primary & coating_secondary):
        overlap_status = "partial_primary_overlap"
    elif support_or_risk_overlap:
        overlap_status = "support_only_overlap"
    else:
        overlap_status = "limited_overlap"
    coating_risks = _profile_risks(coating_profile, gradient=False)
    gradient_risks = _profile_risks(gradient_profile, gradient=True)
    shared_risks = sorted(set(coating_risks) & set(gradient_risks))
    notes = [
        "Comparison is diagnostic only; no score, rank or winner is produced.",
        "No winner selected.",
    ]
    if not shared:
        notes.append("Surface-function overlap is limited; comparison is retained for architecture visibility.")
    if _contains_any(coating_risks, "interface", "spallation", "mismatch"):
        notes.append("Discrete coating/interface risks remain visible for the coating-enabled system.")
    if _contains_any(gradient_risks, "transition", "process-window", "inspect"):
        notes.append("Gradient transition-zone, process-window and inspectability risks remain visible.")

    return {
        "coating_candidate_id": _text(coating_profile.get("candidate_id"), "unknown_coating"),
        "gradient_candidate_id": _text(gradient_profile.get("candidate_id"), "unknown_gradient"),
        "shared_surface_functions": shared,
        "shared_primary_service_functions": shared_primary,
        "shared_secondary_service_functions": shared_secondary,
        "shared_support_considerations": shared_support,
        "shared_risk_considerations": shared_risk_considerations,
        "coating_only_surface_functions": coating_only,
        "gradient_only_surface_functions": gradient_only,
        "coating_only_primary_service_functions": coating_only_primary,
        "gradient_only_primary_service_functions": gradient_only_primary,
        "functional_overlap_status": overlap_status,
        "coating_strengths": _profile_strengths(coating_profile, gradient=False),
        "gradient_strengths": _profile_strengths(gradient_profile, gradient=True),
        "coating_risks": coating_risks,
        "gradient_risks": gradient_risks,
        "shared_risks": shared_risks,
        "evidence_maturity_contrast": _contrast(
            "Evidence maturity",
            coating_profile.get("evidence_maturity"),
            gradient_profile.get("evidence_maturity"),
        ),
        "inspection_contrast": _contrast(
            "Inspection burden",
            coating_profile.get("inspection_burden"),
            gradient_profile.get("inspection_burden"),
        ),
        "repairability_contrast": _contrast(
            "Repairability",
            coating_profile.get("repairability_level"),
            gradient_profile.get("repairability_level"),
        ),
        "qualification_contrast": _contrast(
            "Qualification burden",
            coating_profile.get("qualification_burden"),
            gradient_profile.get("qualification_burden"),
        ),
        "interface_contrast": _contrast(
            "Interfaces",
            ", ".join(_as_list(coating_profile.get("interface_types"))) or "none visible",
            ", ".join(_as_list(gradient_profile.get("interface_types"))) or "none visible",
        ),
        "process_route_contrast": _contrast(
            "Process route",
            coating_profile.get("process_route_template_id"),
            gradient_profile.get("process_route_template_id"),
        ),
        "validation_gap_contrast": _contrast(
            "Validation gaps",
            "; ".join(_as_list(coating_profile.get("validation_gaps"))[:2]) or "none visible",
            "; ".join(_as_list(gradient_profile.get("validation_gaps"))[:2]) or "none visible",
        ),
        "diagnostic_notes": notes,
        "winner": None,
        "decision_status": "comparison_only_no_winner",
    }


def _common_items(profiles: Sequence[Mapping[str, Any]], field: str, limit: int = 6) -> list[str]:
    counter = Counter(
        _text(item)
        for profile in profiles
        for item in _as_list(profile.get(field))
        if _text(item)
    )
    return [item for item, _ in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))[:limit]]


def _observation_counts(profiles: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(_text(profile.get(field), "unknown") for profile in profiles).items()))


def _build_pairwise(coating_profiles: list[Mapping[str, Any]], gradient_profiles: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    pairs: list[tuple[int, str, str, Mapping[str, Any], Mapping[str, Any]]] = []
    for coating in coating_profiles:
        coating_primary = set(_as_list(coating.get("primary_service_functions")))
        coating_secondary = set(_as_list(coating.get("secondary_service_functions")))
        coating_support = set(_as_list(coating.get("support_or_lifecycle_considerations"))) | set(
            _as_list(coating.get("risk_or_interface_considerations"))
        )
        for gradient in gradient_profiles:
            shared_primary = coating_primary & set(_as_list(gradient.get("primary_service_functions")))
            cross_service = (coating_primary & set(_as_list(gradient.get("secondary_service_functions")))) | (
                set(_as_list(gradient.get("primary_service_functions"))) & coating_secondary
            )
            support_overlap = coating_support & (
                set(_as_list(gradient.get("support_or_lifecycle_considerations")))
                | set(_as_list(gradient.get("risk_or_interface_considerations")))
            )
            priority = 0 if shared_primary else 1 if cross_service else 2 if support_overlap else 3
            pairs.append(
                (
                    priority,
                    _text(coating.get("candidate_id")),
                    _text(gradient.get("candidate_id")),
                    coating,
                    gradient,
                )
            )
    pairs.sort(key=lambda item: (item[0], item[1], item[2]))
    return [
        compare_surface_profiles(coating, gradient)
        for _, _, _, coating, gradient in pairs[:PAIRWISE_COMPARISON_LIMIT]
    ]


def _build_package_coating_vs_gradient_diagnostic(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    design_space = _mapping(package.get("design_space"))
    coating_candidates = [candidate for candidate in candidates if is_coating_enabled_candidate(candidate)]
    gradient_candidates = [candidate for candidate in candidates if is_spatial_gradient_candidate(candidate)]
    coating_profiles = [build_surface_protection_profile(candidate) for candidate in coating_candidates]
    gradient_profiles = [build_surface_protection_profile(candidate) for candidate in gradient_candidates]
    comparison_required = (
        design_space.get("coating_vs_gradient_comparison_required") is True
        or (bool(coating_profiles) and bool(gradient_profiles))
    )
    pairwise = _build_pairwise(coating_profiles, gradient_profiles) if coating_profiles and gradient_profiles else []
    coating_risks = _common_items([{"items": _profile_risks(profile, gradient=False)} for profile in coating_profiles], "items")
    gradient_risks = _common_items([{"items": _profile_risks(profile, gradient=True)} for profile in gradient_profiles], "items")
    shared_surface_functions = sorted(
        set(_common_items(coating_profiles, "surface_functions"))
        & set(_common_items(gradient_profiles, "surface_functions"))
    )
    shared_primary_functions = sorted(
        set(_common_items(coating_profiles, "primary_service_functions"))
        & set(_common_items(gradient_profiles, "primary_service_functions"))
    )
    shared_support_considerations = sorted(
        (
            set(_common_items(coating_profiles, "support_or_lifecycle_considerations"))
            | set(_common_items(coating_profiles, "risk_or_interface_considerations"))
        )
        & (
            set(_common_items(gradient_profiles, "support_or_lifecycle_considerations"))
            | set(_common_items(gradient_profiles, "risk_or_interface_considerations"))
        )
    )

    warnings: list[str] = []
    summary_notes = [
        "Diagnostic only; no winner, score, ranking or filtering is produced.",
        "Pairwise comparisons are capped for readability.",
    ]
    if comparison_required and not coating_profiles:
        warnings.append("Coating-vs-gradient comparison is required, but no coating-enabled candidates are visible.")
    if comparison_required and not gradient_profiles:
        warnings.append("Coating-vs-gradient comparison is required, but no spatial-gradient candidates are visible.")
    if gradient_profiles and all(profile.get("evidence_maturity") in _LOW_MATURITY for profile in gradient_profiles):
        warnings.append("All spatial-gradient candidates are D/E/F exploratory maturity.")
    if any(profile.get("inspection_burden") == "high" or profile.get("qualification_burden") in {"high", "very_high"} for profile in coating_profiles):
        warnings.append("One or more coating-enabled candidates have high inspection or qualification burden.")
    if any(
        profile.get("inspection_burden") == "high"
        or profile.get("repairability_level") in {"limited", "poor"}
        or profile.get("qualification_burden") == "very_high"
        for profile in gradient_profiles
    ):
        warnings.append("One or more spatial-gradient candidates have high inspection, limited/poor repairability or very high qualification burden.")
    if not shared_surface_functions and coating_profiles and gradient_profiles:
        summary_notes.append("No shared surface-function themes were detected; representative comparisons are still shown.")

    return {
        "diagnostic_status": "comparison_only_no_winner",
        "comparison_required": comparison_required,
        "coating_enabled_candidate_ids": [_text(profile.get("candidate_id")) for profile in coating_profiles],
        "spatial_gradient_candidate_ids": [_text(profile.get("candidate_id")) for profile in gradient_profiles],
        "coating_profiles": coating_profiles,
        "gradient_profiles": gradient_profiles,
        "pairwise_comparisons": pairwise,
        "shared_surface_function_themes": shared_surface_functions,
        "shared_primary_service_functions": shared_primary_functions,
        "shared_support_considerations": shared_support_considerations,
        "coating_common_strengths": _common_items(
            [{"items": _profile_strengths(profile, gradient=False)} for profile in coating_profiles],
            "items",
        ),
        "gradient_common_strengths": _common_items(
            [{"items": _profile_strengths(profile, gradient=True)} for profile in gradient_profiles],
            "items",
        ),
        "coating_common_risks": coating_risks,
        "gradient_common_risks": gradient_risks,
        "evidence_maturity_observations": {
            "coating": _observation_counts(coating_profiles, "evidence_maturity"),
            "gradient": _observation_counts(gradient_profiles, "evidence_maturity"),
        },
        "inspection_repair_observations": {
            "inspection_burden": {
                "coating": _observation_counts(coating_profiles, "inspection_burden"),
                "gradient": _observation_counts(gradient_profiles, "inspection_burden"),
            },
            "repairability": {
                "coating": _observation_counts(coating_profiles, "repairability_level"),
                "gradient": _observation_counts(gradient_profiles, "repairability_level"),
            },
        },
        "qualification_observations": {
            "coating": _observation_counts(coating_profiles, "qualification_burden"),
            "gradient": _observation_counts(gradient_profiles, "qualification_burden"),
        },
        "validation_gap_observations": {
            "coating": _common_items(coating_profiles, "validation_gaps"),
            "gradient": _common_items(gradient_profiles, "validation_gaps"),
        },
        "summary_notes": summary_notes,
        "warnings": warnings,
    }


def build_coating_vs_gradient_diagnostic(
    limiting_factors: list[str] | Mapping[str, Any],
    *,
    candidate_class: str | None = None,
    substrate_family: str | None = None,
    process_routes: list[str] | None = None,
    research_mode_enabled: bool = False,
) -> dict[str, Any]:
    if isinstance(limiting_factors, Mapping):
        return _build_package_coating_vs_gradient_diagnostic(limiting_factors)

    return _build_template_coating_vs_gradient_diagnostic(
        limiting_factors,
        candidate_class=candidate_class,
        substrate_family=substrate_family,
        process_routes=process_routes,
        research_mode_enabled=research_mode_enabled,
    )


def attach_coating_vs_gradient_diagnostic(package: Mapping[str, Any]) -> dict[str, Any]:
    output = dict(package)
    diagnostic = build_coating_vs_gradient_diagnostic(package)
    output["coating_vs_gradient_diagnostic"] = diagnostic
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    for warning in diagnostic["warnings"]:
        if warning not in warnings:
            warnings.append(warning)
    output["warnings"] = warnings
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics["coating_vs_gradient_diagnostic_attached"] = True
    output["diagnostics"] = diagnostics
    return output
