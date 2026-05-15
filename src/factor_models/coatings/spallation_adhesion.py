from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


_LOW_MATURITY = {"D", "E", "F"}
_COATING_CUES = (
    "coating",
    "tbc",
    "ebc",
    "thermal barrier",
    "environmental barrier",
    "bond coat",
    "bondcoat",
    "hard coating",
    "wear coating",
    "oxidation coating",
    "hot corrosion coating",
    "surface coating",
    "top coat",
    "topcoat",
    "mcraly",
    "aluminide",
    "silicide",
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


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _field_text(candidate: Mapping[str, Any]) -> str:
    fields = {
        "candidate_id": candidate.get("candidate_id"),
        "system_name": candidate.get("system_name") or candidate.get("name"),
        "summary": candidate.get("summary"),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "base_material_family": candidate.get("base_material_family"),
        "constituents": candidate.get("constituents"),
        "coating_or_surface_system": candidate.get("coating_or_surface_system"),
        "coating_system": candidate.get("coating_system"),
        "environmental_barrier_coating": candidate.get("environmental_barrier_coating"),
        "process_route_details": candidate.get("process_route_details"),
        "route_risks": candidate.get("route_risks"),
        "route_validation_gaps": candidate.get("route_validation_gaps"),
        "inspection_plan": candidate.get("inspection_plan"),
        "repairability": candidate.get("repairability"),
        "qualification_route": candidate.get("qualification_route"),
        "risks": candidate.get("risks"),
        "assumptions": candidate.get("assumptions"),
        "provenance": candidate.get("provenance"),
    }
    return _blob({key: value for key, value in fields.items() if value not in (None, "", [], {})})


def _matched_terms(text: str, terms: Sequence[str]) -> list[str]:
    return [term for term in terms if term in text]


def _level_count(candidates: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(_text(candidate.get(field), "unknown") for candidate in candidates).items()))


