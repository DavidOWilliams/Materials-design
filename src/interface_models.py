from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from src.contracts import EVIDENCE_MATURITY_LEVELS


_LOW_EVIDENCE_MATURITY = {"D", "E", "F"}
_RISK_ORDER = ("low", "medium", "high")


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


def _blob(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(f"{key} {_blob(item)}" for key, item in value.items()).lower()
    if isinstance(value, (list, tuple, set)):
        return " ".join(_blob(item) for item in value).lower()
    return _text(value).lower()


def _candidate_classes(candidate: Mapping[str, Any]) -> set[str]:
    classes = {
        _text(candidate.get("candidate_class")).lower(),
        _text(candidate.get("system_class")).lower(),
    }
    classes.update(_text(value).lower() for value in _as_list(candidate.get("system_classes")))
    return {value for value in classes if value}


def _candidate_id(candidate: Mapping[str, Any]) -> str:
    return _text(candidate.get("candidate_id"), "unknown_candidate")


def _evidence_maturity(candidate: Mapping[str, Any]) -> str | None:
    evidence = candidate.get("evidence_package") or candidate.get("evidence") or {}
    evidence_mapping = evidence if isinstance(evidence, Mapping) else {}
    for value in (
        evidence_mapping.get("maturity"),
        evidence_mapping.get("evidence_maturity"),
        candidate.get("evidence_maturity"),
    ):
        maturity = _text(value).upper()
        if maturity in EVIDENCE_MATURITY_LEVELS:
            return maturity
    return None


def _increase_risk_for_low_evidence(risk_level: str, maturity: str | None) -> str:
    if risk_level == "unknown" or maturity not in _LOW_EVIDENCE_MATURITY:
        return risk_level
    next_index = min(_RISK_ORDER.index(risk_level) + 1, len(_RISK_ORDER) - 1)
    return _RISK_ORDER[next_index]


def _has_coating_or_surface_system(candidate: Mapping[str, Any]) -> bool:
    return bool(
        candidate.get("coating_or_surface_system")
        or candidate.get("coating_system")
        or candidate.get("environmental_barrier_coating")
    )


def _is_cmc(candidate: Mapping[str, Any]) -> bool:
    classes = _candidate_classes(candidate)
    architecture = _text(candidate.get("system_architecture_type")).lower()
    return (
        "ceramic_matrix_composite" in classes
        or "cmc_plus_ebc" in architecture
        or "ceramic_matrix_composite" in architecture
        or "cmc" in architecture
    )


def _is_coating_enabled(candidate: Mapping[str, Any]) -> bool:
    classes = _candidate_classes(candidate)
    architecture = _text(candidate.get("system_architecture_type")).lower()
    return (
        "coating_enabled" in classes
        or architecture in {"coating_enabled", "substrate_plus_coating"}
        or bool(candidate.get("coating_enabled"))
    )


def _is_spatially_graded_am(candidate: Mapping[str, Any]) -> bool:
    classes = _candidate_classes(candidate)
    architecture = _text(candidate.get("system_architecture_type")).lower()
    return (
        "spatially_graded_am" in classes
        or "spatially_graded" in architecture
        or "spatial_gradient" in architecture
    )


def _constituents(candidate: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [item for item in _as_list(candidate.get("constituents")) if isinstance(item, Mapping)]


def _constituent_roles(candidate: Mapping[str, Any]) -> set[str]:
    roles: set[str] = set()
    for constituent in _constituents(candidate):
        role = _text(constituent.get("role")).lower()
        if role:
            roles.add(role)
    return roles


def _has_ebc(candidate: Mapping[str, Any]) -> bool:
    ebc = candidate.get("environmental_barrier_coating")
    if ebc:
        return True
    coating = candidate.get("coating_or_surface_system") or candidate.get("coating_system")
    coating_text = _blob(coating)
    return "ebc" in coating_text or "environmental barrier" in coating_text


def _gradient_text(candidate: Mapping[str, Any]) -> str:
    return _blob(candidate.get("gradient_architecture"))


def _risk_record(
    candidate: Mapping[str, Any],
    interface_type: str,
    base_risk: str,
    risk_flags: list[str],
    reason: str,
) -> dict[str, Any]:
    maturity = _evidence_maturity(candidate)
    risk_level = _increase_risk_for_low_evidence(base_risk, maturity)
    flags = list(risk_flags)
    if maturity in _LOW_EVIDENCE_MATURITY and base_risk != "unknown":
        flags.append(f"low_evidence_maturity_{maturity}")
    return {
        "interface_type": interface_type,
        "risk_level": risk_level,
        "risk_flags": flags,
        "reason": reason,
        "evidence_maturity": maturity,
    }


def infer_interface_type(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    """Infer a coarse interface type from adjacent component metadata."""
    left_text = _blob(left)
    right_text = _blob(right)
    combined = f"{left_text} {right_text}"

    left_role = _text(left.get("role")).lower()
    right_role = _text(right.get("role")).lower()
    roles = {left_role, right_role}

    if "gradient" in combined and "transition" in combined:
        if any(token in combined for token in ("metal_to_ceramic", "metal to ceramic", "metal ceramic")):
            return "metal_ceramic_transition"
        return "gradient_transition_zone"
    if any(token in combined for token in ("metal_to_ceramic", "multi_material_transition")):
        return "metal_ceramic_transition"
    if ("substrate" in roles and ({"coating", "bond_coat", "barrier_layer"} & roles)) or (
        "substrate" in combined and "coating" in combined
    ):
        return "substrate_coating"
    if {"matrix", "fiber"} <= roles or ("matrix" in roles and "reinforcement" in roles):
        return "matrix_fiber"
    if "fiber" in roles and "interphase" in roles:
        return "fiber_interphase"
    if any(token in combined for token in ("environmental barrier", "ebc")) and any(
        token in combined for token in ("cmc", "ceramic matrix composite")
    ):
        return "cmc_ebc"
    return "unknown_interface"


def assess_interface_risks(candidate: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return deterministic interface-risk records for a normalized candidate-like mapping."""
    risks: list[dict[str, Any]] = []

    if _is_coating_enabled(candidate):
        if _has_coating_or_surface_system(candidate):
            risks.append(
                _risk_record(
                    candidate,
                    "substrate_coating",
                    "medium",
                    ["coating_enabled_system"],
                    "Coating-enabled material systems require substrate/coating compatibility review.",
                )
            )
        else:
            risks.append(
                _risk_record(
                    candidate,
                    "substrate_coating",
                    "unknown",
                    ["missing_coating_or_surface_system"],
                    "Coating-enabled candidate is missing coating or surface-system details.",
                )
            )

    if _is_cmc(candidate):
        if _has_ebc(candidate):
            risks.append(
                _risk_record(
                    candidate,
                    "cmc_ebc",
                    "medium",
                    ["cmc_environmental_barrier_interface"],
                    "CMC plus EBC systems require CMC/environmental-barrier interface checks.",
                )
            )
        elif _has_coating_or_surface_system(candidate):
            risks.append(
                _risk_record(
                    candidate,
                    "cmc_ebc",
                    "medium",
                    ["cmc_coating_interface"],
                    "CMC system includes coating data that should be treated as an interface.",
                )
            )

        roles = _constituent_roles(candidate)
        if "matrix" in roles and ({"fiber", "reinforcement"} & roles):
            risks.append(
                _risk_record(
                    candidate,
                    "matrix_fiber",
                    "medium",
                    ["visible_matrix_fiber_constituents"],
                    "CMC constituents expose a matrix/fiber load-transfer interface.",
                )
            )
        elif _constituents(candidate) and not ({"matrix", "fiber", "reinforcement"} <= roles):
            risks.append(
                _risk_record(
                    candidate,
                    "matrix_fiber",
                    "unknown",
                    ["incomplete_cmc_constituent_roles"],
                    "CMC constituent details are present but matrix/fiber roles are incomplete.",
                )
            )

        if "fiber" in roles and "interphase" in roles:
            risks.append(
                _risk_record(
                    candidate,
                    "fiber_interphase",
                    "medium",
                    ["visible_fiber_interphase_constituents"],
                    "CMC constituents expose a fiber/interphase compatibility interface.",
                )
            )

    if _is_spatially_graded_am(candidate):
        if candidate.get("gradient_architecture"):
            risks.append(
                _risk_record(
                    candidate,
                    "gradient_transition_zone",
                    "medium",
                    ["spatially_graded_am_transition_zone"],
                    "Spatially graded AM candidates require transition-zone inspection and qualification.",
                )
            )
        else:
            risks.append(
                _risk_record(
                    candidate,
                    "gradient_transition_zone",
                    "unknown",
                    ["missing_gradient_architecture"],
                    "Spatially graded AM candidate is missing gradient architecture details.",
                )
            )

    gradient_text = _gradient_text(candidate)
    if any(
        token in gradient_text
        for token in (
            "transition",
            "metal_to_ceramic",
            "metal to ceramic",
            "metal-ceramic",
            "metal ceramic",
            "multi_material_transition",
            "multi material transition",
        )
    ):
        risks.append(
            _risk_record(
                candidate,
                "metal_ceramic_transition",
                "high",
                ["multi_material_gradient_transition"],
                "Gradient architecture describes a multi-material or metal/ceramic transition.",
            )
        )

    return risks


def summarize_interface_risks(candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize interface-risk records without filtering or ranking candidates."""
    assessed = [(candidate, assess_interface_risks(candidate)) for candidate in candidates]
    interface_type_counts = Counter(
        risk["interface_type"] for _, risks in assessed for risk in risks
    )
    risk_level_counts = Counter(risk["risk_level"] for _, risks in assessed for risk in risks)
    high_risk_candidate_ids = sorted(
        {
            _candidate_id(candidate)
            for candidate, risks in assessed
            if any(risk.get("risk_level") == "high" for risk in risks)
        }
    )
    warnings = [
        f"{_candidate_id(candidate)} has interface risks with unknown risk level."
        for candidate, risks in assessed
        if any(risk.get("risk_level") == "unknown" for risk in risks)
    ]

    return {
        "candidate_count": len(candidates),
        "interface_type_counts": dict(sorted(interface_type_counts.items())),
        "risk_level_counts": dict(sorted(risk_level_counts.items())),
        "high_risk_candidate_ids": high_risk_candidate_ids,
        "warnings": warnings,
    }
