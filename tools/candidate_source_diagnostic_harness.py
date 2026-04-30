from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.requirement_inference import infer_requirements
from src.evaluation import apply_decision_profile
from src.candidate_generation import generate_candidates
from src.scoring import score_candidates
from src.reranking import scientific_rerank
from src.ranking import rank_candidates
from src.provenance import add_provenance
from src.requirement_schema import CANDIDATE_FAMILY_TO_SCOPE_KEY


OUTPUT_DIR = Path("candidate_source_diagnostics")

CASES = [
    {
        "case_id": "hot_section_creep_am",
        "prompt": "Design a material for a hot aviation component operating at 850°C where creep is critical and additive manufacturing is preferred.",
        "temperature": 850,
        "am_preferred": True,
        "profile": "Balanced",
    },
    {
        "case_id": "lightweight_strength_to_weight",
        "prompt": "Design a lightweight structural aviation bracket with high strength-to-weight and good fatigue resistance. Conventional processing is acceptable.",
        "temperature": 350,
        "am_preferred": False,
        "profile": "Balanced",
    },
    {
        "case_id": "wear_hot_corrosion",
        "prompt": "Select a material for a hot-corrosion and wear exposed aviation seal surface with sliding contact and salt contaminant exposure.",
        "temperature": 725,
        "am_preferred": False,
        "profile": "Performance-first",
    },
    {
        "case_id": "am_complex_geometry_creep",
        "prompt": "Design a high temperature component with complex internal cooling channels where additive manufacturing is preferred and creep still matters.",
        "temperature": 825,
        "am_preferred": True,
        "profile": "AM route-first",
    },
    {
        "case_id": "certification_mature_conventional",
        "prompt": "Select a mature conventional-route aerospace material for a moderately warm structural component where certification maturity and inspectability matter.",
        "temperature": 450,
        "am_preferred": False,
        "profile": "Cost & sustainability-aware",
    },
    {
        "case_id": "extreme_temperature_refractory",
        "prompt": "Explore an extreme-temperature material concept above 1000°C where creep capability is more important than cost and specialist processing is acceptable.",
        "temperature": 1050,
        "am_preferred": False,
        "profile": "Performance-first",
    },
]


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True)
    except Exception:
        return str(value)


def _family_scope(value: Any) -> str:
    text = str(value or "")
    return CANDIDATE_FAMILY_TO_SCOPE_KEY.get(text, text)


def _value_counts_json(df: pd.DataFrame, column: str) -> str:
    if df is None or len(df) == 0 or column not in df.columns:
        return "{}"
    return _json_dumps(df[column].fillna("Unknown").astype(str).value_counts().to_dict())


def _source_label(value: Any) -> str:
    text = str(value or "materials_project")
    if text == "engineering_analogue":
        return "engineering_analogue"
    return "materials_project"


