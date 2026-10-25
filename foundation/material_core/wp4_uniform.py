"""Second synthetic process capability: single-batch uniform-feed deposition.

Unlike the layer-resolved route, this capability intentionally loses all
through-thickness composition variation. This is an alternative *assumption*
and must not be interpreted as a calibrated mixing/residence-time model.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from .contracts import (IntendedDesign,ProcessScenario,Homogeneous,Composition,
    ConstituentFraction,ManufacturingCommands,Command,EstimatedAchievedState,Provenance)
from .wp4_resolution import _integrated_layer,_quantize

ID="wp4-ideal-uniform-batch"
VERSION="0.1.0"
ROUTE="synthetic_ideal_uniform_batch_deposition"

def transform(design:IntendedDesign,process:ProcessScenario):
    if process.route!=ROUTE or process.status=="unresolved":
        raise ValueError("Unsupported uniform-batch process")
    if process.feed_fraction_resolution is None:
        raise ValueError("Uniform-batch feed resolution is required")
    if process.layer_resolution is not None and process.layer_resolution.value!=design.thickness.value:
        raise ValueError("Uniform batch must use a single full-thickness layer")
    arch=design.architecture
    first=(arch.composition if hasattr(arch,"composition") else
           arch.layers[0].composition if hasattr(arch,"layers") else arch.knots[0].composition)
    if first.basis!="volume":
        raise ValueError("Uniform batch supports only volume fractions")
    average=_integrated_layer(design,0.,1.)
    mix=_quantize(average,process.feed_fraction_resolution)
    comp=Composition(basis="volume",fractions=tuple(
        ConstituentFraction(material_id=k,fraction=v) for k,v in sorted(mix.items())))
    prov=Provenance(source_id=ID,source_version=VERSION,
        source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        location="WP4 synthetic uniform-batch transform",reuse_terms="demonstration only",
        evidence_kind="estimated",conditions="ideal full-thickness uniform feed; unit area",
        extraction="integrate full intended thickness and quantise once")
    commands=ManufacturingCommands(design_hash=design.content_hash,
        process_hash=process.content_hash,commands=(Command(sequence=0,composition=comp,volume=None),),
        provenance=prov)
    geometry=IntendedDesign(id=design.id+"-uniform-batch-estimated",
        parent_hashes=(design.content_hash,),thickness=design.thickness,
        architecture=Homogeneous(composition=comp),
        proposal_method="estimated uniform-batch geometry container",assumptions=design.assumptions)
    state=EstimatedAchievedState(id=design.id+"-uniform-batch-estimate",
        intended_design_hash=design.content_hash,process_hash=process.content_hash,
        geometry=geometry,observations=(),estimator_id=ID,estimator_version=VERSION,
        feasibility="conditional",conditions="synthetic ideal uniform-batch deposition; no measured evidence",
        assumptions=process.assumptions)
    return commands,state
