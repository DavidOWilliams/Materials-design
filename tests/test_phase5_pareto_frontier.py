from copy import deepcopy

from src.pareto_frontier import (
    build_pareto_frontier_from_vectors,
    comparable_dimension_from_tradeoff_dimension,
    comparable_dimensions_for_vector,
    compare_frontier_candidates,
    frontier_candidate_from_vector,
    run_pareto_frontier,
)


def _dimension(
    dimension_id: str,
    numeric_value,
    direction: str,
    raw_value: str | None = None,
) -> dict:
    return {
        "dimension_id": dimension_id,
        "raw_value": raw_value if raw_value is not None else str(numeric_value),
        "numeric_value": numeric_value,
        "direction": direction,
        "rationale": f"{dimension_id} rationale",
    }


def _vector(candidate_id: str, dimensions: list[dict]) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"System {candidate_id}",
        "vector_status": "tradeoff_vector_available",
        "dimensions": dimensions,
        "warnings": [],
    }


def _frontier_candidate(candidate_id: str, dimensions: list[dict]) -> dict:
    return frontier_candidate_from_vector(_vector(candidate_id, dimensions))


def _candidate(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"Nickel DED System {candidate_id}",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "limiting_factors": [],
    }


def test_comparable_dimension_returns_none_when_numeric_value_missing():
    assert comparable_dimension_from_tradeoff_dimension(
        {"dimension_id": "evidence_maturity", "direction": "higher_is_better"}
    ) is None


def test_comparable_dimension_returns_none_for_contextual_direction():
    assert comparable_dimension_from_tradeoff_dimension(
        _dimension("certification_caution", 1.0, "contextual")
    ) is None


def test_comparable_dimension_keeps_higher_is_better_positive():
    comparable = comparable_dimension_from_tradeoff_dimension(
        _dimension("evidence_maturity", 4.0, "higher_is_better")
    )

    assert comparable["comparable_value"] == 4.0


def test_comparable_dimension_negates_lower_is_better_value():
    comparable = comparable_dimension_from_tradeoff_dimension(
        _dimension("review_burden", 4.0, "lower_is_better")
    )

    assert comparable["comparable_value"] == -4.0


def test_comparable_dimensions_for_vector_returns_comparable_and_excluded_ids():
    vector = _vector(
        "A",
        [
            _dimension("evidence_maturity", 5.0, "higher_is_better"),
            _dimension("certification_caution", None, "lower_is_better"),
            _dimension("narrative", 1.0, "contextual"),
        ],
    )

    comparable, excluded = comparable_dimensions_for_vector(vector)

    assert [dimension["dimension_id"] for dimension in comparable] == ["evidence_maturity"]
    assert excluded == ["certification_caution", "narrative"]


def test_compare_frontier_candidates_returns_a_dominates_b():
    candidate_a = _frontier_candidate(
        "A",
        [
            _dimension("evidence_maturity", 5.0, "higher_is_better"),
            _dimension("review_burden", 1.0, "lower_is_better"),
        ],
    )
    candidate_b = _frontier_candidate(
        "B",
        [
            _dimension("evidence_maturity", 4.0, "higher_is_better"),
            _dimension("review_burden", 1.0, "lower_is_better"),
        ],
    )

    comparison = compare_frontier_candidates(candidate_a, candidate_b)

    assert comparison["dominance_result"] == "a_dominates_b"
    assert comparison["a_better_dimensions"] == ["evidence_maturity"]


def test_compare_frontier_candidates_returns_b_dominates_a():
    candidate_a = _frontier_candidate(
        "A",
        [_dimension("review_burden", 4.0, "lower_is_better")],
    )
    candidate_b = _frontier_candidate(
        "B",
        [_dimension("review_burden", 2.0, "lower_is_better")],
    )

    comparison = compare_frontier_candidates(candidate_a, candidate_b)

    assert comparison["dominance_result"] == "b_dominates_a"
    assert comparison["b_better_dimensions"] == ["review_burden"]


def test_compare_frontier_candidates_returns_neither_when_each_is_better():
    candidate_a = _frontier_candidate(
        "A",
        [
            _dimension("evidence_maturity", 6.0, "higher_is_better"),
            _dimension("review_burden", 5.0, "lower_is_better"),
        ],
    )
    candidate_b = _frontier_candidate(
        "B",
        [
            _dimension("evidence_maturity", 4.0, "higher_is_better"),
            _dimension("review_burden", 1.0, "lower_is_better"),
        ],
    )

    comparison = compare_frontier_candidates(candidate_a, candidate_b)

    assert comparison["dominance_result"] == "neither_dominates"


def test_compare_frontier_candidates_returns_insufficient_when_no_shared_dimensions():
    candidate_a = _frontier_candidate(
        "A",
        [_dimension("evidence_maturity", 6.0, "higher_is_better")],
    )
    candidate_b = _frontier_candidate(
        "B",
        [_dimension("review_burden", 1.0, "lower_is_better")],
    )

    comparison = compare_frontier_candidates(candidate_a, candidate_b)

    assert comparison["dominance_result"] == "insufficient_comparable_dimensions"


