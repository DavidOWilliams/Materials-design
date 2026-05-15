from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


DEFAULT_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "material_systems"
    / "process_route_templates.json"
)

_REQUIRED_TEMPLATE_FIELDS = {
    "route_id",
    "display_name",
    "applicable_candidate_classes",
    "applicable_architecture_types",
    "process_family",
    "process_chain",
    "key_process_controls",
    "inspection_plan",
    "repairability",
    "qualification",
    "route_risks",
    "route_benefits",
    "sustainability_or_cost_notes",
    "assumptions",
    "validation_gaps",
}
_INSPECTION_BURDENS = {"low", "medium", "high", "unknown"}
_REPAIRABILITY_LEVELS = {"good", "moderate", "limited", "poor", "unknown"}
_QUALIFICATION_BURDENS = {"low", "medium", "high", "very_high", "unknown"}
_MATURITY_LEVELS = {"A", "B", "C", "D", "E", "F"}


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


def _validate_string_list(template: Mapping[str, Any], field: str) -> None:
    values = template.get(field)
    if not isinstance(values, list) or not all(isinstance(item, str) and item.strip() for item in values):
        raise ValueError(f"Process route template {template.get('route_id')}: {field} must be a list of strings.")


def _validate_template(template: Mapping[str, Any]) -> None:
    missing = sorted(field for field in _REQUIRED_TEMPLATE_FIELDS if field not in template)
    if missing:
        raise ValueError(f"Process route template is missing required fields: {', '.join(missing)}.")

    route_id = _text(template.get("route_id"))
    if not route_id:
        raise ValueError("Process route template route_id must be a non-empty string.")
    for field in (
        "display_name",
        "process_family",
    ):
        if not _text(template.get(field)):
            raise ValueError(f"Process route template {route_id}: {field} must be a non-empty string.")
    for field in (
        "applicable_candidate_classes",
        "applicable_architecture_types",
        "process_chain",
        "key_process_controls",
        "route_risks",
        "route_benefits",
        "sustainability_or_cost_notes",
        "assumptions",
        "validation_gaps",
    ):
        _validate_string_list(template, field)

    inspection = _mapping(template.get("inspection_plan"))
    if inspection.get("inspection_burden") not in _INSPECTION_BURDENS:
        raise ValueError(f"Process route template {route_id}: inspection_burden is invalid.")
    for field in ("inspection_methods", "inspection_targets", "inspection_challenges"):
        if not isinstance(inspection.get(field), list):
            raise ValueError(f"Process route template {route_id}: inspection_plan.{field} must be a list.")

    repairability = _mapping(template.get("repairability"))
    if repairability.get("repairability_level") not in _REPAIRABILITY_LEVELS:
        raise ValueError(f"Process route template {route_id}: repairability_level is invalid.")
    if not _text(repairability.get("repair_concept")):
        raise ValueError(f"Process route template {route_id}: repair_concept must be a non-empty string.")
    for field in ("repair_constraints", "likely_maintenance_actions"):
        if not isinstance(repairability.get(field), list):
            raise ValueError(f"Process route template {route_id}: repairability.{field} must be a list.")

    qualification = _mapping(template.get("qualification"))
    if qualification.get("qualification_burden") not in _QUALIFICATION_BURDENS:
        raise ValueError(f"Process route template {route_id}: qualification_burden is invalid.")
    if not isinstance(qualification.get("qualification_notes"), list):
        raise ValueError(f"Process route template {route_id}: qualification_notes must be a list.")

    maturity_floor = template.get("evidence_maturity_floor")
    if maturity_floor is not None and maturity_floor not in _MATURITY_LEVELS:
        raise ValueError(f"Process route template {route_id}: evidence_maturity_floor is invalid.")


