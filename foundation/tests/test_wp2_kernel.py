"""Independent analytical checks for the bounded WP2 numerical kernel."""
from math import isclose
import pytest
from material_core.wp2_kernel import Cell,evaluate_cells


def material(thickness=.01,k=2.,rho=2000.,Q=120e9,alpha=8e-6):
    return Cell(thickness,k,rho,Q,alpha)


def test_homogeneous_steady_slab_and_mass():
    v=evaluate_cells((material(),),400.,300.,300.)
    assert isclose(v.hot_to_cold_flux_W_m2,20000.,rel_tol=1e-13)
    assert isclose(v.areal_mass_kg_m2,20.,rel_tol=1e-13)
    assert v.tensile_mismatch_Pa==pytest.approx(0.,abs=0.01)


def test_unequal_series_resistance_and_reversal():
    x=(material(thickness=.003,k=2.),material(thickness=.007,k=10.))
    target=100/(.003/2+.007/10)
    pos=evaluate_cells(x,400.,300.,300.)
    neg=evaluate_cells(x,300.,400.,300.)
    assert pos.hot_to_cold_flux_W_m2==pytest.approx(target)
    assert neg.hot_to_cold_flux_W_m2==pytest.approx(-target)
    assert pos.transmitted_flux_magnitude_W_m2==pytest.approx(target)
    assert neg.transmitted_flux_magnitude_W_m2==pytest.approx(target)
    assert pos.temperature_K[0]>pos.temperature_K[1]


def test_exact_free_and_restrained_uniform_expansion():
    # Single homogeneous cell with uniform temperature; free expansion
    # is stress free; flat restraint produces known compressive stress.
    c=material(k=4.,Q=120e9,alpha=8e-6)
    free=evaluate_cells((c,),350.,350.,300.,restraint='free')
    locked=evaluate_cells((c,),350.,350.,300.,restraint='flat_restrained')
    assert free.signed_equibiaxial_stress_Pa[0]==pytest.approx(0.,abs=.01)
    assert free.midplane_strain==pytest.approx(8e-6*50)
    assert locked.signed_equibiaxial_stress_Pa[0]==pytest.approx(-120e9*8e-6*50)
    assert locked.tensile_mismatch_Pa==0.


def test_layered_free_plate_force_moment_balance():
    layers=(material(thickness=.004,k=2.,Q=100e9,alpha=5e-6),
            material(thickness=.006,k=8.,Q=160e9,alpha=12e-6))
    v=evaluate_cells(layers,400.,300.,300.,restraint='free')
    assert abs(v.force_residual_N_m)<1e-5
    assert abs(v.moment_residual_N)<1e-7
    assert abs(v.curvature_per_m)>0
    assert len(v.coordinates_m)==2 and len(v.signed_equibiaxial_stress_Pa)==2


def test_mesh_refinement_constant_coefficients():
    one=evaluate_cells((material(),),400.,300.,300.)
    many=evaluate_cells(tuple(material(thickness=.01/64) for _ in range(64)),
                        400.,300.,300.)
    assert many.hot_to_cold_flux_W_m2==pytest.approx(one.hot_to_cold_flux_W_m2)
    assert many.areal_mass_kg_m2==pytest.approx(one.areal_mass_kg_m2)
    coarse=evaluate_cells(tuple(material(thickness=.01/16) for _ in range(16)),
                          400.,300.,300.)
    # Exactly linear thermal eigenstrain is representable by membrane+bending.
    assert coarse.tensile_mismatch_Pa < .05
    assert many.tensile_mismatch_Pa < .05
    assert coarse.curvature_per_m == pytest.approx(-.08,abs=2e-9)
    assert many.curvature_per_m == pytest.approx(-.08,abs=2e-9)


@pytest.mark.parametrize('bad',[Cell(.01,0,2000,1e11,1e-5),
    Cell(.01,2.,float('nan'),1e11,1e-5),
    Cell(.01,2.,2000.,1e11,.02)])
def test_out_of_domain_cannot_default(bad):
    with pytest.raises(ValueError):evaluate_cells((bad,),400.,300.,300.)


def test_free_homogeneous_exact_linear_temperature_refinement():
    for n in (2,16,128,512):
        r=evaluate_cells(tuple(material(thickness=.01/n) for _ in range(n)),400.,300.,300.)
        assert r.tensile_mismatch_Pa < .05  # absolute Pa roundoff tolerance
        assert r.curvature_per_m==pytest.approx(-.08,abs=2e-9)
        assert r.midplane_strain==pytest.approx(.0004,abs=1e-12)


def test_force_and_moment_independent_polynomial_integration():
    layers=(material(thickness=.004,k=2.,Q=100e9,alpha=5e-6),
            material(thickness=.006,k=8.,Q=160e9,alpha=12e-6))
    r=evaluate_cells(layers,400.,300.,300.)
    total=sum(c.thickness_m for c in layers)
    z=0.;temperature=400.; force=0.;moment=0.
    for c in layers:
        a=z-total/2; b=z+c.thickness_m-total/2
        next_t=temperature-r.hot_to_cold_flux_W_m2*c.thickness_m/c.conductivity_W_mK
        slope=(next_t-temperature)/c.thickness_m
        intercept=r.midplane_strain-c.expansion_per_K*(temperature-300.)+c.expansion_per_K*slope*a
        gradient=r.curvature_per_m-c.expansion_per_K*slope
        force+=c.biaxial_modulus_Pa*(intercept*(b-a)+gradient*(b*b-a*a)/2)
        moment+=c.biaxial_modulus_Pa*(intercept*(b*b-a*a)/2+gradient*(b**3-a**3)/3)
        z+=c.thickness_m;temperature=next_t
    assert abs(force)<1e-4
    assert abs(moment)<1e-6


@pytest.mark.parametrize('layers',[
    (material(thickness=.003,k=2.,Q=100e9,alpha=5e-6),
     material(thickness=.007,k=10.,Q=160e9,alpha=12e-6)),
    tuple(material(thickness=.01/20,k=2+8*(j+.5)/20,
                   Q=100e9+60e9*(j+.5)/20,
                   alpha=(5+7*(j+.5)/20)*1e-6)
          for j in range(20)),
])
def test_orientation_reversal_preserves_stress_and_inverts_curvature(layers):
    original=evaluate_cells(layers,400.,300.,300.)
    flipped=evaluate_cells(tuple(reversed(layers)),300.,400.,300.)
    assert flipped.hot_to_cold_flux_W_m2 == pytest.approx(-original.hot_to_cold_flux_W_m2)
    assert flipped.tensile_mismatch_Pa == pytest.approx(original.tensile_mismatch_Pa,rel=1e-9,abs=.05)
    assert flipped.curvature_per_m == pytest.approx(-original.curvature_per_m,rel=1e-9,abs=2e-9)
    assert flipped.signed_equibiaxial_stress_Pa == pytest.approx(
        tuple(reversed(original.signed_equibiaxial_stress_Pa)),rel=1e-9,abs=.05)
