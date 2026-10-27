"""EXPLORATORY P1 pilot only. Never pool with frozen confirmatory trials."""
from pathlib import Path
from material_core.p1_comparator import execute, compare
import json, os, hashlib, platform, sys

def main():
    root=Path("foundation/p1/pilot-evidence")
    root.mkdir(parents=True,exist_ok=True)
    records=[]
    for method in ("sampling","explore"):
        for feed in (0.25,0.5):
            for seed in (101, 102, 103, 104):
                pair=[]
                for feedback in (False,True):
                    name=f"{method}-feed{str(feed).replace('.','p')}-seed{seed}-{'on' if feedback else 'off'}.json"
                    path=root/name
                    r=execute(seed=seed,budget=4,feedback=feedback,output=path,elements=32,
                              mass_limit=31.0,feed=feed,method=method)
                    pair.append(path)
                    records.append(dict(method=method,feed=feed,seed=seed,feedback=feedback,
                                        statuses=[x["status"] for x in r["rows"]],
                                        qualified=sum(x.get("qualified") is True for x in r["rows"]),
                                        achieved_feasible=sum(x.get("qualified") is True and
                                            x.get("feasibility")=="conditional" and
                                            x.get("manufacturing_feasibility")=="conditional"
                                            for x in r["rows"]),
                                        cpu_ns=sum(v for k,v in r["accounting"].items() if k.endswith("_cpu_ns")),
                                        revision_count=sum(x.get("revision_applied",False) for x in r["rows"]),
                                        file=name))
                audit=compare(*pair)
                if not audit["matched_numerical_work"]:
                    raise AssertionError("Pilot equal-work violation")
    (root/"pilot_summary.json").write_text(json.dumps(records,indent=2,sort_keys=True)+"\n")
    meta=dict(experiment_status="PILOT_NOT_CONFIRMATORY",python=sys.version,platform=platform.platform(),
              github_sha=os.environ.get("GITHUB_SHA"),trial_count=len(records))
    (root/"provenance.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
    files=sorted(p for p in root.iterdir() if p.is_file())
    (root/"sha256_manifest.txt").write_text("".join(
        hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name+"\n" for p in files))
    print(json.dumps({"status":"PILOT_ONLY","trials":len(records),"output":str(root)}))

if __name__=="__main__":
    main()
