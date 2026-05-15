from copy import deepcopy

from src.phase5_decision_cockpit_view_models import (
    badges_for_candidate_plan,
    build_badge,
    build_candidate_cockpit_card,
    build_decision_cockpit_view_model_from_validation_run,
    build_metric,
    chart_from_counts,
    charts_for_validation_run,
    caution_summary_for_plan,
    count_by_key,
    detail_sections_for_plan,
    metrics_for_candidate_plan,
    overview_metrics_for_validation_run,
    priority_validation_needs,
    review_actions_for_plan,
    run_phase5_decision_cockpit_view_model,
    tone_for_plan_status,
    tone_for_priority,
    tone_for_tier,
)


def _need(
    need_id: str,
    priority: str,
    *,
    category: str = "general_engineering_review",
    validation_activity: str | None = None,
    warnings: list[str] | None = None,
) -> dict:
    return {
        "need_id": need_id,
        "candidate_id": "C-1",
        "category": category,
        "priority": priority,
        "validation_activity": validation_activity or f"Review {need_id}.",
        "trigger": need_id,
        "status": "proposed_validation_need",
        "warnings": warnings if warnings is not None else [],
    }


def _plan(
    candidate_id: str = "C-1",
    *,
    tier: str = "validation_needed_option",
    tier_label: str = "Validation-needed option",
    plan_status: str = "validation_needs_available",
    research_mode_exposure: bool = False,
    validation_needs: list[dict] | None = None,
    warnings: list[str] | None = None,
) -> dict:
    needs = validation_needs if validation_needs is not None else [
        _need("need-low", "low"),
        _need("need-high", "high", warnings=["Need warning"]),
        _need("need-medium", "medium"),
    ]
    return {
        "candidate_id": candidate_id,
        "system_name": f"System {candidate_id}",
        "tier": tier,
        "tier_label": tier_label,
        "frontier_status": "on_frontier",
        "evidence_maturity": "C",
        "evidence_band": "engineering_reference",
        "research_mode_exposure": research_mode_exposure,
        "validation_need_count": len(needs),
        "validation_needs": needs,
        "plan_status": plan_status,
        "notes": [],
        "warnings": warnings if warnings is not None else ["Plan warning"],
    }


def _validation_run(plans: list[dict]) -> dict:
    high = sum(
        1
        for plan in plans
        for need in plan["validation_needs"]
        if need["priority"] == "high"
    )
    medium = sum(
        1
        for plan in plans
        for need in plan["validation_needs"]
        if need["priority"] == "medium"
    )
    low = sum(
        1
        for plan in plans
        for need in plan["validation_needs"]
        if need["priority"] == "low"
    )
    category_counts: dict[str, int] = {}
    for plan in plans:
        for need in plan["validation_needs"]:
            category_counts[need["category"]] = category_counts.get(need["category"], 0) + 1

    return {
        "candidate_count": len(plans),
        "plan_count": len(plans),
        "validation_need_count": sum(len(plan["validation_needs"]) for plan in plans),
        "research_mode_enabled": False,
        "candidate_validation_needs": plans,
        "validation_summary": {
            "by_plan_status": count_by_key(plans, "plan_status"),
            "by_category": category_counts,
            "by_priority": {"high": high, "medium": medium, "low": low},
            "research_mode_plan_count": sum(
                1
                for plan in plans
                if plan["plan_status"] == "research_mode_validation_required"
            ),
        },
        "notes": [],
        "warnings": ["Run warning"],
    }


def _pipeline_candidate(candidate_id: str) -> dict:
    return {
        "candidate_id": candidate_id,
        "system_name": f"Nickel DED System {candidate_id}",
        "candidate_class": "metallic",
        "substrate_family": "nickel_alloy",
        "process_route": {"route_name": "DED"},
        "limiting_factors": [],
    }


def test_tone_for_tier_maps_mature_reference_to_positive():
    assert tone_for_tier("mature_reference_option") == "positive"


def test_tone_for_tier_maps_research_only_to_high_caution():
    assert tone_for_tier("research_only_suggestion") == "high_caution"


def test_tone_for_plan_status_maps_research_required_to_high_caution():
    assert tone_for_plan_status("research_mode_validation_required") == "high_caution"


def test_tone_for_priority_maps_high_and_low():
    assert tone_for_priority("high") == "high_caution"
    assert tone_for_priority("low") == "neutral"


def test_build_badge_returns_expected_fields():
    badge = build_badge("tier", label="Tier", tone="positive", tooltip="tip")

    assert badge == {
        "badge_id": "tier",
        "label": "Tier",
        "tone": "positive",
        "tooltip": "tip",
    }


def test_build_metric_converts_numeric_value_to_string():
    metric = build_metric("count", label="Count", value=3, tone="info")

    assert metric["value"] == "3"


def test_badges_for_candidate_plan_includes_core_badges():
    badge_ids = [badge["badge_id"] for badge in badges_for_candidate_plan(_plan())]

    assert badge_ids == [
        "tier",
        "frontier_status",
        "evidence_band",
        "plan_status",
        "no_certification_claim",
    ]


def test_badges_for_candidate_plan_includes_research_badge_when_exposed():
    badges = badges_for_candidate_plan(
        _plan(
            research_mode_exposure=True,
            plan_status="research_mode_validation_required",
        )
    )

    assert "research_mode_exposure" in [badge["badge_id"] for badge in badges]


def test_metrics_for_candidate_plan_counts_priority_validation_needs():
    metrics = {
        metric["metric_id"]: metric["value"]
        for metric in metrics_for_candidate_plan(_plan())
    }

    assert metrics["high_priority_need_count"] == "1"
    assert metrics["medium_priority_need_count"] == "1"
    assert metrics["low_priority_need_count"] == "1"


