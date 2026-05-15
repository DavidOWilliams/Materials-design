from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.factor_models.common import collect_text, evidence_maturity, evidence_maturity_penalty, factor_requested, make_factor_score


_FACTORS = (
    "graded_am.gradient_functional_benefit",
    "graded_am.gradient_feasibility",
    "graded_am.transition_zone_risk",
    "graded_am.process_window_sensitivity",
    "graded_am.inspectability_repairability",
    "graded_am.cost_scalability_certification_risk",
)


def _score(candidate: Mapping[str, Any], base: float, positive: Sequence[str], negative: Sequence[str] = ()) -> float:
    text = collect_text(candidate)
    return (
        base
        + 5.0 * sum(signal in text for signal in positive)
        - 7.0 * sum(signal in text for signal in negative)
        - evidence_maturity_penalty(candidate)
    )


def evaluate_graded_am_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> list[FactorScore]:
    text = collect_text(candidate)
    maturity = evidence_maturity(candidate)
    common_warnings = [
        "Spatially graded AM proxy factors are exploratory architecture skeletons, not coating or bulk-material scores."
    ]
    if maturity in {"D", "E", "F"}:
        common_warnings.append(
            f"Graded AM evidence maturity {maturity} is exploratory; do not upgrade to mature recommendation status."
        )
    if "gradient_architecture" not in text and "gradient" not in text:
        common_warnings.append("Gradient architecture details are missing or not visible.")

    definitions = {
        "graded_am.gradient_functional_benefit": (
            _score(candidate, 58.0, ("oxidation", "thermal", "surface", "transition", "graded", "gradient")),
            {"base": 58.0, "surface_to_core_cues": any(token in text for token in ("surface", "core", "transition"))},
            "Proxy reflects potential surface-to-core functional benefit from a gradient.",
        ),
        "graded_am.gradient_feasibility": (
            _score(candidate, 42.0, ("directed energy", "powder bed", "additive", "process window"), ("cracking", "repeatability")),
            {"base": 42.0, "am_route_visible": any(token in text for token in ("additive", "directed energy", "powder bed"))},
            "Proxy reflects whether a plausible AM route is visible, with maturity penalty.",
        ),
        "graded_am.transition_zone_risk": (
            _score(candidate, 36.0, ("compliant", "transition"), ("cracking", "delamination", "mismatch", "residual stress")),
            {"base": 36.0, "transition_zone_cues": "transition" in text},
            "Lower proxy score surfaces transition-zone risk rather than filtering the candidate.",
        ),
        "graded_am.process_window_sensitivity": (
            _score(candidate, 34.0, ("parameter", "process window", "heat treatment"), ("repeatability", "cracking", "qualification")),
            {"base": 34.0, "process_sensitivity_cues": any(token in text for token in ("parameter", "repeatability", "qualification"))},
            "Proxy keeps process-window sensitivity visible.",
        ),
        "graded_am.inspectability_repairability": (
            _score(candidate, 32.0, ("inspection", "verification", "repair"), ("inspection gaps", "repair", "through depth")),
            {"base": 32.0, "through_depth_verification_cues": "through" in text or "inspection" in text},
            "Proxy reflects inspectability and repairability uncertainty for integrated gradients.",
        ),
        "graded_am.cost_scalability_certification_risk": (
            _score(candidate, 30.0, ("demonstrated", "reference"), ("certification", "scalability", "complexity", "exploratory")),
            {"base": 30.0, "certification_risk_cues": "certification" in text or "qualification" in text},
            "Proxy surfaces cost, scalability and certification route risk.",
        ),
    }

    return [
        make_factor_score(
            factor=factor,
            candidate=candidate,
            score=definitions[factor][0],
            method="build4_deterministic_graded_am_proxy_v0",
            components=definitions[factor][1],
            reason=definitions[factor][2],
            assumptions=["No additive process simulation, residual-stress model or optimization is performed."],
            warnings=common_warnings,
        )
        for factor in _FACTORS
        if factor_requested(factor, active_factors)
    ]
