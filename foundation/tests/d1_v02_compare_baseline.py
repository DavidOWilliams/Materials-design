"""Compare deterministic WP3/WP4 numerical outcomes against the accepted release.

Uses isolated Python processes, distinct PYTHONPATHs, fresh run stores, and
compares full numeric objectives and exact Pareto results (not app formatting).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = r'''
import json, sys
from pathlib import Path
from material_core.wp4_feedback import run
from material_core.wp3_search import run_search
root=Path(sys.argv[1])
wp4=run(elements=128,mass_limit=31.,budget=4)
wp3=run_search(root/"wp3"/"campaign.json",seed=17,budget=9,elements=128,mass_limit=31.,method="explore")
report={
    "wp4":{"stop_reason":wp4["stop_reason"],
           "records":[{"index":r["index"],"objectives":r["objectives"],
                       "feasible":r["feasible"],"feedback":r["feedback"],
                       "numerical_quality":r["numerical_quality"]} for r in wp4["records"]]},
    "wp3":{"stop_reason":wp3["stop_reason"],
           "pareto":wp3["qualified_comparison"],
           "proposals":[{"index":p["index"],"status":p["status"],"objectives":p.get("objectives"),
                         "qualified":p.get("qualified"),"numerical_quality":p.get("numerical_quality")}
                        for p in wp3["proposals"]]}
}
print(json.dumps(report,sort_keys=True,allow_nan=False))
'''

def run_one(root, source, destination):
    env=os.environ.copy()
    env["PYTHONPATH"]=str(source/"foundation")
    proc=subprocess.run([sys.executable,"-c",SCRIPT,str(destination)],
                        cwd=root,env=env,capture_output=True,text=True,check=True)
    return json.loads(proc.stdout.strip().splitlines()[-1])

def main():
    repo=Path.cwd()
    base=Path(sys.argv[1]).resolve()
    evidence=Path(sys.argv[2]).resolve()
    evidence.mkdir(parents=True,exist_ok=False)
    if not (base/"foundation"/"material_core"/"wp4_feedback.py").exists():
        raise ValueError("Expected separate baseline worktree")
    original=run_one(repo,base,evidence/"baseline")
    revised=run_one(repo,repo,evidence/"v02")
    (evidence/"baseline-outcomes.json").write_text(json.dumps(original,indent=2,sort_keys=True))
    (evidence/"v02-outcomes.json").write_text(json.dumps(revised,indent=2,sort_keys=True))
    if original!=revised:
        raise AssertionError("Scientific WP3/WP4 outcome mismatch; inspect exact JSON")
    print("PASS: identical WP3 intended-state Pareto/proposal and WP4 feedback/numerical objective outcomes")
if __name__=="__main__":
    main()
