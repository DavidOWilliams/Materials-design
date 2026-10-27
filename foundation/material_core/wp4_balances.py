"""Unit-area analytical constituent accounting for WP4 synthetic ideal deposition."""
from __future__ import annotations
from .contracts import Homogeneous,Layered,Gradient
from .wp4_resolution import _integrated_layer

def balances(design,commands,estimated_state):
    if commands.design_hash!=design.content_hash or estimated_state.intended_design_hash!=design.content_hash:
        raise ValueError("Balance lineage mismatch")
    geometry=estimated_state.geometry
    if geometry is None or geometry.thickness!=design.thickness:
        raise ValueError("Missing or changed achieved geometry")
    arch=geometry.architecture
    if isinstance(arch,Homogeneous):
        regions=[(0.,1.,arch.composition)]
    elif isinstance(arch,Layered):
        regions=[(x.start,x.end,x.composition) for x in arch.layers]
    else: raise ValueError("Unsupported achieved geometry")
    if len(regions)!=len(commands.commands):
        raise ValueError("Command and achieved region counts differ")
    ids=sorted(f.material_id for f in commands.commands[0].composition.fractions)
    h=design.thickness.value
    intended={k:0. for k in ids}
    commanded={k:0. for k in ids}
    achieved={k:0. for k in ids}
    integrated_error=0.
    max_layer_error=0.
    for (a,b,comp),command in zip(regions,commands.commands):
        intended_average=_integrated_layer(design,a,b)
        feed={f.material_id:f.fraction for f in command.composition.fractions}
        output={f.material_id:f.fraction for f in comp.fractions}
        if set(feed)!=set(ids) or set(output)!=set(ids) or set(intended_average)!=set(ids):
            raise ValueError("Constituent identity mismatch")
        if feed!=output: raise ValueError("Estimated field differs from commanded composition")
        if abs(sum(feed.values())-1)>1e-10:raise ValueError("Nonconserving feed composition")
        for k in ids:
            intended[k]+=h*(b-a)*intended_average[k]
            commanded[k]+=h*(b-a)*feed[k]
            achieved[k]+=h*(b-a)*output[k]
            error=abs(intended_average[k]-output[k])
            integrated_error+=h*(b-a)*error
            max_layer_error=max(max_layer_error,error)
    return dict(basis="unit projected area",amount_unit="m3/m2",
        thickness_m=h,intended=intended,commanded=commanded,estimated=achieved,
        signed_estimated_minus_intended={k:achieved[k]-intended[k] for k in ids},
        integrated_absolute_fraction_error_m=integrated_error,
        maximum_layer_average_fraction_error=max_layer_error,
        excluded="sub-layer pointwise error and process mixing are not resolved")
