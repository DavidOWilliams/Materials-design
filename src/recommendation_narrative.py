from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


NARRATIVE_STATUS = "controlled_narrative_no_final_recommendation"
NARRATIVE_WARNING = "Controlled recommendation narrative is decision-support text, not a final recommendation."


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=str)
    return [value]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _find_trace(candidate_id: str, package_context: Mapping[str, Any] | None) -> Mapping[str, Any]:
    context = _mapping(package_context)
    for trace in _as_list(context.get("optimisation_trace")):
        trace_map = _mapping(trace)
        if _text(trace_map.get("candidate_id")) == candidate_id:
            return trace_map
    return {}


def classify_narrative_role(candidate: Mapping[str, Any]) -> dict[str, Any]:
    readiness = _mapping(candidate.get("decision_readiness"))
    readiness_status = _text(readiness.get("readiness_status"), "unknown")
    maturity = _text(readiness.get("evidence_maturity"), _evidence_maturity(candidate)).upper()
    category = _text(readiness.get("readiness_category"), "unknown_readiness")
    if readiness_status == "usable_as_reference":
        role = "mature_comparison_reference"
    elif readiness_status == "usable_with_caveats" and maturity in {"B"}:
        role = "engineering_analogue_option"
    elif readiness_status == "usable_with_caveats" and maturity in {"C"}:
        role = "caveated_engineering_option"
    elif maturity in {"D", "E"} or readiness_status == "exploratory_only":
        role = "exploratory_option"
    elif maturity == "F" or readiness_status == "research_only":
        role = "research_only_option"
    elif readiness_status == "not_ready":
        role = "not_decision_ready_option"
    else:
        role = "unknown_role"
    return {
        "narrative_role": role,
        "readiness_status": readiness_status,
        "readiness_category": category,
        "evidence_maturity": maturity,
        "rationale": "Narrative role follows decision-readiness status and evidence maturity without upgrading low-maturity candidates.",
    }


def _surface_notes(candidate: Mapping[str, Any]) -> list[str]:
    profile = _mapping(candidate.get("surface_function_profile"))
    functions = _as_list(profile.get("primary_surface_functions")) + _as_list(profile.get("secondary_surface_functions"))
    return [f"Surface functions visible: {', '.join(_text(item) for item in functions if _text(item))}."] if functions else []


def _route_notes(candidate: Mapping[str, Any]) -> list[str]:
    details = _mapping(candidate.get("process_route_details"))
    route = _text(details.get("display_name"), _text(candidate.get("process_route_template_id"), "unknown route"))
    family = _text(details.get("process_family"), "unknown")
    return [f"Process route: {route} ({family})."]


def _inspection_repair_notes(candidate: Mapping[str, Any]) -> list[str]:
    inspection = _mapping(candidate.get("inspection_plan"))
    repair = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))
    coating = _mapping(candidate.get("coating_spallation_adhesion"))
    graded_am = _mapping(candidate.get("graded_am_transition_zone_risk"))
    notes = [
        f"Inspection burden: {_text(inspection.get('inspection_burden'), 'unknown')}.",
        f"Repairability: {_text(repair.get('repairability_level'), 'unknown')}.",
        f"Qualification burden: {_text(qualification.get('qualification_burden'), 'unknown')}.",
    ]
    if coating:
        notes.append(
            "Coating diagnostic: "
            f"{_text(coating.get('coating_system_label'), 'coating system')}; "
            f"adhesion/spallation risk {_text(coating.get('adhesion_or_spallation_risk'), 'unknown')}; "
            f"inspection difficulty {_text(coating.get('inspection_difficulty'), 'unknown')}; "
            f"repairability constraint {_text(coating.get('repairability_constraint'), 'unknown')}."
        )
    if graded_am:
        notes.append(
            "Graded AM diagnostic: "
            f"{_text(graded_am.get('gradient_system_label'), 'gradient system')}; "
            f"transition-zone complexity {_text(graded_am.get('transition_zone_complexity'), 'unknown')}; "
            f"residual-stress risk {_text(graded_am.get('residual_stress_risk'), 'unknown')}; "
            f"through-depth inspection {_text(graded_am.get('through_depth_inspection_difficulty'), 'unknown')}."
        )
    return notes


