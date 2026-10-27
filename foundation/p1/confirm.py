"""P1 preregistered confirmatory execution; immutable per-arm records.

Requires CONFIRMATORY_CONFIG_FROZEN.json committed BEFORE this script runs.
Do not use pilot seeds or retune analysis reference after observing outcomes.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from material_core.p1_comparator import execute, compare, score_saved
from foundation.p1.analysis import (
    analyze, paired_bootstrap, feasible_hypervolume, prefix_for_cpu)

HERE=Path(__file__).resolve().parent
CONFIG=HERE/"CONFIRMATORY_CONFIG_FROZEN.json"
OUT=HERE/"confirmatory-evidence"

def digest(blob):
    return hashlib.sha256(blob).hexdigest()

def write_atomic(path, obj):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".pending")
    if tmp.exists():
        raise FileExistsError("Unsafe preexisting partial checkpoint")
    tmp.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n")
    os.replace(tmp,path)

def run():
    raw=CONFIG.read_bytes()
    cfg=json.loads(raw)
    if cfg["protocol_version"]!="p1-confirmatory-v1":
        raise ValueError("Unsupported frozen protocol")
    if tuple(cfg["reference"])!=(120000,45,1000000000):
        raise ValueError("Analysis reference changed after freeze")
    if (cfg["seed_start"],cfg["seed_end_inclusive"],cfg["budget_proposals"])!=(2001,2020,4):
        raise ValueError("Unreviewed confirmatory seed or budget change")
    assert set(cfg["methods"])=={"sampling","explore"}
    assert set(cfg["feeds"])=={0.25,0.5}
    output=OUT
    output.mkdir(parents=True,exist_ok=True)
    trials=[]
    for method in cfg["methods"]:
        for feed in cfg["feeds"]:
            for seed in range(cfg["seed_start"],cfg["seed_end_inclusive"]+1):
                paths={}
                scores={}
                held={}
                data={}
                for enabled in (False,True):
                    arm="feedback" if enabled else "blind"
                    path=output/f"{method}-feed{str(feed).replace('.','p')}-seed{seed}-{arm}.json"
                    if not path.exists():
                        execute(seed=seed,budget=cfg["budget_proposals"],
                            feedback=enabled,output=path,elements=cfg["elements"],
                            mass_limit=cfg["mass_limit"],layer=cfg["layer"],
                            feed=feed,route=cfg["route"],method=method)
                    item=json.loads(path.read_text())
                    expected=dict(seed=seed,budget=cfg["budget_proposals"],
                                  feedback=enabled,elements=cfg["elements"],
                                  mass_limit=cfg["mass_limit"],method=method,
                                  feed=feed,layer=cfg["layer"],route=cfg["route"])
                    if any(item["config"].get(k)!=v for k,v in expected.items()):
                        raise ValueError("Incompatible saved experiment: "+str(path))
                    paths[arm]=path
                    data[arm]=item
                    scores[arm]=score_saved(path)
                    opposite=0.5 if feed==0.25 else 0.25
                    held[arm]=score_saved(path,heldout_feed=opposite)
                parity=compare(paths["blind"],paths["feedback"])
                if not parity["matched_numerical_work"]:
                    raise ValueError("Equal numerical-work budget violated")
                from foundation.p1.analysis import summarize_pair
                summary=summarize_pair(data["blind"],data["feedback"],
                    scores["blind"],scores["feedback"],
                    cpu_limit_ns=cfg["cpu_budget_ns"])
                robustness=dict(
                    control_hv=feasible_hypervolume(held["blind"]["results"]),
                    feedback_hv=feasible_hypervolume(held["feedback"]["results"]))
                for key in ("blind","feedback"):
                    path=output/(paths[key].stem+"-final-score.json")
                    # Scores live in separate durable artifacts, not editable search rows.
                    if not path.exists():
                        write_atomic(path,dict(native=scores[key],heldout=held[key]))
                    elif json.loads(path.read_text())!=dict(native=scores[key],heldout=held[key]):
                        raise ValueError("Existing independent scoring differs")
                trial=dict(method=method,feed=feed,seed=seed,summary=summary,
                           robustness=robustness,parity=parity,
                           arm_files={k:p.name for k,p in paths.items()})
                trials.append(trial)
                marker=output/f"pair-{method}-{str(feed).replace('.','p')}-{seed}.json"
                if marker.exists():
                    if json.loads(marker.read_text())!=trial:
                        raise ValueError("Immutable paired trial mismatch")
                else:
                    write_atomic(marker,trial)
    if len(trials)!=80:
        raise RuntimeError("Confirmatory grid is incomplete")
    results=analyze(trials)
    pooled=[t["summary"]["numerical_work"]["feedback_hv"]-
            t["summary"]["numerical_work"]["control_hv"] for t in trials]
    cpu=[t["summary"]["cpu_work"]["feedback_hv"]-
         t["summary"]["cpu_work"]["control_hv"] for t in trials]
    feasible=[int(t["summary"]["numerical_work"]["feedback_feasible"])-
              int(t["summary"]["numerical_work"]["control_feasible"])
              for t in trials]
    # Stratified paired bootstrap: each of the four strata contributes 20 samples.
    import random
    rng=random.Random(cfg["bootstrap_seed"])
    strata=[[t for t in trials if t["method"]==method and t["feed"]==feed]
            for method in cfg["methods"] for feed in cfg["feeds"]]
    draws=[]
    for _ in range(cfg["bootstrap_repetitions"]):
        sample=[]
        for group in strata:
            sample.extend(group[rng.randrange(len(group))] for _ in group)
        draws.append(sum(t["summary"]["numerical_work"]["feedback_hv"]-
                         t["summary"]["numerical_work"]["control_hv"]
                         for t in sample)/len(sample))
    draws.sort()
    primary=dict(n_pairs=80,mean=sum(pooled)/80,
                 ci95=[draws[int(.025*(len(draws)-1))],
                       draws[int(.975*(len(draws)-1))]])
    curves={}
    for group in strata:
        label=f"{group[0]['method']}/feed-{group[0]['feed']}"
        lines=[]
        for n in range(1,cfg["budget_proposals"]+1):
            effects=[]
            for t in group:
                a=json.loads((output/t["arm_files"]["blind"].replace(".json","-final-score.json")).read_text())["native"]["results"]
                b=json.loads((output/t["arm_files"]["feedback"].replace(".json","-final-score.json")).read_text())["native"]["results"]
                effects.append(feasible_hypervolume(b[:n])-feasible_hypervolume(a[:n]))
            lines.append(dict(budget_proposals=n,mean_paired_hv=sum(effects)/len(effects)))
        curves[label]=lines
    summary=dict(protocol_sha256=digest(raw),protocol_version=cfg["protocol_version"],
                 confirmatory_n_pairs=80,primary=primary,
                 cpu_paired_hv=paired_bootstrap(cpu), feasibility_paired=paired_bootstrap(feasible),
                 per_scenario=results, performance_curves=curves,
                 heldout_by_scenario={str((m,f)):paired_bootstrap(
                     [t["robustness"]["feedback_hv"]-t["robustness"]["control_hv"]
                      for t in trials if t["method"]==m and t["feed"]==f])
                      for m in cfg["methods"] for f in cfg["feeds"]},
                 physical_validation=False,
                 search_and_scorer_model_independence=False,
                 caveat="Synthetic in-model finding, not measured ceramic evidence")
    write_atomic(output/"confirmatory_summary.json",summary)
    write_atomic(output/"all_paired_trials.json",trials)
    with (output/"numeric_curve_data.csv").open("x",newline="") as fh:
        w=csv.writer(fh)
        w.writerow(("stratum","proposal_budget","mean_paired_hv"))
        for key,values in curves.items():
            for row in values:
                w.writerow((key,row["budget_proposals"],row["mean_paired_hv"]))
    versions=dict(python=sys.version,system=platform.platform(),
                  git_checkout=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                  git_parents=subprocess.check_output(["git","show","-s","--format=%P","HEAD"],text=True).strip(),
                  github_sha=os.environ.get("GITHUB_SHA"),
                  protocol_sha256=digest(raw))
    write_atomic(output/"environment_and_source.json",versions)
    manifest=output/"sha256_manifest.txt"
    manifest.write_text("".join(digest(p.read_bytes())+"  "+p.name+"\n" for p in sorted(output.iterdir())
                    if p.is_file() and p.name!="sha256_manifest.txt"))
    print(json.dumps({"P1_STATUS":"CONFIRMATORY_EXECUTED_UNREVIEWED",
                      "n_pairs":80,"primary":primary,
                      "feasible_difference":summary["feasibility_paired"],
                      "cpu_difference":summary["cpu_paired_hv"],
                      "artifact_count":len(list(output.iterdir())),
                      "source":versions["git_checkout"]},sort_keys=True))
if __name__=="__main__":
    run()
