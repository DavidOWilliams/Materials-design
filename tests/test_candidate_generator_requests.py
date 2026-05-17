from copy import deepcopy
from pathlib import Path

import src.candidate_generator_requests as requests
from src.candidate_source_orchestrator import hot_section_demo_source_orchestration_plan


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
    assert requests.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_request_type_maps_coating_component_generation():
    assert requests.request_type("coating_component_generation") == "component_generator"


def test_request_label_returns_readable_label_and_unknown_fallback():
    assert (
        requests.request_label("cmc_ebc_system_assembly")
        == "CMC + EBC system assembly"
    )
    assert requests.request_label("new_request_id") == "New request id"


def test_request_status_for_source_request_maps_disabled_placeholder_and_planned():
    assert requests.request_status_for_source_request({"enabled": False}) == "disabled"
    assert (
        requests.request_status_for_source_request(
            {"enabled": True, "status": "placeholder_only"}
        )
        == "placeholder_only"
    )
    assert (
        requests.request_status_for_source_request(
            {"enabled": True, "status": "planned"}
        )
        == "planned"
    )


def test_source_request_lookup_returns_source_id_mapping():
    plan = hot_section_demo_source_orchestration_plan()

    lookup = requests.source_request_lookup(plan)

    assert "metallic_reference_sources" in lookup
    assert lookup["metallic_reference_sources"]["source_id"] == "metallic_reference_sources"


def test_generator_request_disables_live_source_retrieval_and_model_calls():
    request = requests.generator_request("metallic_reference_generation")

    assert request["live_source_retrieval_allowed"] is False
    assert request["live_model_call_allowed"] is False


def test_generator_request_normalises_unknown_status_to_planned():
    request = requests.generator_request("metallic_reference_generation", status="live")

    assert request["status"] == "planned"


def test_request_parameters_from_source_copies_parameters_and_adds_metadata():
    source_request = {
        "request_type": "candidate_reference",
        "status": "planned",
        "live_retrieval_allowed": False,
        "request_parameters": {"active_criteria": ["oxidation_resistance"]},
    }

    params = requests.request_parameters_from_source(source_request)

    assert params["active_criteria"] == ["oxidation_resistance"]
    assert params["source_request_type"] == "candidate_reference"
    assert params["source_request_status"] == "planned"
    assert params["live_retrieval_allowed"] is False


def test_request_parameters_from_source_does_not_mutate_source_request():
    source_request = {
        "request_type": "candidate_reference",
        "status": "planned",
        "live_retrieval_allowed": False,
        "request_parameters": {"active_criteria": ["oxidation_resistance"]},
    }
    original = deepcopy(source_request)

    requests.request_parameters_from_source(source_request)

    assert source_request == original


def test_generator_requests_from_sources_create_expected_hot_section_requests():
    generator_requests = requests.generator_requests_from_source_requests(
        hot_section_demo_source_orchestration_plan()
    )
    request_ids = {request["request_id"] for request in generator_requests}

    assert "metallic_reference_generation" in request_ids
    assert "cmc_reference_generation" in request_ids
    assert "coating_component_generation" in request_ids
    assert "gradient_template_generation" in request_ids
    assert "criteria_evidence_preparation" in request_ids
    assert "model_estimate_preparation" in request_ids


def test_generator_requests_merge_criteria_and_evidence_sources():
    generator_requests = requests.generator_requests_from_source_requests(
        hot_section_demo_source_orchestration_plan()
    )
    by_id = {request["request_id"]: request for request in generator_requests}
    criteria_request = by_id["criteria_evidence_preparation"]

    assert criteria_request["source_ids"] == [
        "criteria_reference_sources",
        "evidence_maturity_sources",
    ]
    assert criteria_request["request_parameters"]["merged_sources"] == [
        "criteria_reference_sources",
        "evidence_maturity_sources",
    ]
    assert "source_parameters_by_id" in criteria_request["request_parameters"]


def test_generator_requests_create_placeholder_model_estimate_preparation():
    generator_requests = requests.generator_requests_from_source_requests(
        hot_section_demo_source_orchestration_plan()
    )
    by_id = {request["request_id"]: request for request in generator_requests}

    assert by_id["model_estimate_preparation"]["status"] == "placeholder_only"


def test_assembler_requests_create_hot_section_assembly_requests():
    assembler_requests = requests.assembler_requests_from_source_plan(
        hot_section_demo_source_orchestration_plan()
    )
    request_ids = {request["request_id"] for request in assembler_requests}

    assert "substrate_plus_coating_assembly" in request_ids
    assert "cmc_ebc_system_assembly" in request_ids
    assert "spatially_graded_am_system_assembly" in request_ids


