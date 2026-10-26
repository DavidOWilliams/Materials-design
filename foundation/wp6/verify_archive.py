"""Separate-process verification of WP6 persisted numerical dossiers."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from material_core.wp5_service import inspect, replay

def verify(root):
    root=Path(root)
    report=json.loads((root/"report.json").read_text())
    rows=[]
    for case in report["cases"]:
        name=case["case"]
        path=root/(name+".json")
        if case["status"]!="complete":
            raise ValueError(f"Campaign did not complete: {name}")
        detail=inspect(path)
        result=replay(path)
        status=result.get("status") if isinstance(result,dict) else None
        if status!="passed":
            raise ValueError(f"Replay did not pass for {name}: {result}")
        if detail["measured_evidence"] is not None:
            raise ValueError(f"Measured evidence unexpectedly present: {name}")
        rows.append({"case":name,"replay":result,"measured_evidence":None,
                     "records":len(detail["records"])})
    (root/"separate_process_replay.json").write_text(json.dumps(rows,indent=2,sort_keys=True,default=str)+"\n")
    return rows

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: verify_archive.py CAMPAIGN_DIRECTORY")
    print(json.dumps({"verified_cases":len(verify(sys.argv[1]))}))
