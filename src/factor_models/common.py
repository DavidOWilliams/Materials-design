from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import EVIDENCE_MATURITY_LEVELS, FactorScore


_CONFIDENCE_BY_MATURITY = {
    "A": 0.90,
    "B": 0.78,
    "C": 0.62,
    "D": 0.45,
    "E": 0.32,
    "F": 0.18,
}

_PENALTY_BY_MATURITY = {
    "A": 0.0,
    "B": 3.0,
    "C": 8.0,
    "D": 16.0,
    "E": 24.0,
    "F": 34.0,
}


def clamp_score(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    """Clamp a proxy score to a 0-100 style range."""
    return round(max(lower, min(upper, float(value))), 2)


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _evidence_mapping(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    evidence = candidate.get("evidence_package") or candidate.get("evidence") or {}
    return evidence if isinstance(evidence, Mapping) else {}


def evidence_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _evidence_mapping(candidate)
    for value in (
        evidence.get("maturity"),
        evidence.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        maturity = _text(value).upper()
        if maturity in EVIDENCE_MATURITY_LEVELS:
            return maturity
    return "E"


def maturity_confidence(candidate: Mapping[str, Any]) -> float:
    """Return conservative confidence from A-F evidence maturity."""
    return _CONFIDENCE_BY_MATURITY.get(evidence_maturity(candidate), 0.25)


def evidence_maturity_penalty(candidate: Mapping[str, Any]) -> float:
    """Return a score penalty for immature evidence."""
    return _PENALTY_BY_MATURITY.get(evidence_maturity(candidate), 24.0)


def collect_text(candidate: Mapping[str, Any]) -> str:
    """Collect searchable text from a MaterialSystemCandidate-like mapping."""
    keys = (
        "candidate_id",
        "name",
        "system_name",
        "summary",
        "base_material_family",
        "material_family",
        "system_architecture_type",
        "candidate_class",
        "system_class",
        "constituents",
        "coating_or_surface_system",
        "coating_system",
        "environmental_barrier_coating",
        "gradient_architecture",
        "processing_routes",
        "process_route",
        "risks",
        "uncertainty_flags",
        "certification_risk_flags",
        "assembly_warnings",
        "provenance",
    )
    evidence = _evidence_mapping(candidate)
    values = [candidate.get(key) for key in keys]
    values.extend(evidence.get(key) for key in ("summary", "sources", "validation_gaps", "assumptions"))
    return " ".join(_text(value).lower() for value in values if value is not None)


def factor_requested(factor: str, active_factors: Sequence[str] | None) -> bool:
    if active_factors is None:
        return True
    requested = {str(item) for item in active_factors}
    namespace = factor.split(".", 1)[0]
    return factor in requested or namespace in requested


def low_evidence_warnings(candidate: Mapping[str, Any]) -> list[str]:
    maturity = evidence_maturity(candidate)
    if maturity in {"D", "E", "F"}:
        return [
            f"Evidence maturity {maturity} limits confidence; this proxy must not be treated as qualified performance."
        ]
    return []


def missing_detail_warning(candidate: Mapping[str, Any], detail: str, warning: str) -> list[str]:
    text = collect_text(candidate)
    return [] if detail.lower() in text else [warning]


def score_from_signals(
    base: float,
    candidate: Mapping[str, Any],
    positive_signals: Sequence[str] = (),
    negative_signals: Sequence[str] = (),
    missing_detail_penalty: float = 0.0,
) -> float:
    text = collect_text(candidate)
    score = base
    score += 5.0 * sum(1 for signal in positive_signals if signal.lower() in text)
    score -= 7.0 * sum(1 for signal in negative_signals if signal.lower() in text)
    if missing_detail_penalty and not positive_signals:
        score -= missing_detail_penalty
    return clamp_score(score - evidence_maturity_penalty(candidate))


def make_factor_score(
    *,
    factor: str,
    candidate: Mapping[str, Any],
    score: float,
    method: str,
    components: Mapping[str, Any] | None = None,
    reason: str,
    evidence_refs: Sequence[str] | None = None,
    assumptions: Sequence[str] | None = None,
    warnings: Sequence[str] | None = None,
) -> FactorScore:
    """Create a transparent FactorScore-compatible Build 4 proxy record."""
    candidate_class = _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")
    evidence = _evidence_mapping(candidate)
    refs = list(evidence_refs or [])
    if not refs:
        refs = [_text(item) for item in _as_list(evidence.get("sources")) if _text(item)]

    merged_warnings = list(warnings or [])
    for warning in low_evidence_warnings(candidate):
        if warning not in merged_warnings:
            merged_warnings.append(warning)

    confidence = maturity_confidence(candidate)
    if merged_warnings:
        confidence = max(0.05, confidence - 0.08)

    return {
        "factor": factor,
        "factor_name": factor,
        "candidate_class": candidate_class,
        "score": clamp_score(score),
        "confidence": round(confidence, 2),
        "method": method,
        "components": dict(components or {}),
        "reason": reason,
        "evidence_refs": refs,
        "assumptions": list(assumptions or []),
        "warnings": merged_warnings,
        "evidence": dict(evidence),
    }
