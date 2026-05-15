from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.optimisation_trace import build_traces_for_candidate, run_optimisation_traces


TRADEOFF_DIMENSION_IDS: tuple[str, ...] = (
    "evidence_maturity",
    "coating_dependency",
    "spatial_gradient_dependency",
    "research_mode_exposure",
    "review_burden",
    "introduced_risk_burden",
    "expected_benefit_signal",
    "process_route_visibility",
    "architecture_change_exposure",
    "certification_caution",
)

VECTOR_STATUSES: tuple[str, ...] = (
    "no_traces_available",
    "tradeoff_vector_available",
    "research_mode_vector_available",
)

BAND_VALUES: tuple[str, ...] = (
    "favourable",
    "neutral",
    "caution",
    "high_caution",
    "unknown",
)


class TradeoffDimension(TypedDict, total=False):
    dimension_id: str
    label: str
    raw_value: str
    band: str
    numeric_value: float | None
    direction: str
    rationale: str
    evidence_refs: list[str]
    warnings: list[str]


class CandidateTradeoffVector(TypedDict, total=False):
    candidate_id: str
    system_name: str
    limiting_factors: list[str]
    trace_count: int
    dimensions: list[TradeoffDimension]
    dimension_count: int
    vector_status: str
    notes: list[str]
    warnings: list[str]


class TradeoffVectorRun(TypedDict, total=False):
    candidate_count: int
    vector_count: int
    dimension_count: int
    research_mode_enabled: bool
    vectors: list[CandidateTradeoffVector]
    vector_summary: dict[str, Any]
    notes: list[str]
    warnings: list[str]


def _as_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    if not all(isinstance(item, str) for item in value):
        return []
    return list(value)


def evidence_maturity_numeric(maturity: str) -> float | None:
    maturity_key = _as_string(maturity, "unknown").lower()
    return {
        "a": 6.0,
        "b": 5.0,
        "c": 4.0,
        "d": 3.0,
        "e": 2.0,
        "f": 1.0,
        "unknown": None,
    }.get(maturity_key)


def evidence_maturity_band(maturity: str) -> str:
    maturity_key = _as_string(maturity, "unknown").lower()
    if maturity_key in ("a", "b"):
        return "favourable"
    if maturity_key in ("c", "d"):
        return "caution"
    if maturity_key in ("e", "f"):
        return "high_caution"
    return "unknown"


def count_traces_with_badge(traces: Sequence[Mapping[str, Any]], badge: str) -> int:
    count = 0
    for trace in traces:
        badges = trace.get("ui_badges")
        if isinstance(badges, list) and badge in badges:
            count += 1
    return count


def count_traces_with_status(traces: Sequence[Mapping[str, Any]], status: str) -> int:
    return sum(1 for trace in traces if trace.get("status") == status)


def max_review_required_count(traces: Sequence[Mapping[str, Any]]) -> int:
    max_count = 0
    for trace in traces:
        review_required = _string_list(trace.get("review_required"))
        max_count = max(max_count, len(review_required))
    return max_count


def total_introduced_risk_count(traces: Sequence[Mapping[str, Any]]) -> int:
    return sum(len(_string_list(trace.get("introduced_risks"))) for trace in traces)


def total_expected_benefit_count(traces: Sequence[Mapping[str, Any]]) -> int:
    return sum(len(_string_list(trace.get("expected_benefits"))) for trace in traces)


def has_architecture_change(traces: Sequence[Mapping[str, Any]]) -> bool:
    for trace in traces:
        change_summary = _string_list(trace.get("change_summary"))
        for change in change_summary:
            if "system_architecture_type changed" in change.lower():
                return True
    return False


def candidate_evidence_maturity(candidate_trace: Mapping[str, Any]) -> str:
    traces = candidate_trace.get("traces")
    if not isinstance(traces, list):
        return "unknown"
    for trace in traces:
        if not isinstance(trace, Mapping):
            continue
        maturity = _as_string(trace.get("evidence_maturity"), "unknown")
        if maturity.lower() != "unknown":
            return maturity
    return "unknown"


def build_dimension(
    dimension_id: str,
    *,
    label: str,
    raw_value: str,
    band: str,
    numeric_value: float | None = None,
    direction: str = "contextual",
    rationale: str,
    evidence_refs: Sequence[str] | None = None,
    warnings: Sequence[str] | None = None,
) -> TradeoffDimension:
    return {
        "dimension_id": dimension_id,
        "label": label,
        "raw_value": raw_value,
        "band": band,
        "numeric_value": numeric_value,
        "direction": direction,
        "rationale": rationale,
        "evidence_refs": list(evidence_refs or []),
        "warnings": list(warnings or []),
    }


def _band_for_positive_count(count: int) -> str:
    return "favourable" if count == 0 else "caution"


def _review_burden_band(count: int) -> str:
    if count == 0:
        return "favourable"
    if count <= 3:
        return "caution"
    return "high_caution"


