from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.coating_vs_gradient_diagnostics import attach_coating_vs_gradient_diagnostic  # noqa: E402
from src.decision_readiness import attach_decision_readiness  # noqa: E402
from src.factor_models.coatings.spallation_adhesion import attach_coating_spallation_adhesion  # noqa: E402
from src.optimisation.deterministic_optimizer import attach_deterministic_optimisation  # noqa: E402
from src.process_route_enrichment import attach_process_route_enrichment  # noqa: E402
from src.recommendation_builder import build_package_from_candidate_source_package  # noqa: E402
from src.recommendation_narrative import attach_recommendation_narrative  # noqa: E402
from src.surface_function_model import attach_surface_function_profiles  # noqa: E402
from src.validation_plan import build_validation_plan  # noqa: E402
from src.ui_view_models import (  # noqa: E402
    build_recommendation_package_view_model,
    package_to_json_safe_dict,
    render_markdown_report,
)
from src.vertical_slices.ceramics_first import build_ceramics_first_candidate_package  # noqa: E402


INDEX_FILENAME = "build4_review_pack_index.md"
SUMMARY_FILENAME = "build4_review_pack_summary.json"
PACKAGE_FILENAME = "build4_recommendation_package.json"
VIEW_MODEL_FILENAME = "build4_view_model.json"
FULL_REPORT_FILENAME = "build4_full_report.md"

SECTION_FILENAMES = {
    "package_summary": "01_package_summary.md",
    "surface_function_coverage": "02_surface_function_coverage.md",
    "process_route_inspection_repair": "03_process_route_inspection_repair.md",
    "coating_spallation_adhesion": "04_coating_spallation_adhesion.md",
    "deterministic_optimisation_trace": "05_deterministic_optimisation_trace.md",
    "coating_vs_gradient_diagnostic": "06_coating_vs_gradient_diagnostic.md",
    "decision_readiness": "07_decision_readiness.md",
    "controlled_recommendation_narrative": "08_controlled_recommendation_narrative.md",
    "warnings_and_deferred_capabilities": "09_warnings_and_deferred_capabilities.md",
}

GENERATED_FILES = [
    INDEX_FILENAME,
    SUMMARY_FILENAME,
    PACKAGE_FILENAME,
    VIEW_MODEL_FILENAME,
    FULL_REPORT_FILENAME,
    *[f"sections/{filename}" for filename in SECTION_FILENAMES.values()],
]


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=str)
    return [value]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _count(value: Any) -> int:
    if isinstance(value, Mapping):
        return len(value)
    return len(_as_list(value))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def build_full_build4_package() -> dict[str, Any]:
    """Build the deterministic Build 4 ceramics-first package for review export."""
    source_package = build_ceramics_first_candidate_package()
    package = build_package_from_candidate_source_package(
        source_package,
        run_id="build4_review_pack_exporter",
    )
    package = attach_process_route_enrichment(package)
    package = attach_surface_function_profiles(package)
    package = attach_coating_spallation_adhesion(package)
    package = attach_deterministic_optimisation(package)
    package = attach_coating_vs_gradient_diagnostic(package)
    package = attach_decision_readiness(package)
    package = attach_recommendation_narrative(package)
    package = build_validation_plan(package)
    return dict(package)


