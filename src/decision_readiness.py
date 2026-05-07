from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


READINESS_LABELS = {
    "mature_reference": "Mature comparison reference",
    "strong_engineering_analogue": "Strong engineering analogue",
    "caveated_engineering_option": "Caveated engineering option",
    "emerging_validation_needed": "Emerging option - validation needed",
    "exploratory_concept_only": "Exploratory concept only",
    "research_mode_only": "Research-mode only",
    "not_decision_ready": "Not decision-ready",
    "unknown_readiness": "Unknown decision readiness",
}

_EVIDENCE_TO_CATEGORY = {
    "A": "mature_reference",
    "B": "strong_engineering_analogue",
    "C": "caveated_engineering_option",
    "D": "emerging_validation_needed",
    "E": "exploratory_concept_only",
    "F": "research_mode_only",
}
_LOW_MATURITY = {"D", "E", "F"}
_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "blocking": 4}


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


def classify_evidence_readiness(evidence_maturity: str | None) -> dict[str, Any]:
    maturity = _text(evidence_maturity, "unknown").upper()
    category = _EVIDENCE_TO_CATEGORY.get(maturity, "unknown_readiness")
    label = READINESS_LABELS[category]
    reasons = {
        "A": "Evidence maturity A can be used as a mature comparison reference in this diagnostic layer.",
        "B": "Evidence maturity B supports use as a strong engineering analogue, not a final recommendation.",
        "C": "Evidence maturity C requires caveats and additional validation before decision use.",
        "D": "Evidence maturity D is emerging and needs validation before engineering decision use.",
        "E": "Evidence maturity E is exploratory and should remain concept-only.",
        "F": "Evidence maturity F is research-mode only.",
    }
    return {
        "evidence_maturity": maturity,
        "base_readiness_category": category,
        "base_readiness_label": label,
        "base_readiness_reason": reasons.get(maturity, "Evidence maturity is missing or unknown."),
    }


def _constraint(
    candidate: Mapping[str, Any],
    *,
    constraint_id: str,
    category: str,
    severity: str,
    reason: str,
    source_field: str,
) -> dict[str, Any]:
    return {
        "constraint_id": f"{_candidate_id(candidate)}::{constraint_id}",
        "category": category,
        "severity": severity,
        "reason": reason,
        "source_field": source_field,
    }


