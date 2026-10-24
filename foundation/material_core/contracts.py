"""Versioned immutable contracts. SI only; unsupported quantities fail closed.

Tuple collections prevent mutation after validation. JSON is the interchange
format; adding a domain requires explicit contracts rather than arbitrary payloads.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Annotated, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

Text = Annotated[str, Field(min_length=1, pattern=r'.*\S.*')]
Positive = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Finite = Annotated[float, Field(allow_inf_nan=False)]
Fraction = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
Digest = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]

class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True, allow_inf_nan=False)
    schema_version: Literal['1.0'] = '1.0'

    def canonical_json(self) -> str:
        return json.dumps(self.model_dump(mode='json'), sort_keys=True, separators=(',', ':'), allow_nan=False)

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode()).hexdigest()

UNITS = {'length':'m', 'temperature':'K', 'conductivity':'W/(m K)',
         'heat_flux':'W/m2', 'areal_mass':'kg/m2', 'density':'kg/m3',
         'stress':'Pa', 'fraction':'1', 'time':'s', 'energy':'J',
         'mass':'kg', 'volume':'m3', 'expansion':'1/K',
         'force':'N', 'force_per_length':'N/m'}

class Quantity(Contract):
    dimension: Text
    value: Finite
    unit: Text

    @model_validator(mode='after')
    def valid_unit(self):
        if UNITS.get(self.dimension) != self.unit:
            raise ValueError('Unsupported dimension or noncanonical SI unit')
        if self.dimension in ('length','conductivity','density','temperature') and self.value <= 0:
            raise ValueError('Quantity must be positive')
        if self.dimension in ('areal_mass','time','energy','mass','volume') and self.value < 0:
            raise ValueError('Quantity must be nonnegative')
        if self.dimension == 'fraction' and not 0 <= self.value <= 1:
            raise ValueError('Fraction outside [0,1]')
        return self

def quantity(dimension, value):
    if type(value) not in (float,int): raise ValueError('Numeric quantity required; no booleans or coercion')
    return Quantity(dimension=dimension, value=float(value), unit=UNITS[dimension])

def require_dimension(q, dimension):
    if q.dimension != dimension:
        raise ValueError(f'Expected {dimension}, got {q.dimension}')

def unique(values, what):
    if len(values) != len(set(values)):
        raise ValueError(f'Duplicate {what}')

class Provenance(Contract):
    source_id: Text
    source_version: Text
    source_hash: Digest
    location: Text
    reuse_terms: Text
    evidence_kind: Literal['synthetic_scenario','published_measurement','numerical_verification','estimated','measured']
    conditions: Text
    extraction: Text

class AssumptionRef(Contract):
    id: Text
    version: Annotated[int, Field(ge=1)]

class Objective(Contract):
    id: Text
    dimension: Text
    unit: Text
    direction: Literal['min','max']
    applicability: Text

    @model_validator(mode='after')
    def units(self):
        if UNITS.get(self.dimension) != self.unit: raise ValueError('Objective unit mismatch')
        return self

class Constraint(Contract):
    id: Text
    metric_id: Text
    limit: Quantity
    relation: Literal['le','ge']
    applicability: Text

class Brief(Contract):
    kind: Literal['brief'] = 'brief'
    id: Text
    version: Annotated[int, Field(ge=1)]
    duty: Text
    thickness: Quantity
    hot_boundary: Quantity
    cold_boundary: Quantity
    mechanical_condition: Text
    objectives: Annotated[tuple[Objective,...], Field(min_length=1)]
    constraints: tuple[Constraint,...] = ()
    assumptions: tuple[AssumptionRef,...]
    evaluation_budget: Annotated[int, Field(ge=1)]

    @model_validator(mode='after')
    def consistent(self):
        require_dimension(self.thickness,'length')
        require_dimension(self.hot_boundary,'temperature'); require_dimension(self.cold_boundary,'temperature')
        unique([o.id for o in self.objectives],'objectives'); unique([c.id for c in self.constraints],'constraints')
        unique([a.id for a in self.assumptions],'assumptions')
        per_metric={}
        for c in self.constraints:
            previous=per_metric.setdefault(c.metric_id,(c.limit.dimension,c.limit.unit))
            if previous!=(c.limit.dimension,c.limit.unit): raise ValueError('Conflicting constraint units for one metric')
            for o in self.objectives:
                if c.metric_id == o.id and (c.limit.dimension,c.limit.unit)!=(o.dimension,o.unit):
                    raise ValueError('Constraint/objective dimension mismatch')
        return self

class Uncertainty(Contract):
    dimension: Text
    value: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    unit: Text

    @model_validator(mode='after')
    def units(self):
        if UNITS.get(self.dimension) != self.unit: raise ValueError('Uncertainty unit mismatch')
        return self

class Property(Contract):
    name: Text
    quantity: Quantity
    convention: Text
    conditions: Text
    uncertainty: Uncertainty | None
    provenance: Provenance
    temperature_min: Quantity | None = None
    temperature_max: Quantity | None = None

    def canonical_json(self) -> str:
        raw=self.model_dump(mode='json')
        for key in ('temperature_min','temperature_max'):
            if raw.get(key) is None: raw.pop(key,None)
        return json.dumps(raw,sort_keys=True,separators=(',',':'),allow_nan=False)

    @model_validator(mode='after')
    def valid_uncertainty(self):
        if (self.temperature_min is None)!=(self.temperature_max is None):
            raise ValueError('Property temperature applicability requires both limits')
        if self.temperature_min is not None:
            require_dimension(self.temperature_min,'temperature')
            require_dimension(self.temperature_max,'temperature')
            if self.temperature_max.value<=self.temperature_min.value:
                raise ValueError('Invalid property temperature applicability')
        if self.uncertainty is not None:
            if self.uncertainty.dimension != self.quantity.dimension or self.uncertainty.value < 0:
                raise ValueError('Uncertainty must be nonnegative in property units')
        return self

class MaterialRecord(Contract):
    kind: Literal['material'] = 'material'
    id: Text
    version: Annotated[int, Field(ge=1)]
    label: Text
    state: Text
    chemistry: Text
    properties: tuple[Property,...]
    provenance: Provenance

    @model_validator(mode='after')
    def unique_properties(self):
        unique([p.name for p in self.properties],'material properties')
        return self

class ConstituentFraction(Contract):
    material_id: Text
    fraction: Fraction

class Composition(Contract):
    basis: Literal['volume','mass','atomic']
    fractions: Annotated[tuple[ConstituentFraction,...], Field(min_length=1)]

    @model_validator(mode='after')
    def balanced(self):
        unique([f.material_id for f in self.fractions],'constituents')
        if not math.isclose(sum(f.fraction for f in self.fractions),1,rel_tol=0,abs_tol=1e-10):
            raise ValueError('Composition fractions must sum to one')
        return self

class Layer(Contract):
    start: Fraction
    end: Fraction
    composition: Composition

    @model_validator(mode='after')
    def ordered(self):
        if self.end <= self.start: raise ValueError('Layer must have positive extent')
        return self

class Knot(Contract):
    position: Fraction
    composition: Composition

class Homogeneous(Contract):
    kind: Literal['homogeneous'] = 'homogeneous'
    composition: Composition

class Layered(Contract):
    kind: Literal['layered'] = 'layered'
    layers: Annotated[tuple[Layer,...], Field(min_length=2)]
    interface_condition: Text

    @model_validator(mode='after')
    def coverage(self):
        if self.layers[0].start != 0 or self.layers[-1].end != 1:
            raise ValueError('Layers must span normalized thickness [0,1]')
        if any(a.end != b.start for a,b in zip(self.layers,self.layers[1:])):
            raise ValueError('Layer overlap or gap')
        if len({x.composition.basis for x in self.layers}) != 1: raise ValueError('Mixed composition bases')
        return self

class Gradient(Contract):
    kind: Literal['gradient'] = 'gradient'
    interpolation: Literal['piecewise_linear'] = 'piecewise_linear'
    knots: Annotated[tuple[Knot,...], Field(min_length=2)]

    @model_validator(mode='after')
    def coverage(self):
        if self.knots[0].position != 0 or self.knots[-1].position != 1: raise ValueError('Gradient must span [0,1]')
        if any(a.position >= b.position for a,b in zip(self.knots,self.knots[1:])): raise ValueError('Unordered knots')
        keys = [set(f.material_id for f in k.composition.fractions) for k in self.knots]
        if any(x != keys[0] for x in keys) or len({k.composition.basis for k in self.knots}) != 1:
            raise ValueError('Gradient knots must use same constituent set and basis')
        return self

Architecture = Annotated[Homogeneous | Layered | Gradient, Field(discriminator='kind')]

class IntendedDesign(Contract):
    kind: Literal['intended_design'] = 'intended_design'
    id: Text
    parent_hashes: tuple[Digest,...] = ()
    coordinate_system: Literal['planar_normalized_thickness'] = 'planar_normalized_thickness'
    thickness: Quantity
    architecture: Architecture
    proposal_method: Text
    assumptions: tuple[AssumptionRef,...]

    @model_validator(mode='after')
    def geometry(self):
        require_dimension(self.thickness,'length'); unique(list(self.parent_hashes),'parents')
        return self

class ProcessScenario(Contract):
    kind: Literal['process_scenario'] = 'process_scenario'
    id: Text
    version: Annotated[int, Field(ge=1)]
    route: Text
    layer_resolution: Quantity | None
    feed_fraction_resolution: Fraction | None
    status: Literal['assumed','evidenced','unresolved']
    provenance: Provenance
    assumptions: tuple[AssumptionRef,...]
    excluded_mechanisms: tuple[Text,...]

    @model_validator(mode='after')
    def dimensions(self):
        if self.layer_resolution is not None: require_dimension(self.layer_resolution,'length')
        if self.feed_fraction_resolution is not None and self.feed_fraction_resolution <= 0: raise ValueError('Resolution must be positive')
        return self

class Command(Contract):
    sequence: Annotated[int, Field(ge=0)]
    composition: Composition
    volume: Quantity | None

    @model_validator(mode='after')
    def volume_units(self):
        if self.volume is not None: require_dimension(self.volume,'volume')
        return self

class ManufacturingCommands(Contract):
    kind: Literal['manufacturing_commands'] = 'manufacturing_commands'
    design_hash: Digest
    process_hash: Digest
    commands: tuple[Command,...]
    provenance: Provenance

    @model_validator(mode='after')
    def ordered(self):
        if any(a.sequence >= b.sequence for a,b in zip(self.commands,self.commands[1:])): raise ValueError('Command order invalid')
        return self

class Observation(Contract):
    name: Text
    value: Quantity | None
    uncertainty: Uncertainty | None
    missing_reason: Text | None
    provenance: Provenance

    @model_validator(mode='after')
    def missingness(self):
        if (self.value is None) != (self.missing_reason is not None): raise ValueError('Unknown values require reason; known values cannot be marked missing')
        if self.uncertainty is not None and (self.value is None or self.uncertainty.dimension != self.value.dimension or self.uncertainty.value < 0): raise ValueError('Invalid uncertainty')
        return self

class EstimatedAchievedState(Contract):
    kind: Literal['estimated_achieved_state'] = 'estimated_achieved_state'
    id: Text
    intended_design_hash: Digest
    process_hash: Digest
    geometry: IntendedDesign | None
    observations: tuple[Observation,...]
    estimator_id: Text
    estimator_version: Text
    feasibility: Literal['unknown','conditional','infeasible']
    conditions: Text
    assumptions: tuple[AssumptionRef,...]

class MeasuredAchievedState(Contract):
    kind: Literal['measured_achieved_state'] = 'measured_achieved_state'
    id: Text
    intended_design_hash: Digest
    specimen_id: Text
    measurement_stage: Text
    observations: Annotated[tuple[Observation,...], Field(min_length=1)]
    failure_status: Literal['not_reported','failed','survived']
    provenance: Provenance

    @model_validator(mode='after')
    def measurements(self):
        if self.provenance.evidence_kind not in ('measured','published_measurement'): raise ValueError('Measured state requires measurement provenance')
        for o in self.observations:
            if o.provenance.evidence_kind not in ('measured','published_measurement'): raise ValueError('Observation lacks measurement provenance')
        return self

class SolverIdentity(Contract):
    id: Text
    version: Text
    source_hash: Digest
    dependency_versions: tuple[Text,...]

class Discretisation(Contract):
    method: Literal['linear_finite_elements'] = 'linear_finite_elements'
    elements: Annotated[int, Field(ge=2)]

class ThermalSettings(Contract):
    kind: Literal['prescribed_thermal_fixture'] = 'prescribed_thermal_fixture'
    mesh: Discretisation
    conductivity: Annotated[tuple[Quantity,...], Field(min_length=1)]
    property_mapping: Literal['prescribed_synthetic_spatial_field'] = 'prescribed_synthetic_spatial_field'
    interface_condition: Literal['perfect'] = 'perfect'
    source_terms: Literal['none'] = 'none'
    lateral_loss: Literal['none'] = 'none'
    provenance: Provenance

    @model_validator(mode='after')
    def dimensions(self):
        for q in self.conductivity: require_dimension(q,'conductivity')
        if self.mesh.elements % 2: raise ValueError('Recovered fixture requires even mesh')
        if self.provenance.evidence_kind != 'synthetic_scenario': raise ValueError('Prescribed fixture must be synthetic')
        return self

class ThermoelasticSettings(Contract):
    """Bounded mechanics method; not a manufacturing residual-stress model."""
    kind: Literal['planar_thermoelastic'] = 'planar_thermoelastic'
    mesh: Discretisation
    stress_free_temperature: Quantity
    kinematics: Literal['equibiaxial_plane_stress'] = 'equibiaxial_plane_stress'
    restraint: Literal['force_and_moment_free','fully_flat_restrained']
    expansion_convention: Literal['small_strain_isotropic'] = 'small_strain_isotropic'
    stiffness_mapping: Text
    expansion_mapping: Text
    provenance: Provenance

    @model_validator(mode='after')
    def physical_units(self):
        require_dimension(self.stress_free_temperature,'temperature')
        return self


class MappedThermalSettings(Contract):
    kind: Literal['mapped_steady_conduction'] = 'mapped_steady_conduction'
    mesh: Discretisation
    conductivity_mapping: Literal['parallel_voigt_upper_bound'] = 'parallel_voigt_upper_bound'
    interface_condition: Literal['perfect'] = 'perfect'
    source_terms: Literal['none'] = 'none'
    lateral_loss: Literal['none'] = 'none'
    provenance: Provenance


class CoupledThermomechanicalSettings(Contract):
    """Explicit matched thermal/mechanics settings for three D1 quantities."""
    kind: Literal['planar_coupled'] = 'planar_coupled'
    thermal: MappedThermalSettings
    mechanics: ThermoelasticSettings
    density_mapping: Text
    property_pack_id: Text
    property_pack_version: Text
    property_pack_hash: Digest
    temperature_min: Quantity
    temperature_max: Quantity
    evaluation_context_hash: Digest

    @model_validator(mode='after')
    def consistent_mesh(self):
        if self.thermal.mesh != self.mechanics.mesh:
            raise ValueError('Thermal/mechanics mesh mismatch')
        require_dimension(self.temperature_min,'temperature')
        require_dimension(self.temperature_max,'temperature')
        if self.temperature_max.value <= self.temperature_min.value:
            raise ValueError('Invalid supported temperature range')
        return self


class Metric(Contract):
    objective_id: Text
    value: Quantity | None
    status: Literal['computed','unsupported','missing','failed']
    explanation: Text

    @model_validator(mode='after')
    def known(self):
        if (self.value is not None) != (self.status == 'computed'): raise ValueError('Computed status/value mismatch')
        return self

class ConstraintMetric(Contract):
    """Independent measured/calculated constraint quantity, not an objective."""
    metric_id: Text
    value: Quantity | None
    status: Literal['computed','unsupported','missing','failed']
    explanation: Text

    @model_validator(mode='after')
    def known(self):
        if (self.value is not None) != (self.status == 'computed'):
            raise ValueError('Computed constraint status/value mismatch')
        return self


class SpatialFields(Contract):
    coordinate_from_hot_m: tuple[Finite,...]
    temperature_K: tuple[Positive,...]
    signed_equibiaxial_stress_Pa: tuple[Finite,...]
    signed_hot_to_cold_flux: Quantity
    force_residual: Quantity
    moment_residual: Quantity
    curvature_per_m: Finite
    sampled_stress_region: Literal['cell_centres'] = 'cell_centres'

    @model_validator(mode='after')
    def shapes(self):
        n=len(self.coordinate_from_hot_m)
        if n<1 or len(self.temperature_K)!=n or len(self.signed_equibiaxial_stress_Pa)!=n:
            raise ValueError('Spatial field arrays must have matching nonempty coordinates')
        if any(a>=b for a,b in zip(self.coordinate_from_hot_m,self.coordinate_from_hot_m[1:])):
            raise ValueError('Coordinates must be strictly increasing')
        require_dimension(self.signed_hot_to_cold_flux,'heat_flux')
        require_dimension(self.force_residual,'force_per_length')
        require_dimension(self.moment_residual,'force')
        return self


class ConstraintOutcome(Contract):
    constraint_id: Text
    metric_id: Text
    outcome: Literal['satisfied','violated','unknown']
    relation: Literal['le','ge']
    limit: Quantity


class Evaluation(Contract):
    kind: Literal['evaluation'] = 'evaluation'

    def canonical_json(self) -> str:
        # WP1 v1.0 evaluation artifacts did not contain constraint_metrics.
        # Preserve their exact canonical bytes and SHA256 identifiers.
        raw=self.model_dump(mode='json')
        if not self.constraint_metrics:
            raw.pop('constraint_metrics', None)
        for key in ('spatial_fields','comparison_context_hash','evidence_status','manufacturing_feasibility'):
            if raw.get(key) is None: raw.pop(key,None)
        if not self.constraint_outcomes: raw.pop('constraint_outcomes',None)
        return json.dumps(raw,sort_keys=True,separators=(',',':'),allow_nan=False)
    input_hash: Digest
    brief_hash: Digest
    solver: SolverIdentity
    status: Literal['complete','incomplete','unsupported','failed']
    metrics: tuple[Metric,...]
    constraint_metrics: tuple[ConstraintMetric,...] = ()
    spatial_fields: SpatialFields | None = None
    comparison_context_hash: Digest | None = None
    evidence_status: Literal['synthetic','provisional','supported'] | None = None
    manufacturing_feasibility: Literal['unknown','conditional','infeasible'] | None = None
    constraint_outcomes: tuple['ConstraintOutcome',...] = ()
    feasibility: Literal['unknown','conditional','infeasible']
    limitations: Annotated[tuple[Text,...], Field(min_length=1)]
    temperature_K: tuple[Positive,...] = ()
    flux_spread: Quantity | None = None

    @model_validator(mode='after')
    def complete(self):
        unique([m.objective_id for m in self.metrics],'metric IDs')
        unique([m.metric_id for m in self.constraint_metrics],'constraint metric IDs')
        unique([m.constraint_id for m in self.constraint_outcomes],'constraint outcome IDs')
        if self.status == 'complete' and (not self.metrics or any(m.status!='computed' for m in self.metrics)): raise ValueError('Incomplete objectives cannot be complete')
        if self.flux_spread is not None: require_dimension(self.flux_spread,'heat_flux')
        return self

    def comparison_eligible(self, brief: Brief) -> bool:
        if self.brief_hash != brief.content_hash or self.status != 'complete' or self.feasibility != 'conditional': return False
        if self.manufacturing_feasibility in ('unknown','infeasible'): return False
        metrics = {m.objective_id:m for m in self.metrics}
        if set(metrics) != {o.id for o in brief.objectives}: return False
        for o in brief.objectives:
            m=metrics[o.id]
            if m.status!='computed' or m.value is None or (m.value.dimension,m.value.unit)!=(o.dimension,o.unit): return False
        constrained={m.metric_id:m for m in self.constraint_metrics}
        if set(constrained) - {c.metric_id for c in brief.constraints}: return False
        for c in brief.constraints:
            # A quantity shared with an objective must agree rather than supply
            # two contradictory values for the same physical metric.
            m=constrained.get(c.metric_id)
            objective=metrics.get(c.metric_id)
            if m is not None and objective is not None:
                if m.value != objective.value or m.status != objective.status: return False
            if m is None: m=objective
            if m is None or m.status!='computed' or m.value is None: return False
            if (m.value.dimension,m.value.unit)!=(c.limit.dimension,c.limit.unit): return False
            if c.relation=='le' and m.value.value>c.limit.value: return False
            if c.relation=='ge' and m.value.value<c.limit.value: return False
        return True

class DecisionRecord(Contract):
    kind: Literal['decision'] = 'decision'
    id: Text
    compared_run_ids: tuple[Text,...]
    action: Literal['retain','revise','reject','defer']
    rationale: Text
    reviewer: Text
    evidence_hashes: tuple[Digest,...]
    assumption_refs: tuple[AssumptionRef,...]
    revisit_trigger: Text

class RunInputs(Contract):
    kind: Literal['run_inputs'] = 'run_inputs'
    brief: Brief
    design: IntendedDesign
    materials: tuple[MaterialRecord,...]
    process: ProcessScenario | None = None
    estimated_state: EstimatedAchievedState | None = None
    measured_state: MeasuredAchievedState | None = None
    commands: ManufacturingCommands | None = None
    evaluation_target: Literal['intended','estimated','measured'] = 'intended'
    solver: SolverIdentity
    settings: Annotated[ThermalSettings | ThermoelasticSettings | CoupledThermomechanicalSettings, Field(discriminator='kind')]
    assumption_snapshots: tuple[str,...]
    provenance: Annotated[tuple[Provenance,...], Field(min_length=1)]

    @model_validator(mode='after')
    def links(self):
        from .assumptions import validate_snapshot
        records=validate_snapshot([json.loads(s) for s in self.assumption_snapshots])
        object.__setattr__(self, 'assumption_snapshots', tuple(json.dumps(r.to_dict(),sort_keys=True,separators=(',',':')) for r in sorted(records,key=lambda r:r.assumption_id)))
        available={(r.assumption_id,r.version) for r in records}
        refs=list(self.brief.assumptions)+list(self.design.assumptions)
        if self.process: refs+=list(self.process.assumptions)
        if self.estimated_state: refs+=list(self.estimated_state.assumptions)
        if any((r.id,r.version) not in available for r in refs): raise ValueError('Missing assumption snapshot')
        if self.design.thickness != self.brief.thickness: raise ValueError('Brief/design thickness mismatch')
        unique([m.id for m in self.materials],'material IDs')
        arch=self.design.architecture
        comps=[arch.composition] if isinstance(arch,Homogeneous) else [x.composition for x in (arch.layers if isinstance(arch,Layered) else arch.knots)]
        ids={m.id for m in self.materials}
        if self.estimated_state and self.estimated_state.geometry:
            ga=self.estimated_state.geometry.architecture
            comps += [ga.composition] if isinstance(ga,Homogeneous) else [x.composition for x in (ga.layers if isinstance(ga,Layered) else ga.knots)]
            if any((r.id,r.version) not in available for r in self.estimated_state.geometry.assumptions): raise ValueError('Missing achieved-geometry assumption')
        if self.commands: comps += [c.composition for c in self.commands.commands]
        if any(f.material_id not in ids for c in comps for f in c.fractions): raise ValueError('Missing constituent material')
        for state in (self.estimated_state,self.measured_state):
            if state and state.intended_design_hash != self.design.content_hash: raise ValueError('State belongs to another design')
        if self.estimated_state and (not self.process or self.estimated_state.process_hash!=self.process.content_hash): raise ValueError('Estimated state/process mismatch')
        if self.commands and (not self.process or self.commands.design_hash!=self.design.content_hash or self.commands.process_hash!=self.process.content_hash): raise ValueError('Command lineage mismatch')
        if self.evaluation_target=='estimated' and self.estimated_state is None: raise ValueError('Estimated target missing')
        if self.evaluation_target=='measured' and self.measured_state is None: raise ValueError('Measured target missing')
        return self

class CandidateGenerator(Protocol):
    id: str
    version: str
    def generate(self, brief: Brief, materials: tuple[MaterialRecord,...]) -> tuple[IntendedDesign,...]: ...

class ManufacturingTransformer(Protocol):
    id: str
    version: str
    def transform(self, design: IntendedDesign, process: ProcessScenario) -> EstimatedAchievedState: ...

class PerformanceEvaluator(Protocol):
    def evaluate(self, inputs: RunInputs) -> Evaluation: ...
