from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st
from mp_api.client import MPRester


DEFAULT_FIELDS = [
    "material_id",
    "formula_pretty",
    "chemsys",
    "density",
    "energy_above_hull",
    "is_stable",
    "theoretical",
    "band_gap",
]

NI_FAMILY_HINTS = {"Cr", "Co", "Al", "Ti", "Ta", "W", "Mo", "Nb"}
CO_FAMILY_HINTS = {"Cr", "W", "Ni", "Mo", "Ta"}
TI_FAMILY_HINTS = {"Al", "V", "Mo", "Nb", "Zr", "Sn", "Cr"}
REFRACTORY_HINTS = {"Nb", "Mo", "Ta", "W", "Ti", "Zr"}

OUTPUT_COLUMNS = [
    "candidate_id",
    "material_family",
    "composition_concept",
    "base_process_route",
    "base_creep_score",
    "base_toughness_score",
    "base_temp_score",
    "base_cost_score",
    "base_sustainability_score",
    "am_capable",
    "mp_material_id",
    "formula_pretty",
    "chemsys",
    "n_elements",
    "density",
    "energy_above_hull",
    "band_gap",
    "is_stable",
    "theoretical",
    "classification_reason",
    "engineering_plausibility",
    "alloy_likeness_score",
    "alloy_likeness_reason",
    "generated_note",
    "baseline_survives",
    "baseline_rejection_stage",
    "baseline_rejection_reason",
    "diagnostic_family_match",
    "diagnostic_complexity_score",
    "diagnostic_complexity_threshold",
]

CANDIDATE_LOG_COLUMNS = [
    "candidate_id",
    "formula_pretty",
    "chemsys",
    "n_elements",
    "assigned_family",
    "family_match",
    "complexity_score",
    "complexity_threshold",
    "passed_complexity_gate",
    "rejection_stage",
    "rejection_reason",
    "survives_baseline",
]


def _empty_candidates_df() -> pd.DataFrame:
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


