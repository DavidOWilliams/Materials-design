from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import EVIDENCE_MATURITY_LEVELS


_LOW_MATURITY = {"D", "E", "F"}
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


def _severity_from_score(score: Any) -> str:
    try:
        value = float(score)
    except (TypeError, ValueError):
        return "unknown"
    if value < 35.0:
        return "high"
    if value < 50.0:
        return "medium"
    if value < 65.0:
        return "low"
    return ""


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
    reason: str,
    related_warnings: Sequence[Any] | None = None,
) -> dict[str, Any]:
    return {
        "factor": factor,
        "namespace": namespace,
        "severity": severity or "unknown",
        "reason": reason,
        "evidence_maturity": _evidence_maturity(candidate),
        "candidate_id": _candidate_id(candidate),
        "candidate_class": _candidate_class(candidate),
        "related_warnings": [_text(item) for item in _as_list(related_warnings) if _text(item)],
    }


def _dedupe(records: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for record in records:
        key = (
            _text(record.get("candidate_id")),
            _text(record.get("factor")),
            _text(record.get("reason")),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(dict(record))
    return output


def _factor_score_limits(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for score in _as_list(candidate.get("factor_scores")):
        score_map = _mapping(score)
        if not score_map:
            continue
        factor = _text(score_map.get("factor") or score_map.get("factor_name"), "unknown_factor")
        severity = _severity_from_score(score_map.get("score"))
        warnings = [_text(item) for item in _as_list(score_map.get("warnings")) if _text(item)]
        if severity:
            records.append(
                _record(
                    candidate=candidate,
                    factor=factor,
                    namespace=_namespace(factor),
                    severity=severity,
                    reason=f"Factor score {score_map.get('score')} is low enough to limit confidence.",
                    related_warnings=warnings,
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
                        reason=warning,
                        related_warnings=[warning],
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
                    reason=text,
                    related_warnings=[text],
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
                reason=_text(
                    interface_map.get("reason"),
                    f"{interface_type} requires interface compatibility review.",
                ),
                related_warnings=interface_map.get("risk_flags"),
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
                reason=f"Evidence maturity {_evidence_maturity(candidate)} prevents recommendation-ready treatment.",
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
                reason="CMC hot-section use visibly depends on EBC, oxidation or recession assumptions.",
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
                    reason="Coating life, spallation or inspection burden is visible in the system record.",
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
                    reason=reason,
                )
            )

    if candidate_class == "monolithic_ceramic":
        records.append(
            _record(
                candidate=candidate,
                factor="ceramic.brittleness_proof_testing",
                namespace="ceramic",
                severity="medium",
                reason="Monolithic ceramics require brittleness, thermal-shock and proof-testing limitations to remain visible.",
            )
        )

    if candidate_class == "metallic" and any(token in text for token in ("tbc", "thermal barrier", "bond coat")):
        records.append(
            _record(
                candidate=candidate,
                factor="metallic_tbc.coating_life_density_thermal_margin",
                namespace="metallic_tbc",
                severity="medium",
                reason="Metallic + TBC comparison carries coating-life, density and thermal-margin limitations.",
            )
        )

    if not _as_list(candidate.get("processing_routes")) and not candidate.get("process_route"):
        records.append(
            _record(
                candidate=candidate,
                factor="process.missing_route_detail",
                namespace="process",
                severity="unknown",
                reason="Process route detail is missing or not visible.",
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
    return _dedupe(records)


def summarize_limiting_factors(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize limiting factors over a candidate sequence without filtering."""
    candidate_records = {
        _candidate_id(candidate): identify_limiting_factors(candidate)
        for candidate in candidates
    }
    all_records = [record for records in candidate_records.values() for record in records]
    severity_counts = Counter(_text(record.get("severity"), "unknown") for record in all_records)
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
        "severity_counts": dict(sorted(severity_counts.items())),
        "namespace_counts": dict(sorted(namespace_counts.items())),
        "candidate_limiting_factor_counts": {
            candidate_id: len(records)
            for candidate_id, records in sorted(candidate_records.items())
        },
        "high_severity_candidate_ids": high_ids,
        "warnings": warnings,
    }
