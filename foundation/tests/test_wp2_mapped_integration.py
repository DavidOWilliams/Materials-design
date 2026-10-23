"""WP2 mapped synthetic integration, domain and immutable replay checks."""
import json
import math
import subprocess
import sys

import pytest
from material_core.contracts import RunInputs, quantity
from material_core.store import RunStore
from material_core.wp2_numerical import (
    compatible_comparison, evaluate, property_pack_hash, comparison_context_hash,
)
from material_core.wp2_scenarios import make_wp2_fixture, make_wp2_achieved_fixture


@pytest.mark.parametrize('arch',('homogeneous','layered','gradient'))
def test_three_objectives_equal_budget_and_store(tmp_path,arch):
    x=make_wp2_fixture(arch)
    y=evaluate(x)
    assert y.status=='complete'
    assert y.evidence_status=='synthetic'
    assert y.feasibility=='conditional'
    assert [m.objective_id for m in y.metrics]==[
        'thermal_transmission','areal_mass','tensile_thermal_mismatch']
    assert all(m.status=='computed' for m in y.metrics)
    assert y.metrics[1].value.value==pytest.approx(30.,abs=1e-8)
    assert y.comparison_eligible(x.brief)
    assert y.spatial_fields is not None
    assert len(y.spatial_fields.coordinate_from_hot_m)>=128
    assert len(y.spatial_fields.signed_equibiaxial_stress_Pa)==len(y.spatial_fields.temperature_K)
    assert y.spatial_fields.signed_hot_to_cold_flux.value>0
    store=RunStore(tmp_path)
    run_id=store.create(x);store.finish(run_id,y)
    reread=RunStore(tmp_path).load(run_id)
    assert reread.evaluation==y
    assert reread.evaluation.content_hash==y.content_hash


def test_independent_thermal_reference_and_layer_interface():
    h=evaluate(make_wp2_fixture('homogeneous'))
    l=evaluate(make_wp2_fixture('layered'))
    g=evaluate(make_wp2_fixture('gradient'))
    # Arithmetic conductivity upper bound locally, series resistance globally.
    assert h.metrics[0].value.value==pytest.approx(60000.,rel=1e-10)
    assert l.metrics[0].value.value==pytest.approx(100/(.005/2+.005/10),rel=1e-10)
    assert g.metrics[0].value.value==pytest.approx(800/.01/math.log(5),rel=1e-4)
    assert compatible_comparison(h,l) and compatible_comparison(l,g)
    assert h.metrics[1].value.value==pytest.approx(l.metrics[1].value.value)
    assert l.metrics[1].value.value==pytest.approx(g.metrics[1].value.value)


def test_gradients_refinement_preserves_material_budget_and_flux():
    cases=[evaluate(make_wp2_fixture('gradient',elements=n))
           for n in (32,64,128,256)]
    exact=800/.01/math.log(5)
    errors=[abs(c.metrics[0].value.value-exact) for c in cases]
    assert all(a>b for a,b in zip(errors,errors[1:]))
    assert errors[-1]/exact<1e-5
    assert all(abs(c.metrics[1].value.value-30.)<1e-9 for c in cases)


def test_free_layer_equilibrium_and_positive_tensile_stress():
    y=evaluate(make_wp2_fixture('layered'))
    f=y.spatial_fields
    assert abs(f.force_residual.value)<1
    assert abs(f.moment_residual.value)<.01
    assert y.metrics[2].value.value>0
    assert f.curvature_per_m!=0


def test_constraint_violation_independent_of_numerical_success(tmp_path):
    x=make_wp2_fixture('layered',mass_limit=29.)
    y=evaluate(x)
    assert y.status=='complete' and y.feasibility=='infeasible'
    assert y.constraint_metrics[0].value.value==pytest.approx(30.)
    assert not y.comparison_eligible(x.brief)
    s=RunStore(tmp_path);run=s.create(x);s.finish(run,y)
    assert not s.load(run).evaluation.comparison_eligible(x.brief)


def test_changed_brief_and_mesh_invalidate_scenario_and_context():
    x=make_wp2_fixture('homogeneous')
    z=make_wp2_fixture('homogeneous',elements=64)
    assert x.content_hash!=z.content_hash
    assert evaluate(x).comparison_context_hash!=evaluate(z).comparison_context_hash
    a=make_wp2_fixture('homogeneous',mass_limit=31.)
    b=make_wp2_fixture('homogeneous',mass_limit=32.)
    assert not compatible_comparison(evaluate(a),evaluate(b))
    raw=x.model_dump(mode='json')
    raw['settings']['property_pack_hash']='a'*64
    with pytest.raises(ValueError,match='Property pack hash'):
        evaluate(RunInputs.model_validate_json(json.dumps(raw)))