def build_review_pack_summary(package: Mapping[str, Any], view_model: Mapping[str, Any]) -> dict[str, Any]:
    summary = _mapping(view_model.get("summary"))
    optimisation_summary = _mapping(package.get("optimisation_summary"))
    process_route_summary = _mapping(package.get("process_route_summary"))
    surface_summary = _mapping(package.get("surface_function_coverage_summary"))
    required_coverage = _mapping(package.get("surface_function_required_coverage"))
    coating_spallation = _mapping(package.get("coating_spallation_adhesion_summary"))
    diagnostic = _mapping(package.get("coating_vs_gradient_diagnostic"))
    readiness_summary = _mapping(package.get("decision_readiness_summary"))
    narrative = _mapping(package.get("recommendation_narrative"))
    application_fit_summary = _mapping(package.get("application_requirement_fit_summary"))
    limiting_factor_summary = _mapping(package.get("application_limiting_factor_summary"))
    controlled_shortlist_summary = _mapping(package.get("controlled_shortlist_summary"))
    validation_plan_summary = _mapping(package.get("validation_plan_summary"))
    diagnostics = _mapping(package.get("diagnostics"))
    return {
        "run_id": summary.get("run_id") or package.get("run_id"),
        "package_status": summary.get("package_status") or package.get("package_status"),
        "candidate_count": summary.get("candidate_count", _count(package.get("candidate_systems"))),
        "candidate_class_mix": dict(_mapping(summary.get("candidate_class_mix"))),
        "evidence_maturity_mix": dict(_mapping(summary.get("evidence_maturity_mix"))),
        "process_route_enriched_candidate_count": process_route_summary.get("enriched_candidate_count", 0),
        "required_surface_function_count": _count(package.get("required_surface_functions")),
        "covered_required_surface_function_count": _count(required_coverage.get("covered_required_function_ids")),
        "coating_spallation_relevant_candidate_count": coating_spallation.get("relevant_candidate_count", 0),
        "coating_system_kind_counts": dict(_mapping(coating_spallation.get("coating_system_kind_counts"))),
        "coating_vs_gradient_diagnostic_status": diagnostic.get("diagnostic_status", "unknown"),
        "coating_vs_gradient_pairwise_count": _count(diagnostic.get("pairwise_comparisons")),
        "decision_readiness_category_counts": dict(_mapping(readiness_summary.get("readiness_category_counts"))),
        "decision_readiness_status_counts": dict(_mapping(readiness_summary.get("readiness_status_counts"))),
        "recommendation_narrative_status": narrative.get("narrative_status", "unknown"),
        "application_fit_status_counts": dict(_mapping(application_fit_summary.get("application_fit_status_counts"))),
        "application_architecture_path_counts": dict(_mapping(application_fit_summary.get("architecture_path_counts"))),
        "application_limiting_factor_analysis_status_counts": dict(
            _mapping(limiting_factor_summary.get("analysis_status_counts"))
        ),
        "controlled_shortlist_bucket_counts": dict(_mapping(controlled_shortlist_summary.get("bucket_counts"))),
        "validation_plan_category_counts": dict(_mapping(validation_plan_summary.get("validation_category_counts"))),
        "optimisation_status": optimisation_summary.get("status", "unknown"),
        "generated_candidate_count": optimisation_summary.get("generated_candidate_count", 0),
        "live_model_calls_made": diagnostics.get("live_model_calls_made") is True,
        "ranked_recommendations_count": _count(package.get("ranked_recommendations")),
        "pareto_front_count": _count(package.get("pareto_front")),
        "warning_count": _count(package.get("warnings")),
        "unknown_surface_function_candidate_count": _count(
            surface_summary.get("unknown_surface_function_candidate_ids")
        ),
        "exporter_status": "review_pack_created",
    }