def _strengths(candidate: Mapping[str, Any]) -> list[str]:
    output: list[str] = []
    readiness = _mapping(candidate.get("decision_readiness"))
    if _text(readiness.get("readiness_status")) == "usable_as_reference":
        output.append("Useful as a comparison reference.")
    if _text(readiness.get("readiness_status")) == "usable_with_caveats":
        output.append("Useful for caveated early trade-space discussion.")
    output.extend(_surface_notes(candidate)[:1])
    benefits = [_text(item) for item in _as_list(candidate.get("route_benefits")) if _text(item)]
    output.extend(benefits[:2])
    return list(dict.fromkeys(output))[:4] or ["Included to preserve the candidate-system design-space view."]


def _cautions(candidate: Mapping[str, Any]) -> list[str]:
    readiness = _mapping(candidate.get("decision_readiness"))
    constraints = [_mapping(item) for item in _as_list(readiness.get("constraints")) if _mapping(item)]
    cautions = [
        f"{_text(item.get('category'), 'constraint')}: {_text(item.get('reason'))}"
        for item in constraints[:4]
    ]
    if _evidence_maturity(candidate) in {"D", "E", "F"}:
        cautions.append("Low evidence maturity keeps this out of recommendation-ready treatment.")
    return list(dict.fromkeys(cautions))[:5]


