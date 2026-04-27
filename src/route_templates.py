
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import pandas as pd

ROUTE_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "ni_am_age_hardened": {
        "template_title": "Ni age-hardened AM route",
        "primary_route": "Pre-alloyed powder -> LPBF/DMLS -> stress relief -> solution + age",
        "secondary_route": "Vacuum melt / wrought stock -> solution + age",
        "steps": [
            "Select a Ni-base composition window consistent with the matched age-hardened analogue.",
            "Assume or procure pre-alloyed powder feedstock suitable for LPBF/DMLS.",
            "Qualify powder condition, storage, and powder-size window before build trials.",
            "Build coupons or a representative near-net-shape trial geometry.",
            "Apply stress relief after build to reduce residual stress.",
            "Apply family-guided solution treatment and age hardening.",
            "Inspect cracking, porosity, distortion, and post-heat-treatment response.",
        ],
        "watch_outs": [
            "Heat-treatment details are analogue-guided, not certified production instructions.",
            "Precipitation-strengthened Ni systems can be sensitive to distortion and cracking after build and post-processing.",
        ],
    },
    "ni_wrought_solid_solution": {
        "template_title": "Ni wrought / solid-solution route",
        "primary_route": "Wrought or welded Ni route -> solution/anneal -> finish + inspect",
        "secondary_route": "Powder route only if separate evidence justifies it",
        "steps": [
            "Select a corrosion-tolerant or solid-solution-strengthened Ni-base composition aligned to the matched analogue.",
            "Assume wrought plate/bar/sheet or welded fabrication feedstock as the primary starting point.",
            "Form, join, or machine the material to near-net shape.",
            "Apply solid-solution or annealing heat-treatment logic guided by the analogue family.",
            "Finish machine and inspect joining quality, distortion, and service-condition suitability.",
        ],
        "watch_outs": [
            "Do not present this as a precipitation-hardening recipe unless the analogue explicitly supports that.",
            "AM support is intentionally conservative for this route class.",
        ],
    },
    "ni_am_or_wrought_age_hardened": {
        "template_title": "Ni AM or wrought age-hardened route",
        "primary_route": "Choose AM powder route or wrought route -> solution + age",
        "secondary_route": "Matched analogue supports both AM and wrought-style interpretations",
        "steps": [
            "Choose whether the part is geometry-driven enough to justify AM, otherwise start from wrought/feedstock processing.",
            "Select a Ni-base composition window aligned to the matched analogue family.",
            "If AM is selected, use pre-alloyed powder, build coupons, then stress relieve before solution + age treatment.",
            "If conventional processing is selected, assume wrought or forged stock followed by solution + age treatment.",
            "Inspect high-temperature capability, cracking response, and heat-treatment response after processing.",
        ],
        "watch_outs": [
            "Route selection still depends on part geometry and qualification strategy.",
            "Do not imply AM is automatically superior simply because it is available.",
        ],
    },
    "ti_am_or_wrought_stress_relief": {
        "template_title": "Ti AM route with stress relief and optional HIP",
        "primary_route": "Powder AM -> stress relief -> optional HIP -> finish + inspect",
        "secondary_route": "Wrought Ti route for less geometry-driven parts",
        "steps": [
            "Select a Ti-base composition window aligned to the matched analogue.",
            "Assume pre-alloyed powder feedstock suitable for powder-bed AM.",
            "Build coupons or representative geometry with contamination control and powder handling discipline.",
            "Apply stress relief after build.",
            "Use HIP only when defect closure or quality targets justify it.",
            "Finish machine and inspect porosity, oxygen pickup, distortion, and cleanliness-sensitive properties.",
        ],
        "watch_outs": [
            "Powder cleanliness and interstitial control can dominate process success.",
            "HIP should be treated as conditional, not automatic.",
        ],
    },
    "ti_eli_am_or_wrought_hip_ready": {
        "template_title": "Ti clean-route ELI recipe",
        "primary_route": "Clean wrought or powder AM route -> stress relief -> optional HIP -> inspect",
        "secondary_route": "Use additional cleanliness controls for fracture-critical interpretations",
        "steps": [
            "Select a Ti-base low-interstitial composition window aligned to the matched ELI analogue.",
            "Prefer routes with strong cleanliness and chemistry-control assumptions.",
            "If AM is used, qualify powder condition and contamination controls before build.",
            "Apply stress relief and use HIP only where the defect-risk case justifies it.",
            "Inspect porosity, oxygen pickup, cleanliness, and fracture-critical quality markers.",
        ],
        "watch_outs": [
            "ELI positioning is about chemistry cleanliness and fracture-critical use, not just route choice.",
            "Do not present HIP as mandatory unless the quality target requires it.",
        ],
    },
    "co_wrought_solution_annealed": {
        "template_title": "Co wrought / solution-annealed route",
        "primary_route": "Wrought / formed stock -> solution treatment -> finish + inspect",
        "secondary_route": "AM only after separate evidence justifies it",
        "steps": [
            "Select a Co-base high-temperature alloy envelope aligned to the matched analogue.",
            "Assume wrought or formed stock as the primary starting route.",
            "Form or fabricate to near-net shape using the analogue family as guidance.",
            "Apply solution-anneal treatment at family-guided conditions.",
            "Finish machine and inspect for weldability, oxidation exposure, and dimensional stability.",
        ],
        "watch_outs": [
            "Public AM evidence is weaker here than for Ni/Ti seed analogues.",
            "Do not imply AM readiness unless route evidence is explicitly available.",
        ],
    },
    "refractory_mo_pm_or_wrought": {
        "template_title": "Refractory Mo-base PM or wrought route",
        "primary_route": "Powder metallurgy or wrought refractory route -> high-temp conditioning -> inspect",
        "secondary_route": "AM only as a research route unless stronger evidence exists",
        "steps": [
            "Select a refractory alloy envelope centered on the matched Mo-base analogue.",
            "Prefer powder-metallurgy or specialist wrought refractory processing over general-purpose routes.",
            "Apply high-temperature consolidation or conditioning steps guided by the analogue family.",
            "Machine using refractory-aware finishing assumptions.",
            "Inspect oxidation sensitivity, brittleness risk, and high-temperature dimensional response.",
        ],
        "watch_outs": [
            "Refractory routes are specialist and should not be presented as commodity manufacturing steps.",
            "Oxidation and environmental sensitivity must be surfaced clearly.",
        ],
    },
    "refractory_nb_wrought_or_lpbf_coated": {
        "template_title": "Refractory Nb route with optional LPBF + protection",
        "primary_route": "Wrought or LPBF research route -> stress relief / HIP as needed -> protective finishing",
        "secondary_route": "Specialist wrought route with coatings/environmental protection",
        "steps": [
            "Select a niobium-base refractory envelope aligned to the matched analogue.",
            "Use specialist wrought processing where production maturity matters.",
            "If AM is considered, treat LPBF as a constrained evidence-backed route rather than a default.",
            "Apply stress relief and, where justified, HIP after AM build.",
            "Add protective finishing or coating logic where environmental exposure demands it.",
            "Inspect oxidation vulnerability, defect state, and coating integrity.",
        ],
        "watch_outs": [
            "Environmental protection is often part of the route concept, not an optional cosmetic step.",
            "AM evidence is still narrower than for Ti/Ni mainstream aerospace alloys.",
        ],
    },
    "ni_based_family_envelope": {
        "template_title": "Ni-family envelope route",
        "primary_route": "Choose between powder-first AM and wrought Ni route after geometry review",
        "secondary_route": "Family-envelope fallback",
        "steps": [
            "Define a Ni-base alloy envelope from the candidate element set.",
            "Assign element roles as base, strengthening, corrosion/oxidation support, or secondary additions.",
            "Choose AM only if the candidate and user preference justify a powder-first concept.",
            "Otherwise use a wrought or cast-plus-heat-treatment route concept.",
            "Apply family-level stress-relief / solution / ageing logic where appropriate.",
            "Inspect cracking, distortion, and heat-treatment response.",
        ],
        "watch_outs": [
            "No high-confidence named analogue was found; this is a family-envelope recipe.",
            "Do not treat any temperatures or times as certified values.",
        ],
    },
    "co_based_family_envelope": {
        "template_title": "Co-family envelope route",
        "primary_route": "Prefer wrought/forming route unless stronger AM evidence emerges",
        "secondary_route": "Family-envelope fallback",
        "steps": [
            "Define a Co-base alloy envelope from the candidate element set.",
            "Assign element roles for hot corrosion / wear / high-temperature support.",
            "Prefer wrought or formed stock as the default route concept.",
            "Use solution-anneal-style conditioning where family logic suggests it.",
            "Inspect weldability, oxidation response, and dimensional stability.",
        ],
        "watch_outs": [
            "Family-envelope fallback is conservative because named analogue confidence is weak.",
            "AM should not be implied unless separate evidence supports it.",
        ],
    },
    "refractory_family_envelope": {
        "template_title": "Refractory-family envelope route",
        "primary_route": "Specialist refractory PM / wrought route",
        "secondary_route": "Family-envelope fallback",
        "steps": [
            "Define a refractory alloy envelope from the candidate element set.",
            "Select specialist powder-metallurgy or refractory wrought processing as the starting concept.",
            "Surface oxidation/environmental protection as part of the recipe, not as an afterthought.",
            "Apply high-temperature conditioning and inspect brittleness and oxidation sensitivity.",
        ],
        "watch_outs": [
            "This recipe is intentionally conservative and specialist-oriented.",
            "Refractory candidates often need stronger process evidence before detailed route claims are made.",
        ],
    },
    "ti_based_family_envelope": {
        "template_title": "Ti-family envelope route",
        "primary_route": "AM or wrought Ti route depending on geometry and cleanliness needs",
        "secondary_route": "Family-envelope fallback",
        "steps": [
            "Define a Ti-base alloy envelope from the candidate element set.",
            "Assign element roles for alpha/beta stabilization and strength support.",
            "Choose AM for geometry-driven cases and wrought/forged feedstock for conventional shapes.",
            "Apply stress-relief logic and optional HIP depending on defect-control needs.",
            "Inspect contamination, porosity, and distortion.",
        ],
        "watch_outs": [
            "This is a family-envelope Ti recipe, not a named alloy route.",
            "Chemistry cleanliness and oxygen control can dominate process suitability.",
        ],
    },
}