def render_review_pack_index(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Build 4 Material-System Review Pack",
        "",
        "## Status Disclaimer",
        "- This review pack is not a final recommendation.",
        "- No final ranking was produced.",
        "- No Pareto optimisation was performed.",
        "- No generated variants were created.",
        "- No live model calls were made.",
        "- This is not qualification or certification approval.",
        "",
        "## Summary Metrics",
        f"- Exporter status: {summary.get('exporter_status')}",
        f"- Run ID: {summary.get('run_id')}",
        f"- Package status: {summary.get('package_status')}",
        f"- Candidate count: {summary.get('candidate_count')}",
        f"- Process-route enriched candidates: {summary.get('process_route_enriched_candidate_count')}",
        f"- Required surface functions: {summary.get('required_surface_function_count')}",
        f"- Covered required surface functions: {summary.get('covered_required_surface_function_count')}",
        f"- Coating spallation relevant candidates: {summary.get('coating_spallation_relevant_candidate_count')}",
        f"- Coating system kinds: {summary.get('coating_system_kind_counts')}",
        f"- Coating-vs-gradient diagnostic status: {summary.get('coating_vs_gradient_diagnostic_status')}",
        f"- Coating-vs-gradient pairwise comparisons: {summary.get('coating_vs_gradient_pairwise_count')}",
        f"- Decision readiness categories: {summary.get('decision_readiness_category_counts')}",
        f"- Decision readiness statuses: {summary.get('decision_readiness_status_counts')}",
        f"- Recommendation narrative status: {summary.get('recommendation_narrative_status')}",
        f"- Application fit statuses: {summary.get('application_fit_status_counts')}",
        f"- Application architecture paths: {summary.get('application_architecture_path_counts')}",
        f"- Application limiting-factor statuses: {summary.get('application_limiting_factor_analysis_status_counts')}",
        f"- Controlled shortlist buckets: {summary.get('controlled_shortlist_bucket_counts')}",
        f"- Validation plan categories: {summary.get('validation_plan_category_counts')}",
        f"- Optimisation status: {summary.get('optimisation_status')}",
        f"- Generated candidate count: {summary.get('generated_candidate_count')}",
        f"- Live model calls made: {summary.get('live_model_calls_made')}",
        f"- Ranked recommendations count: {summary.get('ranked_recommendations_count')}",
        f"- Pareto front count: {summary.get('pareto_front_count')}",
        f"- Warning count: {summary.get('warning_count')}",
        "",
        "## Generated Files",
    ]
    lines.extend(f"- `{filename}`" for filename in GENERATED_FILES)
    lines.extend(
        [
            "",
            "## Suggested Review Order",
            "1. Read the package index and summary JSON.",
            "2. Review surface-function coverage.",
            "3. Review process route, inspection, repairability and qualification burdens.",
            "4. Review coating spallation, adhesion, inspection and repair diagnostics.",
            "5. Review deterministic optimisation trace boundaries.",
            "6. Review coating-vs-gradient diagnostics.",
            "7. Review decision readiness.",
            "8. Review the controlled recommendation narrative.",
            "9. Review warnings and deferred capabilities.",
            "",
            "## Deferred Capabilities",
            "- final ranking",
            "- Pareto optimisation",
            "- generated variants",
            "- candidate filtering",
            "- final decision logic",
            "- live specialist model adapters",
            "- Streamlit Build 4 integration",
            "- qualification or certification approval",
        ]
    )
    return "\n".join(lines) + "\n"


def _normalise_heading(heading: str) -> str:
    text = heading.strip().lower()
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _section_key_for_heading(heading: str) -> str | None:
    normalised = _normalise_heading(heading)
    if "controlled recommendation narrative" in normalised:
        return "controlled_recommendation_narrative"
    if "decision readiness" in normalised:
        return "decision_readiness"
    if "surface function coverage" in normalised:
        return "surface_function_coverage"
    if "process route" in normalised and ("inspection" in normalised or "repairability" in normalised):
        return "process_route_inspection_repair"
    if "coating spallation" in normalised and ("adhesion" in normalised or "repair" in normalised):
        return "coating_spallation_adhesion"
    if "deterministic optimisation" in normalised or "limiting factors and refinement options" in normalised:
        return "deterministic_optimisation_trace"
    if "coating vs gradient diagnostic" in normalised:
        return "coating_vs_gradient_diagnostic"
    if "warnings" in normalised and "deferred" in normalised:
        return "warnings_and_deferred_capabilities"
    return None