def build_candidate_narrative_card(
    candidate: Mapping[str, Any],
    package_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_id = _candidate_id(candidate)
    readiness = _mapping(candidate.get("decision_readiness"))
    role = classify_narrative_role(candidate)
    trace = _find_trace(candidate_id, package_context)
    gaps = [_text(item) for item in _as_list(candidate.get("route_validation_gaps")) if _text(item)]
    coating = _mapping(candidate.get("coating_spallation_adhesion"))
    coating_evidence = [
        _text(item) for item in _as_list(coating.get("required_validation_evidence")) if _text(item)
    ]
    graded_am = _mapping(candidate.get("graded_am_transition_zone_risk"))
    graded_am_evidence = [
        _text(item) for item in _as_list(graded_am.get("required_validation_evidence")) if _text(item)
    ]
    required_evidence = [
        _text(item) for item in _as_list(readiness.get("required_next_evidence")) if _text(item)
    ]
    optimisation_notes = []
    if trace:
        optimisation_notes.append(
            f"Optimisation skeleton displayed {len(_as_list(trace.get('limiting_factors')))} limiting factors and "
            f"{len(_as_list(trace.get('refinement_options')))} suggestions; no variants were generated."
        )
    return {
        "candidate_id": candidate_id,
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "evidence_maturity": _text(readiness.get("evidence_maturity"), _evidence_maturity(candidate)),
        "readiness_label": _text(readiness.get("readiness_label"), "Unknown decision readiness"),
        "readiness_status": _text(readiness.get("readiness_status"), "unknown"),
        "narrative_role": role["narrative_role"],
        "why_it_is_included": role["rationale"],
        "responsible_use": _text(readiness.get("allowed_use"), "Use only as decision-support context."),
        "main_strengths": _strengths(candidate),
        "main_cautions": _cautions(candidate),
        "evidence_gaps": list(dict.fromkeys(gaps + coating_evidence + graded_am_evidence + required_evidence))[:5],
        "process_route_notes": _route_notes(candidate),
        "inspection_repair_notes": _inspection_repair_notes(candidate),
        "surface_function_notes": _surface_notes(candidate),
        "optimisation_notes": optimisation_notes,
        "not_a_final_recommendation": True,
    }


def _group_ids(cards: Sequence[Mapping[str, Any]], role: str) -> list[str]:
    return [_text(card.get("candidate_id")) for card in cards if card.get("narrative_role") == role]


def _diagnostic_notes(package: Mapping[str, Any]) -> list[str]:
    diagnostic = _mapping(package.get("coating_vs_gradient_diagnostic"))
    notes = [_text(item) for item in _as_list(diagnostic.get("summary_notes")) if _text(item)]
    shared = [_text(item) for item in _as_list(diagnostic.get("shared_surface_function_themes")) if _text(item)]
    if shared:
        notes.append("Shared coating/gradient surface-function themes: " + ", ".join(shared[:6]) + ".")
    notes.append("Coating-vs-gradient comparison is diagnostic only; no winner selected.")
    coating_summary = _mapping(package.get("coating_spallation_adhesion_summary"))
    if coating_summary:
        notes.append(
            "Coating spallation/adhesion diagnostic relevant candidates: "
            f"{coating_summary.get('relevant_candidate_count', 0)}."
        )
    graded_am_summary = _mapping(package.get("graded_am_transition_zone_summary"))
    if graded_am_summary:
        notes.append(
            "Graded AM transition-zone diagnostic relevant candidates: "
            f"{graded_am_summary.get('relevant_candidate_count', 0)}."
        )
    return list(dict.fromkeys(notes))[:6]


def build_recommendation_narrative(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    cards = [build_candidate_narrative_card(candidate, package) for candidate in candidates]
    readiness_summary = _mapping(package.get("decision_readiness_summary"))
    route_summary = _mapping(package.get("process_route_summary"))
    coating_summary = _mapping(package.get("coating_spallation_adhesion_summary"))
    graded_am_summary = _mapping(package.get("graded_am_transition_zone_summary"))
    key_gaps = []
    for card in cards:
        key_gaps.extend(_as_list(card.get("evidence_gaps"))[:2])
    next_steps = [
        "confirm service environment",
        "validate process route",
        "validate inspection approach",
        "validate repair concept",
        "validate interface durability",
        "validate evidence maturity for intended use",
        "review certification path",
    ]
    disclaimer = (
        "This controlled narrative is not a final recommendation, no winner selected, no final ranking, "
        "and not qualification or certification approval."
    )
    return {
        "narrative_status": NARRATIVE_STATUS,
        "executive_summary": [
            "Build 4 presents a controlled decision-support narrative over existing candidate systems.",
            "Mature and analogue records are comparison references only, not selected recommendations.",
            "Exploratory and research-only candidates remain non-recommendation concepts until evidence improves.",
        ],
        "mature_comparison_references": _group_ids(cards, "mature_comparison_reference"),
        "engineering_analogue_options": _group_ids(cards, "engineering_analogue_option")
        + _group_ids(cards, "caveated_engineering_option"),
        "exploratory_options": _group_ids(cards, "exploratory_option"),
        "research_only_options": _group_ids(cards, "research_only_option"),
        "not_decision_ready_options": _group_ids(cards, "not_decision_ready_option"),
        "coating_vs_gradient_considerations": _diagnostic_notes(package),
        "key_evidence_gaps": list(dict.fromkeys(_text(item) for item in key_gaps if _text(item)))[:10],
        "process_inspection_repair_considerations": [
            f"High inspection burden candidates: {len(_as_list(route_summary.get('high_inspection_burden_candidate_ids')))}.",
            f"Limited or poor repairability candidates: {len(_as_list(route_summary.get('limited_or_poor_repairability_candidate_ids')))}.",
            f"High or very high qualification burden candidates: {len(_as_list(route_summary.get('high_or_very_high_qualification_burden_candidate_ids')))}.",
            "Coating adhesion/spallation high-risk candidates: "
            f"{len(_as_list(coating_summary.get('high_spallation_risk_candidate_ids')))}.",
            "Coating inspection/repair high-constraint candidates: "
            f"{len(_as_list(coating_summary.get('high_inspection_difficulty_candidate_ids')))} inspection, "
            f"{len(_as_list(coating_summary.get('high_repairability_constraint_candidate_ids')))} repair.",
            "Graded AM transition/residual-stress high-risk candidates: "
            f"{len(_as_list(graded_am_summary.get('high_transition_complexity_candidate_ids')))} transition, "
            f"{len(_as_list(graded_am_summary.get('high_residual_stress_risk_candidate_ids')))} residual stress.",
            "Graded AM inspection/repair high-constraint candidates: "
            f"{len(_as_list(graded_am_summary.get('high_inspection_difficulty_candidate_ids')))} inspection, "
            f"{len(_as_list(graded_am_summary.get('high_repairability_constraint_candidate_ids')))} repair.",
        ],
        "decision_readiness_overview": {
            "readiness_category_counts": dict(_mapping(readiness_summary.get("readiness_category_counts"))),
            "readiness_status_counts": dict(_mapping(readiness_summary.get("readiness_status_counts"))),
        },
        "next_validation_steps": next_steps,
        "deferred_capabilities": [
            "final ranking",
            "Pareto optimisation",
            "generated variants",
            "candidate filtering",
            "final decision logic",
            "live specialist model adapters",
            "certification approval",
        ],
        "safety_disclaimer": disclaimer,
        "candidate_narrative_cards": cards,
        "warnings": [NARRATIVE_WARNING],
    }


def attach_recommendation_narrative(package: Mapping[str, Any]) -> dict[str, Any]:
    output = dict(package)
    narrative = build_recommendation_narrative(package)
    cards_by_id = {
        _text(card.get("candidate_id")): dict(card)
        for card in _as_list(narrative.get("candidate_narrative_cards"))
        if isinstance(card, Mapping)
    }
    candidates = []
    for candidate in _as_list(package.get("candidate_systems")):
        if isinstance(candidate, Mapping):
            enriched = dict(candidate)
            enriched["recommendation_narrative_card"] = cards_by_id.get(_candidate_id(candidate), {})
            candidates.append(enriched)
    output["candidate_systems"] = candidates
    output["recommendation_narrative"] = narrative
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    warnings = [_text(item) for item in _as_list(package.get("warnings")) if _text(item)]
    if NARRATIVE_WARNING not in warnings:
        warnings.append(NARRATIVE_WARNING)
    output["warnings"] = warnings
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics["recommendation_narrative_attached"] = True
    output["diagnostics"] = diagnostics
    return output


def _markdown_list(items: Sequence[Any]) -> list[str]:
    values = [_text(item) for item in items if _text(item)]
    return [f"- {item}" for item in values] if values else ["- none"]


def render_recommendation_narrative_markdown(narrative: Mapping[str, Any]) -> str:
    lines = [
        "## Controlled Recommendation Narrative",
        "",
        "### Executive Summary",
    ]
    lines.extend(_markdown_list(_as_list(narrative.get("executive_summary"))))
    sections = [
        ("Mature Comparison References", "mature_comparison_references"),
        ("Engineering Analogue Options", "engineering_analogue_options"),
        ("Exploratory Options", "exploratory_options"),
        ("Research-Only Options", "research_only_options"),
        ("Coating vs Gradient Considerations", "coating_vs_gradient_considerations"),
        ("Key Evidence Gaps", "key_evidence_gaps"),
        ("Process / Inspection / Repair Considerations", "process_inspection_repair_considerations"),
        ("Next Validation Steps", "next_validation_steps"),
    ]
    for title, field in sections:
        lines.extend(["", f"### {title}"])
        lines.extend(_markdown_list(_as_list(narrative.get(field))))
    lines.extend(["", "### Safety Disclaimer", f"- {_text(narrative.get('safety_disclaimer'))}"])
    return "\n".join(lines) + "\n"
