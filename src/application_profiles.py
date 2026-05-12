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


def default_application_profile():
    """Return the default Build 4 application profile."""
    return deepcopy(_DEFAULT_APPLICATION_PROFILE)
