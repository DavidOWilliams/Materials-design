from copy import deepcopy
from pathlib import Path

import src.candidate_criteria_valuation as valuation
from src.criteria_value_schema import hot_section_demo_criteria_valuation_plan


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
    assert valuation.unique_preserve_order(["a", "b", "a", "c", "b"]) == [
        "a",
        "b",
        "c",
    ]


def test_slugify_identifier_creates_safe_lowercase_ids():
    assert valuation.slugify_identifier("Candidate 1 / Oxidation") == (
        "candidate_1_oxidation"
    )
    assert valuation.slugify_identifier("!!!") == "unknown"


def test_candidate_id_returns_fallback_for_missing_id():
    assert valuation.candidate_id({}) == "unknown_candidate"


def test_candidate_architecture_type_returns_unknown_fallback():
    assert valuation.candidate_architecture_type({}) == "unknown"


def test_active_criteria_from_criteria_plan_returns_hot_section_criteria():
    criteria = valuation.active_criteria_from_criteria_plan(
        hot_section_demo_criteria_valuation_plan()
    )

    assert "temperature_capability" in criteria
    assert "oxidation_resistance" in criteria


def test_relevant_criteria_uses_active_criteria_when_provided():
    candidate = valuation.hot_section_demo_candidates()[0]

    assert valuation.relevant_criteria_for_candidate(
        candidate, ["oxidation_resistance"]
    ) == ["oxidation_resistance"]


def test_relevant_criteria_falls_back_to_architecture_hints():
    candidate = valuation.hot_section_demo_candidates()[2]

    criteria = valuation.relevant_criteria_for_candidate(candidate, [])

    assert "gradient_transition_risk" in criteria
    assert "model_confidence" in criteria


def test_relevant_criteria_never_returns_empty_list():
    assert valuation.relevant_criteria_for_candidate({}, []) == [
        "evidence_maturity",
        "qualification_risk",
    ]


def test_allowed_method_types_always_include_placeholder_and_deterministic():
    methods = valuation.allowed_method_types_for_work_item(
        {}, "oxidation_resistance", {}
    )

    assert "placeholder" in methods
    assert "deterministic_estimator" in methods


def test_allowed_method_types_include_computational_model_when_required():
    methods = valuation.allowed_method_types_for_work_item(
        {}, "oxidation_resistance", {"require_model_provenance": True}
    )

    assert "computational_model" in methods


def test_allowed_method_types_include_measurement_feedback_when_required():
    methods = valuation.allowed_method_types_for_work_item(
        {}, "oxidation_resistance", {"require_measurement_provenance": True}
    )

    assert "measurement_feedback" in methods


def test_work_item_id_for_creates_stable_id():
    assert valuation.work_item_id_for("Candidate 1", "oxidation_resistance") == (
        "valuate_candidate_1_oxidation_resistance"
    )


def test_valuation_work_item_creates_placeholder_with_live_flags_false():
    candidate = valuation.hot_section_demo_candidates()[0]

    item = valuation.valuation_work_item(
        candidate,
        "oxidation_resistance",
        criteria_plan=hot_section_demo_criteria_valuation_plan(),
    )

    assert item["valuation_status"] == "placeholder_only"
    assert item["live_model_call_allowed"] is False
    assert item["live_source_retrieval_allowed"] is False


def test_valuation_work_item_contains_candidate_specific_criterion_value():
    candidate = valuation.hot_section_demo_candidates()[0]

    item = valuation.valuation_work_item(
        candidate,
        "oxidation_resistance",
        criteria_plan=hot_section_demo_criteria_valuation_plan(),
    )

    assert item["criterion_value"]["candidate_id"] == "demo_metallic_candidate"
    assert item["criterion_value"]["criterion_id"] == "oxidation_resistance"


def test_valuation_work_items_for_candidate_creates_one_per_active_criterion():
    candidate = valuation.hot_section_demo_candidates()[0]
    criteria_plan = hot_section_demo_criteria_valuation_plan()

    items = valuation.valuation_work_items_for_candidate(
        candidate, criteria_plan=criteria_plan
    )

    assert len(items) == len(criteria_plan["active_criteria"])


def test_valuation_work_items_for_candidate_does_not_mutate_candidate():
    candidate = valuation.hot_section_demo_candidates()[0]
    original = deepcopy(candidate)

    valuation.valuation_work_items_for_candidate(
        candidate, criteria_plan=hot_section_demo_criteria_valuation_plan()
    )

    assert candidate == original


def test_valuation_work_items_mark_invalid_candidate_blocked():
    candidate = valuation.hot_section_demo_candidates()[0]
    candidate["candidate_id"] = ""

    items = valuation.valuation_work_items_for_candidate(
        candidate, criteria_plan={"active_criteria": ["oxidation_resistance"]}
    )

    assert items[0]["valuation_status"] == "blocked_invalid_candidate"
    assert items[0]["warnings"]


