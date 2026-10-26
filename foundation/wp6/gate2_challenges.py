"""Frozen WP6 Gate 2 scientific challenges; no changes to WP2/WP4/WP5."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from material_core.wp5_service import execute, replay, inspect
from material_core.wp4_feedback import starting_inputs
from material_core.wp2_numerical import evaluate, numerical_comparison_eligible
from material_core.contracts import RunInputs

def run(root):
    root=Path(root)
    if root.exists(): raise FileExistsError(root)
    root.mkdir(parents=True)
    dossier=root/"no_improvement.json"
    record=execute(dossier,elements=128,mass_limit=1.0,budget=8,feedback=True)
    actual=record["stop_reason"]
    no_improvement=dict(expected="no_improvement_possible",actual=actual,
        status="pass" if actual=="no_improvement_possible" else "fail",
        proposals=record["proposals"],evaluations=record["evaluations"],
        refinement_solves=record["refinement_solves"],
        candidates=[{"index":r["index"],"feasible":r["feasible"],
                     "numerical_quality":r["numerical_quality"],
                     "feedback":r["feedback"],"objectives":r["objectives"]}
                    for r in record["records"]],
        replay=replay(dossier),measured_evidence=inspect(dossier)["measured_evidence"])
    attempts=[]
    selected=None
    for elements in (1,2,4,8):
        inputs=starting_inputs(elements=elements,mass_limit=31.0)
        result=evaluate(inputs)
        eligible=numerical_comparison_eligible(result,inputs.brief)
        row=dict(elements=elements,input=inputs.model_dump(mode="json"),
                 evaluation=result.model_dump(mode="json"),
                 numerical_quality=result.numerical_quality,status=result.status,
                 eligible=eligible)
        attempts.append(row)
        if result.status=="complete" and result.numerical_quality=="unresolved" and not eligible:
            selected=row
            break
    unresolved=dict(expected="complete evaluation with unresolved numerical quality and ineligible",
        status="pass" if selected is not None else "inconclusive",
        selected_elements=None if selected is None else selected["elements"],
        attempts=[dict(elements=a["elements"],status=a["status"],
                       numerical_quality=a["numerical_quality"],eligible=a["eligible"])
                  for a in attempts])
    (root/"numerical_attempts.json").write_text(json.dumps(attempts,indent=2,sort_keys=True)+"\n")
    (root/"gate2_results.json").write_text(json.dumps(dict(no_improvement=no_improvement,
        unresolved=unresolved),indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps(dict(no_improvement=no_improvement["status"],
                          no_improvement_actual=actual,unresolved=unresolved["status"],
                          unresolved_mesh=unresolved["selected_elements"])))
    if no_improvement["status"]!="pass" or unresolved["status"]!="pass":
        raise SystemExit(1)

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: gate2_challenges.py OUTPUT_DIRECTORY")
    run(sys.argv[1])
