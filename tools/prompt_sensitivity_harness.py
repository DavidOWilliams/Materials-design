from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.requirement_inference import infer_requirements
from src.candidate_generation import generate_candidates
from src.evaluation import apply_decision_profile
from src.scoring import score_candidates
from src.reranking import scientific_rerank
from src.ranking import rank_candidates
from src.provenance import add_provenance

DEFAULT_CASES = [
    {
        "case_id": "baseline_hot_am",
        "application_prompt": "Design a material for a hot aviation component operating at 850°C where creep is critical and additive manufacturing is preferred.",
        "operating_temperature": 850,
        "am_preferred": True,
        "scenario_profile": "Balanced",
    },
    {
        "case_id": "hot_conventional",
        "application_prompt": "Design a material for a hot aviation component operating at 850°C where creep is critical and conventional manufacturing is preferred.",
        "operating_temperature": 850,
        "am_preferred": False,
        "scenario_profile": "Balanced",
    },
    {
        "case_id": "cost_sustainability",
        "application_prompt": "Design a material for a component operating at 750°C where cost and sustainability matter almost as much as temperature capability.",
        "operating_temperature": 750,
        "am_preferred": False,
        "scenario_profile": "Cost & sustainability-aware",
    },
    {
        "case_id": "lightweight_ti",
        "application_prompt": "Design a lightweight aerospace material for a component operating at 350°C where strength-to-weight ratio is critical and additive manufacturing is preferred.",
        "operating_temperature": 350,
        "am_preferred": True,
        "scenario_profile": "Balanced",
    },
    {
        "case_id": "refractory_extreme",
        "application_prompt": "Design a material for an aerospace component operating at 1100°C where extreme temperature capability matters more than cost.",
        "operating_temperature": 1100,
        "am_preferred": False,
        "scenario_profile": "Performance-first",
    },
]


def _safe_len(value: Any) -> int:
    if value is None:
        return 0
    try:
        return int(len(value))
    except Exception:
        return 0


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y"}


