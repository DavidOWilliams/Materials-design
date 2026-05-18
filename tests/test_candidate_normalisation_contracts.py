from copy import deepcopy
from pathlib import Path

import src.candidate_normalisation_contracts as contracts
from src.candidate_generator_requests import hot_section_demo_generator_request_plan


def _requirements_by_id(plan):
    return {
        requirement["request_id"]: requirement
        for requirement in plan["normalisation_requirements"]
    }


def _requests_by_id(plan):
    return {request["request_id"]: request for request in plan["generator_requests"]}


def _walk_keys_and_values(value):
    if isinstance(value, dict):
        items = []
        for key, nested in value.items():
            items.append(str(key))
            items.extend(_walk_keys_and_values(nested))
        return items
    if isinstance(value, list):
        items = []
        for nested in value:
            items.extend(_walk_keys_and_values(nested))
        return items
    return [str(value)]


def test_unique_preserve_order_removes_duplicates_and_preserves_order():
    assert contracts.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_slugify_identifier_creates_safe_lowercase_ids():
    assert contracts.slugify_identifier("Ni Superalloy + TBC Reference") == (
        "ni_superalloy_tbc_reference"
    )
    assert contracts.slugify_identifier("!!!") == "unknown"


def test_architecture_type_for_request_id_maps_substrate_plus_coating():
    assert (
        contracts.architecture_type_for_request_id("substrate_plus_coating_assembly")
        == "substrate_plus_coating_system"
    )


def test_evidence_maturity_record_normalises_unknown_levels():
    record = contracts.evidence_maturity_record("Z")

    assert record["level"] == "unknown"
    assert record["label"] == "Unknown"


def test_source_provenance_record_falls_back_to_readable_label():
    record = contracts.source_provenance_record("metallic_reference_sources")

    assert record["label"] == "Metallic reference sources"
    assert record["provenance_type"] == "unknown"


def test_criterion_value_placeholders_create_pending_records():
    placeholders = contracts.criterion_value_placeholders(
        ["oxidation_resistance", "lifecycle_cost"]
    )

    assert placeholders[0]["criterion_id"] == "oxidation_resistance"
    assert placeholders[0]["estimated_value"] == "pending"
    assert placeholders[0]["confidence"] == "not_assessed"
    assert placeholders[1]["unit"] == "not_specified"


def test_model_provenance_placeholders_from_hot_section_demo():
    placeholders = contracts.model_provenance_placeholders_from_generator_plan(
        hot_section_demo_generator_request_plan()
    )

    assert placeholders == [
        {
            "model_estimate_id": "pending_model_estimate",
            "model_type": "placeholder",
            "model_name": "Model-estimate preparation",
            "live_call_allowed": False,
            "provenance_required": True,
        }
    ]


def test_measurement_feedback_links_empty_for_hot_section_without_measurement_request():
    assert (
        contracts.measurement_feedback_links_from_generator_plan(
            hot_section_demo_generator_request_plan()
        )
        == []
    )

    plan = hot_section_demo_generator_request_plan()
    plan["generator_requests"].append(
        {
            "request_id": "measurement_feedback_preparation",
            "enabled": True,
            "status": "placeholder_only",
        }
    )
    assert contracts.measurement_feedback_links_from_generator_plan(plan)


def test_required_candidate_fields_include_gradient_architecture_for_spatial_am():
    fields = contracts.required_candidate_fields_for_architecture(
        "spatially_graded_am_system"
    )

    assert "gradient_architecture" in fields


def test_normalisation_requirement_maps_placeholder_status():
    request = _requests_by_id(hot_section_demo_generator_request_plan())[
        "model_estimate_preparation"
    ]

    requirement = contracts.normalisation_requirement_for_request(request)

    assert requirement["placeholder_only"] is True
    assert requirement["record_status"] == "placeholder_only"


def test_normalisation_requirements_include_enabled_requests_only():
    plan = hot_section_demo_generator_request_plan()
    plan["generator_requests"].append(
        {"request_id": "research_generated_system_wrapping", "enabled": False}
    )

    requirements = contracts.normalisation_requirements_from_generator_plan(plan)
    request_ids = {requirement["request_id"] for requirement in requirements}

    assert "metallic_reference_generation" in request_ids
    assert "research_generated_system_wrapping" not in request_ids


def test_active_criteria_from_generator_plan_extracts_hot_section_criteria():
    criteria = contracts.active_criteria_from_generator_plan(
        hot_section_demo_generator_request_plan()
    )

    assert "oxidation_resistance" in criteria
    assert "lifecycle_cost" in criteria


def test_normalised_candidate_template_creates_contract_template_with_criteria():
    candidate = contracts.normalised_candidate_template(
        "metallic_reference_generation",
        active_criteria=["oxidation_resistance"],
    )

    assert candidate["record_status"] == "contract_template"
    assert candidate["candidate_id"] == "metallic_reference_generation"
    assert candidate["criteria_values"][0]["criterion_id"] == "oxidation_resistance"


def test_normalise_candidate_record_does_not_mutate_raw_candidate():
    raw_candidate = {
        "system_name": "Ni superalloy + TBC",
        "material": {"family": "nickel_alloy"},
    }
    original = deepcopy(raw_candidate)

    contracts.normalise_candidate_record(raw_candidate)

    assert raw_candidate == original


