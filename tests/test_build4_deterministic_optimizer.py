from src.optimisation.deterministic_optimizer import (
    attach_deterministic_optimisation,
    build_candidate_optimisation_trace,
    build_coating_vs_gradient_comparison,
)
from src.optimisation.limiting_factors import identify_limiting_factors
from src.optimisation.limiting_factors import (
    classify_factor_score,
    dedupe_limiting_factors,
    normalise_factor_score,
)
from src.optimisation.refinement_operators import select_refinement_operators


def _candidate(candidate_id, candidate_class, **overrides):
    evidence = overrides.pop("evidence_package", {"maturity": overrides.pop("maturity", "C")})
    candidate = {
        "candidate_id": candidate_id,
        "candidate_class": candidate_class,
        "system_class": candidate_class,
        "system_architecture_type": overrides.pop("system_architecture_type", "bulk_material"),
        "system_name": candidate_id,
        "constituents": [],
        "factor_scores": [],
        "interfaces": [],
        "evidence_package": evidence,
        "evidence": evidence,
        "evidence_maturity": evidence.get("maturity", "C"),
        "processing_routes": [{"route_name": "known route"}],
        "ranked_recommendations": [],
        "pareto_front": [],
    }
    candidate.update(overrides)
    return candidate


def _package(candidates):
    return {
        "run_id": "deterministic-optimisation-test",
        "requirement_schema": {},
        "design_space": {"coating_vs_gradient_comparison_required": True},
        "candidate_systems": list(candidates),
        "ranked_recommendations": [],
        "pareto_front": [],
        "optimisation_summary": {"status": "not_implemented"},
        "warnings": [],
        "diagnostics": {"live_model_calls_made": False},
    }


def test_identify_limiting_factors_finds_low_evidence_maturity_limitations():
    candidate = _candidate("low-evidence", "ceramic_matrix_composite", maturity="E")

    factors = identify_limiting_factors(candidate)

    assert any(factor["namespace"] == "evidence" for factor in factors)
    assert any(factor["severity"] == "high" for factor in factors)
    assert any(factor["category"] == "evidence_maturity" for factor in factors)


def test_normalise_factor_score_supports_fraction_and_percent_scales():
    assert normalise_factor_score(0.82) == 82.0
    assert normalise_factor_score(82) == 82.0
    assert normalise_factor_score(None) is None
    assert normalise_factor_score("not numeric") is None


def test_factor_score_classification_uses_calibrated_thresholds():
    assert classify_factor_score(0.82)["is_limiting"] is False
    assert classify_factor_score(82)["is_limiting"] is False
    assert classify_factor_score(0.28)["severity"] == "high"
    assert classify_factor_score(28)["severity"] == "high"
    assert classify_factor_score(0.45)["severity"] == "medium"
    assert classify_factor_score(45)["severity"] == "medium"


def test_high_scores_do_not_create_hard_limits_by_score_alone():
    candidate = _candidate(
        "strong-score",
        "monolithic_ceramic",
        factor_scores=[{"factor": "thermal.temperature", "score": 0.82}],
    )

    factors = identify_limiting_factors(candidate)

    assert not any(
        factor["factor"] == "thermal.temperature" and factor["category"] == "hard_limit"
        for factor in factors
    )


def test_low_scores_create_high_hard_limits_with_normalised_score():
    candidate = _candidate(
        "low-score",
        "coating_enabled",
        factor_scores=[{"factor": "thermal.temperature", "score": 0.28}],
    )

    factors = identify_limiting_factors(candidate)
    score_factor = next(factor for factor in factors if factor["factor"] == "thermal.temperature")

    assert score_factor["severity"] == "high"
    assert score_factor["category"] == "hard_limit"
    assert score_factor["normalised_score"] == 28.0


def test_medium_scores_create_medium_hard_limits_with_normalised_score():
    candidate = _candidate(
        "medium-score",
        "coating_enabled",
        factor_scores=[{"factor": "thermal.temperature", "score": 45}],
    )

    factors = identify_limiting_factors(candidate)
    score_factor = next(factor for factor in factors if factor["factor"] == "thermal.temperature")

    assert score_factor["severity"] == "medium"
    assert score_factor["category"] == "hard_limit"
    assert score_factor["normalised_score"] == 45.0


