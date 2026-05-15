from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.factor_models.common import collect_text, evidence_maturity_penalty, factor_requested, make_factor_score


_FACTORS = (
    "cmc.temperature_capability",
    "cmc.fiber_matrix_interphase_basis",
    "cmc.ebc_dependency",
    "cmc.oxidation_recession_risk",
    "cmc.thermal_cycling_delamination_risk",
    "cmc.repairability_maturity",
)


def _score(candidate: Mapping[str, Any], base: float, positive: Sequence[str], negative: Sequence[str] = ()) -> float:
    text = collect_text(candidate)
    return (
        base
        + 5.0 * sum(signal in text for signal in positive)
        - 7.0 * sum(signal in text for signal in negative)
        - evidence_maturity_penalty(candidate)
    )


def evaluate_cmc_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> list[FactorScore]:
    text = collect_text(candidate)
    has_ebc = "ebc" in text or "environmental barrier" in text
    common_warnings = [
        "CMC proxy factors are system-level skeletons and do not qualify fiber, matrix, interphase or EBC performance."
    ]
    if has_ebc:
        common_warnings.append("CMC candidate depends on EBC or coating-system assumptions for steam/oxidation exposure.")
    if "interphase" not in text:
        common_warnings.append("Interphase detail is missing or not visible; confidence is limited.")

    definitions = {
        "cmc.temperature_capability": (
            _score(candidate, 72.0, ("sic", "cmc", "high temperature", "ceramic matrix")),
            {"base": 72.0, "cmc_temperature_cues": True},
            "Proxy reflects CMC high-temperature capability cues and evidence maturity.",
        ),
        "cmc.fiber_matrix_interphase_basis": (
            _score(candidate, 58.0, ("fiber", "matrix", "interphase"), ("missing",)),
            {"base": 58.0, "fiber_matrix_interphase_visible": all(token in text for token in ("fiber", "matrix", "interphase"))},
            "Proxy reflects whether fiber, matrix and interphase are visible in the record.",
        ),
        "cmc.ebc_dependency": (
            _score(candidate, 50.0, ("ebc", "environmental barrier", "rare-earth silicate"), ("missing",)),
            {"base": 50.0, "ebc_present": has_ebc},
            "Proxy surfaces environmental-barrier dependency for CMC hot-section use.",
        ),
        "cmc.oxidation_recession_risk": (
            _score(candidate, 45.0, ("oxidation", "steam", "water vapor", "recession", "ebc"), ("fiber oxidation", "recession")),
            {"base": 45.0, "steam_recession_cues": any(token in text for token in ("steam", "water vapor", "recession"))},
            "Proxy keeps oxidation, steam and recession risk visible.",
        ),
        "cmc.thermal_cycling_delamination_risk": (
            _score(candidate, 44.0, ("thermal cycling", "damage tolerance"), ("delamination", "mismatch", "spallation")),
            {"base": 44.0, "thermal_cycling_cues": "thermal" in text},
            "Proxy surfaces thermal-cycling and delamination uncertainty.",
        ),
        "cmc.repairability_maturity": (
            _score(candidate, 46.0, ("repair", "mature", "aerospace", "curated"), ("repair complexity", "repair limits")),
            {"base": 46.0, "repairability_cues": "repair" in text},
            "Proxy reflects repair and maturity cues for CMC systems.",
        ),
    }

    return [
        make_factor_score(
            factor=factor,
            candidate=candidate,
            score=definitions[factor][0],
            method="build4_deterministic_cmc_proxy_v0",
            components=definitions[factor][1],
            reason=definitions[factor][2],
            assumptions=["No CMC micromechanics, oxidation kinetics or EBC durability model is applied."],
            warnings=common_warnings,
        )
        for factor in _FACTORS
        if factor_requested(factor, active_factors)
    ]
