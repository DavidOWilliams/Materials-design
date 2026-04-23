from __future__ import annotations

import json
from pathlib import Path

from src.candidate_generation import run_coverage_probe

CASES = [
    "Co-Cr-W",
    "Co-Cr-Ni",
    "Co-Cr-Mo",
]

OUT_DIR = Path("probe_outputs")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    all_summaries = {}

    for case in CASES:
        result = run_coverage_probe(case, max_rows_per_strategy=50)
        df = result["probe_rows"]

        csv_name = case.lower().replace("-", "_") + "_probe.csv"
        df.to_csv(OUT_DIR / csv_name, index=False)

        all_summaries[case] = {
            "requested_family": result["requested_family"],
            "strategies": result["strategies"],
        }

        print("=" * 80)
        print(case)
        print(f"requested_family: {result['requested_family']}")
        print("strategy summary:")
        for item in result["strategies"]:
            print(
                f"  {item['retrieval_mode']:28s} "
                f"{item['matched_query_chemsys']:15s} "
                f"returned={item['returned_count']:3d} "
                f"accepted_for_request={item['accepted_for_request_count']:3d}"
                + (f" error={item['error']}" if item["error"] else "")
            )

        if df.empty:
            print("No rows returned.")
            continue

        view_cols = [
            "retrieval_mode",
            "matched_query_chemsys",
            "formula_pretty",
            "chemsys",
            "candidate_family",
            "family_matches_request",
            "accepted_for_request",
            "rejection_reason",
        ]
        print()
        print(df[view_cols].head(20).to_string(index=False))

    with open(OUT_DIR / "cobalt_probe_summary.json", "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)


if __name__ == "__main__":
    main()

