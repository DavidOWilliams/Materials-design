from __future__ import annotations

from pathlib import Path

from src.candidate_criteria_valuation import (
    hot_section_demo_candidate_criteria_valuation_plan,
    validate_candidate_criteria_valuation_plan,
)
from src.criteria_coverage_summary import (
    hot_section_demo_criteria_coverage_summary_plan,
    validate_criteria_coverage_summary_plan,
)
from src.criteria_result_integration import (
    hot_section_demo_criteria_result_integration_plan,
    validate_criteria_result_integration_plan,
)
from src.criteria_value_schema import (
    hot_section_demo_criteria_valuation_plan,
    validate_criteria_valuation_plan,
)
from src.criteria_valuation_package import (
    hot_section_demo_criteria_valuation_package,
    validate_criteria_valuation_package,
)
from src.criteria_valuation_view_models import (
    hot_section_demo_criteria_valuation_view_model,
    validate_criteria_valuation_view_model,
)
from src.deterministic_estimator_contracts import (
    hot_section_demo_deterministic_estimator_contract_plan,
    validate_deterministic_estimator_contract_plan,
)
from src.evidence_gap_action_worklist import (
    hot_section_demo_evidence_gap_action_worklist_plan,
    validate_evidence_gap_action_worklist_plan,
)


def _phase65_chain() -> dict[str, dict]:
    return {
        "criteria_valuation_plan": hot_section_demo_criteria_valuation_plan(),
        "candidate_criteria_valuation_plan": (
            hot_section_demo_candidate_criteria_valuation_plan()
        ),
        "deterministic_estimator_contract_plan": (
            hot_section_demo_deterministic_estimator_contract_plan()
        ),
        "criteria_result_integration_plan": (
            hot_section_demo_criteria_result_integration_plan()
        ),
        "criteria_coverage_summary_plan": (
            hot_section_demo_criteria_coverage_summary_plan()
        ),
        "evidence_gap_action_worklist_plan": (
            hot_section_demo_evidence_gap_action_worklist_plan()
        ),
        "criteria_valuation_package": hot_section_demo_criteria_valuation_package(),
        "criteria_valuation_view_model": hot_section_demo_criteria_valuation_view_model(),
    }


def collect_keys(obj: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            keys.add(str(key))
            keys.update(collect_keys(value))
    elif isinstance(obj, list):
        for item in obj:
            keys.update(collect_keys(item))
    return keys


def collect_values_for_key(obj: object, key: str) -> list[object]:
    values: list[object] = []
    if isinstance(obj, dict):
        for item_key, value in obj.items():
            if item_key == key:
                values.append(value)
            values.extend(collect_values_for_key(value, key))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(collect_values_for_key(item, key))
    return values


def assert_live_flags_disabled(obj: dict) -> None:
    for field_name in (
        "live_model_call_allowed",
        "live_source_retrieval_allowed",
        "measurement_execution_allowed",
    ):
        if field_name in obj:
            assert obj[field_name] is False


def test_full_phase65_chain_validates_with_warnings_allowed() -> None:
    chain = _phase65_chain()
    validations = [
        validate_criteria_valuation_plan(chain["criteria_valuation_plan"]),
        validate_candidate_criteria_valuation_plan(
            chain["candidate_criteria_valuation_plan"]
        ),
        validate_deterministic_estimator_contract_plan(
            chain["deterministic_estimator_contract_plan"]
        ),
        validate_criteria_result_integration_plan(
            chain["criteria_result_integration_plan"]
        ),
        validate_criteria_coverage_summary_plan(
            chain["criteria_coverage_summary_plan"]
        ),
        validate_evidence_gap_action_worklist_plan(
            chain["evidence_gap_action_worklist_plan"]
        ),
        validate_criteria_valuation_package(chain["criteria_valuation_package"]),
        validate_criteria_valuation_view_model(
            chain["criteria_valuation_view_model"]
        ),
    ]

    assert all(validation["is_valid"] is True for validation in validations)


def test_full_phase65_chain_preserves_three_hot_section_candidates() -> None:
    chain = _phase65_chain()
    view_model = chain["criteria_valuation_view_model"]

    assert chain["candidate_criteria_valuation_plan"]["candidate_count"] == 3
    assert chain["criteria_result_integration_plan"]["candidate_count"] == 3
    assert chain["criteria_coverage_summary_plan"]["candidate_count"] == 3
    assert chain["criteria_valuation_package"]["candidate_count"] == 3
    assert view_model["candidate_count"] == 3
    assert len(view_model["candidate_summary_cards"]) == 3


def test_full_phase65_chain_keeps_live_calls_disabled() -> None:
    for obj in _phase65_chain().values():
        assert_live_flags_disabled(obj)


def test_full_phase65_chain_remains_placeholder_only_or_gap_review_ready() -> None:
    chain = _phase65_chain()
    package = chain["criteria_valuation_package"]
    view_model = chain["criteria_valuation_view_model"]

    assert chain["criteria_result_integration_plan"]["populated_value_count"] == 0
    assert chain["criteria_coverage_summary_plan"]["populated_value_count"] == 0
    assert package["package_status"] in {"placeholder_only", "partial_coverage"}
    assert package["readiness_summary"]["readiness_level"] in {
        "placeholder_only",
        "ready_with_gaps",
    }
    assert view_model["evidence_gap_rows"]
    assert view_model["action_worklist_rows"]


def test_full_phase65_chain_contains_expected_hot_section_criteria() -> None:
    view_model = _phase65_chain()["criteria_valuation_view_model"]
    criterion_ids = {
        row["cells"]["criterion_id"] for row in view_model["criterion_value_rows"]
    }

    assert {
        "temperature_capability",
        "oxidation_resistance",
        "coating_spallation_risk",
        "gradient_transition_risk",
        "manufacturability",
        "lifecycle_cost",
        "embodied_carbon",
        "qualification_risk",
    }.issubset(criterion_ids)


def test_full_phase65_chain_contains_expected_action_types() -> None:
    view_model = _phase65_chain()["criteria_valuation_view_model"]
    action_types = {
        row["cells"]["action_type"] for row in view_model["action_worklist_rows"]
    }
    gap_types = set(
        collect_values_for_key(
            _phase65_chain()["criteria_valuation_package"]["evidence_gap_records"],
            "gap_type",
        )
    )

    assert {"deterministic_estimator", "literature_evidence_review"}.issubset(
        action_types
    )
    if "missing_model_provenance" in gap_types:
        assert "computational_model" in action_types


def test_full_phase65_chain_has_safety_badges() -> None:
    view_model = _phase65_chain()["criteria_valuation_view_model"]
    labels = {badge["label"].lower() for badge in view_model["badges"]}

    assert "live model calls disabled" in labels
    assert "live source retrieval disabled" in labels
    assert "measurement execution disabled" in labels
    assert "decision-support only" in labels
    assert "no certification approval implied" in labels


def test_full_phase65_chain_has_no_forbidden_claim_or_ranking_fields() -> None:
    chain = _phase65_chain()
    forbidden = {
        "certification_approval",
        "qualification_approval",
        "approved",
        "certified",
        "rank",
        "winner",
        "best_candidate",
        "score",
    }

    assert collect_keys(chain["criteria_valuation_package"]).isdisjoint(forbidden)
    assert collect_keys(chain["criteria_valuation_view_model"]).isdisjoint(forbidden)


def test_phase65_smoke_file_does_not_import_forbidden_runtime_modules() -> None:
    source = Path(__file__).read_text()

    assert "import " + "app" not in source
    assert "import " + "stream" + "lit" not in source
    assert "phase6_decision" + "_cockpit_prototype" not in source
