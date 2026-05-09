from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any


BUCKETS = (
    "near_term_comparison_references",
    "validation_needed_options",
    "exploratory_context_only",
    "research_only_context",
    "poor_fit_for_profile",
    "insufficient_information",
)

CMC_EBC_PATH = "cmc_ebc_environmental_protection_path"
CMC_EBC_CAUTION = (
    "CMC/EBC path is an alternative environmental-protection architecture, "
    "not a direct TBC equivalence."
)
CMC_EBC_REQUIRED_EVIDENCE = (
    "EBC recession/environmental durability evidence",
    "EBC/substrate compatibility evidence",
    "CMC/EBC NDI acceptance criteria",
    "repair/disposition rules",
    "thermal cycling evidence for the target duty cycle",
    "comparison against Ni/TBC reference architecture",
)


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


def _system_name(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_name") or candidate.get("name"), "Unnamed material system")


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    return _text(
        evidence.get("maturity")
        or evidence.get("evidence_maturity")
        or candidate.get("evidence_maturity"),
        "unknown",
    ).upper()


def _readiness_from_maturity(maturity: str) -> tuple[str, str]:
    if maturity in {"A", "B"}:
        return "usable_as_reference", "strong_engineering_analogue"
    if maturity == "C":
        return "usable_with_caveats", "caveated_engineering_option"
    if maturity in {"D", "E"}:
        return "exploratory_only", "exploratory_concept_only"
    if maturity == "F":
        return "research_only", "research_mode_only"
    return "unknown", "unknown_readiness"


def _decision_readiness(candidate: Mapping[str, Any], maturity: str) -> tuple[str, str]:
    readiness = _mapping(candidate.get("decision_readiness"))
    status = _text(readiness.get("readiness_status"))
    category = _text(readiness.get("readiness_category"))
    if status or category:
        return status or _readiness_from_maturity(maturity)[0], category or _readiness_from_maturity(maturity)[1]
    fallback_status, fallback_category = _readiness_from_maturity(maturity)
    return fallback_status, fallback_category


def _append_once(items: list[str], value: str) -> None:
    text = _text(value)
    if text and text not in items:
        items.append(text)


def _merged_texts(*values: Any, limit: int = 8) -> list[str]:
    output: list[str] = []
    for value in values:
        for item in _as_list(value):
            _append_once(output, _text(item))
    return output[:limit]


def _bucket_use(bucket: str) -> tuple[str, str]:
    by_bucket = {
        "near_term_comparison_references": (
            "Use as comparison references or engineering analogues with stated caveats.",
            "Do not treat as final material selection or certification approval.",
        ),
        "validation_needed_options": (
            "Use as plausible application-relevant options requiring validation.",
            "Do not advance without resolving the listed validation evidence.",
        ),
        "exploratory_context_only": (
            "Use only as exploratory context for future investigation.",
            "Do not treat as engineering-ready.",
        ),
        "research_only_context": (
            "Use only as research context.",
            "Do not use for engineering selection.",
        ),
        "poor_fit_for_profile": (
            "Do not advance for this selected profile.",
            "Reconsider only if application requirements change or missing architecture is added.",
        ),
        "insufficient_information": (
            "Use only to document missing information before review.",
            "Do not advance until application fit and analysis status are clarified.",
        ),
    }
    return by_bucket[bucket]


def _bucket_role(bucket: str) -> str:
    return {
        "near_term_comparison_references": "comparison_reference",
        "validation_needed_options": "validation_needed_application_option",
        "exploratory_context_only": "exploratory_context",
        "research_only_context": "research_context",
        "poor_fit_for_profile": "do_not_advance_for_selected_profile",
        "insufficient_information": "information_gap",
    }[bucket]


def _is_cmc_ebc_plausible(architecture_path: str, fit_status: str, analysis_status: str) -> bool:
    return (
        architecture_path == CMC_EBC_PATH
        and fit_status == "plausible_with_validation"
        and analysis_status == "analysed_for_application"
    )


def _assign_bucket(
    *,
    fit_status: str,
    analysis_status: str,
    maturity: str,
    readiness_status: str,
    readiness_category: str,
) -> str:
    if fit_status == "poor_fit_for_profile" or analysis_status == "poor_fit_suppressed":
        return "poor_fit_for_profile"
    if (
        fit_status == "insufficient_information"
        or analysis_status == "insufficient_information"
        or not fit_status
        or not analysis_status
    ):
        return "insufficient_information"
    if fit_status == "research_only_for_profile" or analysis_status == "research_context_only":
        return "research_only_context"
    if maturity == "F" or readiness_status == "research_only":
        return "research_only_context"
    if (
        fit_status == "exploratory_only_for_profile"
        or analysis_status == "exploratory_context_only"
        or maturity in {"D", "E"}
    ):
        return "exploratory_context_only"
    if (
        fit_status in {"plausible_with_validation", "plausible_near_term_analogue"}
        and analysis_status == "analysed_for_application"
        and maturity in {"A", "B"}
        and (
            readiness_status == "usable_as_reference"
            or readiness_category == "strong_engineering_analogue"
            or maturity in {"A", "B"} and readiness_status == "unknown"
        )
    ):
        return "near_term_comparison_references"
    if (
        fit_status == "plausible_with_validation"
        and analysis_status == "analysed_for_application"
        and (
            maturity == "C"
            or readiness_status == "usable_with_caveats"
            or readiness_category == "caveated_engineering_option"
        )
    ):
        return "validation_needed_options"
    if fit_status in {"plausible_with_validation", "plausible_near_term_analogue"}:
        return "validation_needed_options"
    return "insufficient_information"


def _why(bucket: str, fit_status: str, analysis_status: str, maturity: str, readiness_status: str) -> str:
    return {
        "near_term_comparison_references": (
            f"{maturity} maturity, {readiness_status} readiness and {fit_status} fit make this useful "
            "as a comparison reference for the selected profile."
        ),
        "validation_needed_options": (
            f"{fit_status} fit is application-relevant, but {maturity} maturity or {readiness_status} "
            "readiness keeps it validation-dependent."
        ),
        "exploratory_context_only": (
            f"{fit_status} fit or {analysis_status} analysis indicates exploratory context only for this profile."
        ),
        "research_only_context": (
            f"{maturity} maturity, {readiness_status} readiness or {analysis_status} analysis keeps this in research context."
        ),
        "poor_fit_for_profile": (
            f"{fit_status} fit or {analysis_status} analysis says this should not advance for the selected profile."
        ),
        "insufficient_information": "Application fit or application-aware analysis information is insufficient.",
    }[bucket]


def _default_actions(bucket: str) -> list[str]:
    return {
        "near_term_comparison_references": [
            "Use as a baseline comparison reference.",
            "Compare validation questions against the selected application profile.",
        ],
        "validation_needed_options": [
            "Define application-specific validation plan.",
            "Close listed evidence gaps before engineering decision use.",
        ],
        "exploratory_context_only": [
            "Keep visible for future investigation.",
            "Do not advance as an engineering option for this profile.",
        ],
        "research_only_context": [
            "Keep in research context only.",
            "Do not use for engineering selection.",
        ],
        "poor_fit_for_profile": [
            "Do not advance for selected profile.",
            "Reconsider only if requirements change or missing architecture is added.",
        ],
        "insufficient_information": [
            "Collect missing application-fit and analysis evidence.",
            "Reassess after required fields are available.",
        ],
    }[bucket]


def build_controlled_shortlist_record(candidate: Mapping[str, Any]) -> dict[str, Any]:
    fit = _mapping(candidate.get("application_requirement_fit"))
    aware = _mapping(candidate.get("application_aware_limiting_factors"))
    maturity = _evidence_maturity(candidate)
    readiness_status, readiness_category = _decision_readiness(candidate, maturity)
    fit_status = _text(
        aware.get("application_fit_status") or fit.get("fit_status"),
        "insufficient_information",
    )
    analysis_status = _text(aware.get("analysis_status"), "insufficient_information")
    architecture_path = _text(
        aware.get("architecture_path") or fit.get("architecture_path"),
        "unknown_path",
    )
    bucket = _assign_bucket(
        fit_status=fit_status,
        analysis_status=analysis_status,
        maturity=maturity,
        readiness_status=readiness_status,
        readiness_category=readiness_category,
    )

    blockers = _merged_texts(aware.get("application_blockers"), fit.get("critical_blockers"), limit=6)
    cautions = _merged_texts(
        aware.get("application_major_cautions"),
        fit.get("major_cautions"),
        fit.get("architecture_path_cautions"),
        limit=6,
    )
    required_evidence = _merged_texts(
        aware.get("required_next_evidence"),
        fit.get("required_next_evidence"),
        _mapping(candidate.get("decision_readiness")).get("required_next_evidence"),
        limit=8,
    )
    actions = _merged_texts(
        aware.get("suggested_validation_or_refinement_actions"),
        _default_actions(bucket),
        limit=8,
    )

    if bucket == "poor_fit_for_profile":
        _append_once(actions, "Do not advance for selected profile.")
    if bucket == "insufficient_information":
        _append_once(blockers, "Required application-fit or application-aware analysis fields are missing.")
    if _is_cmc_ebc_plausible(architecture_path, fit_status, analysis_status):
        _append_once(cautions, CMC_EBC_CAUTION)
        for item in CMC_EBC_REQUIRED_EVIDENCE:
            _append_once(required_evidence, item)

    responsible_use, disallowed_use = _bucket_use(bucket)
    return {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "evidence_maturity": maturity,
        "decision_readiness_status": readiness_status,
        "application_fit_status": fit_status,
        "architecture_path": architecture_path,
        "application_analysis_status": analysis_status,
        "shortlist_bucket": bucket,
        "shortlist_role": _bucket_role(bucket),
        "why_in_bucket": _why(bucket, fit_status, analysis_status, maturity, readiness_status),
        "key_blockers": blockers,
        "key_cautions": cautions,
        "required_next_evidence": required_evidence,
        "suggested_next_actions": actions,
        "responsible_use": responsible_use,
        "disallowed_use": disallowed_use,
        "not_a_final_recommendation": True,
        "no_ranking_applied": True,
        "no_selection_made": True,
    }


def _count_themes(records: Sequence[Mapping[str, Any]], field: str) -> list[str]:
    counter = Counter(
        _text(item)
        for record in records
        for item in _as_list(record.get(field))
        if _text(item)
    )
    return [item for item, _ in counter.most_common(8)]


def build_controlled_application_shortlist(package: Mapping[str, Any]) -> dict[str, Any]:
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    records = [build_controlled_shortlist_record(candidate) for candidate in candidates]
    bucket_counts = {bucket: 0 for bucket in BUCKETS}
    candidate_ids_by_bucket = {bucket: [] for bucket in BUCKETS}
    for record in records:
        bucket = _text(record.get("shortlist_bucket"), "insufficient_information")
        bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
        candidate_ids_by_bucket.setdefault(bucket, []).append(_text(record.get("candidate_id")))

    profile = deepcopy(
        _mapping(package.get("application_profile"))
        or _mapping(_mapping(package.get("application_requirement_fit")).get("profile"))
    )
    warnings = []
    if not _mapping(package.get("application_requirement_fit")):
        warnings.append("Application requirement-fit matrix is missing.")
    if not _mapping(package.get("application_aware_limiting_factor_analysis")):
        warnings.append("Application-aware limiting-factor analysis is missing.")
    if not records:
        warnings.append("No candidates are available for controlled application shortlisting.")

    shortlist_summary = [
        "Controlled shortlist buckets preserve candidate order and are not rankings.",
        "Near-term references anchor comparison only; validation-needed options remain evidence-gated.",
        "Exploratory and research-only candidates are retained as context separate from engineering options.",
        "Poor-fit candidates are parked unless the selected application profile changes.",
    ]
    bucket_rationales = {
        "near_term_comparison_references": "Mature or strong-analogue plausible candidates used only as comparison references.",
        "validation_needed_options": "Application-relevant plausible candidates that need significant validation before engineering decision use.",
        "exploratory_context_only": "Emerging or exploratory candidates kept visible but separate from engineering options.",
        "research_only_context": "F maturity or research-mode concepts retained only as research context.",
        "poor_fit_for_profile": "Candidates suppressed by the application-fit layer for this selected profile.",
        "insufficient_information": "Candidates missing required application-fit or application-aware analysis fields.",
    }
    return {
        "profile": profile,
        "candidate_count": len(candidates),
        "records": records,
        "bucket_counts": bucket_counts,
        "candidate_ids_by_bucket": candidate_ids_by_bucket,
        "shortlist_summary": shortlist_summary,
        "bucket_rationales": bucket_rationales,
        "cross_bucket_evidence_themes": _count_themes(records, "required_next_evidence"),
        "cross_bucket_caution_themes": _count_themes(records, "key_cautions"),
        "suggested_review_sequence": [
            "Review near-term comparison references to anchor the application baseline.",
            "Review validation-needed options against the same evidence questions.",
            "Keep exploratory context visible but separate from engineering options.",
            "Keep research-only candidates out of engineering decision use.",
            "Park poor-fit candidates unless the application profile changes.",
        ],
        "warnings": warnings,
        "not_a_final_recommendation": True,
        "no_ranking_applied": True,
        "no_selection_made": True,
        "no_variants_generated": True,
        "no_pareto_optimisation": True,
    }


def attach_controlled_application_shortlist(package: Mapping[str, Any]) -> dict[str, Any]:
    output = dict(package)
    shortlist = build_controlled_application_shortlist(package)
    records_by_id = {
        _text(record.get("candidate_id")): dict(record)
        for record in _as_list(shortlist.get("records"))
        if isinstance(record, Mapping)
    }
    candidates = []
    for candidate in _as_list(package.get("candidate_systems")):
        if isinstance(candidate, Mapping):
            enriched = dict(candidate)
            enriched["controlled_shortlist_record"] = records_by_id.get(_candidate_id(candidate), {})
            candidates.append(enriched)
    output["candidate_systems"] = candidates
    output["controlled_application_shortlist"] = shortlist
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))
    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics.update(
        {
            "controlled_application_shortlist_attached": True,
            "controlled_application_shortlist_ranking_performed": False,
            "controlled_application_shortlist_variants_generated": False,
            "controlled_application_shortlist_selection_made": False,
        }
    )
    output["diagnostics"] = diagnostics
    warnings = [_text(item) for item in _as_list(package.get("warnings")) if _text(item)]
    for warning in _as_list(shortlist.get("warnings")):
        text = _text(warning)
        if text and text not in warnings:
            warnings.append(text)
    output["warnings"] = warnings
    return output