def test_dedupe_limiting_factors_removes_repeated_warnings_and_keeps_severe_record():
    factors = [
        {
            "candidate_id": "c1",
            "namespace": "process",
            "factor": "process.warning",
            "category": "advisory_warning",
            "severity": "medium",
            "reason": "repeat",
            "related_warnings": ["a"],
            "dedupe_key": "same",
        },
        {
            "candidate_id": "c1",
            "namespace": "process",
            "factor": "process.warning",
            "category": "advisory_warning",
            "severity": "high",
            "reason": "repeat",
            "related_warnings": ["a", "b"],
            "dedupe_key": "same",
        },
    ]

    deduped = dedupe_limiting_factors(factors)

    assert len(deduped) == 1
    assert deduped[0]["severity"] == "high"
    assert deduped[0]["related_warnings"] == ["a", "b"]


def test_coating_enabled_candidate_gets_coating_and_interface_limiting_factors():
    candidate = _candidate(
        "coating-1",
        "coating_enabled",
        system_architecture_type="substrate_plus_coating",
        coating_or_surface_system={
            "coating_type": "thermal_barrier_coating",
            "failure_modes": ["spallation", "CTE mismatch"],
        },
        interfaces=[
            {
                "interface_type": "substrate_coating",
                "risk_level": "medium",
                "reason": "Substrate/coating compatibility review.",
            }
        ],
    )

    factors = identify_limiting_factors(candidate)
    namespaces = {factor["namespace"] for factor in factors}

    assert "coating" in namespaces
    assert "interface" in namespaces


def test_spatially_graded_am_candidate_gets_transition_and_maturity_limiting_factors():
    candidate = _candidate(
        "graded-1",
        "spatially_graded_am",
        maturity="F",
        system_architecture_type="spatial_gradient",
        gradient_architecture={
            "gradient_types": ["composition"],
            "transition_risks": ["cracking", "process-window sensitivity"],
        },
    )

    factors = identify_limiting_factors(candidate)
    text = " ".join(factor["factor"] for factor in factors)

    assert "transition_zone_risk" in text
    assert any(factor["namespace"] == "evidence" for factor in factors)


def test_monolithic_ceramic_candidate_gets_brittleness_or_proof_testing_limit():
    candidate = _candidate("ceramic-1", "monolithic_ceramic")

    factors = identify_limiting_factors(candidate)
    text = " ".join(factor["reason"].lower() for factor in factors)

    assert "brittleness" in text or "proof-testing" in text


def test_select_refinement_operators_suggests_coating_or_gradient_for_surface_limits():
    candidate = _candidate("surface-limit", "monolithic_ceramic")
    limiting_factors = [
        {
            "factor": "environment.oxidation_steam_recession",
            "namespace": "environment",
            "severity": "medium",
            "reason": "Oxidation, steam and recession risk is limiting.",
            "candidate_id": "surface-limit",
            "candidate_class": "monolithic_ceramic",
            "evidence_maturity": "C",
            "related_warnings": [],
        }
    ]

    operators = select_refinement_operators(candidate, limiting_factors)
    operator_types = {operator["operator_type"] for operator in operators}

    assert "add_or_refine_environmental_barrier_coating" in operator_types
    assert "add_near_surface_oxidation_gradient" in operator_types


def test_select_refinement_operators_suggests_downgrade_and_additional_evidence_for_low_maturity():
    candidate = _candidate(
        "exploratory",
        "spatially_graded_am",
        maturity="F",
        system_architecture_type="spatial_gradient",
    )
    limiting_factors = identify_limiting_factors(candidate)

    operators = select_refinement_operators(candidate, limiting_factors)
    operator_types = {operator["operator_type"] for operator in operators}

    assert "downgrade_to_exploratory_research_option" in operator_types
    assert "require_additional_evidence_before_recommendation" in operator_types
    assert all(operator["generated_candidate_flag"] is False for operator in operators)
    assert all(operator["research_mode_required"] is False for operator in operators)


