"""Effective-property scenario bounds and mass/volume basis references."""
import json
import pytest

from material_core.contracts import (
    Composition, ConstituentFraction, MaterialRecord, Property, Provenance,
    quantity,
)
from material_core.wp2_numerical import DomainError, _get_properties, _map_cell
from material_core.wp2_scenarios import make_wp2_fixture


def materials_and_props():
    x=make_wp2_fixture()
    return x.materials,_get_properties(x.materials)


def fraction(a,b,basis='volume'):
    return Composition(basis=basis,fractions=(
        ConstituentFraction(material_id='scenario_A',fraction=a),
        ConstituentFraction(material_id='scenario_B',fraction=b),
    ))


def test_pure_endpoints_and_midpoint():
    _,p=materials_and_props()
    a=_map_cell(fraction(1.,0.),p,.01)
    b=_map_cell(fraction(0.,1.),p,.01)
    mid=_map_cell(fraction(.5,.5),p,.01)
    assert a.conductivity_W_mK==pytest.approx(2.)
    assert b.conductivity_W_mK==pytest.approx(10.)
    assert mid.conductivity_W_mK==pytest.approx(6.)
    assert mid.density_kg_m3==pytest.approx(3000.)
    assert mid.biaxial_modulus_Pa==pytest.approx(130e9)
    assert mid.expansion_per_K==pytest.approx((100*5+160*12)/(100+160)*1e-6)


def test_mass_to_volume_basis_uses_density_and_preserves_material_amount():
    _,p=materials_and_props()
    # 50:50 volume gives mass fractions 1/3 and 2/3 for rho=2000/4000.
    mass=_map_cell(fraction(1/3,2/3,'mass'),p,.01)
    volume=_map_cell(fraction(.5,.5,'volume'),p,.01)
    assert mass.density_kg_m3==pytest.approx(volume.density_kg_m3)
    assert mass.conductivity_W_mK==pytest.approx(volume.conductivity_W_mK)
    assert mass.biaxial_modulus_Pa==pytest.approx(volume.biaxial_modulus_Pa)


def test_atomic_basis_must_not_default_to_volume():
    _,p=materials_and_props()
    with pytest.raises(DomainError,match='Atomic fraction'):
        _map_cell(fraction(.5,.5,'atomic'),p,.01)


def test_missing_or_wrongly_dimensioned_property_is_rejected():
    materials,_=materials_and_props()
    a=materials[0]
    missing=a.model_copy(update={'properties':a.properties[:-1]})
    with pytest.raises(DomainError,match='Missing required properties'):
        _get_properties((missing,materials[1]))
    from material_core.contracts import Property
    wrong=a.properties[0].model_copy(update={'quantity':quantity('density',2.)})
    altered=a.model_copy(update={'properties':(wrong,)+a.properties[1:]})
    with pytest.raises(DomainError,match='dimensional mismatch'):
        _get_properties((altered,materials[1]))


def test_different_process_state_and_non_synthetic_sources_are_rejected():
    materials,_=materials_and_props()
    altered=materials[1].model_copy(update={'state':'unverified porous fired body'})
    with pytest.raises(DomainError,match='Incompatible'):
        _get_properties((materials[0],altered))
    p=materials[0].provenance.model_copy(update={'evidence_kind':'estimated'})
    changed=materials[0].model_copy(update={'provenance':p})
    with pytest.raises(DomainError,match='synthetic'):
        _get_properties((changed,materials[1]))


def test_unknown_constituent_is_not_silently_substituted():
    _,p=materials_and_props()
    c=Composition(basis='volume',fractions=(
        ConstituentFraction(material_id='scenario_missing',fraction=1.),))
    with pytest.raises(DomainError,match='missing material'):
        _map_cell(c,p,.01)