def _coating_record(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(
        candidate.get("coating_spallation_adhesion")
        or candidate.get("coating_or_surface_system")
        or candidate.get("coating_system")
        or candidate.get("environmental_barrier_coating")
    )


def _substrate_family(candidate: Mapping[str, Any]) -> str:
    coating = _mapping(candidate.get("coating_or_surface_system") or candidate.get("coating_system"))
    if _text(coating.get("substrate_compatibility")):
        return _text(coating.get("substrate_compatibility"))
    if _text(candidate.get("base_material_family")):
        return _text(candidate.get("base_material_family"))
    for constituent in _as_list(candidate.get("constituents")):
        item = _mapping(constituent)
        role = _text(item.get("role")).lower()
        if role in {"substrate", "matrix"}:
            return _text(item.get("material_family") or item.get("name"), "unknown")
    return "unknown"


def _coating_stack_summary(candidate: Mapping[str, Any]) -> str:
    coating = _mapping(
        candidate.get("coating_or_surface_system")
        or candidate.get("coating_system")
        or candidate.get("environmental_barrier_coating")
    )
    if coating:
        coating_type = _text(coating.get("coating_type") or coating.get("name"), "coating system")
        layers = [_text(_mapping(item).get("name") or item) for item in _as_list(coating.get("layers")) if _text(_mapping(item).get("name") or item)]
        if layers:
            return f"{coating_type}: " + " / ".join(layers)
        return coating_type
    coating_constituents = [
        _text(_mapping(item).get("name"))
        for item in _as_list(candidate.get("constituents"))
        if _text(_mapping(item).get("role")).lower() in {"coating", "top coat", "bond coat", "surface"}
        and _text(_mapping(item).get("name"))
    ]
    return " / ".join(coating_constituents) if coating_constituents else "coating details not specified"


def _raise_level(current: str, minimum: str) -> str:
    rank = {"none": 0, "low": 1, "medium": 2, "moderate": 2, "high": 3, "very_high": 4, "unknown": -1}
    if current == "unknown":
        return minimum
    return current if rank.get(current, 0) >= rank.get(minimum, 0) else minimum


def _kind_label(kind: str) -> str:
    return {
        "thermal_barrier_coating": "Thermal barrier coating system",
        "environmental_barrier_coating": "Environmental barrier coating system",
        "oxidation_hot_corrosion_coating": "Oxidation / hot-corrosion coating system",
        "wear_or_erosion_coating": "Wear or erosion coating system",
        "abradable_or_clearance_control_coating": "Abradable / clearance-control coating system",
        "generic_coating_system": "Generic coating system",
        "not_coating_relevant": "Not coating relevant",
    }[kind]


def is_coating_spallation_relevant_candidate(candidate: Mapping[str, Any]) -> bool:
    """Return whether coating spallation/adhesion diagnostics are relevant."""
    if _candidate_class(candidate) == "coating_enabled":
        return True
    if _architecture(candidate) == "substrate_plus_coating":
        return True
    text = _field_text(candidate)
    return any(cue in text for cue in _COATING_CUES)


def classify_coating_system(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Classify the visible coating system with conservative keyword heuristics."""
    if not is_coating_spallation_relevant_candidate(candidate):
        return {
            "coating_system_kind": "not_coating_relevant",
            "coating_system_label": _kind_label("not_coating_relevant"),
            "classification_confidence": "high",
            "classification_evidence_terms": [],
            "conservative_notes": ["No coating, TBC, EBC, bond-coat, wear or surface-coating cues were visible."],
        }

    text = _field_text(candidate)
    rules = [
        ("thermal_barrier_coating", ("tbc", "ysz", "thermal barrier", "bond coat", "bondcoat")),
        (
            "environmental_barrier_coating",
            ("ebc", "environmental barrier", "rare-earth silicate", "rare earth silicate", "recession", "steam"),
        ),
        (
            "oxidation_hot_corrosion_coating",
            ("oxidation", "hot corrosion", "hot-corrosion", "aluminide", "silicide", "mcraly"),
        ),
        ("wear_or_erosion_coating", ("wear", "erosion", "hard coating", "hard wear", "contact", "fretting")),
        ("abradable_or_clearance_control_coating", ("abradable", "clearance", "rub", "rub-tolerance")),
    ]
    matched_by_kind = [(kind, _matched_terms(text, terms)) for kind, terms in rules]
    matched_by_kind = [(kind, terms) for kind, terms in matched_by_kind if terms]
    if matched_by_kind:
        kind, terms = matched_by_kind[0]
        confidence = "high" if len(set(terms)) >= 2 or _candidate_class(candidate) == "coating_enabled" else "medium"
    else:
        kind = "generic_coating_system"
        terms = _matched_terms(text, _COATING_CUES)
        confidence = "medium" if terms else "low"

    notes = ["Classification is deterministic and conservative; it is not a coating qualification claim."]
    if kind == "thermal_barrier_coating":
        notes.append("Thermal-barrier systems require explicit bond-coat/interface and thermal-cycle validation.")
    elif kind == "environmental_barrier_coating":
        notes.append("Environmental-barrier systems require environment-specific recession and adhesion validation.")
    elif kind == "generic_coating_system":
        notes.append("Coating role is visible but the coating family is not specific enough for a narrower class.")
    return {
        "coating_system_kind": kind,
        "coating_system_label": _kind_label(kind),
        "classification_confidence": confidence,
        "classification_evidence_terms": list(dict.fromkeys(terms)),
        "conservative_notes": notes,
    }


def build_coating_spallation_adhesion_profile(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic diagnostic profile for coating adhesion and repair concerns."""
    classification = classify_coating_system(candidate)
    kind = classification["coating_system_kind"]
    maturity = _evidence_maturity(candidate)
    text = _field_text(candidate)
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))
    inspection_burden = _text(inspection.get("inspection_burden"), "unknown")
    repairability_level = _text(repairability.get("repairability_level"), "unknown")
    qualification_burden = _text(qualification.get("qualification_burden"), "unknown")

    profile = {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "evidence_maturity": maturity,
        **classification,
        "substrate_family": _substrate_family(candidate),
        "coating_stack_summary": _coating_stack_summary(candidate),
        "bond_coat_or_interface_dependency": "unknown",
        "adhesion_or_spallation_risk": "unknown",
        "cte_mismatch_risk": "unknown",
        "thermal_cycling_damage_risk": "unknown",
        "environmental_attack_risk": "unknown",
        "inspection_difficulty": "unknown",
        "repairability_constraint": "unknown",
        "qualification_burden": qualification_burden,
        "key_degradation_modes": [],
        "coating_strengths": [],
        "coating_concerns": [],
        "required_validation_evidence": [],
        "inspection_and_repair_notes": [],
        "maturity_constraint": "",
        "not_a_life_prediction": True,
        "not_a_qualification_claim": True,
    }

    if kind == "not_coating_relevant":
        profile.update(
            {
                "bond_coat_or_interface_dependency": "none",
                "adhesion_or_spallation_risk": "unknown",
                "coating_concerns": ["Coating diagnostics are not relevant to this candidate."],
            }
        )
        return profile

    strengths = [_text(item) for item in _as_list(candidate.get("route_benefits")) if _text(item)]
    concerns = [_text(item) for item in _as_list(candidate.get("route_risks")) if _text(item)]
    validation = [_text(item) for item in _as_list(candidate.get("route_validation_gaps")) if _text(item)]
    degradation = []
    notes = []

    if kind == "thermal_barrier_coating":
        profile.update(
            {
                "bond_coat_or_interface_dependency": "very_high" if "bond coat" in text or "bondcoat" in text else "high",
                "adhesion_or_spallation_risk": "high" if "spallation" in text or "adhesion" in text else "medium",
                "cte_mismatch_risk": "high" if "cte" in text or "mismatch" in text else "medium",
                "thermal_cycling_damage_risk": "high",
                "environmental_attack_risk": "medium",
            }
        )
        degradation.extend(["spallation", "bond coat oxidation", "thermal-cycle damage", "CTE mismatch"])
        strengths.extend(["thermal protection function is explicit"])
        concerns.extend(["bond coat/interface dependency", "thermal cycling durability", "coating inspection and repair planning"])
        validation.extend(["bond coat/top-coat adhesion evidence", "thermal-cycle spallation evidence", "CTE compatibility evidence"])
        notes.extend(["Inspect coating condition and interface-sensitive damage; repair typically depends on strip/recoat disposition."])
    elif kind == "environmental_barrier_coating":
        profile.update(
            {
                "bond_coat_or_interface_dependency": "high" if "bond" in text else "moderate",
                "adhesion_or_spallation_risk": "medium",
                "cte_mismatch_risk": "high" if "mismatch" in text or "thermal expansion" in text else "medium",
                "thermal_cycling_damage_risk": "medium",
                "environmental_attack_risk": "high",
            }
        )
        degradation.extend(["water-vapor recession", "environmental attack", "coating defects", "adhesion loss"])
        strengths.extend(["environmental barrier role is explicit"])
        concerns.extend(["environmental compatibility", "recession durability", "repair/recoat constraints"])
        validation.extend(["environment-specific recession evidence", "EBC/substrate compatibility evidence", "EBC adhesion evidence"])
        notes.extend(["Inspection must account for coating defects and recession; repair/recoat assumptions need validation."])
    elif kind == "wear_or_erosion_coating":
        profile.update(
            {
                "bond_coat_or_interface_dependency": "moderate",
                "adhesion_or_spallation_risk": "high" if "adhesion" in text else "medium",
                "cte_mismatch_risk": "medium" if any(term in text for term in ("thermal", "cte", "mismatch")) else "low",
                "thermal_cycling_damage_risk": "low" if "thermal" not in text else "medium",
                "environmental_attack_risk": "medium" if "erosion" in text else "low",
            }
        )
        degradation.extend(["adhesion loss", "residual stress cracking", "edge damage", "surface wear"])
        strengths.extend(["localized wear or erosion protection is explicit"])
        concerns.extend(["substrate compatibility", "residual stress", "surface finish", "strip/recoat repair"])
        validation.extend(["coating adhesion evidence", "substrate fatigue compatibility evidence", "repair or recoat evidence"])
        notes.extend(["Inspect worn regions, edges and coating loss; repair may require strip/recoat and surface-finish restoration."])
    elif kind == "oxidation_hot_corrosion_coating":
        profile.update(
            {
                "bond_coat_or_interface_dependency": "moderate",
                "adhesion_or_spallation_risk": "medium",
                "cte_mismatch_risk": "medium",
                "thermal_cycling_damage_risk": "medium",
                "environmental_attack_risk": "high",
            }
        )
        degradation.extend(["oxidation", "hot corrosion", "coating depletion", "cracking"])
        strengths.extend(["oxidation or hot-corrosion protection role is explicit"])
        concerns.extend(["coating/substrate compatibility", "environmental exposure specificity", "process repeatability"])
        validation.extend(["environmental exposure evidence", "coating/substrate compatibility evidence", "process repeatability evidence"])
        notes.extend(["Inspection should cover environmental attack and coating loss; repair may require strip/recoat compatibility review."])
    elif kind == "abradable_or_clearance_control_coating":
        profile.update(
            {
                "bond_coat_or_interface_dependency": "moderate",
                "adhesion_or_spallation_risk": "medium",
                "cte_mismatch_risk": "medium",
                "thermal_cycling_damage_risk": "medium",
                "environmental_attack_risk": "medium",
            }
        )
        degradation.extend(["rub damage", "erosion", "thermal aging", "debris compatibility"])
        strengths.extend(["clearance-control or sacrificial wear role is explicit"])
        concerns.extend(["rub compatibility", "repair interval uncertainty", "application-specific inspection"])
        validation.extend(["rub interaction evidence", "inspection interval evidence", "repair interval evidence"])
        notes.extend(["Inspect rub tracks and local coating condition; repair interval assumptions should remain explicit."])
    else:
        profile.update(
            {
                "bond_coat_or_interface_dependency": "moderate",
                "adhesion_or_spallation_risk": "medium",
                "cte_mismatch_risk": "medium" if any(term in text for term in ("thermal", "cte", "mismatch")) else "unknown",
                "thermal_cycling_damage_risk": "medium" if "thermal" in text else "unknown",
                "environmental_attack_risk": "medium" if any(term in text for term in ("oxidation", "corrosion", "steam")) else "unknown",
            }
        )
        degradation.extend(["coating adhesion loss", "interface compatibility limits"])
        concerns.extend(["coating/substrate compatibility", "process repeatability", "inspection and repair assumptions"])
        validation.extend(["coating adhesion evidence", "coating/substrate compatibility evidence", "inspection and repair evidence"])
        notes.extend(["Coating family is generic, so inspection and repair assumptions should remain conservative."])

    if "spallation" in text:
        profile["adhesion_or_spallation_risk"] = _raise_level(profile["adhesion_or_spallation_risk"], "high")
    if "cte" in text or "thermal expansion mismatch" in text or "thermal expansion" in text:
        profile["cte_mismatch_risk"] = _raise_level(profile["cte_mismatch_risk"], "high")
    if "thermal cycling" in text or "thermal-cycle" in text:
        profile["thermal_cycling_damage_risk"] = _raise_level(profile["thermal_cycling_damage_risk"], "high")
    if any(term in text for term in ("steam", "water vapor", "recession", "cmas", "hot corrosion", "oxidation")):
        profile["environmental_attack_risk"] = _raise_level(profile["environmental_attack_risk"], "high")

    if inspection_burden == "high":
        profile["inspection_difficulty"] = "high"
    elif inspection_burden == "medium":
        profile["inspection_difficulty"] = "medium"
    elif inspection_burden == "low":
        profile["inspection_difficulty"] = "low"
    else:
        profile["inspection_difficulty"] = "medium" if kind != "generic_coating_system" else "unknown"

    if repairability_level == "poor":
        profile["repairability_constraint"] = "high"
    elif repairability_level == "limited":
        profile["repairability_constraint"] = "high" if kind in {"thermal_barrier_coating", "environmental_barrier_coating"} else "medium"
    elif repairability_level == "moderate":
        profile["repairability_constraint"] = "medium"
    elif repairability_level == "good":
        profile["repairability_constraint"] = "low"
    else:
        profile["repairability_constraint"] = "medium"

    if qualification_burden in {"high", "very_high"}:
        profile["qualification_burden"] = qualification_burden
    elif maturity in _LOW_MATURITY:
        profile["qualification_burden"] = "high"

    if maturity in _LOW_MATURITY:
        profile["maturity_constraint"] = (
            f"Evidence maturity {maturity} keeps this coating-relevant system exploratory or validation-limited."
        )
        validation.append("higher maturity coating durability evidence")
        concerns.append(profile["maturity_constraint"])

    if inspection_burden == "high":
        notes.append("Process-route enrichment exposes high inspection burden.")
    if repairability_level in {"limited", "poor"}:
        notes.append(f"Process-route enrichment exposes {repairability_level} repairability.")
    if qualification_burden in {"high", "very_high"}:
        concerns.append(f"Process-route enrichment exposes {qualification_burden} qualification burden.")

    profile["key_degradation_modes"] = list(dict.fromkeys(_text(item) for item in degradation if _text(item)))[:8]
    profile["coating_strengths"] = list(dict.fromkeys(_text(item) for item in strengths if _text(item)))[:6]
    profile["coating_concerns"] = list(dict.fromkeys(_text(item) for item in concerns if _text(item)))[:8]
    profile["required_validation_evidence"] = list(dict.fromkeys(_text(item) for item in validation if _text(item)))[:8]
    profile["inspection_and_repair_notes"] = list(dict.fromkeys(_text(item) for item in notes if _text(item)))[:6]
    return profile


