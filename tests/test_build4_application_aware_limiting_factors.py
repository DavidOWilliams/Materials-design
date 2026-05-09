import json

from src.application_profiles import get_default_application_profile
from src.optimisation.application_aware_limiting_factors import (
    attach_application_aware_limiting_factor_analysis,
    build_application_aware_limiting_factor_analysis,
    build_application_aware_limiting_factor_record,
)
from src.ui_view_models import package_to_json_safe_dict


def _candidate(candidate_id, fit_status, architecture_path, maturity="C", **extra):
    candidate = {
        "candidate_id": candidate_id,
        "name": candidate_id,
        "candidate_class": "coating_enabled",
        "evidence_maturity": maturity,
        "application_requirement_fit": {
            "candidate_id": candidate_id,
            "fit_status": fit_status,
            "architecture_path": architecture_path,
            "matched_required_primary_functions": ["thermal_barrier", "oxidation_resistance"]
            if fit_status != "poor_fit_for_profile"
            else [],
            "missing_required_primary_functions": []
            if fit_status != "poor_fit_for_profile"
            else ["thermal_barrier", "oxidation_resistance"],
            "critical_blockers": [],
            "major_cautions": [],
            "required_next_evidence": ["application-specific validation evidence"],
            "fit_rationale": ["test rationale"],
        },
        "process_route_profile": {
            "inspection_burden": "medium",
            "repairability_level": "moderate",
            "qualification_burden": "high",
        },
    }
    candidate.update(extra)
    return candidate


def test_plausible_tbc_candidate_is_analysed_for_application():
    candidate = _candidate(
        "tbc",
        "plausible_with_validation",
        "coated_metallic_tbc_path",
        coating_spallation_adhesion={
            "adhesion_or_spallation_risk": "high",
            "thermal_cycling_damage_risk": "high",
            "bond_coat_or_interface_dependency": "high",
        },
    )

    record = build_application_aware_limiting_factor_record(candidate, get_default_application_profile())

    assert record["analysis_status"] == "analysed_for_application"
    assert {"coating_spallation", "coating_thermal_cycling"} & set(record["top_application_limiting_factors"])
    assert any("coating" in item.lower() for item in record["suggested_validation_or_refinement_actions"])
    assert record["not_a_ranking"] is True
    assert record["no_variants_generated"] is True


def test_plausible_cmc_ebc_candidate_is_validation_dependent_not_poor_fit():
    candidate = _candidate(
        "cmc-ebc",
        "plausible_with_validation",
        "cmc_ebc_environmental_protection_path",
        candidate_class="ceramic_matrix_composite",
        application_requirement_fit={
            "fit_status": "plausible_with_validation",
            "architecture_path": "cmc_ebc_environmental_protection_path",
            "matched_required_primary_functions": [],
            "missing_required_primary_functions": ["thermal_barrier"],
            "critical_blockers": [],
            "major_cautions": ["Missing literal thermal_barrier is an architecture difference."],
            "required_next_evidence": ["steam recession evidence"],
        },
        cmc_ebc_environmental_durability={
            "ebc_dependency_risk": "high",
            "oxidation_recession_risk": "high",
            "interface_or_interphase_risk": "high",
        },
    )

    record = build_application_aware_limiting_factor_record(candidate, get_default_application_profile())

    assert record["analysis_status"] == "analysed_for_application"
    assert "cmc_ebc_recession" in record["top_application_limiting_factors"]
    assert any("ebc" in item.lower() for item in record["suggested_validation_or_refinement_actions"])
    assert record["application_fit_status"] == "plausible_with_validation"


def test_poor_fit_wear_candidate_suppresses_generic_optimisation():
    candidate = _candidate(
        "wear",
        "poor_fit_for_profile",
        "wear_or_erosion_path",
        coating_spallation_adhesion={"adhesion_or_spallation_risk": "high"},
        _deterministic_optimisation_trace={"candidate_id": "wear", "limiting_factor_count": 7},
    )

    record = build_application_aware_limiting_factor_record(candidate, get_default_application_profile())

    assert record["analysis_status"] == "poor_fit_suppressed"
    assert {"application_mismatch", "missing_required_function"} & set(record["top_application_limiting_factors"])
    assert any("erosion_wear_surface_component" in item for item in record["suggested_validation_or_refinement_actions"])
    assert record["suppressed_generic_factor_count"] == 7


def test_research_only_graded_am_is_context_only():
    candidate = _candidate(
        "gradient",
        "research_only_for_profile",
        "graded_am_research_path",
        maturity="F",
        candidate_class="spatially_graded_am",
        graded_am_transition_zone_risk={
            "transition_zone_complexity": "high",
            "residual_stress_risk": "high",
            "process_window_sensitivity": "high",
        },
    )

    record = build_application_aware_limiting_factor_record(candidate, get_default_application_profile())

    assert record["analysis_status"] == "research_context_only"
    assert {"graded_am_transition_zone", "graded_am_residual_stress", "evidence_maturity"} & set(
        record["top_application_limiting_factors"]
    )
    assert any("engineering selection" in item.lower() for item in record["suggested_validation_or_refinement_actions"])
    assert record["no_variants_generated"] is True


def test_exploratory_oxidation_gradient_remains_context_only():
    candidate = _candidate(
        "oxidation-gradient",
        "exploratory_only_for_profile",
        "graded_am_research_path",
        maturity="E",
        candidate_class="spatially_graded_am",
    )

    record = build_application_aware_limiting_factor_record(candidate, get_default_application_profile())

    assert record["analysis_status"] == "exploratory_context_only"
    assert any("before engineering use" in item.lower() for item in record["suggested_validation_or_refinement_actions"])


def test_attach_application_aware_analysis_preserves_order_and_boundaries():
    package = {
        "application_profile": get_default_application_profile(),
        "candidate_systems": [
            _candidate("a", "plausible_with_validation", "coated_metallic_tbc_path"),
            _candidate("b", "poor_fit_for_profile", "wear_or_erosion_path"),
        ],
        "optimisation_trace": [
            {"candidate_id": "a", "limiting_factor_count": 3},
            {"candidate_id": "b", "limiting_factor_count": 4},
        ],
        "ranked_recommendations": [{"candidate_id": "keep"}],
        "pareto_front": [{"candidate_id": "pareto"}],
    }

    attached = attach_application_aware_limiting_factor_analysis(package)

    assert [candidate["candidate_id"] for candidate in attached["candidate_systems"]] == ["a", "b"]
    assert "application_aware_limiting_factors" not in package["candidate_systems"][0]
    assert all("application_aware_limiting_factors" in candidate for candidate in attached["candidate_systems"])
    assert attached["ranked_recommendations"] == [{"candidate_id": "keep"}]
    assert attached["pareto_front"] == [{"candidate_id": "pareto"}]
    json.dumps(package_to_json_safe_dict(attached))


def test_application_aware_summary_includes_statuses_and_themes():
    package = {
        "application_profile": get_default_application_profile(),
        "candidate_systems": [
            _candidate("a", "plausible_with_validation", "coated_metallic_tbc_path"),
            _candidate("b", "poor_fit_for_profile", "wear_or_erosion_path"),
            _candidate("c", "research_only_for_profile", "graded_am_research_path", maturity="F"),
        ],
    }

    analysis = build_application_aware_limiting_factor_analysis(package)

    assert analysis["candidate_count"] == 3
    assert analysis["analysis_status_counts"]
    assert analysis["blocker_theme_counts"]
    assert analysis["no_ranking_applied"] is True
    assert analysis["no_variants_generated"] is True
    assert analysis["no_pareto_optimisation"] is True
