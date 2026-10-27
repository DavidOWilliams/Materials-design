"""P1-IR-05 exploratory CPU metrology, NOT a confirmatory redesign."""
import json, platform, statistics, sys, tempfile, time
from pathlib import Path
from material_core.p1_comparator import execute
from analysis import prefix_for_cpu

def run():
    rows=[]
    with tempfile.TemporaryDirectory() as d:
        for repeat in range(8):
            for feedback in (False,True):
                path=Path(d)/f"repeat{repeat}-feedback{int(feedback)}.json"
                start=time.perf_counter_ns()
                result=execute(seed=41,budget=4,feedback=feedback,
                               output=path,elements=32,feed=0.25)
                wall=time.perf_counter_ns()-start
                account=result["accounting"]
                cpu=sum(account[k] for k in (
                    "proposal_cpu_ns","manufacturing_cpu_ns","numerical_cpu_ns","feedback_cpu_ns"))
                assert cpu==sum(sum(r[k] for k in (
                    "proposal_cpu_ns","manufacturing_cpu_ns","numerical_cpu_ns","feedback_cpu_ns"))
                    for r in result["rows"])
                rows.append(dict(repeat=repeat,feedback=feedback,
                     cpu_ns=cpu, wall_ns=wall,
                     cpu_to_wall_ratio=cpu/wall if wall else None,
                     prefix_60ms=prefix_for_cpu(result,60_000_000),
                     prefix_80ms=prefix_for_cpu(result,80_000_000),
                     prefix_100ms=prefix_for_cpu(result,100_000_000),
                     warmup=(repeat==0), cache_hits=account["cache_hits"]))
    stats={}
    for treatment in (False,True):
        sub=[r for r in rows if r["feedback"]==treatment and not r["warmup"]]
        stats[str(treatment)]=dict(
            cpu_mean_ms=statistics.mean(r["cpu_ns"] for r in sub)/1e6,
            cpu_stdev_ms=statistics.stdev(r["cpu_ns"] for r in sub)/1e6,
            cpu_min_ms=min(r["cpu_ns"] for r in sub)/1e6,
            cpu_max_ms=max(r["cpu_ns"] for r in sub)/1e6,
            cutoff_slots_60ms=[r["prefix_60ms"] for r in sub],
            cutoff_slots_80ms=[r["prefix_80ms"] for r in sub],
            cutoff_slots_100ms=[r["prefix_100ms"] for r in sub])
    out=dict(status="EXPLORATORY_CPU_METROLOGY",not_confirmatory=True,
        python=sys.version,platform=platform.platform(),
        clock="process_time_ns per computation component",
        independent_wall_clock="perf_counter_ns around complete call",
        limitation="File writing and process startup are outside per-candidate CPU ledger; "
                   "elapsed wall time is not a matched CPU search budget",
        repeats=rows,summary=stats)
    dest=Path("foundation/p1/correction-evidence/cpu_benchmark.json")
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"cpu_summary":stats},sort_keys=True))
if __name__=="__main__":
    run()
