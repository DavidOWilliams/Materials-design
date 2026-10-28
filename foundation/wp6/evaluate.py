"""WP6 reproducible D1 evaluation runner; reuses WP5/WP4 without new physics."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from material_core.wp5_service import execute, replay, inspect, prepared_inputs
from material_core.wp5_brief_editor import revise_brief

CASES = (
    ("control_on", 31.0, 0.005, 0.25, True, 1),
    ("control_off", 31.0, 0.005, 0.25, False, 1),
    ("tight_mass_on", 30.0, 0.005, 0.25, True, 1),
    ("tight_mass_off", 30.0, 0.005, 0.25, False, 1),
    ("layer_sensitivity", 31.0, 0.010, 0.25, True, 2),
    ("feed_sensitivity", 31.0, 0.005, 0.50, True, 3),
    ("heldout_on", 31.0, 0.005, 0.25, True, 1),
    ("heldout_off", 31.0, 0.005, 0.25, False, 1),
    ("no_feasible", 1.0, 0.005, 0.25, True, 1),
)
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(root, *, elements=4096, budget=4):
    if type(elements) is not int or elements < 1 or type(budget) is not int or budget < 1:
        raise ValueError("Positive integer mesh and budget required")
    root = Path(root)
    if root.exists():
        raise FileExistsError("WP6 output directory already exists")
    root.mkdir(parents=True)
    rows=[]
    for name,mass,layer,feed,feedback,version in CASES:
        path=root/(name+".json")
        row=dict(case=name, mass_limit_kg_m2=mass,layer_resolution_m=layer,
                 feed_fraction_resolution=feed,feedback=feedback,
                 process_version=version,nominal_budget=budget)
        try:
            brief = None
            if name.startswith('heldout_'):
                original=prepared_inputs(elements=elements,mass_limit=mass).brief
                brief=revise_brief(original, {'duty': 'WP6 held-out duty: hypothetical secondary thermal protection coupon; synthetic demonstration only', 'evaluation_budget': budget}).model_dump(mode='json')
            result=execute(path,elements=elements,mass_limit=mass,layer=layer,
                           feed=feed,feedback=feedback,budget=budget,process_version=version,brief=brief)
            detail=inspect(path)
            check=replay(path)
            row.update(status="complete",dossier_sha256=digest(path),
                       stop_reason=result["stop_reason"],evaluations=result["evaluations"],
                       unused_candidate_slots=budget-result['proposals'],
                       comparison_effort='maximum slots matched, actual evaluations may differ',
                       proposals=result["proposals"],refinement_solves=result["refinement_solves"],
                       feasible_candidates=sum(bool(x["feasible"]) for x in result["records"]),
                       baseline_intended_hash=result['baseline_intended_inputs']['design']['id'],
                       brief_hash=detail['brief_hash'],
                       records=[dict(index=x["index"],objectives=x["objectives"],
                                     numerical_quality=x["numerical_quality"],
                                     eligible=bool(x["feasible"]),feedback=x["feedback"],
                                     intended_hash=x["intended_hash"],estimated_hash=x["estimated_hash"])
                                for x in result["records"]],
                       measured_evidence=detail["measured_evidence"],
                       manufacturing_validation=detail["manufacturing_validation"],
                       replay=check)
            if name=='no_feasible' and row['feasible_candidates']:
                row.update(status='failed',error='No-feasible challenge unexpectedly found a feasible candidate')
        except Exception as exc:
            row.update(status="failed",error=type(exc).__name__+": "+str(exc))
        rows.append(row)
    pairs=[]
    for prefix in ('control','tight_mass','heldout'):
        on=next(x for x in rows if x['case']==prefix+'_on')
        off=next(x for x in rows if x['case']==prefix+'_off')
        pairs.append(dict(pair=prefix, nominal_budget=budget,
            on_evaluations=on.get('evaluations'),off_evaluations=off.get('evaluations'),
            equal_actual_effort=(on.get('evaluations')==off.get('evaluations') if on.get('status')=='complete' and off.get('status')=='complete' else None),
            causal_superiority_established=False))
    report=dict(pairs=pairs,schema_version=1,protocol="foundation/wp6/PREREGISTERED_PROTOCOL.md",
                scientific_scope="D1 synthetic only; no measured manufacturing evidence",
                units={"thermal_transmission":"W/m2","areal_mass":"kg/m2",
                       "tensile_thermal_mismatch":"Pa"},cases=rows)
    (root/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--elements",type=int,default=4096)
    p.add_argument("--budget",type=int,default=4)
    a=p.parse_args()
    report=run(a.output,elements=a.elements,budget=a.budget)
    print(json.dumps({"cases":len(report["cases"]),
                      "complete":sum(x["status"]=="complete" for x in report["cases"]),
                      "failed":sum(x["status"]=="failed" for x in report["cases"])}))
    if any(x["status"]!="complete" for x in report["cases"]):
        raise SystemExit(1)
if __name__=="__main__":
    main()
