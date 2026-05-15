"""Build 4 decision-engine placeholder.

Real decision logic is deferred. This module does not rank, optimise, perform
Pareto analysis, or make final recommendation decisions. It exists only to
preserve a transparent package boundary so candidate, evidence, assembly and
factor-model outputs can be inspected without overclaiming decision authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.recommendation_builder import (
    RecommendationPackage,
    build_package_from_candidate_source_package,
    build_recommendation_package,
)


def build_decision_package(*args: Any, **kwargs: Any) -> RecommendationPackage:
    """Return a non-decision package wrapper without ranking or optimisation."""
    if len(args) >= 3:
        return build_recommendation_package(*args, **kwargs)

    if len(args) == 1 and isinstance(args[0], Mapping):
        return build_package_from_candidate_source_package(args[0], **kwargs)

    if {"requirement_schema", "design_space", "candidate_systems"} <= set(kwargs):
        return build_recommendation_package(
            requirement_schema=kwargs.pop("requirement_schema"),
            design_space=kwargs.pop("design_space"),
            candidate_systems=kwargs.pop("candidate_systems"),
            **kwargs,
        )

    return {
        "run_id": str(kwargs.get("run_id") or "build4_decision_package_placeholder"),
        "requirement_schema": {},
        "design_space": {},
        "candidate_systems": [],
        "ranked_recommendations": [],
        "pareto_front": [],
        "optimisation_summary": {"status": "not_implemented"},
        "source_mix_summary": {},
        "evidence_maturity_summary": {"candidate_count": 0, "maturity_counts": {}},
        "diagnostics": {
            "decision_engine": "placeholder",
            "ranking_performed": False,
            "optimisation_performed": False,
            "pareto_analysis_performed": False,
            "live_model_calls_made": False,
            "materials_project_calls_made": False,
        },
        "warnings": [
            "Decision logic is not implemented; this package does not rank, optimise or recommend."
        ],
        "factor_summary": {},
        "system_assembly_summary": {},
        "package_status": "decision_not_implemented",
    }
