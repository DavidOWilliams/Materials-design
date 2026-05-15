from copy import deepcopy

from src.phase5_specialist_model_adapters import (
    DEFAULT_DISABLED_ADAPTER_IDS,
    adapter_contract_review_summary,
    adapter_lookup,
    build_adapter_capability,
    build_blocked_response_for_request,
    build_specialist_adapter_registry,
    build_specialist_model_request,
    candidate_allowed_for_mature_recommendation,
    controlled_value,
    default_disabled_adapter_capabilities,
    default_safety_flags,
    live_call_allowed,
    normalise_token,
    run_disabled_specialist_adapter_contract_review,
    audit_record_for_request,
    wrap_research_generated_candidate,
)


def _unsafe_adapter() -> dict:
    return {
        "adapter_id": "unsafe_adapter",
        "adapter_label": "Unsafe adapter",
        "model_family": "unsafe_model",
        "supported_tasks": ["candidate_generation"],
        "adapter_status": "gated_research_only",
        "allowed_mode": "gated_research_contract_only",
        "live_calls_enabled": True,
    }


def test_normalise_token_lowercases_and_replaces_spaces_hyphens():
    assert normalise_token(" AtomGPT Candidate-Generator ") == "atomgpt_candidate_generator"


def test_controlled_value_returns_allowed_value_or_default():
    assert controlled_value("Property Estimation", ["property_estimation"], "candidate_generation") == (
        "property_estimation"
    )
    assert controlled_value("bad", ["candidate_generation"], "candidate_generation") == (
        "candidate_generation"
    )


def test_default_safety_flags_includes_required_guardrails():
    flags = default_safety_flags(["custom_flag"])

    assert "custom_flag" in flags
    assert "no_live_call" in flags
    assert "no_mature_evidence_claim" in flags
    assert "no_certification_approval" in flags
    assert "no_qualification_approval" in flags


def test_build_adapter_capability_always_sets_live_calls_false():
    capability = build_adapter_capability(
        "adapter",
        adapter_label="Adapter",
        model_family="family",
        supported_tasks=["candidate_generation"],
        adapter_status="gated_research_only",
    )

    assert capability["live_calls_enabled"] is False


def test_build_adapter_capability_blocks_generated_and_mature_evidence():
    capability = build_adapter_capability(
        "adapter",
        adapter_label="Adapter",
        model_family="family",
        supported_tasks=["candidate_generation"],
    )

    assert capability["generated_candidates_allowed"] is False
    assert capability["mature_evidence_allowed"] is False
    assert capability["default_evidence_maturity"] == "F"


def test_build_adapter_capability_filters_unsupported_tasks():
    capability = build_adapter_capability(
        "adapter",
        adapter_label="Adapter",
        model_family="family",
        supported_tasks=["candidate_generation", "bad_task", "Property Estimation"],
    )

    assert capability["supported_tasks"] == ["candidate_generation", "property_estimation"]


def test_default_disabled_adapter_capabilities_returns_expected_order():
    capabilities = default_disabled_adapter_capabilities()

    assert [item["adapter_id"] for item in capabilities] == list(DEFAULT_DISABLED_ADAPTER_IDS)
    assert all(item["live_calls_enabled"] is False for item in capabilities)


def test_build_specialist_adapter_registry_default_is_disabled_and_safe():
    registry = build_specialist_adapter_registry()
    summary = adapter_contract_review_summary(registry)

    assert registry["registry_status"] == "disabled_registry"
    assert summary["registry_safe"] is True


def test_build_specialist_adapter_registry_blocks_unsafe_live_call_setting():
    registry = build_specialist_adapter_registry([_unsafe_adapter()])

    assert registry["registry_status"] == "unsafe_registry_blocked"
    assert registry["adapters"][0]["live_calls_enabled"] is False
    assert any("Unsafe supplied adapter settings were blocked" in warning for warning in registry["warnings"])


def test_adapter_lookup_builds_lookup_by_adapter_id():
    registry = build_specialist_adapter_registry()

    lookup = adapter_lookup(registry)

    assert list(lookup) == list(DEFAULT_DISABLED_ADAPTER_IDS)
    assert lookup["atomgpt_candidate_generator"]["adapter_label"] == "AtomGPT candidate generator"


def test_build_specialist_model_request_records_live_call_without_execution():
    request = build_specialist_model_request(
        adapter_id="AtomGPT Candidate Generator",
        task_type="candidate_generation",
        live_call_requested=True,
        input_constraints={"temperature": "high"},
    )

    assert request["adapter_id"] == "atomgpt_candidate_generator"
    assert request["live_call_requested"] is True
    assert request["input_constraints"] == {"temperature": "high"}
    assert "no_live_call" in request["safety_flags"]


def test_live_call_allowed_always_false():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        live_call_requested=True,
    )

    assert live_call_allowed(request) is False


