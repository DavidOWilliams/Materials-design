from __future__ import annotations

import os
import re
from dataclasses import dataclass
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

API_SAFE_EXCLUSIONS = {
    # Keep this intentionally short because the MP API enforces a tight serialized
    # length limit on exclude_elements.
    "Fe", "S", "P", "B", "C", "N", "O", "Cl", "F", "Se", "Te",
}

LOCAL_NON_TARGET_EXCLUSIONS = {
    # Apply the broader chemistry cleanup locally after retrieval instead of in the
    # API call so the query remains within MP parameter limits.
    "Fe",
    "S",
    "P",
    "B",
    "C",
    "N",
    "O",
    "Cl",
    "F",
    "Se",
    "Te",
    "As",
    "Sb",
    "Bi",
    "Ge",
    "Si",
    "Br",
    "I",
    "Li", "Na", "K", "Rb", "Cs",
    "Be", "Mg", "Ca", "Sr", "Ba",
    "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
}

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
    "origin_requested_chemsys",
    "matched_query_chemsys",
    "retrieval_mode",
    "requested_overlap_score",
    "requested_distinguishing_bonus",
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
    "origin_requested_chemsys",
    "matched_query_chemsys",
    "retrieval_mode",
    "requested_overlap_score",
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

PROBE_COLUMNS = [
    "requested_chemsys",
    "requested_family",
    "matched_query_chemsys",
    "retrieval_mode",
    "material_id",
    "formula_pretty",
    "chemsys",
    "requested_overlap_score",
    "candidate_family",
    "family_plausible",
    "family_matches_request",
    "accepted_for_request",
    "is_cobalt_near_miss",
    "near_miss_reason",
    "near_miss_bucket",
    "rejection_reason",
    "n_elements",
    "density",
    "energy_above_hull",
    "band_gap",
    "is_stable",
    "theoretical",
]

COBALT_ANCHOR_CHEMSYS = [
    "Co-Cr-W",
    "Co-Cr-Ni",
    "Co-Cr-Mo",
    "Co-Cr-Ni-W",
    "Co-Ni-W",
]

@dataclass(frozen=True)
class RetrievalStrategy:
    requested_chemsys: str
    retrieval_mode: str
    method: str
    query_payload: Any
    broadness_rank: int

FAMILY_LABEL_BY_KEY = {
    "ni": "Ni-based superalloy-like candidate",
    "co": "Co-based high-temperature candidate",
    "refractory": "Refractory-alloy-like candidate",
    "ti": "Ti-alloy-like candidate",
    "fe_ni": "Fe-Ni high-temperature candidate",
}

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

    forced_chemsys = requirements.get("forced_chemsys")
    if forced_chemsys:
        if isinstance(forced_chemsys, str):
            return [forced_chemsys]
        return list(dict.fromkeys(forced_chemsys))

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
                "Co-Cr-W-Ni",
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

def _fallback_chemsys_map() -> Dict[str, List[str]]:
    return {
        "Ni-Cr-Co": [
            "Ni-Cr-Co-Al",
            "Ni-Cr-Co-Ti",
            "Ni-Cr-Co-Al-Ti",
            "Ni-Cr-Co-Mo",
            "Ni-Cr-Al",
            "Ni-Co-Al",
            "Ni-Cr-Ti",
        ],
        "Co-Cr-W": [
            "Co-Cr-Ni-W",
            "Co-Cr-W-Ni",
            "Co-Ni-W",
            "Co-Cr-Ni",
            "Co-Cr-Mo",
        ],
        "Co-Cr-Ni": [
            "Co-Cr-Ni-W",
            "Co-Cr-W-Ni",
            "Co-Ni-W",
            "Co-Cr-W",
            "Co-Cr-Mo",
        ],
        "Co-Cr-Mo": [
            "Co-Cr-Ni",
            "Co-Cr-Ni-W",
            "Co-Cr-W-Ni",
            "Co-Ni-W",
            "Co-Cr-W",
        ],
    }

def _family_aware_fallbacks(requested_chemsys: str, allowed_families: List[str]) -> List[str]:
    explicit = _fallback_chemsys_map().get(requested_chemsys, [])
    if explicit:
        return list(dict.fromkeys(explicit))

    family_set = set(allowed_families or [])

    if "Ni-based superalloy" in family_set:
        return [
            "Ni-Cr-Co-Al",
            "Ni-Cr-Co-Ti",
            "Ni-Cr-Co-Al-Ti",
            "Ni-Cr-Co-Mo",
            "Ni-Co-Al",
            "Ni-Cr-Ti",
        ]

    if "Refractory alloy concept" in family_set:
        return [
            "Mo-Nb-Ti",
            "Mo-Nb-Ta",
            "Nb-Ti-Zr",
            "Mo-Nb-Ti-Zr",
            "Mo-Nb-Ta-Ti",
        ]

    return []

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

def _to_element_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return set(_parse_elements(value))
    if isinstance(value, set):
        return {str(v).strip() for v in value if str(v).strip()}
    if isinstance(value, (list, tuple)):
        return {str(v).strip() for v in value if str(v).strip()}
    return set()