def build_coating_spallation_adhesion_summary(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    candidate_list = [candidate for candidate in candidates if isinstance(candidate, Mapping)]
    profiles = []
    for candidate in candidate_list:
        profile = _mapping(candidate.get("coating_spallation_adhesion"))
        if not profile and is_coating_spallation_relevant_candidate(candidate):
            profile = build_coating_spallation_adhesion_profile(candidate)
        if profile and profile.get("coating_system_kind") != "not_coating_relevant":
            profiles.append(dict(profile))

    themes = sorted(
        {
            _text(item)
            for profile in profiles
            for item in _as_list(profile.get("required_validation_evidence"))
            if _text(item)
        }
    )
    warnings = []
    if any(profile.get("adhesion_or_spallation_risk") == "high" for profile in profiles):
        warnings.append("High coating adhesion/spallation risk is visible.")
    if any(profile.get("inspection_difficulty") == "high" for profile in profiles):
        warnings.append("High coating inspection difficulty is visible.")
    if any(profile.get("repairability_constraint") == "high" for profile in profiles):
        warnings.append("High coating repairability constraint is visible.")
    if any(_text(profile.get("evidence_maturity")).upper() in _LOW_MATURITY for profile in profiles):
        warnings.append("D/E/F maturity appears on one or more coating-relevant systems.")

    return {
        "candidate_count": len(candidate_list),
        "relevant_candidate_count": len(profiles),
        "coating_system_kind_counts": _level_count(profiles, "coating_system_kind"),
        "bond_coat_or_interface_dependency_counts": _level_count(profiles, "bond_coat_or_interface_dependency"),
        "adhesion_or_spallation_risk_counts": _level_count(profiles, "adhesion_or_spallation_risk"),
        "cte_mismatch_risk_counts": _level_count(profiles, "cte_mismatch_risk"),
        "thermal_cycling_damage_risk_counts": _level_count(profiles, "thermal_cycling_damage_risk"),
        "environmental_attack_risk_counts": _level_count(profiles, "environmental_attack_risk"),
        "inspection_difficulty_counts": _level_count(profiles, "inspection_difficulty"),
        "repairability_constraint_counts": _level_count(profiles, "repairability_constraint"),
        "qualification_burden_counts": _level_count(profiles, "qualification_burden"),
        "high_spallation_risk_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("adhesion_or_spallation_risk") == "high"
        ],
        "high_interface_dependency_candidate_ids": [
            profile["candidate_id"]
            for profile in profiles
            if profile.get("bond_coat_or_interface_dependency") in {"high", "very_high"}
        ],
        "high_inspection_difficulty_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("inspection_difficulty") == "high"
        ],
        "high_repairability_constraint_candidate_ids": [
            profile["candidate_id"] for profile in profiles if profile.get("repairability_constraint") == "high"
        ],
        "high_qualification_burden_candidate_ids": [
            profile["candidate_id"]
            for profile in profiles
            if profile.get("qualification_burden") in {"high", "very_high"}
        ],
        "low_maturity_relevant_candidate_ids": [
            profile["candidate_id"] for profile in profiles if _text(profile.get("evidence_maturity")).upper() in _LOW_MATURITY
        ],
        "required_validation_evidence_themes": themes,
        "warnings": warnings,
    }