def load_process_route_templates(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load and minimally validate deterministic Build 4 process-route templates."""
    template_path = Path(path) if path is not None else DEFAULT_TEMPLATE_PATH
    try:
        raw = json.loads(template_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed process route template JSON: {template_path}") from exc

    if isinstance(raw, Mapping):
        templates = list(raw.values())
    elif isinstance(raw, list):
        templates = raw
    else:
        raise ValueError("Process route templates JSON must be a list or mapping.")

    output: dict[str, dict[str, Any]] = {}
    for template in templates:
        if not isinstance(template, Mapping):
            raise ValueError("Each process route template must be a mapping.")
        _validate_template(template)
        route_id = _text(template.get("route_id"))
        if route_id in output:
            raise ValueError(f"Duplicate process route template route_id: {route_id}.")
        output[route_id] = dict(template)
    return output


def infer_process_route_template_id(candidate: Mapping[str, Any]) -> str | None:
    """Infer the best deterministic process-route template for a candidate."""
    candidate_id = _candidate_id(candidate).lower()
    candidate_class = _candidate_class(candidate)
    architecture = _architecture(candidate)
    text = _blob(
        {
            "candidate_id": candidate.get("candidate_id"),
            "name": candidate.get("name") or candidate.get("system_name"),
            "candidate_class": candidate_class,
            "architecture": architecture,
            "coating": candidate.get("coating_or_surface_system") or candidate.get("coating_system"),
            "gradient": candidate.get("gradient_architecture"),
            "constituents": candidate.get("constituents"),
            "process_route": candidate.get("process_route") or candidate.get("processing_routes"),
        }
    )

    exact_ids = {
        "demo_ni_superalloy_bondcoat_tbc_comparison": "ni_superalloy_tbc",
        "demo_refractory_oxidation_protection_comparison": "refractory_oxidation_protection",
        "sic_sic_cmc_ebc_anchor": "sic_sic_cmc_ebc",
        "oxide_oxide_cmc_comparison": "oxide_oxide_cmc",
        "monolithic_sic_reference": "monolithic_sic",
        "silicon_nitride_reference": "silicon_nitride",
        "alumina_reference": "alumina",
        "tbc_reference": "thermal_barrier_coating_system",
        "ebc_reference": "environmental_barrier_coating_system",
        "wear_coating_reference": "wear_resistant_coating_system",
        "surface_oxidation_gradient": "surface_oxidation_gradient",
        "surface_wear_gradient": "surface_wear_gradient",
        "tough_core_hard_surface_gradient": "tough_core_hard_surface_gradient",
        "thermal_barrier_gradient": "thermal_barrier_gradient",
    }
    if candidate_id in exact_ids:
        return exact_ids[candidate_id]

    if "ni" in text and ("tbc" in text or "thermal barrier" in text) and "superalloy" in text:
        return "ni_superalloy_tbc"
    if "refractory" in text and ("oxidation" in text or "silicide" in text or "aluminide" in text):
        return "refractory_oxidation_protection"
    if (
        candidate_class == "ceramic_matrix_composite"
        and ("sic/sic" in text or "sic sic" in text)
        and ("ebc" in text or "environmental barrier" in text)
    ):
        if candidate_id == "sic_sic_cmc_ebc_anchor":
            return "sic_sic_cmc_ebc"
        return "generic_sic_sic_cmc_ebc"
    if "oxide/oxide" in text or "oxide oxide" in text:
        if candidate_id == "oxide_oxide_cmc_comparison":
            return "oxide_oxide_cmc"
        return "generic_oxide_oxide_cmc"
    if candidate_class == "ceramic_matrix_composite" and ("carbon" in text or "c/sic" in text or "c sic" in text):
        return "generic_carbon_containing_cmc_with_oxidation_protection"
    if "silicon nitride" in text:
        return "silicon_nitride"
    if "alumina" in text:
        return "alumina"
    if "silicon carbide" in text or "monolithic sic" in text:
        return "monolithic_sic"
    if ("wear" in text or "erosion" in text or "abradable" in text or "clearance" in text) and candidate_class == "coating_enabled":
        if candidate_id == "wear_coating_reference":
            return "wear_resistant_coating_system"
        return "generic_erosion_wear_coating"
    if ("ebc" in text or "environmental barrier" in text) and candidate_class == "coating_enabled":
        if candidate_id == "ebc_reference":
            return "environmental_barrier_coating_system"
        return "generic_ebc_stack"
    if ("oxidation" in text or "hot-corrosion" in text or "hot corrosion" in text) and candidate_class == "coating_enabled":
        return "generic_oxidation_hot_corrosion_coating"
    if ("tbc" in text or "thermal barrier" in text) and candidate_class == "coating_enabled":
        if candidate_id == "tbc_reference":
            return "thermal_barrier_coating_system"
        return "generic_tbc_stack"
    if architecture == "spatial_gradient" or candidate_class == "spatially_graded_am":
        if "metal-to-ceramic" in text or "metal ceramic" in text or "ceramic-rich" in text:
            return "generic_metal_ceramic_transition_gradient"
        if "repair" in text or "buildup" in text:
            return "generic_repair_gradient"
        if "oxidation" in text:
            return "surface_oxidation_gradient" if candidate_id == "surface_oxidation_gradient" else "surface_oxidation_gradient"
        if "wear" in text or "hard surface" in text or "hard-surface" in text:
            return "surface_wear_gradient" if candidate_id == "surface_wear_gradient" else "surface_wear_gradient"
        if "tough" in text and "hard" in text:
            return "tough_core_hard_surface_gradient"
        if "thermal" in text or "barrier" in text:
            return "thermal_barrier_gradient" if candidate_id == "thermal_barrier_gradient" else "thermal_barrier_gradient"
    return None


def _unknown_route_record(candidate: Mapping[str, Any]) -> dict[str, Any]:
    candidate_id = _candidate_id(candidate)
    return {
        "route_id": "unknown_route",
        "display_name": "Unknown process route",
        "applicable_candidate_classes": [_candidate_class(candidate)],
        "applicable_architecture_types": [_architecture(candidate)],
        "process_family": "unknown",
        "process_chain": [],
        "key_process_controls": [],
        "inspection_plan": {
            "inspection_burden": "unknown",
            "inspection_methods": [],
            "inspection_targets": [],
            "inspection_challenges": ["Process route is not identified, so inspection requirements are unknown."],
        },
        "repairability": {
            "repairability_level": "unknown",
            "repair_concept": "No deterministic repair concept is available for the inferred route.",
            "repair_constraints": ["Repairability cannot be assessed until route details are known."],
            "likely_maintenance_actions": [],
        },
        "qualification": {
            "qualification_burden": "unknown",
            "qualification_notes": ["Qualification route cannot be assessed until process route is identified."],
        },
        "route_risks": ["unknown process route"],
        "route_benefits": [],
        "sustainability_or_cost_notes": [],
        "evidence_maturity_floor": None,
        "assumptions": ["Conservative unknown-route fallback attached by Build 4 process-route enrichment."],
        "validation_gaps": ["identify deterministic process route template"],
        "warnings": [f"{candidate_id}: no deterministic process route template matched."],
    }


def enrich_candidate_with_process_route(
    candidate: Mapping[str, Any],
    templates: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a candidate copy with deterministic process, inspection and repair fields."""
    route_templates = templates or load_process_route_templates()
    output = dict(candidate)
    route_id = infer_process_route_template_id(candidate)
    template = dict(route_templates[route_id]) if route_id and route_id in route_templates else _unknown_route_record(candidate)
    selected_route_id = _text(template.get("route_id"), "unknown_route")

    inspection_plan = dict(_mapping(template.get("inspection_plan")))
    repairability = dict(_mapping(template.get("repairability")))
    qualification = dict(_mapping(template.get("qualification")))
    process_route_details = {
        "route_id": selected_route_id,
        "display_name": _text(template.get("display_name"), "Unknown process route"),
        "process_family": _text(template.get("process_family"), "unknown"),
        "process_chain": [_text(item) for item in _as_list(template.get("process_chain")) if _text(item)],
        "key_process_controls": [_text(item) for item in _as_list(template.get("key_process_controls")) if _text(item)],
        "route_risks": [_text(item) for item in _as_list(template.get("route_risks")) if _text(item)],
        "route_benefits": [_text(item) for item in _as_list(template.get("route_benefits")) if _text(item)],
        "sustainability_or_cost_notes": [
            _text(item) for item in _as_list(template.get("sustainability_or_cost_notes")) if _text(item)
        ],
        "evidence_maturity_floor": template.get("evidence_maturity_floor"),
        "assumptions": [_text(item) for item in _as_list(template.get("assumptions")) if _text(item)],
        "validation_gaps": [_text(item) for item in _as_list(template.get("validation_gaps")) if _text(item)],
    }

    warnings = [_text(item) for item in _as_list(output.get("process_route_warnings")) if _text(item)]
    if selected_route_id == "unknown_route":
        warnings.extend(_text(item) for item in _as_list(template.get("warnings")) if _text(item))

    output.update(
        {
            "process_route_template_id": selected_route_id,
            "process_route_details": process_route_details,
            "inspection_plan": inspection_plan,
            "repairability": repairability,
            "qualification_route": qualification,
            "route_risks": list(process_route_details["route_risks"]),
            "route_benefits": list(process_route_details["route_benefits"]),
            "route_validation_gaps": list(process_route_details["validation_gaps"]),
        }
    )
    if warnings:
        output["process_route_warnings"] = warnings
    return output


def enrich_candidates_with_process_routes(
    candidates: Sequence[Mapping[str, Any]],
    templates: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Enrich candidates while preserving count and order."""
    route_templates = templates or load_process_route_templates()
    return [enrich_candidate_with_process_route(candidate, route_templates) for candidate in candidates]


def build_process_route_summary(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize process-route, inspection, repairability and qualification visibility."""
    candidate_list = [candidate for candidate in candidates if isinstance(candidate, Mapping)]
    route_counts = Counter(_text(candidate.get("process_route_template_id"), "unknown_route") for candidate in candidate_list)
    process_family_counts = Counter(
        _text(_mapping(candidate.get("process_route_details")).get("process_family"), "unknown")
        for candidate in candidate_list
    )
    inspection_counts = Counter(
        _text(_mapping(candidate.get("inspection_plan")).get("inspection_burden"), "unknown")
        for candidate in candidate_list
    )
    repair_counts = Counter(
        _text(_mapping(candidate.get("repairability")).get("repairability_level"), "unknown")
        for candidate in candidate_list
    )
    qualification_counts = Counter(
        _text(_mapping(candidate.get("qualification_route")).get("qualification_burden"), "unknown")
        for candidate in candidate_list
    )

    unknown_ids = [
        _candidate_id(candidate)
        for candidate in candidate_list
        if _text(candidate.get("process_route_template_id"), "unknown_route") == "unknown_route"
    ]
    high_inspection_ids = [
        _candidate_id(candidate)
        for candidate in candidate_list
        if _text(_mapping(candidate.get("inspection_plan")).get("inspection_burden")) == "high"
    ]
    limited_repair_ids = [
        _candidate_id(candidate)
        for candidate in candidate_list
        if _text(_mapping(candidate.get("repairability")).get("repairability_level")) in {"limited", "poor"}
    ]
    high_qualification_ids = [
        _candidate_id(candidate)
        for candidate in candidate_list
        if _text(_mapping(candidate.get("qualification_route")).get("qualification_burden")) in {"high", "very_high"}
    ]

    warnings: list[str] = []
    warnings.extend(f"{candidate_id}: process route is unknown." for candidate_id in unknown_ids)
    warnings.extend(f"{candidate_id}: high inspection burden is visible." for candidate_id in high_inspection_ids)
    warnings.extend(
        f"{candidate_id}: limited or poor repairability is visible."
        for candidate_id in limited_repair_ids
    )
    warnings.extend(
        f"{candidate_id}: high or very high qualification burden is visible."
        for candidate_id in high_qualification_ids
    )
    for candidate in candidate_list:
        warnings.extend(_text(item) for item in _as_list(candidate.get("process_route_warnings")) if _text(item))

    return {
        "candidate_count": len(candidate_list),
        "enriched_candidate_count": sum(1 for candidate in candidate_list if candidate.get("process_route_details")),
        "route_template_counts": dict(sorted(route_counts.items())),
        "process_family_counts": dict(sorted(process_family_counts.items())),
        "inspection_burden_counts": dict(sorted(inspection_counts.items())),
        "repairability_level_counts": dict(sorted(repair_counts.items())),
        "qualification_burden_counts": dict(sorted(qualification_counts.items())),
        "candidates_with_unknown_route": unknown_ids,
        "high_inspection_burden_candidate_ids": high_inspection_ids,
        "limited_or_poor_repairability_candidate_ids": limited_repair_ids,
        "high_or_very_high_qualification_burden_candidate_ids": high_qualification_ids,
        "warnings": list(dict.fromkeys(warnings)),
    }


def attach_process_route_enrichment(package: Mapping[str, Any]) -> dict[str, Any]:
    """Attach deterministic process-route enrichment to a package-compatible copy."""
    output = dict(package)
    candidates = [
        candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)
    ]
    enriched_candidates = enrich_candidates_with_process_routes(candidates)
    summary = build_process_route_summary(enriched_candidates)

    output["candidate_systems"] = enriched_candidates
    output["process_route_summary"] = summary
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))

    warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    for warning in summary["warnings"]:
        if warning not in warnings:
            warnings.append(warning)
    output["warnings"] = warnings

    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "process_route_enrichment_attached": True,
            "process_route_enriched_candidate_count": summary["enriched_candidate_count"],
        }
    )
    output["diagnostics"] = diagnostics
    return output
