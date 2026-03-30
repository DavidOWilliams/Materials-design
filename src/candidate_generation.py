from __future__ import annotations
import os
from typing import Dict, Any, List

import pandas as pd
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

def _choose_chemsys(requirements: Dict[str, Any]) -> List[str]:
    families = requirements.get("allowed_material_families", [])
    chemsys = []

    if "Ni-based superalloy" in families:
        chemsys.extend(["Ni-Cr", "Ni-Al", "Ni-Co", "Ni-Cr-Al", "Ni-Cr-Co"])
    if "Co-based alloy" in families:
        chemsys.extend(["Co-Cr", "Co-W", "Co-Ni", "Co-Cr-W"])
    if "Fe-Ni alloy" in families:
        chemsys.extend(["Fe-Ni", "Fe-Ni-Cr"])
    if "Ti alloy" in families:
        chemsys.extend(["Ti-Al", "Ti-V", "Ti-Al-V"])
    if "Refractory alloy concept" in families:
        chemsys.extend(["Mo-Nb", "Mo-Ti", "Nb-Ti", "Mo-Nb-Ti"])

    return list(dict.fromkeys(chemsys))[:8]

def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default

def generate_candidates(requirements: Dict[str, Any]) -> pd.DataFrame:
    api_key = os.getenv("MP_API_KEY")
    if not api_key:
        raise RuntimeError(
            "MP_API_KEY is not set. Please export your Materials Project API key first."
        )

    chemsys_list = _choose_chemsys(requirements)
    docs = []

    with MPRester(api_key) as mpr:
        for chemsys in chemsys_list:
            try:
                results = mpr.materials.summary.search(
                    chemsys=chemsys,
                    fields=DEFAULT_FIELDS,
                    is_stable=True
                )
                docs.extend(results[:10])
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
                "density",
                "energy_above_hull",
                "band_gap",
                "is_stable",
                "theoretical",
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

        family = "General material"
        if "Ni" in chemsys:
            family = "Ni-based superalloy"
        elif "Co" in chemsys:
            family = "Co-based alloy"
        elif "Fe" in chemsys:
            family = "Fe-Ni alloy"
        elif "Ti" in chemsys:
            family = "Ti alloy"
        elif "Mo" in chemsys or "Nb" in chemsys:
            family = "Refractory alloy concept"

        am_capable = "yes" if family in {
            "Ni-based superalloy",
            "Co-based alloy",
            "Ti alloy",
            "Fe-Ni alloy",
        } else "no"

        # Simple proxy placeholders derived from real MP data
        temp_score = max(30, min(95, int(95 - 200 * e_hull)))
        creep_score = max(25, min(92, int(70 + (10 if is_stable else -10) - (15 if theoretical else 0))))
        toughness_score = max(20, min(85, int(60 + (5 if density > 5 else 10))))
        cost_score = max(10, min(80, int(
            70
            - (20 if "Co" in chemsys else 0)
            - (15 if "Nb" in chemsys or "Mo" in chemsys else 0)
            - (10 if "Ni" in chemsys else 0)
        )))
        sustainability_score = max(10, min(80, int(
            65
            - (20 if "Co" in chemsys else 0)
            - (15 if "Nb" in chemsys or "Mo" in chemsys else 0)
            - (8 if "Ni" in chemsys else 0)
        )))

        if am_capable == "yes":
            process_route = "Powder route candidate -> AM process screening -> stress relief / heat treatment"
        else:
            process_route = "Conventional processing route to be defined"

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
            "density": density,
            "energy_above_hull": e_hull,
            "band_gap": band_gap,
            "is_stable": is_stable,
            "theoretical": theoretical,
            "generated_note": "Retrieved from Materials Project summary data."
        })

    df = pd.DataFrame(rows)

    if requirements.get("am_preferred", False):
        preferred = df["am_capable"].astype(str).str.lower() == "yes"
        if preferred.any():
            df = df[preferred].copy()

    return df.reset_index(drop=True)