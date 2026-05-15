from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import evidence_maturity_label
from src.material_system_schema import MaterialSystemCandidate


_BULK_ARCHITECTURE_CLASSES = {"metallic", "monolithic_ceramic"}


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


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


def _has_coating_or_surface_system(candidate: Mapping[str, Any]) -> bool:
    return bool(candidate.get("coating_or_surface_system") or candidate.get("coating_system"))


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    system_classes = candidate.get("system_classes")
    first_system_class = system_classes[0] if isinstance(system_classes, list) and system_classes else ""
    return _text(candidate.get("candidate_class") or candidate.get("system_class") or first_system_class, "unknown")


def _architecture_default(candidate_class: str, candidate: Mapping[str, Any]) -> str:
    if candidate_class in _BULK_ARCHITECTURE_CLASSES:
        return "bulk_material"
    if candidate_class == "ceramic_matrix_composite":
        if _has_coating_or_surface_system(candidate):
            return "cmc_plus_ebc"
        return "composite_system"
    if candidate_class == "coating_enabled":
        return "coating_enabled"
    if candidate_class == "spatially_graded_am":
        return "spatially_graded_am_system"
    if candidate_class == "research_generated":
        return "research_generated_system"
    return "unknown"


def _fallback_candidate_id(candidate: Mapping[str, Any], candidate_class: str) -> str:
    seed = "|".join(
        [
            candidate_class,
            _text(candidate.get("system_name") or candidate.get("name"), "unnamed"),
            _text(candidate.get("source_type") or candidate.get("source_label"), "unknown_source"),
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:10]
    return f"normalized-{candidate_class}-{digest}"


def _source_text(candidate: Mapping[str, Any]) -> str:
    return " ".join(
        _text(candidate.get(key)).lower()
        for key in ("source_type", "source_label", "candidate_source", "generated_by_adapter")
    )


def _existing_maturity(candidate: Mapping[str, Any], evidence_package: Mapping[str, Any]) -> str:
    for value in (
        evidence_package.get("maturity"),
        evidence_package.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        text = _text(value).upper()
        if text in {"A", "B", "C", "D", "E", "F"}:
            return text
    return ""


def _default_maturity(candidate: Mapping[str, Any], evidence_package: Mapping[str, Any]) -> str:
    existing = _existing_maturity(candidate, evidence_package)
    if existing:
        return existing
    if _as_bool(candidate.get("generated_candidate_flag")) or _as_bool(candidate.get("research_mode_flag")):
        return "F"
    source = _source_text(candidate)
    if any(token in source for token in ("materials_project", "database", "exploratory")):
        return "E"
    if any(token in source for token in ("engineering_analogue", "curated", "reference")):
        return "C"
    return "E"


def _normalise_evidence_package(candidate: Mapping[str, Any]) -> dict[str, Any]:
    raw = candidate.get("evidence_package") or candidate.get("evidence") or {}
    evidence_package = dict(raw) if isinstance(raw, Mapping) else {}
    maturity = _default_maturity(candidate, evidence_package)
    evidence_package["maturity"] = maturity
    evidence_package.setdefault("evidence_maturity", maturity)
    evidence_package.setdefault("maturity_label", evidence_maturity_label(maturity))
    evidence_package.setdefault("sources", [])
    evidence_package["sources"] = _as_list(evidence_package.get("sources"))
    evidence_package.setdefault("validation_gaps", [])
    evidence_package["validation_gaps"] = _as_list(evidence_package.get("validation_gaps"))
    evidence_package.setdefault("assumptions", [])
    evidence_package["assumptions"] = _as_list(evidence_package.get("assumptions"))
    return evidence_package


def _normalise_factor_scores(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, Mapping):
        return [dict(value)]
    return [value]


def normalize_system_candidate(candidate: Mapping[str, Any]) -> MaterialSystemCandidate:
    """Return a consistently shaped MaterialSystemCandidate-compatible dictionary."""
    normalized: MaterialSystemCandidate = dict(candidate)
    candidate_class = _candidate_class(normalized)
    system_name = _text(normalized.get("system_name") or normalized.get("name"), "Unnamed material system")
    generated_candidate_flag = _as_bool(normalized.get("generated_candidate_flag"))
    research_mode_flag = _as_bool(normalized.get("research_mode_flag"))

    normalized["candidate_class"] = candidate_class
    normalized.setdefault("system_class", candidate_class)
    normalized.setdefault("system_classes", [candidate_class] if candidate_class != "unknown" else [])
    normalized["candidate_id"] = _text(normalized.get("candidate_id")) or _fallback_candidate_id(
        normalized,
        candidate_class,
    )
    normalized["system_name"] = system_name
    normalized.setdefault("name", system_name)
    normalized["system_architecture_type"] = _text(
        normalized.get("system_architecture_type"),
        _architecture_default(candidate_class, normalized),
    )

    for field in (
        "constituents",
        "interfaces",
        "uncertainty_flags",
        "certification_risk_flags",
        "optimisation_history",
    ):
        normalized[field] = _as_list(normalized.get(field))

    normalized["generated_candidate_flag"] = generated_candidate_flag
    normalized["research_mode_flag"] = research_mode_flag
    normalized["research_generated"] = _as_bool(normalized.get("research_generated"))
    normalized["factor_scores"] = _normalise_factor_scores(normalized.get("factor_scores"))

    evidence_package = _normalise_evidence_package(normalized)
    normalized["evidence_package"] = evidence_package
    normalized["evidence"] = evidence_package
    normalized["evidence_maturity"] = evidence_package["maturity"]
    normalized.setdefault("maturity_rationale", evidence_package.get("maturity_label", ""))

    if evidence_package["maturity"] in {"D", "E", "F"}:
        warning = (
            f"Evidence maturity {evidence_package['maturity']} is not qualification-ready; "
            "candidate requires validation before certification use."
        )
        if warning not in normalized["certification_risk_flags"]:
            normalized["certification_risk_flags"].append(warning)

    if candidate_class == "spatially_graded_am" and not normalized.get("gradient_architecture"):
        warning = "Spatially graded AM candidate is missing gradient_architecture details."
        if warning not in normalized["uncertainty_flags"]:
            normalized["uncertainty_flags"].append(warning)

    if candidate_class == "coating_enabled" and not _has_coating_or_surface_system(normalized):
        warning = "Coating-enabled candidate is missing coating_or_surface_system details."
        if warning not in normalized["uncertainty_flags"]:
            normalized["uncertainty_flags"].append(warning)

    validation_messages = validate_normalized_candidate(normalized)
    if validation_messages:
        normalized["normalization_warnings"] = _as_list(normalized.get("normalization_warnings"))
        for message in validation_messages:
            if message not in normalized["normalization_warnings"]:
                normalized["normalization_warnings"].append(message)

    return normalized


def normalize_system_candidates(
    candidates: Sequence[Mapping[str, Any]],
) -> list[MaterialSystemCandidate]:
    return [normalize_system_candidate(candidate) for candidate in candidates]


def validate_normalized_candidate(candidate: Mapping[str, Any]) -> list[str]:
    messages: list[str] = []
    if not _text(candidate.get("candidate_id")):
        messages.append("candidate_id is missing.")
    if not _text(candidate.get("candidate_class") or candidate.get("system_class")):
        messages.append("candidate_class is missing.")
    if not isinstance(candidate.get("constituents"), list):
        messages.append("constituents should be a list.")
    if not isinstance(candidate.get("interfaces"), list):
        messages.append("interfaces should be a list.")
    if not isinstance(candidate.get("uncertainty_flags"), list):
        messages.append("uncertainty_flags should be a list.")
    if not isinstance(candidate.get("certification_risk_flags"), list):
        messages.append("certification_risk_flags should be a list.")
    if not isinstance(candidate.get("optimisation_history"), list):
        messages.append("optimisation_history should be a list.")
    if not isinstance(candidate.get("generated_candidate_flag"), bool):
        messages.append("generated_candidate_flag should be boolean.")
    if not isinstance(candidate.get("research_mode_flag"), bool):
        messages.append("research_mode_flag should be boolean.")
    if not isinstance(candidate.get("evidence_package"), Mapping):
        messages.append("evidence_package should be present.")
    if not isinstance(candidate.get("factor_scores"), list):
        messages.append("factor_scores should be a list for this MaterialSystemCandidate contract.")
    if (
        candidate.get("system_architecture_type") == "bulk_material"
        and candidate.get("coating_or_surface_system")
    ):
        messages.append(
            "system_architecture_type is bulk_material while coating_or_surface_system is present."
        )
    return messages


def summarize_normalization(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    normalized = normalize_system_candidates(candidates)
    validation_messages = [
        message
        for candidate in normalized
        for message in validate_normalized_candidate(candidate)
    ]
    return {
        "total_candidate_count": len(normalized),
        "candidate_class_counts": dict(
            sorted(Counter(candidate.get("candidate_class", "unknown") for candidate in normalized).items())
        ),
        "source_type_counts": dict(
            sorted(
                Counter(
                    _text(candidate.get("source_type") or candidate.get("source_label"), "unknown")
                    for candidate in normalized
                ).items()
            )
        ),
        "evidence_maturity_counts": dict(
            sorted(Counter(candidate.get("evidence_maturity", "E") for candidate in normalized).items())
        ),
        "validation_message_count": len(validation_messages),
        "validation_messages": validation_messages,
    }