def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    requirements = infer_requirements(case["prompt"], case["temperature"], case["am_preferred"])
    requirements = apply_decision_profile(requirements, case["profile"])
    scope_plan = requirements.get("scope_plan", {}) or {}
    family_priors = scope_plan.get("family_priors", requirements.get("family_priors", {})) or {}
    top_family = max(family_priors.items(), key=lambda item: item[1])[0] if family_priors else ""

    result = generate_candidates(requirements)
    candidates = result.get("candidates")
    diagnostics = result.get("diagnostics", {}) or {}

    summary: Dict[str, Any] = {
        "case_id": case["case_id"],
        "status": result.get("status"),
        "top_prompt_family": top_family,
        "family_priors": _json_dumps(family_priors),
        "final_candidate_count": len(candidates) if candidates is not None else 0,
        "candidate_source_mix": _json_dumps(diagnostics.get("candidate_source_mix", {})),
        "surviving_family_mix": _json_dumps(diagnostics.get("surviving_family_mix", {})),
        "engineering_analogue_candidate_count": diagnostics.get("engineering_analogue_candidate_count", 0),
        "mp_candidate_count_before_supplementation": diagnostics.get("mp_candidate_count_before_supplementation", 0),
        "engineering_analogue_family_mix": _json_dumps(diagnostics.get("engineering_analogue_family_mix", {})),
        "supplementation_plan": _json_dumps(diagnostics.get("engineering_analogue_supplementation_plan", [])),
        "supplementation_result": _json_dumps(diagnostics.get("engineering_analogue_supplementation", [])),
        "warnings": _json_dumps(diagnostics.get("warnings", [])),
    }

    candidate_rows: List[Dict[str, Any]] = []
    if candidates is not None and len(candidates) > 0:
        for idx, (_, row) in enumerate(candidates.iterrows(), start=1):
            candidate_rows.append(
                {
                    "case_id": case["case_id"],
                    "generation_rank": idx,
                    "candidate_id": row.get("candidate_id"),
                    "candidate_source": _source_label(row.get("candidate_source")),
                    "source_alloy_id": row.get("source_alloy_id"),
                    "source_alloy_name": row.get("source_alloy_name"),
                    "material_family": row.get("material_family"),
                    "scope_family": _family_scope(row.get("material_family")),
                    "composition_concept": row.get("composition_concept"),
                    "chemsys": row.get("chemsys"),
                    "retrieval_mode": row.get("retrieval_mode"),
                    "n_elements": row.get("n_elements"),
                    "alloy_likeness_score": row.get("alloy_likeness_score"),
                    "generated_note": row.get("generated_note"),
                }
            )

    ranked_rows: List[Dict[str, Any]] = []
    try:
        if candidates is not None and len(candidates) > 0:
            scored = score_candidates(candidates, requirements)
            reranked = scientific_rerank(scored, requirements)
            with_prov = add_provenance(reranked)
            top, near = rank_candidates(with_prov)
            ranked = with_prov.sort_values("final_rank_score", ascending=False).reset_index(drop=True)
            summary["ranked_source_mix"] = _value_counts_json(ranked, "candidate_source")
            summary["ranked_recipe_mode_mix"] = _value_counts_json(ranked, "recipe_mode")
            summary["top5_source_mix"] = _value_counts_json(top, "candidate_source")
            summary["top5_recipe_mode_mix"] = _value_counts_json(top, "recipe_mode")
            summary["top5_family_mix"] = _json_dumps(top["material_family"].map(_family_scope).value_counts().to_dict()) if top is not None and len(top) > 0 else "{}"

            for idx, (_, row) in enumerate(ranked.iterrows(), start=1):
                ranked_rows.append(
                    {
                        "case_id": case["case_id"],
                        "rank": idx,
                        "candidate_id": row.get("candidate_id"),
                        "candidate_source": _source_label(row.get("candidate_source")),
                        "source_alloy_name": row.get("source_alloy_name"),
                        "material_family": row.get("material_family"),
                        "scope_family": _family_scope(row.get("material_family")),
                        "recipe_mode": row.get("recipe_mode"),
                        "matched_alloy_name": row.get("matched_alloy_name"),
                        "analogue_weighted_score": row.get("analogue_weighted_score"),
                        "recipe_support_score": row.get("recipe_support_score"),
                        "final_rank_score": row.get("final_rank_score"),
                        "confidence": row.get("confidence"),
                        "provenance": row.get("provenance"),
                    }
                )
    except Exception as exc:
        summary["ranking_error"] = str(exc)

    diagnostics_rows = []
    for item in diagnostics.get("engineering_analogue_supplementation", []) or []:
        row = {"case_id": case["case_id"]}
        row.update(item)
        diagnostics_rows.append(row)

    return {
        "summary": summary,
        "candidate_rows": candidate_rows,
        "ranked_rows": ranked_rows,
        "supplementation_rows": diagnostics_rows,
    }


