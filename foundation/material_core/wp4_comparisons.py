"""Fixed, non-selective WP4 resolution sensitivity and paired comparison."""
from __future__ import annotations
from .wp4_feedback import run

PREREGISTERED=((0.01,0.25),(0.005,0.25),(0.0025,0.25),
               (0.005,0.5),(0.005,0.125))

def paired(*,elements=4096,mass_limit=31.,layer=.005,feed=.25,budget=4):
    on=run(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,budget=budget,feedback=True)
    off=run(elements=elements,mass_limit=mass_limit,layer=layer,feed=feed,budget=budget,feedback=False)
    assert on["records"][0]["intended_hash"]==off["records"][0]["intended_hash"]
    assert on["process"]==off["process"]
    return dict(common_budget=budget,feedback_on=on,feedback_off=off,
        # An early stop is not an equal number of numerical evaluations.
        budget_policy="same maximum evaluation slots; unused slots reported, not charged",
        unused_on=budget-on["proposals"],unused_off=budget-off["proposals"])

def sensitivity(*,elements=4096,mass_limit=31.,budget=4):
    records=[]
    for layer,feed in PREREGISTERED:
        result=run(elements=elements,mass_limit=mass_limit,
            layer=layer,feed=feed,budget=budget,feedback=True)
        records.append(dict(layer_m=layer,feed_step=feed,
            stop_reason=result["stop_reason"],evaluations=result["evaluations"],
            transforms=result["transforms"],selected=next((
                row["intended_hash"] for row in result["records"] if row["feasible"]),None),
            objective_vectors=[row["objectives"] for row in result["records"]],
            qualified=[row["numerical_quality"] for row in result["records"]],
            violations=[row["feedback"] for row in result["records"]]))
    return dict(preregistered_grid=[list(x) for x in PREREGISTERED],records=records,
        selection_rule="first numerically qualified, conditionally scenario-feasible candidate; otherwise none")
