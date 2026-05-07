import json

from src.coating_vs_gradient_diagnostics import attach_coating_vs_gradient_diagnostic
from src.decision_readiness import (
    attach_decision_readiness,
    classify_evidence_readiness,
    derive_candidate_readiness_constraints,
    determine_decision_readiness,
)
from src.optimisation.deterministic_optimizer import attach_deterministic_optimisation
from src.process_route_enrichment import attach_process_route_enrichment
from src.surface_function_model import attach_surface_function_profiles
from src.ui_view_models import package_to_json_safe_dict
from src.vertical_slices.ceramics_first import build_ceramics_first_candidate_package


def _candidate(**overrides):
    candidate = {
        "candidate_id": "candidate-1",
        "candidate_class": "coating_enabled",
        "system_architecture_type": "substrate_plus_coating",
        "system_name": "Candidate 1",
        "evidence_maturity": "C",
        "evidence_package": {"maturity": "C"},
        "process_route_template_id": "route",
        "process_route_details": {"route_id": "route"},
        "inspection_plan": {"inspection_burden": "medium"},
        "repairability": {"repairability_level": "moderate"},
        "qualification_route": {"qualification_burden": "medium"},
        "route_validation_gaps": [],
        "interfaces": [],
    }
    candidate.update(overrides)
    return candidate


def _package():
    package = build_ceramics_first_candidate_package()
    package = attach_process_route_enrichment(package)
    package = attach_surface_function_profiles(package)
    package = attach_deterministic_optimisation(package)
    package = attach_coating_vs_gradient_diagnostic(package)
    return attach_decision_readiness(package)


def test_classify_evidence_readiness_maps_a_to_f():
    assert classify_evidence_readiness("A")["base_readiness_category"] == "mature_reference"
    assert classify_evidence_readiness("B")["base_readiness_category"] == "strong_engineering_analogue"
    assert classify_evidence_readiness("C")["base_readiness_category"] == "caveated_engineering_option"
    assert classify_evidence_readiness("D")["base_readiness_category"] == "emerging_validation_needed"
    assert classify_evidence_readiness("E")["base_readiness_category"] == "exploratory_concept_only"
    assert classify_evidence_readiness("F")["base_readiness_category"] == "research_mode_only"
    assert classify_evidence_readiness(None)["base_readiness_category"] == "unknown_readiness"


def test_generated_candidate_flag_creates_blocking_research_constraint():
    constraints = derive_candidate_readiness_constraints(_candidate(generated_candidate_flag=True))

    assert any(item["category"] == "research_mode" and item["severity"] == "blocking" for item in constraints)


def test_route_burdens_create_certification_inspection_and_repairability_constraints():
    candidate = _candidate(
        qualification_route={"qualification_burden": "very_high"},
        inspection_plan={"inspection_burden": "high"},
        repairability={"repairability_level": "poor"},
    )

    constraints = derive_candidate_readiness_constraints(candidate)

    assert any(item["category"] == "certification" for item in constraints)
    assert any(item["category"] == "inspection" for item in constraints)
    assert any(item["category"] == "repairability" for item in constraints)


def test_determine_decision_readiness_does_not_upgrade_e_or_f_candidates():
    e_record = determine_decision_readiness(_candidate(evidence_maturity="E", evidence_package={"maturity": "E"}))
    f_record = determine_decision_readiness(_candidate(evidence_maturity="F", evidence_package={"maturity": "F"}))

    assert e_record["readiness_category"] == "exploratory_concept_only"
    assert e_record["readiness_status"] == "exploratory_only"
    assert f_record["readiness_category"] == "research_mode_only"
    assert f_record["readiness_status"] == "research_only"


def test_spatially_graded_d_e_f_remain_emerging_exploratory_or_research_only():
    for maturity, category in (
        ("D", "emerging_validation_needed"),
        ("E", "exploratory_concept_only"),
        ("F", "research_mode_only"),
    ):
        record = determine_decision_readiness(
            _candidate(
                candidate_class="spatially_graded_am",
                system_architecture_type="spatial_gradient",
                evidence_maturity=maturity,
                evidence_package={"maturity": maturity},
            )
        )
        assert record["readiness_category"] == category


def test_attach_decision_readiness_preserves_candidate_count_order_and_empty_decision_fields():
    package = _package()
    source = build_ceramics_first_candidate_package()

    assert [candidate["candidate_id"] for candidate in package["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in source["candidate_systems"]
    ]
    assert package["ranked_recommendations"] == []
    assert package["pareto_front"] == []
    assert all(candidate["decision_readiness"] for candidate in package["candidate_systems"])


def test_ceramics_first_readiness_contains_reference_and_exploratory_records():
    package = _package()
    summary = package["decision_readiness_summary"]

    assert (
        summary["readiness_category_counts"].get("strong_engineering_analogue", 0)
        + summary["readiness_category_counts"].get("mature_reference", 0)
        > 0
    )
    gradient_records = [
        candidate["decision_readiness"]
        for candidate in package["candidate_systems"]
        if candidate["candidate_class"] == "spatially_graded_am"
    ]
    assert any(record["readiness_status"] in {"exploratory_only", "research_only"} for record in gradient_records)


def test_decision_readiness_package_remains_json_safe():
    package = _package()

    json.dumps(package_to_json_safe_dict(package))
    assert package["optimisation_summary"]["generated_candidate_count"] == 0
    assert package["optimisation_summary"]["live_model_calls_made"] is False
