from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.requirement_inference import infer_requirements  # noqa: E402
from src.evaluation import apply_decision_profile  # noqa: E402
from src.candidate_generation import (  # noqa: E402
    CANDIDATE_LABEL_TO_SCOPE_FAMILY,
    _build_retrieval_strategies,
    _choose_chemsys,
    _family_label_to_scope_key,
    _infer_family_from_chemsys_pattern,
    _infer_requested_family,
    generate_candidates,
)

OUTPUT_DIR = PROJECT_ROOT / "family_recall_diagnostics"
OUTPUT_DIR.mkdir(exist_ok=True)

CASES = [
    {
        "case_id": "hot_section_creep_am",
        "prompt": "Design a material for a hot aviation component operating at 850°C where creep is critical and additive manufacturing is preferred.",
        "temperature_c": 850,
        "am_preferred": True,
        "profile": "Balanced",
    },
    {
        "case_id": "lightweight_strength_to_weight",
        "prompt": "Design a lightweight structural aviation bracket with high strength-to-weight and good fatigue resistance. Conventional route is acceptable.",
        "temperature_c": 450,
        "am_preferred": False,
        "profile": "Balanced",
    },
    {
        "case_id": "wear_hot_corrosion",
        "prompt": "Select a material for a hot-corrosion and wear exposed aviation seal surface with sliding contact and salt contaminant exposure.",
        "temperature_c": 700,
        "am_preferred": False,
        "profile": "Performance-first",
    },
    {
        "case_id": "am_complex_geometry_creep",
        "prompt": "Design a high temperature component with complex internal channels where additive manufacturing is preferred but creep still matters.",
        "temperature_c": 825,
        "am_preferred": True,
        "profile": "AM route-first",
    },
    {
        "case_id": "certification_mature_conventional",
        "prompt": "Select a mature conventional aerospace alloy concept for a moderately hot structural component where certification maturity and repairability matter.",
        "temperature_c": 550,
        "am_preferred": False,
        "profile": "Cost & sustainability-aware",
    },
    {
        "case_id": "extreme_temperature_refractory",
        "prompt": "Explore an extreme temperature aviation concept above 1000°C where creep and oxidation are severe and specialist refractory processing may be acceptable.",
        "temperature_c": 1050,
        "am_preferred": False,
        "profile": "Performance-first",
    },
]


def _top_family(req: Dict[str, Any]) -> tuple[str | None, float]:
    priors = req.get("family_priors") or (req.get("scope_plan", {}) or {}).get("family_priors") or {}
    items = []
    for family, value in priors.items():
        try:
            items.append((str(family), float(value)))
        except Exception:
            pass
    return max(items, key=lambda item: item[1]) if items else (None, 0.0)


def _json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _build_requirements(case: Dict[str, Any]) -> Dict[str, Any]:
    req = infer_requirements(case["prompt"], case["temperature_c"], case["am_preferred"])
    return apply_decision_profile(req, case["profile"])


