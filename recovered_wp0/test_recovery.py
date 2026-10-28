"""Fresh reference checks; test counts are not the lost original suite."""
from dataclasses import FrozenInstanceError, asdict
import json
import math
from pathlib import Path
import subprocess
import sys
import zipfile

import numpy as np
import pytest
from recovered_wp0.thermal import ThermalDesign, dominates, evaluate, fixtures, from_legacy, input_hash
from recovered_wp0.laminate import stress, compatible_strain


@pytest.mark.parametrize('design', fixtures())
def test_thermal_reference_bounds_conservation(design):
    r = evaluate(design)
    assert r['relative_error'] < 3e-5
    assert r['flux_spread_W_m2'] < 1e-5
    assert min(r['temperature_K']) >= 300-1e-9
    assert max(r['temperature_K']) <= 400+1e-9
    assert r['temperature_K'][0] == 400 and r['temperature_K'][-1] == 300


def test_gradient_convergence():
    errors=[evaluate(fixtures()[2], n)['relative_error'] for n in (8,16,32,64,128)]
    assert all(a/b > 3 for a,b in zip(errors,errors[1:]))


@pytest.mark.parametrize('design', fixtures())
def test_bridge_same_backend(design):
    assert evaluate(from_legacy({'wp0_thermal_fixture':asdict(design)})) == evaluate(design)


@pytest.mark.parametrize('change', [{'units':'mm'}, {'length_m':0}, {'hot_K':float('nan')},
    {'conductivity_W_mK':[2,10]}, {'architecture':'coating'}, {'cold_K':float('inf')}])
def test_contract_rejects(change):
    data=asdict(fixtures()[0]); data.update(change)
    with pytest.raises(ValueError): ThermalDesign(**data)


def test_missing_legacy_fields():
    with pytest.raises(KeyError): from_legacy({'name':'ceramic','score':95})
    with pytest.raises(TypeError): from_legacy({'wp0_thermal_fixture': {'architecture':'graded'}})


def test_immutable_copy_and_hash():
    values=[2.]
    d=ThermalDesign('homogeneous',.01,400.,300.,values,'SI')
    values[0]=10
    assert d.conductivity_W_mK == (2.,)
    with pytest.raises(FrozenInstanceError): d.length_m=.02
    assert input_hash(d,64) != input_hash(d,128)
    assert input_hash(d,128) != input_hash(fixtures()[1],128)


@pytest.mark.parametrize('n',[0,3,2.5,True])
def test_mesh_guard(n):
    with pytest.raises(ValueError): evaluate(fixtures()[0],n)


def test_equal_boundaries_and_constant_gradient():
    r=evaluate(ThermalDesign('graded',.01,300.,300.,(2.,2.),'SI'))
    assert abs(r['flux_W_m2']) < 1e-6
    assert r['relative_error'] is None
    r=evaluate(ThermalDesign('graded',.01,400.,300.,(2.,2.),'SI'))
    assert math.isclose(r['flux_W_m2'],20000,rel_tol=1e-10)


def test_objective_completeness_and_tradeoffs():
    with pytest.raises(ValueError): dominates({'q':1},{'q':2,'mass':3},{'q':'min','mass':'min'})
    with pytest.raises(ValueError): dominates({'q':float('nan')},{'q':2},{'q':'min'})
    assert dominates({'q':1,'m':2},{'q':2,'m':2},{'q':'min','m':'min'})
    assert not dominates({'q':1,'m':3},{'q':2,'m':2},{'q':'min','m':'min'})


@pytest.mark.parametrize('a,b',[(549e-6,526e-6),(526e-6,549e-6),(1.,1.),(4.,1.)])
def test_laminate_equilibrium_independent(a,b):
    s=stress(a,b); f=s['B4C_fraction']; independent=compatible_strain(a,b)
    assert abs(f*s['B4C_stress_Pa']+(1-f)*s['SiC_stress_Pa']) < 1e-5
    np.testing.assert_allclose([s['B4C_stress_Pa'],s['SiC_stress_Pa']],independent,rtol=1e-12)


def test_laminate_discrepancy_and_tradeoff():
    literal=stress(549,526); reversed_=stress(526,549)
    assert round(literal['B4C_stress_Pa']/1e9,2) == -1.05
    assert round(reversed_['B4C_stress_Pa']/1e9,2) == -1.11
    assert round(reversed_['SiC_stress_Pa']/1e9,2) == 1.42
    base=stress(1,1); revised=stress(4,1)
    reduction=1-revised['B4C_stress_Pa']/base['B4C_stress_Pa']
    increase=revised['SiC_stress_Pa']/base['SiC_stress_Pa']-1
    assert .647 < reduction < .649 and .408 < increase < .410


def test_laminate_scale_and_invalid():
    assert stress(1,1)==stress(.001,.001)
    assert math.isclose(stress(1,1,962.5)['B4C_stress_Pa']*2,stress(1,1)['B4C_stress_Pa'])
    for x in (0,-1,float('nan'),float('inf')):
        with pytest.raises(ValueError): stress(x,1)


def test_recovered_ceramic_replays_exactly():
    root=Path(__file__).parent/'ceramic'
    expected=(root/'ceramic_evaluation.json').read_bytes()
    subprocess.run([sys.executable,str(root/'evaluate_ceramic.py')],check=True,capture_output=True)
    assert (root/'ceramic_evaluation.json').read_bytes()==expected
    data=json.loads(expected)
    assert not data['milestone_gate']['passed']
    assert data['designs']['type3']['mean_curling_deg'] is None
