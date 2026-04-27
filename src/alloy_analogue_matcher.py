
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

FAMILY_NORMALIZATION = {
    "Ni-based superalloy-like candidate": "Ni-based",
    "Co-based high-temperature candidate": "Co-based",
    "Refractory-alloy-like candidate": "Refractory",
    "Ti-alloy-like candidate": "Ti-based",
    "Fe-Ni high-temperature candidate": "Fe-Ni",
    "Ni-based": "Ni-based",
    "Co-based": "Co-based",
    "Refractory": "Refractory",
    "Ti-based": "Ti-based",
    "Fe-Ni": "Fe-Ni",
}

WEIGHT_BASE = 0.45
WEIGHT_MAJOR = 0.35
WEIGHT_SECONDARY = 0.20

REQUIRED_COLUMNS = {
    "alloy_id",
    "canonical_name",
    "family",
    "composition_elements",
    "base_element",
    "major_additions",
    "route_tags",
    "am_supported",
    "preferred_recipe_template",
    "known_watch_outs",
    "match_guardrails",
    "provenance_note",
    "source_url_or_ref",
}


def _split_semicolon_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    items = [str(v).strip() for v in str(value).split(";")]
    return [item for item in items if item]


def _parse_chemsys(chemsys: Any) -> List[str]:
    if chemsys is None:
        return []
    if isinstance(chemsys, float) and pd.isna(chemsys):
        return []
    return [e.strip() for e in str(chemsys).split("-") if e.strip()]


def _normalize_family(family: Any) -> str:
    if family is None:
        return "Unknown"
    value = str(family).strip()
    return FAMILY_NORMALIZATION.get(value, value)


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(col).strip().replace("\ufeff", "") for col in out.columns]
    return out


def _load_csv_with_fallbacks(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        df = _normalize_columns(df)
        if len(df.columns) > 1:
            return df
    except Exception:
        pass

    try:
        sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        df = pd.read_csv(path, sep=dialect.delimiter, engine="python", encoding="utf-8-sig")
        df = _normalize_columns(df)
        if len(df.columns) > 1:
            return df
    except Exception:
        pass

    try:
        df = pd.read_csv(path, sep="\t", engine="python", encoding="utf-8-sig")
        df = _normalize_columns(df)
        if len(df.columns) > 1:
            return df
    except Exception:
        pass

    try:
        df = pd.read_csv(path, sep=r"\s{2,}", engine="python", encoding="utf-8-sig")
        df = _normalize_columns(df)
        if len(df.columns) > 1:
            return df
    except Exception:
        pass

    df = pd.read_csv(path, encoding="utf-8-sig")
    return _normalize_columns(df)


def load_alloy_knowledge_table(path: str | Path, sheet_name: str = "Seed_Alloys") -> pd.DataFrame:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = _load_csv_with_fallbacks(path)
    elif suffix in {".xlsx", ".xlsm", ".xls"}:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name)
        except Exception:
            df = pd.read_excel(path)
        df = _normalize_columns(df)
    elif suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(raw, dict) and "rows" in raw:
            raw = raw["rows"]
        df = pd.DataFrame(raw)
        df = _normalize_columns(df)
    elif suffix == ".parquet":
        df = pd.read_parquet(path)
        df = _normalize_columns(df)
    else:
        raise ValueError(f"Unsupported knowledge-table file type: {path.suffix}")

    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(
            f"Knowledge table is missing required columns: {sorted(missing)}. "
            f"Detected columns: {list(df.columns)}"
        )

    out = df.copy()
    out["family_normalized"] = out["family"].apply(_normalize_family)
    out["composition_elements_list"] = out["composition_elements"].apply(_split_semicolon_values)
    out["major_additions_list"] = out["major_additions"].apply(_split_semicolon_values)
    out["route_tags_list"] = out["route_tags"].apply(_split_semicolon_values)
    out["am_supported_norm"] = out["am_supported"].astype(str).str.strip().str.lower()
    return out