def test_out_of_domain_property_and_missing_achieved_state():
    x=make_wp2_fixture()
    raw=x.model_dump(mode='json')
    raw['brief']['hot_boundary']['value']=500.
    # Should not silently rewrite the input comparison context.
    with pytest.raises(ValueError,match='Comparison context'):
        evaluate(RunInputs.model_validate_json(json.dumps(raw)))
    raw=x.model_dump(mode='json')
    raw['evaluation_target']='estimated'
    # Explicitly updated context, but no estimated geometry.
    # The WP1 input contract correctly blocks missing achieved states before
    # the numerical adapter is invoked; no intended-state fallback is allowed.
    with pytest.raises(ValueError,match='Estimated target missing'):
        RunInputs.model_validate_json(json.dumps(raw))


def test_mapped_run_separate_process_replay(tmp_path):
    x=make_wp2_fixture('gradient',elements=64)
    y=evaluate(x)
    store=RunStore(tmp_path);run_id=store.create(x);store.finish(run_id,y)
    program="""import sys
from material_core.store import RunStore
from material_core.wp2_numerical import evaluate
r=RunStore(sys.argv[1]).load(sys.argv[2])
got=evaluate(r.inputs)
assert got.content_hash==r.evaluation.content_hash
assert got.comparison_eligible(r.inputs.brief)
print(got.metrics[0].value.value)
"""
    process=subprocess.run([sys.executable,'-c',program,str(tmp_path),run_id],
        capture_output=True,text=True,check=True)
    assert float(process.stdout)>0


def test_supplied_achieved_field_changes_physical_result_and_identity(tmp_path):
    intended=make_wp2_fixture('gradient')
    estimated=make_wp2_achieved_fixture()
    a=evaluate(intended)
    b=evaluate(estimated)
    assert b.status=='complete' and b.evidence_status=='synthetic'
    assert b.feasibility=='infeasible'
    assert b.metrics[1].value.value>a.metrics[1].value.value
    assert b.metrics[0].value.value!=pytest.approx(a.metrics[0].value.value)
    assert not compatible_comparison(a,b)
    assert b.comparison_context_hash!=a.comparison_context_hash
    assert estimated.content_hash!=intended.content_hash
    s=RunStore(tmp_path);rid=s.create(estimated);s.finish(rid,b)
    assert RunStore(tmp_path).load(rid).inputs.estimated_state.geometry==estimated.estimated_state.geometry
    assert RunStore(tmp_path).load(rid).evaluation==b


def test_independent_analytic_bilayer_thermal_bending_reference():
    """Exact continuous through-layer A/B/D integrals (not a second solver call).

    Equal 5 mm layers, Q=100/160 GPa, alpha=5/12 microstrain/K,
    400/300 K, stress-free 300 K. Fourier flux=100000/3 W/m2.
    The analytic free-laminate solution is eps0=703/3540000,
    curvature=-763/17700 1/m. The max tensile stress is
    680000000/59 Pa on the side-A interface, within the idealisation.
    """
    y=evaluate(make_wp2_fixture('layered',elements=512))
    f=y.spatial_fields
    assert f.curvature_per_m==pytest.approx(-763/17700,rel=2e-4)
    assert y.metrics[2].value.value==pytest.approx(680000000/59,rel=.005)
    assert f.force_residual.value==pytest.approx(0.,abs=1)
    assert f.moment_residual.value==pytest.approx(0.,abs=.01)


def test_actual_numeric_mass_constraint_with_mass_not_an_objective(tmp_path):
    x=make_wp2_fixture('layered',mass_limit=31.)
    raw=x.model_dump(mode='json')
    raw['brief']['objectives']=[
        o for o in raw['brief']['objectives'] if o['id']!='areal_mass']
    interim=RunInputs.model_validate_json(json.dumps(raw))
    raw['settings']['evaluation_context_hash']=comparison_context_hash(
        interim.brief,interim.settings,'intended')
    constrained=RunInputs.model_validate_json(json.dumps(raw))
    y=evaluate(constrained)
    assert [m.objective_id for m in y.metrics]==[
        'thermal_transmission','tensile_thermal_mismatch']
    assert y.constraint_metrics[0].metric_id=='areal_mass'
    assert y.constraint_metrics[0].value.value==pytest.approx(30.)
    assert y.comparison_eligible(constrained.brief)
    store=RunStore(tmp_path);run=store.create(constrained);store.finish(run,y)
    assert store.load(run).evaluation.comparison_eligible(constrained.brief)


def test_wp2_open_assumptions_are_immutable_and_historical_versions_retained():
    from material_core.assumptions import validate_snapshot, AssumptionRegistry
    x=make_wp2_fixture()
    records=validate_snapshot([json.loads(s) for s in x.assumption_snapshots])
    by_id={a.assumption_id:a for a in records}
    assert set(f'A{i}' for i in range(16,22)).issubset(by_id)
    assert all(by_id[f'A{i}'].status=='open' and
               by_id[f'A{i}'].value is None for i in range(16,22))
    builtin=AssumptionRegistry.from_builtin()
    for a in ('A01','A06','A07','A12','A14'):
        assert by_id[a].content_hash==builtin.get(a,1).content_hash
