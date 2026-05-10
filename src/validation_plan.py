from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any


VALIDATION_PLAN_STATUSES = (
    "baseline_reference_validation",
    "validation_required_before_engineering_use",
    "exploratory_validation_only",
    "research_validation_only",
    "parked_no_validation_for_this_profile",
    "insufficient_information",
)

BUCKET_TO_STATUS = {
    "near_term_comparison_references": "baseline_reference_validation",
    "validation_needed_options": "validation_required_before_engineering_use",
    "exploratory_context_only": "exploratory_validation_only",
    "research_only_context": "research_validation_only",
    "poor_fit_for_profile": "parked_no_validation_for_this_profile",
    "insufficient_information": "insufficient_information",
}

RESPONSIBLE_USE = {
    "near_term_comparison_references": "Use to anchor comparison and validation questions.",
    "validation_needed_options": "Use to define evidence required before engineering decision use.",
    "exploratory_context_only": "Use only for feasibility or future investigation.",
    "research_only_context": "Use only as research context.",
    "poor_fit_for_profile": "Do not validate for this selected profile unless requirements change.",
    "insufficient_information": "Use only to request missing fields before validation planning.",
}

DISCLAIMER = (
    "This is a validation-planning scaffold only; it is not qualification approval, "
    "certification approval, final material selection or an optimised design."
)

DO_NOT_USE_FOR = [
    "final selection",
    "certification approval",
    "qualification approval",
    "production release",
    "ranking or winner selection",
]


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


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _append(items: list[str], item: str) -> None:
    text = _text(item)
    if text and text not in items:
        items.append(text)


def _extend(items: list[str], values: Any) -> None:
    for value in _as_list(values):
        _append(items, _text(value))