def _base_match_score(candidate_elements: set[str], analogue_row: pd.Series, family_normalized: str) -> float:
    if family_normalized == "Refractory":
        analogue_base = analogue_row.get("base_element")
        if analogue_base in candidate_elements:
            return WEIGHT_BASE
        return WEIGHT_BASE * 0.5 if candidate_elements.intersection({"Mo", "Nb", "Ta", "W"}) else 0.0

    analogue_base = str(analogue_row.get("base_element") or "").strip()
    if analogue_base and analogue_base in candidate_elements:
        return WEIGHT_BASE
    return 0.0


def _major_match_score(candidate_elements: set[str], analogue_row: pd.Series) -> float:
    major_additions = set(analogue_row.get("major_additions_list") or [])
    if not major_additions:
        return 0.0
    overlap = len(candidate_elements.intersection(major_additions))
    return WEIGHT_MAJOR * (overlap / len(major_additions))


def _secondary_match_score(candidate_elements: set[str], analogue_row: pd.Series) -> float:
    analogue_elements = set(analogue_row.get("composition_elements_list") or [])
    major_additions = set(analogue_row.get("major_additions_list") or [])
    analogue_base = str(analogue_row.get("base_element") or "").strip()
    secondary = analogue_elements - major_additions
    if analogue_base:
        secondary.discard(analogue_base)
    if not secondary:
        return 0.0
    overlap = len(candidate_elements.intersection(secondary))
    return WEIGHT_SECONDARY * (overlap / len(secondary))


def _chemistry_penalty(candidate_elements: set[str], analogue_row: pd.Series) -> float:
    analogue_elements = set(analogue_row.get("composition_elements_list") or [])
    extra_elements = candidate_elements - analogue_elements
    return 0.05 * min(len(extra_elements), 3) if extra_elements else 0.0


def _route_compatibility(analogue_row: pd.Series, am_preferred: bool) -> float:
    route_tags = set(analogue_row.get("route_tags_list") or [])
    am_supported = str(analogue_row.get("am_supported_norm") or "no")

    if am_preferred:
        if am_supported == "yes":
            return 1.0
        if am_supported == "limited":
            return 0.65
        if any("LPBF" in tag or "DMLS" in tag or "HIP" in tag for tag in route_tags):
            return 0.9
        return 0.3

    if any(tag in route_tags for tag in {"wrought", "forging", "welding", "forming", "powder_metallurgy", "machining"}):
        return 1.0
    return 0.7


