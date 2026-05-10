import copy
import json

from src.validation_plan import (
    attach_validation_plan,
    build_candidate_validation_plan_record,
    build_validation_plan,
)


def _candidate(candidate_id, bucket, architecture_path, maturity="C"):
    return {
        "candidate_id": candidate_id,
        "system_name": candidate_id.replace("_", " ").title(),
        "candidate_class": "material_system",
        "evidence_package": {"maturity": maturity},
        "application_requirement_fit": {
            "fit_status": "plausible_with_validation",
            "architecture_path": architecture_path,
        },
        "application_aware_limiting_factors": {
            "application_fit_status": "plausible_with_validation",
            "analysis_status": "analysed_for_application",
            "architecture_path": architecture_path,
        },
        "controlled_shortlist_record": {
            "candidate_id": candidate_id,
            "system_name": candidate_id.replace("_", " ").title(),
            "candidate_class": "material_system",
            "evidence_maturity": maturity,
            "shortlist_bucket": bucket,
            "application_fit_status": "plausible_with_validation",
            "application_analysis_status": "analysed_for_application",
            "architecture_path": architecture_path,
            "required_next_evidence": ["existing evidence gap"],
            "suggested_next_actions": ["existing suggested action"],
            "key_blockers": [],
            "key_cautions": [],
        },
    }


def _text(record, *fields):
    values = []
    for field in fields:
        value = record.get(field)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return " ".join(values).lower()


def test_near_term_tbc_reference_validation_plan():
    record = build_candidate_validation_plan_record(
        _candidate("tbc_reference", "near_term_comparison_references", "coated_metallic_tbc_path", "B")
    )

    assert record["validation_plan_status"] == "baseline_reference_validation"
    text = _text(record, "required_validation_activities", "interface_validation_items", "mechanical_or_thermal_validation_items")
    assert "adhesion" in text
    assert "spallation" in text
    assert "thermal-cycle" in text
    assert record["not_certification_approval"] is True
    assert record["no_ranking_applied"] is True
    assert record["no_selection_made"] is True


def test_near_term_cmc_ebc_reference_validation_plan():
    record = build_candidate_validation_plan_record(
        _candidate(
            "sic_sic_cmc_ebc_anchor",
            "near_term_comparison_references",
            "cmc_ebc_environmental_protection_path",
            "B",
        )
    )

    assert record["validation_plan_status"] == "baseline_reference_validation"
    text = _text(
        record,
        "required_validation_activities",
        "inspection_and_ndi_plan_items",
        "repair_and_disposition_plan_items",
        "environmental_exposure_validation_items",
    )
    assert "ebc recession" in text
    assert "environmental durability" in text
    assert "ndi acceptance criteria" in text
    assert "repair" in text
    assert record["validation_plan_status"] != "parked_no_validation_for_this_profile"


def test_validation_needed_cmc_ebc_option_validation_plan():
    record = build_candidate_validation_plan_record(
        _candidate(
            "sic_sic_cmc_rare_earth_ebc_variant",
            "validation_needed_options",
            "cmc_ebc_environmental_protection_path",
            "C",
        )
    )

    assert record["validation_plan_status"] == "validation_required_before_engineering_use"
    text = _text(record, "required_validation_activities", "interface_validation_items", "environmental_exposure_validation_items", "comparison_baseline_items")
    assert "ebc/substrate compatibility" in text
    assert "steam" in text or "environmental durability" in text
    assert "ni/tbc reference architecture" in text


def test_exploratory_concept_validation_plan_is_feasibility_only():
    record = build_candidate_validation_plan_record(
        _candidate("oxidation_protected_concept", "exploratory_context_only", "oxidation_protection_only_path", "D")
    )

    assert record["validation_plan_status"] == "exploratory_validation_only"
    text = _text(record, "required_validation_activities", "evidence_gaps", "exit_criteria_before_next_gate")
    assert "feasibility" in text
    assert "evidence maturity uplift" in text
    assert "qualification planning" in text