def run_preflight() -> tuple[pd.DataFrame, pd.DataFrame]:
    case_rows: List[Dict[str, Any]] = []
    query_rows: List[Dict[str, Any]] = []

    for case in CASES:
        req = _build_requirements(case)
        chemsys_list = _choose_chemsys(req)
        top_family, top_prior = _top_family(req)
        family_priors = req.get("family_priors") or {}
        allowed = req.get("allowed_material_families", []) or []

        case_rows.append(
            {
                "case_id": case["case_id"],
                "temperature_c": case["temperature_c"],
                "am_preferred": case["am_preferred"],
                "profile": case["profile"],
                "top_prompt_family": top_family,
                "top_prompt_prior": top_prior,
                "allowed_families": "; ".join(allowed),
                "family_priors_json": _json(family_priors),
                "queried_chemsys": "; ".join(chemsys_list),
                "query_count": len(chemsys_list),
                "top_family_represented_in_queries": any(
                    _family_label_to_scope_key(_infer_requested_family(chemsys, req)) == top_family
                    for chemsys in chemsys_list
                ),
            }
        )

        for idx, chemsys in enumerate(chemsys_list, start=1):
            expected_label = _infer_family_from_chemsys_pattern(chemsys)
            expected_scope = _family_label_to_scope_key(expected_label)
            inferred_label = _infer_requested_family(chemsys, req)
            inferred_scope = _family_label_to_scope_key(inferred_label)
            strategies = _build_retrieval_strategies(chemsys, req)
            query_rows.append(
                {
                    "case_id": case["case_id"],
                    "query_order": idx,
                    "requested_chemsys": chemsys,
                    "expected_family_from_chemsys": expected_label,
                    "expected_scope_family": expected_scope,
                    "actual_inferred_requested_family": inferred_label,
                    "actual_scope_family": inferred_scope,
                    "matches_chemistry_family": expected_scope == inferred_scope,
                    "top_prompt_family": top_family,
                    "family_prior": family_priors.get(inferred_scope),
                    "retrieval_strategy_count": len(strategies),
                    "retrieval_modes": "; ".join(strategy.retrieval_mode for strategy in strategies),
                    "strategy_payloads": "; ".join(str(strategy.query_payload) for strategy in strategies),
                }
            )

    case_df = pd.DataFrame(case_rows)
    query_df = pd.DataFrame(query_rows)
    case_df.to_csv(OUTPUT_DIR / "family_recall_case_preflight.csv", index=False)
    query_df.to_csv(OUTPUT_DIR / "family_recall_query_preflight.csv", index=False)
    return case_df, query_df


def run_live_generation() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows: List[Dict[str, Any]] = []
    attempt_rows: List[Dict[str, Any]] = []
    log_rows: List[Dict[str, Any]] = []

    for case in CASES:
        req = _build_requirements(case)
        top_family, top_prior = _top_family(req)
        try:
            result = generate_candidates(req)
            diagnostics = result.get("diagnostics", {}) or {}
            candidates = result.get("candidates")
            if candidates is not None and len(candidates) > 0 and "material_family" in candidates.columns:
                survivor_mix = Counter(candidates["material_family"].map(lambda x: CANDIDATE_LABEL_TO_SCOPE_FAMILY.get(str(x), str(x))))
            else:
                survivor_mix = Counter()

            summary_rows.append(
                {
                    "case_id": case["case_id"],
                    "status": result.get("status"),
                    "message": result.get("message"),
                    "top_prompt_family": top_family,
                    "top_prompt_prior": top_prior,
                    "queried_chemsys": "; ".join(diagnostics.get("queried_chemsys", []) or []),
                    "raw_docs_retrieved": diagnostics.get("raw_docs_retrieved"),
                    "accepted_docs_after_request_acceptance": diagnostics.get("accepted_docs_after_request_acceptance"),
                    "unique_docs_after_request_acceptance": diagnostics.get("unique_docs_after_request_acceptance"),
                    "rejected_by_retrieval_acceptance": diagnostics.get("rejected_by_retrieval_acceptance"),
                    "rejected_by_family": diagnostics.get("rejected_by_family"),
                    "rejected_by_complexity_gate": diagnostics.get("rejected_by_complexity_gate"),
                    "final_candidate_count": diagnostics.get("final_candidate_count"),
                    "surviving_family_mix_json": _json(diagnostics.get("surviving_family_mix") or dict(survivor_mix)),
                    "prompt_family_alignment_warning": diagnostics.get("prompt_family_alignment_warning"),
                    "warnings_json": _json(diagnostics.get("warnings", [])),
                }
            )

            for row in diagnostics.get("retrieval_attempts", []) or []:
                attempt = dict(row)
                attempt["case_id"] = case["case_id"]
                attempt_rows.append(attempt)

            for row in diagnostics.get("candidate_logs", []) or []:
                log = dict(row)
                log["case_id"] = case["case_id"]
                log_rows.append(log)

        except Exception as exc:
            summary_rows.append(
                {
                    "case_id": case["case_id"],
                    "status": "error",
                    "message": str(exc),
                    "top_prompt_family": top_family,
                    "top_prompt_prior": top_prior,
                }
            )

    summary_df = pd.DataFrame(summary_rows)
    attempts_df = pd.DataFrame(attempt_rows)
    logs_df = pd.DataFrame(log_rows)
    summary_df.to_csv(OUTPUT_DIR / "family_recall_live_summary.csv", index=False)
    attempts_df.to_csv(OUTPUT_DIR / "family_recall_retrieval_attempts.csv", index=False)
    logs_df.to_csv(OUTPUT_DIR / "family_recall_candidate_logs.csv", index=False)
    return summary_df, attempts_df, logs_df