def _empty_result(
    status: str,
    message: str,
    diagnostics: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return {
        "status": status,
        "message": message,
        "candidates": _empty_candidates_df(),
        "diagnostics": diagnostics or {},
    }


def _get_mp_api_key() -> str | None:
    env_key = os.getenv("MP_API_KEY")
    if env_key:
        return env_key

    try:
        if "MP_API_KEY" in st.secrets:
            return st.secrets["MP_API_KEY"]
    except Exception:
        pass

    return None


def _choose_chemsys(requirements: Dict[str, Any]) -> List[str]:
    families = requirements.get("allowed_material_families", [])
    chemsys: List[str] = []

    if "Ni-based superalloy" in families:
        chemsys.extend(
            [
                "Ni-Cr-Al",
                "Ni-Cr-Co",
                "Ni-Co-Al",
                "Ni-Cr-Ti",
                "Ni-Cr-Co-Al",
                "Ni-Cr-Co-Ti",
                "Ni-Cr-Co-Al-Ti",
                "Ni-Cr-Co-Mo",
            ]
        )
    if "Co-based alloy" in families:
        chemsys.extend(
            [
                "Co-Cr-W",
                "Co-Cr-Ni",
                "Co-Ni-W",
                "Co-Cr-Mo",
                "Co-Cr-Ni-W",
            ]
        )
    if "Fe-Ni alloy" in families:
        chemsys.extend(
            [
                "Fe-Ni-Cr",
                "Fe-Ni-Cr-Al",
                "Fe-Ni-Cr-Co",
                "Fe-Ni-Cr-Co-Al",
            ]
        )
    if "Ti alloy" in families:
        chemsys.extend(
            [
                "Ti-Al-V",
                "Ti-Al-Mo",
                "Ti-Al-Nb",
                "Ti-V-Nb",
                "Ti-Al-V-Mo",
            ]
        )
    if "Refractory alloy concept" in families:
        chemsys.extend(
            [
                "Mo-Nb-Ti",
                "Mo-Nb-Ta",
                "Nb-Ti-Zr",
                "Mo-Nb-Ti-Zr",
                "Mo-Nb-Ta-Ti",
            ]
        )

    return list(dict.fromkeys(chemsys))[:16]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _parse_elements(chemsys: str) -> List[str]:
    if not chemsys:
        return []
    return [e.strip() for e in chemsys.split("-") if e.strip()]


def _formula_looks_intermetallic(formula: str) -> bool:
    if not formula:
        return False

    tokens = re.findall(r"([A-Z][a-z]?)(\d*\.?\d*)", formula)
    if not tokens:
        return False

    counts: List[float] = []
    for _, n in tokens:
        if n == "":
            counts.append(1.0)
        else:
            try:
                counts.append(float(n))
            except Exception:
                counts.append(1.0)

    return len(counts) <= 3 and all(c <= 3 for c in counts)


def _alloy_likeness(
    elements: List[str], formula: str, theoretical: bool
) -> Tuple[int, str]:
    score = 40
    notes: List[str] = []
    n = len(set(elements))

    if n >= 4:
        score += 25
        notes.append("4+ element chemistry favored for engineering-alloy-like behavior.")
    elif n == 3:
        score += 5
        notes.append("3-element chemistry retained as a plausible but weaker alloy-like candidate.")
    else:
        score -= 30
        notes.append("Low chemistry complexity reduces engineering alloy likeness.")

    if _formula_looks_intermetallic(formula):
        score -= 20
        notes.append("Stoichiometric/intermetallic-looking formula penalized.")
    else:
        score += 10
        notes.append("Formula looks less like a simple stoichiometric compound.")

    if theoretical:
        score -= 20
        notes.append("Theoretical-only candidate penalized.")

    score = max(0, min(100, score))
    return score, " ".join(notes)


def _classify_family(elements: List[str]) -> Tuple[str, str, bool]:
    element_set = set(elements)
    n = len(element_set)

    if n < 3:
        return (
            "Excluded",
            f"Rejected because only {n} element(s) are present; demo currently requires 3+ element alloy-like systems.",
            False,
        )

    if "Ni" in element_set and len(element_set.intersection(NI_FAMILY_HINTS)) >= 1:
        return (
            "Ni-based superalloy-like candidate",
            "Contains Ni plus at least one alloying element associated with high-temperature Ni alloy systems.",
            True,
        )

    if "Co" in element_set and len(element_set.intersection(CO_FAMILY_HINTS)) >= 1:
        return (
            "Co-based high-temperature candidate",
            "Contains Co plus at least one alloying element associated with Co-based high-temperature alloy systems.",
            True,
        )

    if "Ti" in element_set and len(element_set.intersection(TI_FAMILY_HINTS)) >= 1:
        return (
            "Ti-alloy-like candidate",
            "Contains Ti plus at least one alloying element associated with engineering Ti alloy systems.",
            True,
        )

    if len(element_set.intersection(REFRACTORY_HINTS)) >= 2:
        return (
            "Refractory-alloy-like candidate",
            "Contains multiple refractory or high-temperature alloying elements.",
            True,
        )

    if "Fe" in element_set and "Ni" in element_set:
        return (
            "Fe-Ni high-temperature candidate",
            "Contains Fe-Ni chemistry suggesting a more engineering-like alloy system.",
            True,
        )

    return (
        "Excluded",
        "Rejected because chemistry does not resemble the prototype's target engineering alloy families closely enough.",
        False,
    )


def _process_route_label(family: str, am_preferred: bool) -> str:
    if (
        "Ni-based" in family
        or "Co-based" in family
        or "Ti-alloy" in family
        or "Fe-Ni" in family
    ):
        if am_preferred:
            return "Illustrative AM-oriented route placeholder; material-specific process not yet derived."
        return "Illustrative high-temperature alloy processing placeholder; process not yet derived."

    if "Refractory" in family:
        return "Illustrative refractory-alloy processing placeholder; process not yet derived."

    return "No process route assigned."


def _complexity_gate(
    elements: List[str],
    alloy_likeness_score: int,
    assigned_family: str,
) -> Tuple[bool, int, int, str]:
    """
    Freeze-phase baseline complexity gate.

    Important:
    - Treat this as a minimum viability gate, not a preference-ranking mechanism.
    - Keep ternary systems alive if they are otherwise plausible.
    - Avoid requiring 4+ elements as a hard survival rule.
    """
    n_elements = len(set(elements))

    # Family-specific minimum thresholds kept intentionally conservative for freeze.
    if "Ni-based" in assigned_family:
        threshold = 3
    elif "Co-based" in assigned_family:
        threshold = 3
    elif "Refractory" in assigned_family:
        threshold = 3
    elif "Ti-alloy" in assigned_family:
        threshold = 3
    elif "Fe-Ni" in assigned_family:
        threshold = 3
    else:
        threshold = 3

    complexity_score = n_elements

    if n_elements < threshold and alloy_likeness_score < 40:
        return (
            False,
            complexity_score,
            threshold,
            "Rejected by minimum complexity gate: too few elements and weak alloy-likeness.",
        )

    return (
        True,
        complexity_score,
        threshold,
        "Passed minimum baseline complexity gate.",
    )


def _build_candidate_log_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    log_df = df.copy()

    rename_map = {
        "material_family": "assigned_family",
        "diagnostic_family_match": "family_match",
        "diagnostic_complexity_score": "complexity_score",
        "diagnostic_complexity_threshold": "complexity_threshold",
        "baseline_rejection_stage": "rejection_stage",
        "baseline_rejection_reason": "rejection_reason",
        "baseline_survives": "survives_baseline",
    }
    log_df = log_df.rename(columns=rename_map)

    if "passed_complexity_gate" not in log_df.columns:
        log_df["passed_complexity_gate"] = None

    existing = [c for c in CANDIDATE_LOG_COLUMNS if c in log_df.columns]
    return log_df[existing].to_dict(orient="records")


def generate_candidates(requirements: Dict[str, Any]) -> Dict[str, Any]:
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError(
            "MP_API_KEY is not set. Add it in Streamlit Community Cloud > App Settings > Secrets, "
            "or export it locally before running the app."
        )

    chemsys_list = _choose_chemsys(requirements)

    diagnostics: Dict[str, Any] = {
        "queried_chemsys": chemsys_list,
        "mp_query_failures": [],
        "raw_docs_retrieved": 0,
        "unique_docs_after_dedup": 0,
        "rejected_by_family": 0,
        "rejected_by_complexity_gate": 0,
        "removed_by_prefer_4plus_filter": 0,
        "removed_by_am_filter": 0,
        "final_candidate_count": 0,
        "sample_returned_chemsys": [],
        "sample_returned_formulas": [],
        "candidate_names_before_final_filtering": [],
        "candidate_names_after_final_filtering": [],
        "candidate_logs": [],
        "warnings": [],
    }

    docs: List[Any] = []

    with MPRester(api_key) as mpr:
        for chemsys in chemsys_list:
            try:
                results = mpr.materials.summary.search(
                    chemsys=chemsys,
                    fields=DEFAULT_FIELDS
                )
                result_list = list(results[:20])
                diagnostics["raw_docs_retrieved"] += len(result_list)
                docs.extend(result_list)
            except Exception as exc:
                diagnostics["mp_query_failures"].append(
                    {"chemsys": chemsys, "error": str(exc)}
                )

    if not docs:
        return _empty_result(
            status="empty",
            message="No Materials Project records were returned for the current search scope.",
            diagnostics=diagnostics,
        )

    rows: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()

    for d in docs:
        mpid = str(getattr(d, "material_id", ""))
        if not mpid or mpid in seen_ids:
            continue
        seen_ids.add(mpid)

        formula = getattr(d, "formula_pretty", "Unknown")
        chemsys = getattr(d, "chemsys", "")
        density = _safe_float(getattr(d, "density", None), default=0.0)
        e_hull = _safe_float(getattr(d, "energy_above_hull", None), default=0.5)
        band_gap = _safe_float(getattr(d, "band_gap", None), default=0.0)
        is_stable = bool(getattr(d, "is_stable", False))
        theoretical = bool(getattr(d, "theoretical", True))

        if len(diagnostics["sample_returned_chemsys"]) < 10:
            diagnostics["sample_returned_chemsys"].append(chemsys)

        if len(diagnostics["sample_returned_formulas"]) < 10:
            diagnostics["sample_returned_formulas"].append(formula)

        elements = _parse_elements(chemsys)
        n_elements = len(elements)

        family, classification_reason, plausible = _classify_family(elements)
        if not plausible:
            diagnostics["rejected_by_family"] += 1
            diagnostics["candidate_logs"].append(
                {
                    "candidate_id": mpid,
                    "formula_pretty": formula,
                    "chemsys": chemsys,
                    "n_elements": n_elements,
                    "assigned_family": family,
                    "family_match": False,
                    "complexity_score": None,
                    "complexity_threshold": None,
                    "passed_complexity_gate": None,
                    "rejection_stage": "family_match",
                    "rejection_reason": classification_reason,
                    "survives_baseline": False,
                }
            )
            continue

        alloy_likeness_score, alloy_likeness_reason = _alloy_likeness(
            elements, formula, theoretical
        )

        complexity_pass, complexity_score, complexity_threshold, complexity_reason = _complexity_gate(
            elements, alloy_likeness_score, family
        )

        if not complexity_pass:
            diagnostics["rejected_by_complexity_gate"] += 1
            diagnostics["candidate_logs"].append(
                {
                    "candidate_id": mpid,
                    "formula_pretty": formula,
                    "chemsys": chemsys,
                    "n_elements": n_elements,
                    "assigned_family": family,
                    "family_match": True,
                    "complexity_score": complexity_score,
                    "complexity_threshold": complexity_threshold,
                    "passed_complexity_gate": False,
                    "rejection_stage": "complexity_gate",
                    "rejection_reason": complexity_reason,
                    "survives_baseline": False,
                }
            )
            continue

        am_capable = (
            "yes"
            if family
            in {
                "Ni-based superalloy-like candidate",
                "Co-based high-temperature candidate",
                "Ti-alloy-like candidate",
                "Fe-Ni high-temperature candidate",
            }
            else "no"
        )

        process_route = _process_route_label(
            family, requirements.get("am_preferred", False)
        )

        temp_score = max(
            20,
            min(
                95,
                int(
                    90
                    - 180 * e_hull
                    + (5 if is_stable else -10)
                    + (6 if n_elements >= 4 else -2)
                    + (alloy_likeness_score * 0.10)
                    - (15 if theoretical else 0)
                ),
            ),
        )

        creep_score = max(
            15,
            min(
                92,
                int(
                    55
                    + (12 if "Ni-based" in family else 0)
                    + (9 if "Co-based" in family else 0)
                    + (7 if "Refractory" in family else 0)
                    + (6 if n_elements >= 4 else 0)
                    + (alloy_likeness_score * 0.12)
                    + (4 if is_stable else -8)
                    - (18 if theoretical else 0)
                ),
            ),
        )

        toughness_score = max(
            15,
            min(
                85,
                int(
                    52
                    + (6 if "Ti-alloy" in family else 0)
                    + (3 if "Fe-Ni" in family else 0)
                    + (2 if density > 5 else 6)
                    + (3 if n_elements >= 4 else 0)
                    + (alloy_likeness_score * 0.08)
                    - (10 if theoretical else 0)
                ),
            ),
        )

        cost_score = max(
            10,
            min(
                80,
                int(
                    68
                    - (18 if "Co" in elements else 0)
                    - (
                        14
                        if "Nb" in elements
                        or "Mo" in elements
                        or "Ta" in elements
                        or "W" in elements
                        else 0
                    )
                    - (8 if "Ni" in elements else 0)
                ),
            ),
        )

        sustainability_score = max(
            10,
            min(
                80,
                int(
                    64
                    - (18 if "Co" in elements else 0)
                    - (
                        14
                        if "Nb" in elements
                        or "Mo" in elements
                        or "Ta" in elements
                        or "W" in elements
                        else 0
                    )
                    - (6 if "Ni" in elements else 0)
                ),
            ),
        )

        if n_elements >= 4 and is_stable and not theoretical and alloy_likeness_score >= 60:
            engineering_plausibility = "Higher"
        elif alloy_likeness_score >= 45 and not theoretical:
            engineering_plausibility = "Medium"
        else:
            engineering_plausibility = "Lower"

        rows.append(
            {
                "candidate_id": mpid,
                "material_family": family,
                "composition_concept": formula,
                "base_process_route": process_route,
                "base_creep_score": creep_score,
                "base_toughness_score": toughness_score,
                "base_temp_score": temp_score,
                "base_cost_score": cost_score,
                "base_sustainability_score": sustainability_score,
                "am_capable": am_capable,
                "mp_material_id": mpid,
                "formula_pretty": formula,
                "chemsys": chemsys,
                "n_elements": n_elements,
                "density": density,
                "energy_above_hull": e_hull,
                "band_gap": band_gap,
                "is_stable": is_stable,
                "theoretical": theoretical,
                "classification_reason": classification_reason,
                "engineering_plausibility": engineering_plausibility,
                "alloy_likeness_score": alloy_likeness_score,
                "alloy_likeness_reason": alloy_likeness_reason,
                "generated_note": "Retrieved from Materials Project summary data and filtered through baseline alloy-family rules.",
                "baseline_survives": True,
                "baseline_rejection_stage": None,
                "baseline_rejection_reason": None,
                "diagnostic_family_match": True,
                "diagnostic_complexity_score": complexity_score,
                "diagnostic_complexity_threshold": complexity_threshold,
                "passed_complexity_gate": True,
            }
        )

    diagnostics["unique_docs_after_dedup"] = len(seen_ids)

    df = pd.DataFrame(rows)
    if df.empty:
        if diagnostics["raw_docs_retrieved"] > 0:
            diagnostics["warnings"].append(
                "No final candidates survived filtering. This may indicate that the complexity gate or family rules are too strict."
            )
        if diagnostics["unique_docs_after_dedup"] > 0 and diagnostics["rejected_by_complexity_gate"] == diagnostics["unique_docs_after_dedup"]:
            diagnostics["warnings"].append(
                "All deduplicated candidates were removed by the complexity gate."
            )

        return _empty_result(
            status="empty",
            message="Materials Project records were found, but none matched the current baseline plausibility screen.",
            diagnostics=diagnostics,
        )

    diagnostics["candidate_names_before_final_filtering"] = df["candidate_id"].astype(str).tolist()

    # Freeze-phase change:
    # DO NOT use the 4+ element preference as a hard exclusion filter.
    diagnostics["removed_by_prefer_4plus_filter"] = 0

    # Keep AM preference conservative:
    # only filter if at least one AM-capable survivor exists.
    before_am_filter = len(df)
    if requirements.get("am_preferred", False):
        preferred = df["am_capable"].astype(str).str.lower() == "yes"
        if preferred.any():
            df = df[preferred].copy()
            diagnostics["removed_by_am_filter"] = before_am_filter - len(df)

    if df.empty:
        diagnostics["warnings"].append(
            "No final candidates survived filtering. This may indicate that the AM preference filter is too strict for the current search scope."
        )
        return _empty_result(
            status="empty",
            message="Candidates were found, but none survived the AM-capability preference filter.",
            diagnostics=diagnostics,
        )

    df = df.reset_index(drop=True)
    diagnostics["final_candidate_count"] = len(df)
    diagnostics["candidate_names_after_final_filtering"] = df["candidate_id"].astype(str).tolist()
    diagnostics["candidate_logs"].extend(_build_candidate_log_rows(df))

    if diagnostics["raw_docs_retrieved"] > 0 and diagnostics["final_candidate_count"] == 0:
        diagnostics["warnings"].append(
            "No final candidates survived filtering. This may indicate that the complexity gate or other filters are too strict."
        )

    if diagnostics["unique_docs_after_dedup"] > 0 and diagnostics["rejected_by_complexity_gate"] == diagnostics["unique_docs_after_dedup"]:
        diagnostics["warnings"].append(
            "All deduplicated candidates were removed by the complexity gate."
        )

    status = "success"
    message = "Candidates retrieved and filtered successfully."

    if diagnostics["mp_query_failures"]:
        message += " Some Materials Project queries failed; partial results are shown."

    return {
        "status": status,
        "message": message,
        "candidates": df,
        "diagnostics": diagnostics,
    }