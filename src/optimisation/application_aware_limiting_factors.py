from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from src.application_profiles import get_default_application_profile, normalise_application_profile


_MATURITY_ORDER = {"A": 6, "B": 5, "C": 4, "D": 3, "E": 2, "F": 1}


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


def _blob(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_blob(item)}" for key, item in value.items()).lower()
    if isinstance(value, (list, tuple, set)):
        return " ".join(_blob(item) for item in value).lower()
    return _text(value).lower()


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    maturity = _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()
    return maturity if maturity in _MATURITY_ORDER else "unknown"


def _append_once(output: list[str], value: str) -> None:
    text = _text(value)
    if text and text not in output:
        output.append(text)


def _theme(text: Any) -> str:
    blob = _blob(text)
    if "missing required" in blob or "missing" in blob and "function" in blob:
        return "missing_required_function"
    if any(term in blob for term in ("maturity", "research-only", "research only", "d/e", "evidence alignment")):
        return "evidence_maturity"
    if any(term in blob for term in ("spallation", "adhesion", "bond coat", "bondcoat")):
        return "coating_spallation"
    if any(term in blob for term in ("thermal-cycle", "thermal cycle", "thermal cycling", "thermal fatigue")):
        return "coating_thermal_cycling"
    if any(term in blob for term in ("recession", "steam", "ebc durability", "environmental durability")):
        return "cmc_ebc_recession"
    if any(term in blob for term in ("interphase", "fiber", "fibre", "matrix durability")):
        return "cmc_interphase"
    if any(term in blob for term in ("inspection", "ndi", "acceptance criteria", "detectability")):
        return "inspection_acceptance"
    if any(term in blob for term in ("repair", "disposition", "recoat")):
        return "repairability"
    if any(term in blob for term in ("qualification", "certification")):
        return "certification_burden"
    if any(term in blob for term in ("transition-zone", "transition zone", "delamination", "cracking")):
        return "graded_am_transition_zone"
    if any(term in blob for term in ("residual stress", "stress")):
        return "graded_am_residual_stress"
    if any(term in blob for term in ("process-window", "process window", "process route", "repeatability")):
        return "process_route_validation"
    if any(term in blob for term in ("poor-fit", "poor fit", "wrong architecture", "does not satisfy", "mismatch")):
        return "application_mismatch"
    if any(term in blob for term in ("insufficient", "unknown", "not visible")):
        return "insufficient_information"
    return "process_route_validation"


def _diagnostic_cautions(candidate: Mapping[str, Any], architecture_path: str) -> tuple[list[str], list[str]]:
    cautions: list[str] = []
    actions: list[str] = []
    coating = _mapping(candidate.get("coating_spallation_adhesion"))
    cmc = _mapping(candidate.get("cmc_ebc_environmental_durability"))
    graded = _mapping(candidate.get("graded_am_transition_zone_risk"))
    process = _mapping(candidate.get("process_route_profile"))

    if architecture_path == "cmc_ebc_environmental_protection_path" or cmc:
        if cmc.get("ebc_dependency_risk") == "high":
            _append_once(cautions, "EBC dependency is high.")
        if cmc.get("oxidation_recession_risk") == "high":
            _append_once(cautions, "Steam recession and oxidation exposure validation is required.")
        if cmc.get("interface_or_interphase_risk") == "high":
            _append_once(cautions, "Interphase/fiber/matrix durability and compatibility require validation.")
        _append_once(actions, "Define EBC recession/environmental durability evidence package.")
        _append_once(actions, "Define CMC/EBC NDI acceptance criteria.")
        _append_once(actions, "Define EBC repair/disposition rules.")
        _append_once(actions, "Compare certification burden against Ni/TBC analogue.")
        _append_once(actions, "Validate thermal cycling for the target duty cycle.")

    if architecture_path == "coated_metallic_tbc_path":
        if coating.get("adhesion_or_spallation_risk") == "high":
            _append_once(cautions, "Coating adhesion/spallation risk is high for the target profile.")
        if coating.get("thermal_cycling_damage_risk") == "high":
            _append_once(cautions, "Coating thermal-cycling damage risk requires validation.")
        if coating.get("bond_coat_or_interface_dependency") in {"high", "very_high"}:
            _append_once(cautions, "Bond-coat/interface dependency is high.")
        if coating.get("inspection_difficulty") == "high":
            _append_once(cautions, "Coating inspection difficulty is high.")
        if coating.get("repairability_constraint") == "high":
            _append_once(cautions, "Coating repairability is highly constrained.")
        _append_once(actions, "Define coating adhesion/spallation validation plan.")
        _append_once(actions, "Define thermal-cycle exposure validation.")
        _append_once(actions, "Define coating inspection and repair acceptance criteria.")

    if architecture_path == "graded_am_research_path" or graded:
        if graded.get("transition_zone_complexity") == "high":
            _append_once(cautions, "Graded AM transition-zone complexity is high.")
        if graded.get("residual_stress_risk") == "high":
            _append_once(cautions, "Graded AM residual-stress risk is high.")
        if graded.get("process_window_sensitivity") == "high":
            _append_once(cautions, "Graded AM process-window sensitivity is high.")
        if graded.get("through_depth_inspection_difficulty") == "high":
            _append_once(cautions, "Through-depth inspection difficulty is high.")
        _append_once(actions, "Retain as exploratory/research concept only.")
        _append_once(actions, "Define transition-zone validation package.")
        _append_once(actions, "Compare with coating-enabled and CMC/EBC paths.")

    if process.get("qualification_burden") in {"high", "very_high"}:
        _append_once(cautions, f"Qualification burden is {process.get('qualification_burden')}.")
    if process.get("inspection_burden") == "high":
        _append_once(cautions, "Process route has high inspection burden.")
    if process.get("repairability_level") in {"limited", "poor"}:
        _append_once(cautions, "Process route has limited or poor repairability.")
    return cautions, actions