def _dedupe_constraints(constraints: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    index_by_key: dict[tuple[str, str], int] = {}
    for item in constraints:
        record = dict(item)
        key = (_text(record.get("constraint_id")), _text(record.get("category")))
        if key not in index_by_key:
            index_by_key[key] = len(output)
            output.append(record)
            continue
        existing = output[index_by_key[key]]
        if _SEVERITY_RANK.get(_text(record.get("severity")), 0) > _SEVERITY_RANK.get(
            _text(existing.get("severity")), 0
        ):
            output[index_by_key[key]] = record
    return output


def derive_candidate_readiness_constraints(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    constraints: list[dict[str, Any]] = []
    maturity = _evidence_maturity(candidate)
    candidate_class = _candidate_class(candidate)
    architecture = _architecture(candidate)
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))

    if maturity in {"E"}:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="evidence_maturity_e",
                category="evidence",
                severity="high",
                reason="Evidence maturity E keeps this candidate exploratory.",
                source_field="evidence_maturity",
            )
        )
    elif maturity == "F":
        constraints.append(
            _constraint(
                candidate,
                constraint_id="evidence_maturity_f",
                category="research_mode",
                severity="blocking",
                reason="Evidence maturity F is research-mode only.",
                source_field="evidence_maturity",
            )
        )
    elif maturity in {"D"}:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="evidence_maturity_d",
                category="evidence",
                severity="medium",
                reason="Evidence maturity D requires validation before engineering decision use.",
                source_field="evidence_maturity",
            )
        )
    elif maturity in {"", "UNKNOWN"} or maturity == "unknown":
        constraints.append(
            _constraint(
                candidate,
                constraint_id="unknown_evidence_maturity",
                category="maturity",
                severity="blocking",
                reason="Evidence maturity is missing or unknown.",
                source_field="evidence_maturity",
            )
        )

    if candidate.get("generated_candidate_flag") is True:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="generated_candidate",
                category="research_mode",
                severity="blocking",
                reason="Generated candidates are not engineering recommendations without validation.",
                source_field="generated_candidate_flag",
            )
        )
    if candidate.get("research_mode_flag") is True:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="research_mode_candidate",
                category="research_mode",
                severity="blocking",
                reason="Research-mode candidates are research-only unless separately validated.",
                source_field="research_mode_flag",
            )
        )

    qualification_burden = _text(qualification.get("qualification_burden"), "unknown")
    if qualification_burden in {"high", "very_high"}:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="qualification_burden",
                category="certification",
                severity="high",
                reason=f"Qualification burden is {qualification_burden}.",
                source_field="qualification_route.qualification_burden",
            )
        )

    inspection_burden = _text(inspection.get("inspection_burden"), "unknown")
    if inspection_burden == "high":
        constraints.append(
            _constraint(
                candidate,
                constraint_id="inspection_burden",
                category="inspection",
                severity="high" if candidate_class == "spatially_graded_am" else "medium",
                reason="High inspection burden is visible.",
                source_field="inspection_plan.inspection_burden",
            )
        )

    repairability_level = _text(repairability.get("repairability_level"), "unknown")
    if repairability_level in {"limited", "poor"}:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="repairability",
                category="repairability",
                severity="high" if repairability_level == "poor" else "medium",
                reason=f"Repairability is {repairability_level}.",
                source_field="repairability.repairability_level",
            )
        )

    route_id = _text(candidate.get("process_route_template_id"), "unknown_route")
    if route_id == "unknown_route" or not candidate.get("process_route_details"):
        constraints.append(
            _constraint(
                candidate,
                constraint_id="unknown_process_route",
                category="process_route",
                severity="blocking",
                reason="Process route is unknown or missing.",
                source_field="process_route_details",
            )
        )

    validation_gaps = [_text(item) for item in _as_list(candidate.get("route_validation_gaps")) if _text(item)]
    if validation_gaps:
        constraints.append(
            _constraint(
                candidate,
                constraint_id="route_validation_gaps",
                category="validation_gap",
                severity="high" if len(validation_gaps) >= 3 else "medium",
                reason="Route validation gaps remain visible: " + "; ".join(validation_gaps[:3]),
                source_field="route_validation_gaps",
            )
        )

    for interface in _as_list(candidate.get("interfaces")):
        interface_map = _mapping(interface)
        if _text(interface_map.get("risk_level")).lower() == "high":
            constraints.append(
                _constraint(
                    candidate,
                    constraint_id=f"interface_{_text(interface_map.get('interface_type'), 'unknown')}",
                    category="interface",
                    severity="high",
                    reason="High interface risk is visible.",
                    source_field="interfaces",
                )
            )

    for field, category in (("certification_risk_flags", "certification"), ("uncertainty_flags", "uncertainty")):
        for flag in _as_list(candidate.get(field)):
            text = _text(flag)
            if text:
                constraints.append(
                    _constraint(
                        candidate,
                        constraint_id=f"{field}_{len(constraints)}",
                        category=category,
                        severity="high" if "high" in text.lower() else "medium",
                        reason=text,
                        source_field=field,
                    )
                )

    if candidate_class == "spatially_graded_am" or architecture == "spatial_gradient":
        if maturity in _LOW_MATURITY:
            constraints.append(
                _constraint(
                    candidate,
                    constraint_id="low_maturity_spatial_gradient",
                    category="maturity",
                    severity="high" if maturity in {"D", "E"} else "blocking",
                    reason="D/E/F spatial-gradient candidates remain emerging, exploratory or research-only.",
                    source_field="candidate_class",
                )
            )

    return _dedupe_constraints(constraints)


def _status_for_category(category: str) -> str:
    if category in {"mature_reference", "strong_engineering_analogue"}:
        return "usable_as_reference"
    if category == "caveated_engineering_option":
        return "usable_with_caveats"
    if category in {"emerging_validation_needed", "exploratory_concept_only"}:
        return "exploratory_only"
    if category == "research_mode_only":
        return "research_only"
    if category == "not_decision_ready":
        return "not_ready"
    return "unknown"


def _readiness_confidence(maturity: str, constraints: Sequence[Mapping[str, Any]]) -> str:
    if maturity in {"A", "B", "C"} and not any(item.get("severity") == "blocking" for item in constraints):
        return "high"
    if maturity in {"D", "E", "F"}:
        return "medium"
    return "low"