def _has_local_non_target_elements(elements: set[str], requested_elements: set[str]) -> bool:
    # Allow requested elements to remain even if they appear in a general exclusion set.
    # This keeps the rule query-aware and prevents accidental rejection of legitimate
    # requested chemistry.
    return len((elements - requested_elements).intersection(LOCAL_NON_TARGET_EXCLUSIONS)) > 0

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

def _alloy_likeness(elements: List[str], formula: str, theoretical: bool) -> Tuple[int, str]:
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

def _is_cobalt_direct_gap_case(requested_chemsys: str) -> bool:
    requested = set(_parse_elements(requested_chemsys))
    return "Co" in requested and "Cr" in requested and len(requested) == 3

def _cobalt_anchor_candidates_for_request(requested_chemsys: str) -> List[str]:
    requested = set(_parse_elements(requested_chemsys))
    anchors: List[str] = []

    for anchor in COBALT_ANCHOR_CHEMSYS:
        anchor_elements = set(_parse_elements(anchor))

        # Must remain in cobalt family and preserve Cr if requested.
        if "Co" not in anchor_elements:
            continue
        if "Cr" in requested and "Cr" not in anchor_elements:
            continue

        # Prefer anchors sharing at least two requested elements.
        if len(requested.intersection(anchor_elements)) >= 2:
            anchors.append(anchor)

    # Preserve order while removing duplicates.
    seen = set()
    ordered = []
    for item in anchors:
        if item not in seen:
            seen.add(item)
            ordered.append(item)

    return ordered

def _classify_family(elements: List[str]) -> Tuple[str, str, bool]:
    element_set = set(elements)
    n = len(element_set)

    if n < 3:
        return (
            "Excluded",
            f"Rejected because only {n} element(s) are present; demo currently requires 3+ element alloy-like systems.",
            False,
        )

    refractory_bases = {"Mo", "Nb", "Ta", "W"}
    refractory_additions = {"Ti", "Zr", "Hf"}
    if (
        len(element_set.intersection(refractory_bases)) >= 2
        or (
            len(element_set.intersection(refractory_bases)) >= 1
            and len(element_set.intersection(refractory_additions)) >= 2
        )
    ):
        return (
            FAMILY_LABEL_BY_KEY["refractory"],
            "Contains refractory-base chemistry consistent with refractory alloy systems.",
            True,
        )

    if "Co" in element_set and "Ni" in element_set:
        co_support = len(element_set.intersection({"Cr", "W", "Mo", "Ta"}))
        ni_support = len(element_set.intersection({"Al", "Ti"}))
        if co_support >= max(1, ni_support):
            return (
                FAMILY_LABEL_BY_KEY["co"],
                "Contains Co-Ni chemistry with stronger cobalt-family alloying support.",
                True,
            )
        return (
            FAMILY_LABEL_BY_KEY["ni"],
            "Contains Ni plus alloying additions associated with high-temperature Ni alloy systems.",
            True,
        )

    if "Ni" in element_set and len(element_set.intersection(NI_FAMILY_HINTS)) >= 1:
        return (
            FAMILY_LABEL_BY_KEY["ni"],
            "Contains Ni plus at least one alloying element associated with high-temperature Ni alloy systems.",
            True,
        )

    if "Co" in element_set and len(element_set.intersection(CO_FAMILY_HINTS)) >= 1:
        return (
            FAMILY_LABEL_BY_KEY["co"],
            "Contains Co plus alloying additions consistent with Co-based high-temperature alloy systems.",
            True,
        )

    if "Fe" in element_set and "Ni" in element_set:
        return (
            FAMILY_LABEL_BY_KEY["fe_ni"],
            "Contains Fe-Ni chemistry suggesting a more engineering-like alloy system.",
            True,
        )

    if "Ti" in element_set and len(element_set.intersection(TI_FAMILY_HINTS)) >= 1:
        return (
            FAMILY_LABEL_BY_KEY["ti"],
            "Contains Ti plus alloying additions associated with engineering Ti alloy systems.",
            True,
        )

    return (
        "Excluded",
        "Rejected because chemistry does not resemble the prototype's target engineering alloy families closely enough.",
        False,
    )

def _infer_requested_family(requested_chemsys: str, requirements: Dict[str, Any]) -> str | None:
    allowed_families = set(requirements.get("allowed_material_families", []) or [])
    element_set = set(_parse_elements(requested_chemsys))

    if requested_chemsys.startswith("Ni-") or "Ni-based superalloy" in allowed_families:
        return FAMILY_LABEL_BY_KEY["ni"]
    if requested_chemsys.startswith("Co-") or "Co-based alloy" in allowed_families:
        return FAMILY_LABEL_BY_KEY["co"]
    if requested_chemsys.startswith("Ti-") or "Ti alloy" in allowed_families:
        return FAMILY_LABEL_BY_KEY["ti"]
    if requested_chemsys.startswith("Fe-") or "Fe-Ni alloy" in allowed_families:
        return FAMILY_LABEL_BY_KEY["fe_ni"]
    if element_set.intersection({"Mo", "Nb", "Ta", "W"}) and "Refractory alloy concept" in allowed_families:
        return FAMILY_LABEL_BY_KEY["refractory"]
    if element_set.intersection({"Mo", "Nb", "Ta", "W"}) and len(element_set) >= 3:
        return FAMILY_LABEL_BY_KEY["refractory"]
    return None