def attach_coating_spallation_adhesion(package: Mapping[str, Any]) -> dict[str, Any]:
    """Attach coating spallation/adhesion diagnostics without mutating package input."""
    output = dict(package)
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    enriched_candidates = []
    for candidate in candidates:
        enriched = dict(candidate)
        if is_coating_spallation_relevant_candidate(candidate):
            enriched["coating_spallation_adhesion"] = build_coating_spallation_adhesion_profile(candidate)
        enriched_candidates.append(enriched)

    summary = build_coating_spallation_adhesion_summary(enriched_candidates)
    output["candidate_systems"] = enriched_candidates
    output["coating_spallation_adhesion_summary"] = summary
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))

    warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    warning_rules = [
        ("high_spallation_risk_candidate_ids", "high coating adhesion/spallation risk"),
        ("high_interface_dependency_candidate_ids", "high coating bond-coat/interface dependency"),
        ("high_inspection_difficulty_candidate_ids", "high coating inspection difficulty"),
        ("high_repairability_constraint_candidate_ids", "high coating repairability constraint"),
        ("high_qualification_burden_candidate_ids", "high or very high coating qualification burden"),
        ("low_maturity_relevant_candidate_ids", "D/E/F maturity on coating-relevant system"),
    ]
    high_cte = []
    high_thermal = []
    high_environment = []
    for candidate in enriched_candidates:
        profile = _mapping(candidate.get("coating_spallation_adhesion"))
        if not profile:
            continue
        candidate_id = _candidate_id(candidate)
        if profile.get("cte_mismatch_risk") == "high":
            high_cte.append(candidate_id)
        if profile.get("thermal_cycling_damage_risk") == "high":
            high_thermal.append(candidate_id)
        if profile.get("environmental_attack_risk") == "high":
            high_environment.append(candidate_id)
    extra = {
        "high_cte_mismatch_risk_candidate_ids": high_cte,
        "high_thermal_cycling_damage_risk_candidate_ids": high_thermal,
        "high_environmental_attack_risk_candidate_ids": high_environment,
    }
    summary.update(extra)
    warning_rules.extend(
        [
            ("high_cte_mismatch_risk_candidate_ids", "high coating CTE mismatch risk"),
            ("high_thermal_cycling_damage_risk_candidate_ids", "high coating thermal cycling damage risk"),
            ("high_environmental_attack_risk_candidate_ids", "high coating environmental attack risk"),
        ]
    )
    for field, label in warning_rules:
        for candidate_id in _as_list(summary.get(field)):
            warning = f"{candidate_id}: {label} is visible in diagnostic profile."
            if warning not in warnings:
                warnings.append(warning)
    for warning in _as_list(summary.get("warnings")):
        text = _text(warning)
        if text and text not in warnings:
            warnings.append(text)
    output["warnings"] = warnings

    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "coating_spallation_adhesion_attached": True,
            "coating_spallation_relevant_candidate_count": summary["relevant_candidate_count"],
        }
    )
    output["diagnostics"] = diagnostics
    return output
