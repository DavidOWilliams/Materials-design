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
from src.process_route_enrichment import (  # noqa: E402
    attach_process_route_enrichment,
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
    recommendation_package = attach_deterministic_optimisation(recommendation_package)
    recommendation_package = attach_coating_vs_gradient_diagnostic(recommendation_package)
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