def write_insights(summary_df: pd.DataFrame, ranked_df: pd.DataFrame, supplementation_df: pd.DataFrame) -> None:
    lines: List[str] = []
    lines.append("# Candidate Source Diagnostic Insights")
    lines.append("")
    lines.append("## Purpose")
    lines.append("This harness checks whether Build 3.1 is adding explicitly labelled curated engineering analogue candidates, and whether those candidates improve source diversity and recipe support without relaxing Materials Project request-aware acceptance.")
    lines.append("")
    lines.append("## Run summary")
    lines.append(f"- Cases run: **{len(summary_df)}**")
    if "engineering_analogue_candidate_count" in summary_df.columns:
        total_kb = int(pd.to_numeric(summary_df["engineering_analogue_candidate_count"], errors="coerce").fillna(0).sum())
        lines.append(f"- Engineering analogue candidates added across all cases: **{total_kb}**")
    if len(ranked_df) > 0 and "candidate_source" in ranked_df.columns:
        source_mix = ranked_df["candidate_source"].fillna("materials_project").astype(str).value_counts().to_dict()
        lines.append(f"- Ranked candidate source mix: `{json.dumps(source_mix)}`")
    if len(ranked_df) > 0 and "recipe_mode" in ranked_df.columns:
        recipe_mix = ranked_df["recipe_mode"].fillna("Unknown").astype(str).value_counts().to_dict()
        lines.append(f"- Ranked recipe mode mix: `{json.dumps(recipe_mix)}`")
    lines.append("")
    lines.append("## What to inspect")
    lines.append("1. `candidate_source_summary.csv`: check that prompt-favoured families receive engineering analogues when MP candidates are sparse or simplified.")
    lines.append("2. `candidate_source_ranked_candidates.csv`: check whether engineering analogue candidates produce `named_analogue` or `analogue_guided` recipe modes.")
    lines.append("3. `candidate_source_supplementation.csv`: inspect why each family was supplemented and which named analogues were selected.")
    lines.append("")
    lines.append("## Build 3.1 success signals")
    lines.append("- Wear / hot-corrosion prompts should include at least one Co-based engineering analogue if MP Co candidates do not survive.")
    lines.append("- Hot-section creep prompts should include stronger Ni engineering analogues, not only simplified Al-Cr-Ni / Al-Co-Ni MP ternaries.")
    lines.append("- Lightweight prompts should keep Ti candidates visible and may add Ti engineering analogues where useful.")
    lines.append("- Candidate-source labels should make clear which candidates are Materials Project records and which are curated engineering analogues.")
    OUTPUT_DIR.joinpath("candidate_source_diagnostic_insights.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries: List[Dict[str, Any]] = []
    candidate_rows: List[Dict[str, Any]] = []
    ranked_rows: List[Dict[str, Any]] = []
    supplementation_rows: List[Dict[str, Any]] = []

    for case in CASES:
        print(f"Running {case['case_id']}...")
        result = run_case(case)
        summaries.append(result["summary"])
        candidate_rows.extend(result["candidate_rows"])
        ranked_rows.extend(result["ranked_rows"])
        supplementation_rows.extend(result["supplementation_rows"])

    summary_df = pd.DataFrame(summaries)
    candidate_df = pd.DataFrame(candidate_rows)
    ranked_df = pd.DataFrame(ranked_rows)
    supplementation_df = pd.DataFrame(supplementation_rows)

    summary_df.to_csv(OUTPUT_DIR / "candidate_source_summary.csv", index=False)
    candidate_df.to_csv(OUTPUT_DIR / "candidate_source_generated_candidates.csv", index=False)
    ranked_df.to_csv(OUTPUT_DIR / "candidate_source_ranked_candidates.csv", index=False)
    supplementation_df.to_csv(OUTPUT_DIR / "candidate_source_supplementation.csv", index=False)
    write_insights(summary_df, ranked_df, supplementation_df)

    print(f"Done. Outputs written to {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
