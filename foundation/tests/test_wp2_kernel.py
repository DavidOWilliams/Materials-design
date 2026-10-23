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
    # Cell-centroid discontinuous temperature samples approximate a continuous\n    # linear profile. Refinement decreases the discrete mismatch, but its\n    # finite-resolution peak is not exactly zero.\n    coarse=evaluate_cells(tuple(material(thickness=.01/16) for _ in range(16)),\n                          400.,300.,300.)\n    assert many.tensile_mismatch_Pa < coarse.tensile_mismatch_Pa


@pytest.mark.parametrize('bad',[Cell(.01,0,2000,1e11,1e-5),
    Cell(.01,2.,float('nan'),1e11,1e-5),
    Cell(.01,2.,2000.,1e11,.02)])
def test_out_of_domain_cannot_default(bad):
    with pytest.raises(ValueError):evaluate_cells((bad,),400.,300.,300.)
