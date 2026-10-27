"""Render audit-readable P1 report and budget curves from frozen raw evidence."""
import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

def fmt(value):
    if value is None:
        return "Not estimated"
    return f"{value:+.6f}" if isinstance(value,(int,float)) else str(value)

def effect(row):
    return f'{fmt(row["mean"])} (95% paired CI {fmt(row["ci95"][0])} to {fmt(row["ci95"][1])}; n={row["n"]})'

def make_report(root, output):
    root=Path(root)
    summary=json.loads((root/"confirmatory_summary.json").read_text())
    env=json.loads((root/"environment_and_source.json").read_text())
    trials=json.loads((root/"all_paired_trials.json").read_text())
    if len(trials)!=80 or summary["confirmatory_n_pairs"]!=80:
        raise ValueError("Cannot report incomplete confirmation")
    lines=[
        "# P1 scientific evaluation — confirmatory synthetic in-model study",
        "",
        "**Status:** executed and software-verified; **independent Gate 3 review pending**.",
        f'**Exact tested checkout SHA:** `{env["git_checkout"]}`.',
        f'**Frozen protocol SHA256:** `{env["protocol_sha256"]}`.',
        "",
        "## Executive summary",
        "",
        "Primary question: Does WP4's bounded density-guided areal-mass correction improve numerically qualified synthetic estimated achieved-state performance when WP3 proposal opportunities and numerical work are matched?",
        "",
        f'Across 80 paired trials, normalized feasible three-objective HV difference (feedback minus blind) was {effect(summary["primary"])}.',
        f'At the preregistered 80 ms search CPU threshold, paired HV difference was {effect(summary["cpu_paired_hv"])}.',
        f'Trial-level feasibility difference was {effect(summary["feasibility_paired"])}.',
        "The prespecified practical HV threshold was 0.02; assess statistical uncertainty and engineering materiality separately.",
        "These are entirely synthetic results. No improved real manufactured ceramic performance is established.",
        "",
        "## Frozen design and fairness",
        "",
        "WP3 seeded sampling or structured exploration, two supported WP4 feed resolutions (0.25, 0.50), four proposal slots per arm, 20 paired seeds (2001–2020) per stratum, 80 pairs total. Each arm applies the same WP4 ideal process transform and WP2 numerical evaluator. Feedback-on additionally permits WP4's previous-violation density-guided revision; blind does not use achieved-state information to select future designs.",
        "No additional optimisers were introduced. The exploration policy is a different proposal schedule, not a distinct inverse-optimisation algorithm. Cache hits are disabled for both arms. Separate final scoring costs are excluded from optimisation budgets.",
        "",
        "## Computational budget and metric definitions",
        "",
        "Matched numerical work means equal attempted proposal slots, WP4 transformations and WP2 evaluations. CPU-prefix results use measured generation, transformation, numerical and feedback calculation CPU time. Revision cost is included in proposal generation. The 80 ms threshold and all trial seeds were frozen before confirmation.",
        "Three minimized objectives: thermal transmission W/m², areal mass kg/m², tensile thermal mismatch Pa. Fixed normalized hypervolume reference: 120000 W/m², 45 kg/m², 1e9 Pa. No-feasible designs contribute zero HV; infeasible attempts remain in the denominator.",
        "",
        "## Full stratum-level paired results",
        "",
        "| Scenario (proposal / feed) | Equal-work HV effect (95% CI) | CPU-budget HV effect (95% CI) | Feasible-rate difference (95% CI) | Held-out feed HV effect (95% CI) |",
        "|---|---|---|---|---|",
    ]
    for label,row in sorted(summary["per_scenario"].items()):
        import ast
        method,feed=ast.literal_eval(label)
        held=summary["heldout_by_scenario"][str((method,feed))]
        lines.append(f'| {method} / {feed} | {effect(row["paired_hv"])} | {effect(row["paired_cpu_hv"])} | {effect(row["paired_feasibility"])} | {effect(held)} |')
    lines+=["",
        "## Raw outcomes and sensitivity",
        "",
        "The attached all_paired_trials.json provides every paired objective vector, feasibility outcome, budget audit, seed, method and process scenario without outcome selection. Raw arm records, complete common-scorer output, per-candidate CPU ledgers, dependencies, source identity, curves and SHA256 manifest are retained in the same evidence directory.",
        "Held-out rescoring switches 0.25 and 0.50 feed resolutions only after design selection. It checks sensitivity to another assumption within the SAME synthetic WP4 process family; it is not an independent empirical validation model.",
        "",
        "## Interpretation and threats to validity",
        "",
        "1. Software correctness is supported by focused tests, replay and full regression; this does not qualify physical ceramics.",
        "2. Numerical eligibility is established only where WP2 reports qualified mesh/constraints; mesh 32 can leave objectives unresolved.",
        "3. The correction targets an achieved areal-mass violation specifically and is not a multiobjective adaptive optimiser.",
        "4. CPU comparisons are runner- and execution-condition-dependent and are not matched wall-clock, distributed or GPU budgets.",
        "5. Synthetic achieved-state and holdout feeds share idealized physics, so superiority in this environment cannot establish physical or generalised superiority.",
        "6. Only two supported feed resolutions and four-proposal budgets were studied; a true identity-process negative control is unavailable for arbitrary WP3 architectures.",
        "7. These confidence intervals are descriptive and have not undergone separate independent statistical review; no unadjusted scenario-level multiplicity claims are made.",
        "",
        "## Roadmap implications",
        "",
        "P2 should challenge numerical quality and independent objective modelling using external published benchmarks without introducing unqualified physics. P3 should obtain independently measured ceramic command-to-achieved-state data and validate the process model out of sample. Only after those checks could feedback benefits be evaluated as manufactured performance rather than synthetic consistency.",
        "",
        "## Independent Gate 3 reviewer tasks",
        "",
        "Check frozen protocol precedes confirmation; inspect exact tested SHA and full CI raw log; rerun focused and foundation regression; independently recompute saved arms and objective metrics; verify paired seeds/candidate opportunities/cache policy/CPU accounting; recompute the 3D hypervolume and bootstrap estimates; test failure/no-feasible/identity-limit controls; assess scientific interpretation and heldout dependence; verify every SHA256 manifest entry.",
        "**Gate 3 is NOT self-approved. WP6 Gate 2 remains OPEN and formal acceptance withheld.**",
        ""]
    Path(output).write_text("\n".join(lines))
    # SVG curves: one panel per stratum, all data already in machine-readable CSV.
    series=summary["performance_curves"]
    width,height=920,400
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<text x="30" y="25" font-family="sans-serif" font-size="16">P1 mean paired feasible HV gain vs matched proposal budget (synthetic)</text>',
           '<path d="M60 45V340H880" stroke="#444" fill="none"/>']
    values=[v["mean_paired_hv"] for rows in series.values() for v in rows]
    lo=min(0.,min(values));hi=max(0.,max(values))
    if hi==lo:hi=lo+0.01
    palette=["#2060aa","#bb5533","#32885d","#8050aa"]
    for idx,(label,rows) in enumerate(sorted(series.items())):
        coords=[]
        for row in rows:
            x=60+(row["budget_proposals"]-1)*230
            y=340-(row["mean_paired_hv"]-lo)/(hi-lo)*265
            coords.append(f"{x:.2f},{y:.2f}")
        parts.append(f'<polyline points="{" ".join(coords)}" stroke="{palette[idx]}" stroke-width="3" fill="none"/>')
        parts.append(f'<text x="600" y="{65+idx*23}" font-family="sans-serif" font-size="12" fill="{palette[idx]}">{escape(label)}</text>')
    parts.append('</svg>')
    (root/"performance_curves.svg").write_text("\n".join(parts))
    print(json.dumps({"report":str(output),"cases":len(trials),
                      "source":env["git_checkout"]},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--evidence",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    make_report(a.evidence,a.output)
