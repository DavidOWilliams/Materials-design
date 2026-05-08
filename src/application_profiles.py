from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from typing import Any


PROFILE_IDS = (
    "hot_section_thermal_cycling_oxidation",
    "cmc_ebc_steam_oxidation_component",
    "erosion_wear_surface_component",
    "repairable_coated_metallic_component",
    "exploratory_graded_surface_architecture",
)

_REQUIRED_FIELDS = {
    "profile_id",
    "display_name",
    "description",
    "service_environment",
    "required_primary_service_functions",
    "desired_secondary_service_functions",
    "disallowed_or_caution_functions",
    "thermal_exposure_level",
    "thermal_cycling_severity",
    "oxidation_or_steam_exposure",
    "erosion_or_wear_exposure",
    "structural_load_sensitivity",
    "weight_sensitivity",
    "inspection_access",
    "repairability_expectation",
    "certification_sensitivity",
    "minimum_evidence_maturity_for_engineering_use",
    "allow_exploratory_concepts",
    "allow_research_only_concepts",
    "profile_notes",
    "not_a_selection_request",
}
_EXPOSURE_LEVELS = {"low", "medium", "high", "very_high", "unknown"}
_CYCLING_LEVELS = {"low", "medium", "high", "unknown"}
_ENV_LEVELS = {"none", "low", "medium", "high", "unknown"}
_SENSITIVITY_LEVELS = {"low", "medium", "high", "unknown"}
_INSPECTION_ACCESS = {"easy", "moderate", "difficult", "unknown"}
_REPAIRABILITY = {"replacement_ok", "repair_desired", "repair_required", "unknown"}
_CERTIFICATION = {"low", "medium", "high", "very_high"}
_MATURITY = {"A", "B", "C", "D", "E", "F"}


def _unique_sorted_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = [value]
    return sorted({str(item).strip() for item in values if str(item).strip()})


def _profile(
    *,
    profile_id: str,
    display_name: str,
    description: str,
    service_environment: str,
    required_primary_service_functions: list[str],
    desired_secondary_service_functions: list[str],
    disallowed_or_caution_functions: list[str] | None = None,
    thermal_exposure_level: str = "unknown",
    thermal_cycling_severity: str = "unknown",
    oxidation_or_steam_exposure: str = "unknown",
    erosion_or_wear_exposure: str = "unknown",
    structural_load_sensitivity: str = "unknown",
    weight_sensitivity: str = "unknown",
    inspection_access: str = "unknown",
    repairability_expectation: str = "unknown",
    certification_sensitivity: str = "high",
    minimum_evidence_maturity_for_engineering_use: str = "C",
    allow_exploratory_concepts: bool = False,
    allow_research_only_concepts: bool = False,
    profile_notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "profile_id": profile_id,
        "display_name": display_name,
        "description": description,
        "service_environment": service_environment,
        "required_primary_service_functions": required_primary_service_functions,
        "desired_secondary_service_functions": desired_secondary_service_functions,
        "disallowed_or_caution_functions": disallowed_or_caution_functions or [],
        "thermal_exposure_level": thermal_exposure_level,
        "thermal_cycling_severity": thermal_cycling_severity,
        "oxidation_or_steam_exposure": oxidation_or_steam_exposure,
        "erosion_or_wear_exposure": erosion_or_wear_exposure,
        "structural_load_sensitivity": structural_load_sensitivity,
        "weight_sensitivity": weight_sensitivity,
        "inspection_access": inspection_access,
        "repairability_expectation": repairability_expectation,
        "certification_sensitivity": certification_sensitivity,
        "minimum_evidence_maturity_for_engineering_use": minimum_evidence_maturity_for_engineering_use,
        "allow_exploratory_concepts": allow_exploratory_concepts,
        "allow_research_only_concepts": allow_research_only_concepts,
        "profile_notes": profile_notes or [],
        "not_a_selection_request": True,
    }


