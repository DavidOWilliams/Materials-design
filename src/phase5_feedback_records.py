from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any, TypedDict

from src.phase5_cockpit_review_export import run_phase5_cockpit_review_export


FEEDBACK_SCHEMA_VERSION = "phase5_feedback_records_v1"

FEEDBACK_TYPES: tuple[str, ...] = (
    "comment",
    "concern",
    "question",
    "evidence_request",
    "validation_request",
    "decision_note",
)

DECISION_POSITIONS: tuple[str, ...] = (
    "no_position_recorded",
    "accept_for_review",
    "request_more_evidence",
    "retain_for_niche_review",
    "park_candidate",
    "reject_from_current_scope",
)

RECORD_STATUSES: tuple[str, ...] = (
    "draft_feedback",
    "recorded_feedback",
    "needs_follow_up",
    "resolved_feedback",
)

REVIEW_STATES: tuple[str, ...] = (
    "no_feedback_recorded",
    "feedback_recorded",
    "follow_up_required",
)

SAFETY_FLAGS: tuple[str, ...] = (
    "does_not_change_analysis",
    "no_certification_approval",
    "no_qualification_approval",
    "no_final_recommendation",
    "engineering_review_required",
)


class FeedbackRecord(TypedDict, total=False):
    feedback_id: str
    candidate_id: str
    system_name: str
    reviewer_id: str
    reviewer_role: str
    feedback_type: str
    feedback_text: str
    decision_position: str
    record_status: str
    linked_tier_label: str
    linked_frontier_status: str
    linked_plan_status: str
    linked_evidence_band: str
    linked_priority_actions: list[str]
    follow_up_required: bool
    safety_flags: list[str]
    notes: list[str]
    warnings: list[str]


class CandidateFeedbackSummary(TypedDict, total=False):
    candidate_id: str
    system_name: str
    feedback_count: int
    follow_up_count: int
    review_state: str
    feedback_types: dict[str, int]
    decision_positions: dict[str, int]
    feedback_records: list[FeedbackRecord]
    notes: list[str]
    warnings: list[str]


class FeedbackRecordPackage(TypedDict, total=False):
    package_type: str
    schema_version: str
    candidate_count: int
    feedback_record_count: int
    follow_up_count: int
    feedback_summaries: list[CandidateFeedbackSummary]
    unlinked_feedback_records: list[FeedbackRecord]
    notes: list[str]
    warnings: list[str]