def score_candidate_against_analogue(candidate_row: pd.Series, analogue_row: pd.Series, *, am_preferred: bool = False) -> Dict[str, Any]:
    candidate_family = _normalize_family(candidate_row.get("material_family"))
    analogue_family = _normalize_family(analogue_row.get("family"))
    candidate_elements = set(_parse_chemsys(candidate_row.get("chemsys")))

    if candidate_family != analogue_family:
        return {
            "family_match": False,
            "similarity_score": 0.0,
            "route_compatibility_score": 0.0,
            "weighted_score": 0.0,
            "candidate_elements": sorted(candidate_elements),
            "explanation_bits": ["Family mismatch."],
            "base_component": 0.0,
            "major_component": 0.0,
            "secondary_component": 0.0,
            "chemistry_penalty": 0.0,
            "alloy_likeness_input": 0.0,
            "stable_bonus": 0.0,
            "theoretical_penalty": 0.0,
        }

    base_component = _base_match_score(candidate_elements, analogue_row, candidate_family)
    major_component = _major_match_score(candidate_elements, analogue_row)
    secondary_component = _secondary_match_score(candidate_elements, analogue_row)
    chemistry_penalty = _chemistry_penalty(candidate_elements, analogue_row)
    similarity_score = max(0.0, base_component + major_component + secondary_component - chemistry_penalty)
    route_score = _route_compatibility(analogue_row, am_preferred=am_preferred)

    alloy_likeness = float(candidate_row.get("alloy_likeness_score", 50.0) or 50.0) / 100.0
    stable_bonus = 0.04 if bool(candidate_row.get("is_stable", False)) else 0.0
    theoretical_penalty = 0.05 if bool(candidate_row.get("theoretical", True)) else 0.0

    explanation_bits = [
        f"Family match on {candidate_family}.",
        f"Base={base_component:.2f}.",
        f"Major additions={major_component:.2f}.",
        f"Secondary additions={secondary_component:.2f}.",
        f"Route={route_score:.2f}.",
        f"Alloy-likeness input={alloy_likeness:.2f}.",
    ]
    if chemistry_penalty > 0:
        explanation_bits.append(f"Chemistry-drift penalty={chemistry_penalty:.2f}.")
    if stable_bonus > 0:
        explanation_bits.append("Stable bonus applied.")
    if theoretical_penalty > 0:
        explanation_bits.append("Theoretical penalty applied.")

    weighted_score = (
        (similarity_score * 0.68)
        + (route_score * 0.17)
        + (alloy_likeness * 0.15)
        + stable_bonus
        - theoretical_penalty
    )
    return {
        "family_match": True,
        "similarity_score": round(similarity_score, 4),
        "route_compatibility_score": round(route_score, 4),
        "weighted_score": round(weighted_score, 4),
        "candidate_elements": sorted(candidate_elements),
        "explanation_bits": explanation_bits,
        "base_component": round(base_component, 4),
        "major_component": round(major_component, 4),
        "secondary_component": round(secondary_component, 4),
        "chemistry_penalty": round(chemistry_penalty, 4),
        "alloy_likeness_input": round(alloy_likeness, 4),
        "stable_bonus": round(stable_bonus, 4),
        "theoretical_penalty": round(theoretical_penalty, 4),
    }


def _confidence_from_score(weighted_score: float) -> str:
    if weighted_score >= 0.88:
        return "High"
    if weighted_score >= 0.72:
        return "Medium"
    if weighted_score >= 0.58:
        return "Medium-Low"
    return "Low"


def classify_match_mode(weighted_score: float) -> tuple[str, str]:
    if weighted_score >= 0.88:
        return "named_analogue", "named_analogue"
    if weighted_score >= 0.72:
        return "analogue_guided", "analogue_guided"
    return "family_envelope", "family_envelope"


