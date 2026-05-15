from src.controlled_shortlist import SHORTLIST_BUCKETS, build_controlled_shortlist


def _candidate(candidate_id, maturity="B", **overrides):
    candidate = {
        "candidate_id": candidate_id,
        "name": f"Candidate {candidate_id}",
        "candidate_class": "ceramic_matrix_composite",
        "architecture_path": "cmc_ebc_environmental_protection_path",
        "evidence_maturity": maturity,
        "surface_function_profile": {
            "primary_service_functions": [
                "oxidation_resistance",
                "environmental_barrier",
            ],
            "secondary_service_functions": [
                "thermal_cycling_tolerance",
            ],
            "surface_functions": [
                {"function_id": "oxidation_resistance", "function_kind": "primary_service_function"},
                {"function_id": "environmental_barrier", "function_kind": "primary_service_function"},
                {"function_id": "thermal_cycling_tolerance", "function_kind": "secondary_service_function"},
            ],
        },
        "environmental_barrier_coating": {"name": "rare-earth silicate EBC"},
        "inspection_plan": {"inspection_burden": "high"},
        "repairability": {"repairability_level": "moderate"},
        "qualification_route": {"qualification_burden": "very_high"},
    }
    candidate.update(overrides)
    return candidate


def _precomputed_candidate(
    candidate_id,
    maturity,
    fit_status,
    analysis_status,
    architecture_path="precomputed_path",
    required_evidence=None,
    cautions=None,
    suggested_actions=None,
):
    return {
        "candidate_id": candidate_id,
        "name": f"Candidate {candidate_id}",
        "candidate_class": "reference",
        "evidence_maturity": maturity,
        "application_requirement_fit": {
            "candidate_id": candidate_id,
            "profile_id": "hot_section_thermal_cycling_oxidation",
            "architecture_path": architecture_path,
            "fit_status": fit_status,
            "application_fit_status": fit_status,
            "validation_issues": [],
        },
        "application_limiting_factor_analysis": {
            "candidate_id": candidate_id,
            "profile_id": "hot_section_thermal_cycling_oxidation",
            "architecture_path": architecture_path,
            "fit_status": fit_status,
            "analysis_status": analysis_status,
            "cautions": cautions or [],
            "required_evidence": required_evidence or [],
            "suggested_actions": suggested_actions or ["review application evidence package"],
        },
    }


def _poor_fit_candidate(candidate_id="poor-fit"):
    return _candidate(
        candidate_id,
        maturity="B",
        candidate_class="coating_enabled",
        architecture_path="oxidation_protection_only_path",
        surface_function_profile={
            "primary_service_functions": ["oxidation_resistance"],
            "secondary_service_functions": ["thermal_cycling_tolerance"],
        },
    )


def _insufficient_candidate(candidate_id="insufficient"):
    return _precomputed_candidate(
        candidate_id,
        "unknown",
        "insufficient_information",
        "insufficient_information",
        architecture_path="unknown",
    )


def _package(with_application_layers=True):
    candidates = [
        _precomputed_candidate("near-1", "B", "plausible_with_validation", "analysed_for_application"),
        _precomputed_candidate(
            "validation-1",
            "C",
            "plausible_with_validation",
            "analysed_for_application",
            required_evidence=[{"required_item": "thermal_barrier"}],
        ),
        _precomputed_candidate(
            "validation-2",
            "C",
            "plausible_with_validation",
            "analysed_for_application",
            required_evidence=[{"required_item": "application_path_validation"}],
        ),
        _precomputed_candidate(
            "exploratory-1",
            "D",
            "exploratory_only_for_profile",
            "exploratory_context_only",
            cautions=["Low maturity application fit."],
            suggested_actions=["scope exploratory validation only"],
        ),
        _precomputed_candidate(
            "research-1",
            "F",
            "research_only_for_profile",
            "research_context_only",
            cautions=["Research maturity only."],
            suggested_actions=["monitor research evidence"],
        ),
        _precomputed_candidate(
            "poor-fit",
            "B",
            "poor_fit_for_profile",
            "poor_fit_suppressed",
            architecture_path="oxidation_protection_only_path",
            suggested_actions=["park for this profile"],
        ),
        _insufficient_candidate(),
    ]
    if not with_application_layers:
        candidates = [
            _candidate("validation-1", maturity="C"),
            _poor_fit_candidate(),
        ]
    return {
        "candidate_systems": candidates,
        "diagnostics": {"existing_diagnostic": "preserved"},
        "ranked_recommendations": [{"candidate_id": "preexisting-rank"}],
        "pareto_front": [{"candidate_id": "preexisting-pareto"}],
        "optimisation_summary": {
            "generated_candidate_count": 0,
            "live_model_calls_made": False,
        },
    }


def _bucket_ids(package, bucket):
    return [
        entry["candidate_id"]
        for entry in package["controlled_shortlist"]["buckets"][bucket]
    ]


def test_shortlist_buckets_contains_expected_buckets():
    assert SHORTLIST_BUCKETS == {
        "near_term_comparison_references",
        "validation_needed_options",
        "exploratory_context_only",
        "research_only_context",
        "poor_fit_for_profile",
        "insufficient_information",
    }


