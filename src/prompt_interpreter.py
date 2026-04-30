from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Tuple

from src.requirement_schema import RequirementSchema


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _bump(mapping: Dict[str, float], key: str, value: float) -> None:
    mapping[key] = max(float(mapping.get(key, 0.0)), float(value))


def _temperature_band(temperature_c: int) -> str:
    if temperature_c >= 1000:
        return "extreme_temperature"
    if temperature_c >= 800:
        return "hot_section"
    if temperature_c >= 600:
        return "elevated_temperature"
    return "moderate_temperature"


def _has_extreme_temperature_language(prompt: str) -> bool:
    """Return True for language that should make refractory concepts the primary review family.

    This is deliberately broader than the literal word "refractory" because engineers
    often express the requirement as service temperature, e.g. "above 1000°C".
    """
    return (
        _contains_any(
            prompt,
            [
                "extreme temperature",
                "extreme-temperature",
                "very high temperature",
                "very-high-temperature",
                "ultra high temperature",
                "ultra-high temperature",
                "ultra-high-temperature",
                "above 1000",
                ">1000",
                "1000°",
                "1050°",
                "1100°",
                "1150°",
                "1200°",
                "specialist processing",
            ],
        )
        or bool(re.search(r"(?:above|over|>|>=)\s*1[0-2]\d{2}\s*(?:°?c|celsius)?", prompt))
    )


def _component_class(prompt: str) -> str:
    if _contains_any(prompt, ["turbine", "blade", "vane", "hot section", "combustor", "exhaust"]):
        return "hot-section component"
    if _contains_any(prompt, ["landing gear", "bracket", "fitting", "spar", "frame", "structural"]):
        return "structural component"
    if _contains_any(prompt, ["bearing", "seal", "bushing", "surface", "contact", "wear"]):
        return "tribological/contact component"
    if _contains_any(prompt, ["duct", "pipe", "manifold", "housing", "case", "casing"]):
        return "fabricated system component"
    return "unspecified aviation component"


def _normalise_prompt(prompt: str) -> str:
    return re.sub(r"\s+", " ", (prompt or "").strip().lower())


