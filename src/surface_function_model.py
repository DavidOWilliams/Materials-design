from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from src.contracts import evidence_maturity_label


DEFAULT_TAXONOMY_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "material_systems"
    / "surface_function_taxonomy.json"
)
UNKNOWN_FUNCTION_ID = "unknown_surface_function"

PRIMARY_SERVICE_FUNCTIONS = {
    "thermal_barrier",
    "environmental_barrier",
    "oxidation_resistance",
    "steam_recession_resistance",
    "wear_resistance",
    "erosion_resistance",
    "hard_surface",
}
SECONDARY_SERVICE_FUNCTIONS = {
    "thermal_cycling_tolerance",
    "transition_zone_management",
}
SUPPORT_OR_LIFECYCLE_CONSIDERATIONS = {
    "inspection_access_or_monitoring",
    "repairability_support",
}
RISK_OR_INTERFACE_CONSIDERATIONS = {
    "coating_interface_management",
}

_REQUIRED_FIELDS = {
    "function_id",
    "display_name",
    "description",
    "typical_material_system_classes",
    "typical_architecture_types",
    "positive_keywords",
    "negative_or_caution_keywords",
    "related_route_risks",
    "related_validation_gaps",
    "typical_evidence_concerns",
    "example_candidate_types",
}


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


def _validate_string_list(record: Mapping[str, Any], field: str) -> None:
    value = record.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Surface function {record.get('function_id')}: {field} must be a list of strings.")


def _validate_record(record: Mapping[str, Any]) -> None:
    missing = sorted(field for field in _REQUIRED_FIELDS if field not in record)
    if missing:
        raise ValueError(f"Surface function taxonomy record is missing fields: {', '.join(missing)}.")
    if not _text(record.get("function_id")):
        raise ValueError("Surface function taxonomy record function_id must be non-empty.")
    for field in ("display_name", "description"):
        if not _text(record.get(field)):
            raise ValueError(f"Surface function {record.get('function_id')}: {field} must be non-empty.")
    for field in _REQUIRED_FIELDS - {"function_id", "display_name", "description"}:
        _validate_string_list(record, field)