def determine_decision_readiness(
    candidate: Mapping[str, Any],
    package_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    del package_context
    maturity = _evidence_maturity(candidate)
    base = classify_evidence_readiness(maturity)
    constraints = derive_candidate_readiness_constraints(candidate)
    category = base["base_readiness_category"]

    if any(item["category"] == "process_route" and item["severity"] == "blocking" for item in constraints):
        category = "not_decision_ready"
    elif any(item["category"] == "maturity" and item["severity"] == "blocking" for item in constraints):
        category = "unknown_readiness"
    elif any(item["category"] == "research_mode" and item["severity"] == "blocking" for item in constraints):
        category = "research_mode_only"

    if maturity == "D":
        category = "emerging_validation_needed"
    elif maturity == "E":
        category = "exploratory_concept_only"
    elif maturity == "F":
        category = "research_mode_only"

    status = _status_for_category(category)
    blocking = [dict(item) for item in constraints if item.get("severity") == "blocking"]
    caution = [dict(item) for item in constraints if item.get("severity") != "blocking"]
    required_next_evidence = []
    if any(item["category"] == "certification" for item in constraints):
        required_next_evidence.append("qualification and certification-route evidence")
    if any(item["category"] == "inspection" for item in constraints):
        required_next_evidence.append("inspection method and acceptance criteria")
    if any(item["category"] == "repairability" for item in constraints):
        required_next_evidence.append("repairability and disposition evidence")
    if any(item["category"] == "validation_gap" for item in constraints):
        required_next_evidence.append("route validation gap closure evidence")
    if any(item["category"] in {"evidence", "maturity", "research_mode"} for item in constraints):
        required_next_evidence.append("higher maturity evidence package")
    if not required_next_evidence:
        required_next_evidence.append("component-specific validation evidence before final recommendation")

    allowed_by_status = {
        "usable_as_reference": "Use as a comparison reference or engineering analogue with stated caveats.",
        "usable_with_caveats": "Use for early trade-space discussion with explicit caveats.",
        "exploratory_only": "Use only as an exploratory option requiring validation.",
        "research_only": "Use only as a research-mode concept, not an engineering recommendation.",
        "not_ready": "Use only to document gaps; not ready for decision support.",
        "unknown": "Use only after evidence and route visibility improve.",
    }
    disallowed_by_status = {
        "usable_as_reference": "Do not treat as final recommendation or certification approval.",
        "usable_with_caveats": "Do not treat as final recommendation, winner, or qualification approval.",
        "exploratory_only": "Do not use as a recommendation-ready engineering option.",
        "research_only": "Do not use as an engineering recommendation.",
        "not_ready": "Do not use for engineering down-select.",
        "unknown": "Do not use for down-select until readiness is clarified.",
    }
    notes = [
        base["base_readiness_reason"],
        "Decision readiness is not a final recommendation or certification approval.",
    ]
    if maturity in _LOW_MATURITY:
        notes.append("Low maturity D/E/F candidates remain exploratory or research-only.")

    return {
        "candidate_id": _candidate_id(candidate),
        "system_name": _system_name(candidate),
        "candidate_class": _candidate_class(candidate),
        "system_architecture_type": _architecture(candidate),
        "evidence_maturity": maturity,
        "readiness_category": category,
        "readiness_label": READINESS_LABELS[category],
        "readiness_status": status,
        "readiness_confidence": _readiness_confidence(maturity, constraints),
        "constraints": constraints,
        "blocking_constraints": blocking,
        "caution_constraints": caution,
        "allowed_use": allowed_by_status[status],
        "disallowed_use": disallowed_by_status[status],
        "required_next_evidence": list(dict.fromkeys(required_next_evidence)),
        "decision_notes": notes,
        "not_final_recommendation": True,
    }


def build_decision_readiness_summary(
    candidates: Sequence[Mapping[str, Any]],
    readiness_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    candidate_list = [candidate for candidate in candidates if isinstance(candidate, Mapping)]
    records = [record for record in readiness_records if isinstance(record, Mapping)]
    category_counts = Counter(_text(record.get("readiness_category"), "unknown_readiness") for record in records)
    status_counts = Counter(_text(record.get("readiness_status"), "unknown") for record in records)
    maturity_counts = Counter(_text(record.get("evidence_maturity"), "unknown") for record in records)
    by_category: dict[str, list[str]] = {}
    by_status: dict[str, list[str]] = {}
    constraint_categories = Counter(
        _text(constraint.get("category"))
        for record in records
        for constraint in _as_list(record.get("constraints"))
        if isinstance(constraint, Mapping)
    )
    for record in records:
        candidate_id = _text(record.get("candidate_id"))
        by_category.setdefault(_text(record.get("readiness_category"), "unknown_readiness"), []).append(candidate_id)
        by_status.setdefault(_text(record.get("readiness_status"), "unknown"), []).append(candidate_id)

    warnings = []
    if by_status.get("research_only"):
        warnings.append("One or more candidates are research-only.")
    if by_status.get("not_ready"):
        warnings.append("One or more candidates are not decision-ready.")
    return {
        "candidate_count": len(candidate_list),
        "readiness_category_counts": dict(sorted(category_counts.items())),
        "readiness_status_counts": dict(sorted(status_counts.items())),
        "evidence_maturity_counts": dict(sorted(maturity_counts.items())),
        "candidates_by_readiness_category": {key: sorted(value) for key, value in sorted(by_category.items())},
        "candidates_by_readiness_status": {key: sorted(value) for key, value in sorted(by_status.items())},
        "not_decision_ready_candidate_ids": sorted(by_status.get("not_ready", [])),
        "research_only_candidate_ids": sorted(by_status.get("research_only", [])),
        "exploratory_only_candidate_ids": sorted(by_status.get("exploratory_only", [])),
        "usable_as_reference_candidate_ids": sorted(by_status.get("usable_as_reference", [])),
        "usable_with_caveats_candidate_ids": sorted(by_status.get("usable_with_caveats", [])),
        "blocking_constraint_count": sum(
            1
            for record in records
            for constraint in _as_list(record.get("constraints"))
            if isinstance(constraint, Mapping) and constraint.get("severity") == "blocking"
        ),
        "high_constraint_count": sum(
            1
            for record in records
            for constraint in _as_list(record.get("constraints"))
            if isinstance(constraint, Mapping) and constraint.get("severity") == "high"
        ),
        "common_constraint_categories": dict(sorted(constraint_categories.items())),
        "warnings": warnings,
    }


def attach_decision_readiness(package: Mapping[str, Any]) -> dict[str, Any]:
    output = dict(package)
    candidates = [candidate for candidate in _as_list(package.get("candidate_systems")) if isinstance(candidate, Mapping)]
    enriched_candidates = []
    records = []
    for candidate in candidates:
        enriched = dict(candidate)
        readiness = determine_decision_readiness(enriched, package)
        enriched["decision_readiness"] = readiness
        enriched_candidates.append(enriched)
        records.append(readiness)
    summary = build_decision_readiness_summary(enriched_candidates, records)

    output["candidate_systems"] = enriched_candidates
    output["decision_readiness_summary"] = summary
    output["ranked_recommendations"] = _as_list(package.get("ranked_recommendations"))
    output["pareto_front"] = _as_list(package.get("pareto_front"))

    warnings = [_text(warning) for warning in _as_list(package.get("warnings")) if _text(warning)]
    for warning in summary["warnings"]:
        if warning not in warnings:
            warnings.append(warning)
    if any(candidate.get("generated_candidate_flag") is True or candidate.get("research_mode_flag") is True for candidate in enriched_candidates):
        warnings.append("Generated or research-mode candidates are present and must not be treated as recommendations.")
    if any(
        (_candidate_class(candidate) == "spatially_graded_am" or _architecture(candidate) == "spatial_gradient")
        and _evidence_maturity(candidate) in _LOW_MATURITY
        for candidate in enriched_candidates
    ):
        warnings.append("Spatial-gradient D/E/F candidates remain emerging, exploratory or research-only.")
    if any(
        _text(_mapping(candidate.get("qualification_route")).get("qualification_burden")) in {"high", "very_high"}
        for candidate in enriched_candidates
    ):
        warnings.append("High or very high qualification burden is visible in decision-readiness constraints.")
    output["warnings"] = list(dict.fromkeys(warnings))

    diagnostics = dict(_mapping(package.get("diagnostics")))
    diagnostics["decision_readiness_attached"] = True
    output["diagnostics"] = diagnostics
    return output
