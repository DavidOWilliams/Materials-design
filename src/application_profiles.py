"""Default Build 4 application profile definitions."""

from copy import deepcopy


DEFAULT_APPLICATION_PROFILE_ID = "hot_section_thermal_cycling_oxidation"


_DEFAULT_APPLICATION_PROFILE = {
    "profile_id": DEFAULT_APPLICATION_PROFILE_ID,
    "profile_name": "Hot-section thermal cycling and oxidation",
    "required_primary_service_functions": [
        "oxidation_resistance",
        "thermal_barrier",
    ],
    "desired_secondary_service_functions": [
        "thermal_cycling_tolerance",
    ],
    "constraints": {
        "thermal_exposure": "very_high",
        "thermal_cycling": "high",
        "oxidation_steam_exposure": "high",
        "inspection_difficulty": "difficult",
        "repair": "desired",
        "certification_sensitivity": "very_high",
        "minimum_evidence_maturity": "C",
    },
    "assessment_boundaries": {
        "ranks_candidates": False,
        "shortlists_candidates": False,
        "validates_plan": False,
        "generates_variants": False,
        "populates_pareto_output": False,
    },
}

_APPLICATION_PROFILE_REGISTRY = {
    DEFAULT_APPLICATION_PROFILE_ID: _DEFAULT_APPLICATION_PROFILE,
}


def _available_profile_ids():
    return sorted(_APPLICATION_PROFILE_REGISTRY)


def default_application_profile():
    """Return the default Build 4 application profile."""
    return deepcopy(_DEFAULT_APPLICATION_PROFILE)


def list_application_profiles():
    """Return metadata for available Build 4 application profiles."""
    return [
        {
            "profile_id": profile["profile_id"],
            "profile_name": profile["profile_name"],
        }
        for profile in (
            _APPLICATION_PROFILE_REGISTRY[profile_id]
            for profile_id in _available_profile_ids()
        )
    ]


def get_application_profile(profile_id):
    """Return a defensive copy of a registered Build 4 application profile."""
    if profile_id not in _APPLICATION_PROFILE_REGISTRY:
        available = ", ".join(_available_profile_ids())
        raise ValueError(
            f"Unknown application profile ID '{profile_id}'. Available profile IDs: {available}."
        )
    return deepcopy(_APPLICATION_PROFILE_REGISTRY[profile_id])


def resolve_application_profile(profile_id=None):
    """Resolve an application profile ID, defaulting to the default Build 4 profile."""
    return get_application_profile(profile_id or DEFAULT_APPLICATION_PROFILE_ID)
