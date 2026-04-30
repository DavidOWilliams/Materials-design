from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List

import pandas as pd

# Run from project root: python tools/prompt_sensitivity_harness.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.requirement_inference import infer_requirements  # noqa: E402

CASES = [
    {
        "case_id": "lightweight_strength_to_weight",
        "prompt": "Design a lightweight structural aviation bracket with high strength-to-weight and good fatigue resistance. Conventional route is acceptable.",
        "temperature_c": 450,
        "am_preferred": False,
        "expect_active": {"lightweight", "fatigue"},
        "expect_top_family": "Ti alloy",
    },
    {
        "case_id": "creep_hot_section_am",
        "prompt": "Design a material for a hot aviation component operating at 850°C where creep is critical and additive manufacturing is preferred.",
        "temperature_c": 850,
        "am_preferred": True,
        "expect_active": {"creep", "temperature", "oxidation", "route_suitability"},
        "expect_top_family_any": {"Ni-based superalloy", "Co-based alloy", "Refractory alloy concept"},
    },
    {
        "case_id": "wear_hot_corrosion",
        "prompt": "Select a material for a hot-corrosion and wear exposed aviation seal surface with sliding contact and salt contaminant exposure.",
        "temperature_c": 780,
        "am_preferred": False,
        "expect_active": {"hot_corrosion", "wear", "oxidation"},
        "expect_top_family": "Co-based alloy",
    },
    {
        "case_id": "am_preferred_complex_geometry",
        "prompt": "Design a high temperature component with complex internal channels where additive manufacturing is preferred but creep still matters.",
        "temperature_c": 825,
        "am_preferred": True,
        "expect_active": {"route_suitability", "manufacturability", "creep"},
    },
    {
        "case_id": "conventional_certification_maturity",
        "prompt": "Select a proven conventional wrought aerospace alloy route for a safety critical component where certification maturity and inspection are important.",
        "temperature_c": 600,
        "am_preferred": False,
        "expect_active": {"certification_maturity", "manufacturability"},
    },
]


def _top_family(family_priors: Dict[str, float]) -> str:
    if not family_priors:
        return ""
    return max(family_priors.items(), key=lambda item: item[1])[0]


def run_cases() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for case in CASES:
        req = infer_requirements(case["prompt"], case["temperature_c"], case["am_preferred"])
        schema = req.get("requirement_schema", {})
        scope = req.get("scope_plan", {})
        active = set(scope.get("active_factor_set", []))
        family_priors = scope.get("family_priors", {})
        top_family = _top_family(family_priors)

        expected_active = set(case.get("expect_active", set()))
        missing_active = sorted(expected_active - active)
        family_pass = True
        if case.get("expect_top_family"):
            family_pass = top_family == case["expect_top_family"]
        if case.get("expect_top_family_any"):
            family_pass = top_family in set(case["expect_top_family_any"])

        rows.append(
            {
                "case_id": case["case_id"],
                "temperature_c": case["temperature_c"],
                "am_preferred": case["am_preferred"],
                "top_family": top_family,
                "allowed_families": "; ".join(scope.get("allowed_families", [])),
                "active_factors": "; ".join(scope.get("active_factor_set", [])),
                "missing_expected_active_factors": "; ".join(missing_active),
                "active_factor_check_pass": len(missing_active) == 0,
                "family_prior_check_pass": family_pass,
                "interpreter_confidence": schema.get("interpreter_confidence"),
                "family_priors_json": json.dumps(family_priors),
                "factor_weights_json": json.dumps(scope.get("active_factor_weights", {})),
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out_dir = PROJECT_ROOT / "validation_outputs"
    out_dir.mkdir(exist_ok=True)
    df = run_cases()
    summary_path = out_dir / "prompt_sensitivity_summary.csv"
    df.to_csv(summary_path, index=False)
    print(df[["case_id", "top_family", "active_factor_check_pass", "family_prior_check_pass", "missing_expected_active_factors"]].to_string(index=False))
    print(f"\nWrote {summary_path}")
