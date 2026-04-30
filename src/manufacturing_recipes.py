
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.alloy_analogue_matcher import (
    FAMILY_NORMALIZATION,
    load_alloy_knowledge_table,
    match_candidates_to_analogues,
)
from src.route_templates import render_manufacturing_recipe


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _candidate_table_paths() -> List[Path]:
    root = _project_root()
    return [
        root / "data" / "starter_alloy_knowledge_table_seed_rows.csv",
        root / "starter_alloy_knowledge_table_seed_rows.csv",
        root / "data" / "starter_alloy_knowledge_table.xlsx",
        root / "starter_alloy_knowledge_table.xlsx",
        root / "data" / "starter_alloy_knowledge_table_seed_rows.json",
        root / "starter_alloy_knowledge_table_seed_rows.json",
    ]


def _find_knowledge_table_path(custom_path: Any = None) -> Optional[Path]:
    if custom_path:
        candidate = Path(str(custom_path)).expanduser()
        if candidate.exists():
            return candidate
    for candidate in _candidate_table_paths():
        if candidate.exists():
            return candidate
    return None


def _normalize_family(family: Any) -> str:
    if family is None:
        return "Unknown"
    value = str(family).strip()
    return FAMILY_NORMALIZATION.get(value, value)


def _default_template_key(candidate_row: pd.Series) -> str:
    family = _normalize_family(candidate_row.get("material_family"))
    return f"{family.lower().replace('-', '_')}_family_envelope"


def _fallback_match_rows(candidates_df: pd.DataFrame, reason: str = "") -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for _, row in candidates_df.iterrows():
        family = _normalize_family(row.get("material_family"))
        rows.append(
            {
                "candidate_id": str(row.get("candidate_id", "")),
                "recipe_mode": "family_envelope",
                "analogue_match_class": "family_envelope",
                "matched_alloy_id": None,
                "matched_alloy_name": None,
                "matched_family": family,
                "analogue_similarity_score": 0.0,
                "analogue_route_compatibility_score": 0.0,
                "analogue_confidence": "Low",
                "analogue_explanation": (
                    reason
                    or "No alloy knowledge table was found; using family-envelope recipe generation."
                ),
                "primary_template_key": _default_template_key(row),
                "candidate_family_normalized": family,
                "candidate_elements": [],
                "analogue_weighted_score": 0.0,
                "analogue_base_component": 0.0,
                "analogue_major_component": 0.0,
                "analogue_secondary_component": 0.0,
                "analogue_chemistry_penalty": 0.0,
                "analogue_alloy_likeness_input": 0.0,
                "analogue_stable_bonus": 0.0,
                "analogue_theoretical_penalty": 0.0,
                "analogue_family_candidate_count": 0,
                "top_analogue_candidates_json": "[]",
            }
        )
    return pd.DataFrame(rows)


def _confidence_to_numeric(value: Any) -> float:
    mapping = {
        "High": 88.0,
        "Medium": 72.0,
        "Medium-Low": 60.0,
        "Low": 45.0,
    }
    return mapping.get(str(value or "").strip(), 45.0)


def _schema_alignment_component(candidate_row: pd.Series, requirements: Optional[Dict[str, Any]] = None) -> float:
    requirements = requirements or {}
    active_factors = list(requirements.get("active_factor_set") or requirements.get("scope_plan", {}).get("active_factor_set", []) or [])
    optional_score_cols = {
        "lightweight": "lightweight_score",
        "oxidation": "oxidation_score",
        "hot_corrosion": "hot_corrosion_score",
        "wear": "wear_score",
        "erosion": "erosion_score",
        "fatigue": "fatigue_score",
        "thermal_fatigue": "thermal_fatigue_score",
        "repairability": "repairability_score",
        "certification_maturity": "certification_maturity_score",
    }
    scores: List[float] = []
    for factor in active_factors:
        col = optional_score_cols.get(factor)
        if col and col in candidate_row.index:
            try:
                scores.append(float(candidate_row.get(col, 0.0) or 0.0))
            except Exception:
                pass
    if not scores:
        return 0.0
    avg = sum(scores) / len(scores)
    return round(max(-2.0, min(5.0, (avg - 60.0) * 0.10)), 2)