def _requested_overlap_score(
    candidate_chemsys: Any,
    requested_chemsys: Any,
) -> int:
    candidate_elements = _to_element_set(candidate_chemsys)
    requested_elements = _to_element_set(requested_chemsys)
    return len(candidate_elements.intersection(requested_elements))

def _requested_overlap(
    candidate_chemsys: Any,
    requested_chemsys: Any,
) -> int:
    # Backwards-compatible alias used in a few call sites.
    return _requested_overlap_score(candidate_chemsys, requested_chemsys)

def _requested_distinguishing_element(requested_chemsys: str) -> str | None:
    requested_elements = _parse_elements(requested_chemsys)
    if not requested_elements:
        return None

    requested_set = set(requested_elements)

    # Only apply this special logic to cobalt requests that include Cr plus a third
    # distinguishing element. This keeps the refinement narrow and avoids changing
    # nickel/refractory behavior.
    if "Co" in requested_set and "Cr" in requested_set:
        extras = [e for e in requested_elements if e not in {"Co", "Cr"}]
        if extras:
            return extras[0]

    return None

def _requested_distinguishing_bonus(
    candidate_chemsys: Any,
    requested_chemsys: str,
) -> int:
    distinguishing = _requested_distinguishing_element(requested_chemsys)
    if not distinguishing:
        return 0

    candidate_elements = _to_element_set(candidate_chemsys)
    return 1 if distinguishing in candidate_elements else 0

def _pair_window_missing_requested_elements(
    requested_chemsys: str,
    pair_elements: set[str],
) -> set[str]:
    requested_elements = _to_element_set(requested_chemsys)
    return requested_elements - pair_elements

def _min_overlap_required(requested_family: str | None, retrieval_mode: str, requested_size: int) -> int:
    if retrieval_mode == "exact":
        return requested_size

    if requested_family == FAMILY_LABEL_BY_KEY["ni"]:
        if retrieval_mode == "fallback_expanded":
            return min(2, requested_size)
        return min(2, requested_size)

    if requested_family == FAMILY_LABEL_BY_KEY["co"]:
        if retrieval_mode == "fallback_expanded":
            return min(2, requested_size)
        if retrieval_mode == "fallback_cobalt_pair_window":
            return min(2, requested_size)
        if retrieval_mode == "fallback_elements_window":
            return requested_size

    if requested_family == FAMILY_LABEL_BY_KEY["refractory"]:
        return min(2, requested_size)

    return min(2, requested_size)

def _is_family_compatible(requested_family: str | None, candidate_family: str) -> bool:
    if not requested_family:
        return True
    return candidate_family == requested_family

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
    n_elements = len(set(elements))
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

def _search_mp_chemsys(mpr: MPRester, chemsys: str) -> Tuple[List[Any], str | None]:
    try:
        results = mpr.materials.summary.search(chemsys=chemsys, fields=DEFAULT_FIELDS)
        return list(results[:20]), None
    except Exception as exc:
        return [], str(exc)

def _search_mp_elements_window(
    mpr: MPRester,
    required_elements: List[str],
    exclude_elements: List[str] | None = None,
    min_num_elements: int = 3,
    max_num_elements: int = 5,
    max_results: int = 50,
) -> Tuple[List[Any], str | None]:
    try:
        results = mpr.materials.summary.search(
            elements=required_elements,
            exclude_elements=exclude_elements or [],
            num_elements=(min_num_elements, max_num_elements),
            fields=DEFAULT_FIELDS,
        )
        return list(results[:max_results]), None
    except Exception as exc:
        return [], str(exc)

def _cobalt_pair_window_queries(requested_chemsys: str) -> List[List[str]]:
    elements = _parse_elements(requested_chemsys)
    if not elements or "Co" not in elements:
        return []

    queries: List[List[str]] = []

    # For cobalt gap cases, always probe the cobalt-chromium backbone first.
    if "Cr" in elements:
        queries.append(["Co", "Cr"])

    distinguishing = _requested_distinguishing_element(requested_chemsys)
    if distinguishing and distinguishing not in {"Co", "Cr"}:
        queries.append(["Co", distinguishing])

    # Preserve order while removing duplicates.
    seen: set[tuple[str, ...]] = set()
    ordered: List[List[str]] = []
    for pair in queries:
        key = tuple(pair)
        if key not in seen:
            seen.add(key)
            ordered.append(pair)

    return ordered

