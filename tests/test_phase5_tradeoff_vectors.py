from copy import deepcopy

from src.tradeoff_vectors import (
    TRADEOFF_DIMENSION_IDS,
    build_dimension,
    build_tradeoff_vector_for_candidate,
    build_tradeoff_vector_from_candidate_trace,
    candidate_evidence_maturity,
    count_traces_with_badge,
    evidence_maturity_band,
    evidence_maturity_numeric,
    has_architecture_change,
    max_review_required_count,
    run_tradeoff_vectors,
    total_expected_benefit_count,
    total_introduced_risk_count,
)


def _candidate() -> dict:
    return {
        "candidate_id": "C-1",
        "system_name": "Nickel DED System",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
    }


def _trace(
    *,
    trace_id: str = "trace:1",
    status: str = "proposed_for_deterministic_review",
    badges: list[str] | None = None,
    evidence_maturity: str = "B",
    review_required: list[str] | None = None,
    introduced_risks: list[str] | None = None,
    expected_benefits: list[str] | None = None,
    change_summary: list[str] | None = None,
) -> dict:
    return {
        "trace_id": trace_id,
        "candidate_id": "C-1",
        "status": status,
        "refinement_operator": "add_oxidation_protection_coating",
        "before_state_summary": {"process_route_summary": ["DED"]},
        "proposed_after_state_summary": {"process_route_summary": ["DED"]},
        "ui_badges": badges
        if badges is not None
        else ["deterministic_review", "coating_refinement", "requires_review"],
        "evidence_maturity": evidence_maturity,
        "review_required": review_required if review_required is not None else ["review_a"],
        "introduced_risks": introduced_risks if introduced_risks is not None else ["risk_a"],
        "expected_benefits": expected_benefits
        if expected_benefits is not None
        else ["benefit_a"],
        "change_summary": change_summary
        if change_summary is not None
        else ["system_architecture_type changed from monolithic to coating_enabled."],
    }


def _candidate_trace(traces: list[dict]) -> dict:
    return {
        "candidate_id": "C-1",
        "system_name": "Nickel DED System",
        "limiting_factors": ["oxidation"],
        "trace_count": len(traces),
        "traces": traces,
        "warnings": [],
    }


def _dimension(vector: dict, dimension_id: str) -> dict:
    return [
        dimension
        for dimension in vector["dimensions"]
        if dimension["dimension_id"] == dimension_id
    ][0]


def test_evidence_maturity_numeric_maps_known_letters_and_unknown():
    assert evidence_maturity_numeric("A") == 6.0
    assert evidence_maturity_numeric("F") == 1.0
    assert evidence_maturity_numeric("unknown") is None


def test_evidence_maturity_numeric_is_case_insensitive():
    assert evidence_maturity_numeric("b") == 5.0
    assert evidence_maturity_numeric(" e ") == 2.0


def test_evidence_maturity_band_maps_known_letters_and_unknown():
    assert evidence_maturity_band("A") == "favourable"
    assert evidence_maturity_band("B") == "favourable"
    assert evidence_maturity_band("C") == "caution"
    assert evidence_maturity_band("D") == "caution"
    assert evidence_maturity_band("E") == "high_caution"
    assert evidence_maturity_band("F") == "high_caution"
    assert evidence_maturity_band("unknown") == "unknown"


def test_count_traces_with_badge_counts_coating_refinement_badges():
    traces = [
        _trace(badges=["coating_refinement"]),
        _trace(badges=["spatial_gradient_refinement"]),
        _trace(badges=["coating_refinement", "requires_review"]),
    ]

    assert count_traces_with_badge(traces, "coating_refinement") == 2


def test_max_review_required_count_returns_maximum_length():
    traces = [
        _trace(review_required=["a"]),
        _trace(review_required=["a", "b", "c"]),
        _trace(review_required=["a", "b"]),
    ]

    assert max_review_required_count(traces) == 3


def test_total_introduced_risk_count_sums_risks():
    traces = [
        _trace(introduced_risks=["a", "b"]),
        _trace(introduced_risks=[]),
        _trace(introduced_risks=["c"]),
    ]

    assert total_introduced_risk_count(traces) == 3


def test_total_expected_benefit_count_sums_benefits():
    traces = [
        _trace(expected_benefits=["a"]),
        _trace(expected_benefits=["b", "c"]),
    ]

    assert total_expected_benefit_count(traces) == 3


def test_has_architecture_change_detects_architecture_change_messages():
    traces = [
        _trace(change_summary=["No tracked before/after state changes were recorded."]),
        _trace(change_summary=["System_Architecture_Type changed from A to B."]),
    ]

    assert has_architecture_change(traces) is True


def test_candidate_evidence_maturity_returns_first_non_unknown_trace_maturity():
    candidate_trace = _candidate_trace(
        [
            _trace(evidence_maturity="unknown"),
            _trace(evidence_maturity="C"),
            _trace(evidence_maturity="A"),
        ]
    )

    assert candidate_evidence_maturity(candidate_trace) == "C"