def split_full_report_into_sections(full_report: str) -> dict[str, str]:
    headings = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", full_report))
    sections = {
        key: f"# {key.replace('_', ' ').title()}\n\nSection was not found in the full report.\n"
        for key in SECTION_FILENAMES
    }
    first_heading_start = headings[0].start() if headings else len(full_report)
    package_summary = full_report[:first_heading_start].rstrip()

    for index, match in enumerate(headings):
        heading = match.group(1)
        start = match.start()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(full_report)
        chunk = full_report[start:end].rstrip()
        key = _section_key_for_heading(heading)
        if key == "deterministic_optimisation_trace" and not sections[key].endswith("not found in the full report.\n"):
            sections[key] = sections[key].rstrip() + "\n\n" + chunk + "\n"
        elif key:
            sections[key] = chunk + "\n"
        else:
            package_summary += "\n\n" + chunk

    sections["package_summary"] = (package_summary.strip() or "# Package Summary\n\nSection was not found.\n") + "\n"
    return sections


def _clean_output_dir(output_path: Path) -> None:
    resolved = output_path.resolve()
    if not resolved.exists():
        return
    for child in resolved.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def write_review_pack(
    output_dir: str | Path = "outputs/build4_review_pack",
    *,
    clean_output_dir: bool = False,
) -> dict[str, Any]:
    output_path = Path(output_dir)
    if clean_output_dir:
        _clean_output_dir(output_path)
    sections_path = output_path / "sections"
    sections_path.mkdir(parents=True, exist_ok=True)

    package = build_full_build4_package()
    view_model = build_recommendation_package_view_model(package)
    full_report = render_markdown_report(package)
    summary = build_review_pack_summary(package, view_model)
    index_markdown = render_review_pack_index(summary)
    sections = split_full_report_into_sections(full_report)

    files_written: list[str] = []

    def write_text(relative_path: str, content: str) -> None:
        path = output_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        files_written.append(str(path))

    def write_json(relative_path: str, payload: Mapping[str, Any]) -> None:
        path = output_path / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(path, payload)
        files_written.append(str(path))

    write_text(INDEX_FILENAME, index_markdown)
    write_json(SUMMARY_FILENAME, package_to_json_safe_dict(summary))
    write_json(PACKAGE_FILENAME, package_to_json_safe_dict(package))
    write_json(VIEW_MODEL_FILENAME, package_to_json_safe_dict(view_model))
    write_text(FULL_REPORT_FILENAME, full_report)
    for key, filename in SECTION_FILENAMES.items():
        write_text(f"sections/{filename}", sections[key])

    return {
        "output_dir": str(output_path),
        "files_written": files_written,
        "summary": summary,
        "candidate_count": summary["candidate_count"],
        "warning_count": summary["warning_count"],
        "generated_candidate_count": summary["generated_candidate_count"],
        "live_model_calls_made": summary["live_model_calls_made"],
        "ranked_recommendations_count": summary["ranked_recommendations_count"],
        "pareto_front_count": summary["pareto_front_count"],
    }


def _print_summary(result: Mapping[str, Any]) -> None:
    summary = _mapping(result.get("summary"))
    print("Build 4 review pack created")
    print(f"Output directory: {result.get('output_dir')}")
    print(f"Files written count: {len(_as_list(result.get('files_written')))}")
    print(f"Candidate count: {result.get('candidate_count')}")
    print(f"Decision readiness counts: {json.dumps(summary.get('decision_readiness_category_counts'), sort_keys=True)}")
    print(f"Narrative status: {summary.get('recommendation_narrative_status')}")
    print(f"Optimisation status: {summary.get('optimisation_status')}")
    print(f"Generated candidate count: {result.get('generated_candidate_count')}")
    print(f"Live model calls made: {result.get('live_model_calls_made')}")
    print(f"Ranked recommendations count: {result.get('ranked_recommendations_count')}")
    print(f"Pareto front count: {result.get('pareto_front_count')}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export deterministic Build 4 review-pack artifacts.")
    parser.add_argument("--output-dir", default="outputs/build4_review_pack", help="Review pack output directory.")
    parser.add_argument("--clean", action="store_true", help="Remove old files inside the output directory first.")
    parser.add_argument("--quiet", action="store_true", help="Suppress console summary.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    result = write_review_pack(args.output_dir, clean_output_dir=args.clean)
    if not args.quiet:
        _print_summary(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
