"""Neutral synthetic WP2 scenarios; never represent these as ceramic measurements.

Three distinct intended architectures use the same 10 mm thickness, material
volume budget (50% each constituent), thermal boundaries, property assumptions
and mechanical restraint. This is a software/numerical demonstration only.
"""
import hashlib
import json
from pathlib import Path

from .assumptions import AssumptionRegistry, AssumptionRecord
from .contracts import (
    AssumptionRef, Brief, Composition, ConstituentFraction, Constraint,
    CoupledThermomechanicalSettings, Discretisation, Gradient, Homogeneous,
    IntendedDesign, Knot, Layer, Layered, MappedThermalSettings, MaterialRecord,
    Objective, Property, Provenance, RunInputs, ThermoelasticSettings, quantity,
)
from .wp2_numerical import (
    comparison_context_hash, context_for_run, property_pack_hash, solver_identity,
)


def make_wp2_fixture(architecture='homogeneous', elements=128, mass_limit=31.,
                     property_domain=(290.,410.)):
    props=(
        ('scenario_A',2.,2000.,100e9,5e-6),
        ('scenario_B',10.,4000.,160e9,12e-6),
    )
    manifest=json.dumps({'phases':props,'temperature_domain':property_domain},separators=(',',':'))
    p=Provenance(source_id='wp2-neutral-synthetic-property-catalogue',
        source_version='scenario-2-domain-versioned',source_hash=hashlib.sha256(manifest.encode()).hexdigest(),
        location='foundation/material_core/wp2_scenarios.py:props',
        reuse_terms='Project-generated synthetic scenario, not external experimental data',
        evidence_kind='synthetic_scenario',
        conditions='Hypothetical isotropic fully dense phases; explicit range in property records',
        extraction='Declared numerical scenario values; not literature extraction')
    materials=[]
    for name,k,rho,Q,alpha in props:
        settings=(('conductivity','conductivity',k),('density','density',rho),
                  ('biaxial_modulus','stress',Q),('expansion','expansion',alpha))
        properties=tuple(Property(name=n,quantity=quantity(dim,v),
            convention='SI synthetic isotropic, direct input',
            conditions='Assumed constant between 290–410 K; as-defined scenario',
            uncertainty=None,provenance=p,
            temperature_min=quantity('temperature',property_domain[0]),
            temperature_max=quantity('temperature',property_domain[1])) for n,dim,v in settings)
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
    registry=AssumptionRegistry.from_builtin()
    wp2_registry=json.loads((Path(__file__).resolve().parent/'data'/
                             'assumptions_wp2_v1.json').read_text())
    assert wp2_registry['schema_version']==1
    for row in wp2_registry['assumptions']:
        registry.add(AssumptionRecord.from_dict(row))
    refs=tuple(AssumptionRef(id=x,version=1) for x in
        ('A01','A06','A07','A12','A14','A16','A17','A18','A19','A20','A21'))
    snapshots=tuple(json.dumps(r,sort_keys=True,separators=(',',':'))
        for r in registry.snapshot({a.id:a.version for a in refs}))
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
        property_pack_id='neutral-synthetic-A-B',property_pack_version='scenario-2-domain-versioned',
        property_pack_hash=property_pack_hash(materials),
        temperature_min=quantity('temperature',property_domain[0]),
        temperature_max=quantity('temperature',property_domain[1]),
        evaluation_context_hash='0'*64)
    preliminary=RunInputs(brief=brief,design=design,materials=materials,
        solver=solver_identity(),settings=settings,assumption_snapshots=snapshots,
        provenance=(p,))
    settings=settings.model_copy(update={'evaluation_context_hash':context_for_run(preliminary)})
    return RunInputs.model_validate_json(json.dumps({
        **preliminary.model_dump(mode='json'),
        'settings':settings.model_dump(mode='json')}))


def make_wp2_achieved_fixture(elements=128):
    """Supplied *synthetic estimated* geometry; NOT a process predictor.

    The changed mid-knot shifts the composition budget. This deliberately
    tests evaluating the achieved, not the original intended, state.
    """
    import json
    from .contracts import (
        EstimatedAchievedState, ProcessScenario, RunInputs,
    )
    x=make_wp2_fixture('gradient',elements=elements)
    p=x.provenance[0]
    process=ProcessScenario(id='supplied-synthetic-estimate',version=1,
        route='external estimated profile fixture; no manufacturing calculation',
        layer_resolution=None,feed_fraction_resolution=None,
        status='assumed',provenance=p,assumptions=x.brief.assumptions,
        excluded_mechanisms=('mixing and residence time','deposition rheology',
                             'drying and sintering','geometry defects'))
    def comp(a):
        return Composition(basis='volume',fractions=(
            ConstituentFraction(material_id='scenario_A',fraction=float(a)),
            ConstituentFraction(material_id='scenario_B',fraction=float(1-a))))
    achieved=IntendedDesign(id='explicit-estimated-spatial-state',
        parent_hashes=(x.design.content_hash,),thickness=x.brief.thickness,
        architecture=Gradient(knots=(
            Knot(position=0.,composition=comp(1.)),
            Knot(position=.5,composition=comp(.25)),
            Knot(position=1.,composition=comp(0.)))),
        proposal_method='Externally supplied labelled synthetic achieved state; no process predictor',
        assumptions=x.brief.assumptions)
    estimate=EstimatedAchievedState(id='synthetic-estimate',
        intended_design_hash=x.design.content_hash,
        process_hash=process.content_hash,geometry=achieved,
        observations=(),estimator_id='external-supplied-spatial-fixture',
        estimator_version='1',feasibility='conditional',
        conditions='Hypothetical achieved composition differs from intended; no manufacturing model',
        assumptions=x.brief.assumptions)
    raw=x.model_dump(mode='json')
    raw['process']=process.model_dump(mode='json')
    raw['estimated_state']=estimate.model_dump(mode='json')
    raw['evaluation_target']='estimated'
    provisional=RunInputs.model_validate_json(json.dumps(raw))
    raw['settings']['evaluation_context_hash']=context_for_run(provisional)
    return RunInputs.model_validate_json(json.dumps(raw))
