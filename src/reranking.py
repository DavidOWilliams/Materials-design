
from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd


def _family_fit_score(material_family: str) -> float:
    family = str(material_family or "")
    if "Ni-based" in family:
        return 10.0
    if "Co-based" in family:
        return 8.0
    if "Refractory" in family:
        return 8.0
    if "Ti-alloy" in family:
        return 7.0
    if "Fe-Ni" in family:
        return 6.0
    return 0.0


def _chemistry_fit_score(row: pd.Series) -> float:
    alloy_likeness = float(row.get("alloy_likeness_score", 0.0))
    n_elements = float(row.get("n_elements", 0.0))
    overlap = float(row.get("requested_overlap_score", 0.0))
    distinguishing_bonus = float(row.get("requested_distinguishing_bonus", 0.0))
    return round(alloy_likeness * 0.08 + n_elements * 1.25 + overlap * 1.5 + distinguishing_bonus * 2.0, 2)


def _profile_bonus(row: pd.Series, profile_name: str) -> Tuple[float, List[str]]:
    bonus = 0.0
    reasons: List[str] = []

    if profile_name == "Performance-first":
        perf_bonus = max(0.0, (float(row.get("performance_summary_score", 0.0)) - 70.0) * 0.12)
        bonus += perf_bonus
        if perf_bonus > 0:
            reasons.append("extra preference for stronger performance summary")

    elif profile_name == "Cost & sustainability-aware":
        combined = (
            float(row.get("through_life_cost_score", 0.0))
            + float(row.get("sustainability_score_v1", 0.0))
            + float(row.get("supply_risk_score", 0.0))
        ) / 3.0
        dec_bonus = max(0.0, (combined - 68.0) * 0.12)
        bonus += dec_bonus
        if dec_bonus > 0:
            reasons.append("extra preference for cost/sustainability/supply profile")

    elif profile_name == "AM route-first":
        route_bonus = max(0.0, (float(row.get("route_suitability_score", 0.0)) - 68.0) * 0.18)
        bonus += route_bonus
        if route_bonus > 0:
            reasons.append("extra preference for preferred-route suitability")

    return round(bonus, 2), reasons


def _recipe_bonus(row: pd.Series) -> Tuple[float, str]:
    recipe_mode = str(row.get("recipe_mode", "") or "")
    support = float(row.get("recipe_support_score", 0.0) or 0.0)
    matched = str(row.get("matched_alloy_name", "") or "").strip()

    if recipe_mode == "named_analogue":
        bonus = min(3.0, max(0.0, (support - 65.0) * 0.08))
        reason = f"named analogue-backed recipe support ({matched})" if matched else "named analogue-backed recipe support"
        return round(bonus, 2), reason if bonus > 0 else ""
    if recipe_mode == "analogue_guided":
        bonus = min(1.8, max(0.0, (support - 60.0) * 0.05))
        reason = f"analogue-guided manufacturing recipe ({matched})" if matched else "analogue-guided manufacturing recipe"
        return round(bonus, 2), reason if bonus > 0 else ""
    return 0.0, ""


def scientific_rerank(df: pd.DataFrame, requirements: Dict[str, Any]) -> pd.DataFrame:
    if df is None or len(df) == 0:
        return df

    out = df.copy()
    profile_name = requirements.get("downstream_profile_name", "Balanced")

    out["family_fit_score"] = out["material_family"].astype(str).apply(_family_fit_score)
    out["chemistry_fit_score"] = out.apply(_chemistry_fit_score, axis=1)
    out["rerank_evidence_bonus"] = (out["evidence_maturity_score"].fillna(0) * 0.08).round(2)

    profile_bonus_values: List[float] = []
    profile_bonus_reason_values: List[str] = []
    recipe_bonus_values: List[float] = []
    recipe_bonus_reason_values: List[str] = []

    for _, row in out.iterrows():
        bonus, reasons = _profile_bonus(row, profile_name)
        profile_bonus_values.append(bonus)
        profile_bonus_reason_values.append("; ".join(reasons))

        recipe_bonus, recipe_reason = _recipe_bonus(row)
        recipe_bonus_values.append(recipe_bonus)
        recipe_bonus_reason_values.append(recipe_reason)

    out["profile_bonus"] = profile_bonus_values
    out["profile_bonus_reason"] = profile_bonus_reason_values
    out["recipe_rerank_bonus"] = recipe_bonus_values
    out["recipe_rerank_reason"] = recipe_bonus_reason_values

    out["scientific_rerank_score"] = (
        out["overall_score"]
        + out["family_fit_score"]
        + out["chemistry_fit_score"]
        + out["rerank_evidence_bonus"]
        + out["profile_bonus"]
        + out["recipe_rerank_bonus"]
    ).round(2)
    out["final_rank_score"] = out["scientific_rerank_score"]

    def rerank_reason(row: pd.Series) -> str:
        reasons = []
        if float(row.get("family_fit_score", 0.0)) >= 8:
            reasons.append("strong family fit")
        if float(row.get("chemistry_fit_score", 0.0)) >= 8:
            reasons.append("good chemistry-fit signal")
        if float(row.get("rerank_evidence_bonus", 0.0)) >= 5:
            reasons.append("good evidence/maturity support")
        recipe_text = str(row.get("recipe_rerank_reason", "") or "").strip()
        if recipe_text:
            reasons.append(recipe_text)
        profile_text = str(row.get("profile_bonus_reason", "") or "").strip()
        if profile_text:
            reasons.append(profile_text)
        if not reasons:
            return "Ordered using the explicit downstream evaluation layer without any survival filtering."
        return "Ordered using " + "; ".join(reasons) + "."

    out["rerank_reason"] = out.apply(rerank_reason, axis=1)
    return out