def test_build_controlled_shortlist_adds_shortlist_and_summary():
    package = build_controlled_shortlist(_package())

    assert package["controlled_shortlist"]["shortlist_status"] == "controlled_shortlist_created"
    assert package["controlled_shortlist_summary"]


def test_candidate_count_and_order_in_candidate_systems_are_unchanged():
    source = _package()
    package = build_controlled_shortlist(source)

    assert len(package["candidate_systems"]) == len(source["candidate_systems"])
    assert [candidate["candidate_id"] for candidate in package["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in source["candidate_systems"]
    ]


def test_application_layers_are_attached_if_missing():
    package = build_controlled_shortlist(_package(with_application_layers=False))

    assert all("application_requirement_fit" in candidate for candidate in package["candidate_systems"])
    assert all("application_limiting_factor_analysis" in candidate for candidate in package["candidate_systems"])


def test_plausible_mature_candidate_goes_to_near_term_comparison_references():
    package = build_controlled_shortlist(_package())

    assert _bucket_ids(package, "near_term_comparison_references") == ["near-1"]


def test_plausible_c_or_evidence_needed_candidate_goes_to_validation_needed_options():
    package = build_controlled_shortlist(_package())

    assert _bucket_ids(package, "validation_needed_options") == ["validation-1", "validation-2"]


def test_exploratory_research_poor_fit_and_insufficient_candidates_go_to_expected_buckets():
    package = build_controlled_shortlist(_package())

    assert _bucket_ids(package, "exploratory_context_only") == ["exploratory-1"]
    assert _bucket_ids(package, "research_only_context") == ["research-1"]
    assert _bucket_ids(package, "poor_fit_for_profile") == ["poor-fit"]
    assert _bucket_ids(package, "insufficient_information") == ["insufficient"]


def test_bucket_entries_preserve_source_order_within_bucket():
    package = build_controlled_shortlist(_package())

    assert _bucket_ids(package, "validation_needed_options") == ["validation-1", "validation-2"]


def test_bucket_entries_include_required_fields():
    package = build_controlled_shortlist(_package())
    entry = package["controlled_shortlist"]["buckets"]["validation_needed_options"][0]

    for key in (
        "candidate_id",
        "architecture_path",
        "fit_status",
        "analysis_status",
        "evidence_maturity",
        "rationale",
        "cautions",
        "required_evidence",
        "suggested_actions",
    ):
        assert key in entry


def test_existing_ranked_pareto_and_optimisation_outputs_remain_unchanged():
    source = _package()
    package = build_controlled_shortlist(source)

    assert package["ranked_recommendations"] == source["ranked_recommendations"]
    assert package["pareto_front"] == source["pareto_front"]
    assert package["optimisation_summary"] == source["optimisation_summary"]


def test_validation_plan_not_created_and_candidate_systems_not_filtered():
    source = _package()
    package = build_controlled_shortlist(source)

    assert "validation_plan" not in package
    assert len(package["candidate_systems"]) == len(source["candidate_systems"])


def test_no_generated_candidates_are_introduced():
    package = build_controlled_shortlist(_package())

    assert "generated_candidates" not in package
    assert package["controlled_shortlist_summary"]["generated_candidate_count"] == 0


def test_diagnostics_show_shortlist_created_without_ranking_or_filtering():
    package = build_controlled_shortlist(_package())

    assert package["diagnostics"]["existing_diagnostic"] == "preserved"
    assert package["diagnostics"]["controlled_shortlist_created"] is True
    assert package["diagnostics"]["controlled_shortlist_candidate_count"] == 7
    assert package["diagnostics"]["controlled_shortlist_candidate_order_preserved"] is True
    assert package["diagnostics"]["controlled_shortlist_ranking_performed"] is False
    assert package["diagnostics"]["controlled_shortlist_filtering_performed"] is False


def test_boundaries_state_shortlist_is_not_downstream_decision_output():
    package = build_controlled_shortlist(_package())

    assert package["controlled_shortlist"]["boundaries"] == {
        "is_ranking": False,
        "is_final_recommendation": False,
        "is_validation_plan": False,
        "implies_qualification_or_certification_approval": False,
    }


def test_summary_counts_match_fixture_bucket_counts():
    package = build_controlled_shortlist(_package())

    assert package["controlled_shortlist_summary"]["bucket_counts"] == {
        "near_term_comparison_references": 1,
        "validation_needed_options": 2,
        "exploratory_context_only": 1,
        "research_only_context": 1,
        "poor_fit_for_profile": 1,
        "insufficient_information": 1,
    }
    assert package["controlled_shortlist_summary"]["total_bucketed_candidate_count"] == 7


def test_summary_records_no_ranking_pareto_filtering_validation_plan_or_live_calls():
    summary = build_controlled_shortlist(_package())["controlled_shortlist_summary"]

    assert summary["ranking_performed"] is False
    assert summary["candidate_filtering_performed"] is False
    assert summary["pareto_analysis_performed"] is False
    assert summary["validation_plan_created"] is False
    assert summary["live_model_calls_made"] is False
