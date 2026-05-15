from copy import deepcopy

from src.phase5_feedback_records import (
    build_feedback_record_package_from_export_package,
    build_feedback_templates_from_export_package,
    candidate_lookup_from_export_package,
    controlled_value,
    count_by_key,
    feedback_record_from_candidate_summary,
    follow_up_required_for_record,
    group_feedback_by_candidate,
    normalise_feedback_record,
    normalise_token,
    record_status_for_feedback,
    run_phase5_feedback_records,
    safety_flags_for_record,
)


def _candidate_summary(candidate_id: str = "C-1") -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"System {candidate_id}",
        "headline": f"System {candidate_id} - Validation-needed option",
        "tier_label": "Validation-needed option",
        "frontier_status": "on_frontier",
        "evidence_band": "engineering_reference",
        "plan_status": "validation_needs_available",
        "research_mode_exposure": False,
        "badge_labels": ["Validation-needed option", "No certification claim"],
        "key_metrics": {"validation_need_count": "3"},
        "priority_actions": ["Review frontier trade-offs.", "Confirm evidence basis."],
        "caution_summary": ["No certification or qualification approval is implied."],
        "validation_need_count": 3,
        "warnings": [],
    }


def _export_package(summaries: list[dict] | None = None) -> dict:
    candidate_summaries = summaries if summaries is not None else [_candidate_summary("C-1")]
    return {
        "manifest": {"schema_version": "phase5_cockpit_review_export_v1"},
        "candidate_summaries": candidate_summaries,
        "warnings": [],
    }


def _feedback(candidate_id: str = "C-1", **overrides) -> dict:
    record = {
        "candidate_id": candidate_id,
        "reviewer_id": "reviewer-1",
        "reviewer_role": "materials",
        "feedback_type": "comment",
        "feedback_text": "Looks reviewable.",
        "decision_position": "accept_for_review",
    }
    record.update(overrides)
    return record


def _pipeline_candidate(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"Nickel DED System {candidate_id}",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "limiting_factors": [],
    }


def test_normalise_token_lowercases_and_replaces_spaces_hyphens():
    assert normalise_token(" C-1 Review Note ") == "c_1_review_note"


def test_controlled_value_returns_allowed_or_default():
    assert controlled_value("Evidence Request", ["evidence_request"], "comment") == (
        "evidence_request"
    )
    assert controlled_value("other", ["comment"], "comment") == "comment"


def test_count_by_key_preserves_first_appearance_order():
    counts = count_by_key(
        [
            {"feedback_type": "concern"},
            {"feedback_type": "comment"},
            {"feedback_type": "concern"},
            {},
        ],
        "feedback_type",
    )

    assert list(counts.items()) == [("concern", 2), ("comment", 1), ("unknown", 1)]


def test_record_status_returns_draft_when_text_empty():
    assert record_status_for_feedback(
        feedback_text="",
        decision_position="accept_for_review",
        feedback_type="comment",
    ) == "draft_feedback"


def test_record_status_returns_follow_up_for_more_evidence_position():
    assert record_status_for_feedback(
        feedback_text="Please add coupon evidence.",
        decision_position="request_more_evidence",
        feedback_type="comment",
    ) == "needs_follow_up"


def test_record_status_returns_follow_up_for_request_and_question_types():
    for feedback_type in ("evidence_request", "validation_request", "question"):
        assert record_status_for_feedback(
            feedback_text="Please check.",
            decision_position="no_position_recorded",
            feedback_type=feedback_type,
        ) == "needs_follow_up"


def test_follow_up_required_detects_needs_follow_up():
    assert follow_up_required_for_record({"record_status": "needs_follow_up"}) is True


def test_safety_flags_include_required_no_approval_flags():
    flags = safety_flags_for_record({"safety_flags": ["custom_flag"]})

    assert "custom_flag" in flags
    assert "no_certification_approval" in flags
    assert "no_qualification_approval" in flags
    assert "no_final_recommendation" in flags


def test_candidate_lookup_from_export_package_builds_lookup():
    lookup = candidate_lookup_from_export_package(
        _export_package([_candidate_summary("C-1"), _candidate_summary("C-2")])
    )

    assert list(lookup) == ["C-1", "C-2"]
    assert lookup["C-1"]["system_name"] == "System C-1"


def test_feedback_record_from_candidate_summary_builds_deterministic_id():
    record = feedback_record_from_candidate_summary(
        _candidate_summary("C-1"),
        feedback_type="question",
        feedback_text="What evidence supports this?",
        sequence_number=4,
    )

    assert record["feedback_id"] == "c_1:feedback:4:question"


def test_feedback_record_from_candidate_summary_links_context_fields():
    record = feedback_record_from_candidate_summary(
        _candidate_summary("C-1"),
        feedback_text="Looks reviewable.",
    )

    assert record["linked_tier_label"] == "Validation-needed option"
    assert record["linked_frontier_status"] == "on_frontier"
    assert record["linked_plan_status"] == "validation_needs_available"
    assert record["linked_priority_actions"] == [
        "Review frontier trade-offs.",
        "Confirm evidence basis.",
    ]


def test_feedback_record_from_candidate_summary_warns_on_empty_text():
    record = feedback_record_from_candidate_summary(_candidate_summary("C-1"))

    assert any("empty" in warning for warning in record["warnings"])


def test_feedback_record_from_candidate_summary_warns_for_reject_position():
    record = feedback_record_from_candidate_summary(
        _candidate_summary("C-1"),
        feedback_text="Out of scope.",
        decision_position="reject_from_current_scope",
    )

    assert any("review position only" in warning for warning in record["warnings"])