def interpret_prompt(application_prompt: str, operating_temperature: int, am_preferred: bool) -> RequirementSchema:
    """Deterministically interpret a free-text engineering prompt into a strict schema.

    This deliberately avoids direct candidate scoring. It produces an inspectable requirement
    object that later deterministic layers can validate, plan around, and explain.
    """

    prompt = _normalise_prompt(application_prompt)
    trace: List[str] = []
    ambiguities: List[str] = []
    environment_tags: List[str] = []
    load_tags: List[str] = []

    failure_modes: Dict[str, float] = {
        "creep": 0.25,
        "fatigue": 0.15,
        "fracture_toughness": 0.15,
        "oxidation": 0.15,
        "hot_corrosion": 0.10,
        "wear": 0.10,
        "erosion": 0.05,
        "thermal_fatigue": 0.10,
    }
    factor_importance: Dict[str, float] = {
        "creep": 0.25,
        "toughness": 0.20,
        "temperature": 0.25,
        "through_life_cost": 0.15,
        "sustainability": 0.15,
        "manufacturability": 0.20,
        "route_suitability": 0.20,
        "supply_risk": 0.12,
        "evidence_maturity": 0.15,
        "recipe_support": 0.15,
    }
    lifecycle = {
        "through_life_cost": 0.15,
        "sustainability": 0.15,
        "supply_risk": 0.12,
        "repairability": 0.10,
        "certification_maturity": 0.12,
    }

    hard_constraints: Dict[str, Any] = {
        "must_support_am": False,
        "must_avoid_am": False,
        "must_be_lightweight": False,
        "max_density": None,
        "family_inclusions": [],
        "family_exclusions": [],
        "process_exclusions": [],
    }
    manufacturing = {
        "preferred_routes": [],
        "disfavoured_routes": [],
        "inspection_sensitivity": "normal",
        "qualification_sensitivity": "normal",
    }

    # Temperature first, because it is explicit structured input.
    band = _temperature_band(int(operating_temperature))
    if band in {"hot_section", "extreme_temperature"}:
        _bump(failure_modes, "creep", 0.65 if operating_temperature >= 850 else 0.45)
        _bump(failure_modes, "oxidation", 0.45)
        _bump(factor_importance, "creep", 0.42)
        _bump(factor_importance, "temperature", 0.42)
        environment_tags.append("high_temperature")
        trace.append("Temperature input activated high-temperature / creep interpretation.")
    elif band == "elevated_temperature":
        _bump(factor_importance, "temperature", 0.30)
        environment_tags.append("elevated_temperature")
        trace.append("Temperature input activated elevated-temperature interpretation.")

    # Performance / failure modes.
    explicit_refractory_language = _contains_any(
        prompt,
        ["refractory", "molybdenum", "niobium", "tantalum", "tungsten"],
    )
    extreme_temperature_language = _has_extreme_temperature_language(prompt)

    if explicit_refractory_language or extreme_temperature_language or operating_temperature >= 1050:
        _bump(failure_modes, "creep", 0.82)
        _bump(failure_modes, "oxidation", 0.70)
        _bump(factor_importance, "temperature", 0.68)
        _bump(factor_importance, "creep", 0.54)
        _bump(factor_importance, "oxidation", 0.48)
        environment_tags.append("extreme_temperature_or_refractory_service")
        load_tags.append("extreme_temperature_load")
        trace.append("Prompt terms activated extreme-temperature / refractory-service interpretation.")
        # Treat explicit >1000°C / extreme-temperature language as a soft-but-strong
        # refractory inclusion. This does not make refractory a survival filter; it
        # tells the scope planner and reranker that refractory options must be reviewed.
        if "Refractory alloy concept" not in hard_constraints["family_inclusions"]:
            hard_constraints["family_inclusions"].append("Refractory alloy concept")
            trace.append("Extreme-temperature wording added refractory concepts to the material-family review set.")

    if _contains_any(prompt, ["creep", "rupture", "stress rupture", "hot section", "turbine", "blade", "vane"]):
        _bump(failure_modes, "creep", 0.85)
        _bump(factor_importance, "creep", 0.55)
        _bump(factor_importance, "temperature", 0.45)
        load_tags.append("sustained_high_temperature_load")
        trace.append("Prompt terms activated creep / hot-section priority.")

    if _contains_any(prompt, ["fatigue", "cyclic", "vibration", "alternating load", "low cycle", "high cycle"]):
        _bump(failure_modes, "fatigue", 0.75)
        _bump(factor_importance, "fatigue", 0.45)
        load_tags.append("cyclic_load")
        trace.append("Prompt terms activated fatigue priority.")

    if _contains_any(prompt, ["thermal fatigue", "thermal cycling", "start stop", "start-stop", "transient"]):
        _bump(failure_modes, "thermal_fatigue", 0.78)
        _bump(factor_importance, "thermal_fatigue", 0.45)
        load_tags.append("thermal_cycle")
        trace.append("Prompt terms activated thermal-fatigue priority.")

    if _contains_any(prompt, ["fracture", "damage tolerance", "toughness", "impact", "crack growth"]):
        _bump(failure_modes, "fracture_toughness", 0.70)
        _bump(factor_importance, "toughness", 0.45)
        trace.append("Prompt terms activated toughness / damage-tolerance priority.")

    if _contains_any(prompt, ["oxidation", "oxide", "scale", "environmental", "hot gas"]):
        _bump(failure_modes, "oxidation", 0.72)
        _bump(factor_importance, "oxidation", 0.42)
        environment_tags.append("oxidising_environment")
        trace.append("Prompt terms activated oxidation priority.")

    if _contains_any(prompt, ["hot corrosion", "corrosion", "sulfidation", "salt", "marine", "contaminant"]):
        _bump(failure_modes, "hot_corrosion", 0.82)
        _bump(factor_importance, "hot_corrosion", 0.50)
        environment_tags.append("hot_corrosion_or_corrosive_environment")
        trace.append("Prompt terms activated hot-corrosion priority.")

    if _contains_any(prompt, ["wear", "sliding", "abrasion", "fretting", "contact", "tribology"]):
        _bump(failure_modes, "wear", 0.80)
        _bump(factor_importance, "wear", 0.48)
        load_tags.append("contact_or_wear_load")
        trace.append("Prompt terms activated wear/contact priority.")

    if _contains_any(prompt, ["erosion", "sand", "particle", "ingestion", "rain erosion"]):
        _bump(failure_modes, "erosion", 0.65)
        _bump(factor_importance, "erosion", 0.38)
        environment_tags.append("erosive_environment")
        trace.append("Prompt terms activated erosion priority.")

    # Lightweight / lifecycle / manufacturability intent.
    if _contains_any(prompt, ["lightweight", "light weight", "low density", "weight saving", "weight reduction", "strength-to-weight", "specific strength"]):
        hard_constraints["must_be_lightweight"] = True
        hard_constraints["max_density"] = 6.0
        _bump(factor_importance, "lightweight", 0.58)
        _bump(factor_importance, "toughness", 0.32)
        trace.append("Prompt terms activated lightweight / density-sensitive selection.")

    if _contains_any(prompt, ["sustainable", "sustainability", "recycled", "low embodied", "critical material", "responsible sourcing"]):
        _bump(factor_importance, "sustainability", 0.42)
        _bump(lifecycle, "sustainability", 0.48)
        _bump(lifecycle, "supply_risk", 0.32)
        trace.append("Prompt terms activated sustainability / supply-risk emphasis.")

    if _contains_any(prompt, ["low cost", "cost", "affordable", "through life", "lifecycle", "maintenance cost"]):
        _bump(factor_importance, "through_life_cost", 0.40)
        _bump(lifecycle, "through_life_cost", 0.45)
        trace.append("Prompt terms activated through-life cost emphasis.")

    if _contains_any(prompt, ["repair", "repairable", "maintain", "maintenance", "inspectable", "field repair"]):
        _bump(factor_importance, "repairability", 0.38)
        _bump(lifecycle, "repairability", 0.45)
        manufacturing["inspection_sensitivity"] = "high"
        trace.append("Prompt terms activated repairability / inspectability emphasis.")

    if _contains_any(prompt, ["certification", "certified", "qualified", "flight critical", "safety critical", "proven", "mature"]):
        _bump(factor_importance, "certification_maturity", 0.45)
        _bump(factor_importance, "evidence_maturity", 0.35)
        _bump(lifecycle, "certification_maturity", 0.55)
        manufacturing["qualification_sensitivity"] = "high"
        trace.append("Prompt terms activated qualification / maturity emphasis.")

    # Route intent. Checkbox is a preference; text can harden it.
    if am_preferred:
        manufacturing["preferred_routes"].append("AM")
        _bump(factor_importance, "route_suitability", 0.35)
        _bump(factor_importance, "manufacturability", 0.30)
        trace.append("AM checkbox activated preferred-route suitability.")

    if _contains_any(prompt, ["additive", "am ", "lpbf", "dmls", "powder bed", "3d print", "3d-print"]):
        manufacturing["preferred_routes"].append("AM")
        _bump(factor_importance, "route_suitability", 0.45)
        _bump(factor_importance, "manufacturability", 0.35)
        trace.append("Prompt terms activated additive-manufacturing route intent.")
        if _contains_any(prompt, ["must", "required", "only"]):
            hard_constraints["must_support_am"] = True
            trace.append("Prompt wording suggests AM is a hard route requirement.")

    if _contains_any(prompt, ["conventional", "wrought", "forged", "forging", "cast", "casting", "sheet", "plate", "bar stock"]):
        manufacturing["preferred_routes"].append("conventional")
        _bump(factor_importance, "manufacturability", 0.34)
        trace.append("Prompt terms activated conventional-route intent.")
        if _contains_any(prompt, ["avoid am", "not additive", "no additive", "not 3d", "avoid powder"]):
            hard_constraints["must_avoid_am"] = True
            hard_constraints["process_exclusions"].append("AM")
            manufacturing["disfavoured_routes"].append("AM")

    # Explicit family mentions are kept as inclusions/exclusions for the planner, not direct scoring.
    family_terms: List[Tuple[str, str]] = [
        ("nickel", "Ni-based superalloy"),
        ("ni-base", "Ni-based superalloy"),
        ("cobalt", "Co-based alloy"),
        ("co-base", "Co-based alloy"),
        ("titanium", "Ti alloy"),
        ("ti alloy", "Ti alloy"),
        ("refractory", "Refractory alloy concept"),
        ("molybdenum", "Refractory alloy concept"),
        ("niobium", "Refractory alloy concept"),
        ("iron-nickel", "Fe-Ni alloy"),
        ("fe-ni", "Fe-Ni alloy"),
    ]
    for term, family in family_terms:
        if term in prompt and family not in hard_constraints["family_inclusions"]:
            hard_constraints["family_inclusions"].append(family)

    if _contains_any(prompt, ["avoid cobalt", "no cobalt", "cobalt-free", "without cobalt"]):
        hard_constraints["family_exclusions"].append("Co-based alloy")
    if _contains_any(prompt, ["avoid nickel", "no nickel", "nickel-free", "without nickel"]):
        hard_constraints["family_exclusions"].append("Ni-based superalloy")

    if not trace:
        trace.append("No strong domain trigger was found; default balanced aviation-material priorities applied.")
        ambiguities.append("Prompt contains few explicit engineering constraints; defaults may dominate.")

    if am_preferred and hard_constraints["must_avoid_am"]:
        ambiguities.append("AM checkbox conflicts with prompt language that appears to avoid additive manufacturing.")

    # Priority order is simply the ranked factor-importance map.
    priority_order = [name for name, _ in sorted(factor_importance.items(), key=lambda item: item[1], reverse=True)]
    confidence = 0.72
    if ambiguities:
        confidence -= 0.12
    if len(trace) >= 4:
        confidence += 0.08
    confidence = max(0.35, min(0.92, confidence))

    return {
        "schema_version": "requirement_schema_v1",
        "prompt_raw": application_prompt or "",
        "prompt_normalized": prompt,
        "component_context": {
            "component_class": _component_class(prompt),
            "use_case_summary": prompt[:240] if prompt else "No prompt provided.",
            "geometry_complexity": "complex" if _contains_any(prompt, ["complex", "lattice", "thin wall", "internal channel"]) else "unspecified",
            "repairability_importance": "high" if lifecycle.get("repairability", 0.0) >= 0.35 else "normal",
        },
        "operating_envelope": {
            "temperature_c": int(operating_temperature),
            "temperature_band": band,
            "environment_tags": list(dict.fromkeys(environment_tags)),
            "load_regime_tags": list(dict.fromkeys(load_tags)),
        },
        "hard_constraints": hard_constraints,
        "soft_objectives": {
            "priority_order": priority_order,
            "factor_importance": {k: round(v, 3) for k, v in factor_importance.items()},
            "tradeoff_mode": "balanced_tradeoff",
        },
        "failure_mode_priorities": {k: round(v, 3) for k, v in failure_modes.items()},
        "manufacturing_intent": {
            **manufacturing,
            "preferred_routes": list(dict.fromkeys(manufacturing["preferred_routes"])),
            "disfavoured_routes": list(dict.fromkeys(manufacturing["disfavoured_routes"])),
        },
        "lifecycle_priorities": {k: round(v, 3) for k, v in lifecycle.items()},
        "ambiguities": ambiguities,
        "interpreter_confidence": round(confidence, 2),
        "interpreter_trace": trace,
    }