def _elements_from_chemsys(value: Any) -> List[str]:
    if value is None:
        return []
    return [e.strip() for e in str(value).split("-") if e.strip()]

def _parse_semicolon_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]

def _family_envelope_ingredient_rows(candidate_row: pd.Series) -> List[Dict[str, str]]:
    family = str(candidate_row.get("material_family", ""))
    elements = _elements_from_chemsys(candidate_row.get("chemsys"))
    rows: List[Dict[str, str]] = []

    for element in elements:
        if "Ni-based" in family:
            role = "base" if element == "Ni" else "major alloying addition"
        elif "Co-based" in family:
            role = "base" if element == "Co" else "major alloying addition"
        elif "Ti-alloy" in family or "Ti-based" in family:
            role = "base" if element == "Ti" else "major alloying addition"
        elif "Refractory" in family:
            role = "refractory-base element" if element in {"Mo", "Nb", "Ta", "W"} else "supporting addition"
        else:
            role = "ingredient"
        rows.append({"element": element, "role": role, "range_hint": "concept envelope / to be refined"})
    return rows

def _analogue_ingredient_rows(knowledge_match_row: pd.Series) -> List[Dict[str, str]]:
    vector_raw = knowledge_match_row.get("composition_vector_json")
    base_element = str(knowledge_match_row.get("base_element", "") or "").strip()
    major_additions = set(_parse_semicolon_values(knowledge_match_row.get("major_additions")))
    rows: List[Dict[str, str]] = []

    parsed_vector: Dict[str, Any] = {}
    if vector_raw is not None and not (isinstance(vector_raw, float) and pd.isna(vector_raw)):
        try:
            parsed_vector = json.loads(str(vector_raw))
        except Exception:
            parsed_vector = {}

    if parsed_vector:
        for element, range_hint in parsed_vector.items():
            role = "ingredient"
            if base_element and base_element in str(element):
                role = "base"
            elif any(addition in str(element) for addition in major_additions):
                role = "major alloying addition"
            else:
                role = "supporting addition"
            rows.append({"element": str(element), "role": role, "range_hint": str(range_hint)})
        return rows

    elements = _parse_semicolon_values(knowledge_match_row.get("composition_elements"))
    for element in elements:
        role = "base" if element == base_element else "major alloying addition" if element in major_additions else "supporting addition"
        rows.append({"element": element, "role": role, "range_hint": "see nominal composition text"})
    return rows

