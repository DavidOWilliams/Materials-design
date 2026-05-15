from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.tradeoff_vectors import run_tradeoff_vectors


DOMINANCE_RESULTS: tuple[str, ...] = (
    "a_dominates_b",
    "b_dominates_a",
    "neither_dominates",
    "insufficient_comparable_dimensions",
)

COMPARABLE_DIRECTION_MAP: dict[str, float] = {
    "higher_is_better": 1.0,
    "lower_is_better": -1.0,
    "lower_is_simpler": -1.0,
    "higher_visibility_is_better": 1.0,
    "lower_change_is_simpler": -1.0,
}


class ComparableDimension(TypedDict, total=False):
    dimension_id: str
    raw_value: str
    numeric_value: float
    direction: str
    comparable_value: float
    rationale: str


class PairwiseFrontierComparison(TypedDict, total=False):
    candidate_a_id: str
    candidate_b_id: str
    comparable_dimension_ids: list[str]
    a_better_dimensions: list[str]
    b_better_dimensions: list[str]
    equal_dimensions: list[str]
    incomparable_dimension_ids: list[str]
    dominance_result: str
    explanation: list[str]


class FrontierCandidate(TypedDict, total=False):
    candidate_id: str
    system_name: str
    vector_status: str
    on_frontier: bool
    dominated_by: list[str]
    dominates: list[str]
    comparable_dimensions: list[ComparableDimension]
    excluded_dimension_ids: list[str]
    warnings: list[str]
    notes: list[str]


class ParetoFrontierRun(TypedDict, total=False):
    candidate_count: int
    vector_count: int
    frontier_count: int
    dominated_count: int
    comparison_count: int
    research_mode_enabled: bool
    frontier_candidates: list[FrontierCandidate]
    pairwise_comparisons: list[PairwiseFrontierComparison]
    frontier_summary: dict[str, Any]
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


def comparable_dimension_from_tradeoff_dimension(
    dimension: Mapping[str, Any],
) -> ComparableDimension | None:
    numeric_value = dimension.get("numeric_value")
    if not isinstance(numeric_value, (int, float)):
        return None

    direction = _as_string(dimension.get("direction"), "unknown")
    sign = COMPARABLE_DIRECTION_MAP.get(direction)
    if sign is None:
        return None

    numeric_float = float(numeric_value)
    return {
        "dimension_id": _as_string(dimension.get("dimension_id"), "unknown_dimension"),
        "raw_value": _as_string(dimension.get("raw_value")),
        "numeric_value": numeric_float,
        "direction": direction,
        "comparable_value": numeric_float * sign,
        "rationale": _as_string(dimension.get("rationale")),
    }


def comparable_dimensions_for_vector(
    vector: Mapping[str, Any],
) -> tuple[list[ComparableDimension], list[str]]:
    dimensions = vector.get("dimensions")
    if not isinstance(dimensions, list):
        return [], []

    comparable_dimensions: list[ComparableDimension] = []
    excluded_dimension_ids: list[str] = []
    for dimension in dimensions:
        if not isinstance(dimension, Mapping):
            continue
        comparable_dimension = comparable_dimension_from_tradeoff_dimension(dimension)
        if comparable_dimension is None:
            excluded_dimension_ids.append(
                _as_string(dimension.get("dimension_id"), "unknown_dimension")
            )
        else:
            comparable_dimensions.append(comparable_dimension)
    return comparable_dimensions, excluded_dimension_ids


def _dimension_map(
    candidate: Mapping[str, Any],
) -> dict[str, ComparableDimension]:
    mapped: dict[str, ComparableDimension] = {}
    dimensions = candidate.get("comparable_dimensions")
    if not isinstance(dimensions, list):
        return mapped
    for dimension in dimensions:
        if isinstance(dimension, Mapping):
            dimension_id = _as_string(dimension.get("dimension_id"))
            if dimension_id:
                mapped[dimension_id] = dict(dimension)
    return mapped


