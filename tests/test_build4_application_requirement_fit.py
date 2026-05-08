import json

from src.application_profiles import get_default_application_profile
from src.application_requirement_fit import (
    assess_candidate_against_application_profile,
    attach_application_requirement_fit,
    build_application_requirement_fit_matrix,
    detect_hot_section_architecture_path,
    has_cmc_ebc_environmental_protection_path,
)
from src.ui_view_models import package_to_json_safe_dict


def _candidate(candidate_id, maturity="C", primary=None, secondary=None, readiness_status="unknown", **extra):
    candidate = {
        "candidate_id": candidate_id,
        "name": candidate_id,
        "candidate_class": "coating_enabled",
        "evidence_maturity": maturity,
        "surface_function_profile": {
            "primary_service_functions": primary or [],
            "secondary_service_functions": secondary or [],
            "support_or_lifecycle_considerations": [],
            "risk_or_interface_considerations": [],
        },
        "decision_readiness": {"readiness_status": readiness_status},
        "inspection_plan": {"inspection_burden": "medium"},
        "repairability": {"repairability_level": "moderate"},
        "qualification_route": {"qualification_burden": "medium"},
    }
    candidate.update(extra)
    return candidate


def test_required_functions_and_c_maturity_can_be_plausible():
    profile = get_default_application_profile()
    candidate = _candidate(
        "candidate-ok",
        maturity="C",
        primary=["thermal_barrier", "oxidation_resistance"],
        secondary=["thermal_cycling_tolerance"],
        readiness_status="usable_with_caveats",
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] in {"plausible_near_term_analogue", "plausible_with_validation"}
    assert record["missing_required_primary_functions"] == []
    assert record["architecture_path"] == "coated_metallic_tbc_path"


def test_candidate_missing_all_required_primary_functions_is_poor_or_insufficient():
    profile = get_default_application_profile()
    candidate = _candidate("candidate-miss", primary=["wear_resistance"], maturity="C")

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] in {"poor_fit_for_profile", "insufficient_information"}
    assert set(record["missing_required_primary_functions"]) == {"thermal_barrier", "oxidation_resistance"}


def test_f_maturity_candidate_is_research_only_for_profile():
    profile = get_default_application_profile()
    candidate = _candidate("candidate-f", maturity="F", primary=["thermal_barrier", "oxidation_resistance"])

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] == "research_only_for_profile"


def test_d_or_e_candidate_is_exploratory_unless_profile_is_exploratory():
    default_profile = get_default_application_profile()
    exploratory_profile = get_default_application_profile("exploratory_graded_surface_architecture")
    candidate = _candidate("candidate-e", maturity="E", primary=["thermal_barrier", "oxidation_resistance"])
    exploratory_candidate = _candidate("candidate-e2", maturity="E", primary=["oxidation_resistance"])

    assert assess_candidate_against_application_profile(candidate, default_profile)["fit_status"] == (
        "exploratory_only_for_profile"
    )
    assert assess_candidate_against_application_profile(exploratory_candidate, exploratory_profile)["fit_status"] in {
        "plausible_with_validation",
        "exploratory_only_for_profile",
    }


