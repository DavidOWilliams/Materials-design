from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

from src.alloy_analogue_matcher import FAMILY_NORMALIZATION, load_alloy_knowledge_table


SCOPE_TO_NORMALIZED_FAMILY = {
    "Ni-based superalloy": "Ni-based",
    "Co-based alloy": "Co-based",
    "Refractory alloy concept": "Refractory",
    "Ti alloy": "Ti-based",
    "Fe-Ni alloy": "Fe-Ni",
}

NORMALIZED_TO_CANDIDATE_FAMILY = {
    "Ni-based": "Ni-based superalloy-like candidate",
    "Co-based": "Co-based high-temperature candidate",
    "Refractory": "Refractory-alloy-like candidate",
    "Ti-based": "Ti-alloy-like candidate",
    "Fe-Ni": "Fe-Ni high-temperature candidate",
}

FAMILY_DENSITY_ESTIMATE = {
    "Ni-based": 8.3,
    "Co-based": 8.9,
    "Refractory": 10.4,
    "Ti-based": 4.5,
    "Fe-Ni": 8.1,
}

FAMILY_DEFAULT_ELEMENTS = {
    "Ni-based": ["Ni", "Cr", "Al", "Ti"],
    "Co-based": ["Co", "Cr", "W", "Ni"],
    "Refractory": ["Mo", "Nb", "Ta", "Ti"],
    "Ti-based": ["Ti", "Al", "V"],
    "Fe-Ni": ["Fe", "Ni", "Cr"],
}

FAMILY_SCORE_BASELINES = {
    "Ni-based": {
        "creep": 83,
        "toughness": 66,
        "temperature": 84,
        "cost": 48,
        "sustainability": 50,
        "engineering_plausibility": "Higher",
    },
    "Co-based": {
        "creep": 78,
        "toughness": 62,
        "temperature": 80,
        "cost": 36,
        "sustainability": 38,
        "engineering_plausibility": "Medium",
    },
    "Refractory": {
        "creep": 88,
        "toughness": 45,
        "temperature": 94,
        "cost": 31,
        "sustainability": 32,
        "engineering_plausibility": "Medium",
    },
    "Ti-based": {
        "creep": 56,
        "toughness": 78,
        "temperature": 63,
        "cost": 62,
        "sustainability": 66,
        "engineering_plausibility": "Higher",
    },
    "Fe-Ni": {
        "creep": 68,
        "toughness": 70,
        "temperature": 70,
        "cost": 58,
        "sustainability": 58,
        "engineering_plausibility": "Medium",
    },
}

FACTOR_KEYWORDS = {
    "creep": ["creep", "high temperature", "hot", "age", "gamma", "precipitation"],
    "temperature_suitability": ["high temperature", "thermal", "hot", "oxidation"],
    "lightweight": ["lightweight", "low density", "specific strength", "ti", "titanium"],
    "fatigue": ["fatigue", "fracture", "damage", "eli", "clean"],
    "thermal_fatigue": ["thermal fatigue", "thermal cycling", "fatigue"],
    "oxidation": ["oxidation", "corrosion", "chromium", "cr"],
    "hot_corrosion": ["hot corrosion", "corrosion", "salt", "sulfidation", "cr"],
    "wear": ["wear", "sliding", "seal", "stellite", "cobalt", "co"],
    "erosion": ["erosion", "wear", "surface"],
    "manufacturability": ["wrought", "forging", "powder", "lpbf", "am", "hip", "machining"],
    "route_suitability": ["wrought", "forging", "powder", "lpbf", "am", "hip", "dmls"],
    "repairability": ["repair", "weld", "welding", "machining"],
    "certification_maturity": ["aerospace", "mature", "qualified", "wrought", "known"],
}


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


def find_knowledge_table_path(custom_path: Any = None) -> Optional[Path]:
    if custom_path:
        candidate = Path(str(custom_path)).expanduser()
        if candidate.exists():
            return candidate
    for candidate in _candidate_table_paths():
        if candidate.exists():
            return candidate
    return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        out = float(value)
        if math.isnan(out):
            return default
        return out
    except Exception:
        return default


def _split_semicolon_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]


