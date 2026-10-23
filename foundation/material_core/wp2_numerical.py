"""WP2 mapped three-objective adapter for bounded synthetic planar coupons.

This adapter reuses the documented numerical Fourier and classical laminate
equations in wp2_kernel; it introduces no fitted ceramic property law.
Volume-based parallel-channel conductivity and iso-strain stiffness are
*assumed upper-bound scenarios*, not assertions about sintered materials.
The reference scenario pack is deliberately synthetic and unqualified.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from .contracts import (
    Brief, Composition, CoupledThermomechanicalSettings, Evaluation, Gradient,
    Homogeneous, Layered, Metric, Quantity, RunInputs, SolverIdentity,
    SpatialFields, ConstraintMetric, quantity,
)
from .wp2_kernel import Cell, evaluate_cells


_REQUIRED = {
    'conductivity': 'conductivity',
    'density': 'density',
    'biaxial_modulus': 'stress',
    'expansion': 'expansion',
}


def property_pack_hash(materials) -> str:
    """Content-address all constituent properties, states and provenance."""
    payload=''.join(sorted(m.canonical_json() for m in materials))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def comparison_context_hash(brief: Brief, settings: CoupledThermomechanicalSettings,
                            target: str) -> str:
    """A common physical duty and evidence scenario, excluding architecture."""
    raw={
        'brief_hash':brief.content_hash,
        'stress_free_temperature':settings.mechanics.stress_free_temperature.model_dump(mode='json'),
        'restraint':settings.mechanics.restraint,
        'kinematics':settings.mechanics.kinematics,
        'mesh':settings.mechanics.mesh.model_dump(mode='json'),
        'mapping':{
            'conductivity':settings.thermal.conductivity_mapping,
            'density':settings.density_mapping,
            'stiffness':settings.mechanics.stiffness_mapping,
            'expansion':settings.mechanics.expansion_mapping,
        },
        'property_pack_id':settings.property_pack_id,
        'property_pack_version':settings.property_pack_version,
        'property_pack_hash':settings.property_pack_hash,
        'target':target,
    }
    return hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def compatible_comparison(a: Evaluation, b: Evaluation) -> bool:
    """Unknown contexts are never considered compatible with one another."""
    return (a.comparison_context_hash is not None and
            a.comparison_context_hash==b.comparison_context_hash and
            a.brief_hash==b.brief_hash and
            a.evidence_status==b.evidence_status and
            a.status=='complete' and b.status=='complete')


def solver_identity() -> SolverIdentity:
    import platform
    from importlib.metadata import version
    here=Path(__file__).resolve()
    source=hashlib.sha256(here.read_bytes()+
        (here.parent/'wp2_kernel.py').read_bytes()).hexdigest()
    return SolverIdentity(id='wp2.planar_thermomechanical',
        version='wp2-bounded-1',source_hash=source,
        dependency_versions=(f'python=={platform.python_version()}',
                             f'pydantic=={version("pydantic")}'))


class DomainError(ValueError):
    pass


def _get_properties(materials):
    states={m.state for m in materials}
    conditions={m.provenance.conditions for m in materials}
    if len(states)!=1 or len(conditions)!=1:
        raise DomainError('Incompatible constituent processing or evidence conditions')
    catalogue={}
    for m in materials:
        if m.provenance.evidence_kind!='synthetic_scenario':
            raise DomainError('WP2 mapped demo accepts only explicitly synthetic scenario records')
        props={}
        for p in m.properties:
            if p.name in _REQUIRED:
                if p.quantity.dimension!=_REQUIRED[p.name]:
                    raise DomainError('Property dimensional mismatch: '+p.name)
                if p.provenance.evidence_kind!='synthetic_scenario':
                    raise DomainError('Mixed process/evidence property states are unsupported')
                props[p.name]=p.quantity.value
        if set(props)!=set(_REQUIRED):
            raise DomainError('Missing required properties for '+m.id)
        if min(props['conductivity'],props['density'],props['biaxial_modulus'])<=0:
            raise DomainError('Nonpositive property for '+m.id)
        catalogue[m.id]=props
    return catalogue


def _volume_fractions(comp: Composition, props):
    if comp.basis=='atomic':
        raise DomainError('Atomic fraction conversion unsupported without molar masses')
    values={x.material_id:x.fraction for x in comp.fractions}
    if any(k not in props for k in values):
        raise DomainError('Composition refers to missing material')
    if comp.basis=='mass':
        ratios={k:x/props[k]['density'] for k,x in values.items()}
        total=sum(ratios.values())
        if total<=0: raise DomainError('Invalid mass/volume conversion')
        return {k:r/total for k,r in ratios.items()}
    return values


def _map_cell(comp: Composition, props, thickness: float):
    v=_volume_fractions(comp,props)
    # Separate rule choices: parallel flux upper-bound conductivity, additive
    # volumes/density, iso-strain biaxial stiffness, stiffness-weighted eigenstrain.
    k=sum(x*props[m]['conductivity'] for m,x in v.items())
    density=sum(x*props[m]['density'] for m,x in v.items())
    Q=sum(x*props[m]['biaxial_modulus'] for m,x in v.items())
    alpha=sum(x*props[m]['biaxial_modulus']*props[m]['expansion']
              for m,x in v.items())/Q
    return Cell(thickness,k,density,Q,alpha)


def _composition_at(architecture, position):
    if isinstance(architecture,Homogeneous):
        return architecture.composition
    if isinstance(architecture,Layered):
        for layer in architecture.layers:
            if layer.start<=position<layer.end:
                return layer.composition
        return architecture.layers[-1].composition
    if isinstance(architecture,Gradient):
        from .contracts import ConstituentFraction
        knots=architecture.knots
        for a,b in zip(knots,knots[1:]):
            if a.position<=position<=b.position:
                w=(position-a.position)/(b.position-a.position)
                af={x.material_id:x.fraction for x in a.composition.fractions}
                bf={x.material_id:x.fraction for x in b.composition.fractions}
                fractions=tuple(ConstituentFraction(material_id=k,
                    fraction=max(0.,min(1.,(1-w)*af[k]+w*bf[k])))
                    for k in sorted(af))
                return Composition(basis=a.composition.basis,fractions=fractions)
    raise DomainError('Unsupported architecture position')


def _mesh_cells(design, props, elements):
    arch=design.architecture
    breaks=[i/elements for i in range(elements+1)]
    if isinstance(arch,Layered):
        if arch.interface_condition!='perfect':
            raise DomainError('Only perfect layer interfaces supported')
        breaks.extend(layer.start for layer in arch.layers)
        breaks.extend(layer.end for layer in arch.layers)
    elif isinstance(arch,Gradient):
        breaks.extend(k.position for k in arch.knots)
    else:
        if not isinstance(arch,Homogeneous):
            raise DomainError('Unsupported architecture')
    breaks=sorted(set(breaks))
    cells=[]
    for start,end in zip(breaks,breaks[1:]):
        if end<=start: continue
        midpoint=(start+end)/2
        comp=_composition_at(arch,midpoint)
        cells.append(_map_cell(comp,props,(end-start)*design.thickness.value))
    return tuple(cells)


def evaluate(inputs: RunInputs) -> Evaluation:
    """Produce all declared supported metrics and preserve raw spatial results."""
    inputs=RunInputs.model_validate_json(inputs.canonical_json())
    settings=inputs.settings
    if not isinstance(settings,CoupledThermomechanicalSettings):
        raise ValueError('Mapped WP2 adapter requires coupled typed settings')
    if inputs.solver!=solver_identity():
        raise ValueError('WP2 solver source or dependency identity differs from request')
    if settings.property_pack_hash!=property_pack_hash(inputs.materials):
        raise ValueError('Property pack hash differs from supplied material evidence')
    ctx=comparison_context_hash(inputs.brief,settings,inputs.evaluation_target)
    if settings.evaluation_context_hash!=ctx:
        raise ValueError('Comparison context hash differs from scientific scenario')
    limitations=('Synthetic constituent and mixture scenario; no ceramic material validation.',
       'Parallel-channel conductivity upper-bound; iso-strain biaxial modulus.',
       'Volume-additive density and stiffness-weighted free thermal expansion.',
       'Steady 1D conduction, perfect interfaces, no heat sources or lateral loss.',
       'Thin plane-stress plate; strain and bending equilibrium as configured.',
       'Cell-centroid tensile mismatch; not total manufacturing residual stress.',
       'No shrinkage, creep, damage, interface failure, life or fracture model.')
    try:
        design=inputs.design
        if inputs.evaluation_target=='estimated':
            state=inputs.estimated_state
            if state is None or state.geometry is None:
                raise DomainError('Estimated achieved geometry is absent')
            design=state.geometry
            if state.intended_design_hash!=inputs.design.content_hash:
                raise DomainError('Estimated achieved state is not linked to intended design')
            if state.feasibility=='infeasible':
                raise DomainError('Manufacturing assessment explicitly infeasible')
        elif inputs.evaluation_target=='measured':
            raise DomainError('Measured achieved geometry unavailable in v1 contract')
        if design.thickness!=inputs.brief.thickness:
            raise DomainError('Evaluated geometry thickness differs from common brief')
        if (inputs.brief.hot_boundary.value>settings.temperature_max.value or
            inputs.brief.cold_boundary.value<settings.temperature_min.value or
            inputs.brief.cold_boundary.value>settings.temperature_max.value or
            inputs.brief.hot_boundary.value<settings.temperature_min.value or
            settings.mechanics.stress_free_temperature.value<settings.temperature_min.value or
            settings.mechanics.stress_free_temperature.value>settings.temperature_max.value):
            raise DomainError('Temperature outside declared supported property range')
        if (settings.density_mapping!='volume_additive' or
            settings.mechanics.stiffness_mapping!='iso_strain_voigt' or
            settings.mechanics.expansion_mapping!='stiffness_weighted_isostrain'):
            raise DomainError('Mapping relation is not qualified by this scenario adapter')
        if settings.mechanics.kinematics!='equibiaxial_plane_stress':
            raise DomainError('Unsupported mechanics kinematics')
        props=_get_properties(inputs.materials)
        cells=_mesh_cells(design,props,settings.thermal.mesh.elements)
        restraint=('free' if settings.mechanics.restraint=='force_and_moment_free'
                   else 'flat_restrained')
        result=evaluate_cells(cells,
            inputs.brief.hot_boundary.value,inputs.brief.cold_boundary.value,
            settings.mechanics.stress_free_temperature.value,restraint)
        values={'thermal_transmission':quantity('heat_flux',result.transmitted_flux_magnitude_W_m2),
                'areal_mass':quantity('areal_mass',result.areal_mass_kg_m2),
                'tensile_thermal_mismatch':quantity('stress',result.tensile_mismatch_Pa)}
        fields=SpatialFields(
            coordinate_from_hot_m=tuple(z+design.thickness.value/2 for z in result.coordinates_m),
            temperature_K=result.temperature_K,
            signed_equibiaxial_stress_Pa=result.signed_equibiaxial_stress_Pa,
            signed_hot_to_cold_flux=quantity('heat_flux',result.hot_to_cold_flux_W_m2),
            force_residual=quantity('force_per_length',result.force_residual_N_m),
            moment_residual=quantity('force',result.moment_residual_N),
            curvature_per_m=result.curvature_per_m)
        metrics=[]
        for obj in inputs.brief.objectives:
            val=values.get(obj.id)
            if val is not None and (val.dimension,val.unit)==(obj.dimension,obj.unit):
                metrics.append(Metric(objective_id=obj.id,value=val,status='computed',
                                      explanation='Mapped synthetic WP2 numerical scenario'))
            else:
                metrics.append(Metric(objective_id=obj.id,value=None,status='unsupported',
                                      explanation='Objective outside bounded WP2 method'))
        constraints=[]
        for c in inputs.brief.constraints:
            val=values.get(c.metric_id)
            if val is not None and (val.dimension,val.unit)==(c.limit.dimension,c.limit.unit):
                constraints.append(ConstraintMetric(metric_id=c.metric_id,value=val,
                    status='computed',explanation='Computed from shared synthetic scenario'))
            else:
                constraints.append(ConstraintMetric(metric_id=c.metric_id,value=None,
                    status='unsupported',explanation='Constraint metric unavailable or dimension mismatch'))
        status='complete' if all(m.status=='computed' for m in metrics) else 'incomplete'
        constrained_values={m.metric_id:m for m in constraints}
        if any(m.status!='computed' for m in constraints):
            feasibility='unknown'
        elif any(
            (c.relation=='le' and constrained_values[c.metric_id].value.value>c.limit.value) or
            (c.relation=='ge' and constrained_values[c.metric_id].value.value<c.limit.value)
            for c in inputs.brief.constraints):
            feasibility='infeasible'
        else:
            feasibility='conditional'
        # Conditional is NOT experimental material validation: evidence
        # maturity and numerical status remain separate from hard feasibility.
        return Evaluation(input_hash=inputs.content_hash,brief_hash=inputs.brief.content_hash,
            solver=inputs.solver,status=status,metrics=tuple(metrics),
            constraint_metrics=tuple(constraints),spatial_fields=fields,
            comparison_context_hash=ctx,evidence_status='synthetic',
            feasibility=feasibility,limitations=limitations+result.limitations)
    except DomainError as error:
        reason=str(error)
        return Evaluation(input_hash=inputs.content_hash,brief_hash=inputs.brief.content_hash,
            solver=inputs.solver,status='unsupported',
            metrics=tuple(Metric(objective_id=o.id,value=None,status='unsupported',explanation=reason)
                          for o in inputs.brief.objectives),
            feasibility='unknown',comparison_context_hash=ctx,evidence_status='synthetic',
            limitations=limitations+(reason,))
