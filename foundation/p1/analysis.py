"""P1 analysis. No fitting on confirmatory outcomes; fixed reference and paired seeds."""
import json
import math
import random
from pathlib import Path

METRICS=("thermal_transmission","areal_mass","tensile_thermal_mismatch")
REFERENCE=(120000.,45.,1_000_000_000.)

def feasible_hypervolume(items, reference=REFERENCE):
    """Exact union of 3D axis-aligned dominance cuboids, normalized [0,1].

    Missing/out-of-reference objective vectors contribute no volume.
    Numerical qualification and feasibility are supplied by common scorer.
    """
    points=[]
    for row in items:
        if not row["feasible"]:
            continue
        raw=[row["achieved_objectives"].get(k) for k in METRICS]
        if any(type(v) not in (int,float) or not math.isfinite(v)
               for v in raw):
            continue
        p=tuple(float(v)/r for v,r in zip(raw,reference))
        if any(v<0 or v>=1 for v in p):
            continue
        points.append(p)
    if not points:
        return 0.
    xvalues=sorted({p[0] for p in points}|{1.})
    volume=0.
    for x0,x1 in zip(xvalues,xvalues[1:]):
        active=[(p[1],p[2]) for p in points if p[0]<=x0]
        if not active:
            continue
        yvalues=sorted({p[0] for p in active}|{1.})
        area=0.
        for y0,y1 in zip(yvalues,yvalues[1:]):
            z=min((z for y,z in active if y<=y0),default=1.)
            area+=(y1-y0)*(1.-z)
        volume+=(x1-x0)*area
    return max(0., min(1.,volume))

def prefix_for_cpu(record, cpu_ns):
    used=0
    n=0
    for row in record["rows"]:
        cost=sum(row[k] for k in (
            "proposal_cpu_ns","manufacturing_cpu_ns","numerical_cpu_ns",
            "feedback_cpu_ns"))
        if used+cost > cpu_ns:
            break
        used+=cost
        n+=1
    return n

def paired_bootstrap(differences, *, repetitions=2000, seed=8846):
    n=len(differences)
    if not n:
        return dict(n=0,mean=None,ci95=[None,None])
    rng=random.Random(seed)
    samples=[]
    for _ in range(repetitions):
        samples.append(sum(differences[rng.randrange(n)] for _ in range(n))/n)
    samples.sort()
    return dict(n=n,mean=sum(differences)/n,
                ci95=[samples[int(.025*(repetitions-1))],
                      samples[int(.975*(repetitions-1))]])

def summarize_pair(control, intervention, a_scores, b_scores, *,
                   cpu_limit_ns=80_000_000):
    ac,bc=control["accounting"],intervention["accounting"]
    if (ac["proposals"]!=bc["proposals"] or
        ac["numerical_evaluations"]!=bc["numerical_evaluations"] or
        ac["manufacturing_transformations"]!=bc["manufacturing_transformations"]):
        raise ValueError("Unequal numerical-work trial cannot enter paired analysis")
    an=prefix_for_cpu(control,cpu_limit_ns)
    bn=prefix_for_cpu(intervention,cpu_limit_ns)
    return dict(
        numerical_work=dict(control_hv=feasible_hypervolume(a_scores["results"]),
                            feedback_hv=feasible_hypervolume(b_scores["results"]),
                            control_feasible=any(r["feasible"] for r in a_scores["results"]),
                            feedback_feasible=any(r["feasible"] for r in b_scores["results"])),
        cpu_work=dict(control_slots=an,feedback_slots=bn,
                      control_hv=feasible_hypervolume(a_scores["results"][:an]),
                      feedback_hv=feasible_hypervolume(b_scores["results"][:bn])),
        objective_vectors=dict(control=[r["achieved_objectives"]
                                         for r in a_scores["results"] if r["feasible"]],
                               feedback=[r["achieved_objectives"]
                                         for r in b_scores["results"] if r["feasible"]]),
        reference=list(REFERENCE))

def analyze(trials):
    """Trials are already paired by condition and seed, never selected by effect."""
    groups={}
    for row in trials:
        key=(row["method"],row["feed"])
        groups.setdefault(key,[]).append(row)
    output={}
    for key,pairs in sorted(groups.items()):
        diffs=[p["summary"]["numerical_work"]["feedback_hv"]-
               p["summary"]["numerical_work"]["control_hv"] for p in pairs]
        cpu=[p["summary"]["cpu_work"]["feedback_hv"]-
             p["summary"]["cpu_work"]["control_hv"] for p in pairs]
        feasibility=[int(p["summary"]["numerical_work"]["feedback_feasible"])-
                     int(p["summary"]["numerical_work"]["control_feasible"])
                     for p in pairs]
        output[str(key)]=dict(
            paired_hv=paired_bootstrap(diffs),
            paired_cpu_hv=paired_bootstrap(cpu),
            paired_feasibility=paired_bootstrap(feasibility),
            all_paired_hv_differences=diffs,
            all_paired_cpu_differences=cpu,
            all_paired_feasibility_differences=feasibility)
    return output
