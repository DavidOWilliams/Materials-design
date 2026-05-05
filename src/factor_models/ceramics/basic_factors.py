from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.factor_models.common import collect_text, evidence_maturity_penalty, factor_requested, make_factor_score


_FACTORS = (
    "ceramic.temperature_capability",
    "ceramic.brittleness_fracture_risk",
    "ceramic.thermal_shock_risk",
    "ceramic.erosion_wear_basis",
    "ceramic.joining_inspection_proof_testing",
)


def _score(candidate: Mapping[str, Any], base: float, positive: Sequence[str], negative: Sequence[str] = ()) -> float:
    text = collect_text(candidate)
    return (
        base
        + 5.0 * sum(signal in text for signal in positive)
        - 7.0 * sum(signal in text for signal in negative)
        - evidence_maturity_penalty(candidate)
    )


def evaluate_ceramic_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> list[FactorScore]:
    text = collect_text(candidate)
    common_warnings = [
        "Monolithic ceramic proxy factors must keep brittle fracture, flaw sensitivity and proof testing visible."
    ]
    if "brittle" in text or "flaw" in text:
        common_warnings.append("Candidate record already flags brittleness or flaw sensitivity.")

    definitions = {
        "ceramic.temperature_capability": (
            _score(candidate, 70.0, ("sic", "silicon carbide", "silicon nitride", "oxide", "high temperature")),
            {"base": 70.0, "ceramic_temperature_cues": True},
            "Proxy reflects high-temperature ceramic family cues and evidence maturity.",
        ),
        "ceramic.brittleness_fracture_risk": (
            _score(candidate, 38.0, ("fracture toughness", "proof testing"), ("brittle", "flaw", "low fracture")),
            {"base": 38.0, "risk_factor": True},
            "Lower proxy score indicates visible brittle-fracture sensitivity rather than rejection.",
        ),
        "ceramic.thermal_shock_risk": (
            _score(candidate, 48.0, ("thermal shock", "silicon nitride"), ("thermal cycling", "thermal shock sensitivity")),
            {"base": 48.0, "thermal_cycle_cues": "thermal" in text},
            "Proxy surfaces thermal-shock and thermal-cycling uncertainty.",
        ),
        "ceramic.erosion_wear_basis": (
            _score(candidate, 55.0, ("hardness", "wear", "erosion", "chemical stability")),
            {"base": 55.0, "surface_damage_cues": "wear" in text or "erosion" in text},
            "Proxy reflects visible wear, erosion or hardness cues.",
        ),
        "ceramic.joining_inspection_proof_testing": (
            _score(candidate, 42.0, ("inspection", "proof testing"), ("joining", "inspection challenges")),
            {"base": 42.0, "inspection_detail_present": "inspection" in text or "proof" in text},
            "Proxy keeps joining, inspection and proof-testing concerns explicit.",
        ),
    }

    return [
        make_factor_score(
            factor=factor,
            candidate=candidate,
            score=definitions[factor][0],
            method="build4_deterministic_ceramic_proxy_v0",
            components=definitions[factor][1],
            reason=definitions[factor][2],
            assumptions=["No fracture mechanics calculation is performed in this skeleton."],
            warnings=common_warnings,
        )
        for factor in _FACTORS
        if factor_requested(factor, active_factors)
    ]