def compare_frontier_candidates(
    candidate_a: Mapping[str, Any],
    candidate_b: Mapping[str, Any],
) -> PairwiseFrontierComparison:
    candidate_a_id = _as_string(candidate_a.get("candidate_id"), "candidate_a")
    candidate_b_id = _as_string(candidate_b.get("candidate_id"), "candidate_b")
    a_dimensions = _dimension_map(candidate_a)
    b_dimensions = _dimension_map(candidate_b)
    shared_dimension_ids = [
        dimension_id for dimension_id in a_dimensions if dimension_id in b_dimensions
    ]
    incomparable_dimension_ids = [
        dimension_id for dimension_id in a_dimensions if dimension_id not in b_dimensions
    ]
    incomparable_dimension_ids.extend(
        dimension_id for dimension_id in b_dimensions if dimension_id not in a_dimensions
    )

    a_better_dimensions: list[str] = []
    b_better_dimensions: list[str] = []
    equal_dimensions: list[str] = []

    for dimension_id in shared_dimension_ids:
        a_value = a_dimensions[dimension_id]["comparable_value"]
        b_value = b_dimensions[dimension_id]["comparable_value"]
        if a_value > b_value:
            a_better_dimensions.append(dimension_id)
        elif b_value > a_value:
            b_better_dimensions.append(dimension_id)
        else:
            equal_dimensions.append(dimension_id)

    if not shared_dimension_ids:
        dominance_result = "insufficient_comparable_dimensions"
    elif a_better_dimensions and not b_better_dimensions:
        dominance_result = "a_dominates_b"
    elif b_better_dimensions and not a_better_dimensions:
        dominance_result = "b_dominates_a"
    else:
        dominance_result = "neither_dominates"

    explanation = [
        f"Compared {candidate_a_id} and {candidate_b_id} using shared comparable dimensions only.",
        "No weights, aggregate scores, ranks or winner selection were used.",
    ]
    if dominance_result == "insufficient_comparable_dimensions":
        explanation.append("No shared comparable dimensions were available.")
    elif dominance_result == "a_dominates_b":
        explanation.append(f"{candidate_a_id} is better on at least one shared dimension and worse on none.")
    elif dominance_result == "b_dominates_a":
        explanation.append(f"{candidate_b_id} is better on at least one shared dimension and worse on none.")
    else:
        explanation.append("Neither candidate dominates the other across shared dimensions.")

    return {
        "candidate_a_id": candidate_a_id,
        "candidate_b_id": candidate_b_id,
        "comparable_dimension_ids": shared_dimension_ids,
        "a_better_dimensions": a_better_dimensions,
        "b_better_dimensions": b_better_dimensions,
        "equal_dimensions": equal_dimensions,
        "incomparable_dimension_ids": incomparable_dimension_ids,
        "dominance_result": dominance_result,
        "explanation": explanation,
    }


def frontier_candidate_from_vector(
    vector: Mapping[str, Any],
) -> FrontierCandidate:
    comparable_dimensions, excluded_dimension_ids = comparable_dimensions_for_vector(vector)
    warnings = _string_list(deepcopy(vector.get("warnings")))
    if not comparable_dimensions:
        warnings.append("No comparable dimensions are available for frontier analysis.")

    return {
        "candidate_id": _as_string(vector.get("candidate_id"), "unknown_candidate"),
        "system_name": _as_string(vector.get("system_name"), "unknown_system"),
        "vector_status": _as_string(vector.get("vector_status"), "unknown"),
        "on_frontier": True,
        "dominated_by": [],
        "dominates": [],
        "comparable_dimensions": comparable_dimensions,
        "excluded_dimension_ids": excluded_dimension_ids,
        "warnings": warnings,
        "notes": [
            "This candidate is positioned by non-dominated trade-off comparison only.",
            "No score, rank, winner, qualification or certification decision is created.",
        ],
    }