def choose_best_analogue(candidate_row: pd.Series, knowledge_table: pd.DataFrame, *, am_preferred: bool = False) -> Dict[str, Any]:
    candidate_id = str(candidate_row.get("candidate_id", "unknown"))
    candidate_family = _normalize_family(candidate_row.get("material_family"))
    candidate_elements = tuple(_parse_chemsys(candidate_row.get("chemsys")))

    family_slice = knowledge_table[knowledge_table["family_normalized"] == candidate_family].copy()
    family_slice_count = int(len(family_slice))
    if family_slice.empty:
        return {
            "candidate_id": candidate_id,
            "recipe_mode": "family_envelope",
            "analogue_match_class": "family_envelope",
            "matched_alloy_id": None,
            "matched_alloy_name": None,
            "matched_family": candidate_family,
            "analogue_similarity_score": 0.0,
            "analogue_route_compatibility_score": 0.0,
            "analogue_confidence": "Low",
            "analogue_explanation": f"No knowledge-table rows exist for family {candidate_family}; using family-envelope recipe.",
            "primary_template_key": f"{candidate_family.lower().replace('-', '_')}_family_envelope",
            "candidate_family_normalized": candidate_family,
            "candidate_elements": list(candidate_elements),
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

    scored_rows: List[Dict[str, Any]] = []
    best_row = None
    best_score = None
    best_weighted = -1.0

    for _, analogue_row in family_slice.iterrows():
        score = score_candidate_against_analogue(candidate_row, analogue_row, am_preferred=am_preferred)
        score_record = {
            "alloy_id": str(analogue_row.get("alloy_id", "")),
            "canonical_name": str(analogue_row.get("canonical_name", "")),
            "weighted_score": float(score["weighted_score"]),
            "similarity_score": float(score["similarity_score"]),
            "route_compatibility_score": float(score["route_compatibility_score"]),
            "base_component": float(score["base_component"]),
            "major_component": float(score["major_component"]),
            "secondary_component": float(score["secondary_component"]),
            "chemistry_penalty": float(score["chemistry_penalty"]),
        }
        scored_rows.append(score_record)
        if score["weighted_score"] > best_weighted:
            best_weighted = float(score["weighted_score"])
            best_row = analogue_row
            best_score = score

    scored_rows = sorted(scored_rows, key=lambda item: item["weighted_score"], reverse=True)
    top_candidates_json = json.dumps(scored_rows[:3])

    weighted_score = float(best_score["weighted_score"])
    recipe_mode, match_class = classify_match_mode(weighted_score)
    confidence = _confidence_from_score(weighted_score)

    if recipe_mode == "family_envelope":
        explanation = (
            "No high-confidence named analogue was found. "
            + " ".join(best_score["explanation_bits"])
            + " Falling back to family-envelope recipe generation."
        )
        template_key = f"{candidate_family.lower().replace('-', '_')}_family_envelope"
        matched_alloy_id = None
        matched_alloy_name = None
    else:
        explanation = (
            f"Closest analogue is {best_row.get('canonical_name')} ({best_row.get('alloy_id')}) "
            f"with weighted match score {weighted_score:.2f}. "
            + " ".join(best_score["explanation_bits"])
        )
        template_key = str(best_row.get("preferred_recipe_template", ""))
        matched_alloy_id = str(best_row.get("alloy_id", ""))
        matched_alloy_name = str(best_row.get("canonical_name", ""))

    return {
        "candidate_id": candidate_id,
        "recipe_mode": recipe_mode,
        "analogue_match_class": match_class,
        "matched_alloy_id": matched_alloy_id,
        "matched_alloy_name": matched_alloy_name,
        "matched_family": candidate_family,
        "analogue_similarity_score": round(best_score["similarity_score"], 2),
        "analogue_route_compatibility_score": round(best_score["route_compatibility_score"], 2),
        "analogue_confidence": confidence,
        "analogue_explanation": explanation,
        "primary_template_key": template_key,
        "candidate_family_normalized": candidate_family,
        "candidate_elements": list(candidate_elements),
        "analogue_weighted_score": round(weighted_score, 4),
        "analogue_base_component": round(float(best_score["base_component"]) * 100.0, 2),
        "analogue_major_component": round(float(best_score["major_component"]) * 100.0, 2),
        "analogue_secondary_component": round(float(best_score["secondary_component"]) * 100.0, 2),
        "analogue_chemistry_penalty": round(float(best_score["chemistry_penalty"]) * 100.0, 2),
        "analogue_alloy_likeness_input": round(float(best_score["alloy_likeness_input"]) * 100.0, 2),
        "analogue_stable_bonus": round(float(best_score["stable_bonus"]) * 100.0, 2),
        "analogue_theoretical_penalty": round(float(best_score["theoretical_penalty"]) * 100.0, 2),
        "analogue_family_candidate_count": family_slice_count,
        "top_analogue_candidates_json": top_candidates_json,
    }


def match_candidates_to_analogues(candidates_df: pd.DataFrame, knowledge_table: pd.DataFrame, *, requirements: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    if candidates_df is None or len(candidates_df) == 0:
        return pd.DataFrame()
    am_preferred = bool((requirements or {}).get("am_preferred", False))
    rows = [
        choose_best_analogue(row, knowledge_table, am_preferred=am_preferred)
        for _, row in candidates_df.iterrows()
    ]
    return pd.DataFrame(rows)