def test_support_tags_alone_do_not_satisfy_required_primary_functions():
    profile = get_default_application_profile()
    candidate = _candidate(
        "support-only",
        primary=["inspection_access_or_monitoring", "repairability_support", "coating_interface_management"],
        maturity="B",
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["matched_required_primary_functions"] == []
    assert record["fit_status"] in {"poor_fit_for_profile", "insufficient_information"}


def test_high_inspection_difficulty_with_difficult_access_creates_caution():
    profile = get_default_application_profile()
    candidate = _candidate(
        "inspection-caution",
        primary=["thermal_barrier", "oxidation_resistance"],
        coating_spallation_adhesion={"inspection_difficulty": "high"},
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert any("inspection" in item.lower() for item in record["major_cautions"])


def test_high_repairability_constraint_with_repair_required_creates_blocker_or_caution():
    profile = get_default_application_profile("repairable_coated_metallic_component")
    candidate = _candidate(
        "repair-caution",
        primary=["oxidation_resistance"],
        coating_spallation_adhesion={"repairability_constraint": "high"},
        repairability={"repairability_level": "limited"},
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["critical_blockers"] or any("repair" in item.lower() for item in record["major_cautions"])


def test_attach_application_requirement_fit_preserves_order_boundaries_and_does_not_mutate():
    package = {
        "candidate_systems": [
            _candidate("a", primary=["thermal_barrier", "oxidation_resistance"]),
            _candidate("b", primary=["wear_resistance"]),
        ],
        "ranked_recommendations": [{"candidate_id": "keep"}],
        "pareto_front": [{"candidate_id": "pareto"}],
    }
    attached = attach_application_requirement_fit(package)

    assert [candidate["candidate_id"] for candidate in attached["candidate_systems"]] == ["a", "b"]
    assert "application_requirement_fit" not in package["candidate_systems"][0]
    assert len(attached["application_requirement_fit"]["fit_records"]) == 2
    assert attached["ranked_recommendations"] == [{"candidate_id": "keep"}]
    assert attached["pareto_front"] == [{"candidate_id": "pareto"}]
    json.dumps(package_to_json_safe_dict(attached))


def test_build_application_requirement_fit_matrix_preserves_candidate_count():
    profile = get_default_application_profile()
    package = {
        "candidate_systems": [
            _candidate("a", primary=["thermal_barrier", "oxidation_resistance"]),
            _candidate("b", primary=["wear_resistance"], maturity="F"),
            _candidate("c", primary=["oxidation_resistance"], maturity="E"),
        ]
    }

    matrix = build_application_requirement_fit_matrix(package, profile)

    assert matrix["candidate_count"] == 3
    assert len(matrix["fit_records"]) == 3
    assert matrix["fit_status_counts"]
    assert matrix["architecture_path_counts"]
    assert matrix["not_a_final_recommendation"] is True
    assert matrix["no_ranking_applied"] is True


def test_cmc_ebc_path_is_hot_section_plausible_without_literal_thermal_barrier():
    profile = get_default_application_profile()
    candidate = _candidate(
        "sic-sic-cmc-ebc",
        maturity="C",
        primary=["environmental_barrier", "steam_recession_resistance"],
        candidate_class="ceramic_matrix_composite",
        coating_or_surface_system={"name": "rare-earth silicate EBC", "purpose": "steam recession protection"},
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert has_cmc_ebc_environmental_protection_path(candidate) is True
    assert record["fit_status"] == "plausible_with_validation"
    assert record["architecture_path"] == "cmc_ebc_environmental_protection_path"
    assert "thermal_barrier" in record["missing_required_primary_functions"]
    assert any("steam recession" in item.lower() for item in record["required_next_evidence"])


def test_rare_earth_silicate_ebc_stack_is_not_poor_fit_for_hot_section():
    profile = get_default_application_profile()
    candidate = _candidate(
        "rare-earth-ebc-stack",
        maturity="C",
        primary=["environmental_barrier", "steam_recession_resistance"],
        candidate_class="coating_enabled",
        coating_or_surface_system="rare-earth silicate environmental barrier coating for SiC/SiC CMC steam recession",
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] == "plausible_with_validation"
    assert record["architecture_path"] == "cmc_ebc_environmental_protection_path"


def test_melt_infiltrated_cmc_with_ebc_dependency_is_not_poor_fit_for_hot_section():
    profile = get_default_application_profile()
    candidate = _candidate(
        "melt-infiltrated-cmc-ebc",
        maturity="B",
        primary=["environmental_barrier", "steam_recession_resistance"],
        candidate_class="ceramic_matrix_composite",
        coating_or_surface_system="CMC+EBC dependency with environmental barrier coating",
        cmc_ebc_environmental_durability={
            "ebc_dependency_risk": "high",
            "oxidation_recession_risk": "high",
            "interface_or_interphase_risk": "high",
        },
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] == "plausible_with_validation"
    assert record["architecture_path"] == "cmc_ebc_environmental_protection_path"
    assert any("ebc dependency" in item.lower() or "oxidation/steam" in item.lower() for item in record["major_cautions"])


def test_wear_only_coating_remains_poor_fit_for_hot_section():
    profile = get_default_application_profile()
    candidate = _candidate(
        "wear-only",
        maturity="C",
        primary=["wear_resistance", "hard_surface"],
        coating_or_surface_system="hard wear coating",
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] == "poor_fit_for_profile"
    assert record["architecture_path"] == "wear_or_erosion_path"


def test_monolithic_ceramic_missing_hot_section_functions_is_poor_fit():
    profile = get_default_application_profile()
    candidate = _candidate(
        "alumina-reference",
        maturity="C",
        primary=[],
        candidate_class="monolithic_ceramic",
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] == "poor_fit_for_profile"
    assert record["architecture_path"] == "monolithic_ceramic_path"


def test_oxidation_only_gradient_is_not_promoted_to_plausible_validation():
    profile = get_default_application_profile()
    candidate = _candidate(
        "oxidation-gradient",
        maturity="E",
        primary=["oxidation_resistance"],
        candidate_class="spatially_graded_am",
        gradient_architecture={"gradient_type": "surface oxidation gradient"},
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] in {"exploratory_only_for_profile", "poor_fit_for_profile"}
    assert record["fit_status"] != "plausible_with_validation"


def test_f_thermal_barrier_gradient_remains_research_only():
    profile = get_default_application_profile()
    candidate = _candidate(
        "thermal-barrier-gradient",
        maturity="F",
        primary=["thermal_barrier", "oxidation_resistance"],
        candidate_class="spatially_graded_am",
        gradient_architecture={"gradient_type": "thermal barrier gradient"},
    )

    record = assess_candidate_against_application_profile(candidate, profile)

    assert record["fit_status"] == "research_only_for_profile"
    assert record["architecture_path"] == "graded_am_research_path"


def test_architecture_path_helper_classifies_tbc_cmc_wear_and_gradient_paths():
    profile = get_default_application_profile()
    tbc = _candidate(
        "tbc",
        primary=["thermal_barrier", "oxidation_resistance"],
        coating_or_surface_system="Ni superalloy bond coat TBC",
    )
    cmc = _candidate(
        "cmc",
        primary=["environmental_barrier", "steam_recession_resistance"],
        candidate_class="ceramic_matrix_composite",
        coating_or_surface_system="rare-earth silicate EBC",
    )
    wear = _candidate("wear", primary=["wear_resistance"], coating_or_surface_system="wear coating")
    gradient = _candidate(
        "gradient",
        primary=["oxidation_resistance"],
        maturity="E",
        candidate_class="spatially_graded_am",
        gradient_architecture={"gradient_type": "oxidation surface gradient"},
    )

    assert detect_hot_section_architecture_path(tbc, profile)["architecture_path"] == "coated_metallic_tbc_path"
    assert detect_hot_section_architecture_path(cmc, profile)["architecture_path"] == (
        "cmc_ebc_environmental_protection_path"
    )
    assert detect_hot_section_architecture_path(wear, profile)["architecture_path"] == "wear_or_erosion_path"
    assert detect_hot_section_architecture_path(gradient, profile)["architecture_path"] == "graded_am_research_path"
