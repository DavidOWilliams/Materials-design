from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.candidate_normalizer import normalize_system_candidate
from src.contracts import (
    EVIDENCE_MATURITY_LEVELS,
    evidence_maturity_label,
    evidence_maturity_treatment,
)
from src.material_system_schema import MaterialSystemCandidate


_CONFIDENCE_BY_MATURITY = {
    "A": 0.90,
    "B": 0.78,
    "C": 0.62,
    "D": 0.45,
    "E": 0.32,
    "F": 0.18,
}


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _valid_maturity(value: Any) -> str:
    text = _text(value).upper()
    return text if text in EVIDENCE_MATURITY_LEVELS else ""


def _evidence_mapping(candidate: Mapping[str, Any]) -> Mapping[str, Any]:
    evidence = candidate.get("evidence_package") or candidate.get("evidence") or {}
    return evidence if isinstance(evidence, Mapping) else {}


def _explicit_valid_maturity(candidate: Mapping[str, Any]) -> str:
    evidence = _evidence_mapping(candidate)
    for value in (
        evidence.get("maturity"),
        evidence.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        maturity = _valid_maturity(value)
        if maturity:
            return maturity
    return ""


def _source_text(candidate: Mapping[str, Any]) -> str:
    evidence = _evidence_mapping(candidate)
    values = [
        candidate.get("source_type"),
        candidate.get("source_label"),
        candidate.get("candidate_source"),
        candidate.get("generated_by_adapter"),
        evidence.get("source_type"),
        evidence.get("candidate_source"),
        evidence.get("source_reference"),
    ]
    return " ".join(_text(value).lower() for value in values if _text(value))


def _has_named_analogue_evidence(candidate: Mapping[str, Any]) -> bool:
    evidence = _evidence_mapping(candidate)
    for key in (
        "recipe_mode",
        "matched_alloy_name",
        "source_alloy_name",
        "named_analogue",
    ):
        if _text(candidate.get(key)) or _text(evidence.get(key)):
            return True
    analogues = evidence.get("engineering_analogues")
    return bool(analogues)


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def maturity_from_source(candidate: Mapping[str, Any]) -> str:
    """Infer a conservative A-F evidence maturity from source metadata."""
    source = _source_text(candidate)

    if (
        _as_bool(candidate.get("generated_candidate_flag"))
        or _as_bool(candidate.get("research_mode_flag"))
        or "generated" in source
        or "research" in source
    ):
        return "F"
    if any(token in source for token in ("materials_project", "database", "computational", "exploratory")):
        return "E"
    if any(token in source for token in ("literature", "laboratory")):
        return "D"
    if "engineering_analogue" in source and _has_named_analogue_evidence(candidate):
        return "B"
    if "build31_metallic_baseline" in source:
        if "materials_project" in source:
            return "E"
        return "C"
    if "curated_engineering_reference" in source:
        return "C"
    if "engineering_analogue" in source:
        return "C"
    return "E"


def _apply_graded_am_cap(
    candidate: Mapping[str, Any],
    maturity: str,
    explicit_maturity: str,
) -> str:
    if _candidate_class(candidate) != "spatially_graded_am":
        return maturity
    if explicit_maturity in {"A", "B", "C"}:
        return explicit_maturity
    if maturity in {"A", "B", "C"}:
        return "D"
    return maturity


def _evidence_summary(candidate: Mapping[str, Any], maturity: str) -> str:
    system_name = _text(candidate.get("system_name") or candidate.get("name"), "Candidate")
    source = _text(candidate.get("source_type") or candidate.get("source_label"), "unknown source")
    return f"{system_name} is treated as evidence maturity {maturity} from {source}."


def _append_unique(values: list[Any], value: str) -> None:
    if value not in values:
        values.append(value)


def evaluate_candidate_evidence(candidate: Mapping[str, Any]) -> MaterialSystemCandidate:
    """Normalize and enrich one MaterialSystemCandidate-compatible record with evidence metadata."""
    explicit_maturity = _explicit_valid_maturity(candidate)
    normalized = normalize_system_candidate(candidate)
    inferred_maturity = maturity_from_source(candidate)
    maturity = explicit_maturity or inferred_maturity
    maturity = _apply_graded_am_cap(normalized, maturity, explicit_maturity)

    evidence_package = dict(normalized.get("evidence_package") or {})
    evidence_package["maturity"] = maturity
    evidence_package["evidence_maturity"] = maturity
    evidence_package["maturity_label"] = evidence_maturity_label(maturity)
    evidence_package["recommendation_treatment"] = evidence_maturity_treatment(maturity)
    evidence_package.setdefault("summary", _evidence_summary(normalized, maturity))
    evidence_package["confidence"] = _CONFIDENCE_BY_MATURITY[maturity]

    for key in (
        "sources",
        "validation_gaps",
        "known_strengths",
        "known_watch_outs",
        "source_reference",
        "provenance",
    ):
        if key in candidate and key not in evidence_package:
            evidence_package[key] = candidate[key]

    evidence_package["sources"] = _as_list(evidence_package.get("sources"))
    source_reference = _text(evidence_package.get("source_reference"))
    source_type = _text(normalized.get("source_type") or normalized.get("source_label"))
    if source_reference:
        _append_unique(evidence_package["sources"], source_reference)
    elif source_type:
        _append_unique(evidence_package["sources"], source_type)

    evidence_package["validation_gaps"] = _as_list(evidence_package.get("validation_gaps"))

    normalized["evidence_package"] = evidence_package
    normalized["evidence"] = evidence_package
    normalized["evidence_maturity"] = maturity
    normalized["maturity_rationale"] = evidence_package["maturity_label"]

    normalized["certification_risk_flags"] = _as_list(normalized.get("certification_risk_flags"))
    normalized["uncertainty_flags"] = _as_list(normalized.get("uncertainty_flags"))

    if maturity in {"D", "E", "F"}:
        _append_unique(
            normalized["certification_risk_flags"],
            f"Evidence maturity {maturity} is not qualification-ready; do not treat as certification approval.",
        )

    if _candidate_class(normalized) == "spatially_graded_am" and maturity in {"D", "E", "F"}:
        _append_unique(
            normalized["certification_risk_flags"],
            "Graded AM template requires process-specific qualification evidence before certification use.",
        )

    if maturity == "E":
        _append_unique(
            normalized["uncertainty_flags"],
            "Evidence maturity E indicates database, computational or exploratory evidence only.",
        )
    if maturity == "F":
        _append_unique(
            normalized["uncertainty_flags"],
            "Evidence maturity F indicates generated or unvalidated research suggestion status.",
        )

    if _as_bool(candidate.get("generated_candidate_flag")):
        normalized["generated_candidate_flag"] = True
    if _as_bool(candidate.get("research_mode_flag")):
        normalized["research_mode_flag"] = True

    return normalized


def evaluate_candidates_evidence(
    candidates: Sequence[Mapping[str, Any]],
) -> list[MaterialSystemCandidate]:
    return [evaluate_candidate_evidence(candidate) for candidate in candidates]


def summarize_evidence_maturity(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    evaluated = evaluate_candidates_evidence(candidates)
    maturity_counts = Counter({level: 0 for level in EVIDENCE_MATURITY_LEVELS})
    maturity_counts.update(candidate.get("evidence_maturity", "E") for candidate in evaluated)

    return {
        "total_candidate_count": len(evaluated),
        "maturity_counts": {level: maturity_counts[level] for level in EVIDENCE_MATURITY_LEVELS},
        "generated_candidate_count": sum(
            1 for candidate in evaluated if candidate.get("generated_candidate_flag") is True
        ),
        "research_mode_candidate_count": sum(
            1 for candidate in evaluated if candidate.get("research_mode_flag") is True
        ),
        "candidate_class_counts": dict(
            sorted(Counter(candidate.get("candidate_class", "unknown") for candidate in evaluated).items())
        ),
    }