def _recipe_support_components(candidate_row: pd.Series, match_row: pd.Series, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    mode = str(match_row.get("recipe_mode", "") or "")
    similarity = float(match_row.get("analogue_similarity_score", 0.0) or 0.0) * 100.0
    route_match = float(match_row.get("analogue_route_compatibility_score", 0.0) or 0.0) * 100.0
    analogue_confidence = _confidence_to_numeric(match_row.get("analogue_confidence"))

    manufacturability = float(candidate_row.get("manufacturability_score", 50.0) or 50.0)
    route_suitability = float(candidate_row.get("route_suitability_score", 50.0) or 50.0)
    evidence = float(candidate_row.get("evidence_maturity_score", 50.0) or 50.0)
    alloy_likeness = float(candidate_row.get("alloy_likeness_score", 50.0) or 50.0)

    stable = bool(candidate_row.get("is_stable", False))
    theoretical = bool(candidate_row.get("theoretical", True))

    components = {
        "analogue_confidence_component": round(analogue_confidence * 0.18, 2),
        "analogue_similarity_component": round(similarity * 0.22, 2),
        "route_match_component": round(route_match * 0.12, 2),
        "manufacturability_component": round(manufacturability * 0.18, 2),
        "route_suitability_component": round(route_suitability * 0.12, 2),
        "evidence_component": round(evidence * 0.12, 2),
        "alloy_likeness_component": round(alloy_likeness * 0.06, 2),
        "schema_alignment_component": _schema_alignment_component(candidate_row, requirements),
        "mode_adjustment": 6.0 if mode == "named_analogue" else 2.0 if mode == "analogue_guided" else -6.0,
        "stable_adjustment": 3.0 if stable else 0.0,
        "theoretical_adjustment": -5.0 if theoretical else 0.0,
    }
    return components


def _recipe_support_score(candidate_row: pd.Series, match_row: pd.Series, requirements: Optional[Dict[str, Any]] = None) -> float:
    components = _recipe_support_components(candidate_row, match_row, requirements=requirements)
    score = sum(components.values())
    return round(max(20.0, min(95.0, score)), 2)


def _ingredient_summary(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No ingredient view available."
    bits: List[str] = []
    for row in rows[:5]:
        element = str(row.get("element", "") or "").strip()
        range_hint = str(row.get("range_hint", "") or "").strip()
        if element and range_hint:
            bits.append(f"{element} ({range_hint})")
        elif element:
            bits.append(element)
    return ", ".join(bits)


def _steps_summary(steps: List[str]) -> str:
    if not steps:
        return "No process steps available."
    if len(steps) <= 2:
        return " -> ".join(steps)
    return " -> ".join(steps[:3]) + " -> ..."


def attach_manufacturing_recipes(candidates_df: pd.DataFrame, requirements: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    if candidates_df is None or len(candidates_df) == 0:
        return candidates_df

    evaluated = candidates_df.copy()
    custom_path = (requirements or {}).get("alloy_knowledge_table_path")
    table_path = _find_knowledge_table_path(custom_path)

    knowledge_table: Optional[pd.DataFrame] = None
    knowledge_table_error: Optional[str] = None

    if table_path is not None:
        try:
            knowledge_table = load_alloy_knowledge_table(table_path)
            match_df = match_candidates_to_analogues(evaluated, knowledge_table, requirements=requirements)
        except Exception as exc:
            knowledge_table_error = str(exc)
            match_df = _fallback_match_rows(
                evaluated,
                reason=(
                    "Knowledge table could not be loaded cleanly; using family-envelope recipe generation. "
                    + knowledge_table_error
                ),
            )
    else:
        knowledge_table_error = "No knowledge-table file was found in the expected locations."
        match_df = _fallback_match_rows(
            evaluated,
            reason="No knowledge-table file was found; using family-envelope recipe generation.",
        )

    recipe_packages: List[Dict[str, Any]] = []
    recipe_support_scores: List[float] = []
    recipe_support_breakdowns: List[str] = []

    for _, candidate_row in evaluated.iterrows():
        candidate_id = str(candidate_row.get("candidate_id", ""))
        matched_rows = match_df[match_df["candidate_id"].astype(str) == candidate_id]
        if matched_rows.empty:
            match_row = _fallback_match_rows(pd.DataFrame([candidate_row])).iloc[0]
        else:
            match_row = matched_rows.iloc[0]

        knowledge_row = None
        matched_alloy_id = match_row.get("matched_alloy_id")
        if knowledge_table is not None and matched_alloy_id:
            alloy_rows = knowledge_table[knowledge_table["alloy_id"].astype(str) == str(matched_alloy_id)]
            if not alloy_rows.empty:
                knowledge_row = alloy_rows.iloc[0]

        recipe_package = render_manufacturing_recipe(
            candidate_row,
            match_row,
            knowledge_row,
            requirements=requirements,
        )
        recipe_packages.append(recipe_package)
        recipe_support_scores.append(_recipe_support_score(candidate_row, match_row, requirements=requirements))
        recipe_support_breakdowns.append(json.dumps(_recipe_support_components(candidate_row, match_row, requirements=requirements)))

    for column in match_df.columns:
        if column == "candidate_id":
            continue
        evaluated[column] = match_df[column].values

    evaluated["recipe_support_score"] = recipe_support_scores
    evaluated["recipe_support_breakdown_json"] = recipe_support_breakdowns
    evaluated["manufacturing_template_title"] = [pkg["template_title"] for pkg in recipe_packages]
    evaluated["manufacturing_primary_route"] = [pkg["primary_route"] for pkg in recipe_packages]
    evaluated["manufacturing_secondary_route"] = [pkg["secondary_route"] for pkg in recipe_packages]
    evaluated["ingredient_rows"] = [pkg["ingredient_rows"] for pkg in recipe_packages]
    evaluated["ingredient_summary"] = [_ingredient_summary(pkg["ingredient_rows"]) for pkg in recipe_packages]
    evaluated["process_steps"] = [pkg["process_steps"] for pkg in recipe_packages]
    evaluated["process_steps_summary"] = [_steps_summary(pkg["process_steps"]) for pkg in recipe_packages]
    evaluated["recipe_watch_outs"] = [pkg["watch_outs"] for pkg in recipe_packages]
    evaluated["why_this_route"] = [pkg["why_this_route"] for pkg in recipe_packages]
    evaluated["recipe_provenance_refs"] = [pkg["provenance_refs"] for pkg in recipe_packages]
    evaluated["recipe_confidence"] = [pkg["recipe_confidence"] for pkg in recipe_packages]
    evaluated["recipe_layer_warning"] = knowledge_table_error or ""

    return evaluated
