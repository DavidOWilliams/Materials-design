from src.validation_plan import VALIDATION_PLAN_CATEGORIES, build_validation_plan


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


def _precomputed_candidate(candidate_id, maturity, fit_status, analysis_status, architecture_path="precomputed_path", required_evidence=None, cautions=None):
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
            "suggested_actions": ["review application evidence package"],
        },
    }


def _insufficient_candidate():
    return _precomputed_candidate(
        "insufficient",
        "unknown",
        "insufficient_information",
        "insufficient_information",
        architecture_path="unknown",
    )


def _package(with_layers=True):
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
            "exploratory-1",
            "D",
            "exploratory_only_for_profile",
            "exploratory_context_only",
            cautions=["Low maturity application fit."],
        ),
        _precomputed_candidate(
            "research-1",
            "F",
            "research_only_for_profile",
            "research_context_only",
            cautions=["Research maturity only."],
        ),
        _precomputed_candidate(
            "poor-fit",
            "B",
            "poor_fit_for_profile",
            "poor_fit_suppressed",
            architecture_path="oxidation_protection_only_path",
        ),
        _insufficient_candidate(),
    ]
    if not with_layers:
        candidates = [
            _candidate("validation-1", maturity="C"),
            _candidate(
                "poor-fit",
                maturity="B",
                candidate_class="coating_enabled",
                architecture_path="oxidation_protection_only_path",
                surface_function_profile={
                    "primary_service_functions": ["oxidation_resistance"],
                    "secondary_service_functions": ["thermal_cycling_tolerance"],
                },
            ),
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


def _entry_by_id(package, candidate_id):
    return next(entry for entry in package["validation_plan"]["entries"] if entry["candidate_id"] == candidate_id)


def test_validation_plan_categories_contains_expected_categories():
    assert VALIDATION_PLAN_CATEGORIES == {
        "baseline_reference_validation",
        "validation_required_before_engineering_use",
        "exploratory_validation_only",
        "research_validation_only",
        "parked_no_validation_for_this_profile",
        "insufficient_information",
    }


def test_build_validation_plan_adds_plan_and_summary():
    package = build_validation_plan(_package())

    assert package["validation_plan"]["validation_plan_status"] == "validation_plan_created"
    assert package["validation_plan_summary"]


def test_candidate_count_and_order_are_unchanged():
    source = _package()
    package = build_validation_plan(source)

    assert len(package["candidate_systems"]) == len(source["candidate_systems"])
    assert [candidate["candidate_id"] for candidate in package["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in source["candidate_systems"]
    ]


def test_application_layers_and_controlled_shortlist_are_created_if_missing():
    package = build_validation_plan(_package(with_layers=False))

    assert all("application_requirement_fit" in candidate for candidate in package["candidate_systems"])
    assert all("application_limiting_factor_analysis" in candidate for candidate in package["candidate_systems"])
    assert package["controlled_shortlist"]["shortlist_status"] == "controlled_shortlist_created"


def test_controlled_shortlist_buckets_map_to_validation_categories():
    package = build_validation_plan(_package())

    assert _entry_by_id(package, "near-1")["validation_category"] == "baseline_reference_validation"
    assert _entry_by_id(package, "validation-1")["validation_category"] == "validation_required_before_engineering_use"
    assert _entry_by_id(package, "exploratory-1")["validation_category"] == "exploratory_validation_only"
    assert _entry_by_id(package, "research-1")["validation_category"] == "research_validation_only"
    assert _entry_by_id(package, "poor-fit")["validation_category"] == "parked_no_validation_for_this_profile"
    assert _entry_by_id(package, "insufficient")["validation_category"] == "insufficient_information"


def test_validation_entries_include_required_fields():
    entry = _entry_by_id(build_validation_plan(_package()), "validation-1")

    for key in (
        "candidate_id",
        "architecture_path",
        "fit_status",
        "analysis_status",
        "controlled_shortlist_bucket",
        "validation_category",
        "evidence_maturity",
        "validation_objectives",
        "required_evidence",
        "suggested_validation_activities",
        "cautions",
        "boundaries",
    ):
        assert key in entry


def test_validation_plan_boundaries_exclude_approval_ranking_and_final_recommendations():
    package = build_validation_plan(_package())

    assert package["validation_plan"]["boundaries"] == {
        "is_qualification_approval": False,
        "is_certification_approval": False,
        "is_final_recommendation": False,
        "is_ranking": False,
        "creates_candidate_variants": False,
    }


def test_existing_ranked_pareto_and_optimisation_outputs_remain_unchanged():
    source = _package()
    package = build_validation_plan(source)

    assert package["ranked_recommendations"] == source["ranked_recommendations"]
    assert package["pareto_front"] == source["pareto_front"]
    assert package["optimisation_summary"] == source["optimisation_summary"]


def test_candidate_systems_are_not_filtered_and_no_generated_candidates_are_introduced():
    source = _package()
    package = build_validation_plan(source)

    assert len(package["candidate_systems"]) == len(source["candidate_systems"])
    assert "generated_candidates" not in package
    assert package["validation_plan_summary"]["generated_candidate_count"] == 0


def test_diagnostics_show_validation_plan_created_without_ranking_filtering_or_approval():
    package = build_validation_plan(_package())

    assert package["diagnostics"]["existing_diagnostic"] == "preserved"
    assert package["diagnostics"]["validation_plan_created"] is True
    assert package["diagnostics"]["validation_plan_candidate_count"] == 6
    assert package["diagnostics"]["validation_plan_candidate_order_preserved"] is True
    assert package["diagnostics"]["validation_plan_ranking_performed"] is False
    assert package["diagnostics"]["validation_plan_filtering_performed"] is False
    assert package["diagnostics"]["validation_plan_certification_approval"] is False
    assert package["diagnostics"]["validation_plan_qualification_approval"] is False


def test_validation_summary_counts_match_fixture():
    summary = build_validation_plan(_package())["validation_plan_summary"]

    assert summary["validation_category_counts"] == {
        "baseline_reference_validation": 1,
        "validation_required_before_engineering_use": 1,
        "exploratory_validation_only": 1,
        "research_validation_only": 1,
        "parked_no_validation_for_this_profile": 1,
        "insufficient_information": 1,
    }
    assert summary["total_validation_entries"] == 6


def test_summary_records_no_downstream_decision_or_approval_outputs():
    summary = build_validation_plan(_package())["validation_plan_summary"]

    assert summary["ranking_performed"] is False
    assert summary["candidate_filtering_performed"] is False
    assert summary["pareto_analysis_performed"] is False
    assert summary["live_model_calls_made"] is False
    assert summary["qualification_approval_granted"] is False
    assert summary["certification_approval_granted"] is False
