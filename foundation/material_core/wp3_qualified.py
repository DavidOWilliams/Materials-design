"""WP3 qualified comparison boundary: derive eligibility from WP2, never caller flags."""
from __future__ import annotations

from .wp2_numerical import numerical_comparison_eligible, compatible_comparison
from .wp3_pareto import Candidate, Objective, nondominated


def qualified_pareto(records, brief):
    """records: sequence of (candidate_id, WP2 Evaluation).

    Intended-only manufacturing feasibility remains unknown. This is a
    *numerically qualified* Pareto view, not a manufacturing-ready ranking.
    """
    if not records:
        return nondominated([], [Objective(o.id, o.direction) for o in brief.objectives])
    if any(not compatible_comparison(records[0][1], evaluation)
           for _, evaluation in records[1:]):
        raise ValueError("Incompatible WP2 evaluation contexts")
    candidates = []
    for identifier, evaluation in records:
        eligible = numerical_comparison_eligible(evaluation, brief)
        metrics = {m.objective_id: (None if m.value is None else m.value.value)
                   for m in evaluation.metrics}
        candidates.append(Candidate(
            id=identifier, values=metrics, eligible=eligible,
            context=evaluation.comparison_context_hash or "",
            exclusion=None if eligible else
            "WP2 numerical quality, completeness, hard constraint or context not qualified"))
    result = nondominated(candidates, [Objective(o.id, o.direction) for o in brief.objectives])
    result["interpretation"] = ("Numerical qualification only; manufacturing feasibility "
                                "and evidence maturity are independent and not certified")
    return result