def test_build_dimension_copies_evidence_refs_and_warnings():
    evidence_refs = ["trace:1"]
    warnings = ["review needed"]

    dimension = build_dimension(
        "evidence_maturity",
        label="Evidence maturity",
        raw_value="A",
        band="favourable",
        rationale="test",
        evidence_refs=evidence_refs,
        warnings=warnings,
    )
    evidence_refs.append("trace:2")
    warnings.append("changed")

    assert dimension["evidence_refs"] == ["trace:1"]
    assert dimension["warnings"] == ["review needed"]


def test_build_tradeoff_vector_from_candidate_trace_creates_dimensions_in_order():
    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([_trace()]))

    assert [dimension["dimension_id"] for dimension in vector["dimensions"]] == list(
        TRADEOFF_DIMENSION_IDS
    )


def test_build_tradeoff_vector_from_candidate_trace_returns_no_traces_status():
    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([]))

    assert vector["vector_status"] == "no_traces_available"
    assert vector["trace_count"] == 0


def test_build_tradeoff_vector_from_candidate_trace_returns_available_for_deterministic_traces():
    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([_trace()]))

    assert vector["vector_status"] == "tradeoff_vector_available"


def test_build_tradeoff_vector_from_candidate_trace_returns_research_mode_status():
    trace = _trace(
        status="research_mode_only",
        badges=["spatial_gradient_refinement", "research_mode_only", "requires_review"],
    )

    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([trace]))

    assert vector["vector_status"] == "research_mode_vector_available"
    assert any("Research-mode" in warning for warning in vector["warnings"])


def test_coating_dependency_dimension_is_caution_when_coating_traces_present():
    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([_trace()]))

    dimension = _dimension(vector, "coating_dependency")
    assert dimension["band"] == "caution"
    assert dimension["numeric_value"] == 1.0


def test_spatial_gradient_dependency_dimension_is_caution_when_gradient_traces_present():
    trace = _trace(badges=["spatial_gradient_refinement", "requires_review"])

    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([trace]))

    assert _dimension(vector, "spatial_gradient_dependency")["band"] == "caution"


def test_review_burden_dimension_is_high_caution_when_count_is_four_or_more():
    trace = _trace(review_required=["a", "b", "c", "d"])

    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([trace]))

    assert _dimension(vector, "review_burden")["band"] == "high_caution"


def test_expected_benefit_signal_dimension_is_favourable_when_count_is_three_or_more():
    trace = _trace(expected_benefits=["a", "b", "c"])

    vector = build_tradeoff_vector_from_candidate_trace(_candidate_trace([trace]))

    assert _dimension(vector, "expected_benefit_signal")["band"] == "favourable"


def test_build_tradeoff_vector_for_candidate_creates_dimensions_for_oxidation_case():
    vector = build_tradeoff_vector_for_candidate(
        _candidate(),
        limiting_factors=["oxidation"],
    )

    assert vector["candidate_id"] == "C-1"
    assert vector["dimension_count"] == len(TRADEOFF_DIMENSION_IDS)
    assert vector["trace_count"] == 2


def test_run_tradeoff_vectors_preserves_candidate_order():
    run = run_tradeoff_vectors(
        [
            {"candidate_id": "C-1", "limiting_factors": []},
            {"candidate_id": "C-2", "limiting_factors": []},
        ]
    )

    assert [vector["candidate_id"] for vector in run["vectors"]] == ["C-1", "C-2"]


def test_run_tradeoff_vectors_summary_includes_counts_by_status_and_band():
    run = run_tradeoff_vectors(
        [_candidate()],
        default_limiting_factors=["oxidation"],
    )

    summary = run["vector_summary"]
    assert summary["by_vector_status"]["tradeoff_vector_available"] == 1
    assert summary["by_dimension_band"]["caution"] >= 1
    assert summary["by_dimension_band"]["high_caution"] >= 1


def test_run_tradeoff_vectors_does_not_mutate_input_candidates():
    candidates = [_candidate()]
    candidates[0]["limiting_factors"] = ["oxidation"]
    original = deepcopy(candidates)

    run_tradeoff_vectors(candidates)

    assert candidates == original


def test_research_mode_enabled_true_adds_run_level_warning():
    run = run_tradeoff_vectors([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in run["warnings"])


def test_no_matching_limiting_factor_returns_no_trace_vector_with_ten_dimensions():
    vector = build_tradeoff_vector_for_candidate(
        _candidate(),
        limiting_factors=["unobtainium_shortage"],
    )

    assert vector["vector_status"] == "no_traces_available"
    assert vector["trace_count"] == 0
    assert vector["dimension_count"] == len(TRADEOFF_DIMENSION_IDS)