def _slug(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def _family_priors(requirements: Dict[str, Any]) -> Dict[str, float]:
    priors = requirements.get("family_priors")
    if not priors:
        priors = (requirements.get("scope_plan", {}) or {}).get("family_priors")
    if not isinstance(priors, dict):
        return {}
    out: Dict[str, float] = {}
    for family, value in priors.items():
        try:
            out[str(family)] = float(value)
        except Exception:
            continue
    return out


def _normalise_candidate_family_to_scope(value: Any) -> str:
    text = str(value or "")
    if "Ni-based" in text:
        return "Ni-based superalloy"
    if "Co-based" in text:
        return "Co-based alloy"
    if "Refractory" in text:
        return "Refractory alloy concept"
    if "Ti-alloy" in text or "Ti-based" in text:
        return "Ti alloy"
    if "Fe-Ni" in text:
        return "Fe-Ni alloy"
    return text


def _family_counts(mp_df: pd.DataFrame) -> Dict[str, int]:
    if mp_df is None or len(mp_df) == 0 or "material_family" not in mp_df.columns:
        return {}
    scope = mp_df["material_family"].map(_normalise_candidate_family_to_scope)
    return scope.value_counts().to_dict()


def _family_looks_weak(mp_df: pd.DataFrame, scope_family: str) -> bool:
    if mp_df is None or len(mp_df) == 0 or "material_family" not in mp_df.columns:
        return True
    subset = mp_df[mp_df["material_family"].map(_normalise_candidate_family_to_scope) == scope_family]
    if subset.empty:
        return True
    median_elements = _safe_float(subset.get("n_elements", pd.Series(dtype=float)).median(), 0.0)
    median_likeness = _safe_float(subset.get("alloy_likeness_score", pd.Series(dtype=float)).median(), 0.0)
    mp_only = True
    if "candidate_source" in subset.columns:
        mp_only = subset["candidate_source"].fillna("materials_project").astype(str).eq("materials_project").all()
    return bool(mp_only and (median_elements <= 3 or median_likeness <= 55))


def _scope_families_to_supplement(mp_df: pd.DataFrame, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    priors = _family_priors(requirements)
    if not priors:
        priors = {family: 0.5 for family in requirements.get("allowed_material_families", []) or []}
    if not priors:
        return []

    top_family = max(priors.items(), key=lambda item: item[1])[0]
    counts = _family_counts(mp_df)
    rows: List[Dict[str, Any]] = []

    for scope_family, prior in sorted(priors.items(), key=lambda item: item[1], reverse=True):
        if scope_family not in SCOPE_TO_NORMALIZED_FAMILY:
            continue
        mp_count = int(counts.get(scope_family, 0))
        weak_mp = _family_looks_weak(mp_df, scope_family)
        reason = ""
        limit = 0
        if prior >= 0.60:
            limit = 3
            reason = "high family prior"
            if weak_mp:
                reason += " and MP survivors are sparse/simplified"
        elif scope_family == top_family and prior >= 0.50 and (mp_count < 3 or weak_mp):
            limit = 3
            reason = "top prompt family under-represented or weak in MP survivors"
        elif prior >= 0.35 and mp_count < 2:
            limit = 2
            reason = "active family has fewer than two MP survivors"

        if limit > 0:
            rows.append(
                {
                    "scope_family": scope_family,
                    "normalized_family": SCOPE_TO_NORMALIZED_FAMILY[scope_family],
                    "prior": round(float(prior), 3),
                    "mp_survivor_count": mp_count,
                    "mp_family_looks_weak": bool(weak_mp),
                    "limit": limit,
                    "reason": reason,
                }
            )
    return rows


def _row_text(row: pd.Series) -> str:
    pieces = [
        row.get("alloy_id", ""),
        row.get("canonical_name", ""),
        row.get("family", ""),
        row.get("composition_elements", ""),
        row.get("base_element", ""),
        row.get("major_additions", ""),
        row.get("route_tags", ""),
        row.get("preferred_recipe_template", ""),
        row.get("known_watch_outs", ""),
        row.get("match_guardrails", ""),
        row.get("provenance_note", ""),
    ]
    return " ".join(str(piece) for piece in pieces if piece is not None).lower()


def _rank_knowledge_rows(
    family_rows: pd.DataFrame,
    *,
    scope_family: str,
    prior: float,
    requirements: Dict[str, Any],
) -> pd.DataFrame:
    if family_rows.empty:
        return family_rows

    active_factors = list(requirements.get("active_factor_set") or (requirements.get("scope_plan", {}) or {}).get("active_factor_set", []) or [])
    active_weights = dict(requirements.get("active_factor_weights") or (requirements.get("scope_plan", {}) or {}).get("active_factor_weights", {}) or {})
    am_preferred = bool(requirements.get("am_preferred", False))

    scores: List[float] = []
    reasons: List[str] = []
    for _, row in family_rows.iterrows():
        score = 50.0 + prior * 20.0
        reason_bits: List[str] = []
        am_supported = str(row.get("am_supported_norm", row.get("am_supported", "")) or "").strip().lower()
        route_tags = " ".join(row.get("route_tags_list", []) or _split_semicolon_values(row.get("route_tags"))).lower()
        text = _row_text(row) + " " + route_tags

        if am_preferred:
            if am_supported == "yes":
                score += 12.0
                reason_bits.append("AM-supported seed")
            elif am_supported == "limited":
                score += 7.0
                reason_bits.append("limited AM evidence")
            else:
                score -= 8.0

        for factor in active_factors:
            weight = _safe_float(active_weights.get(factor), 0.2)
            keywords = FACTOR_KEYWORDS.get(factor, [factor.replace("_", " ")])
            if any(keyword.lower() in text for keyword in keywords):
                score += max(2.0, 12.0 * weight)
                reason_bits.append(f"matches {factor.replace('_', ' ')} intent")

        if str(row.get("source_url_or_ref", "") or "").strip():
            score += 3.0
        if str(row.get("preferred_recipe_template", "") or "").strip():
            score += 4.0

        scores.append(round(score, 3))
        reasons.append("; ".join(dict.fromkeys(reason_bits)) or "family-prior selected seed")

    out = family_rows.copy()
    out["_kb_selection_score"] = scores
    out["_kb_selection_reason"] = reasons
    return out.sort_values(["_kb_selection_score", "canonical_name"], ascending=[False, True]).reset_index(drop=True)


def _elements_from_knowledge_row(row: pd.Series, normalized_family: str) -> List[str]:
    elements = list(row.get("composition_elements_list") or [])
    if not elements:
        elements = _split_semicolon_values(row.get("composition_elements"))
    base_element = str(row.get("base_element", "") or "").strip()
    major = list(row.get("major_additions_list") or []) or _split_semicolon_values(row.get("major_additions"))

    ordered: List[str] = []
    if base_element:
        ordered.append(base_element)
    ordered.extend(major)
    ordered.extend(elements)
    if not ordered:
        ordered = FAMILY_DEFAULT_ELEMENTS.get(normalized_family, [])

    deduped: List[str] = []
    seen = set()
    for element in ordered:
        token = str(element).strip()
        if not token or token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


def _am_capable_from_seed(row: pd.Series) -> str:
    value = str(row.get("am_supported_norm", row.get("am_supported", "")) or "").strip().lower()
    # The app's current AM preference step treats only "yes" as passable.  For curated
    # analogue rows, "limited" still means there is enough evidence to keep it visible,
    # while the route score and recipe notes continue to surface that limitation.
    return "yes" if value in {"yes", "limited"} else "no"


def _family_baselines(normalized_family: str, operating_temperature: float) -> Dict[str, Any]:
    base = dict(FAMILY_SCORE_BASELINES.get(normalized_family, FAMILY_SCORE_BASELINES["Ni-based"]))
    if operating_temperature >= 1000:
        if normalized_family == "Refractory":
            base["temperature"] = max(base["temperature"], 96)
            base["creep"] = max(base["creep"], 90)
        elif normalized_family == "Ni-based":
            # Keep Ni high-temperature analogues visible but avoid allowing mature Ni rows
            # to dominate explicitly refractory/extreme-temperature prompts automatically.
            base["temperature"] = min(base["temperature"], 82)
        elif normalized_family == "Co-based":
            base["temperature"] = min(base["temperature"], 79)

    if normalized_family == "Ti-based":
        if operating_temperature >= 750:
            base["temperature"] = min(base["temperature"], 46)
            base["creep"] = min(base["creep"], 48)
        elif operating_temperature >= 600:
            base["temperature"] = min(base["temperature"], 58)
            base["creep"] = min(base["creep"], 52)
        else:
            base["temperature"] = max(base["temperature"], 72)
    if normalized_family == "Refractory" and operating_temperature < 900:
        base["cost"] = min(base["cost"], 28)
        base["sustainability"] = min(base["sustainability"], 30)
    return base


def _candidate_row_from_knowledge_row(
    row: pd.Series,
    *,
    scope_family: str,
    normalized_family: str,
    requirements: Dict[str, Any],
    selection_reason: str,
) -> Dict[str, Any]:
    alloy_id = str(row.get("alloy_id", "") or "unknown")
    canonical_name = str(row.get("canonical_name", "") or alloy_id)
    elements = _elements_from_knowledge_row(row, normalized_family)
    chemsys = "-".join(elements)
    operating_temperature = _safe_float(requirements.get("operating_temperature"), 850.0)
    baselines = _family_baselines(normalized_family, operating_temperature)
    n_elements = len(elements)
    am_status = str(row.get("am_supported_norm", row.get("am_supported", "")) or "").strip().lower()
    route_tags = list(row.get("route_tags_list") or []) or _split_semicolon_values(row.get("route_tags"))
    provenance_note = str(row.get("provenance_note", "") or "Curated engineering analogue seed row.")

    note_bits = [
        "Engineering analogue candidate generated from the curated alloy knowledge table.",
        f"Selection reason: {selection_reason}.",
    ]
    if am_status:
        note_bits.append(f"AM support in seed table: {am_status}.")
    if provenance_note:
        note_bits.append(provenance_note)

    return {
        "candidate_id": f"kb_{_slug(alloy_id)}",
        "candidate_source": "engineering_analogue",
        "candidate_role": "known_engineering_reference",
        "source_alloy_id": alloy_id,
        "source_alloy_name": canonical_name,
        "source_family": scope_family,
        "source_provenance_note": provenance_note,
        "source_url_or_ref": str(row.get("source_url_or_ref", "") or ""),
        "source_selection_reason": selection_reason,
        "material_family": NORMALIZED_TO_CANDIDATE_FAMILY.get(normalized_family, f"{normalized_family} candidate"),
        "composition_concept": f"Engineering analogue: {canonical_name}",
        "base_process_route": str(row.get("preferred_recipe_template", "") or "Curated engineering analogue route"),
        "base_creep_score": int(baselines["creep"]),
        "base_toughness_score": int(baselines["toughness"]),
        "base_temp_score": int(baselines["temperature"]),
        "base_cost_score": int(baselines["cost"]),
        "base_sustainability_score": int(baselines["sustainability"]),
        "am_capable": _am_capable_from_seed(row),
        "mp_material_id": None,
        "formula_pretty": canonical_name,
        "chemsys": chemsys,
        "origin_requested_chemsys": f"knowledge_table::{scope_family}",
        "matched_query_chemsys": f"knowledge_table::{scope_family}",
        "retrieval_mode": "knowledge_table_seed",
        "requested_overlap_score": n_elements,
        "requested_distinguishing_bonus": 1,
        "n_elements": n_elements,
        "density": FAMILY_DENSITY_ESTIMATE.get(normalized_family, 8.0),
        "energy_above_hull": 0.0,
        "band_gap": 0.0,
        "is_stable": True,
        "theoretical": False,
        "classification_reason": "Curated engineering analogue retained as a knowledge-base candidate for this prompt scope.",
        "engineering_plausibility": baselines.get("engineering_plausibility", "Medium"),
        "alloy_likeness_score": 88 if n_elements >= 4 else 78,
        "alloy_likeness_reason": "Curated engineering alloy analogue from the project knowledge table rather than a raw crystal-structure record.",
        "generated_note": " ".join(note_bits),
        "baseline_survives": True,
        "baseline_rejection_stage": None,
        "baseline_rejection_reason": None,
        "diagnostic_family_match": True,
        "diagnostic_complexity_score": n_elements,
        "diagnostic_complexity_threshold": 3,
        "passed_complexity_gate": True,
        "knowledge_table_route_tags": "; ".join(route_tags),
    }


def add_engineering_analogue_candidates(
    mp_df: pd.DataFrame,
    requirements: Dict[str, Any],
    *,
    diagnostics: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Supplement MP survivors with curated engineering analogue candidates.

    This is intentionally explicit and diagnosable.  It does not loosen MP request-aware
    acceptance.  Instead it adds a separately labelled candidate source when the prompt
    strongly favours a family, or when a prompt-relevant family is sparse/weak in the MP
    survivor pool.
    """
    diagnostics = diagnostics if diagnostics is not None else {}
    base_df = mp_df.copy() if mp_df is not None else pd.DataFrame()
    if "candidate_source" not in base_df.columns and len(base_df) > 0:
        base_df["candidate_source"] = "materials_project"

    custom_path = requirements.get("alloy_knowledge_table_path")
    table_path = find_knowledge_table_path(custom_path)
    diagnostics.setdefault("engineering_analogue_supplementation", [])
    diagnostics["engineering_analogue_table_path"] = str(table_path) if table_path else None

    if table_path is None:
        diagnostics.setdefault("warnings", []).append(
            "Engineering analogue supplementation was skipped because no alloy knowledge table was found."
        )
        diagnostics["engineering_analogue_candidate_count"] = 0
        return base_df

    try:
        knowledge_table = load_alloy_knowledge_table(table_path)
    except Exception as exc:
        diagnostics.setdefault("warnings", []).append(
            f"Engineering analogue supplementation was skipped because the knowledge table could not be loaded: {exc}"
        )
        diagnostics["engineering_analogue_candidate_count"] = 0
        return base_df

    supplement_plan = _scope_families_to_supplement(base_df, requirements)
    diagnostics["engineering_analogue_supplementation_plan"] = supplement_plan

    rows: List[Dict[str, Any]] = []
    selected_ids: set[str] = set()
    existing_candidate_ids = set(base_df.get("candidate_id", pd.Series(dtype=str)).astype(str).tolist()) if len(base_df) > 0 else set()

    for plan in supplement_plan:
        normalized_family = plan["normalized_family"]
        family_rows = knowledge_table[knowledge_table["family_normalized"] == normalized_family].copy()
        if family_rows.empty:
            diagnostics["engineering_analogue_supplementation"].append(
                {
                    **plan,
                    "rows_added": 0,
                    "status": "no_seed_rows_for_family",
                }
            )
            continue

        ranked = _rank_knowledge_rows(
            family_rows,
            scope_family=plan["scope_family"],
            prior=float(plan["prior"]),
            requirements=requirements,
        )
        added = 0
        selected_names: List[str] = []
        for _, seed_row in ranked.iterrows():
            alloy_id = str(seed_row.get("alloy_id", "") or "unknown")
            candidate_id = f"kb_{_slug(alloy_id)}"
            if candidate_id in existing_candidate_ids or candidate_id in selected_ids:
                continue
            selected_ids.add(candidate_id)
            selected_names.append(str(seed_row.get("canonical_name", alloy_id)))
            rows.append(
                _candidate_row_from_knowledge_row(
                    seed_row,
                    scope_family=plan["scope_family"],
                    normalized_family=normalized_family,
                    requirements=requirements,
                    selection_reason=str(seed_row.get("_kb_selection_reason", plan["reason"])),
                )
            )
            added += 1
            if added >= int(plan["limit"]):
                break

        diagnostics["engineering_analogue_supplementation"].append(
            {
                **plan,
                "rows_added": added,
                "selected_analogues": selected_names,
                "status": "added" if added else "no_new_rows_selected",
            }
        )

    if rows:
        supplement_df = pd.DataFrame(rows)
        combined = pd.concat([base_df, supplement_df], ignore_index=True, sort=False)
    else:
        supplement_df = pd.DataFrame()
        combined = base_df

    diagnostics["engineering_analogue_candidate_count"] = int(len(supplement_df))
    diagnostics["mp_candidate_count_before_supplementation"] = int(len(base_df))
    diagnostics["candidate_count_after_supplementation"] = int(len(combined))
    if len(combined) > 0 and "candidate_source" in combined.columns:
        diagnostics["candidate_source_mix"] = combined["candidate_source"].fillna("materials_project").astype(str).value_counts().to_dict()
    else:
        diagnostics["candidate_source_mix"] = {}
    if len(combined) > 0 and "source_family" in combined.columns:
        supplement_family_mix = combined[combined["candidate_source"].fillna("") == "engineering_analogue"].get("source_family", pd.Series(dtype=str)).fillna("Unknown").astype(str).value_counts().to_dict()
        diagnostics["engineering_analogue_family_mix"] = supplement_family_mix
    else:
        diagnostics["engineering_analogue_family_mix"] = {}

    return combined
