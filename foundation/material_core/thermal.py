"""Narrow adapter to the unchanged recovered WP0 Fourier verification fixture."""
from importlib.metadata import version
import hashlib
import platform
from pathlib import Path
from .contracts import (Evaluation, Metric, RunInputs, SolverIdentity, Homogeneous,
                        Layered, Gradient, quantity)


def solver_identity():
    from recovered_wp0 import thermal
    source = hashlib.sha256(Path(thermal.__file__).read_bytes() + Path(__file__).read_bytes()).hexdigest()
    return SolverIdentity(id='recovered_wp0.fourier', version='wp1-adapter-1', source_hash=source,
                          dependency_versions=(f'python=={platform.python_version()}',) + tuple(f'{n}=={version(n)}' for n in ('numpy','scipy','scikit-fem','pydantic')))


def evaluate(inputs: RunInputs) -> Evaluation:
    """Fail closed outside the recovered fixture's explicitly declared domain.

    Neither composition nor manufacturing fidelity is inferred from conductivity.
    No production mixture law or achieved-state evaluator is implemented in WP1.
    """
    inputs = RunInputs.model_validate_json(inputs.canonical_json())
    if inputs.solver != solver_identity():
        raise ValueError('Solver source/dependency identity differs from saved request')
    limitations=('Synthetic prescribed conductivity; not a ceramic composition/property law.',
                 'Steady 1D conduction, no sources/lateral losses, perfect interfaces.',
                 'No manufacturing feasibility, thermal mismatch or physical validation established.')
    a=inputs.design.architecture
    ks=inputs.settings.conductivity
    reason=None
    if inputs.evaluation_target != 'intended': reason='Achieved-state evaluation deferred to qualified adapter'
    elif isinstance(a,Homogeneous) and len(ks)!=1: reason='Homogeneous fixture requires one conductivity'
    elif isinstance(a,Layered) and (len(a.layers)!=2 or a.layers[0].end!=.5 or len(ks)!=2 or a.interface_condition!='perfect'):
        reason='Recovered layered fixture supports exactly two equal layers and perfect interfaces'
    elif isinstance(a,Gradient) and (len(a.knots)!=2 or len(ks)!=2): reason='Recovered gradient fixture supports two endpoint conductivities'
    if reason:
        return Evaluation(input_hash=inputs.content_hash, brief_hash=inputs.brief.content_hash, solver=inputs.solver, status='unsupported',
            metrics=tuple(Metric(objective_id=o.id,value=None,status='unsupported',explanation=reason) for o in inputs.brief.objectives),
            feasibility='unknown',limitations=limitations+(reason,))
    from recovered_wp0.thermal import ThermalDesign, evaluate as recovered_evaluate
    architecture={'homogeneous':'homogeneous','layered':'layered','gradient':'graded'}[a.kind]
    fixture=ThermalDesign(architecture, inputs.design.thickness.value,
         inputs.brief.hot_boundary.value, inputs.brief.cold_boundary.value, tuple(q.value for q in ks),'SI')
    result=recovered_evaluate(fixture, inputs.settings.mesh.elements)
    metrics=tuple(Metric(objective_id=o.id,value=quantity('heat_flux',result['flux_W_m2']),status='computed',
                         explanation='Signed hot-to-cold Fourier heat flux, prescribed synthetic conductivity')
                  if o.id=='thermal_transmission' and o.dimension=='heat_flux' else
                  Metric(objective_id=o.id,value=None,status='unsupported',explanation='No qualified evaluator for this objective in WP1')
                  for o in inputs.brief.objectives)
    complete=all(m.status=='computed' for m in metrics)
    # A numerical run can complete while physical/process feasibility stays unknown.
    # Conditional comparison is limited to the fixture with no process claim or constraints.
    feasibility='conditional' if complete and inputs.process is None and not inputs.brief.constraints else 'unknown'
    return Evaluation(input_hash=inputs.content_hash, brief_hash=inputs.brief.content_hash,solver=inputs.solver,
        status='complete' if complete else 'incomplete',metrics=metrics,feasibility=feasibility,
        limitations=limitations, temperature_K=tuple(result['temperature_K']),
        flux_spread=quantity('heat_flux',result['flux_spread_W_m2']))