def test_build_feedback_templates_creates_one_draft_per_candidate_in_order():
    records = build_feedback_templates_from_export_package(
        _export_package([_candidate_summary("C-2"), _candidate_summary("C-1")])
    )

    assert [record["candidate_id"] for record in records] == ["C-2", "C-1"]
    assert [record["record_status"] for record in records] == [
        "draft_feedback",
        "draft_feedback",
    ]


def test_normalise_feedback_record_fills_candidate_fields_from_lookup():
    lookup = candidate_lookup_from_export_package(_export_package([_candidate_summary("C-1")]))

    record = normalise_feedback_record(
        {"candidate_id": "C-1", "feedback_text": "Please review."},
        candidate_lookup=lookup,
    )

    assert record["system_name"] == "System C-1"
    assert record["linked_tier_label"] == "Validation-needed option"
    assert record["linked_priority_actions"] == [
        "Review frontier trade-offs.",
        "Confirm evidence basis.",
    ]


def test_normalise_feedback_record_derives_follow_up_and_safety_flags():
    record = normalise_feedback_record(
        {
            "candidate_id": "C-1",
            "feedback_type": "evidence_request",
            "feedback_text": "Please add evidence.",
        }
    )

    assert record["follow_up_required"] is True
    assert "does_not_change_analysis" in record["safety_flags"]


def test_group_feedback_by_candidate_preserves_order_and_groups_records():
    summaries, unlinked = group_feedback_by_candidate(
        [_candidate_summary("C-2"), _candidate_summary("C-1")],
        [_feedback("C-1"), _feedback("C-2")],
    )

    assert [summary["candidate_id"] for summary in summaries] == ["C-2", "C-1"]
    assert summaries[0]["feedback_records"][0]["candidate_id"] == "C-2"
    assert summaries[1]["feedback_records"][0]["candidate_id"] == "C-1"
    assert unlinked == []


def test_group_feedback_by_candidate_returns_unlinked_records_for_unknown_candidate():
    summaries, unlinked = group_feedback_by_candidate(
        [_candidate_summary("C-1")],
        [_feedback("C-99")],
    )

    assert summaries[0]["feedback_count"] == 0
    assert [record["candidate_id"] for record in unlinked] == ["C-99"]


def test_group_feedback_by_candidate_sets_follow_up_review_state():
    summaries, _ = group_feedback_by_candidate(
        [_candidate_summary("C-1")],
        [_feedback("C-1", feedback_type="question", feedback_text="Why?")],
    )

    assert summaries[0]["review_state"] == "follow_up_required"


def test_build_package_creates_draft_templates_when_no_records_supplied():
    package = build_feedback_record_package_from_export_package(
        _export_package([_candidate_summary("C-1"), _candidate_summary("C-2")])
    )

    assert package["feedback_record_count"] == 2
    assert [summary["feedback_count"] for summary in package["feedback_summaries"]] == [1, 1]
    assert all(
        summary["feedback_records"][0]["record_status"] == "draft_feedback"
        for summary in package["feedback_summaries"]
    )


def test_build_package_uses_supplied_feedback_records_when_provided():
    package = build_feedback_record_package_from_export_package(
        _export_package([_candidate_summary("C-1")]),
        feedback_records=[_feedback("C-1")],
    )

    assert package["feedback_record_count"] == 1
    assert package["feedback_summaries"][0]["feedback_records"][0]["feedback_text"] == (
        "Looks reviewable."
    )


def test_build_package_warns_for_unlinked_feedback():
    package = build_feedback_record_package_from_export_package(
        _export_package([_candidate_summary("C-1")]),
        feedback_records=[_feedback("C-99")],
    )

    assert any("could not be linked" in warning for warning in package["warnings"])


def test_build_package_warns_when_follow_up_required():
    package = build_feedback_record_package_from_export_package(
        _export_package([_candidate_summary("C-1")]),
        feedback_records=[
            _feedback("C-1", feedback_type="evidence_request", feedback_text="Need data.")
        ],
    )

    assert any("require follow-up" in warning for warning in package["warnings"])


def test_build_package_has_no_score_rank_or_winner_fields():
    package = build_feedback_record_package_from_export_package(
        _export_package([_candidate_summary("C-1")]),
        feedback_records=[_feedback("C-1")],
    )

    assert "score" not in package
    assert "rank" not in package
    assert "winner" not in package
    assert "score" not in package["feedback_summaries"][0]
    assert "rank" not in package["feedback_summaries"][0]
    assert "winner" not in package["feedback_summaries"][0]


def test_build_package_does_not_mutate_export_package_or_feedback_records():
    export_package = _export_package([_candidate_summary("C-1")])
    feedback_records = [_feedback("C-1")]
    original_export = deepcopy(export_package)
    original_feedback = deepcopy(feedback_records)

    build_feedback_record_package_from_export_package(
        export_package,
        feedback_records=feedback_records,
    )

    assert export_package == original_export
    assert feedback_records == original_feedback


def test_run_phase5_feedback_records_preserves_candidate_order():
    package = run_phase5_feedback_records([
        _pipeline_candidate("C-1"),
        _pipeline_candidate("C-2"),
    ])

    assert [summary["candidate_id"] for summary in package["feedback_summaries"]] == [
        "C-1",
        "C-2",
    ]


def test_run_phase5_feedback_records_includes_research_mode_warning():
    package = run_phase5_feedback_records([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in package["warnings"])


def test_run_phase5_feedback_records_does_not_mutate_inputs():
    candidates = [_pipeline_candidate("C-1")]
    feedback_records = [_feedback("C-1", feedback_type="question", feedback_text="Why?")]
    original_candidates = deepcopy(candidates)
    original_feedback = deepcopy(feedback_records)

    run_phase5_feedback_records(candidates, feedback_records=feedback_records)

    assert candidates == original_candidates
    assert feedback_records == original_feedback
