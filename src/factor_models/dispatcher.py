from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.evidence_model import evaluate_candidate_evidence
from src.factor_models.ceramics import evaluate_ceramic_factors
from src.factor_models.cmcs import evaluate_cmc_factors
from src.factor_models.coatings import evaluate_coating_enabled_factors
from src.factor_models.common import factor_requested, make_factor_score
from src.factor_models.graded_am import evaluate_graded_am_factors
from src.factor_models.hybrids import evaluate_hybrid_factors
from src.factor_models.metals import evaluate_metal_factors
from src.material_system_schema import MaterialSystemCandidate
from src.system_assembler import assemble_material_system


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


def _candidate_class(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_class") or candidate.get("system_class"), "unknown")


def _architecture(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("system_architecture_type"), "unknown")


def _factor_namespace(factor_score: Mapping[str, Any]) -> str:
    factor = _text(factor_score.get("factor") or factor_score.get("factor_name"), "unknown")
    return factor.split(".", 1)[0] if "." in factor else factor


def _generic_warning_factor(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None,
) -> list[FactorScore]:
    factor = "generic.unclassified_candidate_warning"
    if not factor_requested(factor, active_factors):
        return []
    return [
        make_factor_score(
            factor=factor,
            candidate=candidate,
            score=20.0,
            method="build4_generic_unknown_class_warning_v0",
            components={
                "candidate_class": _candidate_class(candidate),
                "system_architecture_type": _architecture(candidate),
            },
            reason="Candidate class is not yet covered by a Build 4 class-specific factor skeleton.",
            assumptions=["Unknown class is retained and marked conservatively rather than filtered."],
            warnings=["Unknown candidate class; emitted generic warning factor instead of raising an error."],
        )
    ]


def _dispatch_factor_scores(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None,
) -> list[FactorScore]:
    candidate_class = _candidate_class(candidate)
    architecture = _architecture(candidate)

    if candidate_class == "metallic":
        return evaluate_metal_factors(candidate, active_factors)
    if candidate_class == "monolithic_ceramic":
        return evaluate_ceramic_factors(candidate, active_factors)
    if candidate_class == "ceramic_matrix_composite" or architecture == "cmc_plus_ebc":
        return evaluate_cmc_factors(candidate, active_factors)
    if candidate_class == "coating_enabled" or architecture in {"substrate_plus_coating", "coating_enabled"}:
        return evaluate_coating_enabled_factors(candidate, active_factors)
    if candidate_class == "spatially_graded_am" or architecture in {"spatial_gradient", "spatially_graded_am_system"}:
        return evaluate_graded_am_factors(candidate, active_factors)
    if candidate_class == "hybrid":
        return evaluate_hybrid_factors(candidate, active_factors)
    return _generic_warning_factor(candidate, active_factors)


def evaluate_candidate_system_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Attach Build 4 class-specific proxy factor scores to one candidate."""
    evaluated = evaluate_candidate_evidence(candidate)
    assembled = assemble_material_system(evaluated)
    output: dict[str, Any] = dict(assembled)

    existing_scores = [
        dict(item) for item in _as_list(output.get("factor_scores")) if isinstance(item, Mapping)
    ]
    new_scores = _dispatch_factor_scores(output, active_factors)
    output["factor_scores"] = existing_scores + new_scores
    output["factor_model_trace"] = _as_list(output.get("factor_model_trace"))
    output["factor_model_trace"].append("Attached Build 4 class-specific proxy factor skeletons.")
    output["factor_model_warnings"] = _as_list(output.get("factor_model_warnings"))
    for score in new_scores:
        for warning in _as_list(score.get("warnings")):
            if warning not in output["factor_model_warnings"]:
                output["factor_model_warnings"].append(warning)
    return output


def evaluate_candidate_systems_factors(
    candidates: Sequence[Mapping[str, Any]],
    active_factors: Sequence[str] | None = None,
) -> list[MaterialSystemCandidate]:
    """Evaluate candidates without filtering, preserving input length and order."""
    return [evaluate_candidate_system_factors(candidate, active_factors) for candidate in candidates]


def summarize_factor_outputs(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize attached factor scores by candidate class and factor namespace."""
    candidate_class_counts = Counter(_candidate_class(candidate) for candidate in candidates)
    namespace_counts = Counter(
        _factor_namespace(score)
        for candidate in candidates
        for score in _as_list(candidate.get("factor_scores"))
        if isinstance(score, Mapping)
    )
    warning_candidate_ids = [
        _text(candidate.get("candidate_id"), "unknown_candidate")
        for candidate in candidates
        if _as_list(candidate.get("factor_model_warnings"))
    ]
    return {
        "candidate_count": len(candidates),
        "candidate_class_counts": dict(sorted(candidate_class_counts.items())),
        "factor_namespace_counts": dict(sorted(namespace_counts.items())),
        "candidates_with_factor_scores": sum(
            1 for candidate in candidates if _as_list(candidate.get("factor_scores"))
        ),
        "warning_candidate_ids": warning_candidate_ids,
        "warnings": [
            f"{_text(candidate.get('candidate_id'), 'unknown_candidate')}: {warning}"
            for candidate in candidates
            for warning in _as_list(candidate.get("factor_model_warnings"))
        ],
    }