def test_build_candidate_optimisation_trace_contains_limiting_factors_and_refinement_options():
    candidate = _candidate(
        "trace-candidate",
        "coating_enabled",
        system_architecture_type="substrate_plus_coating",
        coating_or_surface_system={"failure_modes": ["spallation"]},
    )

    trace = build_candidate_optimisation_trace(candidate)

    assert trace["status"] == "analysed_no_variants_generated"
    assert trace["limiting_factors"]
    assert trace["limiting_factors_full"]
    assert trace["limiting_factor_count"] == len(trace["limiting_factors_full"])
    assert trace["displayed_limiting_factor_count"] == len(trace["limiting_factors"])
    assert len(trace["limiting_factors"]) <= 8
    assert trace["refinement_options"]
    assert trace["refinement_options_full"]
    assert len(trace["refinement_options"]) <= 6
    assert trace["variants_generated"] == []
    assert trace["before_after_deltas"] == []


def test_attach_deterministic_optimisation_preserves_candidate_count_and_order():
    candidates = [
        _candidate("coating-1", "coating_enabled", system_architecture_type="substrate_plus_coating"),
        _candidate("graded-1", "spatially_graded_am", system_architecture_type="spatial_gradient", maturity="E"),
    ]
    package = _package(candidates)

    optimised = attach_deterministic_optimisation(package)

    assert len(optimised["candidate_systems"]) == len(package["candidate_systems"])
    assert [candidate["candidate_id"] for candidate in optimised["candidate_systems"]] == [
        "coating-1",
        "graded-1",
    ]


def test_attach_deterministic_optimisation_does_not_populate_ranking_or_pareto():
    package = _package([_candidate("candidate-1", "monolithic_ceramic")])

    optimised = attach_deterministic_optimisation(package)

    assert optimised["ranked_recommendations"] == []
    assert optimised["pareto_front"] == []


def test_coating_vs_gradient_comparison_present_when_both_architecture_types_exist():
    candidates = [
        _candidate("coating-1", "coating_enabled", system_architecture_type="substrate_plus_coating"),
        _candidate("graded-1", "spatially_graded_am", system_architecture_type="spatial_gradient"),
    ]

    comparison = build_coating_vs_gradient_comparison(candidates, _package(candidates))

    assert comparison["comparison_required"] is True
    assert comparison["coating_enabled_candidate_ids"] == ["coating-1"]
    assert comparison["spatial_gradient_candidate_ids"] == ["graded-1"]
    assert comparison["comparison_notes"]


def test_generated_candidate_count_zero_and_live_model_calls_false():
    package = _package([_candidate("graded-1", "spatially_graded_am", system_architecture_type="spatial_gradient")])

    optimised = attach_deterministic_optimisation(package)

    assert optimised["optimisation_summary"]["generated_candidate_count"] == 0
    assert optimised["optimisation_summary"]["live_model_calls_made"] is False
    assert optimised["diagnostics"]["live_model_calls_made"] is False


def test_enriched_route_fields_create_limiting_factors_without_generating_variants():
    candidate = _candidate(
        "route-limited",
        "spatially_graded_am",
        system_architecture_type="spatial_gradient",
        inspection_plan={"inspection_burden": "high", "inspection_challenges": ["through-depth inspection"]},
        repairability={"repairability_level": "limited", "repair_constraints": ["gradient repair route unclear"]},
        qualification_route={"qualification_burden": "very_high", "qualification_notes": ["route evidence needed"]},
        route_risks=["transition-zone cracking"],
        route_validation_gaps=["through-depth inspection method"],
    )

    trace = build_candidate_optimisation_trace(candidate)
    factors = {factor["factor"] for factor in trace["limiting_factors"]}

    assert "inspection.high_route_inspection_burden" in factors
    assert "repairability.limited_or_poor_route_repairability" in factors
    assert "certification.high_route_qualification_burden" in factors
    assert trace["certification_limit_count"] >= 1
    assert trace["route_risk_count"] >= 1
    assert trace["variants_generated"] == []


def test_no_candidates_are_filtered_out():
    candidates = [
        _candidate("ceramic-1", "monolithic_ceramic"),
        _candidate("cmc-1", "ceramic_matrix_composite"),
        _candidate("coating-1", "coating_enabled", system_architecture_type="substrate_plus_coating"),
    ]
    package = _package(candidates)

    optimised = attach_deterministic_optimisation(package)

    assert len(optimised["candidate_systems"]) == 3
    assert optimised["optimisation_summary"]["candidate_count"] == 3
    assert optimised["optimisation_summary"]["generated_candidate_count"] == 0
    assert optimised["optimisation_summary"]["live_model_calls_made"] is False
