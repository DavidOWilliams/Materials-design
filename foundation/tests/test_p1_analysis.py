"""P1 statistical analysis edge-case checks."""
from foundation.p1.analysis import feasible_hypervolume, paired_bootstrap, prefix_for_cpu

def r(x,y,z,feasible=True):
    return dict(feasible=feasible,achieved_objectives=dict(
        thermal_transmission=x,areal_mass=y,tensile_thermal_mismatch=z))

def test_empty_or_missing_feasible_hv_zero():
    assert feasible_hypervolume([])==0
    assert feasible_hypervolume([r(50000,20,1e7,False)])==0
    assert feasible_hypervolume([r(None,20,1e7)])==0

def test_union_hv_monotonic_and_exact_single_box():
    point=r(60000,22.5,5e8)
    assert feasible_hypervolume([point])==0.125
    assert feasible_hypervolume([point,point])==0.125
    assert feasible_hypervolume([point,r(30000,30,2e8)])>=0.125

def test_bootstrap_empty_constant_and_deterministic():
    assert paired_bootstrap([])["mean"] is None
    assert paired_bootstrap([0]*20)["ci95"]==[0,0]
    assert paired_bootstrap([-1,0,1])==paired_bootstrap([-1,0,1])

def test_cpu_prefix_never_includes_overspend():
    rec={"rows":[dict(proposal_cpu_ns=5,manufacturing_cpu_ns=6,
                      numerical_cpu_ns=7,feedback_cpu_ns=2)]*3}
    assert prefix_for_cpu(rec,39)==1
    assert prefix_for_cpu(rec,40)==2
    assert prefix_for_cpu(rec,0)==0