def _summary(
    frontier_candidates: Sequence[FrontierCandidate],
    pairwise_comparisons: Sequence[PairwiseFrontierComparison],
) -> dict[str, Any]:
    by_vector_status: dict[str, int] = {}
    for candidate in frontier_candidates:
        status = _as_string(candidate.get("vector_status"), "unknown")
        by_vector_status[status] = by_vector_status.get(status, 0) + 1

    return {
        "frontier_candidate_ids": [
            candidate["candidate_id"]
            for candidate in frontier_candidates
            if candidate.get("on_frontier") is True
        ],
        "dominated_candidate_ids": [
            candidate["candidate_id"]
            for candidate in frontier_candidates
            if candidate.get("on_frontier") is False
        ],
        "by_vector_status": by_vector_status,
        "insufficient_comparison_count": sum(
            1
            for comparison in pairwise_comparisons
            if comparison.get("dominance_result") == "insufficient_comparable_dimensions"
        ),
    }


def build_pareto_frontier_from_vectors(
    vectors: Sequence[Mapping[str, Any]],
) -> ParetoFrontierRun:
    frontier_candidates = [
        frontier_candidate_from_vector(vector)
        for vector in vectors
    ]
    pairwise_comparisons: list[PairwiseFrontierComparison] = []

    for a_index, candidate_a in enumerate(frontier_candidates):
        for b_index in range(a_index + 1, len(frontier_candidates)):
            candidate_b = frontier_candidates[b_index]
            comparison = compare_frontier_candidates(candidate_a, candidate_b)
            pairwise_comparisons.append(comparison)
            if comparison["dominance_result"] == "a_dominates_b":
                candidate_a["dominates"].append(candidate_b["candidate_id"])
                candidate_b["dominated_by"].append(candidate_a["candidate_id"])
                candidate_b["on_frontier"] = False
            elif comparison["dominance_result"] == "b_dominates_a":
                candidate_b["dominates"].append(candidate_a["candidate_id"])
                candidate_a["dominated_by"].append(candidate_b["candidate_id"])
                candidate_a["on_frontier"] = False

    frontier_count = sum(
        1 for candidate in frontier_candidates if candidate.get("on_frontier") is True
    )
    dominated_count = len(frontier_candidates) - frontier_count
    warnings: list[str] = []
    if len(vectors) < 2:
        warnings.append("Fewer than two vectors supplied; pairwise frontier comparison is limited.")
    if any(
        comparison.get("dominance_result") == "insufficient_comparable_dimensions"
        for comparison in pairwise_comparisons
    ):
        warnings.append("One or more comparisons had insufficient comparable dimensions.")

    return {
        "candidate_count": len(vectors),
        "vector_count": len(vectors),
        "frontier_count": frontier_count,
        "dominated_count": dominated_count,
        "comparison_count": len(pairwise_comparisons),
        "research_mode_enabled": False,
        "frontier_candidates": frontier_candidates,
        "pairwise_comparisons": pairwise_comparisons,
        "frontier_summary": _summary(frontier_candidates, pairwise_comparisons),
        "notes": [
            "No single aggregate score was created.",
            "No winner was selected.",
            "Pareto/frontier position is decision support only.",
        ],
        "warnings": warnings,
    }


def run_pareto_frontier(
    candidates: Sequence[Mapping[str, Any]],
    *,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> ParetoFrontierRun:
    vector_run = run_tradeoff_vectors(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    frontier_run = build_pareto_frontier_from_vectors(vector_run.get("vectors", []))
    warnings = _string_list(deepcopy(vector_run.get("warnings")))
    warnings.extend(frontier_run.get("warnings", []))
    if research_mode_enabled:
        warnings.append("Research mode is enabled; frontier analysis may include exploratory vectors.")

    frontier_run["candidate_count"] = int(vector_run.get("candidate_count") or len(candidates))
    frontier_run["vector_count"] = int(vector_run.get("vector_count") or len(frontier_run["frontier_candidates"]))
    frontier_run["research_mode_enabled"] = research_mode_enabled
    frontier_run["warnings"] = warnings
    return frontier_run
