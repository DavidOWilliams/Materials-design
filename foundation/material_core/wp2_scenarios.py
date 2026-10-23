"""Neutral synthetic WP2 scenarios; never represent these as ceramic measurements.

Three distinct intended architectures use the same 10 mm thickness, material
volume budget (50% each constituent), thermal boundaries, property assumptions
and mechanical restraint. This is a software/numerical demonstration only.
"""
import hashlib
import json

from .assumptions import AssumptionRegistry
from .contracts import (
    AssumptionRef, Brief, Composition, ConstituentFraction, Constraint,
    CoupledThermomechanicalSettings, Discretisation, Gradient, Homogeneous,
    IntendedDesign, Knot, Layer, Layered, MappedThermalSettings, MaterialRecord,
    Objective, Property, Provenance, RunInputs, ThermoelasticSettings, quantity,
)
from .wp2_numerical import (
    comparison_context_hash, property_pack_hash, solver_identity,
)


def make_wp2_fixture(architecture='homogeneous', elements=128, mass_limit=31.):
    props=(
        ('scenario_A',2.,2000.,100e9,5e-6),
        ('scenario_B',10.,4000.,160e9,12e-6),
    )
    manifest=json.dumps(props,separators=(',',':'))
    p=Provenance(source_id='wp2-neutral-synthetic-property-catalogue',
        source_version='scenario-1',source_hash=hashlib.sha256(manifest.encode()).hexdigest(),
        location='foundation/material_core/wp2_scenarios.py:props',
        reuse_terms='Project-generated synthetic scenario, not external experimental data',
        evidence_kind='synthetic_scenario',
        conditions='Hypothetical isotropic fully dense phases; constant properties 290–410 K',
        extraction='Declared numerical scenario values; not literature extraction')
    materials=[]
    for name,k,rho,Q,alpha in props:
        settings=(('conductivity','conductivity',k),('density','density',rho),
                  ('biaxial_modulus','stress',Q),('expansion','expansion',alpha))
        properties=tuple(Property(name=n,quantity=quantity(dim,v),
            convention='SI synthetic isotropic, direct input',
            conditions='Assumed constant between 290–410 K; as-defined scenario',
            uncertainty=None,provenance=p) for n,dim,v in settings)
        materials.append(MaterialRecord(id=name,version=1,
            label='Hypothetical '+name,state='synthetic ideal isotropic fully dense',
            chemistry='no identified engineering composition',
            properties=properties,provenance=p))
    materials=tuple(materials)
    def comp(a):
        return Composition(basis='volume',fractions=(
            ConstituentFraction(material_id='scenario_A',fraction=float(a)),
            ConstituentFraction(material_id='scenario_B',fraction=float(1-a))))
    if architecture=='homogeneous':
        arch=Homogeneous(composition=comp(.5))
    elif architecture=='layered':
        arch=Layered(layers=(
            Layer(start=0.,end=.5,composition=comp(1.)),
            Layer(start=.5,end=1.,composition=comp(0.))),
            interface_condition='perfect')
    elif architecture=='gradient':
        arch=Gradient(knots=(Knot(position=0.,composition=comp(1.)),
                             Knot(position=1.,composition=comp(0.))))
    else:
        raise ValueError('Unsupported scenario architecture')
    refs=tuple(AssumptionRef(id=x,version=1) for x in ('A01','A06','A07','A12','A14'))
    snapshots=tuple(json.dumps(r,sort_keys=True,separators=(',',':'))
        for r in AssumptionRegistry.from_builtin().snapshot({a.id:a.version for a in refs}))
    objectives=(
        Objective(id='thermal_transmission',dimension='heat_flux',unit='W/m2',
            direction='min',applicability='Absolute through-thickness steady flux'),
        Objective(id='areal_mass',dimension='areal_mass',unit='kg/m2',
            direction='min',applicability='Planar coupon mass per unit projected area'),
        Objective(id='tensile_thermal_mismatch',dimension='stress',unit='Pa',
            direction='min',applicability='Positive equibiaxial elastic stress at cell centres'),
    )
    constraints=() if mass_limit is None else (Constraint(id='mass_cap',
        metric_id='areal_mass',limit=quantity('areal_mass',mass_limit),
        relation='le',applicability='Common areal material budget'),)
    brief=Brief(id='WP2-common-three-objective-scenario',version=1,
        duty='Software demonstration: 10 mm coupon, 400 K / 300 K, free plate',
        thickness=quantity('length',.01),hot_boundary=quantity('temperature',400.),
        cold_boundary=quantity('temperature',300.),
        mechanical_condition='force_and_moment_free equibiaxial plane stress',
        objectives=objectives,constraints=constraints,assumptions=refs,evaluation_budget=20)
    design=IntendedDesign(id='wp2-'+architecture,thickness=brief.thickness,
        architecture=arch,proposal_method='Explicit fixed synthetic scenario',
        assumptions=refs)
    mesh=Discretisation(elements=elements)
    thermal=MappedThermalSettings(mesh=mesh,provenance=p)
    mechanics=ThermoelasticSettings(mesh=mesh,
        stress_free_temperature=quantity('temperature',300.),
        restraint='force_and_moment_free',
        stiffness_mapping='iso_strain_voigt',
        expansion_mapping='stiffness_weighted_isostrain',
        provenance=p)
    settings=CoupledThermomechanicalSettings(
        thermal=thermal,mechanics=mechanics,
        density_mapping='volume_additive',
        property_pack_id='neutral-synthetic-A-B',property_pack_version='scenario-1',
        property_pack_hash=property_pack_hash(materials),
        temperature_min=quantity('temperature',290.),
        temperature_max=quantity('temperature',410.),
        evaluation_context_hash='0'*64)
    settings=settings.model_copy(update={'evaluation_context_hash':
        comparison_context_hash(brief,settings,'intended')})
    return RunInputs(brief=brief,design=design,materials=materials,
        solver=solver_identity(),settings=settings,assumption_snapshots=snapshots,
        provenance=(p,))
