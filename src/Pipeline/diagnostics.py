from typing import Any, Dict, List


def candidate_log_record(candidate: Any) -> Dict:
    return {
        "candidate_name": getattr(candidate, "candidate_name", None),
        "assigned_family": getattr(candidate, "assigned_family", None),
        "family_match": getattr(candidate, "family_match", None),
        "complexity_score": getattr(candidate, "complexity_score", None),
        "complexity_threshold": getattr(candidate, "complexity_threshold", None),
        "rejection_reason": getattr(candidate, "rejection_reason", None),
        "rejection_stage": getattr(candidate, "rejection_stage", None),
        "survives_baseline": getattr(candidate, "survives_baseline", None),
    }


def build_warnings(diag: Dict) -> List[str]:
    warnings = []

    raw_docs = diag.get("raw_docs_retrieved", 0)
    unique_docs = diag.get("unique_docs_after_dedup", 0)
    final_count = diag.get("final_candidate_count", 0)
    rejected_by_complexity = diag.get("rejected_by_complexity_gate", 0)

    if raw_docs > 0 and final_count == 0:
        warnings.append(
            "No final candidates survived filtering. This may indicate that the complexity gate or other filters are too strict."
        )

    if unique_docs > 0 and rejected_by_complexity == unique_docs:
        warnings.append(
            "All deduplicated candidates were removed by the complexity gate."
        )

    return warnings