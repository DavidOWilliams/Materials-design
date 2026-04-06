from typing import Any, Dict, List, Tuple
from .diagnostics import candidate_log_record


def apply_baseline_filters(candidates: List[Any], query_ctx: Any) -> Tuple[List[Any], List[Any], Dict]:
    """
    Freeze-phase baseline filtering wrapper.

    Minimum responsibilities:
    - keep family-matching survival decisions here
    - keep complexity-gate survival decisions here
    - keep hard exclusion rules here
    - do NOT do soft reranking here
    """

    survivors = []
    rejected = []

    diag = {
        "query": getattr(query_ctx, "raw_input", None) if query_ctx else None,
        "queried_chemsys": getattr(query_ctx, "queried_chemsys", []),
        "raw_docs_retrieved": len(candidates),
        "unique_docs_after_dedup": len(candidates),
        "rejected_by_family": 0,
        "rejected_by_complexity_gate": 0,
        "removed_by_preference_filters": 0,
        "removed_by_am_filter": 0,
        "final_candidate_count": 0,
        "candidate_names_before_final_filtering": [],
        "candidate_names_after_final_filtering": [],
        "candidate_logs": [],
    }

    for c in candidates:
        # Default fields so logging never crashes
        if not hasattr(c, "candidate_name"):
            c.candidate_name = str(getattr(c, "name", "unknown_candidate"))

        if not hasattr(c, "assigned_family"):
            c.assigned_family = None

        if not hasattr(c, "family_match"):
            c.family_match = None

        if not hasattr(c, "complexity_score"):
            c.complexity_score = None

        if not hasattr(c, "complexity_threshold"):
            c.complexity_threshold = None

        if not hasattr(c, "rejection_reason"):
            c.rejection_reason = None

        if not hasattr(c, "rejection_stage"):
            c.rejection_stage = None

        if not hasattr(c, "survives_baseline"):
            c.survives_baseline = False

        diag["candidate_names_before_final_filtering"].append(c.candidate_name)

        # ---- FAMILY MATCH CHECK ----
        # Replace this block by calling your existing family logic.
        family_match = getattr(c, "family_match", True)

        if family_match is False:
            c.rejection_reason = "wrong_family"
            c.rejection_stage = "family_match"
            c.survives_baseline = False
            diag["rejected_by_family"] += 1
            rejected.append(c)
            diag["candidate_logs"].append(candidate_log_record(c))
            continue

        # ---- COMPLEXITY GATE CHECK ----
        # Replace this block by calling your existing complexity logic.
        complexity_pass = getattr(c, "passed_complexity_gate", True)

        if complexity_pass is False:
            c.rejection_reason = "complexity_gate"
            c.rejection_stage = "complexity_gate"
            c.survives_baseline = False
            diag["rejected_by_complexity_gate"] += 1
            rejected.append(c)
            diag["candidate_logs"].append(candidate_log_record(c))
            continue

        # ---- HARD EXCLUSION RULES ----
        # Replace this block by calling your existing hard exclusion logic.
        hard_excluded = getattr(c, "hard_excluded", False)

        if hard_excluded:
            c.rejection_reason = "hard_exclusion"
            c.rejection_stage = "baseline_exclusion"
            c.survives_baseline = False
            diag["removed_by_am_filter"] += 1
            rejected.append(c)
            diag["candidate_logs"].append(candidate_log_record(c))
            continue

        c.survives_baseline = True
        survivors.append(c)
        diag["candidate_names_after_final_filtering"].append(c.candidate_name)
        diag["candidate_logs"].append(candidate_log_record(c))

    diag["final_candidate_count"] = len(survivors)

    return survivors, rejected, diag