def build_default_application_profiles() -> dict[str, dict[str, Any]]:
    profiles = {
        "hot_section_thermal_cycling_oxidation": _profile(
            profile_id="hot_section_thermal_cycling_oxidation",
            display_name="Hot-section thermal cycling and oxidation",
            description="A high-temperature aviation hot-section profile driven by thermal barrier needs, oxidation resistance, thermal cycling and certification sensitivity.",
            service_environment="very high temperature aviation hot-section environment with oxidation/steam exposure and thermal cycling.",
            required_primary_service_functions=["thermal_barrier", "oxidation_resistance"],
            desired_secondary_service_functions=["thermal_cycling_tolerance"],
            disallowed_or_caution_functions=["unknown_surface_function"],
            thermal_exposure_level="very_high",
            thermal_cycling_severity="high",
            oxidation_or_steam_exposure="high",
            erosion_or_wear_exposure="medium",
            structural_load_sensitivity="high",
            weight_sensitivity="high",
            inspection_access="difficult",
            repairability_expectation="repair_desired",
            certification_sensitivity="very_high",
            minimum_evidence_maturity_for_engineering_use="C",
            allow_exploratory_concepts=False,
            allow_research_only_concepts=False,
            profile_notes=["Default Build 4 profile; not a final material selection request."],
        ),
        "cmc_ebc_steam_oxidation_component": _profile(
            profile_id="cmc_ebc_steam_oxidation_component",
            display_name="CMC/EBC steam oxidation component",
            description="A silicon-based CMC/EBC aviation profile where steam recession, environmental barrier behaviour and oxidation resistance are primary.",
            service_environment="high-temperature oxidizing and steam-containing aviation environment.",
            required_primary_service_functions=[
                "environmental_barrier",
                "oxidation_resistance",
                "steam_recession_resistance",
            ],
            desired_secondary_service_functions=["thermal_cycling_tolerance"],
            thermal_exposure_level="high",
            thermal_cycling_severity="high",
            oxidation_or_steam_exposure="high",
            erosion_or_wear_exposure="medium",
            structural_load_sensitivity="high",
            weight_sensitivity="high",
            inspection_access="difficult",
            repairability_expectation="repair_desired",
            certification_sensitivity="very_high",
            minimum_evidence_maturity_for_engineering_use="C",
        ),
        "erosion_wear_surface_component": _profile(
            profile_id="erosion_wear_surface_component",
            display_name="Erosion and wear surface component",
            description="A surface-damage profile emphasizing wear and erosion resistance with repair and qualification caveats.",
            service_environment="aviation component surface exposed to wear, erosion, fretting or contact.",
            required_primary_service_functions=["wear_resistance", "erosion_resistance"],
            desired_secondary_service_functions=["thermal_cycling_tolerance"],
            thermal_exposure_level="medium",
            thermal_cycling_severity="medium",
            oxidation_or_steam_exposure="medium",
            erosion_or_wear_exposure="high",
            structural_load_sensitivity="high",
            weight_sensitivity="medium",
            inspection_access="moderate",
            repairability_expectation="repair_desired",
            certification_sensitivity="high",
            minimum_evidence_maturity_for_engineering_use="C",
        ),
        "repairable_coated_metallic_component": _profile(
            profile_id="repairable_coated_metallic_component",
            display_name="Repairable coated metallic component",
            description="A metallic substrate plus surface protection profile emphasizing oxidation resistance and repairability.",
            service_environment="coated metallic aviation component with oxidation exposure and repair requirements.",
            required_primary_service_functions=["oxidation_resistance"],
            desired_secondary_service_functions=["thermal_cycling_tolerance"],
            thermal_exposure_level="high",
            thermal_cycling_severity="high",
            oxidation_or_steam_exposure="high",
            erosion_or_wear_exposure="medium",
            structural_load_sensitivity="high",
            weight_sensitivity="medium",
            inspection_access="moderate",
            repairability_expectation="repair_required",
            certification_sensitivity="high",
            minimum_evidence_maturity_for_engineering_use="C",
        ),
        "exploratory_graded_surface_architecture": _profile(
            profile_id="exploratory_graded_surface_architecture",
            display_name="Exploratory graded surface architecture",
            description="An exploration-only profile for graded surface architectures, not an engineering selection profile.",
            service_environment="exploratory graded surface concept space with difficult inspection and validation needs.",
            required_primary_service_functions=["oxidation_resistance", "wear_resistance"],
            desired_secondary_service_functions=["transition_zone_management"],
            thermal_exposure_level="high",
            thermal_cycling_severity="unknown",
            oxidation_or_steam_exposure="high",
            erosion_or_wear_exposure="high",
            structural_load_sensitivity="unknown",
            weight_sensitivity="medium",
            inspection_access="difficult",
            repairability_expectation="repair_desired",
            certification_sensitivity="high",
            minimum_evidence_maturity_for_engineering_use="E",
            allow_exploratory_concepts=True,
            allow_research_only_concepts=True,
            profile_notes=[
                "Exploration-only profile; retaining research concepts here is not engineering selection.",
            ],
        ),
    }
    return {profile_id: normalise_application_profile(profile) for profile_id, profile in profiles.items()}


