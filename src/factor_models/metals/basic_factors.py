from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.factor_models.common import (
    collect_text,
    evidence_maturity_penalty,
    factor_requested,
    make_factor_score,
)


_FACTORS = (
    "metal.temperature_capability",
    "metal.creep_and_fatigue_basis",
    "metal.oxidation_hot_corrosion_basis",
    "metal.manufacturing_route_basis",
    "metal.repairability_and_maturity",
)


def _score(candidate: Mapping[str, Any], base: float, positive: Sequence[str], negative: Sequence[str] = ()) -> float:
    text = collect_text(candidate)
    value = base + 5.0 * sum(signal in text for signal in positive)
    value -= 7.0 * sum(signal in text for signal in negative)
    return value - evidence_maturity_penalty(candidate)


def evaluate_metal_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> list[FactorScore]:
    """Emit conservative Build 4 wrapper factors for metallic system candidates."""
    scores: list[FactorScore] = []
    text = collect_text(candidate)
    common_warnings = [
        "Build 4 metallic factors are wrapper proxies; existing Build 3.1 metallic factors remain separate."
    ]
    if "coating" in text or "tbc" in text:
        common_warnings.append("Metallic surface protection is represented only as a system-level cue here.")

    definitions = {
        "metal.temperature_capability": (
            _score(candidate, 62.0, ("superalloy", "refractory", "tbc", "thermal barrier")),
            {"base": 62.0, "temperature_text_signals": True},
            "Proxy reflects metallic family temperature cues and evidence maturity.",
        ),
        "metal.creep_and_fatigue_basis": (
            _score(candidate, 58.0, ("superalloy", "single crystal", "nickel"), ("brittle",)),
            {"base": 58.0, "creep_fatigue_proxy": True},
            "Proxy preserves creep/fatigue as a metallic basis factor without qualification claims.",
        ),
        "metal.oxidation_hot_corrosion_basis": (
            _score(candidate, 54.0, ("bond coat", "tbc", "oxidation", "aluminide", "mcraly"), ("steam",)),
            {"base": 54.0, "surface_protection_cues": "coating" in text or "oxidation" in text},
            "Proxy reflects visible oxidation or coating cues for metallic systems.",
        ),
        "metal.manufacturing_route_basis": (
            _score(candidate, 56.0, ("cast", "wrought", "powder", "coating deposition", "conventional")),
            {"base": 56.0, "route_detail_present": "route" in text or "process" in text},
            "Proxy reflects whether a route basis is visible in the candidate record.",
        ),
        "metal.repairability_and_maturity": (
            _score(candidate, 60.0, ("repair", "mature", "engineering_analogue", "curated")),
            {"base": 60.0, "maturity_adjusted": True},
            "Proxy combines maturity and repairability text cues for comparison only.",
        ),
    }

    for factor in _FACTORS:
        if not factor_requested(factor, active_factors):
            continue
        score, components, reason = definitions[factor]
        scores.append(
            make_factor_score(
                factor=factor,
                candidate=candidate,
                score=score,
                method="build4_deterministic_metal_wrapper_proxy_v0",
                components=components,
                reason=reason,
                assumptions=["No class-specific engineering calculation is performed in this skeleton."],
                warnings=common_warnings,
            )
        )
    return scores