def test_priority_validation_needs_sorts_by_priority_and_preserves_order_within_priority():
    plan = _plan(
        validation_needs=[
            _need("low-1", "low"),
            _need("high-1", "high"),
            _need("medium-1", "medium"),
            _need("high-2", "high"),
        ]
    )

    assert [need["need_id"] for need in priority_validation_needs(plan)] == [
        "high-1",
        "high-2",
        "medium-1",
        "low-1",
    ]


def test_priority_validation_needs_respects_limit():
    plan = _plan(
        validation_needs=[
            _need("high-1", "high"),
            _need("high-2", "high"),
            _need("medium-1", "medium"),
        ]
    )

    assert len(priority_validation_needs(plan, limit=2)) == 2


def test_caution_summary_deduplicates_and_includes_limitation():
    plan = _plan(
        warnings=["Shared warning"],
        validation_needs=[
            _need("need-1", "high", warnings=["Shared warning", "Need warning"]),
        ],
    )

    cautions = caution_summary_for_plan(plan)
    assert cautions.count("Shared warning") == 1
    assert "No certification or qualification approval is implied." in cautions


def test_review_actions_for_plan_returns_activities_and_limits_to_five():
    plan = _plan(
        validation_needs=[
            _need(f"need-{index}", "high", validation_activity=f"Action {index}")
            for index in range(7)
        ]
    )

    actions = review_actions_for_plan(plan)
    assert actions == ["Action 0", "Action 1", "Action 2", "Action 3", "Action 4"]


def test_detail_sections_for_plan_includes_required_sections():
    sections = detail_sections_for_plan(_plan())

    assert [section["title"] for section in sections] == [
        "Tier and evidence",
        "Validation needs",
        "Cautions and warnings",
        "Decision-support limitations",
    ]


def test_build_candidate_cockpit_card_preserves_identity_and_tier():
    card = build_candidate_cockpit_card(_plan("C-9"))

    assert card["candidate_id"] == "C-9"
    assert card["system_name"] == "System C-9"
    assert card["tier"] == "validation_needed_option"


def test_build_candidate_cockpit_card_does_not_mutate_input_plan():
    plan = _plan()
    original = deepcopy(plan)

    build_candidate_cockpit_card(plan)

    assert plan == original


def test_count_by_key_counts_in_first_appearance_order():
    counts = count_by_key(
        [
            {"tier": "b"},
            {"tier": "a"},
            {"tier": "b"},
            {},
        ],
        "tier",
    )

    assert list(counts.items()) == [("b", 2), ("a", 1), ("unknown", 1)]


def test_chart_from_counts_creates_ui_ready_bar_data_without_rendering():
    chart = chart_from_counts(
        "tier_distribution",
        title="Tier Distribution",
        counts={"a": 2, "b": 1},
    )

    assert chart["chart_type"] == "bar"
    assert chart["data"] == [{"label": "a", "value": 2}, {"label": "b", "value": 1}]
    assert any("no chart is rendered" in note for note in chart["notes"])


def test_overview_metrics_for_validation_run_includes_candidate_and_need_counts():
    metrics = {
        metric["metric_id"]: metric["value"]
        for metric in overview_metrics_for_validation_run(_validation_run([_plan()]))
    }

    assert metrics["candidate_count"] == "1"
    assert metrics["validation_need_count"] == "3"


def test_charts_for_validation_run_creates_four_chart_data_objects():
    charts = charts_for_validation_run(_validation_run([_plan()]))

    assert [chart["chart_id"] for chart in charts] == [
        "plan_status_distribution",
        "validation_category_distribution",
        "validation_priority_distribution",
        "tier_distribution",
    ]


def test_build_view_model_from_validation_run_preserves_card_order():
    view_model = build_decision_cockpit_view_model_from_validation_run(
        _validation_run([_plan("C-2"), _plan("C-1")])
    )

    assert [card["candidate_id"] for card in view_model["cards"]] == ["C-2", "C-1"]


def test_build_view_model_from_validation_run_warns_when_no_cards_exist():
    view_model = build_decision_cockpit_view_model_from_validation_run(_validation_run([]))

    assert any("No candidate cockpit cards" in warning for warning in view_model["global_warnings"])


def test_build_view_model_from_validation_run_has_no_rank_score_or_winner_fields():
    view_model = build_decision_cockpit_view_model_from_validation_run(
        _validation_run([_plan()])
    )

    assert "rank" not in view_model
    assert "score" not in view_model
    assert "winner" not in view_model
    for card in view_model["cards"]:
        assert "rank" not in card
        assert "score" not in card
        assert "winner" not in card


def test_build_view_model_from_validation_run_does_not_mutate_validation_run():
    validation_run = _validation_run([_plan()])
    original = deepcopy(validation_run)

    build_decision_cockpit_view_model_from_validation_run(validation_run)

    assert validation_run == original


def test_run_phase5_decision_cockpit_view_model_preserves_candidate_order():
    view_model = run_phase5_decision_cockpit_view_model(
        [_pipeline_candidate("C-1"), _pipeline_candidate("C-2")]
    )

    assert [card["candidate_id"] for card in view_model["cards"]] == ["C-1", "C-2"]


def test_run_phase5_decision_cockpit_view_model_includes_research_mode_warning():
    view_model = run_phase5_decision_cockpit_view_model([], research_mode_enabled=True)

    assert any("Research mode is enabled" in warning for warning in view_model["global_warnings"])


def test_run_phase5_decision_cockpit_view_model_does_not_mutate_input_candidates():
    candidates = [_pipeline_candidate("C-1"), _pipeline_candidate("C-2")]
    original = deepcopy(candidates)

    run_phase5_decision_cockpit_view_model(candidates)

    assert candidates == original
