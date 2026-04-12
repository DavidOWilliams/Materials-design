from __future__ import annotations

from typing import Dict, Any, List

from src.candidate_generation import generate_candidates


def make_requirements(
    family: str,
    am_preferred: bool = False,
    operating_temperature: int = 850,
    forced_chemsys=None,
) -> Dict[str, Any]:
    return {
        "application_prompt": f"Direct validation for {family}",
        "operating_temperature": operating_temperature,
        "am_preferred": am_preferred,
        "allowed_material_families": [family],
        "forced_chemsys": forced_chemsys,
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
        "name": "ni_cr_al",
        "family": "Ni-based superalloy",
        "forced_chemsys": ["Ni-Cr-Al"],
        "expected_family_contains": "Ni-based",
    },
    {
        "name": "ni_cr_co",
        "family": "Ni-based superalloy",
        "forced_chemsys": ["Ni-Cr-Co"],
        "expected_family_contains": "Ni-based",
    },
    {
        "name": "co_cr_w",
        "family": "Co-based alloy",
        "forced_chemsys": ["Co-Cr-W"],
        "expected_family_contains": "Co-based",
    },
    {
        "name": "co_cr_ni",
        "family": "Co-based alloy",
        "forced_chemsys": ["Co-Cr-Ni"],
        "expected_family_contains": "Co-based",
    },
    {
        "name": "co_cr_mo",
        "family": "Co-based alloy",
        "forced_chemsys": ["Co-Cr-Mo"],
        "expected_family_contains": "Co-based",
    },
    {
        "name": "mo_nb_ti",
        "family": "Refractory alloy concept",
        "forced_chemsys": ["Mo-Nb-Ti"],
        "expected_family_contains": "Refractory",
    },
    {
        "name": "nb_ti_zr",
        "family": "Refractory alloy concept",
        "forced_chemsys": ["Nb-Ti-Zr"],
        "expected_family_contains": "Refractory",
    },
]

def run_case(case: Dict[str, Any], am_preferred: bool) -> Dict[str, Any]:
    requirements = make_requirements(
    case["family"],
    am_preferred=am_preferred,
    forced_chemsys=case.get("forced_chemsys"),
)
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
        "queried_chemsys": diagnostics.get("queried_chemsys", []),
        "mp_query_failures": diagnostics.get("mp_query_failures", []),
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
            print("queried_chemsys:", summary["queried_chemsys"])
            print("mp_query_failures:", summary["mp_query_failures"])
            print("warnings:", summary["warnings"])
            print("candidate_logs_sample:", summary["candidate_logs"][:5])
