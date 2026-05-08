from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import EVIDENCE_MATURITY_LEVELS


_LOW_MATURITY = {"D", "E", "F"}
_SEVERITY_RANK = {"unknown": 0, "low": 1, "medium": 2, "high": 3}
_RISK_TERMS = (
    "risk",
    "spallation",
    "mismatch",
    "delamination",
    "crack",
    "oxidation",
    "corrosion",
    "steam",
    "recession",
    "brittle",
    "flaw",
    "proof",
    "inspection",
    "repair",
    "qualification",
    "certification",
    "exploratory",
    "transition",
    "process window",
    "repeatability",
)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
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


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _namespace(factor: str) -> str:
    return factor.split(".", 1)[0] if "." in factor else factor or "unknown"


def _evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _mapping(candidate.get("evidence_package") or candidate.get("evidence"))
    for value in (
        evidence.get("maturity"),
        evidence.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        maturity = _text(value).upper()
        if maturity in EVIDENCE_MATURITY_LEVELS:
            return maturity
    return "unknown"


def normalise_factor_score(raw_score: Any) -> float | None:
    """Normalize factor scores expressed on either 0-1 or 0-100 scales."""
    try:
        value = float(raw_score)
    except (TypeError, ValueError):
        return None
    if value <= 1.0:
        return round(value * 100.0, 6)
    if value <= 100.0:
        return round(value, 6)
    return None


def classify_factor_score(raw_score: Any) -> dict[str, Any]:
    """Classify a score where higher is better and lower means more concern."""
    normalised_score = normalise_factor_score(raw_score)
    if normalised_score is None:
        return {
            "raw_score": raw_score,
            "normalised_score": None,
            "severity": "unknown",
            "category": "advisory_warning",
            "is_limiting": False,
        }
    if normalised_score < 35.0:
        severity = "high"
    elif normalised_score < 55.0:
        severity = "medium"
    elif normalised_score < 70.0:
        severity = "low"
    else:
        severity = ""
    return {
        "raw_score": raw_score,
        "normalised_score": normalised_score,
        "severity": severity,
        "category": "hard_limit" if severity else "",
        "is_limiting": bool(severity),
    }


def _severity_from_text(text: str, default: str = "medium") -> str:
    lowered = text.lower()
    if any(term in lowered for term in ("high", "critical", "not qualification-ready", "exploratory", "e/f")):
        return "high"
    if any(term in lowered for term in ("unknown", "missing", "not visible")):
        return "unknown"
    return default


def _record(
    *,
    candidate: Mapping[str, Any],
    factor: str,
    namespace: str,
    severity: str,
    category: str,
    reason: str,
    related_warnings: Sequence[Any] | None = None,
    normalised_score: float | None = None,
    source_field: str = "",
    dedupe_key: str | None = None,
) -> dict[str, Any]:
    candidate_id = _candidate_id(candidate)
    category_text = _text(category, "advisory_warning")
    factor_text = _text(factor, "unknown_factor")
    severity_text = severity or "unknown"
    return {
        "factor": factor_text,
        "namespace": namespace,
        "severity": severity_text,
        "category": category_text,
        "reason": reason,
        "normalised_score": normalised_score,
        "source_field": source_field,
        "evidence_maturity": _evidence_maturity(candidate),
        "candidate_id": candidate_id,
        "candidate_class": _candidate_class(candidate),
        "related_warnings": [_text(item) for item in _as_list(related_warnings) if _text(item)],
        "dedupe_key": dedupe_key
        or f"{candidate_id}|{namespace}|{factor_text}|{category_text}|{severity_text}",
    }


def dedupe_limiting_factors(factors: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """De-duplicate factor records while keeping the most severe deterministic representative."""
    output: list[dict[str, Any]] = []
    key_to_index: dict[str, int] = {}
    for record in factors:
        item = dict(record)
        key = _text(
            item.get("dedupe_key"),
            "|".join(
                [
                    _text(item.get("candidate_id")),
                    _text(item.get("namespace")),
                    _text(item.get("factor")),
                    _text(item.get("category")),
                    _text(item.get("severity")),
                ]
            ),
        )
        item["dedupe_key"] = key
        if key not in key_to_index:
            key_to_index[key] = len(output)
            output.append(item)
            continue

        existing = output[key_to_index[key]]
        existing_rank = _SEVERITY_RANK.get(_text(existing.get("severity")), 0)
        item_rank = _SEVERITY_RANK.get(_text(item.get("severity")), 0)
        keep = item if item_rank > existing_rank else existing
        merged_warnings = list(
            dict.fromkeys(
                [
                    _text(warning)
                    for warning in _as_list(existing.get("related_warnings"))
                    + _as_list(item.get("related_warnings"))
                    if _text(warning)
                ]
            )
        )
        keep["related_warnings"] = merged_warnings
        output[key_to_index[key]] = keep
    return output


def _factor_score_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for score in _as_list(candidate.get("factor_scores")):
        score_map = _mapping(score)
        if not score_map:
            continue
        factor = _text(score_map.get("factor") or score_map.get("factor_name"), "unknown_factor")
        classification = classify_factor_score(score_map.get("score"))
        severity = _text(classification.get("severity"))
        warnings = [_text(item) for item in _as_list(score_map.get("warnings")) if _text(item)]
        normalised_score = classification.get("normalised_score")
        if classification.get("is_limiting"):
            records.append(
                _record(
                    candidate=candidate,
                    factor=factor,
                    namespace=_namespace(factor),
                    severity=severity,
                    category="hard_limit",
                    reason=f"Normalised factor score {normalised_score:.1f} is below the calibrated confidence threshold.",
                    related_warnings=warnings,
                    normalised_score=normalised_score,
                    source_field="factor_scores.score",
                    dedupe_key=f"{_candidate_id(candidate)}|score|{factor}|hard_limit",
                )
            )
        for warning in warnings:
            if any(term in warning.lower() for term in _RISK_TERMS):
                records.append(
                    _record(
                        candidate=candidate,
                        factor=f"{factor}.warning",
                        namespace=_namespace(factor),
                        severity=_severity_from_text(warning),
                        category="advisory_warning",
                        reason=warning,
                        related_warnings=[warning],
                        source_field="factor_scores.warnings",
                        dedupe_key=f"{_candidate_id(candidate)}|warning|{factor}|{warning.lower()}",
                    )
                )
    return records


def _flag_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for field, namespace in (
        ("certification_risk_flags", "certification"),
        ("uncertainty_flags", "uncertainty"),
    ):
        for flag in _as_list(candidate.get(field)):
            text = _text(flag)
            if not text:
                continue
            records.append(
                _record(
                    candidate=candidate,
                    factor=f"{namespace}.{field}",
                    namespace=namespace,
                    severity=_severity_from_text(text),
                    category="certification" if namespace == "certification" else "uncertainty",
                    reason=text,
                    related_warnings=[text],
                    source_field=field,
                    dedupe_key=f"{_candidate_id(candidate)}|{namespace}|{field}|{text.lower()}",
                )
            )
    return records


def _interface_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for interface in _as_list(candidate.get("interfaces")):
        interface_map = _mapping(interface)
        if not interface_map:
            continue
        interface_type = _text(interface_map.get("interface_type"), "unknown_interface")
        risk_level = _text(interface_map.get("risk_level"), "unknown").lower()
        severity = risk_level if risk_level in {"low", "medium", "high", "unknown"} else "unknown"
        records.append(
            _record(
                candidate=candidate,
                factor=f"interface.{interface_type}",
                namespace="interface",
                severity=severity,
                category="interface_risk",
                reason=_text(
                    interface_map.get("reason"),
                    f"{interface_type} requires interface compatibility review.",
                ),
                related_warnings=interface_map.get("risk_flags"),
                source_field="interfaces",
                dedupe_key=f"{_candidate_id(candidate)}|interface|{interface_type}",
            )
        )
    return records


def _class_specific_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidate_class = _candidate_class(candidate)
    architecture = _architecture(candidate)
    text = _blob(candidate)
    records: list[dict[str, Any]] = []

    if _evidence_maturity(candidate) in _LOW_MATURITY:
        records.append(
            _record(
                candidate=candidate,
                factor="evidence.low_maturity",
                namespace="evidence",
                severity="high" if _evidence_maturity(candidate) in {"E", "F"} else "medium",
                category="evidence_maturity",
                reason=f"Evidence maturity {_evidence_maturity(candidate)} prevents recommendation-ready treatment.",
                source_field="evidence_maturity",
                dedupe_key=f"{_candidate_id(candidate)}|evidence|low_maturity",
            )
        )

    if candidate_class == "ceramic_matrix_composite" and any(
        token in text for token in ("ebc", "environmental barrier", "steam", "oxidation", "recession")
    ):
        records.append(
            _record(
                candidate=candidate,
                factor="cmc.ebc_dependency",
                namespace="cmc",
                severity="medium",
                category="route_risk",
                reason="CMC hot-section use visibly depends on EBC, oxidation or recession assumptions.",
                source_field="candidate_class",
            )
        )

    if candidate_class == "coating_enabled" or architecture == "substrate_plus_coating":
        if any(token in text for token in ("spallation", "mismatch", "cte", "inspection", "repair", "bond coat")):
            records.append(
                _record(
                    candidate=candidate,
                    factor="coating.life_interface_inspection",
                    namespace="coating",
                    severity="medium",
                    category="route_risk",
                    reason="Coating life, spallation or inspection burden is visible in the system record.",
                    source_field="coating_or_surface_system",
                )
            )

    if candidate_class == "spatially_graded_am" or architecture == "spatial_gradient":
        for factor, reason in (
            ("graded_am.transition_zone_risk", "Spatial gradient transition-zone risk requires explicit review."),
            ("graded_am.process_window_sensitivity", "Graded AM process-window sensitivity remains unresolved."),
            ("graded_am.inspectability_repairability", "Through-depth inspectability and repairability remain visible limits."),
        ):
            records.append(
                _record(
                    candidate=candidate,
                    factor=factor,
                    namespace="graded_am",
                    severity="high" if _evidence_maturity(candidate) in {"E", "F"} else "medium",
                    category="route_risk",
                    reason=reason,
                    source_field="gradient_architecture",
                )
            )

    if candidate_class == "monolithic_ceramic":
        records.append(
            _record(
                candidate=candidate,
                factor="ceramic.brittleness_proof_testing",
                namespace="ceramic",
                severity="medium",
                category="hard_limit",
                reason="Monolithic ceramics require brittleness, thermal-shock and proof-testing limitations to remain visible.",
                source_field="candidate_class",
            )
        )

    if candidate_class == "metallic" and any(token in text for token in ("tbc", "thermal barrier", "bond coat")):
        records.append(
            _record(
                candidate=candidate,
                factor="metallic_tbc.coating_life_density_thermal_margin",
                namespace="metallic_tbc",
                severity="medium",
                category="route_risk",
                reason="Metallic + TBC comparison carries coating-life, density and thermal-margin limitations.",
                source_field="candidate_class",
            )
        )

    if not _as_list(candidate.get("processing_routes")) and not candidate.get("process_route"):
        records.append(
            _record(
                candidate=candidate,
                factor="process.missing_route_detail",
                namespace="process",
                severity="unknown",
                category="route_risk",
                reason="Process route detail is missing or not visible.",
                source_field="processing_routes",
            )
        )

    return records


def _process_route_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    inspection = _mapping(candidate.get("inspection_plan"))
    repairability = _mapping(candidate.get("repairability"))
    qualification = _mapping(candidate.get("qualification_route"))
    route_id = _text(candidate.get("process_route_template_id"), "unknown_route")

    inspection_burden = _text(inspection.get("inspection_burden"), "unknown")
    if inspection_burden == "high":
        records.append(
            _record(
                candidate=candidate,
                factor="inspection.high_route_inspection_burden",
                namespace="inspection",
                severity="high",
                category="route_risk",
                reason=f"Process route {route_id} has high inspection burden.",
                related_warnings=inspection.get("inspection_challenges"),
                source_field="inspection_plan.inspection_burden",
                dedupe_key=f"{_candidate_id(candidate)}|route|inspection_burden",
            )
        )
    elif inspection_burden == "unknown":
        records.append(
            _record(
                candidate=candidate,
                factor="inspection.unknown_route_inspection_burden",
                namespace="inspection",
                severity="unknown",
                category="route_risk",
                reason=f"Process route {route_id} has unknown inspection burden.",
                related_warnings=inspection.get("inspection_challenges"),
                source_field="inspection_plan.inspection_burden",
                dedupe_key=f"{_candidate_id(candidate)}|route|inspection_burden",
            )
        )

    repairability_level = _text(repairability.get("repairability_level"), "unknown")
    if repairability_level in {"limited", "poor"}:
        records.append(
            _record(
                candidate=candidate,
                factor="repairability.limited_or_poor_route_repairability",
                namespace="repairability",
                severity="high" if repairability_level == "poor" else "medium",
                category="route_risk",
                reason=f"Process route {route_id} has {repairability_level} repairability.",
                related_warnings=repairability.get("repair_constraints"),
                source_field="repairability.repairability_level",
                dedupe_key=f"{_candidate_id(candidate)}|route|repairability",
            )
        )

    qualification_burden = _text(qualification.get("qualification_burden"), "unknown")
    if qualification_burden in {"high", "very_high"}:
        records.append(
            _record(
                candidate=candidate,
                factor="certification.high_route_qualification_burden",
                namespace="certification",
                severity="high" if qualification_burden == "very_high" else "medium",
                category="certification",
                reason=f"Process route {route_id} has {qualification_burden} qualification burden.",
                related_warnings=qualification.get("qualification_notes"),
                source_field="qualification_route.qualification_burden",
                dedupe_key=f"{_candidate_id(candidate)}|route|qualification",
            )
        )

    for index, risk in enumerate(_as_list(candidate.get("route_risks"))[:3]):
        text = _text(risk)
        if text:
            records.append(
                _record(
                    candidate=candidate,
                    factor=f"process_route.route_risk_{index + 1}",
                    namespace="process_route",
                    severity=_severity_from_text(text, default="medium"),
                    category="route_risk",
                    reason=text,
                    related_warnings=[text],
                    source_field="route_risks",
                    dedupe_key=f"{_candidate_id(candidate)}|route_risk|{text.lower()}",
                )
            )

    for index, gap in enumerate(_as_list(candidate.get("route_validation_gaps"))[:3]):
        text = _text(gap)
        if text:
            records.append(
                _record(
                    candidate=candidate,
                    factor=f"process.route_validation_gap_{index + 1}",
                    namespace="process",
                    severity="medium",
                    category="route_risk",
                    reason=text,
                    related_warnings=[text],
                    source_field="route_validation_gaps",
                    dedupe_key=f"{_candidate_id(candidate)}|route_gap|{text.lower()}",
                )
            )
    return records


def _coating_spallation_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    profile = _mapping(candidate.get("coating_spallation_adhesion"))
    if not profile:
        return []
    records: list[dict[str, Any]] = []
    checks = (
        (
            "adhesion_or_spallation_risk",
            "coating.adhesion_spallation_risk",
            "High coating adhesion/spallation risk is visible.",
        ),
        ("cte_mismatch_risk", "coating.cte_mismatch_risk", "High coating CTE mismatch risk is visible."),
        (
            "thermal_cycling_damage_risk",
            "coating.thermal_cycling_damage_risk",
            "High coating thermal cycling damage risk is visible.",
        ),
        (
            "environmental_attack_risk",
            "coating.environmental_attack_risk",
            "High coating environmental attack risk is visible.",
        ),
        (
            "inspection_difficulty",
            "coating.inspection_difficulty",
            "High coating inspection difficulty is visible.",
        ),
        (
            "repairability_constraint",
            "coating.repairability_constraint",
            "High coating repairability constraint is visible.",
        ),
    )
    for field, factor, reason in checks:
        if _text(profile.get(field)) == "high":
            records.append(
                _record(
                    candidate=candidate,
                    factor=factor,
                    namespace="coating",
                    severity="high",
                    category="route_risk",
                    reason=reason,
                    related_warnings=profile.get("coating_concerns"),
                    source_field=f"coating_spallation_adhesion.{field}",
                    dedupe_key=f"{_candidate_id(candidate)}|coating_spallation|{field}",
                )
            )
    return records


def _graded_am_transition_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    profile = _mapping(candidate.get("graded_am_transition_zone_risk"))
    if not profile:
        return []
    records: list[dict[str, Any]] = []
    checks = (
        (
            "transition_zone_complexity",
            "graded_am.transition_zone_complexity",
            "High graded AM transition-zone complexity is visible.",
        ),
        (
            "residual_stress_risk",
            "graded_am.residual_stress_risk",
            "High graded AM residual-stress risk is visible.",
        ),
        (
            "cracking_or_delamination_risk",
            "graded_am.cracking_delamination_risk",
            "High graded AM cracking/delamination risk is visible.",
        ),
        (
            "process_window_sensitivity",
            "graded_am.process_window_sensitivity",
            "High graded AM process-window sensitivity is visible.",
        ),
        (
            "through_depth_inspection_difficulty",
            "graded_am.through_depth_inspection_difficulty",
            "High graded AM through-depth inspection difficulty is visible.",
        ),
        (
            "repairability_constraint",
            "graded_am.repairability_constraint",
            "High graded AM repairability constraint is visible.",
        ),
    )
    for field, factor, reason in checks:
        if _text(profile.get(field)) == "high":
            records.append(
                _record(
                    candidate=candidate,
                    factor=factor,
                    namespace="graded_am",
                    severity="high",
                    category="route_risk",
                    reason=reason,
                    related_warnings=profile.get("gradient_concerns"),
                    source_field=f"graded_am_transition_zone_risk.{field}",
                    dedupe_key=f"{_candidate_id(candidate)}|graded_am_transition|{field}",
                )
            )
    return records


def identify_limiting_factors(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Identify deterministic, transparent limiting factors for one existing candidate."""
    records: list[dict[str, Any]] = []
    records.extend(_factor_score_limits(candidate))
    records.extend(_flag_limits(candidate))
    records.extend(_interface_limits(candidate))
    records.extend(_class_specific_limits(candidate))
    records.extend(_process_route_limits(candidate))
    records.extend(_coating_spallation_limits(candidate))
    records.extend(_graded_am_transition_limits(candidate))
    return dedupe_limiting_factors(records)


def summarize_limiting_factors(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize limiting factors over a candidate sequence without filtering."""
    candidate_records = {
        _candidate_id(candidate): identify_limiting_factors(candidate)
        for candidate in candidates
    }
    all_records = [record for records in candidate_records.values() for record in records]
    severity_counts = Counter(_text(record.get("severity"), "unknown") for record in all_records)
    category_counts = Counter(_text(record.get("category"), "unknown") for record in all_records)
    namespace_counts = Counter(_text(record.get("namespace"), "unknown") for record in all_records)
    high_ids = sorted(
        candidate_id
        for candidate_id, records in candidate_records.items()
        if any(record.get("severity") == "high" for record in records)
    )
    warnings = []
    for candidate_id, records in candidate_records.items():
        if not records:
            warnings.append(f"{candidate_id}: no limiting factors identified by skeleton heuristics.")
    return {
        "candidate_count": len(candidates),
        "total_limiting_factor_count": len(all_records),
        "total_hard_limit_count": category_counts.get("hard_limit", 0),
        "total_advisory_warning_count": category_counts.get("advisory_warning", 0),
        "total_evidence_maturity_limit_count": category_counts.get("evidence_maturity", 0),
        "total_route_risk_count": category_counts.get("route_risk", 0) + category_counts.get("interface_risk", 0),
        "total_certification_limit_count": category_counts.get("certification", 0),
        "severity_counts": dict(sorted(severity_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "namespace_counts": dict(sorted(namespace_counts.items())),
        "candidate_limiting_factor_counts": {
            candidate_id: len(records)
            for candidate_id, records in sorted(candidate_records.items())
        },
        "high_severity_candidate_ids": high_ids,
        "warnings": warnings,
    }
