from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.factor_models.common import collect_text, evidence_maturity_penalty, factor_requested, make_factor_score


_FACTORS = (
    "hybrid.interface_compatibility",
    "hybrid.process_chain_complexity",
    "hybrid.cross_class_failure_coupling",
    "hybrid.certification_route",
    "hybrid.through_life_strategy",
)


def _score(candidate: Mapping[str, Any], base: float, positive: Sequence[str], negative: Sequence[str] = ()) -> float:
    text = collect_text(candidate)
    return (
        base
        + 5.0 * sum(signal in text for signal in positive)
        - 7.0 * sum(signal in text for signal in negative)
        - evidence_maturity_penalty(candidate)
    )


def evaluate_hybrid_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> list[FactorScore]:
    text = collect_text(candidate)
    common_warnings = [
        "Hybrid factors are conservative cross-class proxy factors and do not resolve final architecture decisions."
    ]

    definitions = {
        "hybrid.interface_compatibility": (
            _score(candidate, 42.0, ("interface", "compatibility", "bond coat", "interphase"), ("mismatch", "delamination")),
            {"base": 42.0, "interface_cues": "interface" in text or "interphase" in text},
            "Proxy reflects visible interface compatibility cues.",
        ),
        "hybrid.process_chain_complexity": (
            _score(candidate, 38.0, ("route", "process", "repair"), ("multi", "hybrid", "complexity")),
            {"base": 38.0, "process_chain_visible": "process" in text or "route" in text},
            "Proxy surfaces process-chain complexity for hybrid systems.",
        ),
        "hybrid.cross_class_failure_coupling": (
            _score(candidate, 36.0, ("damage tolerance", "inspection"), ("spallation", "cracking", "recession", "delamination")),
            {"base": 36.0, "coupled_failure_cues": any(token in text for token in ("spallation", "cracking", "recession", "delamination"))},
            "Proxy keeps coupled failure modes visible across material classes.",
        ),
        "hybrid.certification_route": (
            _score(candidate, 34.0, ("mature", "curated", "engineering"), ("exploratory", "qualification", "certification")),
            {"base": 34.0, "certification_cues": "certification" in text or "qualification" in text},
            "Proxy reflects certification-route uncertainty for hybrid systems.",
        ),
        "hybrid.through_life_strategy": (
            _score(candidate, 40.0, ("repair", "inspection", "through life"), ("repair limits", "inspection gaps")),
            {"base": 40.0, "through_life_cues": "repair" in text or "inspection" in text},
            "Proxy keeps inspection, repair and through-life strategy visible.",
        ),
    }

    return [
        make_factor_score(
            factor=factor,
            candidate=candidate,
            score=definitions[factor][0],
            method="build4_deterministic_hybrid_proxy_v0",
            components=definitions[factor][1],
            reason=definitions[factor][2],
            assumptions=["No cross-class optimization or final architecture decision is performed."],
            warnings=common_warnings,
        )
        for factor in _FACTORS
        if factor_requested(factor, active_factors)
    ]
