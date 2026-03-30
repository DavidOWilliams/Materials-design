from __future__ import annotations
import os
from typing import Dict, Any, List, Tuple

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

# Elements loosely associated with families for this prototype
NI_FAMILY_HINTS = {"Cr", "Co", "Al", "Ti", "Ta", "W", "Mo", "Nb"}
CO_FAMILY_HINTS = {"Cr", "W", "Ni", "Mo", "Ta"}
TI_FAMILY_HINTS = {"Al", "V", "Mo", "Nb", "Zr", "Sn", "Cr"}
REFRACTORY_HINTS = {"Nb", "Mo", "Ta", "W", "Ti", "Zr"}

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
    chemsys = []

    # Keep these deliberately broader than the final filter.
    # Retrieval can be broad; engineering screening should be strict.
    if "Ni-based superalloy" in families:
        chemsys.extend([
            "Ni-Cr-Al",
            "Ni-Cr-Co",
            "Ni-Co-Al",
            "Ni-Cr-Ti",
            "Ni-Cr-Co-Al",
            "Ni-Cr-Co-Ti",
        ])
    if "Co-based alloy" in families:
        chemsys.extend([
            "Co-Cr-W",
            "Co-Cr-Ni",
            "Co-Ni-W",
            "Co-Cr-Mo",
        ])
    if "Fe-Ni alloy" in families:
        chemsys.extend([
            "Fe-Ni-Cr",
            "Fe-Ni-Cr-Al",
            "Fe-Ni-Cr-Co",
        ])
    if "Ti alloy" in families:
        chemsys.extend([
            "Ti-Al-V",
            "Ti-Al-Mo",
            "Ti-Al-Nb",
            "Ti-V-Nb",
        ])
    if "Refractory alloy concept" in families:
        chemsys.extend([
            "Mo-Nb-Ti",
            "Mo-Nb-Ta",
            "Nb-Ti-Zr",
            "Mo-Nb-Ti-Zr",
        ])

    return list(dict.fromkeys(chemsys))[:12]

def _safe_float(value, default=0.0):
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

def _classify_family(elements: List[str]) -> Tuple[str, str, bool]:
    """
    Returns:
      family_label,
      classification_reason,
      plausible_for_demo
    """
    element_set = set(elements)
    n = len(element_set)

    # Reject very simple systems for this demo
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

    if "Fe" in element_set and "Ni" in element_set and ("Cr" in element_set or "Co" in element_set):
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
    if "Ni-based" in family or "Co-based" in family or "Ti-alloy" in family or "Fe-Ni" in family:
        if am_preferred:
            return "Illustrative AM-oriented route placeholder; material-specific process not yet derived."
        return "Illustrative high-temperature alloy processing placeholder; process not yet derived."
    if "Refractory" in family:
        return "Illustrative refractory-alloy processing placeholder; process not yet derived."
    return "No process route assigned."

def generate_candidates(requirements: Dict[str, Any]) -> pd.DataFrame:
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError(
            "MP_API_KEY is not set. Add it in Streamlit Community Cloud > App Settings > Secrets, "
            "or export it locally before running the app."
        )

    chemsys_list = _choose_chemsys(requirements)
    docs = []

    with MPRester(api_key) as mpr:
        for chemsys in chemsys_list:
            try:
                results = mpr.materials.summary.search(
                    chemsys=chemsys,
                    fields=DEFAULT_FIELDS,
                    is_stable=True,
                )
                docs.extend(results[:15])
            except Exception:
                continue

    if not docs:
        return pd.DataFrame(
            columns=[
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
                "generated_note",
            ]
        )

    rows = []
    seen_ids = set()

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
            continue

        am_capable = "yes" if family in {
            "Ni-based superalloy-like candidate",
            "Co-based high-temperature candidate",
            "Ti-alloy-like candidate",
            "Fe-Ni high-temperature candidate",
        } else "no"

        process_route = _process_route_label(family, requirements.get("am_preferred", False))

        # Still heuristic, but now includes engineering-plausibility logic
        temp_score = max(30, min(95, int(
            92
            - 180 * e_hull
            + (4 if is_stable else -10)
            + (3 if n_elements >= 4 else 0)
            - (6 if theoretical else 0)
        )))

        creep_score = max(25, min(92, int(
            62
            + (10 if "Ni-based" in family else 0)
            + (8 if "Co-based" in family else 0)
            + (6 if "Refractory" in family else 0)
            + (4 if n_elements >= 4 else 0)
            + (4 if is_stable else -8)
            - (8 if theoretical else 0)
        )))

        toughness_score = max(20, min(85, int(
            58
            + (5 if "Ti-alloy" in family else 0)
            + (3 if "Fe-Ni" in family else 0)
            + (2 if density > 5 else 6)
            + (2 if n_elements >= 4 else 0)
        )))

        cost_score = max(10, min(80, int(
            68
            - (18 if "Co" in elements else 0)
            - (14 if "Nb" in elements or "Mo" in elements or "Ta" in elements or "W" in elements else 0)
            - (8 if "Ni" in elements else 0)
        )))

        sustainability_score = max(10, min(80, int(
            64
            - (18 if "Co" in elements else 0)
            - (14 if "Nb" in elements or "Mo" in elements or "Ta" in elements or "W" in elements else 0)
            - (6 if "Ni" in elements else 0)
        )))

        engineering_plausibility = "Medium"
        if n_elements >= 4 and is_stable and not theoretical:
            engineering_plausibility = "Higher"
        elif theoretical:
            engineering_plausibility = "Lower"

        rows.append({
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
            "generated_note": "Retrieved from Materials Project summary data and filtered through prototype alloy-family rules.",
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    if requirements.get("am_preferred", False):
        preferred = df["am_capable"].astype(str).str.lower() == "yes"
        if preferred.any():
            df = df[preferred].copy()

    return df.reset_index(drop=True)