def _risk_burden_band(count: int) -> str:
    if count == 0:
        return "favourable"
    if count <= 4:
        return "caution"
    return "high_caution"


def _benefit_signal_band(count: int) -> str:
    if count == 0:
        return "unknown"
    if count <= 2:
        return "neutral"
    return "favourable"


def _process_route_visibility_count(traces: Sequence[Mapping[str, Any]]) -> int:
    count = 0
    for trace in traces:
        before = trace.get("before_state_summary")
        after = trace.get("proposed_after_state_summary")
        before_routes = (
            before.get("process_route_summary")
            if isinstance(before, Mapping)
            else None
        )
        after_routes = (
            after.get("process_route_summary")
            if isinstance(after, Mapping)
            else None
        )
        if _string_list(before_routes) or _string_list(after_routes):
            count += 1
    return count


def _research_mode_exposure_count(traces: Sequence[Mapping[str, Any]]) -> int:
    count = 0
    for trace in traces:
        badges = trace.get("ui_badges")
        if trace.get("status") == "research_mode_only" or (
            isinstance(badges, list) and "research_mode_only" in badges
        ):
            count += 1
    return count


def _certification_caution_band(
    traces: Sequence[Mapping[str, Any]],
    *,
    maturity_band: str,
) -> str:
    if not traces:
        return "unknown"
    for trace in traces:
        badges = trace.get("ui_badges")
        if isinstance(badges, list) and (
            "no_certification_claim" in badges or "research_mode_only" in badges
        ):
            return "high_caution"
        if trace.get("status") == "research_mode_only":
            return "high_caution"
    if maturity_band == "high_caution":
        return "high_caution"
    return "caution"


def _trace_refs(traces: Sequence[Mapping[str, Any]]) -> list[str]:
    refs: list[str] = []
    for trace in traces:
        trace_id = _as_string(trace.get("trace_id"))
        if trace_id:
            refs.append(trace_id)
    return refs


def build_tradeoff_vector_from_candidate_trace(
    candidate_trace: Mapping[str, Any],
) -> CandidateTradeoffVector:
    traces_value = candidate_trace.get("traces")
    traces = list(traces_value) if isinstance(traces_value, list) else []
    trace_count = len(traces)
    trace_refs = _trace_refs(traces)

    maturity = candidate_evidence_maturity(candidate_trace)
    maturity_band = evidence_maturity_band(maturity)
    coating_count = count_traces_with_badge(traces, "coating_refinement")
    gradient_count = count_traces_with_badge(traces, "spatial_gradient_refinement")
    research_mode_count = _research_mode_exposure_count(traces)
    review_count = max_review_required_count(traces)
    risk_count = total_introduced_risk_count(traces)
    benefit_count = total_expected_benefit_count(traces)
    process_visibility_count = _process_route_visibility_count(traces)
    architecture_changed = has_architecture_change(traces)
    certification_band = _certification_caution_band(
        traces,
        maturity_band=maturity_band,
    )

    dimensions: list[TradeoffDimension] = [
        build_dimension(
            "evidence_maturity",
            label="Evidence maturity",
            raw_value=maturity,
            band=maturity_band,
            numeric_value=evidence_maturity_numeric(maturity),
            direction="higher_is_better",
            rationale=(
                "Exposes evidence maturity without converting it into a recommendation."
            ),
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "coating_dependency",
            label="Coating dependency",
            raw_value=str(coating_count),
            band=_band_for_positive_count(coating_count),
            numeric_value=float(coating_count),
            direction="lower_is_simpler",
            rationale=(
                "Coating-enabled concepts may introduce substrate/interface, inspection "
                "and repair review needs."
            ),
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "spatial_gradient_dependency",
            label="Spatial gradient dependency",
            raw_value=str(gradient_count),
            band=_band_for_positive_count(gradient_count),
            numeric_value=float(gradient_count),
            direction="lower_is_simpler",
            rationale=(
                "Spatial gradients may introduce gradient feasibility, transition-zone "
                "and maturity review needs."
            ),
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "research_mode_exposure",
            label="Research-mode exposure",
            raw_value=str(research_mode_count),
            band="favourable" if research_mode_count == 0 else "high_caution",
            numeric_value=float(research_mode_count),
            direction="lower_is_better",
            rationale="Research-mode concepts remain exploratory.",
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "review_burden",
            label="Review burden",
            raw_value=str(review_count),
            band=_review_burden_band(review_count),
            numeric_value=float(review_count),
            direction="lower_is_better",
            rationale=(
                "More review requirements mean more validation and engineering "
                "assessment effort."
            ),
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "introduced_risk_burden",
            label="Introduced risk burden",
            raw_value=str(risk_count),
            band=_risk_burden_band(risk_count),
            numeric_value=float(risk_count),
            direction="lower_is_better",
            rationale="Introduced risks should remain visible before any recommendation.",
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "expected_benefit_signal",
            label="Expected benefit signal",
            raw_value=str(benefit_count),
            band=_benefit_signal_band(benefit_count),
            numeric_value=float(benefit_count),
            direction="higher_is_better",
            rationale="Counts visible benefit claims without asserting realised performance.",
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "process_route_visibility",
            label="Process route visibility",
            raw_value=str(process_visibility_count),
            band="caution" if process_visibility_count == 0 else "neutral",
            numeric_value=float(process_visibility_count),
            direction="higher_visibility_is_better",
            rationale=(
                "Process route visibility is important for manufacturability and "
                "qualification planning."
            ),
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "architecture_change_exposure",
            label="Architecture change exposure",
            raw_value="true" if architecture_changed else "false",
            band="caution" if architecture_changed else "neutral",
            numeric_value=1.0 if architecture_changed else 0.0,
            direction="lower_change_is_simpler",
            rationale=(
                "Architecture changes may create integration, inspection, repair and "
                "maturity implications."
            ),
            evidence_refs=trace_refs,
        ),
        build_dimension(
            "certification_caution",
            label="Certification caution",
            raw_value=certification_band,
            band=certification_band,
            numeric_value=None,
            direction="lower_is_better",
            rationale=(
                "The tool is decision support only and cannot provide certification or "
                "qualification approval."
            ),
            evidence_refs=trace_refs,
        ),
    ]

    if trace_count == 0:
        vector_status = "no_traces_available"
    elif research_mode_count > 0:
        vector_status = "research_mode_vector_available"
    else:
        vector_status = "tradeoff_vector_available"

    warnings = _string_list(deepcopy(candidate_trace.get("warnings")))
    if vector_status == "research_mode_vector_available":
        warnings.append("Research-mode traces are present; vector is exploratory.")
    if trace_count == 0:
        warnings.append("No optimisation traces are available for this candidate.")

    return {
        "candidate_id": _as_string(candidate_trace.get("candidate_id"), "unknown_candidate"),
        "system_name": _as_string(candidate_trace.get("system_name"), "unknown_system"),
        "limiting_factors": _string_list(candidate_trace.get("limiting_factors")),
        "trace_count": trace_count,
        "dimensions": dimensions,
        "dimension_count": len(dimensions),
        "vector_status": vector_status,
        "notes": [
            "Trade-off dimensions are deterministic signals, not weighted scores.",
            "Dimensions are not ranked, aggregated or used to select a candidate.",
        ],
        "warnings": warnings,
    }


