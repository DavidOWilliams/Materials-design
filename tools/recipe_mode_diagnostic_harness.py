#!/usr/bin/env python3
"""
Recipe mode diagnostic harness for the Aviation Material Selection Tool.

Purpose
-------
Checks whether prompt changes are leading to different candidate families and recipe
modes, with special focus on the observed issue:

    Ni-based superalloy-like candidates are repeatedly returned with
    family-envelope fallback rather than named-analogue or analogue-guided recipes.

This harness preserves the frozen baseline boundary. It does not modify candidate
survival, candidate_generation.py, or scoring. It only runs the existing pipeline
and explains why recipe matching falls back.

Run from the project root:

    python tools/recipe_mode_diagnostic_harness.py

Optional:

    python tools/recipe_mode_diagnostic_harness.py --skip-live
    python tools/recipe_mode_diagnostic_harness.py --prompts-csv my_prompts.csv
    python tools/recipe_mode_diagnostic_harness.py --output-dir recipe_mode_diagnostics

Prompts CSV columns:
    case_id,prompt,temperature,am_preferred,profile

Outputs:
    recipe_mode_summary.csv
    recipe_candidate_diagnostics.csv
    knowledge_table_health.csv
    recipe_mode_diagnostic_insights.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


DEFAULT_CASES: List[Dict[str, Any]] = [
    {
        "case_id": "hot_section_creep_am",
        "prompt": "Design a material for a hot aviation component operating at 850°C where creep is critical and additive manufacturing is preferred.",
        "temperature": 850,
        "am_preferred": True,
        "profile": "Balanced",
    },
    {
        "case_id": "lightweight_fatigue_bracket",
        "prompt": "Design a lightweight structural aviation bracket with high strength-to-weight and good fatigue resistance. Conventional processing is acceptable.",
        "temperature": 350,
        "am_preferred": False,
        "profile": "Balanced",
    },
    {
        "case_id": "wear_hot_corrosion_seal",
        "prompt": "Select a material for a hot-corrosion and wear exposed aviation seal surface with sliding contact and salt contaminant exposure.",
        "temperature": 700,
        "am_preferred": False,
        "profile": "Balanced",
    },
    {
        "case_id": "am_complex_internal_channels",
        "prompt": "Design a high temperature component with complex internal channels where additive manufacturing is preferred but creep still matters.",
        "temperature": 825,
        "am_preferred": True,
        "profile": "AM route-first",
    },
    {
        "case_id": "certification_mature_conventional",
        "prompt": "Choose a mature aviation material for a conventionally manufactured structural part where certification confidence, repairability and low through-life cost matter.",
        "temperature": 450,
        "am_preferred": False,
        "profile": "Cost & sustainability-aware",
    },
    {
        "case_id": "extreme_temperature_refractory",
        "prompt": "Identify a material concept for an extreme temperature aviation test component above 1000°C where oxidation risk is managed by protective design and creep resistance is critical.",
        "temperature": 1050,
        "am_preferred": False,
        "profile": "Performance-first",
    },
]

FAMILY_LABELS = {
    "Ni-based superalloy-like candidate": "Ni-based",
    "Co-based high-temperature candidate": "Co-based",
    "Refractory-alloy-like candidate": "Refractory",
    "Ti-alloy-like candidate": "Ti-based",
    "Fe-Ni high-temperature candidate": "Fe-Ni",
    "Ni-based superalloy": "Ni-based",
    "Co-based alloy": "Co-based",
    "Refractory alloy concept": "Refractory",
    "Ti alloy": "Ti-based",
    "Fe-Ni alloy": "Fe-Ni",
}

ANALOGUE_GUIDED_THRESHOLD = 0.72
NAMED_ANALOGUE_THRESHOLD = 0.88


def _project_root() -> Path:
    # If called from tools/, parent.parent is usually the project root.
    script_root = Path(__file__).resolve().parent.parent
    if (script_root / "src").exists():
        return script_root
    return Path.cwd()


def _ensure_import_path(project_root: Path) -> None:
    root_str = str(project_root.resolve())
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, float) and pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        if isinstance(value, float) and pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y", "on"}


def _short_family(value: Any) -> str:
    text = str(value or "").strip()
    for key, label in FAMILY_LABELS.items():
        if key in text or text == key:
            return label
    if "Ni-based" in text:
        return "Ni-based"
    if "Co-based" in text:
        return "Co-based"
    if "Refractory" in text:
        return "Refractory"
    if "Ti" in text:
        return "Ti-based"
    if "Fe-Ni" in text:
        return "Fe-Ni"
    return text or "Unknown"


def _json_loads(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value))
    except Exception:
        return default


def _counter_text(values: Iterable[Any]) -> str:
    values = [str(v) for v in values if str(v).strip()]
    if not values:
        return ""
    return json.dumps(dict(Counter(values)), sort_keys=True)


def _candidate_table_paths(project_root: Path) -> List[Path]:
    return [
        project_root / "data" / "starter_alloy_knowledge_table_seed_rows.csv",
        project_root / "starter_alloy_knowledge_table_seed_rows.csv",
        project_root / "data" / "starter_alloy_knowledge_table.xlsx",
        project_root / "starter_alloy_knowledge_table.xlsx",
        project_root / "data" / "starter_alloy_knowledge_table_seed_rows.json",
        project_root / "starter_alloy_knowledge_table_seed_rows.json",
    ]


def _find_knowledge_table(project_root: Path) -> Optional[Path]:
    for path in _candidate_table_paths(project_root):
        if path.exists():
            return path
    return None


def _load_cases(path: Optional[Path]) -> List[Dict[str, Any]]:
    if path is None:
        return list(DEFAULT_CASES)
    df = pd.read_csv(path)
    required = {"case_id", "prompt", "temperature", "am_preferred"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Prompts CSV missing columns: {sorted(missing)}")
    cases: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        cases.append(
            {
                "case_id": str(row.get("case_id")),
                "prompt": str(row.get("prompt")),
                "temperature": _safe_int(row.get("temperature"), 850),
                "am_preferred": _boolish(row.get("am_preferred")),
                "profile": str(row.get("profile", "Balanced") or "Balanced"),
            }
        )
    return cases


def _top_family_prior(requirements: Dict[str, Any]) -> Tuple[str, float]:
    scope_plan = requirements.get("scope_plan") or {}
    priors = scope_plan.get("family_priors") or requirements.get("family_priors") or {}
    if not priors:
        return "", 0.0
    if isinstance(priors, list):
        # Supports [{family, prior}] just in case a later implementation changes shape.
        pairs = [(str(item.get("family", "")), _safe_float(item.get("prior"))) for item in priors if isinstance(item, dict)]
    elif isinstance(priors, dict):
        pairs = [(str(k), _safe_float(v)) for k, v in priors.items()]
    else:
        return "", 0.0
    if not pairs:
        return "", 0.0
    family, prior = sorted(pairs, key=lambda item: item[1], reverse=True)[0]
    return family, prior


def _active_factor_text(requirements: Dict[str, Any]) -> str:
    factors = requirements.get("active_factor_set") or (requirements.get("scope_plan") or {}).get("active_factor_set") or []
    return ", ".join(map(str, factors))


def _allowed_family_text(requirements: Dict[str, Any]) -> str:
    families = requirements.get("allowed_material_families") or []
    return ", ".join(map(str, families))


def _diagnose_candidate_recipe(row: pd.Series, *, knowledge_table_found: bool) -> str:
    family = str(row.get("material_family", "") or "")
    mode = str(row.get("recipe_mode", "") or "")
    if mode in {"named_analogue", "analogue_guided"}:
        matched = str(row.get("matched_alloy_name", "") or "").strip()
        return f"OK: {mode} recipe" + (f" using {matched}." if matched else ".")

    reasons: List[str] = []
    if not knowledge_table_found:
        reasons.append("No alloy knowledge table was found, so all recipes must fall back to family-envelope mode.")
        return " ".join(reasons)

    family_count = _safe_int(row.get("analogue_family_candidate_count"), 0)
    weighted = _safe_float(row.get("analogue_weighted_score"), 0.0)
    similarity = _safe_float(row.get("analogue_similarity_score"), 0.0)
    route = _safe_float(row.get("analogue_route_compatibility_score"), 0.0)
    base = _safe_float(row.get("analogue_base_component"), 0.0)
    major = _safe_float(row.get("analogue_major_component"), 0.0)
    secondary = _safe_float(row.get("analogue_secondary_component"), 0.0)
    penalty = _safe_float(row.get("analogue_chemistry_penalty"), 0.0)

    if family_count <= 0:
        reasons.append(
            "No matching knowledge-table rows exist for the candidate family; this points to a missing seed-table family or family-normalisation mismatch."
        )
    elif weighted < ANALOGUE_GUIDED_THRESHOLD:
        reasons.append(
            f"Closest analogue score {weighted:.2f} is below the analogue-guided threshold {ANALOGUE_GUIDED_THRESHOLD:.2f}."
        )
        if similarity < 0.55:
            reasons.append("Chemistry similarity is weak, so the candidate is not close enough to the available seed analogues.")
        if route < 0.60:
            reasons.append("Route compatibility is weak, often because AM is preferred but the closest analogue has limited AM support.")
        if base <= 0 and "Ni" in str(row.get("chemsys", "")):
            reasons.append("Base-element matching appears weak despite Ni in the candidate; inspect family normalisation and base_element in the seed table.")
        if major < 10:
            reasons.append("Major-addition overlap is low; the seed analogue may not include the candidate's main alloying additions.")
        if secondary < 5 and penalty > 0:
            reasons.append("Secondary-addition overlap is low and chemistry-drift penalty is being applied.")
    else:
        reasons.append(
            "The weighted analogue score appears high enough but recipe mode is still family-envelope; inspect classify_match_mode and match_df merge alignment."
        )

    if "Ni-based" in family and mode == "family_envelope":
        reasons.append(
            "For Ni candidates specifically, repeated fallback usually means the Materials Project chemsys survivors are simplified or theoretical compared with named Ni alloy seed rows."
        )
    return " ".join(reasons)


def _extract_best_analogue(row: pd.Series) -> Dict[str, Any]:
    parsed = _json_loads(row.get("top_analogue_candidates_json"), [])
    if not isinstance(parsed, list) or not parsed:
        return {
            "best_analogue_name": "",
            "best_analogue_id": "",
            "best_analogue_weighted_score": None,
            "best_analogue_similarity_score": None,
            "best_analogue_route_score": None,
            "best_analogue_base_component": None,
            "best_analogue_major_component": None,
            "best_analogue_secondary_component": None,
            "best_analogue_chemistry_penalty": None,
        }
    best = parsed[0]
    if not isinstance(best, dict):
        return {}
    return {
        "best_analogue_name": best.get("canonical_name", ""),
        "best_analogue_id": best.get("alloy_id", ""),
        "best_analogue_weighted_score": best.get("weighted_score"),
        "best_analogue_similarity_score": best.get("similarity_score"),
        "best_analogue_route_score": best.get("route_compatibility_score"),
        "best_analogue_base_component": best.get("base_component"),
        "best_analogue_major_component": best.get("major_component"),
        "best_analogue_secondary_component": best.get("secondary_component"),
        "best_analogue_chemistry_penalty": best.get("chemistry_penalty"),
    }


def analyse_knowledge_table(project_root: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    path = _find_knowledge_table(project_root)
    rows: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {"path": str(path) if path else "", "found": bool(path), "load_error": ""}

    if not path:
        rows.append(
            {
                "check_type": "knowledge_table",
                "status": "missing",
                "detail": "No starter alloy knowledge table found in expected locations.",
                "family": "",
                "count": 0,
            }
        )
        return pd.DataFrame(rows), context

    try:
        from src.alloy_analogue_matcher import load_alloy_knowledge_table
        from src.route_templates import ROUTE_TEMPLATES

        kt = load_alloy_knowledge_table(path)
        context["row_count"] = int(len(kt))
        context["columns"] = list(kt.columns)

        rows.append(
            {
                "check_type": "knowledge_table",
                "status": "loaded",
                "detail": str(path),
                "family": "",
                "count": int(len(kt)),
            }
        )

        if "family_normalized" in kt.columns:
            for family, count in kt["family_normalized"].value_counts(dropna=False).items():
                rows.append(
                    {
                        "check_type": "rows_by_family",
                        "status": "ok" if count > 0 else "empty",
                        "detail": "Knowledge-table family coverage.",
                        "family": str(family),
                        "count": int(count),
                    }
                )

        if "preferred_recipe_template" in kt.columns:
            templates = set(str(v) for v in kt["preferred_recipe_template"].dropna().unique())
            missing_templates = sorted([t for t in templates if t and t not in ROUTE_TEMPLATES])
            rows.append(
                {
                    "check_type": "template_keys",
                    "status": "ok" if not missing_templates else "warning",
                    "detail": "Missing route template keys: " + ", ".join(missing_templates) if missing_templates else "All referenced template keys exist.",
                    "family": "",
                    "count": len(missing_templates),
                }
            )

        if "am_supported_norm" in kt.columns:
            for value, count in kt["am_supported_norm"].value_counts(dropna=False).items():
                rows.append(
                    {
                        "check_type": "am_supported_distribution",
                        "status": "info",
                        "detail": "AM support distribution in knowledge table.",
                        "family": str(value),
                        "count": int(count),
                    }
                )
    except Exception as exc:
        context["load_error"] = str(exc)
        rows.append(
            {
                "check_type": "knowledge_table",
                "status": "error",
                "detail": str(exc),
                "family": "",
                "count": 0,
            }
        )

    return pd.DataFrame(rows), context


def run_live_case(case: Dict[str, Any], knowledge_table_found: bool) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    from src.requirement_inference import infer_requirements
    from src.evaluation import apply_decision_profile
    from src.candidate_generation import generate_candidates
    from src.scoring import score_candidates
    from src.reranking import scientific_rerank
    from src.ranking import rank_candidates

    case_id = str(case["case_id"])
    prompt = str(case["prompt"])
    temperature = _safe_int(case["temperature"], 850)
    am_preferred = _boolish(case["am_preferred"])
    profile = str(case.get("profile", "Balanced") or "Balanced")

    summary: Dict[str, Any] = {
        "case_id": case_id,
        "prompt": prompt,
        "temperature": temperature,
        "am_preferred": am_preferred,
        "profile": profile,
        "status": "not_run",
    }
    candidate_rows: List[Dict[str, Any]] = []

    try:
        requirements = infer_requirements(prompt, temperature, am_preferred)
        requirements = apply_decision_profile(requirements, profile)
        top_prior_family, top_prior = _top_family_prior(requirements)

        summary.update(
            {
                "interpreted_use_case": (requirements.get("requirement_schema") or {}).get("use_case")
                or (requirements.get("requirement_schema") or {}).get("application_type")
                or "",
                "top_family_prior": top_prior_family,
                "top_family_prior_value": top_prior,
                "allowed_families": _allowed_family_text(requirements),
                "active_factors": _active_factor_text(requirements),
            }
        )

        candidate_result = generate_candidates(requirements)
        diagnostics = candidate_result.get("diagnostics", {}) or {}
        summary.update(
            {
                "baseline_status": candidate_result.get("status"),
                "baseline_message": candidate_result.get("message", ""),
                "raw_docs_retrieved": diagnostics.get("raw_docs_retrieved", 0),
                "unique_docs_after_dedup": diagnostics.get("unique_docs_after_dedup", 0),
                "rejected_by_family": diagnostics.get("rejected_by_family", 0),
                "rejected_by_complexity_gate": diagnostics.get("rejected_by_complexity_gate", 0),
                "final_candidate_count": diagnostics.get("final_candidate_count", 0),
                "queried_chemsys": ", ".join(map(str, diagnostics.get("queried_chemsys", []) or [])),
                "warnings": " | ".join(map(str, diagnostics.get("warnings", []) or [])),
            }
        )

        candidates = candidate_result.get("candidates")
        if candidate_result.get("status") in {"error", "empty"} or candidates is None or len(candidates) == 0:
            summary["status"] = candidate_result.get("status", "empty")
            return summary, candidate_rows

        scored = score_candidates(candidates, requirements)
        reranked = scientific_rerank(scored, requirements)
        top, near_miss = rank_candidates(reranked)

        all_df = reranked.copy()
        top_df = top.copy() if top is not None else pd.DataFrame()

        summary.update(
            {
                "status": "success",
                "scored_candidate_count": int(len(all_df)),
                "top_candidate_count": int(len(top_df)),
                "all_family_mix": _counter_text(all_df.get("material_family", pd.Series(dtype=str)).map(_short_family)),
                "top_family_mix": _counter_text(top_df.get("material_family", pd.Series(dtype=str)).map(_short_family)),
                "all_recipe_mode_mix": _counter_text(all_df.get("recipe_mode", pd.Series(dtype=str))),
                "top_recipe_mode_mix": _counter_text(top_df.get("recipe_mode", pd.Series(dtype=str))),
            }
        )

        if len(all_df) > 0 and "recipe_mode" in all_df.columns:
            family_envelope_count = int((all_df["recipe_mode"].astype(str) == "family_envelope").sum())
            summary["family_envelope_pct_all"] = round(100.0 * family_envelope_count / len(all_df), 1)
        if len(top_df) > 0:
            summary["top_ranked_family"] = _short_family(top_df.iloc[0].get("material_family", ""))
            summary["top_ranked_recipe_mode"] = str(top_df.iloc[0].get("recipe_mode", "") or "")
            summary["top_ranked_candidate_id"] = str(top_df.iloc[0].get("candidate_id", "") or "")

        ni_mask = all_df.get("material_family", pd.Series(dtype=str)).astype(str).str.contains("Ni-based", case=False, na=False)
        ni_df = all_df[ni_mask].copy()
        summary["ni_candidate_count"] = int(len(ni_df))
        if len(ni_df) > 0 and "recipe_mode" in ni_df.columns:
            summary["ni_recipe_mode_mix"] = _counter_text(ni_df["recipe_mode"])
            summary["ni_family_envelope_count"] = int((ni_df["recipe_mode"].astype(str) == "family_envelope").sum())
            summary["ni_family_envelope_pct"] = round(100.0 * summary["ni_family_envelope_count"] / len(ni_df), 1)

        for rank_idx, (_, row) in enumerate(all_df.sort_values("final_rank_score" if "final_rank_score" in all_df.columns else "overall_score", ascending=False).iterrows(), start=1):
            best = _extract_best_analogue(row)
            candidate_record = {
                "case_id": case_id,
                "prompt": prompt,
                "candidate_rank": rank_idx,
                "candidate_id": row.get("candidate_id", ""),
                "material_family": row.get("material_family", ""),
                "family_short": _short_family(row.get("material_family", "")),
                "composition_concept": row.get("composition_concept", ""),
                "formula_pretty": row.get("formula_pretty", ""),
                "chemsys": row.get("chemsys", ""),
                "recipe_mode": row.get("recipe_mode", ""),
                "matched_alloy_name": row.get("matched_alloy_name", ""),
                "matched_alloy_id": row.get("matched_alloy_id", ""),
                "analogue_confidence": row.get("analogue_confidence", ""),
                "analogue_family_candidate_count": row.get("analogue_family_candidate_count", ""),
                "analogue_weighted_score": row.get("analogue_weighted_score", ""),
                "analogue_similarity_score": row.get("analogue_similarity_score", ""),
                "analogue_route_compatibility_score": row.get("analogue_route_compatibility_score", ""),
                "analogue_base_component": row.get("analogue_base_component", ""),
                "analogue_major_component": row.get("analogue_major_component", ""),
                "analogue_secondary_component": row.get("analogue_secondary_component", ""),
                "analogue_chemistry_penalty": row.get("analogue_chemistry_penalty", ""),
                "recipe_support_score": row.get("recipe_support_score", ""),
                "evidence_maturity_score": row.get("evidence_maturity_score", ""),
                "manufacturability_score": row.get("manufacturability_score", ""),
                "route_suitability_score": row.get("route_suitability_score", ""),
                "final_rank_score": row.get("final_rank_score", ""),
                "recipe_diagnosis": _diagnose_candidate_recipe(row, knowledge_table_found=knowledge_table_found),
            }
            candidate_record.update(best)
            candidate_rows.append(candidate_record)

        return summary, candidate_rows

    except Exception as exc:
        summary.update(
            {
                "status": "error",
                "error_type": type(exc).__name__,
                "error": str(exc),
                "traceback": traceback.format_exc(limit=8),
            }
        )
        return summary, candidate_rows


def _generate_insights(
    summary_df: pd.DataFrame,
    candidate_df: pd.DataFrame,
    knowledge_df: pd.DataFrame,
    knowledge_context: Dict[str, Any],
) -> str:
    lines: List[str] = []
    lines.append("# Recipe Mode Diagnostic Insights")
    lines.append("")
    lines.append("## What this harness checks")
    lines.append("")
    lines.append(
        "This harness checks whether prompt-sensitive interpretation is reaching the recipe layer, and why candidates — especially Ni-based candidates — fall back to `family_envelope` recipes."
    )
    lines.append("")

    lines.append("## Knowledge-table health")
    lines.append("")
    if not knowledge_context.get("found"):
        lines.append("- **Likely root cause:** no alloy knowledge table was found. Recipe matching cannot produce analogue-guided modes without it.")
    elif knowledge_context.get("load_error"):
        lines.append(f"- **Likely root cause:** the alloy knowledge table was found but failed to load: `{knowledge_context.get('load_error')}`")
    else:
        lines.append(f"- Knowledge table loaded: `{knowledge_context.get('path')}`")
        lines.append(f"- Knowledge-table rows: **{knowledge_context.get('row_count', 0)}**")
        family_rows = knowledge_df[knowledge_df["check_type"] == "rows_by_family"] if not knowledge_df.empty else pd.DataFrame()
        if not family_rows.empty:
            fam_text = ", ".join(f"{r['family']}={r['count']}" for _, r in family_rows.iterrows())
            lines.append(f"- Rows by family: {fam_text}")
    lines.append("")

    if summary_df.empty:
        lines.append("## Live pipeline results")
        lines.append("")
        lines.append("No live pipeline results were generated. Run without `--skip-live` and ensure `MP_API_KEY` is configured if you want end-to-end diagnostics.")
        return "\n".join(lines)

    lines.append("## Live pipeline result summary")
    lines.append("")
    status_counts = summary_df["status"].value_counts(dropna=False).to_dict() if "status" in summary_df.columns else {}
    lines.append(f"- Case statuses: `{json.dumps(status_counts, sort_keys=True)}`")

    if "ni_candidate_count" in summary_df.columns:
        ni_cases = summary_df[summary_df["ni_candidate_count"].fillna(0).astype(float) > 0]
        lines.append(f"- Cases with Ni candidates: **{len(ni_cases)} / {len(summary_df)}**")
        if len(ni_cases) > 0:
            avg_fallback = ni_cases["ni_family_envelope_pct"].fillna(0).astype(float).mean() if "ni_family_envelope_pct" in ni_cases.columns else 0.0
            lines.append(f"- Average Ni family-envelope fallback rate in cases with Ni candidates: **{avg_fallback:.1f}%**")
    lines.append("")

    lines.append("## Most likely causes")
    lines.append("")

    causes: List[str] = []
    if not knowledge_context.get("found"):
        causes.append("The alloy knowledge table is missing, so the recipe layer is forced into family-envelope fallback.")
    elif knowledge_context.get("load_error"):
        causes.append("The alloy knowledge table is present but cannot be loaded cleanly, so the recipe layer falls back.")

    if not candidate_df.empty:
        fallback_df = candidate_df[candidate_df["recipe_mode"].astype(str) == "family_envelope"].copy()
        ni_fallback_df = fallback_df[fallback_df["material_family"].astype(str).str.contains("Ni-based", case=False, na=False)].copy()
        if len(ni_fallback_df) > 0:
            no_family_rows = ni_fallback_df[ni_fallback_df["analogue_family_candidate_count"].apply(_safe_float) <= 0]
            low_weighted = ni_fallback_df[
                (ni_fallback_df["analogue_family_candidate_count"].apply(_safe_float) > 0)
                & (ni_fallback_df["analogue_weighted_score"].apply(_safe_float) < ANALOGUE_GUIDED_THRESHOLD)
            ]
            weak_route = ni_fallback_df[ni_fallback_df["analogue_route_compatibility_score"].apply(_safe_float) < 0.60]
            weak_similarity = ni_fallback_df[ni_fallback_df["analogue_similarity_score"].apply(_safe_float) < 0.55]

            if len(no_family_rows) > 0:
                causes.append(
                    f"{len(no_family_rows)} Ni fallback candidate(s) had zero matching knowledge-table rows for the normalized family. That points to missing Ni rows or a family-name normalization mismatch."
                )
            if len(low_weighted) > 0:
                median_weighted = low_weighted["analogue_weighted_score"].apply(_safe_float).median()
                causes.append(
                    f"{len(low_weighted)} Ni fallback candidate(s) had knowledge-table rows but the best analogue score was below {ANALOGUE_GUIDED_THRESHOLD:.2f} median={median_weighted:.2f}. This is the most likely cause when the table is present."
                )
            if len(weak_similarity) > 0:
                causes.append(
                    "Chemistry similarity is often weak for Ni fallback candidates. This usually means the MP survivors are simplified chemsys records while the seed table contains richer named alloys."
                )
            if len(weak_route) > 0:
                causes.append(
                    "Route compatibility is weak for some fallback candidates. This can happen when AM is preferred but the closest seed analogue has limited or no AM support."
                )
        elif len(fallback_df) > 0:
            causes.append("Fallback is present, but not mainly among Ni candidates. Inspect recipe_candidate_diagnostics.csv by family.")

        if len(candidate_df) > 0 and (candidate_df["recipe_mode"].astype(str) == "family_envelope").all():
            causes.append(
                "Every candidate is family-envelope. That usually indicates either missing/failed knowledge-table loading, overly strict analogue thresholds, or seed analogues that are too sparse for the retrieved chemistries."
            )

    if not causes:
        causes.append("No obvious single cause was detected. Inspect candidate-level diagnostics, especially `best_analogue_weighted_score`, `analogue_family_candidate_count`, and `recipe_diagnosis`.")

    for cause in causes:
        lines.append(f"- {cause}")
    lines.append("")

    lines.append("## What to inspect first")
    lines.append("")
    lines.append("1. Open `recipe_candidate_diagnostics.csv` and filter `material_family` contains `Ni-based`.")
    lines.append("2. Sort by `analogue_weighted_score` descending.")
    lines.append("3. Check whether the best Ni analogue scores are just below `0.72` or much lower.")
    lines.append("4. Check `analogue_similarity_score` and `analogue_route_compatibility_score` to see whether chemistry or route support is the limiting component.")
    lines.append("5. Check `knowledge_table_health.csv` to confirm Ni-family seed rows exist and template keys are valid.")
    lines.append("")

    lines.append("## Likely next fixes, depending on the result")
    lines.append("")
    lines.append("- If the knowledge table is missing: copy `data/starter_alloy_knowledge_table_seed_rows.csv` into the deployed project.")
    lines.append("- If Ni seed rows are missing or sparse: expand the Ni seed table with more named Ni analogue rows covering AM, wrought, corrosion, and creep-oriented routes.")
    lines.append("- If many best scores sit just below 0.72: consider adding an intermediate `weak_analogue_guided` or `family_plus_nearest_analogue` mode rather than overclaiming named analogue support.")
    lines.append("- If AM route compatibility is the limiter: add AM-supported Ni seed analogues or make the route component less punitive for analogue-guided, not named-analogue, matching.")
    lines.append("- If prompt family priors change but the final pool remains Ni-only: that is a candidate-generation/retrieval-scope issue, not a recipe-layer issue. Treat it as a targeted recall investigation, not a broad baseline redesign.")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose recipe modes and Ni family-envelope fallback causes.")
    parser.add_argument("--output-dir", default="recipe_mode_diagnostics", help="Directory for CSV/Markdown outputs.")
    parser.add_argument("--prompts-csv", default=None, help="Optional prompts CSV with case_id,prompt,temperature,am_preferred,profile columns.")
    parser.add_argument("--skip-live", action="store_true", help="Only inspect knowledge table health; do not call Materials Project or run the full pipeline.")
    args = parser.parse_args()

    project_root = _project_root()
    _ensure_import_path(project_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    knowledge_df, knowledge_context = analyse_knowledge_table(project_root)
    knowledge_df.to_csv(output_dir / "knowledge_table_health.csv", index=False)

    summary_rows: List[Dict[str, Any]] = []
    candidate_rows: List[Dict[str, Any]] = []

    if not args.skip_live:
        cases = _load_cases(Path(args.prompts_csv) if args.prompts_csv else None)
        for case in cases:
            print(f"Running recipe diagnostic case: {case['case_id']}")
            summary, rows = run_live_case(case, knowledge_table_found=bool(knowledge_context.get("found")) and not bool(knowledge_context.get("load_error")))
            summary_rows.append(summary)
            candidate_rows.extend(rows)

    summary_df = pd.DataFrame(summary_rows)
    candidate_df = pd.DataFrame(candidate_rows)

    summary_df.to_csv(output_dir / "recipe_mode_summary.csv", index=False)
    candidate_df.to_csv(output_dir / "recipe_candidate_diagnostics.csv", index=False)

    insights = _generate_insights(summary_df, candidate_df, knowledge_df, knowledge_context)
    (output_dir / "recipe_mode_diagnostic_insights.md").write_text(insights, encoding="utf-8")

    print("\nWrote diagnostic outputs to:")
    print(f"  {output_dir.resolve()}")
    print("\nKey files:")
    print("  knowledge_table_health.csv")
    print("  recipe_mode_summary.csv")
    print("  recipe_candidate_diagnostics.csv")
    print("  recipe_mode_diagnostic_insights.md")

    if not summary_df.empty:
        print("\nQuick summary:")
        cols = [c for c in ["case_id", "status", "top_family_prior", "top_ranked_family", "all_recipe_mode_mix", "ni_recipe_mode_mix", "ni_family_envelope_pct"] if c in summary_df.columns]
        print(summary_df[cols].to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