def test_criterion_values_by_candidate_groups_values():
    candidate = valuation.hot_section_demo_candidates()[0]
    items = valuation.valuation_work_items_for_candidate(
        candidate, criteria_plan={"active_criteria": ["oxidation_resistance"]}
    )

    grouped = valuation.criterion_values_by_candidate(items)

    assert set(grouped) == {"demo_metallic_candidate"}
    assert grouped["demo_metallic_candidate"][0]["criterion_id"] == "oxidation_resistance"


def test_build_plan_does_not_mutate_candidates_or_criteria_plan():
    candidates = valuation.hot_section_demo_candidates()
    criteria_plan = hot_section_demo_criteria_valuation_plan()
    original_candidates = deepcopy(candidates)
    original_criteria_plan = deepcopy(criteria_plan)

    valuation.build_candidate_criteria_valuation_plan(candidates, criteria_plan)

    assert candidates == original_candidates
    assert criteria_plan == original_criteria_plan


def test_build_plan_disables_live_model_and_source_calls():
    plan = valuation.hot_section_demo_candidate_criteria_valuation_plan()

    assert plan["live_model_call_allowed"] is False
    assert plan["live_source_retrieval_allowed"] is False


def test_build_plan_creates_per_candidate_placeholder_values():
    plan = valuation.hot_section_demo_candidate_criteria_valuation_plan()

    assert plan["candidate_count"] == 3
    assert plan["placeholder_value_count"] == plan["work_item_count"]
    assert set(plan["criterion_values_by_candidate"]) == {
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    }


def test_validate_work_item_validates_hot_section_item_with_warnings_allowed():
    item = valuation.hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]

    result = valuation.validate_valuation_work_item(item)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_work_item_errors_if_live_model_call_true():
    item = valuation.hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]
    item["live_model_call_allowed"] = True

    result = valuation.validate_valuation_work_item(item)

    assert result["is_valid"] is False
    assert "live_model_call_allowed must be false." in result["errors"]


def test_validate_work_item_errors_for_forbidden_claim_fields():
    item = valuation.hot_section_demo_candidate_criteria_valuation_plan()["work_items"][0]
    item["certification_approval"] = True

    result = valuation.validate_valuation_work_item(item)

    assert result["is_valid"] is False
    assert any("Forbidden approval or certification" in error for error in result["errors"])


def test_validate_candidate_plan_validates_hot_section_demo():
    result = valuation.validate_candidate_criteria_valuation_plan(
        valuation.hot_section_demo_candidate_criteria_valuation_plan()
    )

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert isinstance(result["warnings"], list)


def test_validate_candidate_plan_errors_if_live_source_retrieval_true():
    plan = valuation.hot_section_demo_candidate_criteria_valuation_plan()
    plan["live_source_retrieval_allowed"] = True

    result = valuation.validate_candidate_criteria_valuation_plan(plan)

    assert result["is_valid"] is False
    assert "live_source_retrieval_allowed must be false." in result["errors"]


def test_candidate_criteria_valuation_summary_returns_counts_and_live_flags():
    plan = valuation.hot_section_demo_candidate_criteria_valuation_plan()

    summary = valuation.candidate_criteria_valuation_summary(plan)

    assert summary["schema_version"] == valuation.CANDIDATE_CRITERIA_VALUATION_PLAN_SCHEMA_VERSION
    assert summary["candidate_count"] == 3
    assert summary["work_item_count"] == plan["work_item_count"]
    assert summary["placeholder_value_count"] == plan["placeholder_value_count"]
    assert summary["candidate_with_values_count"] == 3
    assert summary["live_model_call_allowed"] is False
    assert summary["live_source_retrieval_allowed"] is False


def test_hot_section_demo_candidates_returns_three_templates():
    candidates = valuation.hot_section_demo_candidates()

    assert [candidate["candidate_id"] for candidate in candidates] == [
        "demo_metallic_candidate",
        "demo_cmc_ebc_system",
        "demo_spatial_gradient_system",
    ]
    assert all(candidate["record_status"] == "contract_template" for candidate in candidates)


def test_hot_section_demo_plan_includes_expected_hot_section_criteria():
    plan = valuation.hot_section_demo_candidate_criteria_valuation_plan()
    criteria = {item["criterion_id"] for item in plan["work_items"]}

    assert {
        "temperature_capability",
        "oxidation_resistance",
        "coating_spallation_risk",
        "gradient_transition_risk",
    } <= criteria
    assert plan["live_model_call_allowed"] is False
    assert plan["live_source_retrieval_allowed"] is False
    assert plan["require_confidence"] is True
    assert plan["require_uncertainty"] is True
    assert plan["require_evidence_basis"] is True
    assert plan["require_model_provenance"] is True


def test_hot_section_demo_plan_has_no_approval_or_certification_claim_fields():
    forbidden_fields = {"certification_approval", "qualification_approval"}

    assert not forbidden_fields.intersection(
        _walk_keys_and_values(valuation.hot_section_demo_candidate_criteria_valuation_plan())
    )


def test_candidate_criteria_valuation_does_not_import_forbidden_modules():
    source = Path("src/candidate_criteria_valuation.py").read_text(encoding="utf-8")
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


def test_candidate_criteria_valuation_does_not_call_io_network_or_process_tools():
    source = Path("src/candidate_criteria_valuation.py").read_text(encoding="utf-8")
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