def build_tradeoff_vector_for_candidate(
    candidate: Mapping[str, Any],
    *,
    limiting_factors: Sequence[str],
    candidate_index: int = 0,
    research_mode_enabled: bool = False,
) -> CandidateTradeoffVector:
    candidate_trace = build_traces_for_candidate(
        candidate,
        limiting_factors=list(limiting_factors),
        candidate_index=candidate_index,
        research_mode_enabled=research_mode_enabled,
    )
    return build_tradeoff_vector_from_candidate_trace(candidate_trace)


def _vector_summary(vectors: Sequence[CandidateTradeoffVector]) -> dict[str, Any]:
    by_vector_status = {status: 0 for status in VECTOR_STATUSES}
    by_dimension_band = {band: 0 for band in BAND_VALUES}
    research_mode_vector_count = 0

    for vector in vectors:
        status = _as_string(vector.get("vector_status"), "unknown")
        by_vector_status[status] = by_vector_status.get(status, 0) + 1
        if status == "research_mode_vector_available":
            research_mode_vector_count += 1
        for dimension in vector.get("dimensions", []):
            band = _as_string(dimension.get("band"), "unknown")
            by_dimension_band[band] = by_dimension_band.get(band, 0) + 1

    return {
        "by_vector_status": by_vector_status,
        "by_dimension_band": by_dimension_band,
        "research_mode_vector_count": research_mode_vector_count,
    }


def run_tradeoff_vectors(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> TradeoffVectorRun:
    trace_run = run_optimisation_traces(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    candidate_traces = trace_run.get("candidate_traces", [])
    vectors = [
        build_tradeoff_vector_from_candidate_trace(candidate_trace)
        for candidate_trace in candidate_traces
    ]
    dimension_count = sum(vector.get("dimension_count", 0) for vector in vectors)
    warnings: list[str] = []
    if research_mode_enabled:
        warnings.append("Research mode is enabled; trade-off vectors may include exploratory traces.")

    return {
        "candidate_count": len(candidates),
        "vector_count": len(vectors),
        "dimension_count": dimension_count,
        "research_mode_enabled": research_mode_enabled,
        "vectors": vectors,
        "vector_summary": _vector_summary(vectors),
        "notes": [
            "This run produces comparison vectors only.",
            "It does not rank, weight, aggregate, certify or select candidates.",
        ],
        "warnings": warnings,
    }
