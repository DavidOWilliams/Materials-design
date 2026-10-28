"""Generic, conservative Pareto comparison for qualified evaluation records.

This module deliberately knows nothing about coupon physics or fixture names.
The caller must supply objective directions and already validated eligibility.
Unknown, missing or nonfinite metrics never become favourable defaults.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Objective:
    id: str
    direction: str

    def __post_init__(self):
        if not self.id or self.direction not in ("min", "max"):
            raise ValueError("Objective needs a nonempty id and min/max direction")


@dataclass(frozen=True)
class Candidate:
    id: str
    values: Mapping[str, float | None]
    eligible: bool
    context: str
    exclusion: str | None = None


def nondominated(candidates: Sequence[Candidate], objectives: Sequence[Objective]) -> dict:
    """Return qualified nondominated IDs within one explicitly matched context.

    Exact ties are represented by the lexicographically first ID; duplicates
    remain visible in the excluded map. No numerical ranking tolerance is
    silently introduced.
    """
    if not objectives or len({o.id for o in objectives}) != len(objectives):
        raise ValueError("Objective IDs must be nonempty and unique")
    if len({c.id for c in candidates}) != len(candidates):
        raise ValueError("Candidate IDs must be unique")
    contexts = {c.context for c in candidates}
    if len(contexts) > 1:
        raise ValueError("Incompatible comparison contexts")
    excluded = {}
    eligible = []
    for c in candidates:
        if type(c.eligible) is not bool:
            raise ValueError("Eligibility must be a strict boolean")
        if not isinstance(c.context, str) or not c.context.strip():
            raise ValueError("Comparison context must be nonempty")
        if not c.eligible:
            excluded[c.id] = c.exclusion or "not qualified/feasible"
            continue
        if any(o.id not in c.values or c.values[o.id] is None or
               isinstance(c.values[o.id], bool) or
               not isinstance(c.values[o.id], (int, float)) or
               not isfinite(c.values[o.id]) for o in objectives):
            excluded[c.id] = "missing or nonfinite objective"
            continue
        eligible.append(c)
    def vector(c):
        return tuple(float(c.values[o.id]) * (1 if o.direction == "min" else -1)
                     for o in objectives)
    selected = []
    seen = {}
    for c in sorted(eligible, key=lambda item: item.id):
        v = vector(c)
        if v in seen:
            excluded[c.id] = "exact objective tie with " + seen[v]
        else:
            seen[v] = c.id
            selected.append(c)
    pareto = []
    for c in selected:
        v = vector(c)
        if not any(other.id != c.id and
                   all(x <= y for x, y in zip(vector(other), v)) and
                   any(x < y for x, y in zip(vector(other), v))
                   for other in selected):
            pareto.append(c.id)
    return {"pareto_ids": sorted(pareto), "excluded": excluded,
            "eligible_ids": sorted(c.id for c in selected),
            "context": next(iter(contexts), None)}