def _split_source_refs(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    return [part.strip() for part in str(value).split(";") if part.strip()]

def render_manufacturing_recipe(
    candidate_row: pd.Series,
    analogue_match_row: pd.Series,
    knowledge_match_row: Optional[pd.Series] = None,
    *,
    requirements: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    template_key = str(analogue_match_row.get("primary_template_key", "") or "")
    if template_key not in ROUTE_TEMPLATES:
        raise KeyError(f"Unknown template key: {template_key}")

    template = ROUTE_TEMPLATES[template_key]
    am_preferred = bool((requirements or {}).get("am_preferred", False))
    if knowledge_match_row is not None and analogue_match_row.get("recipe_mode") != "family_envelope":
        ingredient_rows = _analogue_ingredient_rows(knowledge_match_row)
    else:
        ingredient_rows = _family_envelope_ingredient_rows(candidate_row)

    recipe_watch_outs = list(template.get("watch_outs", []))
    source_refs: List[str] = []

    if knowledge_match_row is not None and analogue_match_row.get("recipe_mode") != "family_envelope":
        source_refs.extend(_split_source_refs(knowledge_match_row.get("source_url_or_ref")))
        kw = str(knowledge_match_row.get("known_watch_outs", "") or "").strip()
        if kw:
            recipe_watch_outs.append(kw)
        guard = str(knowledge_match_row.get("match_guardrails", "") or "").strip()
        if guard:
            recipe_watch_outs.append(f"Analogue guardrail: {guard}")

    # Remove duplicates while preserving order
    recipe_watch_outs = list(dict.fromkeys([item for item in recipe_watch_outs if item]))
    source_refs = list(dict.fromkeys([item for item in source_refs if item]))

    why_route = [
        f"Recipe mode: {analogue_match_row.get('recipe_mode')}.",
        f"Analogue confidence: {analogue_match_row.get('analogue_confidence')}.",
        f"AM preferred by user: {'yes' if am_preferred else 'no'}.",
        str(analogue_match_row.get("analogue_explanation", "")),
    ]
    if knowledge_match_row is not None and analogue_match_row.get("recipe_mode") != "family_envelope":
        nominal = str(knowledge_match_row.get("nominal_composition_text", "") or "").strip()
        if nominal:
            why_route.append(f"Matched analogue nominal composition: {nominal}")
        heat = str(knowledge_match_row.get("heat_treatment_summary", "") or "").strip()
        if heat:
            why_route.append(f"Reference heat-treatment summary: {heat}")

    return {
        "candidate_id": str(candidate_row.get("candidate_id", "")),
        "recipe_mode": str(analogue_match_row.get("recipe_mode", "")),
        "matched_alloy_name": analogue_match_row.get("matched_alloy_name"),
        "template_key": template_key,
        "template_title": template.get("template_title"),
        "primary_route": template.get("primary_route"),
        "secondary_route": template.get("secondary_route"),
        "ingredient_rows": ingredient_rows,
        "process_steps": list(template.get("steps", [])),
        "watch_outs": recipe_watch_outs,
        "why_this_route": why_route,
        "provenance_refs": source_refs,
        "recipe_confidence": analogue_match_row.get("analogue_confidence", "Low"),
    }