def test_normalise_candidate_record_fills_required_fields_from_raw_and_request():
    raw_candidate = {
        "id": "candidate-1",
        "name": "Candidate 1",
        "family": "nickel_alloy",
        "material": {"name": "Ni alloy"},
        "coating": {"name": "TBC"},
    }
    generator_request = {
        "request_id": "substrate_plus_coating_assembly",
        "source_ids": ["metallic_reference_sources", "coating_reference_sources"],
    }

    candidate = contracts.normalise_candidate_record(
        raw_candidate,
        generator_request=generator_request,
        active_criteria=["oxidation_resistance"],
    )

    assert candidate["candidate_id"] == "candidate-1"
    assert candidate["system_name"] == "Candidate 1"
    assert candidate["material_family"] == "nickel_alloy"
    assert candidate["substrate_or_bulk_material"] == {"name": "Ni alloy"}
    assert candidate["coating_or_surface_system"] == {"name": "TBC"}
    assert candidate["source_request_ids"] == [
        "metallic_reference_sources",
        "coating_reference_sources",
    ]
    assert candidate["criteria_values"][0]["criterion_id"] == "oxidation_resistance"


def test_normalise_candidate_record_infers_architecture_from_generator_request():
    candidate = contracts.normalise_candidate_record(
        {"system_name": "Gradient template"},
        generator_request={"request_id": "spatially_graded_am_system_assembly"},
    )

    assert candidate["architecture_type"] == "spatially_graded_am_system"


def test_validate_normalised_candidate_validates_template_with_warnings_allowed():
    candidate = contracts.normalised_candidate_template("metallic_reference_generation")

    result = contracts.validate_normalised_candidate(candidate)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_normalised_candidate_errors_when_candidate_id_missing():
    candidate = contracts.normalised_candidate_template("metallic_reference_generation")
    candidate["candidate_id"] = ""

    result = contracts.validate_normalised_candidate(candidate)

    assert result["is_valid"] is False
    assert "candidate_id must be a non-empty string." in result["errors"]


def test_validate_normalised_candidate_errors_for_forbidden_claim_fields():
    candidate = contracts.normalised_candidate_template("metallic_reference_generation")
    candidate["certification_approval"] = True

    result = contracts.validate_normalised_candidate(candidate)

    assert result["is_valid"] is False
    assert any("Forbidden approval or certification" in error for error in result["errors"])


def test_build_candidate_normalisation_plan_does_not_mutate_generator_plan():
    generator_plan = hot_section_demo_generator_request_plan()
    original = deepcopy(generator_plan)

    contracts.build_candidate_normalisation_plan(generator_plan)

    assert generator_plan == original


def test_build_candidate_normalisation_plan_disables_live_flags():
    plan = contracts.build_candidate_normalisation_plan(
        hot_section_demo_generator_request_plan()
    )

    assert plan["live_source_retrieval_allowed"] is False
    assert plan["live_model_call_allowed"] is False


def test_validate_candidate_normalisation_plan_validates_hot_section_demo():
    result = contracts.validate_candidate_normalisation_plan(
        contracts.hot_section_demo_candidate_normalisation_plan()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_candidate_normalisation_plan_errors_if_live_model_call_true():
    plan = contracts.hot_section_demo_candidate_normalisation_plan()
    plan["live_model_call_allowed"] = True

    result = contracts.validate_candidate_normalisation_plan(plan)

    assert result["is_valid"] is False
    assert "live_model_call_allowed must be false." in result["errors"]


def test_candidate_normalisation_summary_returns_counts_and_live_flags():
    plan = contracts.hot_section_demo_candidate_normalisation_plan()

    summary = contracts.candidate_normalisation_summary(plan)

    assert summary["schema_version"] == contracts.CANDIDATE_NORMALISATION_PLAN_SCHEMA_VERSION
    assert summary["normalisation_requirement_count"] == len(
        plan["normalisation_requirements"]
    )
    assert summary["active_criteria_count"] > 0
    assert summary["criterion_value_placeholders_required"] is True
    assert summary["model_provenance_required"] is True
    assert summary["live_source_retrieval_allowed"] is False
    assert summary["live_model_call_allowed"] is False


def test_hot_section_demo_candidate_normalisation_plan_includes_expected_requirements():
    plan = contracts.hot_section_demo_candidate_normalisation_plan()
    requirements = _requirements_by_id(plan)
    expected = {
        "metallic_reference_generation",
        "cmc_reference_generation",
        "coating_component_generation",
        "gradient_template_generation",
        "model_estimate_preparation",
        "substrate_plus_coating_assembly",
        "cmc_ebc_system_assembly",
        "spatially_graded_am_system_assembly",
    }

    assert expected <= set(requirements)
    assert plan["criterion_value_placeholders_required"] is True
    assert plan["model_provenance_required"] is True
    assert plan["measurement_feedback_links_required"] is False


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(contracts.hot_section_demo_candidate_normalisation_plan())
    )


def test_candidate_normalisation_contracts_does_not_import_forbidden_modules():
    source = Path("src/candidate_normalisation_contracts.py").read_text(encoding="utf-8")
    forbidden = [
        "import app",
        "from app",
        "import streamlit",
        "from streamlit",
        "phase6_decision_cockpit_prototype",
        "import src.phase5_",
        "from src.phase5_",
        "import phase5_",
        "from phase5_",
    ]

    assert not [snippet for snippet in forbidden if snippet in source]


def test_candidate_normalisation_contracts_does_not_call_io_network_or_process_tools():
    source = Path("src/candidate_normalisation_contracts.py").read_text(encoding="utf-8")
    forbidden = [
        "open(",
        "Path",
        "import requests",
        "from requests",
        "requests.get(",
        "requests.post(",
        "requests.Session",
        "subprocess",
        "write_text",
        "write_bytes",
        "urlopen",
        "socket",
    ]

    assert not [snippet for snippet in forbidden if snippet in source]