def test_research_only_graded_am_validation_plan():
    record = build_candidate_validation_plan_record(
        _candidate("thermal_barrier_gradient", "research_only_context", "graded_am_research_path", "F")
    )

    assert record["validation_plan_status"] == "research_validation_only"
    text = _text(record, "required_validation_activities", "inspection_and_ndi_plan_items", "mechanical_or_thermal_validation_items")
    assert "transition-zone" in text
    assert "residual stress" in text
    assert "through-depth inspection" in text
    assert "engineering selection" in text


def test_poor_fit_candidate_is_parked_for_profile():
    record = build_candidate_validation_plan_record(
        _candidate("wear_only_coating", "poor_fit_for_profile", "wear_or_erosion_path", "C")
    )

    assert record["validation_plan_status"] == "parked_no_validation_for_this_profile"
    text = _text(record, "required_validation_activities", "evidence_gaps", "exit_criteria_before_next_gate", "responsible_use")
    assert "mismatch" in text
    assert "do not spend validation effort" in text
    assert "unless requirements change" in text


def test_attach_validation_plan_preserves_order_and_existing_outputs():
    candidates = [
        _candidate("tbc_reference", "near_term_comparison_references", "coated_metallic_tbc_path", "B"),
        _candidate("cmc_option", "validation_needed_options", "cmc_ebc_environmental_protection_path", "C"),
    ]
    package = {
        "application_profile": {"profile_id": "hot_section_thermal_cycling_oxidation"},
        "candidate_systems": candidates,
        "ranked_recommendations": [],
        "pareto_front": [],
        "controlled_application_shortlist": {"records": [{"candidate_id": "tbc_reference"}]},
    }
    original = copy.deepcopy(package)

    attached = attach_validation_plan(package)

    assert [c["candidate_id"] for c in attached["candidate_systems"]] == ["tbc_reference", "cmc_option"]
    assert len(attached["candidate_systems"]) == len(package["candidate_systems"])
    assert all("validation_plan_record" in candidate for candidate in attached["candidate_systems"])
    assert attached["ranked_recommendations"] == []
    assert attached["pareto_front"] == []
    assert attached["controlled_application_shortlist"] == package["controlled_application_shortlist"]
    assert package == original


def test_build_validation_plan_summary_flags_and_counts_are_json_safe():
    package = {
        "application_profile": {"profile_id": "hot_section_thermal_cycling_oxidation"},
        "candidate_systems": [
            _candidate("baseline", "near_term_comparison_references", "coated_metallic_tbc_path", "B"),
            _candidate("needed", "validation_needed_options", "cmc_ebc_environmental_protection_path", "C"),
            _candidate("explore", "exploratory_context_only", "oxidation_protection_only_path", "D"),
            _candidate("research", "research_only_context", "graded_am_research_path", "F"),
            _candidate("parked", "poor_fit_for_profile", "wear_or_erosion_path", "C"),
        ],
        "controlled_application_shortlist": {"records": []},
    }

    plan = build_validation_plan(package)

    assert plan["candidate_count"] == 5
    assert plan["validation_plan_status_counts"]["baseline_reference_validation"] >= 1
    assert plan["validation_plan_status_counts"]["validation_required_before_engineering_use"] >= 1
    assert plan["validation_plan_status_counts"]["exploratory_validation_only"] >= 1
    assert plan["validation_plan_status_counts"]["research_validation_only"] >= 1
    assert plan["validation_plan_status_counts"]["parked_no_validation_for_this_profile"] >= 1
    assert plan["candidate_ids_by_validation_plan_status"]
    assert plan["bucket_level_validation_plans"]
    assert plan["suggested_validation_workflow"]
    assert plan["not_final_selection"] is True
    assert plan["no_ranking_applied"] is True
    assert plan["no_selection_made"] is True
    assert plan["no_variants_generated"] is True
    assert plan["no_pareto_optimisation"] is True
    assert plan["not_certification_approval"] is True
    assert plan["not_qualification_approval"] is True
    json.dumps(plan)
