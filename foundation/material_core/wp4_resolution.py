"""Bounded ideal-deposition layer/feed transform (WP4, synthetic only).

Coordinates are normalized hot-face to cold-face. Thickness is preserved exactly;
a nonintegral layer count is rejected. Commands use unit-area thickness amounts
(m3/m2 = m), not absolute deposited volumes. No physical mixing, porosity,
shrinkage, sintering or residual-stress prediction is implied.
"""
from __future__ import annotations
import math
from .contracts import (
    IntendedDesign, ProcessScenario, Composition, ConstituentFraction,
    Homogeneous, Layered, Gradient, Layer, ManufacturingCommands, Command,
    EstimatedAchievedState, Provenance, quantity,
)

TRANSFORM_ID = "wp4-ideal-layer-feed"
TRANSFORM_VERSION = "0.1.0"

def _fraction_at(design, x):
    arch = design.architecture
    if isinstance(arch, Homogeneous):
        return {f.material_id:f.fraction for f in arch.composition.fractions}
    if isinstance(arch, Layered):
        for layer in arch.layers:
            if layer.start <= x < layer.end or (x == 1 and layer.end == 1):
                return {f.material_id:f.fraction for f in layer.composition.fractions}
        raise ValueError("Uncovered coordinate")
    knots = arch.knots
    for a,b in zip(knots,knots[1:]):
        if a.position <= x <= b.position:
            t=(x-a.position)/(b.position-a.position)
            left={f.material_id:f.fraction for f in a.composition.fractions}
            right={f.material_id:f.fraction for f in b.composition.fractions}
            return {k:left[k]*(1-t)+right[k]*t for k in left}
    raise ValueError("Uncovered coordinate")

def _integrated_layer(design, a, b):
    arch=design.architecture
    breaks=[a,b]
    if isinstance(arch, Layered):
        breaks += [l.start for l in arch.layers if a<l.start<b]
    elif isinstance(arch, Gradient):
        breaks += [k.position for k in arch.knots if a<k.position<b]
    breaks=sorted(set(breaks))
    totals={}
    for x,y in zip(breaks,breaks[1:]):
        eps=(y-x)*1e-9
        left=_fraction_at(design,x+eps)
        right=_fraction_at(design,y-eps)
        for k in left:
            totals[k]=totals.get(k,0)+(left[k]+right[k])*(y-x)/2
    return {k:v/(b-a) for k,v in totals.items()}

def _quantize(fractions, step):
    # Strict two-constituent support: rounding ties towards the lower level.
    if len(fractions)==1:
        return dict(fractions)
    if len(fractions)!=2:
        raise ValueError("Feed quantisation currently supports one or two constituents")
    if not math.isclose(1/step,round(1/step),abs_tol=1e-9):
        raise ValueError("Feed step must divide unity")
    ids=sorted(fractions)
    levels=round(1/step)
    scaled=fractions[ids[0]]*levels
    n=math.ceil(scaled-0.5-1e-12)
    n=max(0,min(levels,n))
    return {ids[0]:n/levels,ids[1]:(levels-n)/levels}

def transform(design: IntendedDesign, process: ProcessScenario):
    if process.status=="unresolved" or process.layer_resolution is None or process.feed_fraction_resolution is None:
        raise ValueError("Resolution scenario unresolved")
    if process.route != "synthetic_ideal_planar_deposition":
        raise ValueError("Unsupported route")
    thickness=design.thickness.value
    count=thickness/process.layer_resolution.value
    if not math.isclose(count,round(count),rel_tol=0,abs_tol=1e-8):
        raise ValueError("Thickness not divisible by layer resolution")
    n=round(count)
    if n<1 or n>10000:
        raise ValueError("Unsupported layer count")
    arch=design.architecture
    basis=(arch.composition if isinstance(arch,Homogeneous) else
           arch.layers[0].composition if isinstance(arch,Layered) else arch.knots[0].composition).basis
    if basis!="volume":
        raise ValueError("Only volume-fraction composition is supported")
    layers=[]
    commands=[]
    for i in range(n):
        a=i/n
        b=(i+1)/n
        mixture=_quantize(_integrated_layer(design,a,b),process.feed_fraction_resolution)
        composition=Composition(basis="volume",fractions=tuple(
            ConstituentFraction(material_id=k,fraction=v) for k,v in sorted(mixture.items())))
        layers.append(Layer(start=a,end=b,composition=composition))
        commands.append(Command(sequence=i,composition=composition,volume=None))
    provenance=Provenance(source_id=TRANSFORM_ID,source_version=TRANSFORM_VERSION,
        source_hash="0"*64,location="WP4 synthetic software transform",
        reuse_terms="demonstration only",evidence_kind="estimated",
        conditions="ideal deposition; unit area",extraction="deterministic integration and feed quantisation")
    cmd=ManufacturingCommands(design_hash=design.content_hash,process_hash=process.content_hash,
        commands=tuple(commands),provenance=provenance)
    geometry=IntendedDesign(id=design.id+"-estimated-geometry",parent_hashes=(design.content_hash,),
        thickness=design.thickness,architecture=Layered(layers=tuple(layers),
        interface_condition="ideal deposited layers"),proposal_method="estimated geometry container only",
        assumptions=design.assumptions)
    achieved=EstimatedAchievedState(id=design.id+"-estimated",
        intended_design_hash=design.content_hash,process_hash=process.content_hash,
        geometry=geometry,observations=(),estimator_id=TRANSFORM_ID,
        estimator_version=TRANSFORM_VERSION,feasibility="conditional",
        conditions="ideal deposition under assumed layer/feed resolution; no measured state",
        assumptions=process.assumptions)
    return cmd,achieved