def _parse_list(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    if value is None:
        return ""
    return str(value)


def _read_csv_flex(path: Path) -> pd.DataFrame:
    parsers = [
        {"sep": ","},
        {"sep": None, "engine": "python"},
        {"sep": "\t"},
        {"sep": r"\s{2,}", "engine": "python"},
    ]
    last_exc: Exception | None = None
    for opts in parsers:
        try:
            df = pd.read_csv(path, **opts)
            if len(df.columns) == 0:
                continue
            if len(df.columns) == 1 and "," not in str(df.columns[0]):
                continue
            return df
        except Exception as exc:  # pragma: no cover - defensive
            last_exc = exc
    raise ValueError(f"Could not parse CSV case file: {path}. Last parser error: {last_exc}")


def load_cases(path: Path | None) -> pd.DataFrame:
    if path is None:
        print("No case file supplied; using built-in default cases.")
        return pd.DataFrame(DEFAULT_CASES)

    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Case file not found: {path}")
    if path.stat().st_size == 0:
        print(f"Case file is empty: {path}. Using built-in default cases instead.")
        return pd.DataFrame(DEFAULT_CASES)

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = _read_csv_flex(path)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    elif suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "cases" in raw:
            raw = raw["cases"]
        df = pd.DataFrame(raw)
    else:
        raise ValueError(f"Unsupported case file type: {path.suffix}")

    if df.empty:
        print(f"Case file parsed but contained no rows: {path}. Using built-in default cases instead.")
        return pd.DataFrame(DEFAULT_CASES)

    required = ["case_id", "application_prompt", "operating_temperature", "am_preferred", "scenario_profile"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Case file is missing required columns: {missing}. Detected columns: {list(df.columns)}")

    return df


def run_case(case_row: pd.Series) -> Dict[str, Any]:
    case_id = str(case_row.get("case_id", "case"))
    prompt = str(case_row.get("application_prompt", ""))
    temp = int(case_row.get("operating_temperature", 850))
    am_preferred = _to_bool(case_row.get("am_preferred", True))
    scenario_profile = str(case_row.get("scenario_profile", "Balanced"))

    requirements = infer_requirements(prompt, temp, am_preferred)
    requirements = apply_decision_profile(requirements, scenario_profile)
    candidate_result = generate_candidates(requirements)

    diagnostics = candidate_result.get("diagnostics", {}) or {}
    result: Dict[str, Any] = {
        "case_id": case_id,
        "application_prompt": prompt,
        "operating_temperature": temp,
        "am_preferred": am_preferred,
        "scenario_profile": scenario_profile,
        "allowed_material_families": _parse_list(requirements.get("allowed_material_families")),
        "weights_json": json.dumps(requirements.get("weights", {})),
        "notes": _parse_list(requirements.get("notes")),
        "status": candidate_result.get("status", "unknown"),
        "message": candidate_result.get("message", ""),
        "raw_candidate_count": _safe_len(candidate_result.get("candidates")),
        "final_candidate_count": 0,
        "top_candidate_id": "",
        "top_material_family": "",
        "recipe_modes_top": "",
        "analogues_top": "",
        "top5_ids": "",
        "top5_families": "",
        "score_range_top5": 0.0,
        "recipe_support_range_top5": 0.0,
        "warnings": _parse_list(diagnostics.get("warnings", [])),
        "raw_docs_retrieved": diagnostics.get("raw_docs_retrieved", 0),
        "unique_docs_after_request_acceptance": diagnostics.get("unique_docs_after_request_acceptance", 0),
        "rejected_by_family": diagnostics.get("rejected_by_family", 0),
        "rejected_by_complexity_gate": diagnostics.get("rejected_by_complexity_gate", 0),
        "baseline_final_candidate_count": diagnostics.get("final_candidate_count", 0),
    }

    req_df = pd.DataFrame([{
        "case_id": case_id,
        "application_prompt": prompt,
        "operating_temperature": temp,
        "am_preferred": am_preferred,
        "scenario_profile": scenario_profile,
        "allowed_material_families": _parse_list(requirements.get("allowed_material_families")),
        "weights_json": json.dumps(requirements.get("weights", {})),
        "decision_factor_weights_json": json.dumps(requirements.get("decision_factor_weights", {})),
        "notes": _parse_list(requirements.get("notes")),
    }])

    if candidate_result.get("status") != "success":
        diag_df = pd.json_normalize(diagnostics) if diagnostics else pd.DataFrame()
        if not diag_df.empty:
            diag_df.insert(0, "case_id", case_id)
        return {
            "summary": result,
            "requirements": req_df,
            "candidates": pd.DataFrame(),
            "top": pd.DataFrame(),
            "near_miss": pd.DataFrame(),
            "diagnostics": diag_df,
        }

    candidates = candidate_result["candidates"]
    scored = score_candidates(candidates, requirements)
    reranked = scientific_rerank(scored, requirements)
    reranked = add_provenance(reranked)
    top, near_miss = rank_candidates(reranked)

    result["final_candidate_count"] = _safe_len(reranked)
    if _safe_len(top) > 0:
        top0 = top.iloc[0]
        result["top_candidate_id"] = str(top0.get("candidate_id", ""))
        result["top_material_family"] = str(top0.get("material_family", ""))
        if "recipe_mode" in top.columns:
            result["recipe_modes_top"] = "; ".join(sorted(set(top["recipe_mode"].astype(str).tolist())))
        if "matched_alloy_name" in top.columns:
            result["analogues_top"] = "; ".join(sorted({str(v) for v in top["matched_alloy_name"].fillna("").tolist() if str(v).strip()}))
        result["top5_ids"] = "; ".join(top["candidate_id"].astype(str).tolist()) if "candidate_id" in top.columns else ""
        result["top5_families"] = "; ".join(top["material_family"].astype(str).tolist()) if "material_family" in top.columns else ""
        if "final_rank_score" in top.columns and _safe_len(top) > 1:
            result["score_range_top5"] = round(float(top["final_rank_score"].max() - top["final_rank_score"].min()), 2)
        if "recipe_support_score" in top.columns and _safe_len(top) > 1:
            result["recipe_support_range_top5"] = round(float(top["recipe_support_score"].max() - top["recipe_support_score"].min()), 2)

    candidate_detail = reranked.copy()
    if not candidate_detail.empty:
        candidate_detail.insert(0, "case_id", case_id)

    top_detail = top.copy()
    if not top_detail.empty:
        top_detail.insert(0, "case_id", case_id)

    near_detail = near_miss.copy()
    if not near_detail.empty:
        near_detail.insert(0, "case_id", case_id)

    diag_df = pd.json_normalize(diagnostics) if diagnostics else pd.DataFrame()
    if not diag_df.empty:
        diag_df.insert(0, "case_id", case_id)

    return {
        "summary": result,
        "requirements": req_df,
        "candidates": candidate_detail,
        "top": top_detail,
        "near_miss": near_detail,
        "diagnostics": diag_df,
    }


def build_cross_case_checks(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    rows: List[Dict[str, Any]] = []
    allowed_family_sets = summary_df["allowed_material_families"].astype(str).nunique()
    top5_sets = summary_df["top5_ids"].astype(str).nunique()
    top_family_sets = summary_df["top_material_family"].astype(str).nunique()

    for _, row in summary_df.iterrows():
        issues: List[str] = []
        if allowed_family_sets == 1:
            issues.append("Allowed families did not vary across cases.")
        if top5_sets == 1:
            issues.append("Top-5 candidate set was identical across all cases.")
        if top_family_sets == 1:
            issues.append("Top-ranked material family did not vary across all cases.")
        if float(row.get("score_range_top5", 0.0) or 0.0) < 3.0:
            issues.append("Top-5 final-rank spread is narrow (<3).")
        if float(row.get("recipe_support_range_top5", 0.0) or 0.0) < 4.0:
            issues.append("Top-5 recipe-support spread is narrow (<4).")
        if str(row.get("recipe_modes_top", "")).strip().lower() == "family_envelope":
            issues.append("Top set used only family-envelope recipes.")
        if str(row.get("top_material_family", "")).startswith("Ni-based") and top_family_sets == 1:
            issues.append("Ni-based family dominated every case.")

        rows.append({
            "case_id": row["case_id"],
            "status": row["status"],
            "top_candidate_id": row.get("top_candidate_id", ""),
            "top_material_family": row.get("top_material_family", ""),
            "issues": " | ".join(issues) if issues else "No immediate flattening flags.",
        })
    return pd.DataFrame(rows)


def save_outputs(
    output_dir: Path,
    summary_df: pd.DataFrame,
    checks_df: pd.DataFrame,
    requirements_df: pd.DataFrame,
    candidates_df: pd.DataFrame,
    top_df: pd.DataFrame,
    near_df: pd.DataFrame,
    diagnostics_df: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(output_dir / "prompt_sensitivity_summary.csv", index=False)
    checks_df.to_csv(output_dir / "prompt_sensitivity_checks.csv", index=False)
    requirements_df.to_csv(output_dir / "prompt_sensitivity_requirements.csv", index=False)
    candidates_df.to_csv(output_dir / "prompt_sensitivity_candidates.csv", index=False)
    top_df.to_csv(output_dir / "prompt_sensitivity_top.csv", index=False)
    near_df.to_csv(output_dir / "prompt_sensitivity_near_miss.csv", index=False)
    diagnostics_df.to_csv(output_dir / "prompt_sensitivity_diagnostics.csv", index=False)

    with pd.ExcelWriter(output_dir / "prompt_sensitivity_report.xlsx", engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        checks_df.to_excel(writer, sheet_name="Checks", index=False)
        requirements_df.to_excel(writer, sheet_name="Requirements", index=False)
        candidates_df.to_excel(writer, sheet_name="Candidates", index=False)
        top_df.to_excel(writer, sheet_name="Top", index=False)
        near_df.to_excel(writer, sheet_name="NearMiss", index=False)
        diagnostics_df.to_excel(writer, sheet_name="Diagnostics", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prompt sensitivity harness for the Aviation Material Selection Tool.")
    parser.add_argument("--cases", type=str, default="", help="Optional path to CSV/XLSX/JSON case file.")
    parser.add_argument("--output-dir", type=str, default="prompt_sensitivity_output", help="Directory for CSV/XLSX outputs.")
    args = parser.parse_args()

    cases_path = Path(args.cases) if args.cases else None
    if cases_path is not None:
        print(f"Loading cases from: {cases_path.resolve()}")
    cases_df = load_cases(cases_path)
    print(f"Loaded {len(cases_df)} case(s).")

    summaries: List[Dict[str, Any]] = []
    requirements_parts: List[pd.DataFrame] = []
    candidate_parts: List[pd.DataFrame] = []
    top_parts: List[pd.DataFrame] = []
    near_parts: List[pd.DataFrame] = []
    diag_parts: List[pd.DataFrame] = []

    for _, case_row in cases_df.iterrows():
        result = run_case(case_row)
        summaries.append(result["summary"])
        requirements_parts.append(result["requirements"])
        candidate_parts.append(result["candidates"])
        top_parts.append(result["top"])
        near_parts.append(result["near_miss"])
        diag_parts.append(result["diagnostics"])

    summary_df = pd.DataFrame(summaries)
    checks_df = build_cross_case_checks(summary_df)
    requirements_df = pd.concat(requirements_parts, ignore_index=True) if requirements_parts else pd.DataFrame()
    candidates_df = pd.concat(candidate_parts, ignore_index=True) if candidate_parts else pd.DataFrame()
    top_df = pd.concat(top_parts, ignore_index=True) if top_parts else pd.DataFrame()
    near_df = pd.concat(near_parts, ignore_index=True) if near_parts else pd.DataFrame()
    diagnostics_df = pd.concat(diag_parts, ignore_index=True) if diag_parts else pd.DataFrame()

    save_outputs(Path(args.output_dir), summary_df, checks_df, requirements_df, candidates_df, top_df, near_df, diagnostics_df)
    print(f"Wrote harness outputs to {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