def _path_actions(architecture_path: str) -> list[str]:
    if architecture_path == "coated_metallic_tbc_path":
        return [
            "Compare against CMC/EBC path where relevant.",
        ]
    if architecture_path == "cmc_ebc_environmental_protection_path":
        return [
            "Do not treat missing literal thermal_barrier as automatic poor-fit; validate the CMC/EBC architecture path.",
        ]
    if architecture_path == "oxidation_protection_only_path":
        return [
            "Do not advance as primary option unless thermal requirement changes.",
            "Add explicit thermal protection architecture or reclassify profile.",
        ]
    if architecture_path == "wear_or_erosion_path":
        return [
            "Do not advance for hot-section thermal/oxidation profile.",
            "Evaluate under erosion_wear_surface_component profile instead.",
        ]
    if architecture_path == "monolithic_ceramic_path":
        return [
            "Use only as reference/comparison for this profile.",
            "Consider CMC or coating-enabled architecture instead.",
        ]
    if architecture_path == "graded_am_research_path":
        return [
            "Do not use as engineering selection.",
            "Require process-specific evidence before application use.",
        ]
    return ["Request missing application-fit and architecture-path evidence."]


def _analysis_status(fit_status: str) -> str:
    if fit_status in {"plausible_with_validation", "plausible_near_term_analogue"}:
        return "analysed_for_application"
    if fit_status == "poor_fit_for_profile":
        return "poor_fit_suppressed"
    if fit_status == "exploratory_only_for_profile":
        return "exploratory_context_only"
    if fit_status == "research_only_for_profile":
        return "research_context_only"
    return "insufficient_information"