def _theme_count(records: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    counter = Counter(
        _text(item)
        for record in records
        for item in _as_list(record.get(field))
        if _text(item)
    )
    return dict(sorted(counter.items()))


def _candidate_ids_by_status(records: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    grouped = {status: [] for status in VALIDATION_PLAN_STATUSES}
    for record in records:
        status = _text(record.get("validation_plan_status"), "insufficient_information")
        grouped.setdefault(status, []).append(_text(record.get("candidate_id")))
    return grouped


def _bucket_objective(bucket: str) -> str:
    return {
        "near_term_comparison_references": "Use as a baseline or comparison reference; do not select.",
        "validation_needed_options": "Define evidence needed before engineering decision use.",
        "exploratory_context_only": "Determine whether feasibility evidence could justify later validation-needed status.",
        "research_only_context": "Retain as research context only; no engineering-use pathway is implied.",
        "poor_fit_for_profile": "Avoid validation effort under the selected profile.",
        "insufficient_information": "Request missing fields before validation planning.",
    }.get(bucket, "Request missing fields before validation planning.")


def _add_bucket_items(
    *,
    bucket: str,
    activities: list[str],
    evidence_gaps: list[str],
    certification_items: list[str],
    comparison_items: list[str],
    sme_items: list[str],
    exit_criteria: list[str],
    themes: list[str],
    evidence_gap_themes: list[str],
    sme_themes: list[str],
) -> None:
    if bucket == "near_term_comparison_references":
        for item in (
            "Confirm service-environment assumptions.",
            "Confirm component-specific thermal cycle and oxidation/steam exposure assumptions.",
            "Validate known critical failure modes for the target duty cycle.",
            "Define inspection and repair acceptance criteria.",
            "Compare validation burden against other shortlist buckets.",
        ):
            _append(activities, item)
        _append(comparison_items, "Define baseline acceptance questions.")
        _append(comparison_items, "Compare inspection, repair and certification burden against other buckets.")
        _extend(themes, ["service_environment_definition", "thermal_cycle_validation", "repair_disposition"])
    elif bucket == "validation_needed_options":
        for item in (
            "Close critical evidence gaps before engineering decision use.",
            "Validate the process route and route repeatability.",
            "Validate interface durability assumptions.",
            "Validate inspection and repair assumptions.",
            "Define go/no-go evidence gates.",
        ):
            _append(activities, item)
        _append(comparison_items, "Compare validation burden against near-term references.")
        _extend(themes, ["process_route_repeatability", "repair_disposition"])
        _append(evidence_gap_themes, "evidence_maturity_gap")
    elif bucket == "exploratory_context_only":
        for item in (
            "Define minimum feasibility evidence needed before moving to validation-needed status.",
            "Assess mechanism feasibility and environmental compatibility.",
            "Assess inspection feasibility without creating an engineering qualification plan.",
            "Define evidence maturity uplift needed for future review.",
        ):
            _append(activities, item)
        _append(evidence_gaps, "Evidence maturity uplift is required before engineering validation planning.")
        _extend(themes, ["service_environment_definition", "evidence_maturity_gap"])
        _append(evidence_gap_themes, "evidence_maturity_gap")
    elif bucket == "research_only_context":
        for item in (
            "Limit work to laboratory or research evidence.",
            "Do not create engineering selection or qualification activities.",
            "Define measurement and inspection feasibility questions only.",
        ):
            _append(activities, item)
        _append(evidence_gaps, "Research-only maturity is not sufficient for engineering selection.")
        _append(evidence_gap_themes, "evidence_maturity_gap")
    elif bucket == "poor_fit_for_profile":
        for item in (
            "Do not spend validation effort under this selected profile.",
            "Document the application/profile mismatch.",
            "Re-evaluate only if requirements change or a missing architecture is added.",
        ):
            _append(activities, item)
        _append(evidence_gaps, "Application/profile mismatch prevents validation planning for this profile.")
        _extend(themes, ["application_profile_mismatch", "parked_profile_mismatch"])
        _extend(evidence_gap_themes, ["application_profile_mismatch", "parked_profile_mismatch"])
    else:
        _append(evidence_gaps, "Controlled shortlist or application-fit information is missing.")
        _append(activities, "Collect missing application-fit, shortlist and architecture-path fields.")
        _append(evidence_gap_themes, "evidence_maturity_gap")

    _append(certification_items, "Review certification and airworthiness implications with SMEs before any next gate.")
    _extend(sme_items, ["materials SME review", "manufacturing SME review", "NDI SME review", "repair SME review"])
    _extend(sme_themes, ["certification_review", "airworthiness_review"])
    _append(exit_criteria, "Document that the result is not qualification approval or certification approval.")


def _add_architecture_items(
    *,
    architecture_path: str,
    status: str,
    activities: list[str],
    inspection_items: list[str],
    repair_items: list[str],
    process_items: list[str],
    interface_items: list[str],
    environmental_items: list[str],
    mechanical_items: list[str],
    certification_items: list[str],
    comparison_items: list[str],
    evidence_gaps: list[str],
    exit_criteria: list[str],
    themes: list[str],
    evidence_gap_themes: list[str],
) -> None:
    if architecture_path == "coated_metallic_tbc_path":
        for item in (
            "Define thermal-cycle exposure matrix for the target duty cycle.",
            "Validate bond coat/top coat adhesion and spallation resistance.",
            "Validate CTE mismatch and substrate compatibility risks.",
            "Validate oxidation and hot-corrosion exposure response.",
        ):
            _append(activities, item)
        _append(inspection_items, "Define coating thickness, defect inspection method and acceptance limits.")
        _append(repair_items, "Define repair/recoat criteria and substrate disposition rules.")
        _append(process_items, "Validate coating-process repeatability and thickness control.")
        _append(interface_items, "Validate bond coat/top coat adhesion and substrate compatibility.")
        _append(environmental_items, "Validate oxidation/hot-corrosion exposure for target environment.")
        _append(mechanical_items, "Validate thermal-cycle durability and spallation resistance.")
        _append(comparison_items, "Compare validation burden against CMC/EBC path.")
        _extend(
            themes,
            [
                "thermal_cycle_validation",
                "oxidation_hot_corrosion_validation",
                "coating_spallation",
                "coating_adhesion",
                "cte_mismatch",
                "ndi_acceptance",
                "repair_disposition",
            ],
        )
    elif architecture_path == "cmc_ebc_environmental_protection_path":
        _append(evidence_gaps, "CMC/EBC path is an alternative environmental-protection architecture, not a direct TBC equivalence.")
        for item in (
            "Define EBC recession/environmental durability test evidence for target environment.",
            "Validate EBC/substrate compatibility and CTE mismatch risk.",
            "Validate CMC interphase, fiber and matrix durability under target duty cycle.",
            "Compare validation burden against Ni/TBC reference architecture.",
        ):
            _append(activities, item)
        _append(inspection_items, "Define CMC/EBC NDI acceptance criteria.")
        _append(repair_items, "Define EBC repair and CMC substrate disposition rules.")
        _append(process_items, "Validate CMC/EBC process route repeatability for the selected architecture.")
        _append(interface_items, "Validate EBC/substrate compatibility and environmental barrier integrity.")
        _append(environmental_items, "Validate EBC recession, steam durability and environmental barrier integrity.")
        _append(mechanical_items, "Validate thermal cycling and delamination risk.")
        _append(comparison_items, "Compare validation burden against Ni/TBC reference architecture.")
        _extend(
            themes,
            [
                "steam_recession_validation",
                "ebc_recession",
                "ebc_substrate_compatibility",
                "cmc_interphase_durability",
                "thermal_cycle_validation",
                "cte_mismatch",
                "ndi_acceptance",
                "repair_disposition",
            ],
        )
        _extend(evidence_gap_themes, ["ebc_recession", "ebc_substrate_compatibility", "cmc_interphase_durability"])
    elif architecture_path == "oxidation_protection_only_path":
        _append(environmental_items, "Define oxidation exposure evidence and protection breach tolerance.")
        _append(evidence_gaps, "Assess thermal-barrier gap for the selected profile.")
        _append(exit_criteria, "Re-evaluate only if requirements change or thermal protection architecture is added.")
        _extend(themes, ["oxidation_hot_corrosion_validation", "application_profile_mismatch"])
    elif architecture_path == "wear_or_erosion_path":
        _append(evidence_gaps, "Application/profile mismatch: wear or erosion path is not the current hot-section validation profile.")
        _append(exit_criteria, "Evaluate under erosion_wear_surface_component profile if requirements change.")
        _extend(themes, ["application_profile_mismatch", "parked_profile_mismatch"])
    elif architecture_path == "monolithic_ceramic_path":
        if status in {"baseline_reference_validation", "parked_no_validation_for_this_profile"}:
            _append(mechanical_items, "If retained as comparison context, define flaw tolerance, proof testing and thermal shock assumptions.")
            _append(repair_items, "Define repair/replacement assumptions for brittle monolithic architecture.")
            _extend(themes, ["proof_testing", "flaw_tolerance"])
        _append(evidence_gaps, "Consider CMC or coating-enabled architecture for this selected profile.")
    elif architecture_path == "graded_am_research_path":
        for item in (
            "Validate transition-zone feasibility at coupon level.",
            "Map residual stress across the gradient transition.",
            "Assess process-window repeatability.",
            "Assess through-depth inspection feasibility.",
            "Assess repair/rebuild feasibility before any engineering-use discussion.",
        ):
            _append(activities, item)
        _append(process_items, "Define graded AM process-window repeatability evidence.")
        _append(inspection_items, "Define through-depth inspection feasibility evidence.")
        _append(repair_items, "Assess repair/rebuild feasibility for the transition zone.")
        _append(mechanical_items, "Map transition-zone residual stress and cracking/delamination risk.")
        _extend(
            themes,
            [
                "transition_zone_validation",
                "residual_stress_mapping",
                "process_route_repeatability",
                "through_depth_inspection",
                "repair_disposition",
            ],
        )
        _extend(evidence_gap_themes, ["transition_zone_validation", "residual_stress_mapping", "through_depth_inspection"])


def build_candidate_validation_plan_record(candidate: Mapping[str, Any]) -> dict[str, Any]:
    shortlist = _mapping(candidate.get("controlled_shortlist_record"))
    fit = _mapping(candidate.get("application_requirement_fit"))
    aware = _mapping(candidate.get("application_aware_limiting_factors"))

    bucket = _text(shortlist.get("shortlist_bucket"), "insufficient_information")
    status = BUCKET_TO_STATUS.get(bucket, "insufficient_information")
    candidate_id = _candidate_id(candidate)
    architecture_path = _text(
        shortlist.get("architecture_path") or aware.get("architecture_path") or fit.get("architecture_path"),
        "unknown_path",
    )

    evidence_gaps: list[str] = []
    required_activities: list[str] = []
    inspection_items: list[str] = []
    repair_items: list[str] = []
    process_items: list[str] = []
    interface_items: list[str] = []
    environmental_items: list[str] = []
    mechanical_items: list[str] = []
    certification_items: list[str] = []
    sme_items: list[str] = []
    comparison_items: list[str] = []
    exit_criteria: list[str] = []
    themes: list[str] = []
    evidence_gap_themes: list[str] = []
    sme_themes: list[str] = []

    _extend(evidence_gaps, shortlist.get("required_next_evidence"))
    _extend(evidence_gaps, _mapping(candidate.get("decision_readiness")).get("required_next_evidence"))
    _extend(required_activities, shortlist.get("suggested_next_actions"))
    _extend(evidence_gaps, shortlist.get("key_blockers"))
    _extend(evidence_gaps, shortlist.get("key_cautions"))

    _add_bucket_items(
        bucket=bucket,
        activities=required_activities,
        evidence_gaps=evidence_gaps,
        certification_items=certification_items,
        comparison_items=comparison_items,
        sme_items=sme_items,
        exit_criteria=exit_criteria,
        themes=themes,
        evidence_gap_themes=evidence_gap_themes,
        sme_themes=sme_themes,
    )
    _add_architecture_items(
        architecture_path=architecture_path,
        status=status,
        activities=required_activities,
        inspection_items=inspection_items,
        repair_items=repair_items,
        process_items=process_items,
        interface_items=interface_items,
        environmental_items=environmental_items,
        mechanical_items=mechanical_items,
        certification_items=certification_items,
        comparison_items=comparison_items,
        evidence_gaps=evidence_gaps,
        exit_criteria=exit_criteria,
        themes=themes,
        evidence_gap_themes=evidence_gap_themes,
    )

    if status == "parked_no_validation_for_this_profile":
        inspection_items.clear()
        repair_items.clear()
        process_items.clear()
        interface_items.clear()
        environmental_items.clear()
        mechanical_items.clear()
        _append(certification_items, "No certification or airworthiness validation plan for this selected profile.")
    if status in {"exploratory_validation_only", "research_validation_only"}:
        _append(exit_criteria, "Do not advance to engineering selection or qualification planning from this scaffold.")
    if status == "validation_required_before_engineering_use":
        _append(exit_criteria, "Go/no-go evidence gates are resolved against near-term references.")
    if status == "baseline_reference_validation":
        _append(exit_criteria, "Baseline comparison questions and acceptance criteria are documented.")

    return {
        "candidate_id": candidate_id,
        "system_name": _text(shortlist.get("system_name") or candidate.get("system_name") or candidate.get("name"), "Unnamed material system"),
        "candidate_class": _text(shortlist.get("candidate_class") or candidate.get("candidate_class") or candidate.get("system_class"), "unknown"),
        "evidence_maturity": _text(shortlist.get("evidence_maturity"), _evidence_maturity(candidate)),
        "shortlist_bucket": bucket,
        "application_fit_status": _text(shortlist.get("application_fit_status") or aware.get("application_fit_status") or fit.get("fit_status"), "insufficient_information"),
        "architecture_path": architecture_path,
        "application_analysis_status": _text(shortlist.get("application_analysis_status") or aware.get("analysis_status"), "insufficient_information"),
        "validation_plan_status": status,
        "validation_objective": _bucket_objective(bucket),
        "evidence_gaps": evidence_gaps,
        "required_validation_activities": required_activities,
        "inspection_and_ndi_plan_items": inspection_items,
        "repair_and_disposition_plan_items": repair_items,
        "process_route_validation_items": process_items,
        "interface_validation_items": interface_items,
        "environmental_exposure_validation_items": environmental_items,
        "mechanical_or_thermal_validation_items": mechanical_items,
        "certification_or_airworthiness_review_items": certification_items,
        "sme_review_items": sme_items,
        "comparison_baseline_items": comparison_items,
        "exit_criteria_before_next_gate": exit_criteria,
        "validation_activity_themes": themes,
        "evidence_gap_themes": evidence_gap_themes,
        "sme_review_themes": sme_themes,
        "do_not_use_for": list(DO_NOT_USE_FOR),
        "responsible_use": RESPONSIBLE_USE.get(bucket, RESPONSIBLE_USE["insufficient_information"]),
        "validation_plan_disclaimer": DISCLAIMER,
        "no_ranking_applied": True,
        "no_selection_made": True,
        "no_variants_generated": True,
        "not_certification_approval": True,
        "not_qualification_approval": True,
    }


def _bucket_level_validation_plans() -> dict[str, dict[str, Any]]:
    return {
        "near_term_comparison_references": {
            "objective": "establish baseline comparison and validation questions",
            "activities": [
                "compare service environment assumptions",
                "compare inspection/repair burden",
                "compare certification burden",
                "define baseline acceptance questions",
            ],
        },
        "validation_needed_options": {
            "objective": "close evidence gaps before engineering use",
            "activities": [
                "resolve critical environmental/interface/process gaps",
                "define coupon/subcomponent evidence needs",
                "compare against near-term references",
            ],
        },
        "exploratory_context_only": {
            "objective": "determine whether concept merits future validation-needed status",
            "activities": [
                "mechanism feasibility",
                "exposure compatibility",
                "inspectability feasibility",
                "evidence maturity uplift",
            ],
        },
        "research_only_context": {
            "objective": "retain research visibility only",
            "activities": [
                "research evidence, no engineering-use gate",
                "process feasibility",
                "measurement/inspection feasibility",
            ],
        },
        "poor_fit_for_profile": {
            "objective": "do not spend validation effort under this profile",
            "activities": [
                "park candidate",
                "document mismatch",
                "revisit only under changed application profile",
            ],
        },
    }


def build_validation_plan(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    records = [build_candidate_validation_plan_record(candidate) for candidate in candidates]
    status_counts = {status: 0 for status in VALIDATION_PLAN_STATUSES}
    for record in records:
        status = _text(record.get("validation_plan_status"), "insufficient_information")
        status_counts[status] = status_counts.get(status, 0) + 1

    profile = deepcopy(
        _mapping(package.get("application_profile"))
        or _mapping(_mapping(package.get("application_requirement_fit")).get("profile"))
        or _mapping(_mapping(package.get("controlled_application_shortlist")).get("profile"))
    )
    warnings: list[str] = []
    if not _mapping(package.get("controlled_application_shortlist")):
        warnings.append("Controlled application shortlist is missing.")
    if not records:
        warnings.append("No candidates are available for validation planning.")

    return {
        "profile": profile,
        "candidate_count": len(candidates),
        "records": records,
        "validation_plan_status_counts": status_counts,
        "candidate_ids_by_validation_plan_status": _candidate_ids_by_status(records),
        "validation_activity_theme_counts": _theme_count(records, "validation_activity_themes"),
        "evidence_gap_theme_counts": _theme_count(records, "evidence_gap_themes"),
        "sme_review_theme_counts": _theme_count(records, "sme_review_themes"),
        "bucket_level_validation_plans": _bucket_level_validation_plans(),
        "suggested_validation_workflow": [
            "Confirm service environment and profile assumptions.",
            "Use near-term comparison references to define baseline evidence questions.",
            "For validation-needed options, close architecture-specific evidence gaps.",
            "Keep exploratory concepts in feasibility validation only.",
            "Keep research-only concepts out of engineering validation.",
            "Park poor-fit candidates unless requirements change.",
            "Review all plans with materials, manufacturing, NDI, repair and certification SMEs.",
        ],
        "warnings": warnings,
        "not_final_selection": True,
        "no_ranking_applied": True,
        "no_selection_made": True,
        "no_variants_generated": True,
        "no_pareto_optimisation": True,
        "not_certification_approval": True,
        "not_qualification_approval": True,
    }


def attach_validation_plan(package: Mapping[str, Any]) -> dict[str, Any]:
    output = dict(package)
    plan = build_validation_plan(package)
    records_by_id = {
        _text(record.get("candidate_id")): dict(record)
        for record in _as_list(plan.get("records"))
        if isinstance(record, Mapping)
    }
    candidates: list[dict[str, Any]] = []
    for candidate in _as_list(package.get("candidate_systems")):
        if isinstance(candidate, Mapping):
            enriched = dict(candidate)
            enriched["validation_plan_record"] = records_by_id.get(_candidate_id(candidate), {})
            candidates.append(enriched)
    output["candidate_systems"] = candidates
    output["validation_plan"] = plan
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    output["controlled_application_shortlist"] = deepcopy(_mapping(package.get("controlled_application_shortlist")))
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "validation_plan_attached": True,
            "validation_plan_ranking_performed": False,
            "validation_plan_selection_made": False,
            "validation_plan_variants_generated": False,
            "validation_plan_certification_approval": False,
            "validation_plan_qualification_approval": False,
        }
    )
    output["diagnostics"] = diagnostics
    warnings = [_text(item) for item in _as_list(package.get("warnings")) if _text(item)]
    for warning in _as_list(plan.get("warnings")):
        _append(warnings, _text(warning))
    output["warnings"] = warnings
    return output