def test_frontier_candidate_from_vector_starts_on_frontier_with_empty_links():
    candidate = frontier_candidate_from_vector(
        _vector("A", [_dimension("evidence_maturity", 6.0, "higher_is_better")])
    )

    assert candidate["on_frontier"] is True
    assert candidate["dominated_by"] == []
    assert candidate["dominates"] == []


def test_frontier_candidate_from_vector_warns_when_no_comparable_dimensions_exist():
    candidate = frontier_candidate_from_vector(
        _vector("A", [_dimension("narrative", 1.0, "contextual")])
    )

    assert any("No comparable dimensions" in warning for warning in candidate["warnings"])


def test_build_pareto_frontier_from_vectors_preserves_input_candidate_order():
    vectors = [
        _vector("B", [_dimension("evidence_maturity", 4.0, "higher_is_better")]),
        _vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")]),
    ]

    run = build_pareto_frontier_from_vectors(vectors)

    assert [candidate["candidate_id"] for candidate in run["frontier_candidates"]] == ["B", "A"]


def test_build_pareto_frontier_from_vectors_marks_dominated_candidate():
    vectors = [
        _vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")]),
        _vector("B", [_dimension("evidence_maturity", 4.0, "higher_is_better")]),
    ]

    run = build_pareto_frontier_from_vectors(vectors)
    candidate_b = run["frontier_candidates"][1]

    assert candidate_b["on_frontier"] is False
    assert candidate_b["dominated_by"] == ["A"]


def test_build_pareto_frontier_from_vectors_leaves_non_dominated_candidates_on_frontier():
    vectors = [
        _vector(
            "A",
            [
                _dimension("evidence_maturity", 6.0, "higher_is_better"),
                _dimension("review_burden", 5.0, "lower_is_better"),
            ],
        ),
        _vector(
            "B",
            [
                _dimension("evidence_maturity", 4.0, "higher_is_better"),
                _dimension("review_burden", 1.0, "lower_is_better"),
            ],
        ),
    ]

    run = build_pareto_frontier_from_vectors(vectors)

    assert [candidate["on_frontier"] for candidate in run["frontier_candidates"]] == [
        True,
        True,
    ]


def test_build_pareto_frontier_from_vectors_has_no_score_rank_or_winner_fields():
    run = build_pareto_frontier_from_vectors(
        [_vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")])]
    )

    assert "score" not in run
    assert "rank" not in run
    assert "winner" not in run
    for candidate in run["frontier_candidates"]:
        assert "score" not in candidate
        assert "rank" not in candidate
        assert "winner" not in candidate


def test_build_pareto_frontier_from_vectors_summary_includes_frontier_and_dominated_ids():
    run = build_pareto_frontier_from_vectors(
        [
            _vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")]),
            _vector("B", [_dimension("evidence_maturity", 4.0, "higher_is_better")]),
        ]
    )

    assert run["frontier_summary"]["frontier_candidate_ids"] == ["A"]
    assert run["frontier_summary"]["dominated_candidate_ids"] == ["B"]


def test_build_pareto_frontier_from_vectors_warns_when_fewer_than_two_vectors():
    run = build_pareto_frontier_from_vectors(
        [_vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")])]
    )

    assert any("Fewer than two vectors" in warning for warning in run["warnings"])


def test_build_pareto_frontier_from_vectors_warns_for_insufficient_dimensions():
    run = build_pareto_frontier_from_vectors(
        [
            _vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")]),
            _vector("B", [_dimension("review_burden", 1.0, "lower_is_better")]),
        ]
    )

    assert any("insufficient comparable dimensions" in warning for warning in run["warnings"])


def test_build_pareto_frontier_from_vectors_does_not_mutate_input_vectors():
    vectors = [
        _vector("A", [_dimension("evidence_maturity", 5.0, "higher_is_better")]),
        _vector("B", [_dimension("evidence_maturity", 4.0, "higher_is_better")]),
    ]
    original = deepcopy(vectors)

    build_pareto_frontier_from_vectors(vectors)

    assert vectors == original


def test_run_pareto_frontier_preserves_candidate_order():
    run = run_pareto_frontier([_candidate("C-1"), _candidate("C-2")])

    assert [candidate["candidate_id"] for candidate in run["frontier_candidates"]] == [
        "C-1",
        "C-2",
    ]


def test_run_pareto_frontier_includes_research_mode_warning_when_enabled():
    run = run_pareto_frontier([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_run_pareto_frontier_does_not_mutate_input_candidates():
    candidates = [_candidate("C-1"), _candidate("C-2")]
    original = deepcopy(candidates)

    run_pareto_frontier(candidates)

    assert candidates == original


def test_run_pareto_frontier_returns_frontier_count_and_comparison_count():
    run = run_pareto_frontier([_candidate("C-1"), _candidate("C-2")])

    assert run["frontier_count"] == 2
    assert run["comparison_count"] == 1


def test_build_pareto_frontier_from_vectors_handles_empty_vector_list():
    run = build_pareto_frontier_from_vectors([])

    assert run["frontier_count"] == 0
    assert run["dominated_count"] == 0
    assert run["comparison_count"] == 0
    assert run["frontier_candidates"] == []