def write_insights(case_df: pd.DataFrame, query_df: pd.DataFrame, live_df: pd.DataFrame | None = None) -> None:
    mismatch_df = query_df[query_df["matches_chemistry_family"] == False] if len(query_df) else pd.DataFrame()
    top_family_missing_query_df = case_df[case_df["top_family_represented_in_queries"] == False] if len(case_df) else pd.DataFrame()

    lines = [
        "# Family Recall Diagnostic Insights",
        "",
        "## Purpose",
        "This harness checks whether prompt-sensitive family priors are reaching candidate-generation retrieval, and whether each requested chemistry is assigned the correct requested family before request-aware acceptance.",
        "",
        "## Preflight findings",
        f"- Cases checked: **{len(case_df)}**",
        f"- Requested-chemistry family-inference mismatches: **{len(mismatch_df)}**",
        f"- Cases where the top prompt family was absent from the query plan: **{len(top_family_missing_query_df)}**",
        "",
    ]

    if len(mismatch_df):
        lines.extend([
            "### Chemistry-family mismatches to inspect",
            "These indicate candidate-generation may still be assigning the wrong requested family before retrieval acceptance.",
            "",
        ])
        for _, row in mismatch_df.head(20).iterrows():
            lines.append(
                f"- {row['case_id']} / {row['requested_chemsys']}: expected {row['expected_scope_family']}, inferred {row['actual_scope_family']}"
            )
        lines.append("")
    else:
        lines.append("No chemistry-family inference mismatches were found in the preflight query plan.\n")

    if len(top_family_missing_query_df):
        lines.extend([
            "### Top-family query-plan gaps",
            "These indicate the scope planner favoured a family, but `_choose_chemsys` did not query it.",
            "",
        ])
        for _, row in top_family_missing_query_df.iterrows():
            lines.append(f"- {row['case_id']}: top family {row['top_prompt_family']} not represented in queries")
        lines.append("")
    else:
        lines.append("Every case had at least one query for the top prompt family.\n")

    if live_df is not None and len(live_df):
        error_count = int((live_df["status"] == "error").sum()) if "status" in live_df.columns else 0
        lines.extend([
            "## Live-generation findings",
            f"- Live cases run: **{len(live_df)}**",
            f"- Live errors: **{error_count}**",
            "",
        ])
        for _, row in live_df.iterrows():
            lines.append(
                f"- **{row.get('case_id')}**: status={row.get('status')}, top_family={row.get('top_prompt_family')}, final_candidate_count={row.get('final_candidate_count')}, survivor_mix={row.get('surviving_family_mix_json')}"
            )
            warning = row.get("prompt_family_alignment_warning")
            if isinstance(warning, str) and warning.strip():
                lines.append(f"  - Alignment warning: {warning}")
        lines.append("")

    lines.extend([
        "## Recommended interpretation",
        "- If preflight mismatches are zero but live non-Ni families still do not survive, the problem is likely Materials Project coverage, request-aware acceptance calibration, or family classification of returned records.",
        "- If preflight mismatches exist, fix `_infer_requested_family` and same-family fallback logic before changing scoring or recipes.",
        "- If the top family is absent from the query plan, fix `_choose_chemsys` ordering and query budgeting before investigating recipe fallback.",
    ])

    (OUTPUT_DIR / "family_recall_diagnostic_insights.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    case_df, query_df = run_preflight()

    live_df = None
    # Try live generation. If MP_API_KEY is not configured, the output will show an error row
    # and the preflight files still remain useful.
    live_df, _, _ = run_live_generation()
    write_insights(case_df, query_df, live_df)

    print(f"Wrote diagnostic outputs to: {OUTPUT_DIR}")
    print("Key files:")
    print("- family_recall_case_preflight.csv")
    print("- family_recall_query_preflight.csv")
    print("- family_recall_live_summary.csv")
    print("- family_recall_candidate_logs.csv")
    print("- family_recall_diagnostic_insights.md")


if __name__ == "__main__":
    main()