def _build_retrieval_strategies(
    requested_chemsys: str,
    requirements: Dict[str, Any],
) -> List[RetrievalStrategy]:
    strategies: List[RetrievalStrategy] = []
    seen: set[tuple[str, str]] = set()

    def _add(method: str, mode: str, payload: Any, broadness_rank: int) -> None:
        key = (method, repr(payload))
        if key in seen:
            return
        seen.add(key)
        strategies.append(
            RetrievalStrategy(
                requested_chemsys=requested_chemsys,
                retrieval_mode=mode,
                method=method,
                query_payload=payload,
                broadness_rank=broadness_rank,
            )
        )

    _add("chemsys", "exact", requested_chemsys, 0)

    cobalt_direct_gap = _is_cobalt_direct_gap_case(requested_chemsys)

    if cobalt_direct_gap:
        for anchor in _cobalt_anchor_candidates_for_request(requested_chemsys):
            if anchor != requested_chemsys:
                _add("chemsys", "fallback_cobalt_anchor_chemsys", anchor, 1)
    else:
        for fallback in _family_aware_fallbacks(
            requested_chemsys,
            requirements.get("allowed_material_families", []) or [],
        ):
            if fallback != requested_chemsys:
                _add("chemsys", "fallback_expanded", fallback, 1)

    if requested_chemsys.startswith("Co-"):
        _add(
            "elements_window",
            "fallback_elements_window",
            _parse_elements(requested_chemsys),
            2,
        )
        for pair in _cobalt_pair_window_queries(requested_chemsys):
            _add("elements_window", "fallback_cobalt_pair_window", pair, 3)

    return strategies

def _run_strategy(
    mpr: MPRester,
    strategy: RetrievalStrategy,
) -> Tuple[List[Any], str | None, str]:
    if strategy.method == "chemsys":
        docs, error = _search_mp_chemsys(mpr, str(strategy.query_payload))
        return docs, error, str(strategy.query_payload)

    if strategy.method == "elements_window":
        required_elements = list(strategy.query_payload)
        min_num_elements = max(3, len(required_elements))
        max_num_elements = 4 if strategy.retrieval_mode.startswith("fallback_cobalt") else 5
        max_results = 25 if strategy.retrieval_mode == "fallback_cobalt_pair_window" else 35
        docs, error = _search_mp_elements_window(
            mpr,
            required_elements=required_elements,
            exclude_elements=sorted(API_SAFE_EXCLUSIONS),
            min_num_elements=min_num_elements,
            max_num_elements=max_num_elements,
            max_results=max_results,
        )
        return docs, error, "+".join(required_elements)

    return [], f"Unknown retrieval method: {strategy.method}", repr(strategy.query_payload)

def _accept_candidate_for_request(
    doc: Any,
    requested_chemsys: str,
    strategy: RetrievalStrategy,
    requested_family: str | None,
) -> Tuple[bool, str | None]:
    result_chemsys = getattr(doc, "chemsys", "") or ""
    result_elements = set(_parse_elements(result_chemsys))
    requested_elements = set(_parse_elements(requested_chemsys))

    if not result_elements:
        return False, "Returned candidate has no chemistry-system metadata."

    if strategy.retrieval_mode != "exact" and _has_local_non_target_elements(result_elements, requested_elements):
        return False, "Returned candidate contains non-target chemistry for this broader recovery step."

    candidate_family, _, plausible = _classify_family(list(result_elements))
    if not plausible:
        return False, "Returned candidate does not belong to a target engineering family."

    if not _is_family_compatible(requested_family, candidate_family):
        return False, "Returned candidate family does not match the requested family."

    overlap = _requested_overlap_score(result_elements, requested_elements)
    min_overlap = _min_overlap_required(requested_family, strategy.retrieval_mode, len(requested_elements))

    if strategy.retrieval_mode == "exact":
        return True, None

    if strategy.retrieval_mode == "fallback_expanded":
        if overlap >= min_overlap:
            return True, None
        return False, "Retrieved neighboring chemistry does not preserve enough requested elements."

    if strategy.retrieval_mode == "fallback_cobalt_anchor_chemsys":
        if overlap < min_overlap:
            return False, "Cobalt-anchor candidate does not preserve enough requested chemistry context."

        # Anchor-chemsys fallback is only valid if it truly restores the requested
        # distinguishing element or fully contains the requested chemistry.
        distinguishing_requested = _requested_distinguishing_element(requested_chemsys)
        if distinguishing_requested and distinguishing_requested not in result_elements:
            return False, "Cobalt-anchor candidate does not contain the requested distinguishing element."

        if not requested_elements.issubset(result_elements):
            return False, "Cobalt-anchor candidate is not a close anchored superset of the requested chemistry."

        return True, None

    if strategy.retrieval_mode == "fallback_elements_window":
        if requested_elements.issubset(result_elements):
            return True, None
        if overlap >= min_overlap and requested_family != FAMILY_LABEL_BY_KEY["co"]:
            return True, None
        return False, "Element-window candidate does not preserve enough requested chemistry context."

    if strategy.retrieval_mode == "fallback_cobalt_pair_window":
        pair_elements = set(strategy.query_payload)
        missing_requested = _pair_window_missing_requested_elements(requested_chemsys, pair_elements)
        distinguishing_requested = _requested_distinguishing_element(requested_chemsys)

        if overlap < min_overlap:
            return False, "Pair-window candidate does not preserve enough requested chemistry context."

        if distinguishing_requested and distinguishing_requested not in result_elements:
            return False, "Pair-window candidate does not preserve the requested distinguishing element."

        # Pair-window recovery must restore any requested anchor element that is not already present in the pair.
        # This keeps the step targeted and prevents generic cobalt-neighbor chemistry from standing in for
        # Co-Cr-W / Co-Cr-Ni / Co-Cr-Mo.
        if missing_requested and result_elements.isdisjoint(missing_requested):
            return False, "Pair-window candidate does not restore the missing requested anchor element."

        return True, None

    return True, None