def test_assembler_requests_do_not_create_research_wrapper_when_research_false():
    assembler_requests = requests.assembler_requests_from_source_plan(
        hot_section_demo_source_orchestration_plan()
    )
    request_ids = {request["request_id"] for request in assembler_requests}

    assert "research_generated_system_wrapping" not in request_ids


def test_build_generator_request_plan_does_not_mutate_source_orchestration_plan():
    plan = hot_section_demo_source_orchestration_plan()
    original = deepcopy(plan)

    requests.build_generator_request_plan(plan)

    assert plan == original


def test_build_generator_request_plan_disables_live_flags():
    plan = requests.build_generator_request_plan(hot_section_demo_source_orchestration_plan())

    assert plan["live_source_retrieval_allowed"] is False
    assert plan["live_model_call_allowed"] is False
    assert all(
        request["live_source_retrieval_allowed"] is False
        and request["live_model_call_allowed"] is False
        for request in plan["generator_requests"]
    )


def test_validate_generator_request_plan_validates_hot_section_demo():
    result = requests.validate_generator_request_plan(
        requests.hot_section_demo_generator_request_plan()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_generator_request_plan_errors_for_plan_live_source_retrieval():
    plan = requests.hot_section_demo_generator_request_plan()
    plan["live_source_retrieval_allowed"] = True

    result = requests.validate_generator_request_plan(plan)

    assert result["is_valid"] is False
    assert "live_source_retrieval_allowed must be false." in result["errors"]


def test_validate_generator_request_plan_errors_for_request_live_model_call():
    plan = requests.hot_section_demo_generator_request_plan()
    plan["generator_requests"][0]["live_model_call_allowed"] = True

    result = requests.validate_generator_request_plan(plan)

    assert result["is_valid"] is False
    assert any("live_model_call_allowed must be false" in error for error in result["errors"])


def test_validate_generator_request_plan_warns_for_research_wrapper_without_research_mode():
    plan = requests.hot_section_demo_generator_request_plan()
    plan["generator_requests"].append(
        requests.assembler_request(
            "research_generated_system_wrapping",
            required_inputs=["model_estimate_preparation"],
            reason="test",
            research_only=True,
        )
    )
    plan["research_mode_allowed"] = False

    result = requests.validate_generator_request_plan(plan)

    assert (
        "Research-generated system wrapping is enabled while research mode is not allowed."
        in result["warnings"]
    )


def test_generator_request_summary_returns_counts_and_live_flags():
    plan = requests.hot_section_demo_generator_request_plan()

    summary = requests.generator_request_summary(plan)

    assert summary["schema_version"] == requests.GENERATOR_REQUEST_SCHEMA_VERSION
    assert summary["generator_request_count"] == len(plan["generator_requests"])
    assert summary["placeholder_request_count"] >= 1
    assert summary["system_assembly_request_count"] >= 1
    assert summary["live_source_retrieval_allowed"] is False
    assert summary["live_model_call_allowed"] is False


def test_hot_section_demo_generator_request_plan_includes_expected_requests():
    by_id = _requests_by_id(requests.hot_section_demo_generator_request_plan())
    expected = {
        "metallic_reference_generation",
        "cmc_reference_generation",
        "coating_component_generation",
        "gradient_template_generation",
        "criteria_evidence_preparation",
        "model_estimate_preparation",
        "bulk_material_assembly",
        "substrate_plus_coating_assembly",
        "cmc_ebc_system_assembly",
        "spatially_graded_am_system_assembly",
        "hybrid_system_assembly",
    }

    assert expected <= set(by_id)
    assert by_id["model_estimate_preparation"]["status"] == "placeholder_only"


def test_hot_section_demo_generator_request_plan_excludes_research_wrapping():
    by_id = _requests_by_id(requests.hot_section_demo_generator_request_plan())

    assert "research_generated_system_wrapping" not in by_id


def test_hot_section_demo_generator_request_plan_has_no_approval_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(requests.hot_section_demo_generator_request_plan())
    )


def test_candidate_generator_requests_does_not_import_forbidden_modules():
    source = Path("src/candidate_generator_requests.py").read_text(encoding="utf-8")
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


def test_candidate_generator_requests_does_not_call_io_network_or_process_tools():
    source = Path("src/candidate_generator_requests.py").read_text(encoding="utf-8")
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