def get_default_application_profile(profile_id: str = "hot_section_thermal_cycling_oxidation") -> dict[str, Any]:
    profiles = build_default_application_profiles()
    if profile_id not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(f"Unknown application profile_id '{profile_id}'. Available profile IDs: {available}.")
    return deepcopy(profiles[profile_id])


def validate_application_profile(profile: Mapping[str, Any]) -> list[str]:
    if not isinstance(profile, Mapping):
        raise TypeError("Application profile must be a mapping.")
    warnings: list[str] = []
    missing = sorted(field for field in _REQUIRED_FIELDS if field not in profile)
    if missing:
        warnings.append("Missing required application profile fields: " + ", ".join(missing) + ".")
    if not _unique_sorted_strings(profile.get("required_primary_service_functions")):
        warnings.append("required_primary_service_functions must not be empty.")
    enum_checks = (
        ("thermal_exposure_level", _EXPOSURE_LEVELS),
        ("thermal_cycling_severity", _CYCLING_LEVELS),
        ("oxidation_or_steam_exposure", _ENV_LEVELS),
        ("erosion_or_wear_exposure", _ENV_LEVELS),
        ("structural_load_sensitivity", _SENSITIVITY_LEVELS),
        ("weight_sensitivity", _SENSITIVITY_LEVELS),
        ("inspection_access", _INSPECTION_ACCESS),
        ("repairability_expectation", _REPAIRABILITY),
        ("certification_sensitivity", _CERTIFICATION),
    )
    for field, allowed in enum_checks:
        value = str(profile.get(field, "unknown")).strip()
        if value not in allowed:
            warnings.append(f"{field} has invalid value '{value}'.")
    maturity = str(profile.get("minimum_evidence_maturity_for_engineering_use", "")).strip().upper()
    if maturity not in _MATURITY:
        warnings.append("minimum_evidence_maturity_for_engineering_use must be A/B/C/D/E/F.")
    for field in ("allow_exploratory_concepts", "allow_research_only_concepts"):
        if not isinstance(profile.get(field), bool):
            warnings.append(f"{field} must be boolean.")
    return warnings


def normalise_application_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(profile, Mapping):
        raise TypeError("Application profile must be a mapping.")
    output = deepcopy(dict(profile))
    output["profile_id"] = str(output.get("profile_id", "unknown_profile")).strip() or "unknown_profile"
    output["display_name"] = str(output.get("display_name", output["profile_id"])).strip() or output["profile_id"]
    output["description"] = str(output.get("description", "")).strip()
    output["service_environment"] = str(output.get("service_environment", "unknown")).strip() or "unknown"
    for field in (
        "required_primary_service_functions",
        "desired_secondary_service_functions",
        "disallowed_or_caution_functions",
        "profile_notes",
    ):
        output[field] = _unique_sorted_strings(output.get(field))
    defaults = {
        "thermal_exposure_level": "unknown",
        "thermal_cycling_severity": "unknown",
        "oxidation_or_steam_exposure": "unknown",
        "erosion_or_wear_exposure": "unknown",
        "structural_load_sensitivity": "unknown",
        "weight_sensitivity": "unknown",
        "inspection_access": "unknown",
        "repairability_expectation": "unknown",
        "certification_sensitivity": "high",
        "minimum_evidence_maturity_for_engineering_use": "C",
    }
    for field, default in defaults.items():
        output[field] = str(output.get(field, default)).strip() or default
    output["minimum_evidence_maturity_for_engineering_use"] = output[
        "minimum_evidence_maturity_for_engineering_use"
    ].upper()
    output["allow_exploratory_concepts"] = output.get("allow_exploratory_concepts") is True
    output["allow_research_only_concepts"] = output.get("allow_research_only_concepts") is True
    output["not_a_selection_request"] = True
    return output
