from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import FactorScore
from src.factor_models.common import collect_text, evidence_maturity_penalty, factor_requested, make_factor_score


_FACTORS = (
    "coating.substrate_compatibility",
    "coating.cte_mismatch_spallation_risk",
    "coating.surface_preparation_process_basis",
    "coating.inspection_repair_interval",
    "coating.environmental_protection_benefit",
)


def _score(candidate: Mapping[str, Any], base: float, positive: Sequence[str], negative: Sequence[str] = ()) -> float:
    text = collect_text(candidate)
    return (
        base
        + 5.0 * sum(signal in text for signal in positive)
        - 7.0 * sum(signal in text for signal in negative)
        - evidence_maturity_penalty(candidate)
    )


def evaluate_coating_enabled_factors(
    candidate: Mapping[str, Any],
    active_factors: Sequence[str] | None = None,
) -> list[FactorScore]:
    text = collect_text(candidate)
    common_warnings = [
        "Coating-enabled factors treat coatings as system components, not standalone bulk candidates.",
        "Spallation, adhesion, CTE mismatch and inspection interval require system-specific validation.",
    ]
    if "coating" not in text and "tbc" not in text and "ebc" not in text:
        common_warnings.append("Coating details are missing or not visible; proxy confidence is limited.")

    definitions = {
        "coating.substrate_compatibility": (
            _score(candidate, 52.0, ("substrate", "bond coat", "compatibility", "ni superalloy", "sic/sic")),
            {"base": 52.0, "substrate_detail_visible": "substrate" in text},
            "Proxy reflects visible substrate/coating compatibility cues.",
        ),
        "coating.cte_mismatch_spallation_risk": (
            _score(candidate, 42.0, ("bond coat", "compliant"), ("spallation", "mismatch", "delamination")),
            {"base": 42.0, "spallation_or_mismatch_cues": any(token in text for token in ("spallation", "mismatch", "delamination"))},
            "Lower proxy score surfaces CTE mismatch, spallation and interface risk.",
        ),
        "coating.surface_preparation_process_basis": (
            _score(candidate, 50.0, ("plasma spray", "pvd", "deposition", "bond coat", "hvof")),
            {"base": 50.0, "process_detail_visible": any(token in text for token in ("spray", "pvd", "deposition", "hvof"))},
            "Proxy reflects whether coating deposition or preparation route is visible.",
        ),
        "coating.inspection_repair_interval": (
            _score(candidate, 46.0, ("repair", "inspection", "repairable"), ("defects", "repair limits", "spallation")),
            {"base": 46.0, "inspection_or_repair_cues": "repair" in text or "inspection" in text},
            "Proxy keeps inspection and repair-interval uncertainty visible.",
        ),
        "coating.environmental_protection_benefit": (
            _score(candidate, 62.0, ("oxidation", "thermal barrier", "environmental barrier", "steam", "recession", "tbc", "ebc")),
            {"base": 62.0, "environmental_protection_cues": True},
            "Proxy reflects visible environmental or thermal protection benefit cues.",
        ),
    }

    return [
        make_factor_score(
            factor=factor,
            candidate=candidate,
            score=definitions[factor][0],
            method="build4_deterministic_coating_enabled_proxy_v0",
            components=definitions[factor][1],
            reason=definitions[factor][2],
            assumptions=["No coating lifetime, adhesion or thermal mismatch calculation is performed."],
            warnings=common_warnings,
        )
        for factor in _FACTORS
        if factor_requested(factor, active_factors)
    ]