def test_blocked_response_returns_live_call_blocked_when_requested():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        research_mode_enabled=True,
        live_call_requested=True,
    )

    response = build_blocked_response_for_request(request)

    assert response["response_status"] == "live_call_blocked"
    assert any("requested and blocked" in warning for warning in response["warnings"])


def test_blocked_response_returns_research_mode_required_when_disabled():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        research_mode_enabled=False,
    )

    response = build_blocked_response_for_request(request)

    assert response["response_status"] == "research_mode_required"


def test_blocked_response_has_no_candidates_and_evidence_f():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        research_mode_enabled=True,
    )

    response = build_blocked_response_for_request(request)

    assert response["generated_candidates"] == []
    assert response["evidence_maturity"] == "F"


def test_audit_record_records_live_attempt_and_block():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        live_call_requested=True,
    )

    audit = audit_record_for_request(request)

    assert audit["live_call_attempted"] is True
    assert audit["live_call_blocked"] is True
    assert audit["event_type"] == "live_call_blocked"


def test_wrap_research_generated_candidate_creates_research_only_id():
    candidate = wrap_research_generated_candidate(
        source_adapter_id="MatterGen Candidate Generator",
        candidate_label="Concept",
        sequence_number=3,
    )

    assert candidate["candidate_id"] == "research:mattergen_candidate_generator:3"
    assert candidate["candidate_status"] == "research_generated_only"


def test_wrap_research_generated_candidate_copies_payload_without_mutation():
    payload = {"chemistry": {"base": "Ni"}}
    original = deepcopy(payload)

    candidate = wrap_research_generated_candidate(
        source_adapter_id="adapter",
        candidate_label="Concept",
        candidate_payload=payload,
    )
    candidate["candidate_payload"]["chemistry"]["base"] = "Co"

    assert payload == original


def test_wrap_research_generated_candidate_sets_evidence_f_and_blocked():
    candidate = wrap_research_generated_candidate(
        source_adapter_id="adapter",
        candidate_label="Concept",
    )

    assert candidate["evidence_maturity"] == "F"
    assert candidate["blocked_from_mature_recommendation"] is True
    assert "blocked_from_mature_recommendation" in candidate["safety_flags"]


def test_candidate_allowed_false_for_research_generated_candidate():
    candidate = wrap_research_generated_candidate(
        source_adapter_id="adapter",
        candidate_label="Concept",
    )

    assert candidate_allowed_for_mature_recommendation(candidate) is False


def test_candidate_allowed_false_even_for_mature_looking_candidate():
    candidate = {
        "candidate_status": "reference",
        "evidence_maturity": "A",
        "safety_flags": [],
    }

    assert candidate_allowed_for_mature_recommendation(candidate) is False


def test_adapter_contract_review_summary_reports_zero_enabled_counts():
    registry = build_specialist_adapter_registry()

    summary = adapter_contract_review_summary(registry)

    assert summary["live_enabled_count"] == 0
    assert summary["generated_candidates_allowed_count"] == 0
    assert summary["mature_evidence_allowed_count"] == 0
    assert summary["registry_safe"] is True


def test_run_contract_review_returns_registry_and_safe_summary_without_request():
    review = run_disabled_specialist_adapter_contract_review()

    assert review["registry"]["registry_status"] == "disabled_registry"
    assert review["summary"]["registry_safe"] is True
    assert review["response"] is None
    assert review["audit_record"] is None


def test_run_contract_review_returns_blocked_response_and_audit_for_request():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        live_call_requested=True,
    )

    review = run_disabled_specialist_adapter_contract_review(request=request)

    assert review["response"]["response_status"] == "live_call_blocked"
    assert review["audit_record"]["event_type"] == "live_call_blocked"


def test_run_contract_review_does_not_mutate_supplied_request_or_registry():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        live_call_requested=True,
    )
    registry = build_specialist_adapter_registry([_unsafe_adapter()])
    original_request = deepcopy(request)
    original_registry = deepcopy(registry)

    run_disabled_specialist_adapter_contract_review(request=request, registry=registry)

    assert request == original_request
    assert registry == original_registry


def test_module_outputs_do_not_include_decision_fields():
    request = build_specialist_model_request(
        adapter_id="adapter",
        task_type="candidate_generation",
        live_call_requested=True,
    )
    review = run_disabled_specialist_adapter_contract_review(request=request)
    candidate = wrap_research_generated_candidate(
        source_adapter_id="adapter",
        candidate_label="Concept",
    )

    for container in (review, review["registry"], review["summary"], review["response"], candidate):
        assert "score" not in container
        assert "rank" not in container
        assert "winner" not in container
        assert "recommendation" not in container
        assert "qualification_approval" not in container
        assert "certification_approval" not in container
