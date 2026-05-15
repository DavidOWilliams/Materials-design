from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.contracts import evidence_maturity_label
from src.material_system_schema import MaterialSystemCandidate


_SCORE_COLUMNS: dict[str, str] = {
    "creep_score": "creep",
    "toughness_score": "toughness",
    "temperature_score": "temperature",
    "through_life_cost_score": "through_life_cost",
    "sustainability_score_v1": "sustainability",
    "manufacturability_score": "manufacturability",
    "route_suitability_score": "route_suitability",
    "supply_risk_score": "supply_risk",
    "evidence_maturity_score": "evidence_maturity",
    "recipe_support_score": "recipe_support",
}


def _present(value: Any) -> bool:
    try:
        if value != value:
            return False
    except Exception:
        pass
    return value is not None and str(value).strip() != ""


def _text(row: Mapping[str, Any], key: str, default: str = "") -> str:
    value = row.get(key)
    if not _present(value):
        return default
    return str(value).strip()


def _stable_fallback_candidate_id(row: Mapping[str, Any]) -> str:
    for key in ("composition_concept", "formula_pretty", "source_alloy_name", "chemsys"):
        value = _text(row, key)
        if value:
            normalized = "_".join(value.lower().split())
            normalized = "".join(ch for ch in normalized if ch.isalnum() or ch in "-_")
            if normalized:
                return f"build31-metallic-{normalized}"
    return "build31-metallic-unknown"


def _system_name(row: Mapping[str, Any], candidate_id: str) -> str:
    for key in ("composition_concept", "formula_pretty", "source_alloy_name"):
        value = _text(row, key)
        if value:
            return value
    return candidate_id


def _source_type(row: Mapping[str, Any]) -> str:
    return _text(row, "candidate_source", "build31_metallic_baseline")


def _is_generated_or_research(source_type: str, row: Mapping[str, Any]) -> bool:
    source = source_type.lower()
    role = _text(row, "candidate_role").lower()
    return any(token in source or token in role for token in ("generated", "research"))


def _evidence_maturity(row: Mapping[str, Any]) -> str:
    source = _source_type(row).lower()
    has_named_analogue = bool(
        _text(row, "matched_alloy_name")
        or _text(row, "source_alloy_name")
        or _text(row, "named_analogue")
    )

    if source == "engineering_analogue" and has_named_analogue:
        return "B"
    if source == "engineering_analogue":
        return "C"
    if source == "materials_project" or "exploratory" in source or "database" in source:
        return "E"
    if "generated" in source or "research" in source:
        return "F"
    return "E"


def _evidence_package(row: Mapping[str, Any], maturity: str) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "maturity": maturity,
        "maturity_label": evidence_maturity_label(maturity),
        "sources": [_source_type(row)],
        "validation_gaps": [],
        "assumptions": ["Adapted from existing Build 3.1 metallic candidate row."],
    }

    for key in (
        "evidence_maturity_score",
        "candidate_source",
        "candidate_role",
        "provenance",
        "matched_alloy_name",
        "recipe_mode",
    ):
        value = row.get(key)
        if _present(value):
            evidence[key] = value

    matched_alloy_name = _text(row, "matched_alloy_name") or _text(row, "source_alloy_name")
    if matched_alloy_name:
        evidence["engineering_analogues"] = [matched_alloy_name]

    provenance = row.get("provenance")
    if _present(provenance):
        evidence["database_refs"] = [str(provenance)]

    return evidence


def _factor_scores(row: Mapping[str, Any], evidence: dict[str, Any]) -> list[dict[str, Any]]:
    factor_scores: list[dict[str, Any]] = []
    for column, factor in _SCORE_COLUMNS.items():
        value = row.get(column)
        if not _present(value):
            continue
        try:
            score = float(value)
        except (TypeError, ValueError):
            continue
        factor_scores.append(
            {
                "factor": factor,
                "score": score,
                "reason": f"Mapped from Build 3.1 column {column}.",
                "evidence": evidence,
            }
        )
    return factor_scores