def _as_string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    if not all(isinstance(item, str) for item in value):
        return []
    return list(value)


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def normalise_token(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def controlled_value(value: Any, allowed: Sequence[str], default: str) -> str:
    token = normalise_token(value)
    return token if token in allowed else default


def count_by_key(items: Sequence[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = _as_string(item.get(key), "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


def record_status_for_feedback(
    *,
    feedback_text: str,
    decision_position: str,
    feedback_type: str,
) -> str:
    if not _as_string(feedback_text):
        return "draft_feedback"
    if decision_position == "request_more_evidence":
        return "needs_follow_up"
    if feedback_type in ("evidence_request", "validation_request", "question"):
        return "needs_follow_up"
    return "recorded_feedback"


def follow_up_required_for_record(record: Mapping[str, Any]) -> bool:
    if record.get("record_status") == "needs_follow_up":
        return True
    if record.get("decision_position") == "request_more_evidence":
        return True
    if record.get("feedback_type") in ("evidence_request", "validation_request", "question"):
        return True
    return False


def safety_flags_for_record(record: Mapping[str, Any]) -> list[str]:
    flags: list[str] = []
    for flag in _string_list(record.get("safety_flags")):
        _append_unique(flags, flag)
    for flag in SAFETY_FLAGS:
        _append_unique(flags, flag)
    return flags


def _candidate_summaries(export_package: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    summaries = export_package.get("candidate_summaries")
    if not isinstance(summaries, list):
        return []
    return [summary for summary in summaries if isinstance(summary, Mapping)]


def candidate_lookup_from_export_package(
    export_package: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    lookup: dict[str, Mapping[str, Any]] = {}
    for summary in _candidate_summaries(export_package):
        candidate_id = _as_string(summary.get("candidate_id"))
        if candidate_id:
            lookup[candidate_id] = summary
    return lookup


def _feedback_id(candidate_id: str, sequence_number: int, feedback_type: str) -> str:
    return (
        f"{normalise_token(candidate_id) or 'unknown_candidate'}:"
        f"feedback:{sequence_number}:{normalise_token(feedback_type) or 'comment'}"
    )


def feedback_record_from_candidate_summary(
    candidate_summary: Mapping[str, Any],
    *,
    reviewer_id: str = "anonymous_reviewer",
    reviewer_role: str = "",
    feedback_type: str = "comment",
    feedback_text: str = "",
    decision_position: str = "no_position_recorded",
    sequence_number: int = 1,
) -> FeedbackRecord:
    candidate_id = _as_string(candidate_summary.get("candidate_id"), "unknown_candidate")
    controlled_type = controlled_value(feedback_type, FEEDBACK_TYPES, "comment")
    controlled_position = controlled_value(
        decision_position,
        DECISION_POSITIONS,
        "no_position_recorded",
    )
    text = _as_string(feedback_text)
    status = record_status_for_feedback(
        feedback_text=text,
        decision_position=controlled_position,
        feedback_type=controlled_type,
    )
    warnings: list[str] = []
    if not text:
        warnings.append("Feedback text is empty; record remains a draft.")
    if controlled_position == "reject_from_current_scope":
        warnings.append("Reject-from-current-scope is a review position only; it does not alter analysis.")

    record: FeedbackRecord = {
        "feedback_id": _feedback_id(candidate_id, sequence_number, controlled_type),
        "candidate_id": candidate_id,
        "system_name": _as_string(candidate_summary.get("system_name"), "unknown_system"),
        "reviewer_id": _as_string(reviewer_id, "anonymous_reviewer"),
        "reviewer_role": _as_string(reviewer_role),
        "feedback_type": controlled_type,
        "feedback_text": text,
        "decision_position": controlled_position,
        "record_status": status,
        "linked_tier_label": _as_string(candidate_summary.get("tier_label")),
        "linked_frontier_status": _as_string(candidate_summary.get("frontier_status")),
        "linked_plan_status": _as_string(candidate_summary.get("plan_status")),
        "linked_evidence_band": _as_string(candidate_summary.get("evidence_band")),
        "linked_priority_actions": _string_list(
            deepcopy(candidate_summary.get("priority_actions"))
        ),
        "notes": [
            "Feedback record does not modify the analysis output.",
            "No recommendation, qualification approval or certification approval is implied.",
        ],
        "warnings": warnings,
    }
    record["follow_up_required"] = follow_up_required_for_record(record)
    record["safety_flags"] = safety_flags_for_record(record)
    return record


def build_feedback_templates_from_export_package(
    export_package: Mapping[str, Any],
    *,
    reviewer_id: str = "anonymous_reviewer",
    reviewer_role: str = "",
) -> list[FeedbackRecord]:
    records: list[FeedbackRecord] = []
    for index, summary in enumerate(_candidate_summaries(export_package), start=1):
        records.append(
            feedback_record_from_candidate_summary(
                summary,
                reviewer_id=reviewer_id,
                reviewer_role=reviewer_role,
                feedback_type="comment",
                feedback_text="",
                decision_position="no_position_recorded",
                sequence_number=index,
            )
        )
    return records


def _lookup_value(
    candidate_summary: Mapping[str, Any] | None,
    key: str,
    default: str = "",
) -> str:
    if candidate_summary is None:
        return default
    return _as_string(candidate_summary.get(key), default)


def normalise_feedback_record(
    record: Mapping[str, Any],
    *,
    candidate_lookup: Mapping[str, Mapping[str, Any]] | None = None,
    sequence_number: int = 1,
) -> FeedbackRecord:
    candidate_id = _as_string(record.get("candidate_id"), "unknown_candidate")
    linked_summary = (
        candidate_lookup.get(candidate_id)
        if candidate_lookup is not None and candidate_id in candidate_lookup
        else None
    )
    feedback_type = controlled_value(record.get("feedback_type"), FEEDBACK_TYPES, "comment")
    decision_position = controlled_value(
        record.get("decision_position"),
        DECISION_POSITIONS,
        "no_position_recorded",
    )
    feedback_text = _as_string(record.get("feedback_text"))
    supplied_status = controlled_value(record.get("record_status"), RECORD_STATUSES, "")
    record_status = supplied_status or record_status_for_feedback(
        feedback_text=feedback_text,
        decision_position=decision_position,
        feedback_type=feedback_type,
    )
    warnings = _string_list(deepcopy(record.get("warnings")))
    if not feedback_text:
        _append_unique(warnings, "Feedback text is empty; record remains a draft.")
    if decision_position == "reject_from_current_scope":
        _append_unique(
            warnings,
            "Reject-from-current-scope is a review position only; it does not alter analysis.",
        )

    normalised: FeedbackRecord = {
        "feedback_id": _as_string(
            record.get("feedback_id"),
            _feedback_id(candidate_id, sequence_number, feedback_type),
        ),
        "candidate_id": candidate_id,
        "system_name": _as_string(
            record.get("system_name"),
            _lookup_value(linked_summary, "system_name", "unknown_system"),
        ),
        "reviewer_id": _as_string(record.get("reviewer_id"), "anonymous_reviewer"),
        "reviewer_role": _as_string(record.get("reviewer_role")),
        "feedback_type": feedback_type,
        "feedback_text": feedback_text,
        "decision_position": decision_position,
        "record_status": record_status,
        "linked_tier_label": _as_string(
            record.get("linked_tier_label"),
            _lookup_value(linked_summary, "tier_label"),
        ),
        "linked_frontier_status": _as_string(
            record.get("linked_frontier_status"),
            _lookup_value(linked_summary, "frontier_status"),
        ),
        "linked_plan_status": _as_string(
            record.get("linked_plan_status"),
            _lookup_value(linked_summary, "plan_status"),
        ),
        "linked_evidence_band": _as_string(
            record.get("linked_evidence_band"),
            _lookup_value(linked_summary, "evidence_band"),
        ),
        "linked_priority_actions": _string_list(
            deepcopy(record.get("linked_priority_actions"))
        )
        or _string_list(deepcopy(linked_summary.get("priority_actions") if linked_summary else [])),
        "notes": _string_list(deepcopy(record.get("notes"))) or [
            "Feedback record does not modify the analysis output.",
            "No recommendation, qualification approval or certification approval is implied.",
        ],
        "warnings": warnings,
    }
    normalised["follow_up_required"] = follow_up_required_for_record(normalised)
    normalised["safety_flags"] = safety_flags_for_record(record)
    return normalised


def group_feedback_by_candidate(
    candidate_summaries: Sequence[Mapping[str, Any]],
    feedback_records: Sequence[Mapping[str, Any]],
) -> tuple[list[CandidateFeedbackSummary], list[FeedbackRecord]]:
    lookup = {
        _as_string(summary.get("candidate_id")): summary
        for summary in candidate_summaries
        if _as_string(summary.get("candidate_id"))
    }
    grouped: dict[str, list[FeedbackRecord]] = {candidate_id: [] for candidate_id in lookup}
    unlinked: list[FeedbackRecord] = []

    for index, record in enumerate(feedback_records, start=1):
        normalised = normalise_feedback_record(
            record,
            candidate_lookup=lookup,
            sequence_number=index,
        )
        candidate_id = normalised["candidate_id"]
        if candidate_id in grouped:
            grouped[candidate_id].append(normalised)
        else:
            unlinked.append(normalised)

    summaries: list[CandidateFeedbackSummary] = []
    for summary in candidate_summaries:
        candidate_id = _as_string(summary.get("candidate_id"), "unknown_candidate")
        records = grouped.get(candidate_id, [])
        follow_up_count = sum(1 for record in records if record.get("follow_up_required") is True)
        if not records:
            review_state = "no_feedback_recorded"
        elif follow_up_count:
            review_state = "follow_up_required"
        else:
            review_state = "feedback_recorded"
        warnings: list[str] = []
        for record in records:
            for warning in _string_list(record.get("warnings")):
                _append_unique(warnings, warning)

        summaries.append(
            {
                "candidate_id": candidate_id,
                "system_name": _as_string(summary.get("system_name"), "unknown_system"),
                "feedback_count": len(records),
                "follow_up_count": follow_up_count,
                "review_state": review_state,
                "feedback_types": count_by_key(records, "feedback_type"),
                "decision_positions": count_by_key(records, "decision_position"),
                "feedback_records": records,
                "notes": [
                    "Feedback does not modify analysis, tiers, frontier status or validation needs.",
                    "No recommendation, qualification approval or certification approval is implied.",
                ],
                "warnings": warnings,
            }
        )

    return summaries, unlinked


def build_feedback_record_package_from_export_package(
    export_package: Mapping[str, Any],
    *,
    feedback_records: Sequence[Mapping[str, Any]] | None = None,
    include_draft_templates_when_empty: bool = True,
) -> FeedbackRecordPackage:
    candidate_summaries = _candidate_summaries(export_package)
    if feedback_records:
        records_to_group = list(feedback_records)
    elif include_draft_templates_when_empty:
        records_to_group = build_feedback_templates_from_export_package(export_package)
    else:
        records_to_group = []

    summaries, unlinked = group_feedback_by_candidate(candidate_summaries, records_to_group)
    linked_count = sum(summary.get("feedback_count", 0) for summary in summaries)
    follow_up_count = sum(summary.get("follow_up_count", 0) for summary in summaries)
    follow_up_count += sum(1 for record in unlinked if record.get("follow_up_required") is True)
    feedback_record_count = linked_count + len(unlinked)

    warnings: list[str] = []
    if not candidate_summaries:
        warnings.append("No candidate summaries are available for feedback records.")
    if unlinked:
        warnings.append("One or more feedback records could not be linked to a candidate summary.")
    if follow_up_count:
        warnings.append("One or more feedback records require follow-up.")

    return {
        "package_type": "phase5_feedback_records",
        "schema_version": FEEDBACK_SCHEMA_VERSION,
        "candidate_count": len(candidate_summaries),
        "feedback_record_count": feedback_record_count,
        "follow_up_count": follow_up_count,
        "feedback_summaries": summaries,
        "unlinked_feedback_records": unlinked,
        "notes": [
            "Feedback records are review annotations only.",
            "Feedback records do not modify recommendations, tiers, frontier status or validation needs.",
            "No qualification or certification approval is implied.",
        ],
        "warnings": warnings,
    }


def run_phase5_feedback_records(
    candidates: Sequence[Mapping[str, Any]],
    *,
    feedback_records: Sequence[Mapping[str, Any]] | None = None,
    limiting_factors_by_candidate: Mapping[str, Sequence[str]] | None = None,
    default_limiting_factors: Sequence[str] | None = None,
    research_mode_enabled: bool = False,
) -> FeedbackRecordPackage:
    export_package = run_phase5_cockpit_review_export(
        candidates,
        limiting_factors_by_candidate=limiting_factors_by_candidate,
        default_limiting_factors=default_limiting_factors,
        research_mode_enabled=research_mode_enabled,
    )
    package = build_feedback_record_package_from_export_package(
        export_package,
        feedback_records=feedback_records,
    )
    if research_mode_enabled:
        warnings = list(package.get("warnings", []))
        warnings.append("Research mode is enabled; feedback may refer to research-mode content.")
        package["warnings"] = warnings
    return package
