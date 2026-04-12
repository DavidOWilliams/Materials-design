from __future__ import annotations

from typing import Dict, Any, List

from src.candidate_generation import generate_candidates


def make_requirements(
    family: str,
    am_preferred: bool = False,
    operating_temperature: int = 850,
) -> Dict[str, Any]:
    return {
        "application_prompt": f"Direct validation for {family}",
        "operating_temperature": operating_temperature,
        "am_preferred": am_preferred,
        "allowed_material_families": [family],
        "weights": {
            "creep_priority": 0.35,
            "toughness_priority": 0.20,
            "temperature_priority": 0.30,
            "cost_priority": 0.10,
            "sustainability_priority": 0.05,
        },
        "notes": ["Direct chemistry validation harness."],
    }


TEST_CASES: List[Dict[str, Any]] = [
    {
        "name": "ni_basic",
        "family": "Ni-based superalloy",
        "expected_family_contains": "Ni-based",
    },
    {
        "name": "co_basic",
        "family": "Co-based alloy",
        "expected_family_contains": "Co-based",
    },
    {
        "name": "refractory_basic",
        "family": "Refractory alloy concept",
        "expected_family_contains": "Refractory",
    },
]


def run_case(case: Dict[str, Any], am_preferred: bool) -> Dict[str, Any]:
    requirements = make_requirements(case["family"], am_preferred=am_preferred)
    result = generate_candidates(requirements)

    candidates = result.get("candidates")
    diagnostics = result.get("diagnostics", {})

    dominant_families = []
    if candidates is not None and len(candidates) > 0 and "material_family" in candidates.columns:
        dominant_families = candidates["material_family"].astype(str).unique().tolist()

    return {
        "case": case["name"],
        "family": case["family"],
        "am_preferred": am_preferred,
        "status": result["status"],
        "final_candidate_count": diagnostics.get("final_candidate_count"),
        "raw_docs_retrieved": diagnostics.get("raw_docs_retrieved"),
        "unique_docs_after_dedup": diagnostics.get("unique_docs_after_dedup"),
        "rejected_by_family": diagnostics.get("rejected_by_family"),
        "rejected_by_complexity_gate": diagnostics.get("rejected_by_complexity_gate"),
        "removed_by_am_filter": diagnostics.get("removed_by_am_filter"),
        "dominant_families": dominant_families,
        "warnings": diagnostics.get("warnings", []),
        "candidate_logs": diagnostics.get("candidate_logs", []),
    }


if __name__ == "__main__":
    for case in TEST_CASES:
        for am_preferred in (False, True):
            summary = run_case(case, am_preferred)
            print("=" * 80)
            print(summary["case"], "| am_preferred =", summary["am_preferred"])
            print("status:", summary["status"])
            print("raw_docs_retrieved:", summary["raw_docs_retrieved"])
            print("unique_docs_after_dedup:", summary["unique_docs_after_dedup"])
            print("rejected_by_family:", summary["rejected_by_family"])
            print("rejected_by_complexity_gate:", summary["rejected_by_complexity_gate"])
            print("removed_by_am_filter:", summary["removed_by_am_filter"])
            print("final_candidate_count:", summary["final_candidate_count"])
            print("dominant_families:", summary["dominant_families"])
            print("warnings:", summary["warnings"])
            print("candidate_logs_sample:", summary["candidate_logs"][:5])