def build_application_aware_limiting_factor_record(
    candidate: Mapping[str, Any],
    profile: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    app = normalise_application_profile(profile or get_default_application_profile())
    fit = _mapping(candidate.get("application_requirement_fit"))
    fit_status = _text(fit.get("fit_status"), "insufficient_information")
    architecture_path = _text(fit.get("architecture_path"), "unknown_path")
    analysis_status = _analysis_status(fit_status)
    trace = _mapping(candidate.get("_deterministic_optimisation_trace"))
    blockers: list[str] = []
    cautions: list[str] = []
    evidence: list[str] = []
    actions: list[str] = []

    for item in _as_list(fit.get("critical_blockers")):
        _append_once(blockers, _text(item))
    for item in _as_list(fit.get("major_cautions")):
        _append_once(cautions, _text(item))
    for item in _as_list(fit.get("required_next_evidence")):
        _append_once(evidence, _text(item))
    diagnostic_cautions, diagnostic_actions = _diagnostic_cautions(candidate, architecture_path)
    for item in diagnostic_cautions:
        _append_once(cautions, item)
    action_source = diagnostic_actions + _path_actions(architecture_path)
    if fit_status in {"poor_fit_for_profile", "research_only_for_profile", "exploratory_only_for_profile"}:
        action_source = _path_actions(architecture_path) + diagnostic_actions
    for item in action_source:
        _append_once(actions, item)

    missing = [_text(item) for item in _as_list(fit.get("missing_required_primary_functions")) if _text(item)]
    if missing:
        _append_once(blockers, "Missing required primary service functions: " + ", ".join(missing) + ".")
    if fit_status == "poor_fit_for_profile":
        if architecture_path in {"wear_or_erosion_path", "oxidation_protection_only_path", "monolithic_ceramic_path"}:
            _append_once(blockers, f"Architecture path {architecture_path} is mismatched to the selected profile.")
        _append_once(actions, "Do not advance for this profile.")
        _append_once(actions, "Only reconsider if application requirements change.")
        if missing:
            _append_once(actions, "Add missing protection architecture if the concept is re-evaluated.")
    elif fit_status == "research_only_for_profile":
        _append_once(blockers, "Research-only evidence maturity suppresses engineering optimisation.")
        _append_once(actions, "Retain as research-only.")
        _append_once(actions, "Do not use for engineering selection.")
    elif fit_status == "exploratory_only_for_profile":
        _append_once(blockers, "Exploratory maturity or readiness limits engineering use for this profile.")
        _append_once(actions, "Retain as exploratory concept.")
        _append_once(actions, "Define evidence required before engineering use.")
        _append_once(actions, "Compare against mature analogue.")
    elif analysis_status == "insufficient_information":
        _append_once(blockers, "Insufficient application-fit, surface-function or process-route evidence.")
        _append_once(actions, "Request missing evidence, function and process-route data.")

    if _evidence_maturity(candidate) in {"D", "E", "F"}:
        _append_once(cautions, "Evidence maturity is low for engineering use.")
    if not evidence:
        _append_once(evidence, "application-specific validation evidence")

    combined_factors = blockers + cautions
    themes = list(dict.fromkeys(_theme(item) for item in combined_factors if _text(item)))
    if architecture_path == "cmc_ebc_environmental_protection_path":
        _append_once(themes, "cmc_ebc_recession")
    if architecture_path == "coated_metallic_tbc_path":
        _append_once(themes, "coating_spallation")
    if architecture_path == "graded_am_research_path":
        _append_once(themes, "graded_am_transition_zone")
    if fit_status in {"research_only_for_profile", "exploratory_only_for_profile"}:
        _append_once(themes, "evidence_maturity")
    if fit_status == "poor_fit_for_profile":
        _append_once(themes, "application_mismatch")

    if analysis_status in {"poor_fit_suppressed", "research_context_only"}:
        retained_count = trace.get("limiting_factor_count", 0)
    else:
        retained_count = 0

    rationale = [
        f"Application fit status is {fit_status}.",
        f"Architecture path is {architecture_path}.",
        f"Analysis status is {analysis_status}.",
        "No ranking, Pareto optimisation or variant generation is performed.",
    ]
    return {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "evidence_maturity": _evidence_maturity(candidate),
        "profile_id": app.get("profile_id", "unknown_profile"),
        "application_fit_status": fit_status,
        "architecture_path": architecture_path,
        "analysis_status": analysis_status,
        "application_blockers": blockers[:8],
        "application_major_cautions": cautions[:8],
        "top_application_limiting_factors": themes[:8],
        "required_next_evidence": evidence[:8],
        "suggested_validation_or_refinement_actions": actions[:8],
        "suppressed_generic_factor_count": retained_count,
        "retained_audit_trace_reference": trace.get("candidate_id") if trace else "",
        "rationale": rationale,
        "not_a_ranking": True,
        "not_an_optimised_design": True,
        "no_variants_generated": True,
    }


def _count_themes(records: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    counter = Counter(
        _theme(item)
        for record in records
        for item in _as_list(record.get(field))
        if _text(item)
    )
    return dict(sorted(counter.items()))


def build_application_aware_limiting_factor_analysis(package: Mapping[str, Any]) -> dict[str, Any]:
    profile = normalise_application_profile(
        _mapping(package.get("application_profile"))
        or _mapping(_mapping(package.get("application_requirement_fit")).get("profile"))
        or get_default_application_profile()
    )
    traces = {
        _text(trace.get("candidate_id")): trace
        for trace in _as_list(package.get("optimisation_trace"))
        if isinstance(trace, Mapping)
    }
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    records = []
    for candidate in candidates:
        enriched = dict(candidate)
        trace = traces.get(_candidate_id(candidate))
        if trace:
            enriched["_deterministic_optimisation_trace"] = trace
        records.append(build_application_aware_limiting_factor_record(enriched, profile))

    status_counts = Counter(_text(record.get("analysis_status"), "unknown") for record in records)
    by_status: dict[str, list[str]] = {}
    for record in records:
        by_status.setdefault(_text(record.get("analysis_status"), "unknown"), []).append(_text(record.get("candidate_id")))
    evidence_counter = Counter(
        _theme(item)
        for record in records
        for item in _as_list(record.get("required_next_evidence"))
        if _text(item)
    )
    action_counter = Counter(
        _theme(item)
        for record in records
        for item in _as_list(record.get("suggested_validation_or_refinement_actions"))
        if _text(item)
    )
    concise_summary = []
    if status_counts.get("analysed_for_application"):
        concise_summary.append("Application-fit candidates receive concise validation and refinement actions.")
    if status_counts.get("poor_fit_suppressed"):
        concise_summary.append("Poor-fit candidates suppress generic optimisation and retain only profile mismatch actions.")
    if status_counts.get("research_context_only"):
        concise_summary.append("Research-only candidates are retained as context, not engineering selections.")
    warnings = []
    if not _mapping(package.get("application_requirement_fit")):
        warnings.append("Application requirement-fit matrix is missing; analysis is limited.")
    if not records:
        warnings.append("No candidates are available for application-aware limiting-factor analysis.")
    return {
        "profile": profile,
        "candidate_count": len(candidates),
        "records": records,
        "analysis_status_counts": dict(sorted(status_counts.items())),
        "candidate_ids_by_analysis_status": {key: value for key, value in sorted(by_status.items())},
        "blocker_theme_counts": _count_themes(records, "application_blockers"),
        "caution_theme_counts": _count_themes(records, "application_major_cautions"),
        "required_next_evidence_themes": dict(sorted(evidence_counter.items())),
        "suggested_action_theme_counts": dict(sorted(action_counter.items())),
        "concise_summary": concise_summary,
        "warnings": warnings,
        "no_ranking_applied": True,
        "no_pareto_optimisation": True,
        "no_variants_generated": True,
        "not_final_selection": True,
    }


def attach_application_aware_limiting_factor_analysis(package: Mapping[str, Any]) -> dict[str, Any]:
    output = dict(package)
    analysis = build_application_aware_limiting_factor_analysis(package)
    records_by_id = {
        _text(record.get("candidate_id")): dict(record)
        for record in _as_list(analysis.get("records"))
        if isinstance(record, Mapping)
    }
    candidates = []
    for candidate in _as_list(package.get("candidate_systems")):
        if isinstance(candidate, Mapping):
            enriched = dict(candidate)
            enriched["application_aware_limiting_factors"] = records_by_id.get(_candidate_id(candidate), {})
            candidates.append(enriched)
    output["candidate_systems"] = candidates
    output["application_aware_limiting_factor_analysis"] = analysis
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "application_aware_limiting_factor_analysis_attached": True,
            "application_aware_ranking_performed": False,
            "application_aware_variants_generated": False,
        }
    )
    output["diagnostics"] = diagnostics
    warnings = [_text(item) for item in _as_list(package.get("warnings")) if _text(item)]
    for warning in _as_list(analysis.get("warnings")):
        text = _text(warning)
        if text and text not in warnings:
            warnings.append(text)
    output["warnings"] = warnings
    output["application_profile"] = deepcopy(_mapping(package.get("application_profile")))
    return output
