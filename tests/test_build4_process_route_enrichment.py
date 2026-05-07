import json

from src.process_route_enrichment import (
    attach_process_route_enrichment,
    build_process_route_summary,
    enrich_candidates_with_process_routes,
    infer_process_route_template_id,
    load_process_route_templates,
)
from src.vertical_slices.ceramics_first import build_ceramics_first_candidate_package


def _source_candidates():
    return build_ceramics_first_candidate_package()["candidate_systems"]


def test_process_route_templates_json_loads_and_contains_required_templates():
    templates = load_process_route_templates()

    assert len(templates) >= 14
    assert templates["ni_superalloy_tbc"]["display_name"]
    assert templates["sic_sic_cmc_ebc"]["inspection_plan"]["inspection_burden"] == "high"
    json.dumps(templates)


def test_every_ceramics_first_candidate_gets_known_or_explicit_unknown_route():
    enriched = enrich_candidates_with_process_routes(_source_candidates())

    assert all(candidate["process_route_template_id"] for candidate in enriched)
    assert all(candidate["process_route_details"] for candidate in enriched)
    assert all(candidate["inspection_plan"] for candidate in enriched)
    assert all(candidate["repairability"] for candidate in enriched)
    assert all(candidate["qualification_route"] for candidate in enriched)


def test_candidate_count_and_order_are_preserved():
    candidates = _source_candidates()
    enriched = enrich_candidates_with_process_routes(candidates)

    assert len(enriched) == len(candidates)
    assert [candidate["candidate_id"] for candidate in enriched] == [
        candidate["candidate_id"] for candidate in candidates
    ]


def test_specific_ceramics_first_route_inference_examples():
    by_id = {candidate["candidate_id"]: candidate for candidate in _source_candidates()}

    assert infer_process_route_template_id(by_id["demo_ni_superalloy_bondcoat_tbc_comparison"]) == "ni_superalloy_tbc"
    assert infer_process_route_template_id(by_id["sic_sic_cmc_ebc_anchor"]) == "sic_sic_cmc_ebc"
    assert infer_process_route_template_id(by_id["surface_oxidation_gradient"]) == "surface_oxidation_gradient"


def test_gradient_candidates_expose_high_or_unknown_inspection_and_qualification_concerns():
    enriched = enrich_candidates_with_process_routes(_source_candidates())
    gradient_candidates = [
        candidate for candidate in enriched if candidate["candidate_class"] == "spatially_graded_am"
    ]

    assert gradient_candidates
    assert all(
        candidate["inspection_plan"]["inspection_burden"] in {"high", "unknown"}
        for candidate in gradient_candidates
    )
    assert all(
        candidate["qualification_route"]["qualification_burden"] in {"high", "very_high", "unknown"}
        for candidate in gradient_candidates
    )


def test_build_process_route_summary_returns_route_burden_counts():
    enriched = enrich_candidates_with_process_routes(_source_candidates())
    summary = build_process_route_summary(enriched)

    assert summary["candidate_count"] == len(enriched)
    assert summary["enriched_candidate_count"] == len(enriched)
    assert summary["inspection_burden_counts"]
    assert summary["repairability_level_counts"]
    assert summary["qualification_burden_counts"]
    assert summary["high_inspection_burden_candidate_ids"]
    assert summary["limited_or_poor_repairability_candidate_ids"]
    assert summary["high_or_very_high_qualification_burden_candidate_ids"]


def test_attach_process_route_enrichment_preserves_ranking_and_pareto():
    package = build_ceramics_first_candidate_package()
    package["ranked_recommendations"] = [{"candidate_id": "keep-ranked"}]
    package["pareto_front"] = [{"candidate_id": "keep-pareto"}]

    enriched = attach_process_route_enrichment(package)

    assert enriched["ranked_recommendations"] == [{"candidate_id": "keep-ranked"}]
    assert enriched["pareto_front"] == [{"candidate_id": "keep-pareto"}]
    assert len(enriched["candidate_systems"]) == len(package["candidate_systems"])
    assert enriched["process_route_summary"]["enriched_candidate_count"] == len(package["candidate_systems"])
