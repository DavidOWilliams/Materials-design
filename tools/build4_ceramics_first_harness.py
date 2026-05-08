from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.recommendation_builder import (  # noqa: E402
    build_package_from_candidate_source_package,
    summarize_recommendation_package,
)
from src.optimisation.deterministic_optimizer import (  # noqa: E402
    attach_deterministic_optimisation,
)
from src.coating_vs_gradient_diagnostics import (  # noqa: E402
    attach_coating_vs_gradient_diagnostic,
)
from src.factor_models.coatings.spallation_adhesion import (  # noqa: E402
    attach_coating_spallation_adhesion,
)
from src.decision_readiness import (  # noqa: E402
    attach_decision_readiness,
)
from src.recommendation_narrative import (  # noqa: E402
    attach_recommendation_narrative,
)
from src.process_route_enrichment import (  # noqa: E402
    attach_process_route_enrichment,
)
from src.surface_function_model import (  # noqa: E402
    attach_surface_function_profiles,
    compare_required_surface_functions_to_candidates,
)
from src.ui_view_models import (  # noqa: E402
    build_recommendation_package_view_model,
    package_to_json_safe_dict,
    render_markdown_report,
)
from src.vertical_slices.ceramics_first import (  # noqa: E402
    build_ceramics_first_candidate_package,
)


