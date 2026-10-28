"""D1 read-only campaign presentation; no scientific/eligibility recalculation.

The WP4 numerical outcomes and strict WP3 Pareto routine remain authoritative.
"""
from __future__ import annotations

import json
from pathlib import Path

from .wp3_pareto import Candidate, Objective, nondominated
from .wp5_service import inspect

DIRECTIONS = (("thermal_transmission", "min", "W/m2"),
              ("areal_mass", "min", "kg/m2"),
              ("tensile_thermal_mismatch", "min", "Pa"))


def summary(path):
    """Open integrity-checked dossier and describe the *actual* candidate set.

    Never promote an unresolved, infeasible or missing-objective candidate.
    No frontend-specific implementation is imported.
    """
    detail = inspect(path)
    records = detail["records"]
    candidates = []
    rows = []
    for record in records:
        idx = record["index"]
        eligibility = record["feasible"] is True
        reasons = []
        if record["feasible"] is not True:
            if record["feedback"] is not None:
                reasons.append("Areal mass exceeds synthetic scenario constraint")
            if record["numerical_quality"] != "qualified":
                reasons.append("Numerical evidence: " + str(record["numerical_quality"]))
            if record["evaluation"]["feasibility"] != "conditional":
                reasons.append("Numerical feasibility: " + str(record["evaluation"]["feasibility"]))
            if record["evaluation"]["manufacturing_feasibility"] != "conditional":
                reasons.append("Manufacturing feasibility: " + str(record["evaluation"]["manufacturing_feasibility"]))
            if not reasons:
                reasons.append("Not eligible under WP4 conditional scenario rules")
        values = record["objectives"]
        rows.append({"candidate": idx, "eligible": eligibility,
                     "numerical_quality": record["numerical_quality"],
                     "reason": "; ".join(reasons) if reasons else "Conditionally scenario-feasible",
                     "pareto": False,
                     **{name: values.get(name) for name, _, _ in DIRECTIONS}})
        candidates.append(Candidate(id=str(idx), values=values, eligible=eligibility,
                                    context=detail["brief_hash"],
                                    exclusion="; ".join(reasons) if reasons else None))
    pareto = nondominated(candidates, [Objective(name, direction)
                                       for name, direction, _ in DIRECTIONS])
    for row in rows:
        row["pareto"] = str(row["candidate"]) in pareto["pareto_ids"]
        if str(row["candidate"]) in pareto["excluded"] and row["eligible"]:
            row["pareto_note"] = pareto["excluded"][str(row["candidate"])]
        elif row["eligible"] and not row["pareto"]:
            row["pareto_note"] = "Dominated within this single campaign"
        else:
            row["pareto_note"] = "Nondominated" if row["pareto"] else "Not Pareto eligible"
    return {"path": str(Path(path)), "stop_reason": detail["stop_reason"],
            "brief_hash": detail["brief_hash"], "rows": rows, "pareto": pareto,
            "directions": [{"objective": n, "direction": d, "unit": u}
                           for n, d, u in DIRECTIONS],
            "measured_evidence": None, "manufacturing_validation": "not_established",
            "records": records, "export": detail["export"]}


def selected_candidate(path, index):
    data = summary(path)
    if type(index) is not int or index < 0 or index >= len(data["records"]):
        raise ValueError("Candidate index outside persisted campaign")
    record = data["records"][index]
    if record["index"] != index:
        raise ValueError("Candidate index mismatch")
    return {"summary": data["rows"][index], "intended_design": record["intended_design"],
            "estimated_inputs": record["estimated_inputs"],
            "evaluation": record["evaluation"],
            "feedback": record["feedback"], "balances": record["balances"],
            "intended_hash": record["intended_hash"],
            "estimated_hash": record["estimated_hash"],
            "evaluation_hash": record["evaluation_hash"],
            "scientific_status": "synthetic estimated state only; not measured or validated"}