def load_surface_function_taxonomy(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    taxonomy_path = Path(path) if path is not None else DEFAULT_TAXONOMY_PATH
    try:
        raw = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed surface function taxonomy JSON: {taxonomy_path}") from exc
    if isinstance(raw, Mapping):
        records = list(raw.values())
    elif isinstance(raw, list):
        records = raw
    else:
        raise ValueError("Surface function taxonomy JSON must be a list or mapping.")

    output: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("Each surface function taxonomy record must be a mapping.")
        _validate_record(record)
        function_id = _text(record.get("function_id"))
        if function_id in output:
            raise ValueError(f"Duplicate surface function taxonomy record: {function_id}.")
        output[function_id] = dict(record)
    if UNKNOWN_FUNCTION_ID not in output:
        raise ValueError("Surface function taxonomy must include unknown_surface_function.")
    return output


def _taxonomy_record(function_id: str, taxonomy: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any]:
    return _mapping(taxonomy.get(function_id))


def classify_function_kind(function_id: str) -> str:
    function = _text(function_id)
    if function in PRIMARY_SERVICE_FUNCTIONS:
        return "primary_service_function"
    if function in SECONDARY_SERVICE_FUNCTIONS:
        return "secondary_service_function"
    if function in SUPPORT_OR_LIFECYCLE_CONSIDERATIONS:
        return "support_or_lifecycle_consideration"
    if function in RISK_OR_INTERFACE_CONSIDERATIONS:
        return "risk_or_interface_consideration"
    if function == UNKNOWN_FUNCTION_ID:
        return "unknown_function_kind"
    return "unknown_function_kind"


def _field_blob(candidate: Mapping[str, Any]) -> tuple[str, dict[str, str]]:
    fields = {
        "candidate_id": _text(candidate.get("candidate_id")),
        "system_name": _text(candidate.get("system_name") or candidate.get("name")),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "coating_or_surface_system": _blob(
            candidate.get("coating_or_surface_system")
            or candidate.get("coating_system")
            or candidate.get("environmental_barrier_coating")
        ),
        "gradient_architecture": _blob(candidate.get("gradient_architecture")),
        "process_route_details": _blob(candidate.get("process_route_details")),
        "route_risks": _blob(candidate.get("route_risks")),
        "route_benefits": _blob(candidate.get("route_benefits")),
        "validation_gaps": _blob(candidate.get("route_validation_gaps")),
        "interfaces": _blob(candidate.get("interfaces")),
        "inspection_plan": _blob(candidate.get("inspection_plan")),
        "repairability": _blob(candidate.get("repairability")),
    }
    return " ".join(fields.values()).lower(), fields


def _function_record(
    function_id: str,
    taxonomy: Mapping[str, Mapping[str, Any]],
    evidence_terms: Sequence[str],
    inferred_from_fields: Sequence[str],
    rationale: str,
) -> dict[str, Any]:
    record = _taxonomy_record(function_id, taxonomy)
    confidence = "high" if len(set(evidence_terms)) >= 2 else "medium"
    return {
        "function_id": function_id,
        "function_kind": classify_function_kind(function_id),
        "display_name": _text(record.get("display_name"), function_id),
        "evidence_terms": list(dict.fromkeys(evidence_terms)),
        "inferred_from_fields": list(dict.fromkeys(inferred_from_fields)),
        "confidence": confidence,
        "rationale": rationale,
    }


def infer_required_surface_functions(
    requirement_schema: Mapping[str, Any] | None = None,
    design_space: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    taxonomy = load_surface_function_taxonomy()
    schema = _mapping(requirement_schema)
    design = _mapping(design_space)
    text = _blob({"requirement_schema": schema, "design_space": design})
    rules = [
        ("thermal_barrier", ("thermal barrier", "thermal protection", "hot-section", "high-temperature", "thermal margin")),
        ("thermal_cycling_tolerance", ("thermal cycling", "thermal-cycle", "thermal fatigue", "thermal shock")),
        ("oxidation_resistance", ("oxidation", "oxidizing", "corrosion", "hot corrosion")),
        ("environmental_barrier", ("environmental barrier", "ebc", "steam", "water vapor")),
        ("steam_recession_resistance", ("steam", "water vapor", "recession")),
        ("wear_resistance", ("wear", "fretting", "contact")),
        ("erosion_resistance", ("erosion",)),
        ("inspection_access_or_monitoring", ("inspection", "inspectability", "monitoring", "proof")),
        ("repairability_support", ("repair", "repairability", "maintenance")),
        ("transition_zone_management", ("gradient", "surface-to-core", "transition")),
        ("coating_interface_management", ("coating", "substrate_plus_coating", "interface", "bond coat")),
    ]
    output: list[dict[str, Any]] = []
    for function_id, terms in rules:
        matched = [term for term in terms if term in text]
        if not matched:
            continue
        record = _taxonomy_record(function_id, taxonomy)
        output.append(
            {
                "function_id": function_id,
                "function_kind": classify_function_kind(function_id),
                "display_name": _text(record.get("display_name"), function_id),
                "inferred_from": matched,
                "confidence": "high" if len(matched) >= 2 else "medium",
                "rationale": f"Requirement/design-space text contains: {', '.join(matched[:4])}.",
            }
        )
    return output


def infer_candidate_surface_functions(
    candidate: Mapping[str, Any],
    taxonomy: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    function_taxonomy = taxonomy or load_surface_function_taxonomy()
    text, field_text = _field_blob(candidate)
    output: list[dict[str, Any]] = []
    for function_id, record in function_taxonomy.items():
        if function_id == UNKNOWN_FUNCTION_ID:
            continue
        terms = [
            _text(term).lower()
            for term in _as_list(record.get("positive_keywords"))
            if _text(term) and _text(term).lower() in text
        ]
        if not terms:
            continue
        fields = [
            field
            for field, value in field_text.items()
            if any(term in value for term in terms)
        ]
        output.append(
            _function_record(
                function_id,
                function_taxonomy,
                terms,
                fields,
                f"Matched deterministic surface-function keywords: {', '.join(terms[:4])}.",
            )
        )

    candidate_class = _candidate_class(candidate)
    architecture = _architecture(candidate)
    if (candidate_class == "spatially_graded_am" or architecture == "spatial_gradient") and not any(
        item["function_id"] == "transition_zone_management" for item in output
    ):
        output.append(
            _function_record(
                "transition_zone_management",
                function_taxonomy,
                ["spatial_gradient"],
                ["candidate_class", "system_architecture_type"],
                "Spatial-gradient candidates carry transition-zone management intent.",
            )
        )
    if not output:
        record = _taxonomy_record(UNKNOWN_FUNCTION_ID, function_taxonomy)
        output.append(
            {
                "function_id": UNKNOWN_FUNCTION_ID,
                "function_kind": classify_function_kind(UNKNOWN_FUNCTION_ID),
                "display_name": _text(record.get("display_name"), UNKNOWN_FUNCTION_ID),
                "evidence_terms": [],
                "inferred_from_fields": [],
                "confidence": "low",
                "rationale": "No deterministic surface-function keywords were visible.",
            }
        )
    return output


def build_candidate_surface_function_profile(
    candidate: Mapping[str, Any],
    taxonomy: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    function_taxonomy = taxonomy or load_surface_function_taxonomy()
    functions = infer_candidate_surface_functions(candidate, function_taxonomy)
    function_ids = [item["function_id"] for item in functions]
    by_kind = {
        "primary_service_function": [],
        "secondary_service_function": [],
        "support_or_lifecycle_consideration": [],
        "risk_or_interface_consideration": [],
    }
    for function_id in function_ids:
        kind = classify_function_kind(function_id)
        if kind in by_kind:
            by_kind[kind].append(function_id)
    unknown = function_ids == [UNKNOWN_FUNCTION_ID]
    supporting_fields = sorted(
        {
            field
            for function in functions
            for field in _as_list(function.get("inferred_from_fields"))
            if _text(field)
        }
    )
    cautions: list[str] = []
    for function in functions:
        record = _taxonomy_record(function["function_id"], function_taxonomy)
        cautions.extend(_text(item) for item in _as_list(record.get("negative_or_caution_keywords")) if _text(item))
    return {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "surface_functions": functions,
        "primary_surface_functions": function_ids[:3],
        "secondary_surface_functions": function_ids[3:],
        "primary_service_functions": by_kind["primary_service_function"],
        "secondary_service_functions": by_kind["secondary_service_function"],
        "support_or_lifecycle_considerations": by_kind["support_or_lifecycle_consideration"],
        "risk_or_interface_considerations": by_kind["risk_or_interface_consideration"],
        "unknown_surface_function_flag": unknown,
        "evidence_maturity": _evidence_maturity(candidate),
        "evidence_label": evidence_maturity_label(_evidence_maturity(candidate)),
        "process_route_template_id": _text(candidate.get("process_route_template_id"), "unknown_route"),
        "supporting_fields": supporting_fields,
        "cautions": list(dict.fromkeys(cautions))[:8],
    }


def _candidates(package: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]


def _function_ids_from_candidate(candidate: Mapping[str, Any]) -> list[str]:
    profile = _mapping(candidate.get("surface_function_profile"))
    if profile:
        return [
            _text(item.get("function_id"))
            for item in _as_list(profile.get("surface_functions"))
            if isinstance(item, Mapping) and _text(item.get("function_id"))
        ]
    return [
        _text(item.get("function_id"))
        for item in infer_candidate_surface_functions(candidate)
        if _text(item.get("function_id"))
    ]


def _profile_ids_by_kind(candidate: Mapping[str, Any], kind: str) -> list[str]:
    profile = _mapping(candidate.get("surface_function_profile"))
    field_by_kind = {
        "primary_service_function": "primary_service_functions",
        "secondary_service_function": "secondary_service_functions",
        "support_or_lifecycle_consideration": "support_or_lifecycle_considerations",
        "risk_or_interface_consideration": "risk_or_interface_considerations",
    }
    field = field_by_kind.get(kind)
    if profile and field:
        return [_text(item) for item in _as_list(profile.get(field)) if _text(item)]
    return [function_id for function_id in _function_ids_from_candidate(candidate) if classify_function_kind(function_id) == kind]


def _function_to_candidate_ids(candidate_to_functions: Mapping[str, Sequence[str]]) -> dict[str, list[str]]:
    output: dict[str, list[str]] = {}
    for candidate_id, function_ids in candidate_to_functions.items():
        for function_id in function_ids:
            output.setdefault(function_id, []).append(candidate_id)
    return {
        function_id: sorted(candidate_ids)
        for function_id, candidate_ids in sorted(output.items())
    }


def _is_coating(candidate: Mapping[str, Any]) -> bool:
    return _candidate_class(candidate) == "coating_enabled" or _architecture(candidate) == "substrate_plus_coating"


def _is_gradient(candidate: Mapping[str, Any]) -> bool:
    return _candidate_class(candidate) == "spatially_graded_am" or _architecture(candidate) == "spatial_gradient"


def build_surface_function_coverage_summary(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = _candidates(package)
    required = [
        dict(item)
        for item in _as_list(package.get("required_surface_functions"))
        if isinstance(item, Mapping)
    ] or infer_required_surface_functions(package.get("requirement_schema"), package.get("design_space"))
    candidate_to_functions = {
        _candidate_id(candidate): _function_ids_from_candidate(candidate)
        for candidate in candidates
    }
    candidate_to_primary = {
        _candidate_id(candidate): _profile_ids_by_kind(candidate, "primary_service_function")
        for candidate in candidates
    }
    candidate_to_secondary = {
        _candidate_id(candidate): _profile_ids_by_kind(candidate, "secondary_service_function")
        for candidate in candidates
    }
    candidate_to_support = {
        _candidate_id(candidate): _profile_ids_by_kind(candidate, "support_or_lifecycle_consideration")
        for candidate in candidates
    }
    candidate_to_risk = {
        _candidate_id(candidate): _profile_ids_by_kind(candidate, "risk_or_interface_consideration")
        for candidate in candidates
    }
    function_to_candidate_ids = _function_to_candidate_ids(candidate_to_functions)
    primary_function_to_candidate_ids = _function_to_candidate_ids(candidate_to_primary)
    secondary_function_to_candidate_ids = _function_to_candidate_ids(candidate_to_secondary)
    support_function_to_candidate_ids = _function_to_candidate_ids(candidate_to_support)
    risk_function_to_candidate_ids = _function_to_candidate_ids(candidate_to_risk)
    coating_counter: Counter[str] = Counter()
    gradient_counter: Counter[str] = Counter()
    for candidate in candidates:
        function_ids = candidate_to_functions[_candidate_id(candidate)]
        if _is_coating(candidate):
            coating_counter.update(function_ids)
        if _is_gradient(candidate):
            gradient_counter.update(function_ids)
    coating_functions = set(coating_counter)
    gradient_functions = set(gradient_counter)
    coating_primary = {
        function_id
        for candidate in candidates
        if _is_coating(candidate)
        for function_id in candidate_to_primary[_candidate_id(candidate)]
    }
    gradient_primary = {
        function_id
        for candidate in candidates
        if _is_gradient(candidate)
        for function_id in candidate_to_primary[_candidate_id(candidate)]
    }
    coating_support = {
        function_id
        for candidate in candidates
        if _is_coating(candidate)
        for function_id in candidate_to_support[_candidate_id(candidate)] + candidate_to_risk[_candidate_id(candidate)]
    }
    gradient_support = {
        function_id
        for candidate in candidates
        if _is_gradient(candidate)
        for function_id in candidate_to_support[_candidate_id(candidate)] + candidate_to_risk[_candidate_id(candidate)]
    }
    required_ids = [
        _text(item.get("function_id"))
        for item in required
        if isinstance(item, Mapping) and _text(item.get("function_id"))
    ]
    required_primary_ids = [
        function_id
        for function_id in required_ids
        if classify_function_kind(function_id) == "primary_service_function"
    ]
    covered_primary = sorted(
        function_id for function_id in required_primary_ids if function_id in primary_function_to_candidate_ids
    )
    uncovered_primary = sorted(
        function_id for function_id in required_primary_ids if function_id not in primary_function_to_candidate_ids
    )
    unknown_ids = [
        candidate_id
        for candidate_id, function_ids in candidate_to_functions.items()
        if function_ids == [UNKNOWN_FUNCTION_ID] or UNKNOWN_FUNCTION_ID in function_ids
    ]
    warnings = []
    caveats = []
    if unknown_ids:
        warnings.append("Some candidates have unknown surface-function classification.")
    if required_primary_ids and not covered_primary:
        caveats.append("Required primary service functions are not visibly covered by candidate primary-service classifications.")
    if not (coating_primary & gradient_primary) and (coating_support & gradient_support):
        caveats.append(
            "Shared coating/gradient coverage is mainly support, lifecycle or interface considerations rather than primary service functions."
        )
    return {
        "candidate_count": len(candidates),
        "required_surface_functions": required,
        "candidate_function_counts": {
            candidate_id: len(function_ids)
            for candidate_id, function_ids in sorted(candidate_to_functions.items())
        },
        "function_to_candidate_ids": function_to_candidate_ids,
        "primary_service_function_to_candidate_ids": primary_function_to_candidate_ids,
        "secondary_service_function_to_candidate_ids": secondary_function_to_candidate_ids,
        "support_consideration_to_candidate_ids": support_function_to_candidate_ids,
        "risk_consideration_to_candidate_ids": risk_function_to_candidate_ids,
        "candidate_to_function_ids": {
            candidate_id: list(function_ids)
            for candidate_id, function_ids in sorted(candidate_to_functions.items())
        },
        "unknown_surface_function_candidate_ids": sorted(unknown_ids),
        "coating_enabled_function_counts": dict(sorted(coating_counter.items())),
        "spatial_gradient_function_counts": dict(sorted(gradient_counter.items())),
        "shared_coating_gradient_functions": sorted(coating_functions & gradient_functions),
        "covered_required_primary_service_functions": covered_primary,
        "uncovered_required_primary_service_functions": uncovered_primary,
        "shared_coating_gradient_primary_service_functions": sorted(coating_primary & gradient_primary),
        "shared_coating_gradient_support_considerations": sorted(coating_support & gradient_support),
        "functions_only_seen_in_coatings": sorted(coating_functions - gradient_functions),
        "functions_only_seen_in_gradients": sorted(gradient_functions - coating_functions),
        "functions_only_seen_in_coatings_primary": sorted(coating_primary - gradient_primary),
        "functions_only_seen_in_gradients_primary": sorted(gradient_primary - coating_primary),
        "coverage_caveats": caveats,
        "warnings": warnings,
    }


def compare_required_surface_functions_to_candidates(package: Mapping[str, Any]) -> dict[str, Any]:
    summary = build_surface_function_coverage_summary(package)
    required_ids = [
        _text(item.get("function_id"))
        for item in _as_list(summary.get("required_surface_functions"))
        if isinstance(item, Mapping) and _text(item.get("function_id"))
    ]
    available = set(summary["function_to_candidate_ids"])
    primary_available = set(summary.get("primary_service_function_to_candidate_ids", {}))
    covered = sorted(function_id for function_id in required_ids if function_id in available)
    uncovered = sorted(function_id for function_id in required_ids if function_id not in available)
    primary_required = [
        function_id
        for function_id in required_ids
        if classify_function_kind(function_id) == "primary_service_function"
    ]
    support_required = [
        function_id
        for function_id in required_ids
        if classify_function_kind(function_id)
        in {"support_or_lifecycle_consideration", "risk_or_interface_consideration"}
    ]
    covered_primary = sorted(function_id for function_id in primary_required if function_id in primary_available)
    uncovered_primary = sorted(function_id for function_id in primary_required if function_id not in primary_available)
    covered_support = sorted(function_id for function_id in support_required if function_id in available)
    records = [
        {
            "required_function_id": function_id,
            "function_kind": classify_function_kind(function_id),
            "candidate_ids": summary["function_to_candidate_ids"].get(function_id, []),
            "coverage_status": "covered" if function_id in available else "not_visible",
            "primary_service_coverage_status": (
                "covered_as_primary_service_function"
                if function_id in primary_available
                else "not_primary_service_coverage"
            ),
        }
        for function_id in required_ids
    ]
    notes = [
        "Surface-function coverage is descriptive only.",
        "No score, rank, winner or final decision is produced.",
    ]
    warnings = []
    if uncovered:
        warnings.append("Some required surface functions are not visible in candidate classifications.")
    if uncovered_primary:
        warnings.append("Some required primary service functions are not visible as primary-service candidate coverage.")
    return {
        "required_function_ids": required_ids,
        "covered_required_function_ids": covered,
        "uncovered_required_function_ids": uncovered,
        "covered_required_primary_service_function_ids": covered_primary,
        "uncovered_required_primary_service_function_ids": uncovered_primary,
        "covered_required_support_consideration_ids": covered_support,
        "candidate_coverage_records": records,
        "coverage_notes": notes,
        "warnings": warnings,
    }


def attach_surface_function_profiles(package: Mapping[str, Any]) -> dict[str, Any]:
    taxonomy = load_surface_function_taxonomy()
    output = dict(package)
    enriched_candidates = []
    for candidate in _candidates(package):
        enriched = dict(candidate)
        enriched["surface_function_profile"] = build_candidate_surface_function_profile(enriched, taxonomy)
        enriched_candidates.append(enriched)
    output["candidate_systems"] = enriched_candidates
    output["required_surface_functions"] = infer_required_surface_functions(
        package.get("requirement_schema"),
        package.get("design_space"),
    )
    output["surface_function_coverage_summary"] = build_surface_function_coverage_summary(output)
    output["surface_function_required_coverage"] = compare_required_surface_functions_to_candidates(output)
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics["surface_function_profiles_attached"] = True
    output["diagnostics"] = diagnostics
    warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    for warning in output["surface_function_coverage_summary"].get("warnings", []):
        if warning not in warnings:
            warnings.append(warning)
    output["warnings"] = warnings
    return output
