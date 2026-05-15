"""Build 4 deterministic vertical-slice packages."""

from src.vertical_slices.ceramics_first import (
    build_ceramics_first_anchor_schema,
    build_ceramics_first_candidate_package,
    build_ceramics_first_design_space,
    build_demo_build31_metallic_rows,
    summarize_ceramics_first_package,
)

__all__ = [
    "build_ceramics_first_anchor_schema",
    "build_ceramics_first_candidate_package",
    "build_ceramics_first_design_space",
    "build_demo_build31_metallic_rows",
    "summarize_ceramics_first_package",
]