REPORT_FILENAME = "build4_ceramics_first_report.md"
PACKAGE_JSON_FILENAME = "build4_ceramics_first_package.json"
VIEW_MODEL_JSON_FILENAME = "build4_ceramics_first_view_model.json"


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def build_outputs(output_dir: str | Path = "outputs") -> dict[str, Any]:
    """Build Build 4 ceramics-first package/view/report artifacts on disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    source_package = build_ceramics_first_candidate_package()
    recommendation_package = build_package_from_candidate_source_package(
        source_package,
        run_id="build4_ceramics_first_harness",
    )
    recommendation_package = attach_process_route_enrichment(recommendation_package)
    recommendation_package = attach_surface_function_profiles(recommendation_package)
    recommendation_package = attach_coating_spallation_adhesion(recommendation_package)
    recommendation_package = attach_deterministic_optimisation(recommendation_package)
    recommendation_package = attach_coating_vs_gradient_diagnostic(recommendation_package)
    recommendation_package = attach_decision_readiness(recommendation_package)
    recommendation_package = attach_recommendation_narrative(recommendation_package)
    view_model = build_recommendation_package_view_model(recommendation_package)
    markdown_report = render_markdown_report(recommendation_package)

    package_json = package_to_json_safe_dict(recommendation_package)
    view_model_json = package_to_json_safe_dict(view_model)

    report_path = output_path / REPORT_FILENAME
    package_json_path = output_path / PACKAGE_JSON_FILENAME
    view_model_json_path = output_path / VIEW_MODEL_JSON_FILENAME

    report_path.write_text(markdown_report, encoding="utf-8")
    _write_json(package_json_path, package_json)
    _write_json(view_model_json_path, view_model_json)

    summary = summarize_recommendation_package(recommendation_package)
    optimisation_summary = recommendation_package.get("optimisation_summary") or {}
    process_route_summary = recommendation_package.get("process_route_summary") or {}
    comparison = recommendation_package.get("coating_vs_gradient_comparison") or {}
    coating_gradient_diagnostic = recommendation_package.get("coating_vs_gradient_diagnostic") or {}
    surface_summary = recommendation_package.get("surface_function_coverage_summary") or {}
    readiness_summary = recommendation_package.get("decision_readiness_summary") or {}
    narrative = recommendation_package.get("recommendation_narrative") or {}
    coating_spallation_summary = recommendation_package.get("coating_spallation_adhesion_summary") or {}
    required_coverage = compare_required_surface_functions_to_candidates(recommendation_package)
    return {
        "report_path": str(report_path),
        "package_json_path": str(package_json_path),
        "view_model_json_path": str(view_model_json_path),
        "candidate_count": summary["candidate_count"],
        "candidate_class_mix": summary["candidate_class_mix"],
        "system_architecture_mix": summary["system_architecture_mix"],
        "evidence_maturity_mix": summary["evidence_maturity_mix"],
        "warning_count": summary["warning_count"],
        "optimisation_status": summary["optimisation_status"],
        "total_limiting_factor_count": optimisation_summary.get("total_limiting_factor_count", 0),
        "total_refinement_option_count": optimisation_summary.get("total_refinement_option_count", 0),
        "generated_candidate_count": optimisation_summary.get("generated_candidate_count", 0),
        "process_route_enriched_candidate_count": process_route_summary.get("enriched_candidate_count", 0),
        "high_inspection_burden_count": len(process_route_summary.get("high_inspection_burden_candidate_ids", [])),
        "limited_or_poor_repairability_count": len(
            process_route_summary.get("limited_or_poor_repairability_candidate_ids", [])
        ),
        "high_or_very_high_qualification_burden_count": len(
            process_route_summary.get("high_or_very_high_qualification_burden_candidate_ids", [])
        ),
        "research_mode_enabled": summary["research_mode_enabled"],
        "live_model_calls_made": view_model["summary"]["live_model_calls_made"],
        "coating_vs_gradient_comparison_required": comparison.get("comparison_required") is True,
        "coating_vs_gradient_diagnostic_status": coating_gradient_diagnostic.get("diagnostic_status", "unknown"),
        "coating_vs_gradient_pairwise_count": len(coating_gradient_diagnostic.get("pairwise_comparisons", [])),
        "coating_profile_count": len(coating_gradient_diagnostic.get("coating_profiles", [])),
        "gradient_profile_count": len(coating_gradient_diagnostic.get("gradient_profiles", [])),
        "shared_surface_function_themes": coating_gradient_diagnostic.get("shared_surface_function_themes", []),
        "required_surface_function_count": len(recommendation_package.get("required_surface_functions", [])),
        "covered_required_surface_function_count": len(required_coverage.get("covered_required_function_ids", [])),
        "unknown_surface_function_candidate_count": len(
            surface_summary.get("unknown_surface_function_candidate_ids", [])
        ),
        "shared_coating_gradient_function_count": len(surface_summary.get("shared_coating_gradient_functions", [])),
        "coating_spallation_relevant_candidate_count": coating_spallation_summary.get("relevant_candidate_count", 0),
        "high_spallation_risk_candidate_count": len(
            coating_spallation_summary.get("high_spallation_risk_candidate_ids", [])
        ),
        "high_coating_inspection_difficulty_candidate_count": len(
            coating_spallation_summary.get("high_inspection_difficulty_candidate_ids", [])
        ),
        "high_coating_repairability_constraint_candidate_count": len(
            coating_spallation_summary.get("high_repairability_constraint_candidate_ids", [])
        ),
        "decision_readiness_category_counts": readiness_summary.get("readiness_category_counts", {}),
        "decision_readiness_status_counts": readiness_summary.get("readiness_status_counts", {}),
        "research_only_candidate_count": len(readiness_summary.get("research_only_candidate_ids", [])),
        "exploratory_only_candidate_count": len(readiness_summary.get("exploratory_only_candidate_ids", [])),
        "usable_with_caveats_count": len(readiness_summary.get("usable_with_caveats_candidate_ids", [])),
        "usable_as_reference_count": len(readiness_summary.get("usable_as_reference_candidate_ids", [])),
        "not_decision_ready_count": len(readiness_summary.get("not_decision_ready_candidate_ids", [])),
        "recommendation_narrative_status": narrative.get("narrative_status", "unknown"),
        "mature_comparison_reference_count": len(narrative.get("mature_comparison_references", [])),
        "engineering_analogue_option_count": len(narrative.get("engineering_analogue_options", [])),
        "exploratory_option_count": len(narrative.get("exploratory_options", [])),
        "research_only_option_count": len(narrative.get("research_only_options", [])),
        "not_decision_ready_option_count": len(narrative.get("not_decision_ready_options", [])),
    }


def _print_summary(summary: dict[str, Any]) -> None:
    print("Build 4 ceramics-first harness completed")
    print(f"Report: {summary['report_path']}")
    print(f"Package JSON: {summary['package_json_path']}")
    print(f"View model JSON: {summary['view_model_json_path']}")
    print(f"Candidate count: {summary['candidate_count']}")
    print(f"Candidate class mix: {json.dumps(summary['candidate_class_mix'], sort_keys=True)}")
    print(f"Evidence maturity mix: {json.dumps(summary['evidence_maturity_mix'], sort_keys=True)}")
    print(f"Optimisation status: {summary['optimisation_status']}")
    print(f"Total limiting factor count: {summary['total_limiting_factor_count']}")
    print(f"Total refinement option count: {summary['total_refinement_option_count']}")
    print(f"Generated candidate count: {summary['generated_candidate_count']}")
    print(f"Process-route enriched candidate count: {summary['process_route_enriched_candidate_count']}")
    print(f"High inspection burden count: {summary['high_inspection_burden_count']}")
    print(f"Limited or poor repairability count: {summary['limited_or_poor_repairability_count']}")
    print(
        "High or very high qualification burden count: "
        f"{summary['high_or_very_high_qualification_burden_count']}"
    )
    print(f"Research mode enabled: {summary['research_mode_enabled']}")
    print(f"Live model calls made: {summary['live_model_calls_made']}")
    print(
        "Coating vs gradient comparison required: "
        f"{summary['coating_vs_gradient_comparison_required']}"
    )
    print(f"Coating vs gradient diagnostic status: {summary['coating_vs_gradient_diagnostic_status']}")
    print(f"Coating vs gradient pairwise count: {summary['coating_vs_gradient_pairwise_count']}")
    print(f"Coating profile count: {summary['coating_profile_count']}")
    print(f"Gradient profile count: {summary['gradient_profile_count']}")
    print(f"Shared surface-function themes: {json.dumps(summary['shared_surface_function_themes'])}")
    print(f"Required surface-function count: {summary['required_surface_function_count']}")
    print(f"Covered required surface-function count: {summary['covered_required_surface_function_count']}")
    print(f"Unknown surface-function candidate count: {summary['unknown_surface_function_candidate_count']}")
    print(f"Shared coating/gradient function count: {summary['shared_coating_gradient_function_count']}")
    print(f"Coating spallation relevant candidate count: {summary['coating_spallation_relevant_candidate_count']}")
    print(f"High coating spallation risk count: {summary['high_spallation_risk_candidate_count']}")
    print(
        "High coating inspection difficulty count: "
        f"{summary['high_coating_inspection_difficulty_candidate_count']}"
    )
    print(
        "High coating repairability constraint count: "
        f"{summary['high_coating_repairability_constraint_candidate_count']}"
    )
    print(
        "Decision-readiness category counts: "
        f"{json.dumps(summary['decision_readiness_category_counts'], sort_keys=True)}"
    )
    print(
        "Decision-readiness status counts: "
        f"{json.dumps(summary['decision_readiness_status_counts'], sort_keys=True)}"
    )
    print(f"Research-only candidate count: {summary['research_only_candidate_count']}")
    print(f"Exploratory-only candidate count: {summary['exploratory_only_candidate_count']}")
    print(f"Usable-with-caveats count: {summary['usable_with_caveats_count']}")
    print(f"Usable-as-reference count: {summary['usable_as_reference_count']}")
    print(f"Not-decision-ready count: {summary['not_decision_ready_count']}")
    print(f"Recommendation narrative status: {summary['recommendation_narrative_status']}")
    print(f"Mature comparison reference count: {summary['mature_comparison_reference_count']}")
    print(f"Engineering analogue option count: {summary['engineering_analogue_option_count']}")
    print(f"Exploratory option count: {summary['exploratory_option_count']}")
    print(f"Research-only option count: {summary['research_only_option_count']}")
    print(f"Not-decision-ready option count: {summary['not_decision_ready_option_count']}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic Build 4 ceramics-first inspection artifacts.",
    )
    parser.add_argument("--output-dir", default="outputs", help="Directory for markdown and JSON outputs.")
    parser.add_argument("--quiet", action="store_true", help="Suppress console summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    summary = build_outputs(args.output_dir)
    if not args.quiet:
        _print_summary(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