def _update_retrieval_diagnostics(
    diagnostics: Dict[str, Any],
    strategy: RetrievalStrategy,
    query_descriptor: str,
    result_count: int,
    error: str | None,
) -> None:
    diagnostics["retrieval_attempts"].append(
        {
            "requested_chemsys": strategy.requested_chemsys,
            "query_chemsys": query_descriptor,
            "retrieval_mode": strategy.retrieval_mode,
            "result_count": result_count,
            "error": error,
        }
    )
    if error:
        diagnostics["mp_query_failures"].append(
            {"chemsys": query_descriptor, "error": error}
        )


def _probe_allowed_families(requested_chemsys: str) -> List[str]:
    if requested_chemsys.startswith("Ni-"):
        return ["Ni-based superalloy"]
    if requested_chemsys.startswith("Co-"):
        return ["Co-based alloy"]
    if requested_chemsys.startswith("Ti-"):
        return ["Ti alloy"]
    if requested_chemsys.startswith("Fe-"):
        return ["Fe-Ni alloy"]

    elements = set(_parse_elements(requested_chemsys))
    if elements.intersection({"Mo", "Nb", "Ta", "W"}):
        return ["Refractory alloy concept"]

    return []

def _evaluate_cobalt_near_miss(
    doc: Any,
    requested_chemsys: str,
    strategy: RetrievalStrategy,
    requested_family: str | None,
) -> Tuple[bool, str | None, str | None]:
    if requested_family != FAMILY_LABEL_BY_KEY["co"]:
        return False, None, None

    if strategy.retrieval_mode not in {
        "fallback_cobalt_anchor_chemsys",
        "fallback_cobalt_pair_window",
    }:
        return False, None, None

    result_chemsys = getattr(doc, "chemsys", "") or ""
    result_elements = set(_parse_elements(result_chemsys))
    requested_elements = set(_parse_elements(requested_chemsys))

    if not result_elements:
        return False, None, None

    candidate_family, _, plausible = _classify_family(list(result_elements))
    if not plausible:
        return False, None, None

    if not _is_family_compatible(requested_family, candidate_family):
        return False, None, None

    overlap = _requested_overlap_score(result_elements, requested_elements)
    if overlap < 2:
        return False, None, None

    unexpected = result_elements - requested_elements

    light_exclusions = {
        "B", "C", "N", "O", "F", "P", "S", "Cl", "Br", "I",
        "As", "Sb", "Se", "Te",
        "Li", "Na", "K", "Rb", "Cs",
        "Be", "Mg", "Ca", "Sr", "Ba",
    }
    rare_earth_exclusions = {
        "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb",
        "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y",
    }

    if unexpected.intersection(light_exclusions):
        return False, None, None

    if unexpected.intersection(rare_earth_exclusions):
        return False, None, None

    distinguishing = _requested_distinguishing_element(requested_chemsys)
    if distinguishing and distinguishing not in result_elements:
        return False, None, None

    if strategy.retrieval_mode == "fallback_cobalt_anchor_chemsys":
        return True, "close cobalt anchor chemistry", "cobalt_anchor_near_miss"

    if strategy.retrieval_mode == "fallback_cobalt_pair_window":
        pair_elements = set(strategy.query_payload)
        if "Cr" in pair_elements:
            return True, "close cobalt chromium neighbor", "cobalt_pair_cr_near_miss"
        return True, "close cobalt pair neighbor", "cobalt_pair_near_miss"

    return False, None, None


def _build_probe_row(
    doc: Any,
    requested_chemsys: str,
    requested_family: str | None,
    strategy: RetrievalStrategy,
    matched_query_chemsys: str,
) -> Dict[str, Any]:
    result_chemsys = getattr(doc, "chemsys", "") or ""
    result_elements = _parse_elements(result_chemsys)
    candidate_family, _, family_plausible = _classify_family(result_elements)
    family_matches_request = family_plausible and _is_family_compatible(
        requested_family,
        candidate_family,
    )

    accepted_for_request, rejection_reason = _accept_candidate_for_request(
        doc,
        requested_chemsys,
        strategy,
        requested_family,
    )

    is_cobalt_near_miss, near_miss_reason, near_miss_bucket = _evaluate_cobalt_near_miss(
        doc,
        requested_chemsys,
        strategy,
        requested_family,
    )

    return {
        "requested_chemsys": requested_chemsys,
        "requested_family": requested_family,
        "matched_query_chemsys": matched_query_chemsys,
        "retrieval_mode": strategy.retrieval_mode,
        "material_id": str(getattr(doc, "material_id", "")),
        "formula_pretty": getattr(doc, "formula_pretty", "Unknown"),
        "chemsys": result_chemsys,
        "requested_overlap_score": _requested_overlap_score(
            result_chemsys,
            requested_chemsys,
        ),
        "candidate_family": candidate_family,
        "family_plausible": family_plausible,
        "family_matches_request": family_matches_request,
        "accepted_for_request": accepted_for_request,
        "is_cobalt_near_miss": is_cobalt_near_miss,
        "near_miss_reason": near_miss_reason,
        "near_miss_bucket": near_miss_bucket,
        "rejection_reason": rejection_reason,
        "n_elements": len(result_elements),
        "density": _safe_float(getattr(doc, "density", None), default=0.0),
        "energy_above_hull": _safe_float(getattr(doc, "energy_above_hull", None), default=0.5),
        "band_gap": _safe_float(getattr(doc, "band_gap", None), default=0.0),
        "is_stable": bool(getattr(doc, "is_stable", False)),
        "theoretical": bool(getattr(doc, "theoretical", True)),
    }