def _processing_routes(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    route_name = _text(row, "base_process_route") or _text(row, "manufacturing_primary_route")
    route: dict[str, Any] = {}
    if route_name:
        route["route_name"] = route_name
    manufacturing_primary_route = _text(row, "manufacturing_primary_route")
    if manufacturing_primary_route:
        route["route_family"] = manufacturing_primary_route
    recipe_mode = _text(row, "recipe_mode")
    if recipe_mode:
        route["qualification_notes"] = f"Build 3.1 recipe mode: {recipe_mode}"
    return [route] if route else []


def _uncertainty_flags(
    row: Mapping[str, Any],
    maturity: str,
    processing_routes: list[dict[str, Any]],
) -> list[str]:
    flags: list[str] = []
    source = _source_type(row).lower()
    role = _text(row, "candidate_role").lower()

    if "theoretical" in source or "theoretical" in role:
        flags.append("Theoretical candidate; requires experimental validation.")
    if maturity in {"D", "E", "F"}:
        flags.append(f"Low evidence maturity ({maturity}); treat as exploratory.")
    if not processing_routes:
        flags.append("Missing process route in Build 3.1 source row.")
    if source == "materials_project" or "exploratory" in source:
        flags.append("Materials Project or exploratory database source; not a qualified alloy record.")
    return flags


def build_material_system_candidate_from_build31_row(
    row: Mapping[str, Any],
    requirements: Mapping[str, Any] | None = None,
) -> MaterialSystemCandidate:
    """Adapt one Build 3.1 metallic row to the Build 4 material-system contract."""
    del requirements

    candidate_id = _text(row, "candidate_id") or _stable_fallback_candidate_id(row)
    system_name = _system_name(row, candidate_id)
    source_type = _source_type(row)
    maturity = _evidence_maturity(row)
    evidence = _evidence_package(row, maturity)
    processing_routes = _processing_routes(row)
    uncertainty_flags = _uncertainty_flags(row, maturity, processing_routes)
    generated_candidate_flag = _is_generated_or_research(source_type, row)

    composition = _text(row, "composition_concept") or _text(row, "chemsys")
    constituent: dict[str, Any] = {"role": "substrate"}
    material_family = _text(row, "material_family")
    if material_family:
        constituent["material_family"] = material_family
    if composition:
        constituent["composition"] = {"description": composition}

    certification_risk_flags: list[str] = []
    if maturity in {"D", "E", "F"}:
        certification_risk_flags.append(
            f"Evidence maturity {maturity} is below conservative certification readiness."
        )

    candidate: MaterialSystemCandidate = {
        "candidate_id": candidate_id,
        "name": system_name,
        "system_name": system_name,
        "system_class": "metallic",
        "system_classes": ["metallic"],
        "candidate_class": "metallic",
        "system_architecture_type": "bulk_material",
        "base_material_family": material_family,
        "constituents": [constituent],
        "processing_routes": processing_routes,
        "process_route": processing_routes[0] if processing_routes else {},
        "factor_scores": _factor_scores(row, evidence),
        "evidence": evidence,
        "evidence_package": evidence,
        "evidence_maturity": maturity,
        "maturity_rationale": evidence_maturity_label(maturity),
        "source_type": source_type,
        "generated_by_adapter": "build31_metallic_adapter",
        "generated_candidate_flag": generated_candidate_flag,
        "research_generated": generated_candidate_flag,
        "research_mode_flag": False,
        "assumptions": evidence["assumptions"],
        "risks": uncertainty_flags + certification_risk_flags,
        "uncertainty_flags": uncertainty_flags,
        "certification_risk_flags": certification_risk_flags,
        "validation_plan": [],
        "provenance": {"build31_row": dict(row), "adapter": "build31_metallic_adapter"},
    }
    return candidate


def wrap_build31_dataframe(
    df: Any,
    requirements: Mapping[str, Any] | None = None,
) -> list[MaterialSystemCandidate]:
    """Adapt every row in a Build 3.1 dataframe without mutating the dataframe."""
    return [
        build_material_system_candidate_from_build31_row(row, requirements=requirements)
        for row in df.to_dict(orient="records")
    ]
