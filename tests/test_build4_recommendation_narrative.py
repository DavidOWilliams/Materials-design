import json

from src.coating_vs_gradient_diagnostics import attach_coating_vs_gradient_diagnostic
from src.decision_readiness import attach_decision_readiness
from src.optimisation.deterministic_optimizer import attach_deterministic_optimisation
from src.process_route_enrichment import attach_process_route_enrichment
from src.recommendation_narrative import (
    attach_recommendation_narrative,
    build_candidate_narrative_card,
    build_recommendation_narrative,
    classify_narrative_role,
    render_recommendation_narrative_markdown,
)
from src.surface_function_model import attach_surface_function_profiles
from src.ui_view_models import package_to_json_safe_dict
from src.vertical_slices.ceramics_first import build_ceramics_first_candidate_package


def _candidate(readiness_status="usable_as_reference", maturity="B"):
    return {
        "candidate_id": "candidate-1",
        "candidate_class": "coating_enabled",
        "system_architecture_type": "substrate_plus_coating",
        "system_name": "Candidate 1",
        "evidence_maturity": maturity,
        "decision_readiness": {
            "readiness_status": readiness_status,
            "readiness_category": "strong_engineering_analogue",
            "readiness_label": "Strong engineering analogue",
            "evidence_maturity": maturity,
            "allowed_use": "Use as reference.",
            "required_next_evidence": ["validation evidence"],
            "constraints": [],
        },
    }


def _package():
    package = build_ceramics_first_candidate_package()
    package = attach_process_route_enrichment(package)
    package = attach_surface_function_profiles(package)
    package = attach_deterministic_optimisation(package)
    package = attach_coating_vs_gradient_diagnostic(package)
    package = attach_decision_readiness(package)
    return package


def test_classify_narrative_role_maps_reference_and_low_maturity_roles():
    assert classify_narrative_role(_candidate("usable_as_reference", "B"))["narrative_role"] == (
        "mature_comparison_reference"
    )
    assert classify_narrative_role(_candidate("research_only", "F"))["narrative_role"] == "research_only_option"
    assert classify_narrative_role(_candidate("exploratory_only", "E"))["narrative_role"] == "exploratory_option"


def test_build_candidate_narrative_card_marks_not_final_recommendation():
    card = build_candidate_narrative_card(_candidate())

    assert card["not_a_final_recommendation"] is True
    assert card["candidate_id"] == "candidate-1"
    assert card["responsible_use"]


def test_build_recommendation_narrative_preserves_candidate_count_and_groups_candidates():
    package = _package()
    narrative = build_recommendation_narrative(package)

    assert narrative["narrative_status"] == "controlled_narrative_no_final_recommendation"
    assert len(narrative["candidate_narrative_cards"]) == len(package["candidate_systems"])
    assert narrative["mature_comparison_references"]
    assert narrative["exploratory_options"] or narrative["research_only_options"]
    assert narrative["research_only_options"]


def test_attach_recommendation_narrative_preserves_package_boundaries():
    package = _package()
    attached = attach_recommendation_narrative(package)

    assert [candidate["candidate_id"] for candidate in attached["candidate_systems"]] == [
        candidate["candidate_id"] for candidate in package["candidate_systems"]
    ]
    assert attached["ranked_recommendations"] == []
    assert attached["pareto_front"] == []
    assert attached["recommendation_narrative"]
    assert all("recommendation_narrative_card" in candidate for candidate in attached["candidate_systems"])


def test_render_recommendation_narrative_markdown_contains_required_safety_phrases():
    markdown = render_recommendation_narrative_markdown(build_recommendation_narrative(_package())).lower()

    assert "not a final recommendation" in markdown
    assert "no winner selected" in markdown
    assert "not qualification or certification approval" in markdown
    assert "no final ranking" in markdown


def test_recommendation_narrative_package_remains_json_safe_and_non_generating():
    attached = attach_recommendation_narrative(_package())

    json.dumps(package_to_json_safe_dict(attached))
    assert attached["optimisation_summary"]["generated_candidate_count"] == 0
    assert attached["optimisation_summary"]["live_model_calls_made"] is False