def run_coverage_probe(
    requested_chemsys: str,
    max_rows_per_strategy: int = 50,
) -> Dict[str, Any]:
    api_key = _get_mp_api_key()
    if not api_key:
        raise RuntimeError(
            "MP_API_KEY is not set. Add it in Streamlit secrets or export it locally."
        )

    requirements = {
        "forced_chemsys": requested_chemsys,
        "allowed_material_families": _probe_allowed_families(requested_chemsys),
    }
    requested_family = _infer_requested_family(requested_chemsys, requirements)
    strategies = _build_retrieval_strategies(requested_chemsys, requirements)

    rows: List[Dict[str, Any]] = []
    strategy_summaries: List[Dict[str, Any]] = []

    with MPRester(api_key) as mpr:
        for strategy in strategies:
            docs, error, query_descriptor = _run_strategy(mpr, strategy)

            if error:
                strategy_summaries.append(
                    {
                        "requested_chemsys": requested_chemsys,
                        "matched_query_chemsys": query_descriptor,
                        "retrieval_mode": strategy.retrieval_mode,
                        "returned_count": 0,
                        "accepted_for_request_count": 0,
                        "error": error,
                    }
                )
                continue

            sliced_docs = list(docs[:max_rows_per_strategy])
            probe_rows = [
                _build_probe_row(
                    doc,
                    requested_chemsys,
                    requested_family,
                    strategy,
                    query_descriptor,
                )
                for doc in sliced_docs
            ]
            rows.extend(probe_rows)

            accepted_count = sum(1 for row in probe_rows if row["accepted_for_request"])
            near_miss_count = sum(1 for row in probe_rows if row["is_cobalt_near_miss"])
            strategy_summaries.append(
                {
                    "requested_chemsys": requested_chemsys,
                    "matched_query_chemsys": query_descriptor,
                    "retrieval_mode": strategy.retrieval_mode,
                    "returned_count": len(probe_rows),
                    "accepted_for_request_count": accepted_count,
                    "near_miss_count": near_miss_count,
                    "error": None,
                }
            )

    probe_df = pd.DataFrame(rows, columns=PROBE_COLUMNS)
    cobalt_near_miss_df = probe_df[probe_df["is_cobalt_near_miss"] == True].copy()

    return {
        "requested_chemsys": requested_chemsys,
        "requested_family": requested_family,
        "strategies": strategy_summaries,
        "probe_rows": probe_df,
        "cobalt_near_misses": cobalt_near_miss_df,
    }

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
        "retrieval_attempts": [],
        "exact_zero_retrieval_cases": [],
        "fallback_queries_used": [],
        "docs_from_exact": 0,
        "docs_from_fallback": 0,
        "mp_query_failures": [],
        "raw_docs_retrieved": 0,
        "accepted_docs_after_request_acceptance": 0,
        "unique_docs_after_dedup": 0,
        "unique_docs_after_request_acceptance": 0,
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
        "surviving_candidate_logs_sample": [],
        "rejected_candidate_logs_sample": [],
        "surviving_candidate_count_before_final_filtering": 0,
        "rejected_by_retrieval_acceptance": 0,
        "rejected_by_local_non_target_filter": 0,
        "warnings": [],
    }

    docs: List[Any] = []
    doc_source_map: Dict[str, Dict[str, str]] = {}
    seen_doc_ids: set[str] = set()
    seen_returned_doc_ids: set[str] = set()

    with MPRester(api_key) as mpr:
        for requested_chemsys in chemsys_list:
            requested_family = _infer_requested_family(requested_chemsys, requirements)
            strategies = _build_retrieval_strategies(requested_chemsys, requirements)
            exact_found = False
            any_strategy_used = False
            any_results_returned = False

            for strategy in strategies:
                result_list, error, query_descriptor = _run_strategy(mpr, strategy)
                _update_retrieval_diagnostics(
                    diagnostics,
                    strategy,
                    query_descriptor,
                    len(result_list),
                    error,
                )
                if error:
                    continue
                if strategy.retrieval_mode == "exact" and not result_list:
                    diagnostics["exact_zero_retrieval_cases"].append(requested_chemsys)
                if result_list:
                    any_results_returned = True
                    diagnostics["raw_docs_retrieved"] += len(result_list)
                    for doc in result_list:
                        returned_id = str(getattr(doc, "material_id", ""))
                        if returned_id:
                            seen_returned_doc_ids.add(returned_id)
                if not result_list:
                    continue

                accepted_docs: List[Any] = []
                for doc in result_list:
                    accepted, reason = _accept_candidate_for_request(
                        doc,
                        requested_chemsys,
                        strategy,
                        requested_family,
                    )
                    if not accepted:
                        diagnostics["rejected_by_retrieval_acceptance"] += 1
                        if reason and "non-target chemistry" in reason:
                            diagnostics["rejected_by_local_non_target_filter"] += 1
                        diagnostics["candidate_logs"].append(
                            {
                                "candidate_id": str(getattr(doc, "material_id", "")),
                                "formula_pretty": getattr(doc, "formula_pretty", "Unknown"),
                                "chemsys": getattr(doc, "chemsys", "") or "",
                                "origin_requested_chemsys": requested_chemsys,
                                "matched_query_chemsys": query_descriptor,
                                "retrieval_mode": strategy.retrieval_mode,
                                "requested_overlap_score": _requested_overlap_score(
                                    getattr(doc, "chemsys", "") or "",
                                    requested_chemsys,
                                ),
                                "n_elements": len(_parse_elements(getattr(doc, "chemsys", "") or "")),
                                "assigned_family": "Excluded",
                                "family_match": False,
                                "complexity_score": None,
                                "complexity_threshold": None,
                                "passed_complexity_gate": None,
                                "rejection_stage": "retrieval_acceptance",
                                "rejection_reason": reason,
                                "survives_baseline": False,
                            }
                        )
                        continue
                    accepted_docs.append(doc)

                if not accepted_docs:
                    continue

                any_strategy_used = True
                if strategy.retrieval_mode == "exact":
                    exact_found = True
                    diagnostics["docs_from_exact"] += len(accepted_docs)
                else:
                    diagnostics["docs_from_fallback"] += len(accepted_docs)
                    diagnostics["fallback_queries_used"].append(
                        {
                            "requested_chemsys": requested_chemsys,
                            "fallback_query_chemsys": query_descriptor,
                            "result_count": len(accepted_docs),
                            "retrieval_mode": strategy.retrieval_mode,
                        }
                    )

                diagnostics["accepted_docs_after_request_acceptance"] += len(accepted_docs)
                for doc in accepted_docs:
                    mpid = str(getattr(doc, "material_id", ""))
                    if not mpid or mpid in seen_doc_ids:
                        continue
                    seen_doc_ids.add(mpid)
                    doc_source_map[mpid] = {
                        "origin_requested_chemsys": requested_chemsys,
                        "matched_query_chemsys": query_descriptor,
                        "retrieval_mode": strategy.retrieval_mode,
                    }
                    docs.append(doc)

                if exact_found:
                    break
                # first successful accepted fallback wins for this requested chemistry
                break

            if not any_strategy_used:
                if any_results_returned:
                    diagnostics["warnings"].append(
                        f"Materials Project returned records for {requested_chemsys}, but none survived request-aware acceptance."
                    )
                else:
                    diagnostics["warnings"].append(
                        f"No Materials Project records found for exact chemsys {requested_chemsys} "
                        f"or any configured recovery strategy."
                    )

    if not docs:
        diagnostics["unique_docs_after_dedup"] = len(seen_returned_doc_ids)
        diagnostics["unique_docs_after_request_acceptance"] = 0
        if diagnostics["raw_docs_retrieved"] > 0:
            diagnostics["warnings"].append(
                "Returned records existed, but all were rejected by request-aware acceptance before baseline family/complexity filtering."
            )
            return _empty_result(
                status="empty",
                message="Materials Project returned records, but none survived request-aware acceptance.",
                diagnostics=diagnostics,
            )
        return _empty_result(
            status="empty",
            message="No Materials Project records were returned for the current search scope.",
            diagnostics=diagnostics,
        )

    rows: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()

    for d in docs:
        mpid = str(getattr(d, "material_id", ""))
        source_info = doc_source_map.get(
            mpid,
            {
                "origin_requested_chemsys": "",
                "matched_query_chemsys": "",
                "retrieval_mode": "unknown",
            },
        )
        if not mpid or mpid in seen_ids:
            continue
        seen_ids.add(mpid)

        formula = getattr(d, "formula_pretty", "Unknown")
        chemsys = getattr(d, "chemsys", "") or ""
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
        requested_family = _infer_requested_family(source_info["origin_requested_chemsys"], requirements)
        family_match = plausible and (requested_family is None or family == requested_family)
        if not family_match:
            diagnostics["rejected_by_family"] += 1
            diagnostics["candidate_logs"].append(
                {
                    "candidate_id": mpid,
                    "formula_pretty": formula,
                    "chemsys": chemsys,
                    "origin_requested_chemsys": source_info["origin_requested_chemsys"],
                    "matched_query_chemsys": source_info["matched_query_chemsys"],
                    "retrieval_mode": source_info["retrieval_mode"],
                    "requested_overlap_score": _requested_overlap_score(
                        chemsys,
                        source_info["origin_requested_chemsys"],
                    ),
                    "n_elements": n_elements,
                    "assigned_family": family,
                    "family_match": False,
                    "complexity_score": None,
                    "complexity_threshold": None,
                    "passed_complexity_gate": None,
                    "rejection_stage": "family_match",
                    "rejection_reason": (
                        classification_reason if not plausible else "Returned candidate family does not match the requested family."
                    ),
                    "survives_baseline": False,
                }
            )
            continue

        alloy_likeness_score, alloy_likeness_reason = _alloy_likeness(elements, formula, theoretical)
        complexity_pass, complexity_score, complexity_threshold, complexity_reason = _complexity_gate(
            elements,
            alloy_likeness_score,
            family,
        )
        if not complexity_pass:
            diagnostics["rejected_by_complexity_gate"] += 1
            diagnostics["candidate_logs"].append(
                {
                    "candidate_id": mpid,
                    "formula_pretty": formula,
                    "chemsys": chemsys,
                    "origin_requested_chemsys": source_info["origin_requested_chemsys"],
                    "matched_query_chemsys": source_info["matched_query_chemsys"],
                    "retrieval_mode": source_info["retrieval_mode"],
                    "requested_overlap_score": _requested_overlap_score(
                        chemsys,
                        source_info["origin_requested_chemsys"],
                    ),
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
            if family in {
                FAMILY_LABEL_BY_KEY["ni"],
                FAMILY_LABEL_BY_KEY["co"],
                FAMILY_LABEL_BY_KEY["ti"],
                FAMILY_LABEL_BY_KEY["fe_ni"],
            }
            else "no"
        )
        process_route = _process_route_label(family, requirements.get("am_preferred", False))

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
                        if "Nb" in elements or "Mo" in elements or "Ta" in elements or "W" in elements
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
                        if "Nb" in elements or "Mo" in elements or "Ta" in elements or "W" in elements
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
                "origin_requested_chemsys": source_info["origin_requested_chemsys"],
                "matched_query_chemsys": source_info["matched_query_chemsys"],
                "retrieval_mode": source_info["retrieval_mode"],
                "requested_overlap_score": _requested_overlap_score(
                    chemsys,
                    source_info["origin_requested_chemsys"],
                ),
                "requested_distinguishing_bonus": _requested_distinguishing_bonus(
                    chemsys,
                    source_info["origin_requested_chemsys"],
                ),
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

    diagnostics["unique_docs_after_dedup"] = len(seen_returned_doc_ids)
    diagnostics["unique_docs_after_request_acceptance"] = len(seen_ids)

    df = pd.DataFrame(rows)
    if df.empty:
        if diagnostics["raw_docs_retrieved"] > 0:
            diagnostics["warnings"].append(
                "No final candidates survived filtering. This may indicate that the complexity gate or family rules are too strict."
            )
        if (
            diagnostics["unique_docs_after_request_acceptance"] > 0
            and diagnostics["rejected_by_complexity_gate"] == diagnostics["unique_docs_after_request_acceptance"]
        ):
            diagnostics["warnings"].append(
                "All deduplicated candidates were removed by the complexity gate."
            )
        return _empty_result(
            status="empty",
            message="Materials Project records were found, but none matched the current baseline plausibility screen.",
            diagnostics=diagnostics,
        )

    diagnostics["candidate_names_before_final_filtering"] = df["candidate_id"].astype(str).tolist()
    diagnostics["surviving_candidate_count_before_final_filtering"] = len(df)
    diagnostics["removed_by_prefer_4plus_filter"] = 0

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

    sort_columns: List[str] = []
    ascending: List[bool] = []

    if "requested_distinguishing_bonus" in df.columns:
        sort_columns.append("requested_distinguishing_bonus")
        ascending.append(False)

    if "requested_overlap_score" in df.columns:
        sort_columns.append("requested_overlap_score")
        ascending.append(False)

    if "alloy_likeness_score" in df.columns:
        sort_columns.append("alloy_likeness_score")
        ascending.append(False)

    if "energy_above_hull" in df.columns:
        sort_columns.append("energy_above_hull")
        ascending.append(True)

    if sort_columns:
        df = df.sort_values(by=sort_columns, ascending=ascending)

    df = df.reset_index(drop=True)
    diagnostics["final_candidate_count"] = len(df)
    diagnostics["candidate_names_after_final_filtering"] = df["candidate_id"].astype(str).tolist()
    survivor_logs = _build_candidate_log_rows(df)
    rejected_logs = [
        row for row in diagnostics["candidate_logs"]
        if not row.get("survives_baseline", False)
    ]
    diagnostics["surviving_candidate_logs_sample"] = survivor_logs[:5]
    diagnostics["rejected_candidate_logs_sample"] = rejected_logs[:5]
    diagnostics["candidate_logs"] = survivor_logs + rejected_logs

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




