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
        notes.append("3-element chemistry allowed only as a weaker alloy-like candidate.")
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

    if "Ni" in element_set and len(element_set.intersection(NI_FAMILY_HINTS)) >= 2:
        return (
            "Ni-based superalloy-like candidate",
            "Contains Ni plus multiple alloying elements associated with high-temperature Ni alloy systems.",
            True,
        )

    if "Co" in element_set and len(element_set.intersection(CO_FAMILY_HINTS)) >= 2:
        return (
            "Co-based high-temperature candidate",
            "Contains Co plus multiple alloying elements associated with Co-based high-temperature alloy systems.",
            True,
        )

    if "Ti" in element_set and len(element_set.intersection(TI_FAMILY_HINTS)) >= 2:
        return (
            "Ti-alloy-like candidate",
            "Contains Ti plus multiple alloying elements associated with engineering Ti alloy systems.",
            True,
        )

    if len(element_set.intersection(REFRACTORY_HINTS)) >= 3:
        return (
            "Refractory-alloy-like candidate",
            "Contains several refractory or high-temperature alloying elements.",
            True,
        )

    if "Fe" in element_set and "Ni" in element_set and (
        "Cr" in element_set or "Co" in element_set
    ):
        return (
            "Fe-Ni high-temperature candidate",
            "Contains Fe-Ni with additional alloying elements suggesting a more engineering-like alloy system.",
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

        elements = _parse_elements(chemsys)
        n_elements = len(elements)

        family, classification_reason, plausible = _classify_family(elements)
        if not plausible:
            diagnostics["rejected_by_family"] += 1
            continue

        alloy_likeness_score, alloy_likeness_reason = _alloy_likeness(
            elements, formula, theoretical
        )

        if n_elements < 4 and alloy_likeness_score < 40:
            diagnostics["rejected_by_complexity_gate"] += 1
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
                "generated_note": "Retrieved from Materials Project summary data and filtered through stricter prototype alloy-family rules.",
            }
        )

    diagnostics["unique_docs_after_dedup"] = len(seen_ids)

    df = pd.DataFrame(rows)
    if df.empty:
        return _empty_result(
            status="empty",
            message="Materials Project records were found, but none matched the current alloy-family plausibility screen.",
            diagnostics=diagnostics,
        )

    before_complexity_preference = len(df)
    preferred_complexity = df["n_elements"] >= 4
    if preferred_complexity.any():
        df = df[preferred_complexity].copy()
        diagnostics["removed_by_prefer_4plus_filter"] = before_complexity_preference - len(df)

    if df.empty:
        return _empty_result(
            status="empty",
            message="Candidates were found, but none survived the 4+ element preference filter.",
            diagnostics=diagnostics,
        )

    before_am_filter = len(df)
    if requirements.get("am_preferred", False):
        preferred = df["am_capable"].astype(str).str.lower() == "yes"
        if preferred.any():
            df = df[preferred].copy()
            diagnostics["removed_by_am_filter"] = before_am_filter - len(df)

    if df.empty:
        return _empty_result(
            status="empty",
            message="Candidates were found, but none survived the AM-capability preference filter.",
            diagnostics=diagnostics,
        )

    df = df.reset_index(drop=True)
    diagnostics["final_candidate_count"] = len(df)

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